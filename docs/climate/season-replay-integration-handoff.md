# Season Replay integration handoff (for Yahya)

**Read this if…** you're connecting the climate evidence to `POST /api/v1/scenarios/{sid}/replay` or the evidence card.

Status: Proposed (not a published contract) · Owner: Mahmoud (climate), reviewed by Amr · Last reviewed 2026-11-14 · Branch `climate/season-replay-hardening`.

---

## What you get

Two layers for one or more farmer sowing dates, with equal-length windows:

- **Layer A:** what actually happened in past NASA POWER data (2001–2025).
- **Layer B:** typical conditions from Refaat's evaluated climatology (2001–2018).

Plus bilingual summary sentences. It **never** changes plan statuses; it echoes the ones you pass in.
Standard library only, CPU only, no network.

## Python interface (`backend.app.replay`)

```python
from backend.app.replay import compare_sowing_windows, get_climate_store, ClimateInputError, ClimateDataError

store = get_climate_store()          # loads once per process (~0.2 s); cached
result = compare_sowing_windows(
    ["2027-05-28", "2027-06-01"],    # 1-4 YYYY-MM-DD sow dates; first is the reference
    window_days=14,                  # 1..120, same for every window
    years=None,                      # default 2001..2025 (2026 'recent' snapshot is quarantined)
    planner_statuses={"2027-05-28": "needs_review", "2027-06-01": "needs_review"},  # from the Promise Test
)
```

Other calls: `get_climatology_profile(date, reference="ml_fit_2001_2018")`, `evaluate_season_replay(plans, ...)`
(only for plans with **explicit** sow and crop-end dates), `run_uncle_hussein_comparison(planner_statuses)` and
`create_evidence_card(...)`.

## Output (key fields)

| Field | Meaning |
|---|---|
| `status` | `complete` / `partial` / `unavailable` (years usable for all windows) |
| `label.en` / `label.ar` | "Historical 14-day planting-window comparison - not a full crop-season analysis." **Show it.** |
| `windows[]` | `window_id` (W1…), `sow_date`, `planned_window` [first, last], `planner_status` (echoed, else `not_supplied`) |
| `layer_a_historical.years_used` / `years_excluded[{year, reasons[{window_id, reason}]}]` | Coverage. Reasons: `date_not_in_year`, `window_outside_dataset`, `window_enters_quarantined_recent_snapshot` |
| `layer_a_historical.windows[W].per_year[]` | `year, start, end, days, tmax_mean_c, tmax_max_c, et0_mean_mm_day, et0_total_mm, snapshots, qc_review_days` (chart data) |
| `layer_a_historical.windows[W].across_years[metric]` | `n, mean, sd_sample, min, q10, median, q90, max` |
| `layer_a_historical.paired_differences[W][metric]` | W minus W1 per year: same summary plus `years_b_higher/lower/equal` |
| `layer_b_climatology.windows[W].summary` | `tmax_q10/q50/q90_mean_c`, `et0_q10/q50/q90_mean_mm_day`, `et0_q50_sum_mm`; `.daily[]` per date |
| `layer_b_climatology.evaluation` | Method ID and cited MAE (2019–2021 validation; archived 2026 holdout) |
| `farmer_summary[]` | `{kind, en, ar}`; kinds `historical_comparison`, `historical_et0`, `typical_conditions`, `caution` |
| `units`, `metric_definitions`, `provenance`, `limitations`, `feasibility.climate_changes_planner_status` (always false) |

All numbers are finite (`json.dumps(..., allow_nan=False)` is safe). A typical payload is about 29 KB.

## Patch for your existing stub (`backend/app/api/v1.py` on `backend/milestone-1`)

Not applied; your file, your call.

```python
from ..replay import compare_sowing_windows, ClimateInputError, ClimateDataError  # adjust to final package path

@router.post("/scenarios/{sid}/replay")
def replay(sid: str, req: Request, body: ReplayBody):          # ReplayBody: sow_dates: list[str], window_days: int = 14
    _scenario_or_404(req, sid)
    statuses = ...  # from the stored Promise Test result of this scenario revision, keyed by sowing date
    try:
        r = compare_sowing_windows(body.sow_dates, window_days=body.window_days, planner_statuses=statuses)
    except ClimateInputError as e:
        raise ApiError(422, "invalid_replay_request", str(e))
    except ClimateDataError:
        return {"status": "unavailable", "reason": "climate_release_missing"}
    r["status"] = {"complete": "available"}.get(r["status"], r["status"])  # contract vocabulary
    return r
```

- **Error mapping.** Bad input → `ClimateInputError` → 422 in your error envelope. Release missing or corrupt →
  `ClimateDataError` → keep the honest `unavailable` status. Never return fake numbers.
- **Status vocabulary.** `ReplayResult` uses `available|partial|unavailable`, so map `complete` → `available`.

## Data dependency (required in deployment)

The release `sakha-power-lst-20261110-et0-v1` (7 files, about 2.5 MB) lives in Refaat's `refaat-data-ml/data/`
(branches `feature/refaat-data-ml` / `data/refaat-data-ml-recovery`). The loader verifies SHA-256 and never
downloads. Resolution order:

1. the `data_dir` argument
2. `MEG_CLIMATE_DATA_DIR`
3. `<repo>/data/local/sakha`
4. `<repo>/refaat-data-ml/data`

A wrong explicit path raises `ClimateDataError`. For Vercel, bundle that directory with the function (read-only is
fine) and set `MEG_CLIMATE_DATA_DIR`. No database or network access is required. This is **not tested on Vercel**.

## UI pieces (suggested)

- **Evidence card:** `label` + `farmer_summary` (Arabic by default) + `planner_status` badge (`needs_review` stays visible).
- **Chart:** `per_year[].tmax_mean_c` for W1 vs W2 by year, plus the Layer B q10–q90 band as a shaded range.
- **Expandable details:** `provenance`, `metric_definitions`, `limitations`, `layer_b_climatology.evaluation`.
- **Wording:** Never show "better date", "saves water" or "safe". ET0 is atmospheric demand, not irrigation.

## Smoke test

```powershell
$env:MEG_CLIMATE_DATA_DIR = "<path>\refaat-data-ml\data"
python -m backend.app.replay.cli compare-uh --text
python -m backend.app.replay.cli windows --dates 2027-05-28,2027-06-01 --text
python -m backend.app.replay.cli climatology --date 2027-05-28
python -m pytest backend/tests -q -p no:cacheprovider
```

`compare-uh` runs the real Promise Test from `packages/meg-core` for the statuses. Expect 25 years, both windows
`needs_review`, and the original plan `rejected`.

## Integration order

1. Merge `planner/twelve-crop-catalogue` (or the planner you deploy).
2. Merge this branch (it is based on `chore/app-integration` + Mahmoud's `2a4e4bc`).
3. Ship the release directory.
4. Apply the route patch on your backend branch.
5. Show the card and chart in the UI.
