"""Integration gates on the packaged reviewed release sakha-agricultural-review-2026-11-14.1.

Signed/enforceable rules below are SYNTHETIC stand-ins; the delivered release has none.
"""

from dataclasses import replace
from datetime import date
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from planner_cli import load  # noqa: E402
from agricultural_kb import KBError  # noqa: E402
from meg_core.agricultural_release import bind_profiles, catalogue_view, load_reviewed_release  # noqa: E402
from meg_core.planner import constraints  # noqa: E402
from meg_core.planner.crop_catalogue import build_planner_kb  # noqa: E402
from meg_core.planner.scope import prepare_scope  # noqa: E402
from meg_core.planner.service import plan  # noqa: E402
from meg_core.planner._types import ExplorationChoice, ScopeRequest, SearchPolicy  # noqa: E402
from meg_core.planner._validation import InputValidationError  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[1] / "tools" / "fixtures" / "uh001.json"
RESEARCH_ONLY = {"watermelon", "strawberry", "cantaloupe", "harankash"}


def signed(rule_id, crop, start, end):
    """SYNTHETIC: a sowing window as Refaat's get_enforceable_rules() would return it after sign-off."""
    return {"rule_id": rule_id, "crop_ids": [crop], "rule_type": "sowing_window", "source_ids": ["SYNTHETIC-ONLY"],
            "conditions": {}, "enforceability": {"enforceable": True, "blockers": []},
            "enforcement": {"status": "ENABLED", "constraint": {"kind": "calendar_window", "field": "sowing_date",
                                                                  "start_month_day": start, "end_month_day": end}}}


class ReleaseIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release = load_reviewed_release()
        _, cls.snapshot, _, cls.choices, _, cls.policy, _ = load(FIXTURE)
        cls.labels = tuple(s.season_label for s in cls.snapshot.input.seasons)
        cls.built = cls.release.for_planner(site_id="sakha", season_labels=cls.labels)

    def uh001(self, kb=None):
        kb = kb or self.built.kb
        seasons = bind_profiles(self.snapshot.input.seasons, kb)
        return replace(self.snapshot, data_release=self.release.version,
                       input=replace(self.snapshot.input, seasons=seasons))

    # --- catalogue visibility vs exploration vs enforcement vs feasibility
    def test_catalogue_view_separates_the_four_concepts(self):
        view = {c["crop_id"]: c for c in catalogue_view(self.release, self.built)}
        self.assertEqual(len(view), 12)
        self.assertEqual({k for k, c in view.items() if c["research_only"]}, RESEARCH_ONLY)
        for crop in RESEARCH_ONLY:
            self.assertEqual((view[crop]["planner_profiles"], view[crop]["offerable_purposes"]), ([], []))
        self.assertEqual(view["berseem"]["offerable_purposes"], ["forage"])  # via the proposal only
        self.assertEqual(view["wheat"]["offerable_purposes"], ["grain"])
        self.assertTrue(all(c["approval"] == "pending" and not c["feasibility_eligible"] and not c["enforced_profiles"]
                            for c in view.values()))
        self.assertIn("wheat-sowing-window", view["wheat"]["conflicts"])
        self.assertIn("berseem-production-purpose", view["berseem"]["conflicts"])
        self.assertEqual(view["wheat"]["kb_rules"], 9)

    # --- negative gates
    def test_pending_rules_never_enforced(self):
        self.assertEqual(self.release.agricultural.get_enforceable_rules(locality="sakha"), [])
        self.assertEqual(self.built.kb.rules, ())

    def test_conflicted_wheat_and_berseem_rules_stay_held_even_if_signed(self):
        built = build_planner_kb(self.release.catalogue, refaat_crops=self.release.agricultural.get_crops(),
                                 enforceable_rules=[signed("C01", "wheat", "11-10", "11-30"),
                                                    signed("C07", "berseem", "10-01", "10-20"),
                                                    signed("C14", "grain_maize", "05-01", "05-31")],
                                 kb_version=self.release.version, data_release=self.release.version,
                                 site_id="sakha", season_labels=self.labels)
        held = {u.rule_id for u in built.unmapped if u.reason == "unresolved_evidence_conflict"}
        self.assertEqual(held, {"C01", "C07"})
        self.assertTrue(any(r.rule_id.startswith("C14:") for r in built.kb.rules))  # gate is specific

    def test_forage_and_seed_are_not_interchangeable(self):
        seasons = self.snapshot.input.seasons
        self.assertEqual(bind_profiles(seasons, self.built.kb)[0].profile_id.value, "berseem-forage-proposed")
        seed = (replace(seasons[0], purpose=replace(seasons[0].purpose, value="seed")),) + seasons[1:]
        with self.assertRaises(InputValidationError):
            bind_profiles(seed, self.built.kb)

    def test_outside_release_scope_refused(self):
        with self.assertRaises(KBError):
            self.release.for_planner(site_id="nubaria", season_labels=self.labels)

    def test_wrong_season_year_never_applies_a_rule(self):
        built = build_planner_kb(self.release.catalogue, refaat_crops=self.release.agricultural.get_crops(),
                                 enforceable_rules=[signed("C14", "grain_maize", "05-01", "05-31")],
                                 kb_version=self.release.version, data_release=self.release.version,
                                 site_id="sakha", season_labels=("summer-2031",))
        snap = self.uh001(built.kb)
        checks = [c for c in constraints.evaluate(snap.input.seasons, snap, built.kb).checks if c.rule_id.startswith("C14:")]
        self.assertEqual({c.outcome for c in checks}, {"not_applicable"})

    def test_research_only_and_wrong_purpose_attempts_are_blocked(self):
        draft = replace(self.uh001(), input=replace(self.uh001().input, journey="explore"))
        preview = prepare_scope(ScopeRequest(snapshot=draft, choices=(
            ExplorationChoice("fruit", "s4", "crop_id", ("watermelon",)),
            ExplorationChoice("rice-in-forage", "s1", "crop_id", ("rice",)))), self.built.kb)
        self.assertIn("catalogue_value_unavailable", {i.code for i in preview.issues})
        self.assertNotIn("watermelon", preview.available_crop_ids)
        bound = replace(draft, input=replace(draft.input, exploration=preview.choices, pending_scope_issues=preview.issues,
                                             scope_hash=preview.scope_hash, exploration_confirmed=True))
        result = plan(bound, self.built.kb, SearchPolicy())
        self.assertEqual(result.feasible_alternatives, ())
        self.assertIn("rice-in-forage", result.search.uninstantiated_choice_ids)  # grain rice cannot bind a forage slot

    # --- acceptance: UH-001 through the real loader, generator and service
    def test_uh001_reviewed_release(self):
        snap = self.uh001()
        current = constraints.evaluate(snap.input.seasons, snap, self.built.kb)
        self.assertEqual(current.status, "rejected")
        self.assertEqual(current.checks[0].explanation.code, "sowing_before_protected_cut")
        draft = replace(snap, input=replace(snap.input, journey="explore"))
        preview = prepare_scope(ScopeRequest(snapshot=draft, choices=self.choices), self.built.kb)
        bound = replace(draft, input=replace(draft.input, exploration=preview.choices, pending_scope_issues=preview.issues,
                                             scope_hash=preview.scope_hash, exploration_confirmed=True))
        result = plan(bound, self.built.kb, self.policy)
        self.assertEqual(result.feasible_alternatives, ())
        self.assertEqual({c.plan[1].sowing_date.value: c.evaluation.status for c in result.review_investigations},
                         {date(2027, 5, 28): "needs_review", date(2027, 6, 1): "needs_review"})
        for c in result.review_investigations:
            self.assertEqual(c.plan[0].harvest_or_cut_date.value, date(2027, 5, 20))  # protected cut unchanged
            self.assertIsNone(c.plan[1].release_date.value)  # missing field release stays unknown
            self.assertIsNone(c.plan[1].harvest_or_cut_date.value)


if __name__ == "__main__":
    unittest.main()
