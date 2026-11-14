"""Climate Evidence Card data model and builder aligned with Yahya's contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .dataset import Json


def build_climate_evidence_card(
    *,
    scenario_id: str,
    scenario_revision: int,
    plan_id: str,
    plan_version: int,
    planning_result_id: str,
    plan_status: str,
    replay_id: str | None = None,
    forecast_id: str | None = None,
    replay_summary: Json | None = None,
    preserved_commitment_ids: list[str] | None = None,
    changes: list[Json] | None = None,
    assumptions: list[str] | None = None,
    outstanding_checks: list[str] | None = None,
    locale: str = "ar",
) -> Json:
    """Build an EvidenceCard payload strictly conforming to docs/backend/api-contracts.md."""
    if plan_status not in {"feasible", "rejected", "needs_review"}:
        raise ValueError(f"Invalid plan_status: {plan_status}")

    # Decision state rules per contract:
    # A review draft retains rejected or needs_review plans.
    # Saving it does NOT make its status feasible.
    # Approved requires feasible and current.
    decision_state = "review_draft" if plan_status in {"rejected", "needs_review"} else "unapproved"

    input_ref = {
        "scenario_id": scenario_id,
        "scenario_revision": scenario_revision,
        "plan_ref": {
            "plan_id": plan_id,
            "plan_version": plan_version,
        },
    }

    # Bilingual takeaway parameters
    takeaway_params: dict[str, Any] = {
        "scenario_id": scenario_id,
        "plan_id": plan_id,
        "plan_status": plan_status,
        "decision_state": decision_state,
        "preserved_commitments_count": len(preserved_commitment_ids or []),
    }

    if replay_summary:
        takeaway_params.update({
            "historical_blocks_evaluated": replay_summary.get("eligible_blocks_count"),
            "historical_years_range": replay_summary.get("years_range"),
            "et0_total_median_mm": replay_summary.get("et0_total_median_mm"),
            "hot_days_median": replay_summary.get("hot_days_median"),
            "et0_unit": "mm",
            "temperature_unit": "degC",
        })

    evidence_card = {
        "evidence_card_id": f"card-{scenario_id}-{plan_id}-rev{scenario_revision}",
        "input_ref": input_ref,
        "planning_result_id": planning_result_id,
        "replay_id": replay_id,
        "forecast_id": forecast_id,
        "plan_status": plan_status,
        "decision_state": decision_state,
        "currency": "current",
        "preserved_commitment_ids": preserved_commitment_ids or ["cut", "occupation"],
        "changes": changes or [],
        "assumptions": assumptions or [
            "Land preparation requires 7 full days after crop release.",
            "Historical NASA POWER daily records (2001-2025 LST) represent past atmospheric demand.",
        ],
        "outstanding_checks": outstanding_checks or [
            "Soil suitability and salinity level for farmer field are unmeasured.",
            "Irrigation delivery schedules and canal reliability are unverified.",
            "Crop-specific Kc coefficients and stages for ETc calculation are unavailable.",
        ],
        "source_refs": [
            {
                "source_id": "NASA_POWER_DAILY_V2.10.3",
                "locator": "sakha_31.10_30.95_LST",
            },
            {
                "source_id": "FAO_56",
                "locator": "Penman-Monteith reference ET0 equation with ASCE cloud floor",
            },
        ],
        "takeaway": {
            "template_id": "takeaway.climate_evidence.v1",
            "template_version": "1",
            "parameters": takeaway_params,
        },
        "climate_evidence": replay_summary,
        "scientific_guardrails": {
            "et0_is_reference_demand_only": True,
            "etc_status": "unavailable",
            "crop_stress_thresholds_invented": False,
            "feasibility_modified_by_climate": False,
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return evidence_card
