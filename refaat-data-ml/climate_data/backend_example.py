"""Run the backend contract on the packaged release; stdout is strict JSON."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from .backend import ClimateStore


def examples(store: ClimateStore) -> dict:
    # Illustrative dates supplied as input by a hypothetical planner.
    template = {
        "plan_id":"calendar_A", "plan_version":"example-1", "field_id":"sample-field",
        "planner_status":"needs_review", "mapping_policy":"explicit_calendar_windows_v1",
        "commitments":[{"id":"cut","description":"Protected livestock cut (example commitment)","date":"2027-05-20"}],
        "seasons":[
            {"season_id":"winter1","crop_id":"berseem","purpose":"forage","sow_date":"2026-11-01","crop_end_exclusive":"2027-05-21"},
            {"season_id":"summer1","crop_id":"grain_maize","purpose":"grain","sow_date":"2027-06-01","crop_end_exclusive":"2027-09-21"},
            {"season_id":"winter2","crop_id":"wheat","purpose":"grain","sow_date":"2027-11-20","crop_end_exclusive":"2028-04-26"},
            {"season_id":"summer2","crop_id":"grain_sorghum","purpose":"grain","sow_date":"2028-06-01","crop_end_exclusive":"2028-09-22"},
        ],
    }
    other = copy.deepcopy(template)
    other["plan_id"] = "calendar_B"
    other["seasons"][1]["sow_date"] = "2027-06-08"
    other["seasons"][1]["crop_end_exclusive"] = "2027-09-29"
    start, end = "2014-06-03", "2014-06-05"
    anchors = [2015,2016,2024]
    result = {
        "request":{"site_id":"sakha_31.10_30.95","interval":[start,end],"climatology_target_date":"2028-02-29",
                   "plans":[template,other],"template_anchor_year":2026,"anchor_years":anchors},
        "daily":store.get_daily_weather(start,end),
        "climatology":store.get_climatology("2028-02-29"),
        "et0_summary":store.calculate_et0_summary(start,end),
        "heat_exposure":store.calculate_heat_exposure(start,end),
        "one_plan_replay":store.get_historical_replay(template,[2015],template_anchor_year=2026),
        "comparison":store.compare_historical_plans([template,other],anchors,template_anchor_year=2026),
        "release":store.get_data_provenance(),
    }
    return result


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data",type=Path,default=Path("data"))
    parser.add_argument("--out",type=Path,help="Write generated example JSON to a new path instead of stdout.")
    args=parser.parse_args()
    payload=json.dumps(examples(ClimateStore(args.data)),indent=2,ensure_ascii=False,allow_nan=False)
    if args.out is None:
        print(payload)
    else:
        with args.out.open("x",encoding="utf-8",newline="\n") as handle:
            handle.write(payload+"\n")


if __name__=="__main__":
    main()

