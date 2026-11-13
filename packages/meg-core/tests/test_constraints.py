"""Promise Test regressions. Positive evidence below is SYNTHETIC, never agronomy."""

import ast
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from meg_core.planner import constraints
from meg_core.planner._types import (
    CalendarRule, Commitment, Condition, Fact, FactRule, KnowledgeBase,
    PreparationRule, ProductionRequirement, Profile, RotationRule,
    ScenarioInput, ScenarioSnapshot, SeasonInput, SourceRef, SowingWindowRule,
)
from meg_core.planner._validation import InputValidationError


SYNTHETIC = (SourceRef("SYNTHETIC-ONLY", "algorithm fixture; no agricultural evidence"),)
REFERENCE = (SourceRef("UH-001-v1", "sections 2-3"),)


def known(value, *, refs=SYNTHETIC, unit=None, illustrative=False):
    return Fact(value=value, unit=unit, unknown_reason=None,
                origin="illustrative" if illustrative else "field_measurement",
                evidence_status="proposed" if illustrative else "verified",
                confirmation_status="confirmed", source_refs=refs)


def unknown(reason="not_established", *, unit=None):
    return Fact(value=None, unit=unit, unknown_reason=reason, origin="unknown",
                evidence_status="open", confirmation_status="confirmed_unknown")


def synthetic():
    """Four intentionally invented seasons and exact supporting rules."""
    slots = (("winter", 2030, date(2030, 11, 20), date(2031, 5, 20)),
             ("summer", 2031, date(2031, 5, 28), date(2031, 9, 20)),
             ("winter", 2031, date(2031, 11, 20), date(2032, 4, 25)),
             ("summer", 2032, date(2032, 6, 1), date(2032, 9, 21)))
    seasons, profiles, rules = [], [], []
    for i, (kind, year, sow, harvest) in enumerate(slots, 1):
        sid, pid, crop = f"s{i}", f"synthetic-profile-{i}", f"synthetic-crop-{i}"
        season = SeasonInput(
            season_id=sid, order=i, season_label=f"{kind}-{year}",
            crop_id=known(crop), purpose=known("grain"), profile_id=known(pid),
            sowing_date=known(sow), harvest_or_cut_date=known(harvest),
            crop_end_exclusive=known(harvest + timedelta(days=1)),
            release_date=known(harvest + timedelta(days=1)),
            preparation_days_after_release=known(7, unit="day") if i < 4 else unknown(unit="day"))
        seasons.append(season)
        profiles.append(Profile(pid, crop, "grain"))
        base = dict(rule_version="synthetic-v1", profile_id=pid,
                    source_refs=SYNTHETIC, evidence_status="verified",
                    applicability=(Condition("site_id", "synthetic-site"),
                                   Condition("season_label", season.season_label)))
        for topic, path, expected in (
            ("identity_purpose", "crop_id", crop),
            ("local_cultivar_field_fit", "field.cultivar_available", "yes"),
            ("irrigation_constraints", "field.irrigation", "available"),
        ):
            rules.append(FactRule(**base, rule_id=f"{sid}-{topic}", topic=topic,
                                  path=path, expected=expected))
        rules.append(SowingWindowRule(**base, rule_id=f"{sid}-sowing", topic="sowing_support",
                                      start=sow, end=sow))
        rules.append(CalendarRule(**base, rule_id=f"{sid}-calendar", topic="harvest_crop_end_release",
                                  sowing_date=sow, harvest_or_cut_date=harvest,
                                  crop_end_exclusive=harvest + timedelta(days=1),
                                  release_date=harvest + timedelta(days=1)))
        if i < 4:
            rules.append(PreparationRule(**base, rule_id=f"{sid}-preparation",
                                         topic="transition_preparation", days=7,
                                         next_profile_id=f"synthetic-profile-{i + 1}"))
    plan = tuple(seasons)
    snapshot = ScenarioSnapshot(
        data_release="synthetic-only-v1",
        input=ScenarioInput(seasons=plan, site_id="synthetic-site", field_id="one-field",
                            field_facts=(("cultivar_available", known("yes")),
                                         ("irrigation", known("available")))))
    kb = KnowledgeBase(data_release=snapshot.data_release, profiles=tuple(profiles), rules=tuple(rules))
    return plan, snapshot, kb


def uh001():
    """Only the recovered reference intentions; its blank S1 sowing stays unknown."""
    rows = (
        ("winter-2026", "berseem", "forage", None, "2027-05-20"),
        ("summer-2027", "grain_maize", "grain", "2027-05-15", "2027-09-20"),
        ("winter-2027", "wheat", "grain", "2027-11-20", "2028-04-25"),
        ("summer-2028", "grain_sorghum", "grain", "2028-06-01", "2028-09-21"),
    )
    def fact(value, unit=None):
        return known(value, refs=REFERENCE, unit=unit, illustrative=True)
    seasons, profiles = [], []
    for i, (label, crop, purpose, sow, harvest) in enumerate(rows, 1):
        h = date.fromisoformat(harvest)
        pid = f"reference-{crop}"
        profiles.append(Profile(pid, crop, purpose))
        seasons.append(SeasonInput(
            season_id=f"s{i}", order=i, season_label=label,
            crop_id=fact(crop), purpose=fact(purpose), profile_id=fact(pid),
            sowing_date=fact(date.fromisoformat(sow)) if sow else unknown("blank_in_recovered_reference"),
            harvest_or_cut_date=fact(h), crop_end_exclusive=fact(h + timedelta(days=1)),
            release_date=fact(h + timedelta(days=1)),
            preparation_days_after_release=fact(7, "day") if i < 4 else unknown(unit="day")))
    locks = (
        Commitment("cut", "s1", "harvest_or_cut_date", fact("2027-05-20")),
        Commitment("occupation", "s1", "occupation_through", fact("2027-05-20")),
        Commitment("maize", "s2", "crop", fact("grain_maize")),
        Commitment("maize-purpose", "s2", "purpose", fact("grain")),
        Commitment("wheat", "s3", "crop", fact("wheat")),
        Commitment("wheat-purpose", "s3", "purpose", fact("grain")),
    )
    plan = tuple(seasons)
    snapshot = ScenarioSnapshot(data_release="UH-001-fixture-not-runtime",
                                input=ScenarioInput(seasons=plan, commitments=locks,
                                                    site_id="sakha", field_id="one-field",
                                                    production_requirements=(ProductionRequirement(
                                                        "feed", ("s1",), unknown(unit="kg"), hard=False),)))
    # Open reference review gates, NOT an activated agricultural rule release.
    gates = []
    for profile in profiles:
        for field, code, topic, required_for in (
            ("soil", "soil_suitability_unknown", "local_cultivar_field_fit", "planning"),
            ("drainage", "soil_suitability_unknown", "local_cultivar_field_fit", "planning"),
            ("cultivar", "cultivar_availability_unknown", "local_cultivar_field_fit", "planning"),
            ("irrigation", "irrigation_availability_unknown", "irrigation_constraints", "planning"),
            ("stages", "crop_stages_unavailable", "demand", "etc"),
        ):
            gates.append(FactRule(rule_id=f"{profile.profile_id}-{field}-open", rule_version="reference-v1",
                                  profile_id=profile.profile_id, topic=topic, effect="review",
                                  required_for=required_for, evidence_status="open", source_refs=REFERENCE,
                                  path=f"field.{field}", expected="supported", unknown_code=code))
    gates.append(FactRule(rule_id="sorghum-eligibility-open", rule_version="reference-v1",
                          profile_id="reference-grain_sorghum", topic="local_cultivar_field_fit",
                          effect="review", evidence_status="open", source_refs=REFERENCE,
                          path="field.sorghum_eligibility", expected="supported",
                          unknown_code="sorghum_local_eligibility_open"))
    return plan, snapshot, KnowledgeBase(data_release=snapshot.data_release, profiles=tuple(profiles), rules=tuple(gates))


def changed(plan, index, **fields):
    return plan[:index] + (replace(plan[index], **fields),) + plan[index + 1:]


class PromiseTest(unittest.TestCase):
    def setUp(self):
        self.plan, self.snapshot, self.kb = synthetic()

    def evaluate(self, plan=None, snapshot=None, kb=None):
        return constraints.evaluate(self.plan if plan is None else plan,
                                    self.snapshot if snapshot is None else snapshot,
                                    self.kb if kb is None else kb)

    def check(self, result, code):
        return next(c for c in result.checks if c.explanation.code == code)

    def test_complete_synthetic_case_feasible(self):
        result = self.evaluate()
        self.assertEqual(result.status, "feasible")
        self.assertTrue(all(ref.source_id == "SYNTHETIC-ONLY"
                            for rule in self.kb.rules for ref in rule.source_refs))

    def test_occupancy_rejected(self):
        result = self.evaluate(changed(self.plan, 1, sowing_date=known(date(2031, 5, 19))))
        self.assertEqual(result.status, "rejected")
        self.check(result, "field_occupied")

    def test_preparation_boundary(self):
        for day, outcome in ((27, "fail"), (28, "pass")):
            with self.subTest(day=day):
                result = self.evaluate(changed(self.plan, 1, sowing_date=known(date(2031, 5, day))))
                check = next(c for c in result.checks if c.rule_id == "transition_preparation"
                             and c.season_ids == ("s1", "s2"))
                self.assertEqual(check.outcome, outcome)

    def test_unknown_preparation_not_zero(self):
        result = self.evaluate(changed(self.plan, 0, preparation_days_after_release=unknown(unit="day")))
        self.assertEqual(result.status, "needs_review")
        self.assertIn("plan.s1.preparation_days_after_release",
                      self.check(result, "transition_timing_unknown").missing_input_paths)

    def test_empty_and_incomplete_kb_never_feasible(self):
        for kb in (KnowledgeBase(data_release=self.kb.data_release),
                   replace(self.kb, rules=()),
                   replace(self.kb, rules=tuple(r for r in self.kb.rules if r.topic != "irrigation_constraints"))):
            with self.subTest(rules=len(kb.rules)):
                self.assertEqual(self.evaluate(kb=kb).status, "needs_review")

    def test_missing_endpoints_review_and_paths(self):
        result = self.evaluate(changed(self.plan, 3, crop_end_exclusive=unknown(), release_date=unknown()))
        self.assertEqual(result.status, "needs_review")
        paths = {p for c in result.checks for p in c.missing_input_paths}
        self.assertIn("plan.s4.crop_end_exclusive", paths)
        self.assertIn("plan.s4.release_date", paths)

    def test_hard_fail_beats_unknown(self):
        plan = changed(self.plan, 1, sowing_date=known(date(2031, 5, 19)))
        result = self.evaluate(plan, kb=replace(self.kb, rules=()))
        self.assertEqual(result.status, "rejected")
        self.assertTrue(any(c.outcome == "unknown" for c in result.checks))

    def test_unknown_middle_cannot_hide_earlier_conflict(self):
        plan = changed(self.plan, 1, sowing_date=unknown(), release_date=unknown())
        plan = changed(plan, 2, sowing_date=known(date(2031, 5, 19)))
        result = self.evaluate(plan)
        self.assertTrue(any(c.outcome == "fail" and c.season_ids == ("s1", "s3")
                            for c in result.checks))

    def test_unknown_release_lower_bound_can_fail_but_not_pass(self):
        plan = changed(self.plan, 0, release_date=unknown())
        failed = self.evaluate(changed(plan, 1, sowing_date=known(date(2031, 5, 27))))
        self.check(failed, "preparation_shortfall")
        later = self.evaluate(plan)
        self.assertEqual(later.status, "needs_review")
        self.check(later, "transition_timing_unknown")

    def test_earlier_slot_start_proves_order_conflict(self):
        plan = changed(self.plan, 1, sowing_date=known(date(2030, 11, 19)))
        self.check(self.evaluate(plan), "season_order_conflict")

    def test_lock_changes_fail_without_mutation(self):
        for kind, field, protected, replacement in (
            ("crop", "crop_id", "synthetic-crop-1", None),
            ("purpose", "purpose", "grain", None),
            ("harvest_or_cut_date", "harvest_or_cut_date", "2031-05-20", date(2031, 5, 19)),
        ):
            lock = Commitment("lock", "s1", kind, known(protected))
            snapshot = replace(self.snapshot, input=replace(self.snapshot.input, commitments=(lock,)))
            plan = changed(self.plan, 0, **{field: unknown() if replacement is None else known(replacement)})
            before = repr((plan, snapshot, self.kb))
            result = self.evaluate(plan, snapshot)
            self.assertEqual(result.status, "needs_review" if replacement is None else "rejected")
            self.assertEqual(repr((plan, snapshot, self.kb)), before)
            self.assertNotIn("lock", result.preserved_commitment_ids)

    def test_protected_day_inclusive_even_without_endpoint(self):
        lock = Commitment("cut", "s1", "harvest_or_cut_date", known("2031-05-20"))
        snapshot = replace(self.snapshot, input=replace(self.snapshot.input, commitments=(lock,)))
        plan = changed(self.plan, 0, crop_end_exclusive=unknown(), release_date=unknown())
        plan = changed(plan, 1, sowing_date=known(date(2031, 5, 20)))
        self.check(self.evaluate(plan, snapshot), "sowing_before_protected_cut")

    def test_deterministic_and_rule_order_independent(self):
        original = self.evaluate()
        self.assertEqual(original, self.evaluate())
        self.assertEqual(original, self.evaluate(kb=replace(self.kb, rules=tuple(reversed(self.kb.rules)))))

    def test_draft_rules_cannot_pass_or_reject(self):
        rules = tuple(replace(r, evidence_status="proposed") for r in self.kb.rules)
        result = self.evaluate(kb=replace(self.kb, rules=rules))
        self.assertEqual(result.status, "needs_review")
        self.assertFalse(any(c.outcome == "fail" for c in result.checks))

    def test_unknown_or_mismatched_applicability_no_coverage(self):
        for condition in (Condition("field.land", "old"), Condition("site_id", "other-site")):
            rules = tuple(replace(r, applicability=(condition,)) for r in self.kb.rules)
            result = self.evaluate(kb=replace(self.kb, rules=rules))
            self.assertEqual(result.status, "needs_review")
            self.assertFalse(any(c.outcome == "fail" for c in result.checks))

    def test_preference_is_not_hard_cutoff_or_eligibility_support(self):
        rules = tuple(replace(r, start=date(2031, 5, 1), end=date(2031, 5, 27),
                              effect="preference", required_for="explanation")
                      if r.rule_id == "s2-sowing" else r for r in self.kb.rules)
        result = self.evaluate(kb=replace(self.kb, rules=rules))
        self.assertEqual(result.status, "needs_review")
        self.check(result, "outside_preferred_sowing_window")

    def test_source_version_and_params_preserved(self):
        check = next(c for c in self.evaluate().checks if c.rule_id == "s2-sowing")
        self.assertEqual(check.rule_version, "synthetic-v1")
        self.assertEqual(check.explanation.source_refs, SYNTHETIC)
        self.assertEqual(check.explanation.params["sowing_date"], "2031-05-28")

    def test_numeric_field_requirement_units_and_method(self):
        rule = FactRule(rule_id="synthetic-ec", rule_version="test", profile_id="synthetic-profile-1",
                        topic="local_cultivar_field_fit", source_refs=SYNTHETIC,
                        evidence_status="verified", path="field.ec", expected=4.0,
                        operator="le", unit="dS/m", method="saturated-paste")
        kb = replace(self.kb, rules=self.kb.rules + (rule,))
        for method, expected in (("other", "needs_review"), ("saturated-paste", "rejected")):
            fact = replace(known(5.0, unit="dS/m"), method=method)
            snapshot = replace(self.snapshot, input=replace(self.snapshot.input,
                field_facts=self.snapshot.input.field_facts + (("ec", fact),)))
            self.assertEqual(self.evaluate(snapshot=snapshot, kb=kb).status, expected)

    def test_supported_rotation_only(self):
        rule = RotationRule(rule_id="synthetic-rotation", rule_version="test",
                            profile_id="synthetic-profile-2", topic="rotation",
                            source_refs=SYNTHETIC, evidence_status="verified",
                            allowed_predecessors=("synthetic-crop-4",))
        result = self.evaluate(kb=replace(self.kb, rules=self.kb.rules + (rule,)))
        self.assertEqual(result.status, "rejected")
        self.check(result, "rotation_restriction_conflict")

    def test_hard_quantity_requires_evidence_not_crop_presence(self):
        requirement = ProductionRequirement("feed", ("s1",), known(100, unit="kg"), hard=True)
        snapshot = replace(self.snapshot, input=replace(self.snapshot.input,
                                                       production_requirements=(requirement,)))
        result = self.evaluate(snapshot=snapshot)
        self.assertEqual(result.status, "needs_review")
        self.check(result, "production_requirement_unverified")

    def test_optional_demand_unknown_does_not_change_feasibility(self):
        rule = FactRule(rule_id="kc", rule_version="test", profile_id="synthetic-profile-1",
                        topic="demand", required_for="etc", effect="review",
                        path="field.kc", expected=1, source_refs=SYNTHETIC)
        self.assertEqual(self.evaluate(kb=replace(self.kb, rules=self.kb.rules + (rule,))).status, "feasible")

    def test_invalid_inputs_raise_separate_validation_error(self):
        cases = [self.plan[:3], list(self.plan),
                 changed(self.plan, 0, order=2),
                 changed(self.plan, 0, season_label="winter-2029"),
                 changed(self.plan, 0, sowing_date=known("2030-11-20")),
                 changed(self.plan, 0, crop_end_exclusive=known(date(2031, 5, 20))),
                 changed(self.plan, 0, release_date=known(date(2031, 5, 19))),
                 changed(self.plan, 0, preparation_days_after_release=known(-1, unit="day")),
                 changed(self.plan, 0, preparation_days_after_release=known(True, unit="day")),
                 changed(self.plan, 0, crop_id=known("incompatible")),
                 changed(self.plan, 0, release_date=replace(unknown(), unknown_reason=None))]
        for plan in cases:
            with self.subTest(plan=repr(plan)[:80]), self.assertRaises(InputValidationError) as ctx:
                self.evaluate(plan)
            self.assertTrue(ctx.exception.code)
            self.assertTrue(ctx.exception.field_paths)

    def test_release_mismatch_rejected_as_input(self):
        with self.assertRaises(InputValidationError):
            self.evaluate(kb=replace(self.kb, data_release="different"))

    def test_forecast_independence_structural_no_integration_claim(self):
        root = Path(constraints.__file__).parent
        allowed = {"__future__", "dataclasses", "datetime", "typing", "types", "math", "re"}
        for file in root.glob("*.py"):
            for node in ast.walk(ast.parse(file.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    self.assertTrue(all(n.name.split(".")[0] in allowed for n in node.names))
                if isinstance(node, ast.ImportFrom) and node.level == 0:
                    self.assertIn(node.module.split(".")[0], allowed)
        self.assertNotIn("forecast", ScenarioSnapshot.__dataclass_fields__)
        self.assertNotIn("forecast", KnowledgeBase.__dataclass_fields__)


class ReferenceRegression(unittest.TestCase):
    def test_required_reference_review_reasons_and_paths(self):
        plan, snapshot, kb = uh001()
        result = constraints.evaluate(plan, snapshot, kb)
        codes = {c.explanation.code for c in result.checks}
        self.assertTrue({"soil_suitability_unknown", "cultivar_availability_unknown",
                         "irrigation_availability_unknown", "crop_stages_unavailable",
                         "sorghum_local_eligibility_open", "forage_quantity_unknown"} <= codes)
        paths = {p for c in result.checks for p in c.missing_input_paths}
        self.assertIn("snapshot.input.field.drainage", paths)
        self.assertIn("snapshot.input.field.cultivar", paths)

    def test_current_rejected_protected_cut_unchanged(self):
        plan, snapshot, kb = uh001()
        before = repr((plan, snapshot, kb))
        result = constraints.evaluate(plan, snapshot, kb)
        self.assertEqual(result.status, "rejected")
        check = result.checks[0]
        self.assertEqual(check.explanation.code, "sowing_before_protected_cut")
        self.assertEqual(dict(check.explanation.params), {
            "season_id": "s2", "sowing_date": "2027-05-15", "protected_cut_date": "2027-05-20"})
        self.assertIn(REFERENCE[0], check.explanation.source_refs)
        self.assertIn("cut", result.preserved_commitment_ids)
        self.assertEqual(repr((plan, snapshot, kb)), before)
        self.assertEqual(plan[0].harvest_or_cut_date.value, date(2027, 5, 20))
        self.assertFalse(any(c.outcome == "fail" and c.season_ids in (("s2", "s3"), ("s3", "s4"))
                             for c in result.checks))

    def test_review_candidates_zero_feasible_repairs(self):
        plan, snapshot, kb = uh001()
        results = []
        for sow in (date(2027, 5, 28), date(2027, 6, 1)):
            candidate = changed(plan, 1, sowing_date=known(sow, refs=REFERENCE, illustrative=True),
                                harvest_or_cut_date=unknown("endpoint_mapping_missing"),
                                crop_end_exclusive=unknown("endpoint_mapping_missing"),
                                release_date=unknown("endpoint_mapping_missing"))
            result = constraints.evaluate(candidate, snapshot, kb)
            results.append(result)
            self.assertEqual(result.status, "needs_review")
            self.assertIn("cut", result.preserved_commitment_ids)
            self.assertTrue(any(c.outcome == "unknown" and c.season_ids == ("s2", "s3")
                                for c in result.checks))
        self.assertEqual(sum(r.status == "feasible" for r in results), 0)


if __name__ == "__main__":
    unittest.main()
