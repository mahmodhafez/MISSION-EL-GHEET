"""Fixed-release integrity, input rejection and full numerical regression."""
import copy
import csv
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from climate_data import pipeline as p

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"


class IntegrityAndSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = p.SNAPSHOTS[1]
        cls.raw = p.strict_json((SOURCES / cls.spec.raw).read_bytes())
        cls.receipt = p.strict_json((SOURCES / cls.spec.receipt).read_bytes())

    def test_all_six_archived_file_hashes(self):
        for spec in p.SNAPSHOTS:
            for name, expected in ((spec.raw, spec.raw_sha), (spec.receipt, spec.receipt_sha),
                                   (spec.reference, spec.reference_sha)):
                with self.subTest(name=name):
                    self.assertEqual(p.sha256(SOURCES / name), expected)

    def test_duplicate_json_key_and_nonfinite_literals_rejected(self):
        for sample in (b'{"T2M_MAX":{"20010101":-999,"20010101":20}}',
                       b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}'):
            with self.subTest(sample=sample), self.assertRaises(p.DataError):
                p.strict_json(sample)

    def test_metadata_query_site_units_and_calendar(self):
        p.validate_schema(self.raw, self.receipt, self.spec)
        for case in ("site", "units", "date", "extra_date", "missing_variable", "community", "time_zone"):
            raw = copy.deepcopy(self.raw)
            receipt = copy.deepcopy(self.receipt)
            if case == "site":
                raw["geometry"]["coordinates"][1] = 31.117
            elif case == "units":
                raw["parameters"]["WS2M"]["units"] = "km/h"
                receipt["response_units"] = raw["parameters"]
            elif case == "date":
                del raw["properties"]["parameter"]["WS2M"]["20260101"]
            elif case == "extra_date":
                raw["properties"]["parameter"]["WS2M"]["20260229"] = 0.0
            elif case == "missing_variable":
                del raw["properties"]["parameter"]["WS2M"]
            elif case == "community":
                receipt["parameters"]["community"] = "RE"
            else:
                raw["header"]["time_standard"] = "UTC"
                receipt["response_header"] = raw["header"]
            with self.subTest(case=case), self.assertRaises(p.DataError):
                p.validate_schema(raw, receipt, self.spec)

    def test_invalid_observations_stop(self):
        day = "20260101"
        initial = {k: {day: values[day]} for k, values in self.raw["properties"]["parameter"].items()}
        for key, value in (("T2M_MIN", None), ("T2M_MAX", -999), ("WS2M", True),
                           ("T2MDEW", float("inf")), ("T2MDEW", float("nan")),
                           ("T2M_MIN", 110), ("ALLSKY_SFC_SW_DWN", -0.2), ("WS2M", -1),
                           ("PS",0), ("PRECTOTCORR",-1), ("RH2M",101), ("T2MDEW",-275)):
            with self.subTest(key=key,value=value), self.assertRaises(p.DataError):
                p.weather_day({**initial, key: {day:value}}, day, -999)

    def test_failed_or_repeat_build_preserves_destination(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            base = Path(temp)
            empty = base / "inputs"
            empty.mkdir()
            destination = base / "new"
            with self.assertRaises(FileNotFoundError):
                p.build_release(empty, destination)
            self.assertFalse(destination.exists())
            destination.mkdir()
            marker = destination / "sentinel.txt"
            marker.write_bytes(b"existing output")
            with self.assertRaises(FileExistsError):
                p.build_release(empty, destination)
            self.assertEqual(marker.read_bytes(), b"existing output")


class AllRowRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(dir=ROOT)
        cls.addClassCleanup(cls.directory.cleanup)
        cls.release = Path(cls.directory.name) / "release"
        cls.report = p.build_release(SOURCES, cls.release)

    def test_dates_partitions_and_source_provenance(self):
        self.assertEqual(self.report["raw_weather_values_verified"], 75480)
        self.assertEqual(self.report["days"], 9435)
        self.assertEqual(self.report["partition_counts"], {"fit":6574,"diagnostic_validation":1096,
                                                          "reserve_not_blind":1461,"2026_quarantine":304})
        self.assertEqual(self.report["leap_days"], [f"{y}-02-29" for y in (2004,2008,2012,2016,2020,2024)])
        self.assertEqual(self.report["site_id"], p.SITE_ID)
        manifests = json.loads((self.release / "provenance/source_manifest.json").read_bytes())
        for archived, generated in zip(p.SNAPSHOTS, manifests, strict=True):
            self.assertEqual(archived.name, generated["snapshot"])
            self.assertEqual(archived.raw_sha, generated["raw_sha256"])
            self.assertEqual(generated["receipt_sha256"], p.sha256(SOURCES / archived.receipt))

    def test_recomputed_three_et0_paths_and_all_12_original_fixtures_per_snapshot(self):
        for snapshot, residual in self.report["max_abs_et0_difference_mm_day"].items():
            self.assertEqual(set(residual), set(p.ET0_COLUMNS))
            for column in p.ET0_COLUMNS:
                with self.subTest(snapshot=snapshot,column=column):
                    self.assertLessEqual(residual[column], 1e-10)
            fixtures = self.report["original_scientific_fixtures"][snapshot]
            self.assertEqual(len(fixtures), 12)
            self.assertTrue(all(f["passed"] for f in fixtures))
            full = next(f for f in fixtures if "end-to-end" in f["name"])
            self.assertAlmostEqual(full["value"],3.88,delta=0.04)

    def test_original_archived_decimal_values_retained(self):
        with (self.release / "data/sakha_daily.csv").open(encoding="utf-8",newline="") as handle:
            dataset = csv.DictReader(handle)
            for spec in p.SNAPSHOTS:
                with (SOURCES / spec.reference).open(encoding="utf-8",newline="") as source:
                    for original in csv.DictReader(source):
                        generated = next(dataset)
                        self.assertEqual(original,{k:generated[k] for k in original})
            self.assertIsNone(next(dataset,None))

    def test_review_masks_and_extreme_values_remain(self):
        self.assertEqual(self.report["hard_invalid_days"], 0)
        self.assertEqual(self.report["review_days"], 937)
        self.assertEqual(self.report["seasonal_outlier_days"], 659)
        self.assertEqual(self.report["flag_counts"]["raw_ratio_below_0_3"], 38)
        self.assertEqual(self.report["flag_counts"]["dew_above_tmin"], 306)
        with (self.release / "data/sakha_daily.csv").open(encoding="utf-8") as source:
            high_day = next(r for r in csv.DictReader(source) if r["date"] == "2014-06-04")
        self.assertAlmostEqual(float(high_day["et0_mm_day"]), 14.048773842966526, places=10)


if __name__ == "__main__":
    unittest.main()
