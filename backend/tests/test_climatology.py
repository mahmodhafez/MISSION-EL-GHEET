"""Unit tests for Refaat's seasonal climatology baseline."""

import unittest
from datetime import date
from pathlib import Path

from backend.app.replay.climatology import (
    DESCRIPTIVE_METHOD,
    RESEARCH_METHOD,
    SeasonalClimatology,
    calendar_window,
    iso_date,
    linear_quantile,
    phase,
)
from backend.app.replay.dataset import ClimateStore, resolve_data_directory


class TestClimatology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = resolve_data_directory()
        cls.store = ClimateStore(cls.data_dir)

    def test_iso_date_and_phase(self):
        d1 = iso_date("2024-02-29")
        self.assertEqual(d1, date(2024, 2, 29))
        self.assertEqual(phase(d1), 59)

        d2 = iso_date("2024-03-01")
        self.assertEqual(phase(d2), 60)

        # In non-leap year, March 1 is still phase 60
        d3 = iso_date("2023-03-01")
        self.assertEqual(phase(d3), 60)

        with self.assertRaises(ValueError):
            iso_date("invalid-date")
        with self.assertRaises(ValueError):
            iso_date(12345)

    def test_calendar_window(self):
        window = calendar_window("2024-01-01")
        self.assertEqual(len(window), 31)
        # Jan 1 is phase 0, so window wraps around 366
        self.assertIn(0, window)
        self.assertIn(15, window)
        self.assertIn(351, window)

    def test_linear_quantile(self):
        vals = [10.0, 20.0, 30.0, 40.0, 50.0]
        self.assertAlmostEqual(linear_quantile(vals, 0.0), 10.0)
        self.assertAlmostEqual(linear_quantile(vals, 0.5), 30.0)
        self.assertAlmostEqual(linear_quantile(vals, 1.0), 50.0)
        self.assertAlmostEqual(linear_quantile(vals, 0.25), 20.0)

        with self.assertRaises(ValueError):
            linear_quantile([], 0.5)
        with self.assertRaises(ValueError):
            linear_quantile(vals, -0.1)
        with self.assertRaises(ValueError):
            linear_quantile(vals, 1.1)

    def test_climatology_historical_2001_2025(self):
        res = self.store.get_climatology("2027-05-28", reference="historical_2001_2025")
        self.assertEqual(res["status"], "complete")
        self.assertEqual(res["reference_id"], "historical_2001_2025")
        q = res["quantiles"]
        self.assertEqual(q["target_date"], "2027-05-28")
        self.assertEqual(q["reference_start"], "2001-01-01")
        self.assertEqual(q["reference_end"], "2025-12-31")
        self.assertEqual(q["method"], DESCRIPTIVE_METHOD)
        # 31 calendar slots * 25 years = 775 support days
        self.assertEqual(q["support_days"], 775)

        # Quantiles must be finite, non-negative, and strictly ordered q10 <= q50 <= q90
        tmax = q["tmax_c"]
        et0 = q["et0_mm_day"]
        self.assertTrue(tmax["q10"] <= tmax["q50"] <= tmax["q90"])
        self.assertTrue(et0["q10"] <= et0["q50"] <= et0["q90"])
        self.assertTrue(et0["q10"] > 0)
        self.assertEqual(res["units"]["tmax_c"], "degC")
        self.assertEqual(res["units"]["et0_mm_day"], "mm/day")

    def test_climatology_ml_fit_2001_2018(self):
        res = self.store.get_climatology("2028-02-29", reference="ml_fit_2001_2018")
        self.assertEqual(res["status"], "complete")
        self.assertEqual(res["reference_id"], "ml_fit_2001_2018")
        q = res["quantiles"]
        self.assertEqual(q["target_date"], "2028-02-29")
        self.assertEqual(q["reference_start"], "2001-01-01")
        self.assertEqual(q["reference_end"], "2018-12-31")
        self.assertEqual(q["method"], RESEARCH_METHOD)
        self.assertEqual(q["support_days"], 544)

    def test_leap_day_climatology(self):
        # Leap day query in leap year vs non-leap year resolves to the same calendar slot
        res_leap = self.store.get_climatology("2024-02-29")
        res_other = self.store.get_climatology("2028-02-29")
        self.assertEqual(
            res_leap["quantiles"]["tmax_c"]["q50"],
            res_other["quantiles"]["tmax_c"]["q50"],
        )


if __name__ == "__main__":
    unittest.main()
