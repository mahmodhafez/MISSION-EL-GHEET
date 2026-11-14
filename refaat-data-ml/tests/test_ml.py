"""Regression and contract tests for the public ML handoff. Run from the ZIP root."""
import csv
import json
import math
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from climate_data.climatology import (
    RESEARCH_METHOD, TRAIN_END, TRAIN_START, SeasonalClimatology, calendar_window,
    float32, iso_date, linear_quantile, load_targets, phase,
)
from climate_data.evaluation import (
    load_diagnostic_data, load_windows, run, score_predictions, seasonal_predictions,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIXTURE = Path(__file__).parent / "fixtures" / "diagnostic_baseline.json"


class SeasonalReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_diagnostic_data(DATA)
        cls.reference = SeasonalClimatology.from_csv(DATA / "fit_targets.csv")

    def test_exact_splits_and_leaps(self):
        self.assertEqual(len(self.data.training), 6574)
        self.assertEqual((self.data.training[0].day, self.data.training[-1].day), (TRAIN_START, TRAIN_END))
        self.assertEqual(len(self.data.validation), 1096)
        self.assertEqual((min(self.data.validation), max(self.data.validation)), (date(2019,1,1), date(2021,12,31)))
        self.assertEqual(sum(day.day == 29 and day.month == 2 for day in self.data.validation), 1)
        self.assertEqual(self.data.training[0].tmax_c, 22.83)
        self.assertAlmostEqual(self.data.training[0].et0_mm_day, 2.7039757858768434)

    def test_new_year_circular_window(self):
        expected = {phase(date(2000, 12, day)) for day in range(17,32)}
        expected.update(phase(date(2000, 1, day)) for day in range(1,17))
        self.assertEqual(set(calendar_window("2019-01-01")), expected)
        self.assertEqual(self.reference.for_date("2020-01-01")["support_days"], 18*31)

    def test_leap_day_has_separate_phase_and_support(self):
        self.assertEqual(phase(date(2020,2,29)), 59)
        self.assertEqual(phase(date(2019,3,1)), phase(date(2020,3,1)))
        self.assertIn(phase(date(2000,2,14)), calendar_window("2020-02-29"))
        self.assertIn(phase(date(2000,3,15)), calendar_window("2020-02-29"))
        self.assertEqual(self.reference.for_date("2020-02-29")["support_days"], 30*18+4)

    def test_descriptive_reference_separate_from_training(self):
        with (DATA / "diagnostic_validation_targets.csv").open(newline="", encoding="utf-8") as src:
            descriptive = SeasonalClimatology.from_records(csv.DictReader(src),"2019-01-01","2021-12-31")
        self.assertNotEqual(descriptive.method, RESEARCH_METHOD)
        self.assertEqual(descriptive.for_date("2028-02-29")["reference_end"], "2021-12-31")
        with self.assertRaises(ValueError):
            SeasonalClimatology.from_csv(DATA / "diagnostic_validation_targets.csv")
        with self.assertRaises(ValueError):
            SeasonalClimatology(self.data.training + (self.data.validation[date(2019,1,1)],),
                               TRAIN_START, TRAIN_END, research=True)

    def test_contiguous_schema_finite_numeric_and_date_validation(self):
        for content in [
            "date,tmax_c,rain\n2001-01-01,20,3\n",
            "date,tmax_c,et0_mm_day\n2001-01-01,20,3,99\n",
            "date,tmax_c,et0_mm_day\n2001-01-01,20,\n",
            "date,tmax_c,et0_mm_day\n2001-01-01,-999,2\n",
            "date,tmax_c,et0_mm_day\n2001-01-01,20,nan\n",
            "date,tmax_c,et0_mm_day\n2001-01-01,20,3\n2001-01-01,21,4\n",
            "date,tmax_c,et0_mm_day\n2001-01-01,20,3\n2001-01-03,21,4\n",
        ]:
            with self.subTest(content=content), tempfile.TemporaryDirectory(dir=ROOT) as tmp:
                path = Path(tmp) / "target.csv"
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_targets(path, date(2001,1,1), date(2001,1,2))
        for bad in ["2019-02-29", "20200101", "2020-W01-1"]:
            with self.assertRaises(ValueError):
                iso_date(bad)
        self.assertEqual(linear_quantile([0,10,30,50], 0.5), 20)
        self.assertAlmostEqual(linear_quantile([0,10,30,50], 0.1), 3)

    def test_schema_valid_value_tampering_changes_release_hash(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            copy = Path(tmp)
            for name in ("release.json","fit_targets.csv","diagnostic_validation_targets.csv","forecast_windows.csv"):
                (copy/name).write_bytes((DATA/name).read_bytes())
            fit = copy/"fit_targets.csv"
            fit.write_bytes(fit.read_bytes().replace(b"22.83",b"22.84",1))
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                load_diagnostic_data(copy)

    def test_contexts_have_only_as_of_information_and_seven_disjoint_labels(self):
        scored_days = set()
        for w, history in self.data.contexts():
            self.assertEqual(len(history), 60)
            self.assertEqual(history[-1].day, w.issue - timedelta(days=7))
            self.assertEqual(history[0].day, w.issue - timedelta(days=66))
            labels = list(w.targets())
            self.assertEqual([(day-history[-1].day).days for day in labels], list(range(8,15)))
            self.assertTrue(scored_days.isdisjoint(labels))
            scored_days.update(labels)
        self.assertEqual(len(scored_days), 252)
        first = next(self.data.contexts())
        self.assertEqual(first[1][0].day, date(2018,11,10))

    def test_modified_or_consumed_window_rejected(self):
        original = (DATA/"forecast_windows.csv").read_text(encoding="utf-8")
        for damaged in [original.replace("2019-01-08", "2019-01-09",1),
                        original.replace("diagnostic_validation","consumed",1)]:
            with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
                path=Path(tmp)/"windows.csv"
                path.write_text(damaged, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_windows(path)

    def test_all_keyed_scoring_errors(self):
        rows=list(seasonal_predictions(self.reference,self.data.windows))
        for damaged in (rows[:-1], [rows[0]]+rows, [dict(rows[0], target_date="2026-07-02"),*rows[1:]],
                        [dict(rows[0],q10=1e5),*rows[1:]], [dict(rows[0],cutoff="2019-01-09"),*rows[1:]]):
            with self.assertRaises(ValueError):
                score_predictions(self.data,damaged)
        # New model's point-only estimates use same keyed scorer, in arbitrary input order.
        point=[]
        for row in reversed(rows):
            item={k:row[k] for k in ("issue","target_date","variable")}
            day=iso_date(item["target_date"])
            item["q50"]=float32(getattr(self.data.validation[day],item["variable"]))+1.0
            point.append(item)
        _,metric=score_predictions(self.data,point)
        self.assertEqual(metric["et0_mm_day"]["mae"],1.0)
        self.assertEqual(metric["tmax_c"]["bias"],1.0)
        self.assertNotIn("interval_80_coverage",metric["et0_mm_day"])

    def test_export_against_original_validation_metrics_for_each_target_and_lead(self):
        benchmark=json.loads(FIXTURE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            result=Path(tmp)/"baseline"
            measurements=run(DATA,result)
            for target, expected in benchmark["metrics"].items():
                actual=measurements["metrics"][target]
                for name,reference in expected.items():
                    if isinstance(reference,list):
                        self.assertEqual(len(reference),len(actual[name]))
                        errors=[abs(a-b) for a,b in zip(reference,actual[name])]
                    else:
                        errors=[abs(reference-actual[name])]
                    self.assertLessEqual(max(errors),benchmark["absolute_tolerance"],(target,name))
                self.assertEqual(actual["scored_target_days"],252)
            with (result/"calendar_reference.csv").open(encoding="utf-8",newline="") as src:
                table=list(csv.DictReader(src))
            self.assertEqual(len(table),366)
            self.assertEqual(table[59]["month_day"],"02-29")
            with (result/"scored_predictions.csv").open(encoding="utf-8",newline="") as src:
                forecasts=list(csv.DictReader(src))
            self.assertEqual(len(forecasts),504)
            self.assertTrue(all(math.isfinite(float(row["truth"])) for row in forecasts))
            with self.assertRaises(FileExistsError):
                run(DATA,result)


if __name__ == "__main__":
    unittest.main()
