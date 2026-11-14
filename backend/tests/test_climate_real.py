"""Checks against the REAL Sakha NASA POWER release (sakha-power-lst-20261110-et0-v1).

Data come from MEG_CLIMATE_DATA_DIR or data/local/sakha. Optional cross-checks against Refaat's
original artifacts run when MEG_REFAAT_DIR points to his refaat-data-ml folder.
"""

import csv
import json
import os
import struct
import time
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

from backend.app.replay import dataset
from backend.app.replay.dataset import ClimateDataError, ClimateStore, resolve_data_directory
from backend.app.replay.windows import BASELINE_EVALUATION, compare_planting_windows

ROOT = resolve_data_directory()
REFAAT = os.environ.get("MEG_REFAAT_DIR")


class RealRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        started = time.perf_counter()
        cls.store = ClimateStore(ROOT)
        cls.load_seconds = time.perf_counter() - started
        cls.rows = {r["date"]: r for r in csv.DictReader(open(ROOT / "sakha_daily.csv", encoding="utf-8"))}

    def test_release_identity_units_and_coverage(self):
        release = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))
        self.assertEqual(release["dataset_version"], "sakha-power-lst-20261110-et0-v1")
        self.assertEqual((release["latitude_deg_n"], release["longitude_deg_e"]), (31.1, 30.95))
        self.assertEqual(len(self.store._days), 9435)
        self.assertEqual((self.store._days[0], self.store._days[-1]), (date(2001, 1, 1), date(2026, 10, 31)))
        self.assertEqual(len(self.rows), 9435)  # no duplicate dates
        self.assertEqual(dataset.UNITS["tmax_c"], "degC")
        self.assertEqual(dataset.UNITS["et0_mm_day"], "mm/day")
        snapshots = {r["snapshot"] for d, r in self.rows.items() if d < "2026-01-01"}
        self.assertEqual(snapshots, {"historical"})
        receipts = json.loads((ROOT / "source_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual({r["snapshot"] for r in receipts}, {"historical", "recent"})
        self.assertTrue(all("power.larc.nasa.gov" in r["url"] for r in receipts))

    def test_loader_is_read_only_and_never_runs_git(self):
        self.assertFalse(hasattr(dataset, "subprocess"))
        with self.assertRaises(ClimateDataError):
            resolve_data_directory(ROOT / "does-not-exist")
        with mock.patch.dict(os.environ, {"MEG_CLIMATE_DATA_DIR": str(ROOT / "nope")}), self.assertRaises(ClimateDataError):
            resolve_data_directory()

    def test_uh001_windows_match_independent_csv_arithmetic(self):
        r = compare_planting_windows(self.store, ["2027-05-28", "2027-06-01"])
        for wid, (m, d) in (("W1", (5, 28)), ("W2", (6, 1))):
            for row in r["layer_a_historical"]["windows"][wid]["per_year"]:
                start = date(row["year"], m, d)
                days = [(start + timedelta(i)).isoformat() for i in range(14)]
                tmax = [float(self.rows[x]["tmax_c"]) for x in days]
                et0 = [float(self.rows[x]["et0_mm_day"]) for x in days]
                self.assertAlmostEqual(row["tmax_mean_c"], sum(tmax) / 14, places=10)
                self.assertAlmostEqual(row["et0_total_mm"], sum(et0), places=10)
                self.assertEqual(row["tmax_max_c"], max(tmax))
        self.assertEqual(list(r["provenance"]["source_sha256"]), ["historical"])  # quarantined 2026 not cited

    def test_layer_b_matches_independent_quantile_from_training_file(self):
        def f32(x):
            return struct.unpack("!f", struct.pack("!f", x))[0]
        target = date(2027, 5, 28)
        centre = (date(2000, 5, 28) - date(2000, 1, 1)).days
        values = []
        for row in csv.DictReader(open(ROOT / "fit_targets.csv", encoding="utf-8")):
            d = date.fromisoformat(row["date"])
            slot = (date(2000, d.month, d.day) - date(2000, 1, 1)).days
            if min(abs(slot - centre), 366 - abs(slot - centre)) <= 15:
                values.append(f32(float(row["tmax_c"])))
        values.sort()
        rank = (len(values) - 1) * 0.5
        lo = int(rank)
        median = values[lo] + (rank - lo) * (values[lo + 1] - values[lo]) if rank > lo else values[lo]
        q = self.store._fit_reference.for_date(target)
        self.assertEqual(q["support_days"], len(values))
        self.assertAlmostEqual(q["tmax_c"]["q50"], median, places=12)
        self.assertEqual(q["method"], BASELINE_EVALUATION["method"])

    @unittest.skipUnless(REFAAT, "set MEG_REFAAT_DIR to refaat-data-ml to cross-check cited metrics")
    def test_cited_metrics_match_refaat_artifact(self):
        m = json.loads((Path(REFAAT) / "ML_HANDOFF" / "reference" / "metrics.json").read_text(encoding="utf-8"))
        cited = BASELINE_EVALUATION["diagnostic_validation_2019_2021"]
        self.assertEqual(m["method"], BASELINE_EVALUATION["method"])
        self.assertEqual(cited["mae"]["tmax_c"], m["metrics"]["tmax_c"]["mae"])
        self.assertEqual(cited["mae"]["et0_mm_day"], m["metrics"]["et0_mm_day"]["mae"])
        self.assertEqual(cited["scored_target_days"], m["metrics"]["tmax_c"]["scored_target_days"])

    def test_performance_and_payload(self):
        started = time.perf_counter()
        r = compare_planting_windows(self.store, ["2027-05-28", "2027-06-01"])
        elapsed = time.perf_counter() - started
        payload = json.dumps(r, allow_nan=False, ensure_ascii=False).encode("utf-8")
        print(f"\n[perf] store load {self.load_seconds:.2f}s, comparison {elapsed * 1000:.1f}ms, payload {len(payload)} B")
        self.assertLess(self.load_seconds, 10.0)
        self.assertLess(elapsed, 1.0)
        self.assertLess(len(payload), 250_000)


if __name__ == "__main__":
    unittest.main()
