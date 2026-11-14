# Season Replay and climatology: final audit

**Read this if…** you need to know whether Mahmoud's Season Replay is correct and what was changed before integration.

Status: Review report, frozen once merged · Reviewed 2026-11-14 · Base `backend/season-replay` @ `2a4e4bc` (Mahmoud Hafez) · Fix branch `climate/season-replay-hardening`.

---

## Verdict

**CONDITIONAL PASS.** The data, calculations and climatology are correct and verified on real NASA data. Three
conditions remain before this is user-facing:

1. Yahya wires the adapter (no FastAPI route is connected yet).
2. The deployment ships the 2.5 MB release directory (not in this branch; see [handoff](../climate/season-replay-integration-handoff.md)).
3. Refaat's `legacy_delivery` provenance blocker (planner/data side) is unaffected and still open.

## What Mahmoud built (base `2a4e4bc`)

`backend/app/replay/`, 15 files, 22 tests. It reuses Refaat's science carefully:

- **`dataset.ClimateStore`:** a port of Refaat's `climate_data/backend.py`. It checks the release hash, rejects
  duplicate and non-finite rows, and validates QC flags.
- **`climatology.py`:** Refaat's seasonal climatology. Verified **identical to Refaat's module on all 366 calendar
  slots** with `fit_targets.csv`.
- **`replay.HistoricalSeasonReplay`:** paired calendar-block replay (port of Refaat's `replay.compare`).
- **CLI, service facade, evidence card, UH-001 module.**

Strengths: release integrity checks, honest ETc suppression, explicit exclusions (Feb 29), paired blocks, and
guardrail text saying ET0 is not irrigation.

## Data verification (real release)

| Check | Result |
|---|---|
| Source | NASA POWER Daily API v2.10.3, community AG, LST, point 31.10 N / 30.95 E, grid elevation 4.96 m. Receipts carry NASA URLs and SHA-256. |
| Coverage | 9,435 days, 2001-01-01 to 2026-10-31, no duplicates. Snapshot `historical` 2001–2025 (9,131 days); `recent` 2026 Jan–Oct (304 days, partition `2026_quarantine`). |
| Variables and units | `tmax_c` degC (`T2M_MAX`); `et0_mm_day` mm/day. ET0 is **derived** by Refaat's pipeline, method `fao56-dewpoint-asce-floor-v1` (FAO-56 Penman-Monteith from POWER inputs). |
| Missing values | The fill value −999 and non-finite values are rejected at load. Hard-invalid QC days are absent. |
| Leap days | Real Feb 29 rows exist. Climatology uses a 366-slot leap calendar. |

## Defects found and fixed

| # | Severity | Defect (root cause) | Fix | Test |
|---|---|---|---|---|
| D1 | **P0 science** | `uncle_hussein.py` **invented agronomic dates**: maize crop ends 2027-10-04 / 10-08 ("129 days"), berseem sowing 2026-11-01, wheat and sorghum windows. The planner deliberately leaves changed endpoints unknown. | Module rewritten. It uses only the documented inputs (20 May cut, 15/28 May, 1 Jun) and a labelled **14-day planting-window comparison**. No crop end is created. | `test_uncle_hussein.py::test_no_crop_end_or_harvest_date_is_invented` |
| D2 | **P0 science** | Agricultural verdicts were **hardcoded strings**, not taken from the Promise Test. | Statuses are passed in and echoed. The demo CLI runs the real planner on `packages/meg-core/tools/fixtures/uh001.json`. | `test_promise_test_statuses_come_from_the_real_planner` |
| D3 | **P0 deploy** | `resolve_data_directory` ran `git show` and **wrote 7 files into the repo** at import time. It swallowed all errors, and a wrong explicit path silently fell back to another dataset. Fails on read-only/serverless hosts and machines without that branch. | Read-only resolution: argument → `MEG_CLIMATE_DATA_DIR` → repo-relative defaults. A wrong explicit path raises `ClimateDataError`. No subprocess. | `test_loader_is_read_only_and_never_runs_git` |
| D4 | **P0 integration** | No Layer B: the climatology existed but was never combined with replay, and the default reference was the **unevaluated** `historical_2001_2025` descriptive table. | New `windows.compare_planting_windows`: Layer A historical + Layer B from Refaat's **evaluated 2001–2018 baseline**, with method ID and cited evaluation. Service default switched to `ml_fit_2001_2018`. | `test_layer_b_matches_independent_quantile_from_training_file`, `test_cli_climatology_default_is_evaluated_baseline` |
| D5 | P1 | The evidence card defaulted any scenario to UH-001's `["cut","occupation"]`, a "7 days preparation" assumption and UH-001 field gaps. | Defaults removed; the caller supplies scenario content. | `test_evidence_card_with_replay_summary` |
| D6 | P1 | The CLI crashed printing Arabic on Windows (cp1252 console). | stdout reconfigured to UTF-8. | `test_cli_windows_text_is_bilingual` |
| D7 | P2 | Heat-threshold prose hardcoded "39.48 degC". It was correct (computed 39.48), but could drift from the data. | Formatted from the computed threshold. | covered by replay tests |
| D8 | P2 | Provenance cited the quarantined 2026 receipt even when it wasn't used. | Only snapshots actually used are cited. | `test_uh001_windows_match_independent_csv_arithmetic` |

Kept unchanged (verified sound): `ClimateStore` integrity checks, `SeasonalClimatology`, the generic `compare_plans`
engine (it requires caller-supplied explicit endpoints and blocks when they are missing), and `test_replay.py` /
`test_climatology.py`.

## Methodology challenge (answers)

1. **Calendar matching.** It describes *past exposure* at those dates, not future weather. Layer A uses the same
   years for every window; a year is dropped for all windows if any one is incomplete (no silent unequal samples).
2. **Equal duration.** Enforced: every window has `window_days` days, start inclusive. Feb 29 starts exclude non-leap
   years explicitly (`date_not_in_year`). Dec→Jan windows keep their relative offset.
3. **Coverage.** `years_requested`, `years_used` and `years_excluded` with reasons. 2026 is excluded by default
   (`window_enters_quarantined_recent_snapshot`).
4. **Sensitivity to unusual years.** Per-year values, min/q10/median/q90/max and sample SD (n−1) are all exposed.
5. **Meaningful difference.** The paired difference is reported with its spread and the count of years each way.
   For UH-001 the Tmax difference (+0.30 degC) is below the paired SD (0.93) and goes the same way in only 14/25
   years. The farmer text states numbers and year-to-year variation, never "significant".
6. **Certainty.** Layer B gives a q10–q90 range and is labelled "not a forecast". Layers A and B share the same
   NASA record, so they are stated as **not independent**.
7–10. Definitions are in `METRIC_DEFINITIONS` (mean Tmax vs single-day max; mean ET0 vs total ET0 = mean × days).
   Observed history (Layer A) and climatology (Layer B) are separate blocks with separate methods. All numbers are
   reproducible from the CSV (independent script in the [test report](season-replay-test-report.md)).

## ML and climatology verification

- **Baseline in use:** `seasonal_climatology/train_2001_2018/linear_quantiles_pm15_f32/v1`, built from
  `fit_targets.csv` (2001–2018, 6,574 rows). Identical to Refaat's module on 366/366 slots.
- **Cited evaluation (verified against Refaat's artifacts, not recomputed).**
  - **Diagnostic validation 2019–2021** (`ML_HANDOFF/reference/metrics.json`): Tmax MAE **2.534** degC, ET0 MAE
    **0.583** mm/day, 252 scored days, 80% interval coverage 0.79 / 0.82. Ridge on the same split: 2.585 / 0.608
    (worse).
  - **Archived consumed holdout, Jul–Oct 2026** (`archive-snapshot/.../holdout_results.json`): climatology
    **1.656 / 0.523** vs Chronos-2 LoRA 1.988 / 0.640.
  - The "1.656 / 0.523" figures in the brief are real but come from this **different, consumed** evaluation. Both
    are cited with their splits.
- **Leakage.** The baseline is fitted on 2001–2018 only. Layer A covers 2001–2025, so for 2001–2018 the two layers
  share data. This is disclosed, not an evaluation. No retraining or tuning was done.

## Remaining risks

- The data release isn't in this branch. Production needs the directory deployed or set via `MEG_CLIMATE_DATA_DIR`.
- Gridded regional data, not station truth. ET0 is grass reference, not crop water use. No crop-stage or heat-damage
  thresholds exist.
- The `compare_plans` 4-season engine needs real planner endpoints, which UH-001 does not have (unknown). It stays
  `blocked` until they exist.
- The API contract status vocabulary (`available`) differs from the module (`complete`). The handoff gives the mapping.
- Python 3.12 runtime is untested (3.13.14 locally); grammar is checked against 3.12.
