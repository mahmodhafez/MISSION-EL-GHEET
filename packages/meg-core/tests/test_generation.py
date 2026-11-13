"""Generic generation tests. All positive calendar support is SYNTHETIC ONLY."""

from dataclasses import replace
from datetime import date, timedelta
import unittest
from unittest.mock import patch

from test_constraints import SYNTHETIC, changed, known, synthetic, uh001, unknown
from meg_core.planner import constraints
from meg_core.planner.scope import prepare_scope
from meg_core.planner.generate import generate
from meg_core.planner.service import plan as plan_service
from meg_core.planner._types import (
    CalendarRule, CatalogueChoice, DateRangeChoice, ExplorationChoice, IndependentFact,
    PlantingTemplate, Profile, ScopeRequest, SearchPolicy, SowingWindowRule,
)
from meg_core.planner._validation import InputValidationError


def authorized(snapshot, kb, choices=(), **inputs):
    """Test-only explicit farmer confirmation, never performed by production preview."""
    draft = replace(snapshot, input=replace(snapshot.input, journey="explore", **inputs))
    preview = prepare_scope(ScopeRequest(snapshot=draft, choices=choices), kb)
    return replace(draft, input=replace(draft.input, exploration=preview.choices,
                                       exploration_confirmed=True, scope_hash=preview.scope_hash))


def date_choice(*days, sid="s2", cid="dates"):
    return ExplorationChoice(cid, sid, "sowing_date", tuple(days))


def support_date(kb, season, sow, *, harvest=None, release=None):
    """Explicit test calendar; not a generic duration formula."""
    rules = []
    for r in kb.rules:
        if r.profile_id == season.profile_id.value and isinstance(r, SowingWindowRule):
            r = replace(r, start=min(r.start, sow), end=max(r.end, sow))
        rules.append(r)
    base = next(r for r in rules if isinstance(r, CalendarRule) and r.profile_id == season.profile_id.value)
    h = harvest or base.harvest_or_cut_date
    end = h + timedelta(days=1)
    rules.append(replace(base, rule_id=base.rule_id + "-" + sow.isoformat(), sowing_date=sow,
                         harvest_or_cut_date=h, crop_end_exclusive=end, release_date=release or end))
    return replace(kb, rules=tuple(rules))


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.current, self.snapshot, self.kb = synthetic()
        # These tests explore sowing within an invented broad window while exact
        # endpoint mappings remain absent. M1's fixture window permits one day
        # only and correctly rejects any date outside it.
        self.kb = replace(self.kb, rules=tuple(
            replace(r, start=r.start - timedelta(days=45), end=r.end + timedelta(days=45))
            if isinstance(r, SowingWindowRule) else r for r in self.kb.rules))

    def test_no_permissions_checks_only_current(self):
        result = plan_service(self.snapshot, self.kb, SearchPolicy())
        self.assertEqual(result.current.status, "feasible")
        self.assertEqual(result.search.status, "complete")
        self.assertEqual(result.search.raw_count, 0)
        self.assertEqual(result.feasible_alternatives, ())

    def test_preview_does_not_authorize_and_hash_binds_input(self):
        choice = date_choice("2031-05-29")
        preview = prepare_scope(ScopeRequest(snapshot=self.snapshot, choices=(choice,)), self.kb)
        self.assertEqual(self.snapshot.input.exploration, ())
        unconfirmed = replace(self.snapshot, input=replace(self.snapshot.input, journey="explore", exploration=preview.choices))
        with self.assertRaises(InputValidationError):
            generate(unconfirmed, self.kb, SearchPolicy())
        confirmed = authorized(self.snapshot, self.kb, (choice,))
        stale = replace(confirmed, input=replace(confirmed.input, field_id="different-field"))
        with self.assertRaises(InputValidationError):
            generate(stale, self.kb, SearchPolicy())

    def test_date_only_invalidates_old_endpoints_and_preserves_other_intentions(self):
        snap = authorized(self.snapshot, self.kb, (date_choice("2031-05-29"),))
        candidate = generate(snap, self.kb, SearchPolicy()).candidates[0]
        self.assertEqual(candidate.evaluation.status, "needs_review")
        for name in ("harvest_or_cut_date", "crop_end_exclusive", "release_date"):
            fact = getattr(candidate.plan[1], name)
            self.assertIsNone(fact.value)
            self.assertEqual(fact.confirmation_status, "unconfirmed")
        self.assertEqual(candidate.plan[1].crop_id, self.current[1].crop_id)
        self.assertEqual(candidate.plan[2].sowing_date, self.current[2].sowing_date)
        self.assertEqual(self.current, self.snapshot.input.seasons)

    def test_supported_mapping_changes_review_to_feasible(self):
        choice = date_choice("2031-05-29")
        snap = authorized(self.snapshot, self.kb, (choice,))
        self.assertEqual(generate(snap, self.kb, SearchPolicy()).candidates[0].evaluation.status, "needs_review")
        kb = support_date(self.kb, self.current[1], date(2031, 5, 29))
        snap = authorized(self.snapshot, kb, (choice,))
        result = generate(snap, kb, SearchPolicy())
        self.assertEqual(result.candidates[0].evaluation.status, "feasible")
        self.assertEqual(result.search.feasible_count, 1)
        self.assertIn(SYNTHETIC[0], result.candidates[0].source_refs)

    def test_candidate_evaluations_reuse_promise_test(self):
        snap = authorized(self.snapshot, self.kb, (date_choice("2031-05-29", "2031-05-30"),))
        with patch.object(constraints, "evaluate", wraps=constraints.evaluate) as evaluator:
            result = generate(snap, self.kb, SearchPolicy())
        self.assertEqual(evaluator.call_count, result.search.evaluated_count)
        for candidate in result.candidates:
            self.assertEqual(candidate.evaluation, constraints.evaluate(candidate.plan, snap, self.kb))

    def test_exact_budget_exhaustion_and_truncation(self):
        snap = authorized(self.snapshot, self.kb, (date_choice("2031-05-29", "2031-05-30"),))
        exact = generate(snap, self.kb, SearchPolicy(raw_budget=2))
        limited = generate(snap, self.kb, SearchPolicy(raw_budget=1))
        self.assertEqual((exact.search.raw_count, exact.search.status), (2, "complete"))
        self.assertEqual((limited.search.raw_count, limited.search.status), (1, "incomplete"))
        self.assertEqual(limited.search.limit_reason, "candidate_budget")

    def test_large_ranges_are_lazy_and_budgeted(self):
        choice = DateRangeChoice("range", "s2", date(2031, 5, 29), date(9999, 12, 31))
        snap = authorized(self.snapshot, self.kb, (choice,))
        result = generate(snap, self.kb, SearchPolicy(raw_budget=3))
        self.assertEqual(result.search.raw_count, 3)
        self.assertEqual(result.search.evaluated_count, 3)
        self.assertEqual(result.search.limit_reason, "candidate_budget")

    def test_equivalent_permissions_stable_ids_and_output(self):
        a = date_choice("2031-05-30", "2031-05-29", "2031-05-29")
        b = date_choice("2031-05-29", "2031-05-30")
        first = generate(authorized(self.snapshot, self.kb, (a,)), self.kb, SearchPolicy())
        second = generate(authorized(self.snapshot, self.kb, (b,)), self.kb, SearchPolicy())
        self.assertEqual(first, second)

    def test_duplicates_merge_provenance(self):
        choices = (date_choice("2031-05-29", cid="a"), date_choice("2031-05-29", cid="b"),
                   DateRangeChoice("c", "s2", date(2031, 5, 29), date(2031, 5, 29)))
        result = generate(authorized(self.snapshot, self.kb, choices), self.kb, SearchPolicy())
        self.assertEqual(result.search.evaluated_count, 1)
        self.assertEqual(result.candidates[0].choice_ids, ("a", "b", "c"))

    def test_later_calendar_collision_is_rechecked(self):
        kb = support_date(self.kb, self.current[1], date(2031, 5, 29), harvest=date(2031, 11, 21))
        result = generate(authorized(self.snapshot, kb, (date_choice("2031-05-29"),)), kb, SearchPolicy())
        candidate = result.candidates[0]
        self.assertEqual(candidate.evaluation.status, "rejected")
        self.assertEqual(candidate.plan[2].sowing_date.value, date(2031, 11, 20))
        self.assertTrue(any(c.outcome == "fail" and c.season_ids == ("s2", "s3") for c in candidate.evaluation.checks))

    def test_nonadjacent_collision_not_hidden_by_unknown_middle(self):
        choices = (date_choice("2031-05-29", sid="s2"), date_choice("2031-05-19", sid="s3", cid="third"))
        result = generate(authorized(self.snapshot, self.kb, choices), self.kb, SearchPolicy())
        both = next(c for c in result.candidates if len(c.direct_season_ids) == 2)
        self.assertEqual(both.evaluation.status, "rejected")
        self.assertTrue(any(c.outcome == "fail" and c.season_ids == ("s1", "s3") for c in both.evaluation.checks))

    def test_all_four_seasons_and_minimal_edit_layers(self):
        choices = tuple(date_choice((s.sowing_date.value + timedelta(days=1)).isoformat(), sid=s.season_id, cid=s.season_id)
                        for s in self.current)
        result = generate(authorized(self.snapshot, self.kb, choices), self.kb, SearchPolicy())
        self.assertEqual(result.search.raw_count, 15)
        self.assertTrue(any(len(c.direct_season_ids) == 4 for c in result.candidates))

    def test_more_than_four_crops_and_missing_profile_choices(self):
        profiles = tuple(Profile(f"extra-{i}", f"fifth-plus-{i}", "grain", source_refs=SYNTHETIC, evidence_status="verified") for i in range(3))
        kb = replace(self.kb, profiles=self.kb.profiles + profiles)
        choices = (ExplorationChoice("crops", "s2", "crop_id", tuple(p.crop_id for p in profiles) + ("missing-crop",)),)
        result = generate(authorized(self.snapshot, kb, choices), kb, SearchPolicy())
        self.assertEqual(result.search.raw_count, 4)
        self.assertEqual(result.search.evaluated_count, 0)
        self.assertEqual(result.search.status, "incomplete")
        self.assertEqual(result.search.uninstantiated_choice_ids, ("crops",))

    def test_crop_substitution_and_dedup_of_automatic_profile_binding(self):
        profile = Profile("fifth", "fifth-crop", "grain", source_refs=SYNTHETIC, evidence_status="verified")
        base = self.current[1]
        extra = tuple(replace(r, rule_id="fifth-" + r.rule_id, profile_id="fifth",
                              **({"expected": "fifth-crop"} if getattr(r, "path", None) == "crop_id" else {}))
                      for r in self.kb.rules if r.profile_id == base.profile_id.value)
        kb = replace(self.kb, profiles=self.kb.profiles + (profile,), rules=self.kb.rules + extra)
        choices = (ExplorationChoice("crop", "s2", "crop_id", ("fifth-crop",)),
                   ExplorationChoice("profile", "s2", "profile_id", ("fifth",)))
        result = generate(authorized(self.snapshot, kb, choices), kb, SearchPolicy())
        self.assertEqual(result.search.raw_count, 3)
        self.assertEqual(result.search.evaluated_count, 1)
        self.assertEqual(result.search.duplicate_count, 1)
        self.assertEqual(result.candidates[0].plan[1].crop_id.value, "fifth-crop")
        self.assertEqual(result.candidates[0].kind, "crop_change")

    def test_protected_crop_permission_is_excluded_not_relaxed(self):
        from meg_core.planner._types import Commitment
        lock = Commitment("lock", "s2", "crop", known(self.current[1].crop_id.value))
        snapshot = replace(self.snapshot, input=replace(self.snapshot.input, commitments=(lock,)))
        choice = ExplorationChoice("crop", "s2", "crop_id", ("different",))
        result = generate(authorized(snapshot, self.kb, (choice,)), self.kb, SearchPolicy())
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.search.excluded_count, 1)
        self.assertEqual(result.search.status, "complete")

    def test_independent_confirmed_endpoint_retained(self):
        fact = IndependentFact("s2", "harvest_or_cut_date")
        snap = authorized(self.snapshot, self.kb, (date_choice("2031-05-29"),), independent_facts=(fact,))
        candidate = generate(snap, self.kb, SearchPolicy()).candidates[0]
        self.assertEqual(candidate.plan[1].harvest_or_cut_date, self.current[1].harvest_or_cut_date)
        self.assertIsNone(candidate.plan[1].release_date.value)

    def test_catalogue_preview_requires_explicit_crop_scope(self):
        request = ScopeRequest(snapshot=self.snapshot, catalogue_choices=(CatalogueChoice(
            "catalogue", "s2", "sowing_date", (self.current[1].crop_id.value,)),))
        preview = prepare_scope(request, self.kb)
        self.assertTrue(preview.choices)
        self.assertIn(self.current[1].crop_id.value, preview.available_crop_ids)
        self.assertEqual(preview.choices[0].allowed_values, ("2031-05-28",))

    def test_template_transfer_requires_explicit_permission_and_keeps_sources(self):
        template = PlantingTemplate(template_id="trial", profile_id=self.current[1].profile_id.value,
                                    season_label="summer-2020", sowing_date=date(2020, 6, 2),
                                    harvest_or_cut_date=date(2020, 9, 21), source_refs=SYNTHETIC)
        kb = replace(self.kb, templates=(template,))
        choices = (date_choice("2031-06-02"),)
        snap = authorized(self.snapshot, kb, choices, authorized_template_ids=("trial",))
        no_transfer = generate(snap, kb, SearchPolicy()).candidates[0]
        self.assertIsNone(no_transfer.plan[1].harvest_or_cut_date.value)
        snap = authorized(self.snapshot, kb, choices, authorized_template_ids=("trial",), hypothetical_template_ids=("trial",))
        candidate = generate(snap, kb, SearchPolicy()).candidates[0]
        self.assertEqual(candidate.plan[1].harvest_or_cut_date.value, date(2031, 9, 21))
        self.assertIsNone(candidate.plan[1].release_date.value)
        self.assertEqual(candidate.evaluation.status, "needs_review")
        self.assertEqual(candidate.template_ids, ("trial",))

    def test_grouping_limits_display_not_search_counts(self):
        kb = self.kb
        days = (date(2031, 5, 29), date(2031, 5, 30), date(2031, 5, 31))
        for day in days:
            kb = support_date(kb, self.current[1], day)
        result = plan_service(authorized(self.snapshot, kb, (date_choice(*(d.isoformat() for d in days)),)), kb, SearchPolicy())
        self.assertEqual(result.search.feasible_count, 3)
        self.assertEqual(len(result.feasible_alternatives), 1)
        self.assertEqual(result.feasible_alternatives[0].plan[1].sowing_date.value, days[0])

    def test_invalid_policies_and_inputs_raise(self):
        for policy in (SearchPolicy(raw_budget=0), SearchPolicy(raw_budget=True), SearchPolicy(ordering_version="unsupported")):
            with self.assertRaises(InputValidationError):
                generate(self.snapshot, self.kb, policy)
        for choice in (date_choice("not-a-date"), date_choice("2031-05-29", sid="missing"),
                       ExplorationChoice("bad", "s2", "purpose", ("forage",))):
            with self.assertRaises(InputValidationError):
                prepare_scope(ScopeRequest(snapshot=self.snapshot, choices=(choice,)), self.kb)


class GeneratedReference(unittest.TestCase):
    def test_actual_uh001_generation_two_reviews_zero_feasible(self):
        current, snapshot, kb = uh001()
        choices = (date_choice("2027-05-28", "2027-06-01"),
                   ExplorationChoice("s4-maize", "s4", "crop_id", ("grain_maize",)))
        independent = tuple(IndependentFact(f"s{i}", "preparation_days_after_release",
                                            ("crop_id", "profile_id", "next.crop_id", "next.profile_id")) for i in range(1, 4))
        snap = authorized(snapshot, kb, choices, independent_facts=independent)
        result = plan_service(snap, kb, SearchPolicy())
        self.assertEqual(result.current.status, "rejected")
        self.assertEqual(result.current.checks[0].explanation.code, "sowing_before_protected_cut")
        self.assertEqual(result.search.raw_count, 5)
        self.assertEqual(result.search.evaluated_count, 2)
        self.assertEqual(result.search.uninstantiated_choice_ids, ("s4-maize",))
        self.assertEqual(result.search.limit_reason, "uninstantiated_choices")
        self.assertEqual(result.feasible_alternatives, ())
        self.assertEqual({c.plan[1].sowing_date.value for c in result.review_investigations},
                         {date(2027, 5, 28), date(2027, 6, 1)})
        for candidate in result.review_investigations:
            self.assertEqual(candidate.plan[0].harvest_or_cut_date, current[0].harvest_or_cut_date)
            self.assertIsNone(candidate.plan[1].release_date.value)


if __name__ == "__main__":
    unittest.main()
