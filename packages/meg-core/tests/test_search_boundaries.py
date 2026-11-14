"""Permission, resource, provenance and boundary regressions for the full service."""

from dataclasses import replace
from datetime import date, timedelta
import unittest

from test_constraints import SYNTHETIC, known, synthetic, unknown
from test_generation import authorized, date_choice, support_date
from meg_core.planner.constraints import evaluate
from meg_core.planner.generate import generate
from meg_core.planner.scope import prepare_scope
from meg_core.planner.service import plan
from meg_core.planner._types import (
    CalendarRule, CatalogueChoice, Commitment, Condition, DateRangeChoice,
    ExplorationChoice, IndependentFact, PlantingTemplate, ScopeRequest, SearchPolicy,
    SowingWindowRule, SourceRef,
)
from meg_core.planner._validation import InputValidationError


class SearchBoundaries(unittest.TestCase):
    def setUp(self):
        self.current, self.snapshot, self.kb = synthetic()

    def test_default_256_budget_and_exact_exhaustion(self):
        for length, status in ((256, "complete"), (257, "incomplete")):
            with self.subTest(length=length):
                start = self.current[1].sowing_date.value + timedelta(days=1)
                choices = (DateRangeChoice("dates", "s2", start, start + timedelta(days=length - 1)),)
                result = generate(authorized(self.snapshot, self.kb, choices), self.kb, SearchPolicy())
                self.assertEqual(result.search.raw_count, 256)
                self.assertEqual(result.search.evaluated_count, 256)
                self.assertEqual(result.search.status, status)

    def test_full_cartesian_count_255_and_truncated_624(self):
        for alternatives, raw, status in ((3, 255, "complete"), (4, 256, "incomplete")):
            with self.subTest(alternatives=alternatives):
                choices = tuple(date_choice(*((s.sowing_date.value + timedelta(days=d)).isoformat()
                                              for d in range(1, alternatives + 1)), sid=s.season_id, cid=s.season_id)
                                for s in self.current)
                result = generate(authorized(self.snapshot, self.kb, choices), self.kb, SearchPolicy())
                self.assertEqual((result.search.raw_count, result.search.status), (raw, status))
                if alternatives == 3:
                    self.assertEqual(result.search.evaluated_count, 255)

    def test_choice_and_rule_permutations_are_deterministic(self):
        choices = (date_choice("2031-05-29", cid="b"), date_choice("2031-05-30", cid="a"))
        a = generate(authorized(self.snapshot, self.kb, choices), self.kb, SearchPolicy())
        other = replace(self.kb, profiles=tuple(reversed(self.kb.profiles)), rules=tuple(reversed(self.kb.rules)))
        b = generate(authorized(self.snapshot, other, tuple(reversed(choices))), other, SearchPolicy())
        self.assertEqual(a, b)

    def test_source_reference_order_does_not_change_candidate_id(self):
        refs = SYNTHETIC + (SourceRef("SECOND-SYNTHETIC", "test"),)
        a = replace(self.kb, rules=tuple(replace(r, source_refs=refs) for r in self.kb.rules))
        b = replace(a, rules=tuple(replace(r, source_refs=tuple(reversed(refs))) for r in a.rules))
        choices = (date_choice("2031-05-29"),)
        ca = generate(authorized(self.snapshot, a, choices), a, SearchPolicy()).candidates[0]
        cb = generate(authorized(self.snapshot, b, choices), b, SearchPolicy()).candidates[0]
        self.assertEqual(ca.candidate_id, cb.candidate_id)

    def test_changed_evidence_version_changes_candidate_identity(self):
        choices = (date_choice("2031-05-29"),)
        a = generate(authorized(self.snapshot, self.kb, choices), self.kb, SearchPolicy()).candidates[0]
        kb = replace(self.kb, rules=tuple(replace(r, rule_version="new-synthetic-version") for r in self.kb.rules))
        b = generate(authorized(self.snapshot, kb, choices), kb, SearchPolicy()).candidates[0]
        self.assertNotEqual(a.candidate_id, b.candidate_id)

    def test_conflicting_endpoint_mappings_do_not_pick_one(self):
        sow = date(2031, 5, 29)
        kb = support_date(self.kb, self.current[1], sow)
        rule = next(r for r in kb.rules if isinstance(r, CalendarRule) and r.sowing_date == sow)
        kb = replace(kb, rules=kb.rules + (replace(rule, rule_id="conflicting-calendar", harvest_or_cut_date=date(2031, 9, 19)),))
        candidate = generate(authorized(self.snapshot, kb, (date_choice(sow.isoformat()),)), kb, SearchPolicy()).candidates[0]
        self.assertIsNone(candidate.plan[1].harvest_or_cut_date.value)
        self.assertEqual(candidate.evaluation.status, "needs_review")

    def test_unknown_preparation_is_never_replaced_by_zero(self):
        kb = replace(self.kb, rules=tuple(r for r in self.kb.rules if r.topic != "transition_preparation"))
        candidate = generate(authorized(self.snapshot, kb, (date_choice("2031-05-29"),)), kb, SearchPolicy()).candidates[0]
        self.assertIsNone(candidate.plan[0].preparation_days_after_release.value)
        self.assertIsNone(candidate.plan[1].preparation_days_after_release.value)

    def test_independence_dependencies_are_rechecked(self):
        item = IndependentFact("s2", "harvest_or_cut_date", ("sowing_date",))
        snapshot = authorized(self.snapshot, self.kb, (date_choice("2031-05-29"),), independent_facts=(item,))
        self.assertIsNone(generate(snapshot, self.kb, SearchPolicy()).candidates[0].plan[1].harvest_or_cut_date.value)

    def test_protected_cut_is_preserved_and_impossible_branch_excluded(self):
        lock = Commitment("cut", "s2", "harvest_or_cut_date", known("2031-09-20"))
        snap = replace(self.snapshot, input=replace(self.snapshot.input, commitments=(lock,)))
        result = generate(authorized(snap, self.kb, (date_choice("2031-05-29", "2031-10-01"),)), self.kb, SearchPolicy())
        self.assertEqual(result.search.excluded_count, 1)
        self.assertEqual(result.candidates[0].plan[1].harvest_or_cut_date.value, date(2031, 9, 20))

    def test_display_at_most_two_does_not_stop_enumeration(self):
        choices, kb = [], self.kb
        for season in self.current[:3]:
            sow = season.sowing_date.value + timedelta(days=1)
            kb = support_date(kb, season, sow)
            choices.append(date_choice(sow.isoformat(), sid=season.season_id, cid=season.season_id))
        result = plan(authorized(self.snapshot, kb, tuple(choices)), kb, SearchPolicy())
        self.assertEqual(result.search.raw_count, 7)
        self.assertEqual(result.search.feasible_count, 7)
        self.assertEqual(len(result.feasible_alternatives), 2)
        self.assertEqual(result.search.status, "complete")

    def test_invalid_derived_intervals_are_exclusions_not_invalid_wire_plans(self):
        item = IndependentFact("s2", "harvest_or_cut_date")
        result = generate(authorized(self.snapshot, self.kb, (date_choice("2031-10-01"),), independent_facts=(item,)), self.kb, SearchPolicy())
        self.assertEqual(result.search.evaluated_count, 0)
        self.assertEqual(result.search.excluded_count, 1)

    def test_unsupported_catalogue_query_survives_confirmation(self):
        snap = replace(self.snapshot, input=replace(self.snapshot.input, journey="explore"))
        preview = prepare_scope(ScopeRequest(snapshot=snap, catalogue_choices=(CatalogueChoice("none", "s2", "crop_id", ("absent",)),)), self.kb)
        self.assertEqual(preview.choices, ())
        self.assertTrue(preview.issues)
        snap = replace(snap, input=replace(snap.input, exploration=preview.choices, pending_scope_issues=preview.issues,
                                          scope_hash=preview.scope_hash, exploration_confirmed=True))
        result = generate(snap, self.kb, SearchPolicy())
        self.assertEqual(result.search.status, "incomplete")
        self.assertEqual(result.search.uninstantiated_choice_ids, ("none",))

    def test_scope_preview_reports_unknown_catalogue_and_locked_choices(self):
        lock = Commitment("locked", "s2", "crop", known("synthetic-crop-2"))
        snap = replace(self.snapshot, input=replace(self.snapshot.input, commitments=(lock,)))
        choices = (ExplorationChoice("locked-choice", "s2", "crop_id", ("missing",)),
                   ExplorationChoice("unknown", "s4", "crop_id", ("missing",)))
        preview = prepare_scope(ScopeRequest(snapshot=snap, choices=choices), self.kb)
        self.assertTrue(any(i.kind == "excluded" and "locked-choice" in i.choice_ids for i in preview.issues))
        self.assertTrue(any(i.kind == "blocked" and "unknown" in i.choice_ids for i in preview.issues))

    def test_unconfirmed_preview_can_be_bound_after_explicit_fact_confirmation(self):
        draft_plan = tuple(replace(s, sowing_date=replace(s.sowing_date, confirmation_status="unconfirmed")) for s in self.current)
        draft = replace(self.snapshot, input=replace(self.snapshot.input, seasons=draft_plan, journey="explore"))
        preview = prepare_scope(ScopeRequest(snapshot=draft, choices=(date_choice("2031-05-29"),)), self.kb)
        confirmed = replace(self.snapshot, input=replace(self.snapshot.input, journey="explore", exploration=preview.choices,
                                                         scope_hash=preview.scope_hash, exploration_confirmed=True))
        self.assertEqual(generate(confirmed, self.kb, SearchPolicy()).search.evaluated_count, 1)

    def test_bad_shapes_and_release_mismatch_are_structural(self):
        for snapshot in (None, replace(self.snapshot, input=None), replace(self.snapshot, data_release="wrong")):
            with self.subTest(snapshot=snapshot), self.assertRaises(InputValidationError):
                prepare_scope(ScopeRequest(snapshot=snapshot), self.kb)
        for query in (ExplorationChoice("x", "s2", "crop_id", ()), DateRangeChoice("x", "s2", date(2031, 6, 1), date(2031, 5, 1)),
                      DateRangeChoice("x", "s2", date(2031, 6, 1), date(2031, 6, 2), step_days=True)):
            with self.assertRaises(InputValidationError):
                prepare_scope(ScopeRequest(snapshot=self.snapshot, choices=(query,)), self.kb)

    def test_empty_kb_has_honest_unknowns_and_no_crash(self):
        from meg_core.planner._types import KnowledgeBase
        kb = KnowledgeBase(data_release=self.kb.data_release)
        result = plan(authorized(self.snapshot, kb, (date_choice("2031-05-29"),)), kb, SearchPolicy())
        self.assertEqual(result.current.status, "needs_review")
        self.assertEqual(result.search.evaluated_count, 0)
        self.assertEqual(result.search.status, "incomplete")

    def test_unknown_baseline_sowing_accepts_only_explicit_proposal(self):
        seasons = (self.current[0], replace(self.current[1], sowing_date=unknown()), *self.current[2:])
        snap = replace(self.snapshot, input=replace(self.snapshot.input, seasons=seasons))
        result = generate(authorized(snap, self.kb, (date_choice("2031-05-28"),)), self.kb, SearchPolicy())
        self.assertEqual(result.search.evaluated_count, 1)
        self.assertEqual(result.candidates[0].plan[1].sowing_date.value, date(2031, 5, 28))

    def test_changed_profile_does_not_keep_old_endpoints(self):
        profile = replace(self.kb.profiles[1], profile_id="new-cultivar")
        window = next(r for r in self.kb.rules if isinstance(r, SowingWindowRule) and r.profile_id == profile.profile_id.replace("new-cultivar", "synthetic-profile-2"))
        kb = replace(self.kb, profiles=self.kb.profiles + (profile,), rules=self.kb.rules + (
            replace(window, rule_id="new-window", profile_id=profile.profile_id),))
        choice = ExplorationChoice("cultivar", "s2", "profile_id", (profile.profile_id,))
        candidate = generate(authorized(self.snapshot, kb, (choice,)), kb, SearchPolicy()).candidates[0]
        self.assertIsNone(candidate.plan[1].release_date.value)
        self.assertEqual(candidate.kind, "crop_change")


if __name__ == "__main__":
    unittest.main()
