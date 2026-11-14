"""Unit tests for Uncle Hussein (UH-001) reference scenario comparison."""

import unittest

from backend.app.replay.uncle_hussein import (
    build_uh001_plans,
    compare_may28_vs_june1,
)


class TestUncleHusseinScenario(unittest.TestCase):
    def test_uh001_plan_structure_and_statuses(self):
        plans = build_uh001_plans()
        p0 = plans["P0"]
        r1 = plans["R1"]
        r2 = plans["R2"]

        # Exact expected statuses
        self.assertEqual(p0["planner_status"], "rejected")
        self.assertEqual(r1["planner_status"], "needs_review")
        self.assertEqual(r2["planner_status"], "needs_review")

        # P0 timing conflict: maize sowing (May 15) precedes berseem crop end (May 21)
        self.assertEqual(p0["seasons"][0]["crop_end_exclusive"], "2027-05-21")
        self.assertEqual(p0["seasons"][1]["sow_date"], "2027-05-15")

        # R1: May 28 (May 21 + 7 days preparation)
        self.assertEqual(r1["seasons"][1]["sow_date"], "2027-05-28")

        # R2: June 1 (farmer-permitted exploration)
        self.assertEqual(r2["seasons"][1]["sow_date"], "2027-06-01")

        # Protected commitments must be identical across all plans
        for plan in (p0, r1, r2):
            self.assertEqual(plan["commitments"][0]["date"], "2027-05-20")
            self.assertEqual(plan["commitments"][0]["id"], "cut")
            self.assertEqual(len(plan["seasons"]), 4)

    def test_may28_vs_june1_historical_replay(self):
        result = compare_may28_vs_june1(anchor_years=[2015, 2016, 2020])

        # Verdicts
        verdict = result["agricultural_verdict"]
        self.assertEqual(verdict["UH001_P0_BASELINE"], "rejected")
        self.assertEqual(verdict["UH001_R1_MAY28"], "needs_review")
        self.assertEqual(verdict["UH001_R2_JUN01"], "needs_review")
        self.assertEqual(verdict["validated_feasible_count"], 0)

        # R1 vs R2 comparison
        r1_r2 = result["comparison_r1_r2"]
        self.assertEqual(r1_r2["status"], "complete")
        self.assertEqual(r1_r2["eligible_anchors"], [2015, 2016, 2020])

        # Tradeoff summary
        s2_summary = result["season_2_maize_tradeoff_summary"]
        self.assertEqual(s2_summary["r1_sowing"], "2027-05-28")
        self.assertEqual(s2_summary["r2_sowing"], "2027-06-01")
        self.assertEqual(s2_summary["sowing_offset_days"], 4)
        self.assertEqual(s2_summary["eligible_years_count"], 3)
        self.assertEqual(len(s2_summary["paired_blocks"]), 3)

        # All paired difference blocks must report ET0 and Tmax differences
        for block_diff in s2_summary["paired_blocks"]:
            self.assertIn("et0_total_diff_mm", block_diff)
            self.assertIn("mean_et0_diff_mm_day", block_diff)
            self.assertIn("tmax_mean_diff_c", block_diff)
            self.assertIn("hot_days_diff", block_diff)

        # P0 baseline in comparison_all is blocked due to the overlap
        comp_all = result["comparison_all"]
        self.assertEqual(comp_all["status"], "blocked_policy")
        self.assertIn("overlapping_or_unordered_windows", [b["reason"] for b in comp_all["blockers"]])

        # Scientific guardrails
        guardrails = result["scientific_guardrails"]
        self.assertTrue(guardrails["et0_is_not_irrigation"])
        self.assertEqual(guardrails["etc_status"], "unavailable")
        self.assertFalse(guardrails["planner_feasibility_modified"])


if __name__ == "__main__":
    unittest.main()
