"""Equal-length planting-window comparison: historical NASA POWER days (Layer A) and
Refaat's evaluated seasonal climatology (Layer B).

Climate evidence only. It never decides or changes agricultural feasibility, and it never
invents crop durations: a window is an illustrative calendar interval, not a growth stage.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

from .climatology import RESEARCH_METHOD, TRAIN_END, TRAIN_START, linear_quantile
from .dataset import ClimateInputError, ClimateStore, Json, iso_day

ANALYSIS_KIND = "historical_planting_window_comparison"
STATUSES = ("feasible", "rejected", "needs_review")
HISTORICAL_YEARS = tuple(range(2001, 2026))  # 'historical' snapshot; 2026 is the quarantined 'recent' snapshot
METRICS = ("tmax_mean_c", "tmax_max_c", "et0_mean_mm_day", "et0_total_mm")
UNITS = {"tmax_mean_c": "degC", "tmax_max_c": "degC", "et0_mean_mm_day": "mm/day", "et0_total_mm": "mm"}
METRIC_DEFINITIONS = {
    "tmax_mean_c": "Mean of the daily maximum air temperatures over the window's days.",
    "tmax_max_c": "Highest single daily maximum air temperature in the window.",
    "et0_mean_mm_day": "Mean daily FAO-56 grass-reference ET0 over the window.",
    "et0_total_mm": "Sum of daily ET0 over the window (equals mean x window days).",
}
# Cited from Refaat's evaluation artifacts; not recomputed here (see docs/reviews/season-replay-final-audit.md).
BASELINE_EVALUATION = {
    "method": RESEARCH_METHOD,
    "reference_period": [TRAIN_START.isoformat(), TRAIN_END.isoformat()],
    "diagnostic_validation_2019_2021": {
        "source": "refaat-data-ml/ML_HANDOFF/reference/metrics.json",
        "scored_target_days": 252,
        "mae": {"tmax_c": 2.534365188507807, "et0_mm_day": 0.583124450747929},
        "interval_80_coverage": {"tmax_c": 0.7936507936507936, "et0_mm_day": 0.8174603174603174},
        "ridge_mae_same_split": {"tmax_c": 2.5845806020312008, "et0_mm_day": 0.6084626644929889},
    },
    "archived_holdout_jul_oct_2026": {
        "source": "archive-snapshot/work/validation_2026-11-10/model_test/holdout_results.json",
        "note": "Consumed holdout; archival comparison only.",
        "mae": {"tmax_c": 1.6555463566499597, "et0_mm_day": 0.5234047084295449},
        "chronos2_lora_mae": {"tmax_c": 1.9875693321228027, "et0_mm_day": 0.6400626301765442},
    },
    "selection": "Seasonal climatology had lower MAE than Ridge and Chronos-2 in both evaluations; it is the selected baseline.",
}
_MONTHS_EN = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
              "October", "November", "December")
_MONTHS_AR = ("يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر",
              "أكتوبر", "نوفمبر", "ديسمبر")


def summarize(values: list[float]) -> Json:
    """Across-year summary. sd_sample uses n-1 and is null for fewer than two values."""
    n = len(values)
    if not n:
        return {"n": 0, "mean": None, "sd_sample": None, "min": None, "q10": None, "median": None,
                "q90": None, "max": None}
    ordered = sorted(values)
    mean = math.fsum(values) / n
    sd = math.sqrt(math.fsum((v - mean) ** 2 for v in values) / (n - 1)) if n > 1 else None
    return {"n": n, "mean": mean, "sd_sample": sd, "min": ordered[0], "q10": linear_quantile(ordered, 0.1),
            "median": linear_quantile(ordered, 0.5), "q90": linear_quantile(ordered, 0.9), "max": ordered[-1]}


def _int(value: Any, low: int, high: int, name: str) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ClimateInputError(f"{name} must be an integer in {low}..{high}.")
    return value


def _historical_window(store: ClimateStore, start: date, days: int, include_recent: bool) -> tuple[Json | None, str | None]:
    span = [start + timedelta(days=i) for i in range(days)]
    rows = [store._weather.get(d) for d in span]
    if any(r is None for r in rows):
        return None, "window_outside_dataset"
    if not include_recent and any(r["snapshot"] != "historical" for r in rows):
        return None, "window_enters_quarantined_recent_snapshot"
    tmax = [r["tmax_c"] for r in rows]
    et0 = [r["et0_mm_day"] for r in rows]
    total = math.fsum(et0)
    return {"start": span[0].isoformat(), "end": span[-1].isoformat(), "days": days,
            "tmax_mean_c": math.fsum(tmax) / days, "tmax_max_c": max(tmax),
            "et0_mean_mm_day": total / days, "et0_total_mm": total,
            "snapshots": sorted({r["snapshot"] for r in rows}),
            "qc_review_days": sum(store._quality[d]["disposition"] == "retain_review" for d in span)}, None


def _climatology_window(store: ClimateStore, start: date, days: int) -> Json:
    daily = []
    for i in range(days):
        q = store._fit_reference.for_date(start + timedelta(days=i))
        daily.append({"date": q["target_date"], "support_days": q["support_days"],
                      "tmax_c": q["tmax_c"], "et0_mm_day": q["et0_mm_day"]})

    def mean(channel: str, key: str) -> float:
        return math.fsum(d[channel][key] for d in daily) / days

    return {"start": daily[0]["date"], "end": daily[-1]["date"], "days": days, "daily": daily,
            "summary": {"tmax_q10_mean_c": mean("tmax_c", "q10"), "tmax_q50_mean_c": mean("tmax_c", "q50"),
                        "tmax_q90_mean_c": mean("tmax_c", "q90"),
                        "et0_q10_mean_mm_day": mean("et0_mm_day", "q10"),
                        "et0_q50_mean_mm_day": mean("et0_mm_day", "q50"),
                        "et0_q90_mean_mm_day": mean("et0_mm_day", "q90"),
                        "et0_q50_sum_mm": math.fsum(d["et0_mm_day"]["q50"] for d in daily)}}


def _date_text(day: date) -> dict[str, str]:
    return {"en": f"{day.day} {_MONTHS_EN[day.month - 1]}", "ar": f"{day.day} {_MONTHS_AR[day.month - 1]}"}


def _farmer_summary(windows: list[Json], layer_a: Json, layer_b: Json, days: int) -> list[Json]:
    """Neutral, number-backed sentences. No recommendation, yield or irrigation claim."""
    out = []
    years = layer_a["years_used"]
    first = _date_text(iso_day(windows[0]["sow_date"]))
    for w in windows[1:]:
        other = _date_text(iso_day(w["sow_date"]))
        diff = layer_a["paired_differences"].get(w["window_id"])
        if not years or diff is None:
            continue
        t, e = diff["tmax_mean_c"], diff["et0_total_mm"]
        spread = layer_a["windows"][windows[0]["window_id"]]["across_years"]["tmax_mean_c"]["sd_sample"]
        spread_en = (f" The same dates usually vary by about {spread:.1f} degC from one year to the next."
                     if spread is not None else "")
        spread_ar = (f" ونفس الأيام دي بتختلف عادةً حوالي {spread:.1f} درجة من سنة للتانية."
                     if spread is not None else "")
        out.append({
            "kind": "historical_comparison",
            "en": (f"In {len(years)} past years ({years[0]}-{years[-1]}), the {days} days starting {other['en']} "
                   f"were on average {abs(t['mean']):.1f} degC {'hotter' if t['mean'] > 0 else 'cooler'} than the "
                   f"{days} days starting {first['en']} (hotter in {t['years_b_higher']} of {t['n']} years)."
                   + spread_en),
            "ar": (f"في {len(years)} سنة فاتت ({years[0]}-{years[-1]})، الـ{days} يوم اللي بتبدأ {other['ar']} كانت "
                   f"في المتوسط {'أحر' if t['mean'] > 0 else 'أبرد'} بحوالي {abs(t['mean']):.1f} درجة من الـ{days} يوم "
                   f"اللي بتبدأ {first['ar']} (كانت أحر في {t['years_b_higher']} من {t['n']} سنة)." + spread_ar),
        })
        out.append({
            "kind": "historical_et0",
            "en": (f"Reference atmospheric water demand (ET0) over the {days} days starting {other['en']} was on "
                   f"average {abs(e['mean']):.1f} mm {'higher' if e['mean'] > 0 else 'lower'} than for {first['en']} "
                   f"(higher in {e['years_b_higher']} of {e['n']} years). ET0 is weather demand on reference grass, "
                   "not your crop's water use or irrigation need."),
            "ar": (f"احتياج الجو للمية (ET0) في الـ{days} يوم اللي بتبدأ {other['ar']} كان في المتوسط "
                   f"{'أعلى' if e['mean'] > 0 else 'أقل'} بحوالي {abs(e['mean']):.1f} مم من {first['ar']} "
                   f"(كان أعلى في {e['years_b_higher']} من {e['n']} سنة). "
                   "ده مقياس لطلب الجو على نجيل مرجعي، مش استهلاك محصولك للمية ولا احتياج الري."),
        })
    for w in windows:
        s = layer_b["windows"][w["window_id"]]["summary"]
        d = _date_text(iso_day(w["sow_date"]))
        out.append({
            "kind": "typical_conditions",
            "en": (f"Typical conditions for the {days} days starting {d['en']} (NASA-based climatology, "
                   f"2001-2018): maximum temperature about {s['tmax_q50_mean_c']:.1f} degC, usually between "
                   f"{s['tmax_q10_mean_c']:.1f} and {s['tmax_q90_mean_c']:.1f} degC. This is not a weather forecast."),
            "ar": (f"الجو المعتاد في الـ{days} يوم اللي بتبدأ {d['ar']} (حسب بيانات ناسا 2001-2018): "
                   f"العظمى حوالي {s['tmax_q50_mean_c']:.1f} درجة، وغالبًا بين {s['tmax_q10_mean_c']:.1f} و"
                   f"{s['tmax_q90_mean_c']:.1f} درجة. ده مش توقع للطقس."),
        })
    out.append({
        "kind": "caution",
        "en": ("This only compares weather near the selected dates. It does not say which date gives a better "
               "harvest or uses less water, and it does not change the agricultural check of any plan."),
        "ar": ("المقارنة دي بتبص على الجو حوالين المواعيد دي بس. مش بتقول أنهي ميعاد محصوله أحسن أو بيستهلك مية أقل، "
               "ومش بتغيّر نتيجة الفحص الزراعي لأي خطة."),
    })
    return out


def compare_planting_windows(store: ClimateStore, sow_dates: list[str], *, window_days: int = 14,
                             years: list[int] | None = None, include_recent_snapshot: bool = False,
                             planner_statuses: dict[str, str] | None = None) -> Json:
    """Compare equal-length windows starting at each sow date (first = reference).

    Layer A uses the same historical years for every window (paired). Layer B uses Refaat's
    research climatology (2001-2018) for the planned dates. Statuses are echoed, never computed.
    """
    if not isinstance(sow_dates, list) or not 1 <= len(sow_dates) <= 4:
        raise ClimateInputError("sow_dates must be a list of 1 to 4 YYYY-MM-DD dates.")
    planned = [iso_day(d) for d in sow_dates]
    if len(set(planned)) != len(planned):
        raise ClimateInputError("sow_dates must be distinct.")
    _int(window_days, 1, 120, "window_days")
    requested = list(HISTORICAL_YEARS) if years is None else years
    if not isinstance(requested, list) or not requested:
        raise ClimateInputError("years must be a nonempty list.")
    requested = [_int(y, 1, 9999, "year") for y in requested]
    if len(set(requested)) != len(requested):
        raise ClimateInputError("years must be distinct.")
    statuses = dict(planner_statuses or {})
    for key, value in statuses.items():
        if key not in sow_dates or value not in STATUSES:
            raise ClimateInputError("planner_statuses maps a supplied sow date to feasible|rejected|needs_review.")

    windows = [{"window_id": f"W{i + 1}", "sow_date": d.isoformat(),
                "planned_window": [d.isoformat(), (d + timedelta(days=window_days - 1)).isoformat()],
                "planner_status": statuses.get(d.isoformat(), "not_supplied")} for i, d in enumerate(planned)]
    anchor = planned[0].year
    per_year: dict[str, list[Json]] = {w["window_id"]: [] for w in windows}
    used, excluded = [], []
    for year in sorted(requested):
        offset, rows, reasons = year - anchor, {}, []
        for w, day in zip(windows, planned):
            try:
                start = day.replace(year=day.year + offset)
            except ValueError:
                reasons.append({"window_id": w["window_id"], "reason": "date_not_in_year"})
                continue
            row, why = _historical_window(store, start, window_days, include_recent_snapshot)
            if why:
                reasons.append({"window_id": w["window_id"], "reason": why})
            else:
                rows[w["window_id"]] = {"year": year, **row}
        if reasons:
            excluded.append({"year": year, "reasons": reasons})
            continue
        used.append(year)
        for wid, row in rows.items():
            per_year[wid].append(row)

    layer_a: Json = {"years_requested": sorted(requested), "years_used": used, "years_excluded": excluded,
                     "pairing": "same historical years for every window", "windows": {}, "paired_differences": {}}
    for w in windows:
        rows = per_year[w["window_id"]]
        layer_a["windows"][w["window_id"]] = {"per_year": rows,
                                              "across_years": {m: summarize([r[m] for r in rows]) for m in METRICS}}
    reference = windows[0]["window_id"]
    for w in windows[1:]:
        diffs = {}
        for m in METRICS:
            values = [b[m] - a[m] for a, b in zip(per_year[reference], per_year[w["window_id"]])]
            diffs[m] = {**summarize(values), "years_b_higher": sum(v > 0 for v in values),
                        "years_b_lower": sum(v < 0 for v in values), "years_equal": sum(v == 0 for v in values)}
        layer_a["paired_differences"][w["window_id"]] = diffs

    layer_b: Json = {"method": RESEARCH_METHOD, "statistic": "per-day q10/q50/q90, then averaged over the window",
                     "evaluation": BASELINE_EVALUATION, "windows": {}, "differences_q50": {}}
    for w, day in zip(windows, planned):
        layer_b["windows"][w["window_id"]] = _climatology_window(store, day, window_days)
    for w in windows[1:]:
        a, b = layer_b["windows"][reference]["summary"], layer_b["windows"][w["window_id"]]["summary"]
        layer_b["differences_q50"][w["window_id"]] = {
            "tmax_q50_mean_c": b["tmax_q50_mean_c"] - a["tmax_q50_mean_c"],
            "et0_q50_mean_mm_day": b["et0_q50_mean_mm_day"] - a["et0_q50_mean_mm_day"],
            "et0_q50_sum_mm": b["et0_q50_sum_mm"] - a["et0_q50_sum_mm"]}

    status = "complete" if len(used) == len(requested) else ("partial" if used else "unavailable")
    result = {
        "status": status,
        "analysis_kind": ANALYSIS_KIND,
        "label": {"en": f"Historical {window_days}-day planting-window comparison - not a full crop-season analysis.",
                  "ar": f"مقارنة تاريخية لفترة زراعة مدتها {window_days} يوم - مش تحليل لموسم المحصول كله."},
        "window_days": window_days,
        "window_semantics": "Illustrative calendar interval starting on the sow date (inclusive); not a validated crop stage.",
        "windows": windows,
        "layer_a_historical": layer_a,
        "layer_b_climatology": layer_b,
        "units": UNITS,
        "metric_definitions": METRIC_DEFINITIONS,
        "provenance": {**store._meta([]),
                       "source_sha256": {k: v for k, v in store._source_hashes.items()
                                         if k == "historical" or include_recent_snapshot},
                       "historical_years_default": [HISTORICAL_YEARS[0], HISTORICAL_YEARS[-1]],
                       "recent_snapshot_included": include_recent_snapshot},
        "feasibility": {"climate_changes_planner_status": False,
                        "note": "Statuses come only from the Promise Test and are echoed unchanged."},
        "limitations": [
            "Layer A matches calendar dates across past years; it describes past exposure, not future weather.",
            "Layer B is a typical-condition estimate (q10-q90 range), not a forecast of daily weather.",
            "Layer A (2001-2025) and Layer B (2001-2018) use the same NASA POWER record, so they are not independent evidence.",
            "Gridded regional NASA POWER data near Sakha, not field-station measurements.",
            "ET0 is grass-reference atmospheric demand, not crop water use or irrigation requirement.",
            "Windows are fixed calendar intervals; no crop stage, harvest or field-release date is implied.",
        ],
    }
    result["farmer_summary"] = (_farmer_summary(windows, layer_a, layer_b, window_days)
                                if used else [])
    return result
