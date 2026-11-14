"""Consumer tests: import only the documented public interface and exercise the packaged files."""
import copy
import csv
import inspect
import json
import math
import statistics
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from climate_data.backend import ClimateDataError, ClimateInputError, ClimateStore
from climate_data.backend_example import examples

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class ClimateConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = ClimateStore(DATA)
        cls.example = examples(cls.store)
        with (DATA / "sakha_daily.csv").open(encoding="utf-8", newline="") as handle:
            cls.weather = {row["date"]: row for row in csv.DictReader(handle)}
        cls.plans = cls.example["request"]["plans"]

    def test_contract_signatures_and_json_serialization(self):
        expected = {
            "get_daily_weather": ("start", "end"),
            "get_climatology": ("target_date", "reference"),
            "calculate_et0_summary": ("start", "end"),
            "calculate_heat_exposure": ("start", "end"),
            "get_historical_replay": ("plan", "anchor_years", "template_anchor_year"),
            "compare_historical_plans": ("plans", "anchor_years", "template_anchor_year"),
            "get_data_provenance": (),
        }
        for name, fields in expected.items():
            sig = inspect.signature(getattr(self.store, name))
            self.assertEqual(tuple(sig.parameters), fields)
            self.assertTrue(all(p.annotation is not inspect.Parameter.empty for p in sig.parameters.values()))
            self.assertNotEqual(sig.return_annotation, inspect.Signature.empty)
            if "template_anchor_year" in fields:
                self.assertEqual(sig.parameters["template_anchor_year"].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertEqual(json.loads(json.dumps(self.example, allow_nan=False)), self.example)

    def test_daily_rows_flags_units_sources_and_copy_isolation(self):
        observed = self.store.get_daily_weather("2025-12-31", "2026-01-01")
        self.assertEqual(observed["status"], "complete")
        self.assertEqual(observed["coverage"], {"expected_days":2, "valid_days":2, "fraction":1})
        self.assertEqual([r["snapshot"] for r in observed["rows"]], ["historical","recent"])
        self.assertEqual(observed["units"]["et0_mm_day"], "mm/day")
        self.assertEqual(observed["units"]["tmax_c"], "degC")
        self.assertIn("mixed_sources_in_response", observed["rows"][1]["flags"])
        self.assertIn("recent", observed["provenance"]["source_sha256"])
        observed["rows"][0]["tmax_c"] = -1000
        daily = self.store.get_daily_weather("2025-12-31", "2025-12-31")["rows"][0]
        self.assertEqual(daily["tmax_c"], float(self.weather[daily["date"]]["tmax_c"]))
        extreme = self.store.get_daily_weather("2014-06-04", "2014-06-04")["rows"][0]
        self.assertEqual(extreme["disposition"], "retain_review")
        self.assertEqual(set(extreme["statistical_columns"]), {"wind2_m_s","solar_mj_m2_day","et0_mm_day"})

    def test_et0_and_temperature_inclusive_including_leap_day(self):
        start, end = "2020-02-28", "2020-03-01"
        ref = [row for day,row in self.weather.items() if start <= day <= end]
        self.assertEqual(len(ref), 3)
        et0 = [float(r["et0_mm_day"]) for r in ref]
        tmax = [float(r["tmax_c"]) for r in ref]
        got = self.store.calculate_et0_summary(start, end)["metrics"]
        self.assertEqual(got["days"], 3)
        self.assertAlmostEqual(got["et0_total_mm"], math.fsum(et0))
        self.assertAlmostEqual(got["mean_et0_mm_day"], statistics.mean(et0))
        self.assertEqual(got["tmax_min_c"], min(tmax))
        self.assertEqual(got["tmax_max_c"], max(tmax))
        self.assertAlmostEqual(got["tmax_mean_c"], statistics.mean(tmax))

    def test_fit_only_heat_threshold_and_inclusive_operator(self):
        values = [float(r["tmax_c"]) for day,r in self.weather.items() if day < "2019"]
        threshold = statistics.quantiles(values, n=10, method="inclusive")[8]
        example = self.example["heat_exposure"]
        self.assertAlmostEqual(example["definition"]["threshold_c"], threshold, places=12)
        self.assertEqual(example["definition"]["fit_end"], "2018-12-31")
        self.assertEqual(example["definition"]["operator"], ">=")
        for hits in (0, 1):
            day = next(d for d,r in self.weather.items() if
                       (float(r["tmax_c"]) == threshold if hits else float(r["tmax_c"]) < threshold))
            result = self.store.calculate_heat_exposure(day,day)
            self.assertEqual((result["hot_days"], result["hot_day_fraction"]), (hits,hits))

    def test_partial_unavailable_and_invalid_dates(self):
        for start,end,status,valid in [
            ("2000-12-31","2001-01-02","partial",2), ("2026-10-31","2026-11-01","partial",1),
            ("2030-01-01","2030-01-05","unavailable",0)]:
            daily = self.store.get_daily_weather(start,end)
            self.assertEqual((daily["status"],len(daily["rows"])),(status,valid))
            self.assertEqual(daily["coverage"]["valid_days"],valid)
            self.assertIsNone(self.store.calculate_et0_summary(start,end)["metrics"])
            self.assertIsNone(self.store.calculate_heat_exposure(start,end)["hot_days"])
        for begin,end in [("20250201","2025-02-02"),("2019-02-29","2019-03-01"),
                          ("2021-01-02","2021-01-01"),(None,"2021-01-01")]:
            with self.assertRaises(ClimateInputError):
                self.store.get_daily_weather(begin,end)

    def test_release_identity_and_tampered_cache_refused(self):
        prov = self.store.get_data_provenance()
        self.assertEqual(prov["coverage"]["valid_days"],9435)
        self.assertEqual(prov["quality"]["review_days"],937)
        src = json.loads((DATA/"source_manifest.json").read_bytes())
        self.assertEqual(prov["source_receipts"],src)
        self.assertEqual(prov["provenance"]["source_sha256"],{r["snapshot"]:r["raw_sha256"] for r in src})
        release = json.loads((DATA/"release.json").read_bytes())
        for key in ("dataset_version","et0_method_version","site_id"):
            self.assertEqual(prov["provenance"][key],release[key])
        with self.assertRaises(ClimateInputError):
            ClimateStore(DATA,"other")
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            folder = Path(temp)
            with self.assertRaises(ClimateDataError):
                ClimateStore(folder)
            (folder/"release.json").write_bytes((DATA/"release.json").read_bytes())
            (folder/"sakha_daily.csv").write_bytes(b"wrong daily values")
            with self.assertRaisesRegex(ClimateDataError,"identity mismatch"):
                ClimateStore(folder)

    def test_references_have_separate_support_and_quantiles(self):
        for ref, end, support in [("ml_fit_2001_2018",2018,544),("historical_2001_2025",2025,756)]:
            result = self.store.get_climatology("2028-02-29",reference=ref)
            q = result["quantiles"]
            self.assertEqual((q["reference_end"],q["support_days"]), (f"{end}-12-31",support))
            self.assertEqual(result["coverage"]["valid_days"],support)
            self.assertEqual(q["tmax_c"]["q50"],self.store.get_climatology("2024-02-29",ref)["quantiles"]["tmax_c"]["q50"])
            if end == 2025:
                ref_tmax = [float(r["tmax_c"]) for d,r in self.weather.items() if d < "2026" and "02-14" <= d[5:] <= "03-15"]
                self.assertEqual(q["tmax_c"]["q50"],statistics.median(ref_tmax))
        with self.assertRaises(ClimateInputError):
            self.store.get_climatology("2020-02-29","all_history")

    def test_paired_continuous_four_season_blocks_and_duration_accounting(self):
        result = self.example["comparison"]
        self.assertEqual(result["status"],"partial")
        self.assertEqual(result["eligible_anchors"],[2015,2016])
        self.assertEqual(result["exclusions"][0]["anchor"],2024)
        self.assertEqual(result["exclusions"][0]["reason"],"incomplete_continuous_block")
        self.assertEqual(result["mapped_feasibility"],"not_evaluated")
        self.assertEqual(result["coverage"],{"requested_blocks":3,"eligible_blocks":2})
        total_diffs = []
        for block in result["blocks"]:
            first, last = map(date.fromisoformat, (block["first"],block["last"]))
            self.assertEqual(block["coverage"]["valid_days"],(last-first).days+1)
            a,b=block["plans"]
            self.assertEqual(len(a["seasons"]),4)
            for plan in (a,b):
                self.assertEqual(plan["planner_status"], "needs_review")
                self.assertEqual(plan["commitments"][0]["date"], f'{block["anchor"]+1}-05-20')
                begin,stop = map(date.fromisoformat,(block["comparison_start"],block["comparison_stop_exclusive"]))
                self.assertEqual(plan["in_crop"]["days"]+plan["outside_crop_days"],(stop-begin).days)
                envelope = self.store.calculate_et0_summary(str(begin),str(stop-timedelta(days=1)))["metrics"]
                self.assertAlmostEqual(plan["in_crop"]["et0_total_mm"]+plan["outside_crop_et0_total_mm"],envelope["et0_total_mm"])
                for season in plan["seasons"]:
                    end = date.fromisoformat(season["crop_end_exclusive"])-timedelta(days=1)
                    daily = [float(row["et0_mm_day"]) for d,row in self.weather.items() if season["sow_date"]<=d<=str(end)]
                    self.assertEqual(season["metrics"]["days"],len(daily))
                    self.assertAlmostEqual(season["metrics"]["mean_et0_mm_day"],statistics.mean(daily))
                    self.assertIn("review_days",season["quality"])
            diff=block["differences_from_baseline"]["calendar_B"]
            self.assertEqual(diff["days"],1)
            for key in ("et0_total_mm","mean_et0_mm_day","hot_day_fraction"):
                self.assertAlmostEqual(diff[key],b["in_crop"][key]-a["in_crop"][key])
            total_diffs.append(diff["et0_total_mm"])
        summary = result["paired_difference_variability"]["calendar_B"]["et0_total_mm"]
        self.assertEqual(summary["median"],statistics.median(total_diffs))
        self.assertEqual(summary["positive_blocks"],sum(d>0 for d in total_diffs))
        self.assertEqual(result["block_variability"]["calendar_A"]["days"]["count"],2)
        one = self.example["one_plan_replay"]
        self.assertEqual(one["status"],"complete")
        self.assertEqual(one["blocks"][0]["plans"][0],result["blocks"][0]["plans"][0])

    def test_leap_rules_exclude_anchor_for_every_plan_or_include_extra_day(self):
        plan=copy.deepcopy(self.plans[0])
        plan.update(commitments=[],seasons=[{"season_id":"one","crop_id":"x","purpose":"demo",
                                              "sow_date":"2024-02-28","crop_end_exclusive":"2024-03-02"}])
        second=copy.deepcopy(plan)
        second["plan_id"]="second"
        second["seasons"][0]["sow_date"]="2024-02-29"
        pair=self.store.compare_historical_plans([plan,second],[2019,2020],template_anchor_year=2024)
        self.assertEqual(pair["eligible_anchors"],[2020])
        self.assertEqual(pair["exclusions"],[{"anchor":2019,"reason":"unrepresentable_explicit_date"}])
        single=self.store.get_historical_replay(plan,[2019,2020],template_anchor_year=2024)
        self.assertEqual([b["plans"][0]["in_crop"]["days"] for b in single["blocks"]],[2,3])

    def test_unknown_policy_missing_endpoint_and_overlap_do_not_produce_evidence(self):
        for change,reason in [("policy","planner_must_supply_explicit_fixed_calendar_endpoints"),
                              ("date","missing_planner_endpoint"),("overlap","overlapping_or_unordered_windows")]:
            plans=copy.deepcopy(self.plans)
            if change=="policy":
                plans[1]["mapping_policy"]="thermal_time"
            elif change=="date":
                plans[1]["seasons"][0]["crop_end_exclusive"]=None
            else:
                plans[1]["seasons"][1]["sow_date"]="2027-05-15"
            result=self.store.compare_historical_plans(plans,[2015],template_anchor_year=2026)
            self.assertEqual(result["status"],"blocked_policy")
            self.assertIn(reason,{entry["reason"] for entry in result["blockers"]})
            self.assertEqual(result["blocks"],[])
        none=self.store.get_historical_replay(self.plans[0],[2024],template_anchor_year=2026)
        self.assertEqual(none["status"],"unavailable")
        self.assertEqual(none["block_variability"],{})

    def test_schema_mismatches_refused_and_planner_status_never_inferred(self):
        for key,val in [("field_id","other"),("plan_id",self.plans[0]["plan_id"]),("planner_status","invented")]:
            plans=copy.deepcopy(self.plans)
            plans[1][key]=val
            with self.assertRaises(ClimateInputError):
                self.store.compare_historical_plans(plans,[2015],template_anchor_year=2026)
        for anchors in ([2015,2015],[True],[],[0]):
            with self.assertRaises(ClimateInputError):
                self.store.get_historical_replay(self.plans[0],anchors,template_anchor_year=2026)
        plan=copy.deepcopy(self.plans[0])
        plan["planner_status"]="rejected"
        out=self.store.get_historical_replay(plan,[2015],template_anchor_year=2026)
        self.assertEqual(out["blocks"][0]["plans"][0]["planner_status"],"rejected")
        self.assertEqual(out["mapped_feasibility"],"not_evaluated")

    def test_protected_commitments_must_be_comparable_and_inside_covered_years(self):
        plans=copy.deepcopy(self.plans)
        plans[1]["commitments"][0]["date"]="2027-05-15"
        result=self.store.compare_historical_plans(plans,[2015],template_anchor_year=2026)
        self.assertEqual(result["status"],"blocked_policy")
        self.assertEqual(result["blocks"],[])
        self.assertIn("different_protected_commitments",{b["reason"] for b in result["blockers"]})
        plan=copy.deepcopy(self.plans[0])
        plan["commitments"][0]["date"]="2037-01-01"
        result=self.store.get_historical_replay(plan,[2015],template_anchor_year=2026)
        self.assertEqual(result["status"],"unavailable")
        self.assertEqual(result["exclusions"][0]["last"],"2026-12-31")


if __name__ == "__main__":
    unittest.main()

