# Canonical data and evaluation protocol

**Read this if…** you're loading the shared data release or evaluating a forecast.

Status: Current,  · Owner: Refaat. Last reviewed .

Protocol `meg-daily7-ridge-v1`; assembled release `meg-shared--v1`; Refaat dataset `sakha-power-lst--et0-v1`. One source lineage; these IDs describe assembly versus original dataset, not alternative weather. Full file hashes live in the generated `data/local/shared--v1/manifest.json`; copy that file with every delivery. The containing application `data_release` binds this manifest plus approved KB/rule/calculation versions and remains Yahya's single HTTP version token.

## Available files and preparation

| File relative to assembled release | Coverage / purpose | SHA256 |
|---|---|---|
| `refaat/data/fit_targets.csv` | –;6,574 rows; fit only | `24a26ba5b0d44d35147397fbed5309fe925a63034cfc4a4b74a90d5dfca130c2` |
| `refaat/data/diagnostic_validation_targets.csv` | –;1,096 rows; diagnostic scoring | `362181c33fde7201b3159d294dc494eaa897adeac8d69d21739416da18647bfc` |
| `refaat/data/forecast_windows.csv` | 36 fixed monthly diagnostic origins | `8fc0c0aa99f57ee47910c3cf3bd49eeb6b4f9cccf692aa9a821d8e9e73311a44` |
| `weather/weather_et0.csv` | 2001–2025;9,131 rows; historical evaluation, unchanged bytes | `17141df82f6300c051257c21fb9ac3d9f5f1627fd32cbc8c07bc9296c477bde8` |
| `weather/weather_et0_2026_Jan_Oct.csv` | Jan–Oct2026;304 rows; quarantine, not new test | `c4d5929fd0d4d55c416ee45d5ebd21502142994afbc76b00c6f20e1b349ee36e` |
| `refaat/data/quality_flags.csv` | 9,435 dated QC rows; review metadata only | `db650082761b27205a0ef8ebae852a28984f5bd296a7b1a8c7d1cb39de0567a6` |
| `refaat/data/{release,source_manifest}.json` | Source requests, product lists, units, original hashes, split boundaries | Outer manifest binds exact bytes |
| `refaat/climate_data/` and reference/tests | Unmodified supplied implementation and expected outputs | Outer/package manifests |

Raw source is [NASA POWER daily point API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/); exact requests already in `data/validation/power_acquisition.json`. Latitude31.10N, longitude30.95E, returned elevation4.96m. Meteorological and solar native-cell IDs are **unknown**, not inferred from coordinate rounding. One site only; no spatial independence claim. LST day labels are retained; no UTC/Cairo-DST conversion. Issuance timestamps use UTC separately. Actual issue-time publication vintages do not exist; comparisons are retrospective with simulated lag.

Targets exactly `date,tmax_c,et0_mm_day`, units `degC`, `mm/day`. Full weather also has Tmin/dewpoint °C, RH%, 2m wind m/s, solar MJ/m²/day, pressure kPa, rain mm/day and two ET0 sensitivity columns. No radiation/pressure reconversion, wind-height conversion or ET0 recalculation. Frozen ET0 is FAO56 dewpoint with ASCE cloud-ratio floor; not irrigation use. Source release fills are -999; reject missing/nonfinite/duplicate/reversed dates or wrong units. New missing data get explicit unavailability, never forward fill or future interpolation. Do not feed future QC flags or sensitivity columns as independent targets.

Build command (exists now; refuses existing destination; no external packages):

```powershell
python ml/tools/prepare_shared_release.py --refaat "C:/Users/Amr Hany/Downloads/ML_HANDOFF.zip" --science docs/VALIDATION_ARTIFACTS.zip --output data/local/shared--v1
python -m unittest discover -s ml/tests -v
```

The current workspace already has that release. Other machines receive either the small assembled directory (with manifest), or the archives through approved team file sharing and run the command. Do not put the 469MB archive/weights in Git. Builder verifies both archive hashes, 27 Refaat file hashes, frozen CSV hashes and cross-source target identity before atomic publication. It does not execute archive code, regenerate scientific bytes, or overwrite outputs. Safe no-overwrite reruns use a new path but retain the release ID only for identical contents.

## One forecast protocol

Use **daily** D+1…D+7 Tmax and ET0, not weekly means. Context is 60 complete days D−66…D−7. D is the issue's LST calendar date; synthetic issuance metadata can use 00:00Z as an explicitly simulated timestamp, never a historical availability claim. Models forecast 14 cutoff-relative steps if recursive/pretrained, score only steps8…14. Direct Ridge maps the context straight to the seven issue-relative labels. Known future covariates: target month/day harmonics only.

Retain Refaat baseline exactly: 366 calendar slots (Feb29 separate; March1 fixed), circular ±15 slots, empirical linear q10/q50/q90, fixed 2001–2018 fitting, float32 conversion at experiment inputs/truth. q50 is **median**, not mean. Full-year float64 historical summaries are distinct methods and cannot contaminate ML scoring. Forecast empirical intervals are not calibrated farmer confidence guarantees.

Persistence repeats the final available value at cutoff for each target date, using identical float32 scoring. Preserve every expected key: 36 issues × 7 days ×2 targets =504 predictions. `score_predictions` recomputes truth and rejects duplicate/missing/unexpected keys, bad cutoffs/leads, nonfinite or crossed quantiles. Do not hand it only favorable dates.

## Minimal Ridge experiment — exact specification

Fourteen independent direct **raw-target** regressions (2 variables ×7 lead days). No residual-baseline fit or recursive weather features. This deliberately simplifies the earlier weekly proposal and avoids hidden climatology fitting on training labels.

Feature order is fixed and written to `feature_schema.json`:

1. For each variable in `[tmax_c,et0_mm_day]`, lags `[0,1,2,3,6,13,27,55]` relative to cutoff.
2. For each variable, trailing mean and population SD over `[7,14,28,56]` days ending cutoff, followed by mean(last7) minus mean(previous7).
3. Target-date `sin(2πk phase/366),cos(2πk phase/366)` for k=1,2, using Refaat's leap-calendar phase.

There are 38 numeric features per model. Exclude any context with a missing required observation; no imputation or observed future weather. All transforms are fitted on that model's training rows. Use `Pipeline(StandardScaler(), Ridge(alpha=...,solver="svd"))`; alpha grid **[1,10,100]**, no extra search. Single shared alpha selected by mean validation MAE skill normalized by the calendar comparator across 14 target/lead cells. Store separate raw MAE/RMSE/bias; the selector is not a crop suitability score. Fit on float32-converted observations cast to float64 for stable linear algebra; score truth using Refaat's original convention.

Inner tuning: fit origins every Monday whose entire 60-day history and label interval are in 2001–2015; train labels end by . Validate on the 15th of each month in 2016–2018, only when training labels are <= that issue's cutoff. Build an **inner-only** climatology from 2001–2015 via the generic records route; label it inner diagnostic, not the immutable research baseline. Do not call fixed-2001–2018 `from_csv` as the inner comparator. No 2019–2021 outcomes select hyperparameters.

After alpha selection, refit on Monday origins with labels entirely in 2001–2018. Assert every fit label date <= and <=first diagnostic cutoff. Score the exact supplied 36 2019–2021 origins once. They are existing **diagnostic** dates, not a new untouched test. 2022–2025 is an inspected reserve; no testing/tuning there today. Jan–Oct2026 is quarantined consumed evidence. No random split, shuffled overlapping-window split, foundation pretraining independence or fresh-test claim.

Store per training example: `issue,cutoff,context_start,target_start,target_end,variable,lead_day,split,source_sha256,feature_schema_version`. Store features/labels in separate `X.csv`/`y.csv` for each partition and model key, or a shared keyed table with identical fields. Label endpoints crossing a boundary are purged. A training manifest records actual retained/excluded origin counts; counts are computed, not guessed.

Metrics: MAE,RMSE,bias by variable/lead, and seasonal breakdown with sample counts. Compare Ridge, climatology and persistence on the same keys. Skill=1−MAE_model/MAE_baseline; zero denominator means undefined. For diagnostic paired uncertainty resample whole issue blocks (3 consecutive monthly origins,2,000 draws,seed), keeping both targets/all leads together. Do not treat correlated daily errors as independent. Point-only Ridge has **no q10/q90**; never invent zero-width confidence bands. No interval calibration work today.

P1 success: reproduce fit, show parameter coefficients differ from zero, no leakage, exact504 output keys, test/metrics report and honest win/loss. Optional research promotion gate: ≥5% lower aggregate MAE for **both** targets against strongest baseline, no lead/season MAE degradation >5%, paired95% improvement interval above zero. Sparse seasonal samples make results inconclusive, not a pass. This diagnostic gate alone does **not** authorize live farmer-facing Ridge: fresh prospective evidence, a relevant permitted decision and compatible uncertainty contract remain missing. The current API needs quantiles, so point-only Ridge stays research-only. Stop after3 alpha values; ≤10min fit/score compute, ≤90min total task.

Fresh evaluation after the hackathon: freeze protocol/model at T0, archive forecasts/input vintages before outcomes, start at next supported issue and collect enough seasons (prefer12months). A short interim result cannot establish annual skill.

## Shared artifact schemas

- Prediction CSV: `issue,cutoff,target_date,variable,lead_from_issue,step_from_cutoff,q50`; optional q10/q90 appear together on all rows. These are Refaat's exact scorer keys. `q50` is used as the point-estimate transport key for Ridge and marked `point_estimator=conditional_mean` in metadata; it is not an estimated median quantile. Do not score Ridge pinball as if it were probabilistic.
- `run.json`: run_id,protocol_id,release_id,source hashes,code hash,Python/package versions,hardware,seed,fit/tune periods,features,alpha,model keys,started/finished UTC,elapsed seconds,artifact hashes,limitations.
- `metrics.json`: target/lead/season keys,counts,raw metrics,paired baseline IDs and confidence procedure; no pooled °C/mm error.
- Ridge model: `ridge.npz` with numeric coefficient/intercept/scaler arrays and feature order in JSON; use `numpy.load(...,allow_pickle=False)`. No arbitrary pickle deserialization in backend.
- `forecast_bundle.json`: unchanged Yahya daily contract; produced only by the reviewed publisher/adapter with finite ordered quantiles and own-method skill. A model file or research prediction CSV is not that bundle.

## Agricultural and other missing evidence

The existing KB draft has11 sources,15 assertions,6 trial templates and15 proposed evidence rules. All retain pending source/rule review. Need exact source-page extraction/hashes/terms; target-year cultivar availability; crop-end/release/preparation; actual soil/drainage/salinity-method and irrigation facts; hard production-quantity support. Refaat delivers a validated draft plus gap register, not invented dates or successful recommendations. Preserve fixture/science distinction and Amr/Astra's ownership. No full SB-001 or `CLIMATE_AWARE_PLANNER.md` was supplied here. C3S/hindcasts/skill, multigrid cell identities and crop-response labels remain unavailable and deferred.
