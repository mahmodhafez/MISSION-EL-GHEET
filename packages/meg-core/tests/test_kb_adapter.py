"""Refaat KB -> planner adapter. Signed/enforceable rules below are SYNTHETIC test data only.

Set MEG_AGRI_KB to Refaat's knowledge_base/agricultural_kb.json to also run the real-release checks.
"""

from dataclasses import replace
from datetime import date
import json
import os
from pathlib import Path
import unittest

from test_constraints import synthetic, uh001
from meg_core.planner import constraints
from meg_core.planner.kb_adapter import adapt
from meg_core.planner._types import FactRule, SowingWindowRule
from meg_core.planner._validation import InputValidationError

LABELS = ("winter-2030", "summer-2031", "winter-2031", "summer-2032")
CROPS = [{"crop_id": f"synthetic-crop-{i}", "purpose": "grain"} for i in range(1, 5)]


def signed(rule_id, crop, constraint, *, rule_type="sowing_window", conditions=None, enforceable=True):
    """SYNTHETIC stand-in for one rule returned by Refaat's get_enforceable_rules()."""
    return {"rule_id": rule_id, "crop_ids": [crop], "rule_type": rule_type, "source_ids": ["SYNTHETIC-ONLY"],
            "conditions": conditions or {}, "enforcement": {"status": "ENABLED", "constraint": constraint},
            "enforceability": {"enforceable": enforceable, "blockers": []}}


def run(rules, crops=CROPS, labels=LABELS):
    return adapt(crops=crops, enforceable_rules=rules, kb_version="synthetic-kb", data_release="synthetic-only-v1",
                 site_id="synthetic-site", season_labels=labels)


def crop_ids_as_profiles(plan):
    return tuple(replace(s, profile_id=replace(s.profile_id, value=s.crop_id.value)) for s in plan)


class AdapterMapping(unittest.TestCase):
    def test_winter_window_crosses_into_next_year(self):
        window = {"kind": "calendar_window", "field": "sowing_date", "start_month_day": "11-15", "end_month_day": "01-10"}
        out = run([signed("S1", "synthetic-crop-1", window)], labels=("winter-2030",))
        (rule,) = out.kb.rules
        self.assertIsInstance(rule, SowingWindowRule)
        self.assertEqual((rule.start, rule.end), (date(2030, 11, 15), date(2031, 1, 10)))
        self.assertEqual(rule.effect, "hard")
        self.assertIn(("season_label", "winter-2030"), [(c.path, c.expected) for c in rule.applicability])

    def test_ambiguous_dates_are_reported_not_guessed(self):
        cross = {"kind": "calendar_window", "field": "sowing_date", "start_month_day": "11-15", "end_month_day": "01-10"}
        leap = {"kind": "calendar_window", "field": "sowing_date", "start_month_day": "02-01", "end_month_day": "02-29"}
        out = run([signed("X", "synthetic-crop-2", cross), signed("L", "synthetic-crop-1", leap)],
                  labels=("summer-2031", "winter-2030"))
        reasons = {(u.rule_id, u.reason) for u in out.unmapped}
        self.assertIn(("X:synthetic-crop-2:summer-2031", "window_crosses_slot_year"), reasons)
        self.assertIn(("L:synthetic-crop-1:winter-2030", "leap_day_unresolved"), reasons)  # Feb 2031 has no 29th

    def test_only_enforceable_mappable_rules_become_planner_rules(self):
        window = {"kind": "calendar_window", "field": "sowing_date", "start_month_day": "05-01", "end_month_day": "05-31"}
        rules = [signed("P", "synthetic-crop-2", window, enforceable=False),
                 signed("T", "synthetic-crop-2", window, rule_type="duration"),
                 signed("C", "synthetic-crop-2", window, conditions={"soil": ["clay", "loam"]}),
                 signed("U", "synthetic-crop-2", {"kind": "category_set", "field": "drainage", "allowed": ["a", "b"]}),
                 signed("Z", "absent-crop", window)]
        out = run(rules)
        self.assertEqual(out.kb.rules, ())
        self.assertEqual({u.reason for u in out.unmapped}, {"not_enforceable", "topic_mapping_required",
                                                            "multi_value_condition", "unsupported_constraint", "unknown_crop"})

    def test_numeric_and_single_category_constraints(self):
        numeric = {"kind": "numeric_range", "field": "ece", "lower": 0, "upper": 4.0, "units": "dS/m"}
        category = {"kind": "category_set", "field": "irrigation", "allowed": ["available"]}
        out = run([signed("N", "synthetic-crop-1", numeric), signed("K", "synthetic-crop-1", category)],
                  labels=("winter-2030",))
        facts = {(r.path, r.operator, r.expected, r.unit) for r in out.kb.rules if isinstance(r, FactRule)}
        self.assertEqual(facts, {("field.ece", "ge", 0, "dS/m"), ("field.ece", "le", 4.0, "dS/m"),
                                 ("field.irrigation", "eq", "available", None)})

    def test_malformed_loader_output_is_structural(self):
        for kwargs in ({"crops": "x"}, {"crops": [{"crop_id": ""}]}, {"enforceable_rules": [{"rule_id": 3}]},
                       {"season_labels": ("autumn-2030",)}):
            with self.subTest(kwargs=kwargs), self.assertRaises(InputValidationError):
                args = dict(crops=CROPS, enforceable_rules=[], kb_version="v", data_release="r",
                            site_id="s", season_labels=LABELS)
                args.update(kwargs)
                adapt(**args)


class AdapterWithPromiseTest(unittest.TestCase):
    def test_signed_window_drives_real_evaluator(self):
        plan, snapshot, _ = synthetic()
        plan = crop_ids_as_profiles(plan)
        sow = plan[1].sowing_date.value
        inside = {"kind": "calendar_window", "field": "sowing_date",
                  "start_month_day": f"{sow.month:02d}-{sow.day:02d}", "end_month_day": f"{sow.month:02d}-{sow.day:02d}"}
        outside = dict(inside, start_month_day="04-01", end_month_day="04-02")
        snap = replace(snapshot, input=replace(snapshot.input, seasons=plan))
        for window, expected in ((inside, "pass"), (outside, "fail")):
            with self.subTest(expected=expected):
                kb = run([signed("W", "synthetic-crop-2", window)]).kb
                result = constraints.evaluate(plan, snap, kb)
                own = f"W:synthetic-crop-2:{plan[1].season_label}"
                self.assertEqual({c.outcome for c in result.checks if c.rule_id == own}, {expected})
                # One rule per season label: the other labels' copies never apply to season 2.
                self.assertEqual({c.outcome for c in result.checks if c.rule_id.startswith("W:") and c.rule_id != own},
                                 {"not_applicable"})
                self.assertNotEqual(result.status, "feasible")  # other mandatory topics stay uncovered

    def test_no_enforceable_rules_never_feasible(self):
        plan, snapshot, _ = synthetic()
        plan = crop_ids_as_profiles(plan)
        snap = replace(snapshot, input=replace(snapshot.input, seasons=plan))
        out = run([])
        self.assertEqual(constraints.evaluate(plan, snap, out.kb).status, "needs_review")


@unittest.skipUnless(os.environ.get("MEG_AGRI_KB"), "set MEG_AGRI_KB to Refaat's agricultural_kb.json")
class RealRefaatRelease(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(Path(os.environ["MEG_AGRI_KB"]).read_text(encoding="utf-8"))

    def test_delivered_release_yields_profiles_and_no_rules(self):
        self.assertEqual(self.doc["schema_version"], "agricultural-kb/1")
        pending = [r for r in self.doc["rules"] if r["approval"]["status"] != "APPROVED"]
        self.assertEqual(len(pending), len(self.doc["rules"]))  # delivered release: nothing signed
        out = adapt(crops=self.doc["crops"], enforceable_rules=[], kb_version=self.doc["kb_version"],
                    data_release=self.doc["kb_version"], site_id="sakha", season_labels=LABELS)
        self.assertEqual(sorted(p.crop_id for p in out.kb.profiles),
                         ["berseem", "grain_maize", "grain_sorghum", "wheat"])
        self.assertEqual(out.kb.rules, ())

    def test_uh001_still_rejected_with_refaat_profiles(self):
        plan, snapshot, _ = uh001()
        purposes = {c["crop_id"]: c["purpose"] for c in self.doc["crops"]}
        plan = tuple(replace(s, profile_id=replace(s.profile_id, value=s.crop_id.value),
                             purpose=replace(s.purpose, value=purposes[s.crop_id.value])) for s in plan)
        snap = replace(snapshot, data_release=self.doc["kb_version"], input=replace(snapshot.input, seasons=plan))
        kb = adapt(crops=self.doc["crops"], enforceable_rules=[], kb_version=self.doc["kb_version"],
                   data_release=self.doc["kb_version"], site_id="sakha",
                   season_labels=tuple(s.season_label for s in plan)).kb
        result = constraints.evaluate(plan, snap, kb)
        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.checks[0].explanation.code, "sowing_before_protected_cut")


if __name__ == "__main__":
    unittest.main()
