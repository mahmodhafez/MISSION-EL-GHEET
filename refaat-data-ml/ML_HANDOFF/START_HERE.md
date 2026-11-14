# Start here • ML Engineer
**Mahmoud: P0 preserves this entire climate/ML release.** The datasets, splits, windows, float32 diagnostic protocol and three reference output files are unchanged. The Agricultural KB added to the full repository is an independent research/approval interface and supplies no training transformations. This task runs only the existing climatology diagnostic, with no model training or new experiments. A Python virtual environment is optional; the runtime and tests use only Python 3.11+ standard library.
**First experiment: reproduce the Sakha Seasonal Climatology baseline.** You need only this ZIP and Python 3.11 or later. Extract it into a writable folder and open a terminal there. No package installation, API credentials, GPU or downloads. If reading this inside the complete project, run the same commands from the project root; the shipped reference tables there are under `ML_HANDOFF/reference/`.

```console
python verify_package.py
python -m climate_data.ml_example --data data
python -m climate_data.evaluation --data data --output my_baseline
python -m unittest discover -s tests -p test_ml.py -v
```

Choose a new output directory on every run; existing results are protected. The example prints 6,574 training days, 1,096 validation days, 36 origins and 504 scored predictions. For the first issue, **2019-01-15**, the 60 known days are **2018-11-10 to 2019-01-08**; the seven scored dates are **2019-01-16 to 2019-01-22**. Compare your outputs with `reference/calendar_reference.csv`, `reference/scored_predictions.csv` and `reference/metrics.json`.

## Which files to use

| File | Contents | Use |
|---|---|---|
| `data/fit_targets.csv` | 2001-01-01 to 2018-12-31 inclusive; 6,574 complete dates | Fit models, transformations, and the calendar reference here only. |
| `data/diagnostic_validation_targets.csv` | 2019-01-01 to 2021-12-31 inclusive; 1,096 complete dates | Score predictions from the 36 prescribed origins; earlier available days may form later contexts. |
| `data/forecast_windows.csv` | Exact 36 diagnostic rows from the original audit's `evidence/forecast_windows.csv`, preserving issue and cutoffs | Use the manifest directly; other original windows are excluded from this export. |
| `data/quality_flags.csv` | 9,435 day-level review records; includes the reserve and recent period | Interpret QC by date; flags and diagnostic fields can depend on observed same-day weather. Do not supply future flags as model features. |
| `data/release.json`, `data/source_manifest.json` | Immutable version, point identity, methods, hashes and product metadata | Shared release metadata. The package manifest identifies the actual files present in this handoff. |
| `SHARED_DATA_DICTIONARY.md` | Every weather, ET₀, QC and input-window column with unit and role | The target CSVs contain only ISO date and two finite numeric targets: `tmax_c` (°C), `et0_mm_day` (mm/day). Site metadata is recorded once. |
| `reference/`, `tests/fixtures/diagnostic_baseline.json` | Freshly calculated reference/results; separate benchmark copied from an archived Chronos run | The evaluator never reads the benchmark. Tests compare its outputs with independently stored numbers. |
| `provenance/CHRONOS_HISTORY.md` | Original archive/member locations, accepted runs, failed initial run, model revision | Research history, not inputs to fit. |

Complete historical weather features, including records from after 2021, are optional research data in the **full project** at `data/sakha_daily.csv`. They are deliberately outside the model-ready handoff. The targets already contain the audited primary ET₀; no joins, cleaning, imputation, unit conversion or label engineering are needed.

## Load, predict, then score

```python
from pathlib import Path
from climate_data.climatology import SeasonalClimatology
from climate_data.evaluation import load_diagnostic_data, seasonal_predictions, score_predictions

root = Path("data")
ds = load_diagnostic_data(root)  # verifies hashes, dates, split boundaries, schemas and windows
w, history = next(ds.contexts())
print(len(ds.training), len(ds.validation), w.issue, history[-1].day)
print([(r.day, r.tmax_c, r.et0_mm_day) for r in history[-2:]])
print(list(w.targets()))

reference = SeasonalClimatology.from_csv(root / "fit_targets.csv")
rows, scores = score_predictions(ds, seasonal_predictions(reference, ds.windows))
print(scores["et0_mm_day"]["mae"])
```

For a new model, fit on `ds.training`. Predict only from the `(window, history)` pairs and known future calendar dates. Keep `ds.validation` in the evaluator. For each target and each of the seven scored dates, supply a dictionary with `issue`, `target_date` (ISO strings), `variable` (either target name) and finite `q50`. For intervals add `q10` and `q90` on every row, with q10 ≤ q50 ≤ q90. Pass the iterable to `score_predictions(ds, forecasts)`. It requires exactly one prediction per key, recomputes truth from the archive, and checks any supplied cutoff/lead fields. Use a distinct directory and version for new models. Files listed by `PACKAGE_MANIFEST.json` are immutable delivered evidence.

## What the comparison measures

- D is the issue date, the 15th of each month. The common cutoff **D−7** applies to both channels and represents a seven-day publication buffer in the original protocol. These are later-retrieved, potentially revised observations; issue-time arrival/revision logs are unavailable. The cutoff simulates availability, not a NASA guarantee. No forward fills or random row splits.
- Predict 14 daily steps starting at cutoff+1. Only steps **8–14**, i.e. **D+1…D+7**, count in the established comparison. These settings enable comparison to earlier work; document any other evaluation as a new protocol. The calendar baseline uses only the target month/day; it does not need the 60 observations.
- Each calendar date has its own bin on a circular **366-day** reference. Pool actual training observations in the central bin and its 15 neighbors on each side. December wraps to January. February 29 has its own bin and receives only actual leap-year observations there; March 1 remains aligned in every year. The February 29 window has 544 observations. Use linear empirical P10/P50/P90 (rank (n−1)p). The historical ML comparison rounds fit inputs and scored truth to float32 using the archived experiment convention; the canonical data retain their original precision. The app's 2001–2025 descriptive reference is a separate method and would leak validation into this comparison.
- Fit all scalers, feature choices, data-derived thresholds and reference tables using only allowed development data. Never use target-date realized weather, realized ET₀ inputs, target QC, or revised/future forecasts as available features. A future data source needs issue-time records. 2022–2025 is an **inspected reserve**; July–October 2026 is a **consumed test**. No 2026 observations are used to choose, fit, or score this baseline. A new blind-performance claim needs a new prospective period with frozen rules.

| Diagnostic metric | Tmax | ET₀ |
|---|---:|---:|
| MAE | 2.534365 °C | 0.583124 mm/day |
| RMSE | 3.305463 °C | 0.805214 mm/day |
| Empirical P10–P90 coverage | 79.37% | 81.75% |

Each target gets 252 equally weighted errors (36 × 7). MAE = mean absolute point error; RMSE = square root of mean squared point error; bias = mean(prediction − truth). Per-lead MAE gives seven scores, 36 observations each. Interval coverage is the fraction of truths in the inclusive P10–P90 band; width is mean P90−P10. Mean pinball loss averages the asymmetric quantile loss over the three probabilities and dates. These are diagnostic sample estimates, not a guarantee on future years.

## Output dictionary

| File | Columns / types / units |
|---|---|
| `calendar_reference.csv` | `month_day`: MM-DD text; `support_days`: observed integer count; `reference_start,reference_end`: inclusive ISO dates; `method`: string version; `tmax_c_q10/q50/q90` and `et0_mm_day_q10/q50/q90`: six floats in the target's unit, e.g. `et0_mm_day_q50`. 366 rows. |
| `scored_predictions.csv` | `issue,cutoff,target_date`: ISO dates; `variable`: one of the two targets; `lead_from_issue`: integer 1–7; `step_from_cutoff`: integer 8–14; `truth,q10,q50,q90`: floats in the selected target's unit. 504 rows. |
| `metrics.json` | Site/version, method, inclusive fit dates, split, row/origin counts, three SHA256 input hashes, and `metrics` keyed by target. Error, width and pinball values have the target's unit; coverage is a fraction. |

ET₀ is grass-reference evaporative demand derived from gridded POWER weather. It is not a field measurement, an irrigation instruction, or actual crop water use.

