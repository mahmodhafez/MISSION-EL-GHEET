"""UH-001 climate demonstration: real NASA data, real Promise Test statuses, no invented dates."""

import json
import unittest

from backend.app.replay.cli import uh001_planner_statuses
from backend.app.replay.service import get_climate_store, run_uncle_hussein_comparison
from backend.app.replay.uncle_hussein import UH001


class TestUncleHusseinScenario(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.statuses = uh001_planner_statuses()
        cls.result = run_uncle_hussein_comparison(planner_statuses=cls.statuses)

    def test_promise_test_statuses_come_from_the_real_planner(self):
        self.assertIsNotNone(self.statuses, "planner fixture packages/meg-core/tools/fixtures/uh001.json missing")
        self.assertEqual(self.statuses["2027-05-15"], "rejected")
        self.assertEqual(self.statuses["2027-05-28"], "needs_review")
        self.assertEqual(self.statuses["2027-06-01"], "needs_review")
        self.assertNotIn("feasible", self.statuses.values())

    def test_climate_echoes_statuses_and_never_changes_them(self):
        r = self.result
        self.assertEqual([(w["sow_date"], w["planner_status"]) for w in r["windows"]],
                         [("2027-05-28", "needs_review"), ("2027-06-01", "needs_review")])
        self.assertEqual(r["scenario"]["original_plan_status"], "rejected")
        self.assertFalse(r["feasibility"]["climate_changes_planner_status"])
        self.assertEqual(r["scenario"]["protected_commitment"]["date"], "2027-05-20")

    def test_no_crop_end_or_harvest_date_is_invented(self):
        text = json.dumps(self.result)
        for key in ("crop_end_exclusive", "harvest", "release_date"):
            self.assertNotIn(f'"{key}"', text)
        self.assertEqual(self.result["window_days"], 14)
        self.assertIn("not a full crop-season analysis", self.result["label"]["en"])
        self.assertEqual(UH001["investigated_sow_dates"], ["2027-05-28", "2027-06-01"])

    def test_real_nasa_coverage_and_paired_years(self):
        a = self.result["layer_a_historical"]
        self.assertEqual(self.result["status"], "complete")
        self.assertEqual(a["years_used"], list(range(2001, 2026)))
        for wid in ("W1", "W2"):
            rows = a["windows"][wid]["per_year"]
            self.assertEqual([r["year"] for r in rows], a["years_used"])
            self.assertTrue(all(r["days"] == 14 and r["snapshots"] == ["historical"] for r in rows))
        self.assertEqual(a["paired_differences"]["W2"]["tmax_mean_c"]["n"], 25)

    def test_unsupplied_statuses_are_reported_not_guessed(self):
        r = run_uncle_hussein_comparison(planner_statuses=None, years=[2015, 2016])
        self.assertEqual({w["planner_status"] for w in r["windows"]}, {"not_supplied"})
        self.assertEqual(r["scenario"]["statuses_source"], "not_supplied")

    def test_store_is_cached(self):
        self.assertIs(get_climate_store(), get_climate_store())


if __name__ == "__main__":
    unittest.main()
