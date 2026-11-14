# Sakha Ridge challenger: specification proposed for approval

**Status: PROPOSED_PENDING_USER_APPROVAL. No Ridge or scaler has been fitted.**

No approved/frozen Ridge configuration was found in the existing project. The existing protocol describes the chronological data, availability cutoff, climatology and historical model comparisons, but specifies no Ridge features or alpha. This directory contains **one proposed configuration**, an approval record and a baseline-only audit. Approval is required by the user's instruction before fitting. The original 105-file package, datasets, P0 runtime and historical outputs remain unchanged; the root package manifest was not refreshed.

Approve specification **`sakha-ridge-direct-calendar-history-v1`**, defined by [config.json](config.json), SHA256:

```text
3978160d209fdfb4dc024d11a9efe1f81b52c19647d2b0d31d962f686ab8c1bc
```

[approval.json](approval.json) records the pending state. The proposal is not represented as already approved or scientifically validated. After explicit approval, preserve the approved config bytes and record the approval separately. Train only that configuration. Changes to features, model settings or preprocessing require a new decision before fitting, never a silent change after seeing validation scores.

## Audited existing resources

- `../../data/fit_targets.csv`: 6,574 complete daily targets, 2001-01-01–2018-12-31.
- `../../data/diagnostic_validation_targets.csv`: 1,096 complete daily targets, 2019-01-01–2021-12-31.
- `../../data/forecast_windows.csv`: 36 monthly issues, the 15th of each month in 2019–2021, with exactly 252 scored dates per target.
- `../../climate_data/evaluation.py`: validated data loading, 60-day contexts, keyed predictions, float32 truth, MAE/RMSE/Bias and per-lead MAE.
- `../../climate_data/climatology.py`: the training-only calendar reference and float32/366-day phase helpers.
- `../../ML_HANDOFF/START_HERE.md`, `reference/metrics.json`, `reference/scored_predictions.csv`, `reference/calendar_reference.csv`, `../../tests/test_ml.py` and `../../provenance/experiment/evaluation_protocol.json`: existing protocol and reference definitions. The existing `archived_scores.csv` supplies a check of diagnostic persistence MAE; it never supplies predictions or Ridge inputs.

The immutable input hashes are recorded in config.json and checked against the actual files. Do not use `sakha_daily.csv`, quality flags or any 2022–2026 targets to build this model. The existing loader may use earlier validation observations in later validation contexts only once their dates are at or before the cutoff. This is rolling prediction with a fixed model, not a validation refit.

## One proposed design

For issue date **D**, use cutoff **C = D−7**. Require exactly 60 continuous historical dates **C−59…C**, equivalent to **D−66…D−7**, inclusive. For each issue lead **h = 1…7**, predict target date **T = D+h = C+(7+h)**. Thus the direct steps after the cutoff are **8…14**.

Use **14 separate direct pipelines**: one for each of two targets (`tmax_c`, `et0_mm_day`) and seven issue leads. These are components of one challenger, with identical fixed feature definitions and Ridge settings, not competing experiments. Each predicts its physical target value directly. There is no recursive feedback, numeric lead feature, target normalization, residual target, extra model, hyperparameter search or feature selection. The model index identifies h; the calendar inputs refer to the known target date T.

### Exact ten features, in order

Define `z_v(t) = float64(float32(observed v(t)))`, using the existing float32 helper for consistency with the diagnostic benchmark. Compute history statistics in float64 with `math.fsum` over chronological values. Define `p(T)` as the zero-based day index of the same month/day in leap year 2000: Jan 1 = 0, Feb 29 = 59, Mar 1 = 60, Dec 31 = 365. This follows the existing calendar phase convention even in non-leap years. No future weather is needed to know T.

| Feature name | Formula | Latest observation / availability |
|---|---|---|
| `target_annual_sin` | sin(2π p(T) / 366) | Deterministic calendar known at issue D |
| `target_annual_cos` | cos(2π p(T) / 366) | Deterministic calendar known at issue D |
| `tmax_last` | z_tmax(C) | C = D−7 |
| `tmax_mean_7` | Σ(i=0…6) z_tmax(C−i) / 7 | Inclusive C−6…C |
| `tmax_mean_30` | Σ(i=0…29) z_tmax(C−i) / 30 | Inclusive C−29…C |
| `tmax_mean_60` | Σ(i=0…59) z_tmax(C−i) / 60 | Inclusive C−59…C |
| `et0_last` | z_et0(C) | C = D−7 |
| `et0_mean_7` | Σ(i=0…6) z_et0(C−i) / 7 | Inclusive C−6…C |
| `et0_mean_30` | Σ(i=0…29) z_et0(C−i) / 30 | Inclusive C−29…C |
| `et0_mean_60` | Σ(i=0…59) z_et0(C−i) / 60 | Inclusive C−59…C |

The calendar pair represents annual seasonality without month discontinuities. The last available values represent recent conditions, while the fixed 7/30/60-day means smooth short, medium and full-context history. Both channels are eligible because both Tmax and derived ET0 are available under the same D−7 assumption. Correlated rolling means are intentional; Ridge penalizes coefficients. These choices are proposed for simplicity before any Ridge results, not selected by validation performance. They do not guarantee improvement over the stronger calendar-median baseline.

### Training examples and boundaries

Use every eligible **daily** simulated issue in the training period, in ascending order and with equal weight. All pipelines share the same issue set: require the full 60-day context and **all seven** target dates inside 2001–2018. Do not admit extra end-of-period samples only for shorter leads.

| Bound | First training example | Last training example |
|---|---|---|
| Issue D | 2001-03-08 | 2018-12-24 |
| Historical context | 2001-01-01…2001-03-01 | 2018-10-19…2018-12-17 |
| Cutoff C | 2001-03-01 | 2018-12-17 |
| Seven labels | 2001-03-09…2001-03-15 | 2018-12-25…2018-12-31 |

This yields **6,501 examples per target/lead pipeline**, a 6,501 × 10 feature matrix per lead. The target for model (v,h) is `z_v(D+h)`. Future targets are labels only; they never enter that example's features. All label dates end no later than 2018-12-31. The estimator and scaler are trained once on all authorized training examples before any validation forecast. No rolling refits or training on validation are proposed. Overlapping training windows are expected; their dependence is not evidence of independent sample size.

For the first diagnostic issue, 2019-01-15, the context is 2018-11-10…2019-01-08 and labels are 2019-01-16…2019-01-22. Reuse `DiagnosticData.contexts()` rather than constructing an unrestricted joined frame and taking risks with shifts. An eventual implementation should pass only the sliced history to feature construction; target truth belongs only in the scorer.

### Fixed estimator and preprocessing

Each target/lead uses `Pipeline(StandardScaler, Ridge)` with a dense float64 matrix. Fit the scaler **only on that pipeline's 6,501 training feature rows**. Use `StandardScaler(copy=True, with_mean=True, with_std=True)`, with training mean and population variance (`ddof=0`), and the library's constant-column handling (scale 1). Validation uses only `transform`. No scaler updates or validation-dependent statistics. [StandardScaler documentation](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)

Use `Ridge(alpha=1.0, fit_intercept=True, copy_X=True, solver="svd", tol=1e-4, max_iter=None, positive=False, random_state=None)`. The objective is the sum of squared residuals plus alpha times squared coefficient norm, with an unpenalized intercept. Alpha is fixed at 1.0 as an untuned starting choice. SVD is appropriate for this small, potentially correlated feature matrix and involves no random seed or sampling; tol does not control the SVD solution. No `RidgeCV` or other candidate fits. [Ridge documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html)

Historical inputs and training/scoring targets use the existing float32 quantization convention, then float64 arithmetic. Sin/cos features are computed directly in float64. Labels remain in °C and mm/day: **no target scaling and no inverse transform**. Do not round or clip predicted values before scoring. Retain/report any negative ET0 prediction as a model limitation; do not silently insert a postprocessing rule.

Missing-data policy: **fail the run** on missing, duplicate, unordered/noncontiguous, nonfinite or fill data, an incomplete 60-day context, or a missing label. No imputation, interpolation, partial rolling windows, dropping observations, removing extremes or using target-day QC. Validated source review flags do not change this experiment's data membership.

Use CPU and one BLAS thread via `threadpoolctl.threadpool_limits(limits=1)`. The available interpreter reports Python **3.14.6** and installed versions scikit-learn **1.9.0**, NumPy **2.4.6**, SciPy **1.18.0**, threadpoolctl **3.5.0**, joblib **1.5.3**. The installed estimator signatures were checked without fitting. Pin these versions for the approved run and record OS/interpreter/BLAS details. No packages were installed or upgraded in this proposal stage. Save scaler means/scales, coefficients/intercepts, feature order, complete configuration, input hashes and environment metadata. A repeat/reload check is for this exact configuration only, with absolute prediction tolerance 1e−10 in the same pinned environment; it is not another model-selection experiment.

## Fair evaluation after approval

All three methods must provide the same **504 keys** `(issue,target_date,variable)`: 36 issues × 7 leads × 2 targets. Use the existing `score_predictions` and its float32 ground truth. Its `q50` field is the generic point-prediction input; using it for Ridge does not assert a calibrated median or fabricate a quantile distribution. Emit no q10/q90 for Ridge or Persistence.

- **Seasonal Climatology:** unchanged training-only 2001–2018 circular 366-day ±15-slot empirical median, via the existing `SeasonalClimatology` and `seasonal_predictions`. Do not use the app descriptive 2001–2025 reference.
- **Persistence:** repeat the same target's last available float32 value at C = D−7 for all seven leads.
- **Ridge:** the corresponding fixed direct pipeline for target and h. No validation refits or corrections.

Use existing `distribution_scores` for MAE, RMSE and Bias = mean(prediction − truth), overall and separately at every lead. Use 252 samples per target overall and 36 at each lead. No changes to the shared evaluator are required; per-lead RMSE/Bias can be calculated on its returned scored rows. Strip the climatology interval columns only in the new point-comparison output, leaving archived outputs untouched.

Report each target separately: MAE is the primary comparison, with RMSE and absolute Bias reported separately. Positive improvement = baseline metric − Ridge metric for MAE/RMSE; percentage = 100 × improvement / baseline metric. Show every lead delta and counts of leads improved. Do not tune after seeing these results or claim statistical significance from seven lead summaries. Signed Bias remains signed in the results; proximity to zero, not a more negative value, indicates lower systematic bias.

## Baseline audit already executed, without Ridge

[audit_proposal.py](audit_proposal.py) reconstructs both baselines from the validated data, checks all climatology scored values and metrics against the existing reference, and checks persistence MAE against archived diagnostic results. It has no Ridge/scaler fit call and does not build Ridge training features. [audit.json](audit.json) contains measured metrics for all leads, identities and checks.

| Model | Target | MAE | RMSE | Bias | Samples |
|---|---|---:|---:|---:|---:|
| Seasonal Climatology | Tmax (°C) | 2.534365 | 3.305463 | +0.155119 | 252 |
| Persistence | Tmax (°C) | 3.790159 | 5.093053 | +0.687381 | 252 |
| Ridge | Tmax (°C) | NOT YET GENERATED | NOT YET GENERATED | NOT YET GENERATED | — |
| Seasonal Climatology | ET0 (mm/day) | 0.583124 | 0.805214 | −0.119814 | 252 |
| Persistence | ET0 (mm/day) | 0.887813 | 1.229853 | −0.126924 | 252 |
| Ridge | ET0 (mm/day) | NOT YET GENERATED | NOT YET GENERATED | NOT YET GENERATED | — |

Climatology predictions/metrics matched the preserved reference exactly. The two persistence MAEs reproduced the historical diagnostic values. These are **diagnostic validation** measurements, not independent test results. There is no Ridge improvement or lead-stability conclusion yet.

Executed checks:

```console
python -B verify_package.py
python -B -m unittest discover -s tests -p test_ml.py -v
python -B -m experiments.ridge_challenger.audit_proposal --output experiments/ridge_challenger/audit.json
```

All **105** existing package files verified unchanged; all **10** existing ML tests passed. The baseline audit passed. An initial audit-script run used the wrong archive column names (`model`/`variable` instead of `method`/`target`); that script-only mapping was corrected before writing audit.json. No source data or model outputs were changed. For a repeat audit, choose a fresh output filename inside this experiment directory; the command refuses overwriting.

## Implementation and tests deferred until approval

`features.py`, `train.py`, `evaluate.py`, trained parameter artifacts, `predictions.csv`, `metrics.csv`, `comparison_report.md`, and experiment-specific tests are **NOT YET GENERATED**. No placeholder CSVs or fabricated Ridge rows are supplied. The model outputs in config.json are a planned inventory, not existing results.

After approval, tests will cover:

1. Exact daily training issue/label/context bounds, 6,501 examples per model, and exclusion of any training target after 2018-12-31.
2. Feature names/order/formulas, leap calendar and rolling means from small hand-calculated fixtures; strict missing-data rejection.
3. D−7 history slicing and perturbation tests: changing any observation after C must not alter features/predictions for that issue. The predictor accepts only available history, never scoring labels.
4. Equal prediction keys/counts for all three methods and seven leads; scorer rejection of missing/duplicate keys.
5. Scaler means/variances from training rows only, constant-column behavior, unchanged scaler during validation, and absence of a target transform/inverse transform.
6. Metric arithmetic including signed Bias, overall/per-lead counts and consistency with the existing baselines.
7. Identical-configuration repeat/reload predictions, recorded versions/input hashes, and preservation of the original release/reference bytes.
8. No quantile or interval fabrication and no imports of Backend, agricultural KB or trained forecasting models.

All new code and outputs will stay under `experiments/ridge_challenger/`. Shared modules are imported read-only; no global dependency/manifest or historical result modifications are proposed. No fitting begins until the approval record can reference the user's explicit approval of the configuration above.

## Scientific limits and next step

This is one fixed linear challenger on one gridded Sakha point, against previously inspected diagnostic years. ET0 labels are derived reference demand, not station-measured crop water use. D−7 is the inherited retrospective availability assumption; as-issued publication/revision histories are unavailable. Training examples overlap, the seasonal relationship may be nonlinear, and fixed Ridge settings may fail to beat climatology. No station/generalization audit, future blind test, prediction-interval calibration or deployment monitoring is supplied. All of 2022–2026 remains outside this experiment, especially the consumed July–October 2026 test.

The immediate next step is approval or revision **before fitting**. After approval, execute the one configuration, report success or failure for both targets and all leads, and preserve the results. Any later prospective test or revised model would require a separate authorized protocol; validation improvement alone would not establish production readiness.
