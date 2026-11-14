"""Unit tests for Climate Evidence Card generation."""

import unittest

from backend.app.replay.evidence_card import build_climate_evidence_card
from backend.app.replay.service import create_evidence_card, evaluate_season_replay


class TestClimateEvidenceCard(unittest.TestCase):
    def test_evidence_card_schema_and_decision_states(self):
        # 1. Rejected plan -> decision_state must be "review_draft"
        card_rejected = build_climate_evidence_card(
            scenario_id="UH-001",
            scenario_revision=1,
            plan_id="UH001_P0",
            plan_version=1,
            planning_result_id="pr-01",
            plan_status="rejected",
        )
        self.assertEqual(card_rejected["decision_state"], "review_draft")
        self.assertEqual(card_rejected["plan_status"], "rejected")
        self.assertEqual(card_rejected["currency"], "current")
        self.assertEqual(card_rejected["input_ref"]["scenario_id"], "UH-001")
        self.assertEqual(card_rejected["input_ref"]["plan_ref"]["plan_id"], "UH001_P0")

        # 2. Needs_review plan -> decision_state must be "review_draft"
        card_review = build_climate_evidence_card(
            scenario_id="UH-001",
            scenario_revision=1,
            plan_id="UH001_R1",
            plan_version=1,
            planning_result_id="pr-02",
            plan_status="needs_review",
        )
        self.assertEqual(card_review["decision_state"], "review_draft")

        # 3. Feasible plan -> decision_state must be "unapproved"
        card_feasible = build_climate_evidence_card(
            scenario_id="UH-001",
            scenario_revision=1,
            plan_id="UH001_FEASIBLE",
            plan_version=1,
            planning_result_id="pr-03",
            plan_status="feasible",
        )
        self.assertEqual(card_feasible["decision_state"], "unapproved")

        # 4. Invalid status raises ValueError
        with self.assertRaises(ValueError):
            build_climate_evidence_card(
                scenario_id="UH-001",
                scenario_revision=1,
                plan_id="UH001_INVALID",
                plan_version=1,
                planning_result_id="pr-04",
                plan_status="invalid_status",
            )

    def test_evidence_card_with_replay_summary(self):
        # TEST-ONLY plan with explicit caller-supplied windows (not agronomy, not UH-001 data).
        r1 = {
            "plan_id": "TEST_PLAN", "plan_version": "1", "field_id": "test_field",
            "planner_status": "needs_review", "mapping_policy": "explicit_calendar_windows_v1", "commitments": [],
            "seasons": [{"season_id": "s1", "crop_id": "test_crop", "purpose": "grain",
                         "sow_date": "2026-06-01", "crop_end_exclusive": "2026-09-01"}],
        }

        replay_res = evaluate_season_replay(
            plans=[r1],
            anchor_years=[2015, 2016, 2020],
            template_anchor_year=2026,
        )

        card = create_evidence_card(
            scenario_id="UH-001",
            scenario_revision=1,
            plan_id=r1["plan_id"],
            plan_version=int(r1["plan_version"]),
            planning_result_id="pr-uh001-r1",
            plan_status=r1["planner_status"],
            replay_result=replay_res,
        )
        # No scenario-specific content is invented when the caller supplies none.
        self.assertEqual(card["preserved_commitment_ids"], [])
        self.assertEqual(card["assumptions"], [])
        self.assertEqual(card["outstanding_checks"], [])

        self.assertIsNotNone(card["replay_id"])
        self.assertEqual(card["climate_evidence"]["eligible_blocks_count"], 3)
        self.assertEqual(card["climate_evidence"]["status"], "complete")
        self.assertIn("et0_total_median_mm", card["climate_evidence"])
        self.assertIn("hot_days_median", card["climate_evidence"])

        # Takeaway parameters
        params = card["takeaway"]["parameters"]
        self.assertEqual(params["historical_blocks_evaluated"], 3)
        self.assertIn("et0_total_median_mm", params)
        self.assertEqual(params["et0_unit"], "mm")

        # Guardrails
        guardrails = card["scientific_guardrails"]
        self.assertTrue(guardrails["et0_is_reference_demand_only"])
        self.assertEqual(guardrails["etc_status"], "unavailable")
        self.assertFalse(guardrails["crop_stress_thresholds_invented"])
        self.assertFalse(guardrails["feasibility_modified_by_climate"])


if __name__ == "__main__":
    unittest.main()
