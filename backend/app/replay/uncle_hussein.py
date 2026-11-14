"""Uncle Hussein (UH-001) reference scenario comparison: May 28 vs June 1."""

from __future__ import annotations

from typing import Any

from .dataset import ClimateStore
from .replay import HistoricalSeasonReplay

UH001_FIELD_ID = "sakha_uh001_field"
UH001_COMMITMENTS = [
    {
        "id": "cut",
        "description": "Protected livestock cut on 20 May 2027",
        "date": "2027-05-20",
    },
    {
        "id": "occupation",
        "description": "Berseem occupation through 20 May 2027",
        "date": "2027-05-20",
    },
]


def build_uh001_plans() -> dict[str, dict[str, Any]]:
    """Build exact 4-season plans grounded in UH-001 reference scenario."""
    # Season 1: Berseem (winter 2026/27).
    # Cut on 2027-05-20. Exclusive crop end 2027-05-21. Release 2027-05-21.
    s1 = {
        "season_id": "s1_berseem",
        "crop_id": "berseem",
        "purpose": "forage",
        "sow_date": "2026-11-01",
        "crop_end_exclusive": "2027-05-21",
    }

    # Season 3: Wheat (winter 2027/28).
    s3 = {
        "season_id": "s3_wheat",
        "crop_id": "wheat",
        "purpose": "grain",
        "sow_date": "2027-11-20",
        "crop_end_exclusive": "2028-04-26",
    }

    # Season 4: Sorghum (summer 2028).
    s4 = {
        "season_id": "s4_sorghum",
        "crop_id": "grain_sorghum",
        "purpose": "grain",
        "sow_date": "2028-06-01",
        "crop_end_exclusive": "2028-09-22",
    }

    # Baseline P0: Farmer's original intention.
    # Maize sown on 2027-05-15 conflicts with protected cut on 2027-05-20.
    # Feasibility status: rejected.
    p0 = {
        "plan_id": "UH001_P0_BASELINE",
        "plan_version": "1",
        "field_id": UH001_FIELD_ID,
        "planner_status": "rejected",
        "mapping_policy": "explicit_calendar_windows_v1",
        "commitments": list(UH001_COMMITMENTS),
        "seasons": [
            s1,
            {
                "season_id": "s2_maize",
                "crop_id": "grain_maize",
                "purpose": "grain",
                "sow_date": "2027-05-15",
                "crop_end_exclusive": "2027-09-21",
            },
            s3,
            s4,
        ],
    }

    # Investigation R1: Timing variant (earliest calendar-compatible sowing).
    # 2027-05-21 release + 7 days preparation = 2027-05-28 sowing.
    # Sowing: 2027-05-28, harvest: 2027-10-03, crop end: 2027-10-04 (129 days duration).
    # Feasibility status: needs_review.
    r1 = {
        "plan_id": "UH001_R1_MAY28",
        "plan_version": "1",
        "field_id": UH001_FIELD_ID,
        "planner_status": "needs_review",
        "mapping_policy": "explicit_calendar_windows_v1",
        "commitments": list(UH001_COMMITMENTS),
        "seasons": [
            s1,
            {
                "season_id": "s2_maize",
                "crop_id": "grain_maize",
                "purpose": "grain",
                "sow_date": "2027-05-28",
                "crop_end_exclusive": "2027-10-04",
            },
            s3,
            s4,
        ],
    }

    # Investigation R2: Timing sensitivity (alternative later sowing).
    # Farmer permitted June 1 exploration.
    # Sowing: 2027-06-01, harvest: 2027-10-07, crop end: 2027-10-08 (129 days duration).
    # Feasibility status: needs_review.
    r2 = {
        "plan_id": "UH001_R2_JUN01",
        "plan_version": "1",
        "field_id": UH001_FIELD_ID,
        "planner_status": "needs_review",
        "mapping_policy": "explicit_calendar_windows_v1",
        "commitments": list(UH001_COMMITMENTS),
        "seasons": [
            s1,
            {
                "season_id": "s2_maize",
                "crop_id": "grain_maize",
                "purpose": "grain",
                "sow_date": "2027-06-01",
                "crop_end_exclusive": "2027-10-08",
            },
            s3,
            s4,
        ],
    }

    return {"P0": p0, "R1": r1, "R2": r2}


def compare_may28_vs_june1(
    replay_engine: HistoricalSeasonReplay | None = None,
    anchor_years: list[int] | None = None,
) -> dict[str, Any]:
    """Compare Uncle Hussein's May 28 (R1) vs June 1 (R2) options over historical NASA POWER records."""
    if replay_engine is None:
        replay_engine = HistoricalSeasonReplay()

    plans = build_uh001_plans()
    if anchor_years is None:
        # 2001 to 2023 (complete 3-year windows 2026-2028 mapped to historical records)
        anchor_years = list(range(2001, 2024))

    # Compare R1 (May 28 as baseline for this comparison) vs R2 (June 1)
    comparison_r1_r2 = replay_engine.compare_plans(
        [plans["R1"], plans["R2"]],
        anchor_years=anchor_years,
        template_anchor_year=2026,
    )

    # Also compare all three against P0 for completeness
    comparison_all = replay_engine.compare_plans(
        [plans["P0"], plans["R1"], plans["R2"]],
        anchor_years=anchor_years,
        template_anchor_year=2026,
    )

    # Detailed season-2 maize comparison
    s2_differences = []
    for block in comparison_r1_r2["blocks"]:
        anchor = block["anchor"]
        r1_s2 = next(s for s in block["plans"][0]["seasons"] if s["season_id"] == "s2_maize")
        r2_s2 = next(s for s in block["plans"][1]["seasons"] if s["season_id"] == "s2_maize")
        diff = {
            "anchor": anchor,
            "et0_total_diff_mm": round(r2_s2["metrics"]["et0_total_mm"] - r1_s2["metrics"]["et0_total_mm"], 2),
            "mean_et0_diff_mm_day": round(r2_s2["metrics"]["mean_et0_mm_day"] - r1_s2["metrics"]["mean_et0_mm_day"], 4),
            "tmax_mean_diff_c": round(r2_s2["metrics"]["tmax_mean_c"] - r1_s2["metrics"]["tmax_mean_c"], 2),
            "hot_days_diff": r2_s2["metrics"]["hot_days"] - r1_s2["metrics"]["hot_days"],
        }
        s2_differences.append(diff)

    return {
        "scenario_id": "UH-001",
        "description": "Uncle Hussein May 28 (R1) vs June 1 (R2) historical climate replay",
        "agricultural_verdict": {
            "UH001_P0_BASELINE": "rejected",
            "UH001_R1_MAY28": "needs_review",
            "UH001_R2_JUN01": "needs_review",
            "validated_feasible_count": 0,
            "note": "Agricultural feasibility is determined solely by Promise Test rules. Historical weather never alters feasibility.",
        },
        "commitments_preserved": ["cut (20 May 2027)", "occupation (through 20 May 2027)"],
        "comparison_r1_r2": comparison_r1_r2,
        "comparison_all": comparison_all,
        "season_2_maize_tradeoff_summary": {
            "r1_sowing": "2027-05-28",
            "r2_sowing": "2027-06-01",
            "sowing_offset_days": 4,
            "eligible_years_count": len(comparison_r1_r2["eligible_anchors"]),
            "paired_blocks": s2_differences,
            "variability": comparison_r1_r2["paired_difference_variability"].get("UH001_R2_JUN01", {}),
        },
        "scientific_guardrails": {
            "et0_is_not_irrigation": True,
            "etc_status": "unavailable",
            "planner_feasibility_modified": False,
        },
    }
