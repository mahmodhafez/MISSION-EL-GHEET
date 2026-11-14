"""UH-001 (Uncle Hussein) climate demonstration: May 28 vs June 1 maize sowing windows.

Only the reference scenario's documented inputs are used: the protected 20 May 2027 cut, the
original 15 May sowing and the two investigated sowing dates. Changed maize endpoints are
unknown in the planner, so no harvest or crop-end date is created here; the comparison uses a
labelled equal-length calendar window instead. Planner statuses must come from the Promise
Test and are only echoed.
"""

from __future__ import annotations

from typing import Any

from .dataset import ClimateStore
from .windows import compare_planting_windows

UH001 = {
    "scenario_id": "UH-001",
    "protected_commitment": {"id": "cut", "kind": "harvest_or_cut_date", "date": "2027-05-20",
                             "description": "Last protected berseem cut"},
    "original_sow_date": "2027-05-15",
    "investigated_sow_dates": ["2027-05-28", "2027-06-01"],
    "source": "docs/product/reference-scenario.md",
}


def run_uh001_window_comparison(store: ClimateStore, *, planner_statuses: dict[str, str] | None = None,
                                window_days: int = 14, years: list[int] | None = None) -> dict[str, Any]:
    """Compare the two investigated sowing windows; the first (28 May) is the reference."""
    supplied = {k: v for k, v in (planner_statuses or {}).items() if k in UH001["investigated_sow_dates"]}
    result = compare_planting_windows(store, list(UH001["investigated_sow_dates"]), window_days=window_days,
                                      years=years, planner_statuses=supplied)
    result["scenario"] = {
        **UH001,
        "original_plan_status": (planner_statuses or {}).get(UH001["original_sow_date"], "not_supplied"),
        "statuses_source": "promise_test" if planner_statuses else "not_supplied",
        "unknown_endpoints": "Changed maize harvest, crop end and field release are unknown; none is assumed.",
    }
    return result
