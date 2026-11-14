"""Planting-window comparison on SYNTHETIC weather with hand-computed expectations (not NASA data)."""

import json
import math
import unittest
from datetime import date, timedelta

from backend.app.replay.dataset import ClimateInputError
from backend.app.replay.windows import compare_planting_windows, summarize


class _Clim:
    """SYNTHETIC climatology: q10/q50/q90 = 10/20/30 for Tmax, 1/2/3 for ET0 on every date."""

    def for_date(self, day):
        return {"target_date": day.isoformat(), "support_days": 31,
                "tmax_c": {"q10": 10.0, "q50": 20.0, "q90": 30.0}, "et0_mm_day": {"q10": 1.0, "q50": 2.0, "q90": 3.0}}


class SyntheticStore:
    """Tmax = 20 + (year - 2001) + 0.1 * day_index_in_year; ET0 = 5.0 (W1) everywhere. Exact arithmetic."""

    def __init__(self, first=date(2001, 1, 1), last=date(2006, 12, 31), missing=(), recent=()):
        self._weather, self._quality = {}, {}
        day = first
        while day <= last:
            if day not in missing:
                index = (day - date(day.year, 1, 1)).days
                self._weather[day] = {"tmax_c": 20.0 + (day.year - 2001) + 0.1 * index, "et0_mm_day": 5.0,
                                      "snapshot": "recent" if day in recent else "historical"}
                self._quality[day] = {"disposition": "retain"}
            day += timedelta(days=1)
        self._fit_reference = _Clim()
        self._source_hashes = {"historical": "synthetic"}

    def _meta(self, days):
        return {"site_id": "synthetic", "dataset_version": "SYNTHETIC"}


YEARS = [2001, 2002, 2003, 2004, 2005]


class Statistics(unittest.TestCase):
    def test_summary_sample_sd_and_quantiles(self):
        s = summarize([1.0, 2.0, 3.0, 4.0])
        self.assertAlmostEqual(s["mean"], 2.5)
        self.assertAlmostEqual(s["sd_sample"], math.sqrt(5 / 3))  # n-1, not population sqrt(1.25)
        self.assertAlmostEqual(s["median"], 2.5)
        self.assertAlmostEqual(s["q10"], 1.3)
        self.assertIsNone(summarize([7.0])["sd_sample"])
        self.assertEqual(summarize([])["n"], 0)


class Windows(unittest.TestCase):
    def setUp(self):
        self.store = SyntheticStore()

    def test_means_totals_and_paired_differences(self):
        r = compare_planting_windows(self.store, ["2027-05-28", "2027-06-01"], window_days=14, years=YEARS)
        a = r["layer_a_historical"]
        self.assertEqual(r["status"], "complete")
        w1 = a["windows"]["W1"]["per_year"][0]  # 2001: May 28 is day index 147 (non-leap)
        expected_tmax = 20.0 + 0.1 * (147 + 147 + 13) / 2
        self.assertAlmostEqual(w1["tmax_mean_c"], expected_tmax)
        self.assertAlmostEqual(w1["tmax_max_c"], 20.0 + 0.1 * 160)
        self.assertEqual(w1["days"], 14)
        self.assertAlmostEqual(w1["et0_total_mm"], 70.0)
        self.assertAlmostEqual(w1["et0_mean_mm_day"], 5.0)
        diff = a["paired_differences"]["W2"]["tmax_mean_c"]
        self.assertAlmostEqual(diff["mean"], 0.4)  # 4 days later * 0.1 degC, every year
        self.assertEqual((diff["years_b_higher"], diff["years_b_lower"], diff["n"]), (5, 0, 5))
        self.assertAlmostEqual(a["paired_differences"]["W2"]["et0_total_mm"]["mean"], 0.0)

    def test_leap_years_keep_window_length(self):
        r = compare_planting_windows(self.store, ["2027-05-28"], window_days=14, years=[2003, 2004])
        rows = r["layer_a_historical"]["windows"]["W1"]["per_year"]
        self.assertEqual([x["days"] for x in rows], [14, 14])
        self.assertEqual([x["start"] for x in rows], ["2003-05-28", "2004-05-28"])

    def test_feb29_start_excludes_non_leap_years_explicitly(self):
        r = compare_planting_windows(self.store, ["2028-02-29"], window_days=10, years=[2003, 2004, 2005])
        a = r["layer_a_historical"]
        self.assertEqual(a["years_used"], [2004])
        self.assertEqual({e["year"]: e["reasons"][0]["reason"] for e in a["years_excluded"]},
                         {2003: "date_not_in_year", 2005: "date_not_in_year"})
        self.assertEqual(r["status"], "partial")

    def test_december_january_rollover(self):
        r = compare_planting_windows(self.store, ["2027-12-25"], window_days=14, years=[2003, 2006])
        a = r["layer_a_historical"]
        self.assertEqual(a["windows"]["W1"]["per_year"][0]["end"], "2004-01-07")
        self.assertEqual(a["years_excluded"][0]["year"], 2006)  # needs 2007 data, which does not exist
        self.assertEqual(a["years_excluded"][0]["reasons"][0]["reason"], "window_outside_dataset")

    def test_cross_year_pairing_keeps_relative_offset(self):
        r = compare_planting_windows(self.store, ["2027-12-30", "2028-01-03"], window_days=3, years=[2002])
        rows = r["layer_a_historical"]["windows"]
        self.assertEqual((rows["W1"]["per_year"][0]["start"], rows["W2"]["per_year"][0]["start"]),
                         ("2002-12-30", "2003-01-03"))

    def test_missing_day_excludes_whole_year_from_all_windows(self):
        store = SyntheticStore(missing={date(2002, 6, 5)})
        r = compare_planting_windows(store, ["2027-05-28", "2027-06-20"], years=YEARS)
        a = r["layer_a_historical"]
        self.assertNotIn(2002, a["years_used"])
        self.assertEqual(len(a["windows"]["W2"]["per_year"]), 4)  # paired: W2 also drops 2002
        self.assertEqual(a["paired_differences"]["W2"]["tmax_mean_c"]["n"], 4)

    def test_recent_snapshot_is_quarantined_by_default(self):
        store = SyntheticStore(recent={date(2005, 6, 2)})
        r = compare_planting_windows(store, ["2027-05-28"], years=[2005])
        self.assertEqual(r["status"], "unavailable")
        self.assertEqual(r["farmer_summary"], [])
        r = compare_planting_windows(store, ["2027-05-28"], years=[2005], include_recent_snapshot=True)
        self.assertEqual(r["status"], "complete")

    def test_layer_b_is_separate_and_labelled(self):
        r = compare_planting_windows(self.store, ["2027-05-28", "2027-06-01"], window_days=14, years=YEARS)
        b = r["layer_b_climatology"]
        self.assertEqual(b["windows"]["W1"]["summary"]["tmax_q50_mean_c"], 20.0)
        self.assertEqual(b["windows"]["W1"]["summary"]["et0_q50_sum_mm"], 28.0)
        self.assertEqual(b["windows"]["W1"]["start"], "2027-05-28")
        self.assertEqual(b["differences_q50"]["W2"]["tmax_q50_mean_c"], 0.0)
        self.assertIn("not a forecast", " ".join(r["limitations"]))

    def test_statuses_echoed_never_computed(self):
        r = compare_planting_windows(self.store, ["2027-05-28", "2027-06-01"], years=YEARS,
                                     planner_statuses={"2027-05-28": "needs_review"})
        self.assertEqual([w["planner_status"] for w in r["windows"]], ["needs_review", "not_supplied"])
        self.assertFalse(r["feasibility"]["climate_changes_planner_status"])

    def test_invalid_inputs_raise(self):
        bad = [dict(sow_dates=[]), dict(sow_dates="2027-05-28"), dict(sow_dates=["2027-5-28"]),
               dict(sow_dates=["2027-02-30"]), dict(sow_dates=["2027-05-28", "2027-05-28"]),
               dict(sow_dates=["2027-05-28"] * 5), dict(sow_dates=["2027-05-28"], window_days=0),
               dict(sow_dates=["2027-05-28"], window_days=True), dict(sow_dates=["2027-05-28"], window_days=121),
               dict(sow_dates=["2027-05-28"], years=[]), dict(sow_dates=["2027-05-28"], years=[2002, 2002]),
               dict(sow_dates=["2027-05-28"], planner_statuses={"2027-05-28": "valid"}),
               dict(sow_dates=["2027-05-28"], planner_statuses={"2027-06-01": "needs_review"})]
        for kwargs in bad:
            with self.subTest(kwargs=kwargs), self.assertRaises(ClimateInputError):
                compare_planting_windows(self.store, **kwargs)

    def test_json_safe_and_deterministic(self):
        a = compare_planting_windows(self.store, ["2027-05-28", "2027-06-01"], years=YEARS)
        b = compare_planting_windows(self.store, ["2027-05-28", "2027-06-01"], years=list(reversed(YEARS)))
        self.assertEqual(json.dumps(a, allow_nan=False, sort_keys=True), json.dumps(b, allow_nan=False, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
