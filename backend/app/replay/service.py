"""Stable Python integration interface for Yahya (backend/API layer)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .climatology import SeasonalClimatology
from .dataset import ClimateStore, Json
from .evidence_card import build_climate_evidence_card
from .replay import HistoricalSeasonReplay
from .uncle_hussein import run_uh001_window_comparison
from .windows import compare_planting_windows

_STORE_CACHE: dict[str, ClimateStore] = {}


def get_climate_store(data_dir: str | Path | None = None) -> ClimateStore:
    """Return a cached or newly loaded ClimateStore instance."""
    key = str(data_dir) if data_dir is not None else "__default__"
    if key not in _STORE_CACHE:
        _STORE_CACHE[key] = ClimateStore(data_dir=data_dir)
    return _STORE_CACHE[key]


def evaluate_season_replay(
    plans: list[Json],
    anchor_years: list[int] | None = None,
    template_anchor_year: int = 2026,
    data_dir: str | Path | None = None,
) -> Json:
    """Run historical season replay over verified Sakha NASA POWER records.

    Args:
        plans: Ordered list of plan dictionaries. The first is the baseline.
               Each plan must have: plan_id, plan_version, field_id, planner_status,
               mapping_policy="explicit_calendar_windows_v1", commitments, seasons.
        anchor_years: List of calendar years to replay onto (e.g. [2015, 2016, 2020]).
                      If None, defaults to complete years [2001..2023].
        template_anchor_year: Year of each plan's first sowing date (e.g. 2026).
        data_dir: Optional custom dataset directory path.

    Returns:
        Structured replay result dictionary conforming to Yahya's ReplayResult contract.
    """
    store = get_climate_store(data_dir)
    engine = HistoricalSeasonReplay(store)
    if anchor_years is None:
        anchor_years = list(range(2001, 2024))
    return engine.compare_plans(plans, anchor_years, template_anchor_year=template_anchor_year)


def get_climatology_profile(
    target_date: str,
    reference: str = "ml_fit_2001_2018",
    data_dir: str | Path | None = None,
) -> Json:
    """Get seasonal climatology quantiles (q10, q50, q90) for target month/day.

    Default is Refaat's evaluated research baseline (2001-2018). "historical_2001_2025" is a
    separately labelled descriptive reference that was never evaluated as a predictor.

    Args:
        target_date: YYYY-MM-DD string (month/day selects circular leap-calendar slot).
        reference: "ml_fit_2001_2018" (default, evaluated baseline) or "historical_2001_2025" (descriptive).
        data_dir: Optional custom dataset directory path.

    Returns:
        Climatology response with quantiles for tmax_c and et0_mm_day, support days, units.
    """
    store = get_climate_store(data_dir)
    return store.get_climatology(target_date, reference=reference)


def compare_sowing_windows(
    sow_dates: list[str],
    *,
    window_days: int = 14,
    years: list[int] | None = None,
    planner_statuses: dict[str, str] | None = None,
    data_dir: str | Path | None = None,
) -> Json:
    """Equal-length historical windows (Layer A) plus Refaat's climatology (Layer B).

    One date evaluates a single window; two or more compare against the first date.
    planner_statuses (sow date -> Promise Test status) is echoed unchanged.
    """
    return compare_planting_windows(get_climate_store(data_dir), sow_dates, window_days=window_days,
                                    years=years, planner_statuses=planner_statuses)


def run_uncle_hussein_comparison(
    planner_statuses: dict[str, str] | None = None,
    years: list[int] | None = None,
    data_dir: str | Path | None = None,
) -> Json:
    """UH-001: 14-day windows from 28 May vs 1 June 2027. No crop-end date is assumed."""
    return run_uh001_window_comparison(get_climate_store(data_dir), planner_statuses=planner_statuses,
                                       years=years)


def create_evidence_card(
    *,
    scenario_id: str,
    scenario_revision: int,
    plan_id: str,
    plan_version: int,
    planning_result_id: str,
    plan_status: str,
    replay_result: Json | None = None,
    forecast_id: str | None = None,
    changes: list[Json] | None = None,
    assumptions: list[str] | None = None,
    outstanding_checks: list[str] | None = None,
) -> Json:
    """Construct a Climate Evidence Card adhering to Yahya's API contract."""
    replay_summary = None
    replay_id = None
    if replay_result:
        replay_id = f"replay-{scenario_id}-{plan_id}"
        eligible_anchors = replay_result.get("eligible_anchors", [])
        plan_variability = replay_result.get("block_variability", {}).get(plan_id, {})
        et0_var = plan_variability.get("et0_total_mm", {})
        hot_var = plan_variability.get("hot_days", {})
        replay_summary = {
            "eligible_blocks_count": len(eligible_anchors),
            "years_range": f"{eligible_anchors[0]}-{eligible_anchors[-1]}" if eligible_anchors else None,
            "et0_total_median_mm": et0_var.get("median"),
            "et0_total_min_mm": et0_var.get("min"),
            "et0_total_max_mm": et0_var.get("max"),
            "hot_days_median": hot_var.get("median"),
            "hot_days_min": hot_var.get("min"),
            "hot_days_max": hot_var.get("max"),
            "units": replay_result.get("units", {}),
            "status": replay_result.get("status"),
        }

    return build_climate_evidence_card(
        scenario_id=scenario_id,
        scenario_revision=scenario_revision,
        plan_id=plan_id,
        plan_version=plan_version,
        planning_result_id=planning_result_id,
        plan_status=plan_status,
        replay_id=replay_id,
        forecast_id=forecast_id,
        replay_summary=replay_summary,
        changes=changes,
        assumptions=assumptions,
        outstanding_checks=outstanding_checks,
    )
