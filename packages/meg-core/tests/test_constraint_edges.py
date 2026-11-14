"""Boundary and malformed-input cases, using only synthetic support."""

from dataclasses import FrozenInstanceError, replace
from datetime import date
import unittest

from test_constraints import SYNTHETIC, changed, known, synthetic, unknown
from meg_core.planner.constraints import evaluate
from meg_core.planner._types import Commitment, Condition, FactRule, Profile
from meg_core.planner._validation import InputValidationError


class EdgeCases(unittest.TestCase):
    def setUp(self):
        self.plan, self.snapshot, self.kb = synthetic()

    def test_supported_zero_preparation_allows_release_equality(self):
        release = self.plan[0].release_date.value
        plan = changed(self.plan, 0, preparation_days_after_release=known(0, unit="day"))
        plan = changed(plan, 1, sowing_date=known(release))
        rules = []
        for rule in self.kb.rules:
            if rule.rule_id == "s1-preparation":
                rule = replace(rule, days=0)
            elif rule.rule_id == "s2-sowing":
                rule = replace(rule, start=release, end=release)
            elif rule.rule_id == "s2-calendar":
                rule = replace(rule, sowing_date=release)
            rules.append(rule)
        self.assertEqual(evaluate(plan, self.snapshot, replace(self.kb, rules=tuple(rules))).status, "feasible")
        # Identical arithmetic without a sourced preparation rule is unresolved.
        rules = tuple(r for r in rules if r.rule_id != "s1-preparation")
        self.assertEqual(evaluate(plan, self.snapshot, replace(self.kb, rules=rules)).status, "needs_review")

    def test_inclusive_window_first_last_and_outside(self):
        rules = tuple(replace(r, start=date(2031, 5, 28), end=date(2031, 5, 31))
                      if r.rule_id == "s2-sowing" else r for r in self.kb.rules)
        for sow, expected in ((date(2031, 5, 28), "pass"), (date(2031, 5, 31), "pass"), (date(2031, 6, 1), "fail")):
            plan = changed(self.plan, 1, sowing_date=known(sow))
            result = evaluate(plan, self.snapshot, replace(self.kb, rules=rules))
            self.assertEqual(next(c.outcome for c in result.checks if c.rule_id == "s2-sowing"), expected)

    def test_changed_locked_crop_and_purpose_rejected(self):
        for kind, crop, purpose in (("crop", "different-crop", "grain"), ("purpose", "synthetic-crop-1", "forage")):
            lock = Commitment("lock", "s1", kind, known("synthetic-crop-1" if kind == "crop" else "grain"))
            snapshot = replace(self.snapshot, input=replace(self.snapshot.input, commitments=(lock,)))
            plan = changed(self.plan, 0, crop_id=known(crop), purpose=known(purpose), profile_id=known("different-profile"))
            kb = replace(self.kb, profiles=self.kb.profiles + (Profile("different-profile", crop, purpose),))
            result = evaluate(plan, snapshot, kb)
            self.assertEqual(result.status, "rejected")
            self.assertNotIn("lock", result.preserved_commitment_ids)

    def test_occupation_lock_rejects_early_release(self):
        lock = Commitment("lock", "s1", "occupation_through", known("2031-05-21"))
        snapshot = replace(self.snapshot, input=replace(self.snapshot.input, commitments=(lock,)))
        self.assertEqual(evaluate(self.plan, snapshot, self.kb).status, "rejected")

    def test_leap_day_uses_calendar_day_arithmetic(self):
        plan = changed(self.plan, 2, harvest_or_cut_date=known(date(2032, 2, 28)),
                       crop_end_exclusive=known(date(2032, 2, 29)), release_date=known(date(2032, 2, 29)),
                       preparation_days_after_release=known(1, unit="day"))
        plan = changed(plan, 3, sowing_date=known(date(2032, 3, 1)))
        kb = replace(self.kb, rules=tuple(replace(r, days=1) if r.rule_id == "s3-preparation" else r for r in self.kb.rules))
        result = evaluate(plan, self.snapshot, kb)
        check = next(c for c in result.checks if c.rule_id == "transition_preparation" and c.season_ids == ("s3", "s4"))
        self.assertEqual(check.outcome, "pass")
        self.assertEqual(check.explanation.params["earliest_sowing_date"], "2032-03-01")

    def test_empty_topic_registry_cannot_disable_minimum_coverage(self):
        kb = replace(self.kb, rules=(), required_planning_topics=())
        self.assertEqual(evaluate(self.plan, self.snapshot, kb).status, "needs_review")

    def test_missing_identity_fact_cannot_be_covered_by_another_fact(self):
        for field in ("crop_id", "purpose", "profile_id"):
            with self.subTest(field=field):
                plan = changed(self.plan, 0, **{field: unknown()})
                self.assertEqual(evaluate(plan, self.snapshot, self.kb).status, "needs_review")

    def test_missing_rule_sources_cannot_establish_support(self):
        kb = replace(self.kb, rules=tuple(replace(r, source_refs=()) for r in self.kb.rules))
        self.assertEqual(evaluate(self.plan, self.snapshot, kb).status, "needs_review")

    def test_proposed_zero_preparation_rule_cannot_establish_support(self):
        kb = replace(self.kb, rules=tuple(replace(r, evidence_status="proposed")
                                        if r.rule_id == "s1-preparation" else r for r in self.kb.rules))
        self.assertEqual(evaluate(self.plan, self.snapshot, kb).status, "needs_review")

    def test_results_are_immutable(self):
        result = evaluate(self.plan, self.snapshot, self.kb)
        with self.assertRaises(TypeError):
            result.checks[0].explanation.params["new"] = "value"
        with self.assertRaises(FrozenInstanceError):
            result.status = "rejected"

    def test_null_with_invalid_unit_is_structural_error(self):
        plan = changed(self.plan, 0, preparation_days_after_release=unknown(unit="hours"))
        with self.assertRaises(InputValidationError):
            evaluate(plan, self.snapshot, self.kb)

    def test_malformed_nested_records_raise_typed_error(self):
        cases = (
            (self.plan, replace(self.snapshot, input=None), self.kb),
            (self.plan, self.snapshot, replace(self.kb, profiles=(object(),))),
            (self.plan, self.snapshot, replace(self.kb, rules=(object(),))),
            (self.plan, replace(self.snapshot, input=replace(self.snapshot.input, commitments=(object(),))), self.kb),
            (self.plan, replace(self.snapshot, input=replace(self.snapshot.input, field_facts=(("broken",),))), self.kb),
        )
        for args in cases:
            with self.subTest(args=repr(args)[:40]), self.assertRaises(InputValidationError):
                evaluate(*args)

    def test_nonfinite_or_malformed_rule_rejected(self):
        first = self.kb.rules[0]
        variants = (replace(first, expected=float("nan")),
                    replace(first, applicability=(Condition("site_id", float("inf")),)),
                    replace(first, applicability=[]),
                    replace(first, path="forecast.rain"))
        for rule in variants:
            with self.subTest(rule=rule), self.assertRaises(InputValidationError):
                evaluate(self.plan, self.snapshot, replace(self.kb, rules=(rule,)))

    def test_malformed_commitment_season_id_is_typed_error(self):
        lock = Commitment("lock", [], "crop", known("synthetic-crop-1"))
        snapshot = replace(self.snapshot, input=replace(self.snapshot.input, commitments=(lock,)))
        with self.assertRaises(InputValidationError):
            evaluate(self.plan, snapshot, self.kb)

    def test_wrong_predicate_cannot_discharge_calendar_topic(self):
        rule = FactRule(rule_id="bad-calendar-coverage", rule_version="test",
                        profile_id="synthetic-profile-1", topic="harvest_crop_end_release",
                        source_refs=SYNTHETIC, evidence_status="verified", path="crop_id",
                        expected="synthetic-crop-1")
        with self.assertRaises(InputValidationError):
            evaluate(self.plan, self.snapshot, replace(self.kb, rules=(rule,)))

    def test_unconfirmed_snapshot_rejected_but_candidate_proposal_allowed(self):
        candidate = changed(self.plan, 1, sowing_date=replace(self.plan[1].sowing_date, confirmation_status="unconfirmed"))
        self.assertEqual(evaluate(candidate, self.snapshot, self.kb).status, "feasible")
        snapshot = replace(self.snapshot, input=replace(self.snapshot.input, seasons=candidate))
        with self.assertRaises(InputValidationError):
            evaluate(candidate, snapshot, self.kb)


if __name__ == "__main__":
    unittest.main()
