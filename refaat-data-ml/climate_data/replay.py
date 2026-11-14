"""Paired historical calendar replay of planner-supplied, fixed season windows."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from .backend import ClimateInputError, ClimateStore, Json, descriptive, iso_day

DAY = timedelta(days=1)
POLICY = "explicit_calendar_windows_v1"
INDICATORS = ("days", "et0_total_mm", "mean_et0_mm_day", "tmax_mean_c", "hot_days", "hot_day_fraction")


def _year(value: Any) -> int:
    if type(value) is not int or not 1 <= value <= 9999:
        raise ClimateInputError("Years must be integers in 1..9999.")
    return value


def _object(value: Any, required: set[str], optional: set[str], label: str) -> None:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - optional:
        raise ClimateInputError(f"Invalid {label} fields. Required: {sorted(required)}. Optional: {sorted(optional)}.")


def _text(record: Json, key: str) -> str:
    value = record[key]
    if not isinstance(value, str) or not value.strip():
        raise ClimateInputError(f"{key} must be nonempty text.")
    return value


def _plans(plans: list[Json], template_anchor_year: int) -> tuple[list[Json], list[Json]]:
    if not isinstance(plans, list) or not plans:
        raise ClimateInputError("Supply an ordered nonempty plan list; the first plan is the baseline.")
    parsed = []
    blocked = []
    for plan in plans:
        required = {"plan_id", "plan_version", "field_id", "planner_status", "seasons"}
        _object(plan, required, {"mapping_policy", "commitments"}, "plan")
        info = {key: _text(plan, key) for key in ("plan_id", "plan_version", "field_id", "planner_status")}
        if info["planner_status"] not in {"feasible", "rejected", "needs_review"}:
            raise ClimateInputError("planner_status must be feasible, rejected, or needs_review.")
        identity = {"plan_id":info["plan_id"]}
        if plan.get("mapping_policy") != POLICY:
            blocked.append({**identity, "reason":"planner_must_supply_explicit_fixed_calendar_endpoints",
                            "policy_received":plan.get("mapping_policy")})
        seasons = plan["seasons"]
        if not isinstance(seasons, list) or not seasons:
            raise ClimateInputError("Each plan must contain an ordered nonempty seasons list.")
        normalized = []
        for item in seasons:
            _object(item, {"season_id", "crop_id", "purpose", "sow_date", "crop_end_exclusive"}, set(), "season")
            season = {k: _text(item,k) for k in ("season_id","crop_id","purpose")}
            if item["sow_date"] is None or item["crop_end_exclusive"] is None:
                blocked.append({**identity, "season_id":season["season_id"], "reason":"missing_planner_endpoint"})
                continue
            season["start"] = iso_day(item["sow_date"])
            season["stop"] = iso_day(item["crop_end_exclusive"])
            if season["start"] >= season["stop"]:
                raise ClimateInputError("sow_date must precede the exclusive crop_end_exclusive.")
            if normalized and season["start"] < normalized[-1]["stop"]:
                blocked.append({**identity, "reason":"overlapping_or_unordered_windows",
                                "season_id":season["season_id"]})
            normalized.append(season)
        if len({s["season_id"] for s in normalized}) != len(normalized):
            raise ClimateInputError("Duplicate season_id.")
        commitments = plan.get("commitments", [])
        if not isinstance(commitments, list):
            raise ClimateInputError("commitments must be a list.")
        verified = []
        for item in commitments:
            _object(item, {"id","description","date"}, set(), "commitment")
            verified.append({"id": _text(item,"id"), "description": _text(item,"description"), "date": iso_day(item["date"])})
        if len({c["id"] for c in verified}) != len(verified):
            raise ClimateInputError("Duplicate commitment id.")
        if normalized and len(normalized) == len(seasons) and normalized[0]["start"].year != template_anchor_year:
            raise ClimateInputError("Each first sow_date must be in the shared template_anchor_year.")
        parsed.append({**info, "seasons":normalized, "commitments":verified})
    if len({p["plan_id"] for p in parsed}) != len(parsed):
        raise ClimateInputError("Duplicate candidate plan_id.")
    if len({p["field_id"] for p in parsed}) != 1:
        raise ClimateInputError("Comparisons require the same field_id.")
    if not blocked and len({tuple(s["season_id"] for s in p["seasons"]) for p in parsed}) != 1:
        raise ClimateInputError("Use the same ordered season_id slots for all candidates.")
    # Compare the same obligations. Only the planner can decide whether a
    # different set of protected commitments is an allowable comparison.
    commitment_keys = {tuple(sorted((c["id"], c["date"]) for c in p["commitments"])) for p in parsed}
    if len(commitment_keys) != 1:
        blocked.append({"reason":"different_protected_commitments", "plan_ids":[p["plan_id"] for p in parsed]})
    return parsed, blocked


def _mapped(plans: list[Json], offset: int) -> list[Json]:
    def translate(day: date) -> date:
        return day.replace(year=day.year + offset)
    result = []
    for p in plans:
        seasons = [{**s, "start":translate(s["start"]), "stop":translate(s["stop"])} for s in p["seasons"]]
        commitments = [{**c, "date":translate(c["date"]).isoformat()} for c in p["commitments"]]
        result.append({**p, "seasons":seasons, "commitments":commitments})
    return result


def _gap(store: ClimateStore, begin: date, stop: date) -> Json:
    days = store._slice(begin, stop-DAY)
    return {"start":begin.isoformat(), "stop_exclusive":stop.isoformat(), "metrics":store._metrics(days),
            "quality":store._quality_summary(days)}


def _profile(store: ClimateStore, plan: Json, start: date, stop: date) -> Json:
    all_days = []
    windows = []
    gaps = []
    cursor = start
    for season in plan["seasons"]:
        begin, end = season["start"], season["stop"]
        days = store._slice(begin, end-DAY)
        windows.append({
            **{k:season[k] for k in ("season_id","crop_id","purpose")},
            "sow_date":str(begin), "crop_end_exclusive":str(end),
            "metrics":store._metrics(days), "quality":store._quality_summary(days),
        })
        all_days.extend(days)
        if cursor < begin:
            gaps.append(_gap(store,cursor,begin))
        cursor = end
    if cursor < stop:
        gaps.append(_gap(store,cursor,stop))
    return {
        **{k:plan[k] for k in ("plan_id","plan_version","field_id","planner_status","commitments")},
        "seasons":windows, "outside_crop_intervals":gaps,
        "in_crop":store._metrics(all_days), "in_crop_quality":store._quality_summary(all_days),
        "outside_crop_days":sum(g["metrics"]["days"] for g in gaps),
        "outside_crop_et0_total_mm":sum(g["metrics"]["et0_total_mm"] for g in gaps),
    }


def compare(store: ClimateStore, plans: list[Json], anchor_years: list[int], template_anchor_year: int) -> Json:
    """The common block includes each full civil year touched by any crop day or explicit commitment."""
    _year(template_anchor_year)
    if not isinstance(anchor_years,list) or not anchor_years:
        raise ClimateInputError("anchor_years must be a nonempty list.")
    years = [_year(value) for value in anchor_years]
    if len(set(years)) != len(years):
        raise ClimateInputError("Duplicate anchor year would double count a block.")
    parsed, blocked = _plans(plans, template_anchor_year)
    result = {
        "status":"blocked_policy" if blocked else "complete", "mapping_policy":POLICY, "mapped_feasibility":"not_evaluated",
        "template_anchor_year":template_anchor_year, "baseline_id":parsed[0]["plan_id"],
        "requested_anchors":sorted(years), "eligible_anchors":[], "exclusions":[],
        "blocks":[], "block_variability":{}, "paired_difference_variability":{}, "blockers":blocked,
        "heat_definition":store._heat_definition(), "provenance":store._meta([]),
        "coverage":{"requested_blocks":len(years),"eligible_blocks":0},
        "quality":{"scope":"Per shared block, in-crop union, season and outside-crop interval; counts in blocks."},
    }
    if blocked:
        return result
    source_days = []
    for anchor in sorted(years):
        try:
            mapped = _mapped(parsed,anchor-template_anchor_year)
        except (ValueError,OverflowError):
            result["exclusions"].append({"anchor":anchor,"reason":"unrepresentable_explicit_date"})
            continue
        begin = min(p["seasons"][0]["start"] for p in mapped)
        stop = max(p["seasons"][-1]["stop"] for p in mapped)
        commits = [iso_day(c["date"]) for p in mapped for c in p["commitments"]]
        first = date(min([begin.year]+[d.year for d in commits]),1,1)
        last = date(max([(stop-DAY).year]+[d.year for d in commits]),12,31)
        coverage, days = store._range(str(first),str(last))
        if coverage["status"] != "complete":
            result["exclusions"].append({"anchor":anchor,"reason":"incomplete_continuous_block","first":str(first),
                                         "last":str(last),"coverage":coverage["coverage"]})
            continue
        source_days.extend(days)
        profiles = [_profile(store,p,begin,stop) for p in mapped]
        result["eligible_anchors"].append(anchor)
        baseline = profiles[0]["in_crop"]
        differences = {p["plan_id"]:{k:p["in_crop"][k]-baseline[k] for k in INDICATORS} for p in profiles[1:]}
        result["blocks"].append({
            "anchor":anchor,"block_id":f"{first.year}-{last.year}", "first":str(first),"last":str(last),
            "comparison_start":str(begin),"comparison_stop_exclusive":str(stop),"coverage":coverage["coverage"],
            "quality":coverage["quality"],"provenance":coverage["provenance"],"plans":profiles,
            "differences_from_baseline":differences,
        })
    count = len(result["eligible_anchors"])
    result["status"] = "complete" if count == len(years) else ("partial" if count else "unavailable")
    result["coverage"]["eligible_blocks"] = count
    result["provenance"] = store._meta(source_days)
    if count:
        for i,p in enumerate(parsed):
            plan_id = p["plan_id"]
            result["block_variability"][plan_id] = {
                k:descriptive([b["plans"][i]["in_crop"][k] for b in result["blocks"]]) for k in INDICATORS}
            if i:
                summary = {}
                for key in INDICATORS:
                    values = [b["differences_from_baseline"][plan_id][key] for b in result["blocks"]]
                    summary[key] = {**descriptive(values), "positive_blocks":sum(v>0 for v in values),
                                    "negative_blocks":sum(v<0 for v in values), "zero_blocks":sum(v==0 for v in values)}
                result["paired_difference_variability"][plan_id] = summary
    return result

