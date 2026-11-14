"""Unit tests for Historical Season Replay."""

import copy
import unittest
from datetime import date
from pathlib import Path

from backend.app.replay.dataset import (
    ClimateDataError,
    ClimateInputError,
    ClimateStore,
    resolve_data_directory,
)
from backend.app.replay.replay import HistoricalSeasonReplay


class TestHistoricalSeasonReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = resolve_data_directory()
        cls.store = ClimateStore(cls.data_dir)
        cls.engine = HistoricalSeasonReplay(cls.store)

        # Baseline plan for tests
        cls.plan_a = {
            "plan_id": "plan_alpha",
            "plan_version": "1",
            "field_id": "test_field_01",
            "planner_status": "needs_review",
            "mapping_policy": "explicit_calendar_windows_v1",
            "commitments": [
                {
                    "id": "c1",
                    "description": "Protected forage cut",
                    "date": "2027-05-20",
                }
            ],
            "seasons": [
                {
                    "season_id": "s1",
                    "crop_id": "berseem",
                    "purpose": "forage",
                    "sow_date": "2026-11-01",
                    "crop_end_exclusive": "2027-05-21",
                },
                {
                    "season_id": "s2",
                    "crop_id": "grain_maize",
                    "purpose": "grain",
                    "sow_date": "2027-06-01",
                    "crop_end_exclusive": "2027-09-21",
                },
            ],
        }

        # Candidate plan with later sowing date
        cls.plan_b = copy.deepcopy(cls.plan_a)
        cls.plan_b["plan_id"] = "plan_beta"
        cls.plan_b["seasons"][1]["sow_date"] = "2027-06-08"
        cls.plan_b["seasons"][1]["crop_end_exclusive"] = "2027-09-28"

    def test_single_plan_replay_complete(self):
        res = self.engine.replay_single_plan(
            self.plan_a,
            anchor_years=[2015, 2016],
            template_anchor_year=2026,
        )
        self.assertEqual(res["status"], "complete")
        self.assertEqual(res["eligible_anchors"], [2015, 2016])
        self.assertEqual(len(res["blocks"]), 2)

        block_0 = res["blocks"][0]
        self.assertEqual(block_0["anchor"], 2015)
        plan_profile = block_0["plans"][0]
        self.assertEqual(plan_profile["plan_id"], "plan_alpha")
        self.assertEqual(len(plan_profile["seasons"]), 2)

        # Metrics must exist and be non-negative
        s1 = plan_profile["seasons"][0]
        self.assertGreater(s1["metrics"]["days"], 0)
        self.assertGreater(s1["metrics"]["et0_total_mm"], 0.0)
        self.assertGreater(s1["metrics"]["mean_et0_mm_day"], 0.0)

        # Scientific guardrails: ETc is unavailable
        self.assertIsNone(s1["etc_metrics"])
        self.assertEqual(s1["etc_status"], "unavailable")

    def test_paired_comparison_and_differences(self):
        res = self.engine.compare_plans(
            [self.plan_a, self.plan_b],
            anchor_years=[2015, 2016],
            template_anchor_year=2026,
        )
        self.assertEqual(res["status"], "complete")
        self.assertEqual(res["baseline_id"], "plan_alpha")

        for block in res["blocks"]:
            diff = block["differences_from_baseline"]["plan_beta"]
            plan_0 = block["plans"][0]
            plan_1 = block["plans"][1]
            # Days difference
            expected_days_diff = plan_1["in_crop"]["days"] - plan_0["in_crop"]["days"]
            self.assertEqual(diff["days"], expected_days_diff)
            # ET0 total difference
            expected_et0_diff = plan_1["in_crop"]["et0_total_mm"] - plan_0["in_crop"]["et0_total_mm"]
            self.assertAlmostEqual(diff["et0_total_mm"], expected_et0_diff, places=6)

        # Paired variability
        paired_var = res["paired_difference_variability"]["plan_beta"]
        self.assertIn("et0_total_mm", paired_var)
        self.assertEqual(paired_var["et0_total_mm"]["count"], 2)

    def test_partial_and_unavailable_status(self):
        # 2024 is incomplete because template plan spans 2026-2027 (so anchor 2024 needs 2025 data,
        # which is present, but anchor 2025 needs 2026 Dec 31 which is incomplete).
        res_partial = self.engine.compare_plans(
            [self.plan_a, self.plan_b],
            anchor_years=[2015, 2025],
            template_anchor_year=2026,
        )
        self.assertEqual(res_partial["status"], "partial")
        self.assertEqual(res_partial["eligible_anchors"], [2015])
        self.assertEqual(res_partial["exclusions"][0]["anchor"], 2025)
        self.assertEqual(res_partial["exclusions"][0]["reason"], "incomplete_continuous_block")

        # Entirely unavailable when no anchors are eligible
        res_unavail = self.engine.compare_plans(
            [self.plan_a, self.plan_b],
            anchor_years=[2025],
            template_anchor_year=2026,
        )
        self.assertEqual(res_unavail["status"], "unavailable")
        self.assertEqual(res_unavail["eligible_anchors"], [])

    def test_leap_day_handling(self):
        # Test a plan with Feb 29 endpoint
        leap_plan = copy.deepcopy(self.plan_a)
        leap_plan["seasons"] = [
            {
                "season_id": "s_leap",
                "crop_id": "test_crop",
                "purpose": "demo",
                "sow_date": "2024-02-28",
                "crop_end_exclusive": "2024-03-02",
            }
        ]
        # In non-leap year 2019, 2024-02-28 maps to 2019-02-28.
        # But if sow_date is 2024-02-29, 2019 cannot represent Feb 29.
        leap_explicit = copy.deepcopy(leap_plan)
        leap_explicit["seasons"][0]["sow_date"] = "2024-02-29"

        res = self.engine.compare_plans(
            [leap_explicit],
            anchor_years=[2019, 2020],
            template_anchor_year=2024,
        )
        self.assertEqual(res["eligible_anchors"], [2020])
        self.assertEqual(res["exclusions"][0]["anchor"], 2019)
        self.assertEqual(res["exclusions"][0]["reason"], "unrepresentable_explicit_date")

    def test_scientific_guardrails_non_negotiable(self):
        res = self.engine.replay_single_plan(
            self.plan_a,
            anchor_years=[2015],
            template_anchor_year=2026,
        )
        # 1. mapped_feasibility is strictly "not_evaluated"
        self.assertEqual(res["mapped_feasibility"], "not_evaluated")

        # 2. planner_status is preserved unchanged
        self.assertEqual(res["blocks"][0]["plans"][0]["planner_status"], "needs_review")

        # 3. Guardrails dict is explicitly populated
        guardrails = res["scientific_guardrails"]
        self.assertIn("FAO-56", guardrails["et0_note"])
        self.assertEqual(guardrails["etc_status"], "unavailable")

    def test_blocked_policy_on_overlapping_windows(self):
        overlapping = copy.deepcopy(self.plan_a)
        overlapping["plan_id"] = "plan_overlapping"
        # Second season starts before first season ends
        overlapping["seasons"][1]["sow_date"] = "2027-05-10"

        res = self.engine.compare_plans(
            [self.plan_a, overlapping],
            anchor_years=[2015],
            template_anchor_year=2026,
        )
        self.assertEqual(res["status"], "blocked_policy")
        self.assertIn(
            "overlapping_or_unordered_windows",
            [b["reason"] for b in res["blockers"]],
        )

    def test_blocked_policy_on_different_commitments(self):
        diff_commitments = copy.deepcopy(self.plan_b)
        diff_commitments["commitments"][0]["date"] = "2027-05-25"

        res = self.engine.compare_plans(
            [self.plan_a, diff_commitments],
            anchor_years=[2015],
            template_anchor_year=2026,
        )
        self.assertEqual(res["status"], "blocked_policy")
        self.assertIn(
            "different_protected_commitments",
            [b["reason"] for b in res["blockers"]],
        )

    def test_input_validation_errors(self):
        # Invalid site
        with self.assertRaises(ClimateInputError):
            ClimateStore(site_id="other_site")

        # Duplicate anchor years
        with self.assertRaises(ClimateInputError):
            self.engine.replay_single_plan(
                self.plan_a,
                anchor_years=[2015, 2015],
                template_anchor_year=2026,
            )

        # Invalid date format
        with self.assertRaises(ClimateInputError):
            self.store.get_daily_weather("20200101", "2020-01-02")


if __name__ == "__main__":
    unittest.main()
