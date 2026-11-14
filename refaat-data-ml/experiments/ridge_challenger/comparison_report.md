# Ridge challenger: measured diagnostic validation

One approved configuration, 14 direct models, CPU. Training 2001-2018; diagnostic validation 2019-2021.
Config SHA256: `3978160d209fdfb4dc024d11a9efe1f81b52c19647d2b0d31d962f686ab8c1bc`.

## Overall measured comparison

| Model | Target | MAE | RMSE | Bias (prediction - actual) | Samples |
|---|---|---:|---:|---:|---:|
| seasonal_climatology | tmax_c (degC) | 2.534365189 | 3.305463183 | +0.155119052 | 252 |
| persistence | tmax_c (degC) | 3.790158563 | 5.093053293 | +0.687380976 | 252 |
| ridge | tmax_c (degC) | 2.584580602 | 3.407869052 | +0.405164345 | 252 |
| seasonal_climatology | et0_mm_day (mm/day) | 0.583124451 | 0.805214481 | -0.119814428 | 252 |
| persistence | et0_mm_day (mm/day) | 0.887812657 | 1.229853462 | -0.126923919 | 252 |
| ridge | et0_mm_day (mm/day) | 0.608462664 | 0.829951350 | -0.022085569 | 252 |

## Absolute and relative differences

Positive difference = baseline minus Ridge, so positive values favor Ridge. Bias is signed above; smaller absolute bias is better.

| Target | Baseline | Metric | Baseline - Ridge | Improvement % | Ridge result |
|---|---|---|---:|---:|---|
| tmax_c | seasonal_climatology | mae | -0.050215414 | -1.9814% | LOSS |
| tmax_c | seasonal_climatology | rmse | -0.102405869 | -3.0981% | LOSS |
| tmax_c | persistence | mae | +1.205577961 | +31.8081% | WIN |
| tmax_c | persistence | rmse | +1.685184241 | +33.0879% | WIN |
| et0_mm_day | seasonal_climatology | mae | -0.025338214 | -4.3452% | LOSS |
| et0_mm_day | seasonal_climatology | rmse | -0.024736868 | -3.0721% | LOSS |
| et0_mm_day | persistence | mae | +0.279349993 | +31.4650% | WIN |
| et0_mm_day | persistence | rmse | +0.399902113 | +32.5162% | WIN |

## Interpretation by target

- **tmax_c vs seasonal_climatology:** MAE LOSS, -1.9814% improvement; RMSE LOSS, -3.0981%. Lower MAE at 2/7 leads; lower RMSE at 0/7 leads. Absolute bias: Ridge 0.405164, baseline 0.155119.
- **tmax_c vs persistence:** MAE WIN, +31.8081% improvement; RMSE WIN, +33.0879%. Lower MAE at 7/7 leads; lower RMSE at 7/7 leads. Absolute bias: Ridge 0.405164, baseline 0.687381.
- **et0_mm_day vs seasonal_climatology:** MAE LOSS, -4.3452% improvement; RMSE LOSS, -3.0721%. Lower MAE at 0/7 leads; lower RMSE at 0/7 leads. Absolute bias: Ridge 0.022086, baseline 0.119814.
- **et0_mm_day vs persistence:** MAE WIN, +31.4650% improvement; RMSE WIN, +32.5162%. Lower MAE at 7/7 leads; lower RMSE at 7/7 leads. Absolute bias: Ridge 0.022086, baseline 0.126924.

## Per-lead comparison

Each row uses 36 identical issue/target pairs. Full MAE/RMSE/Bias/count for every model and lead are in per_lead_metrics.csv; absolute/percentage differences are in per_lead_comparisons.csv.

### tmax_c

| Lead | Clim MAE | Persist MAE | Ridge MAE | Clim RMSE | Persist RMSE | Ridge RMSE | Ridge Bias |
|---|---:|---:|---:|---:|---:|---:|---:|
| D+1 | 2.550139 | 3.688333 | 2.711890 | 3.328897 | 4.915140 | 3.425656 | +0.013360 |
| D+2 | 2.365417 | 3.734167 | 2.426211 | 3.184769 | 4.982576 | 3.276552 | +0.520559 |
| D+3 | 2.501528 | 3.597778 | 2.496136 | 3.379351 | 4.878326 | 3.453878 | +0.361895 |
| D+4 | 2.576528 | 3.452500 | 2.577941 | 3.312523 | 4.700529 | 3.403444 | +0.435165 |
| D+5 | 2.604167 | 3.841666 | 2.536369 | 3.371870 | 4.985031 | 3.507939 | +0.573104 |
| D+6 | 2.980417 | 4.220000 | 3.050619 | 3.629710 | 5.642382 | 3.723639 | +0.275169 |
| D+7 | 2.162361 | 3.996667 | 2.292898 | 2.884644 | 5.478105 | 3.023287 | +0.656898 |

### et0_mm_day

| Lead | Clim MAE | Persist MAE | Ridge MAE | Clim RMSE | Persist RMSE | Ridge RMSE | Ridge Bias |
|---|---:|---:|---:|---:|---:|---:|---:|
| D+1 | 0.577890 | 0.881389 | 0.613972 | 0.737453 | 1.132656 | 0.772382 | -0.052624 |
| D+2 | 0.585788 | 0.872690 | 0.608777 | 0.858579 | 1.255946 | 0.885596 | -0.130969 |
| D+3 | 0.590568 | 0.907749 | 0.627168 | 0.856629 | 1.263411 | 0.874371 | -0.064885 |
| D+4 | 0.518078 | 0.785518 | 0.521533 | 0.662997 | 1.057123 | 0.684203 | -0.012681 |
| D+5 | 0.594545 | 0.868208 | 0.603664 | 0.722759 | 1.155242 | 0.738128 | -0.018075 |
| D+6 | 0.588863 | 0.887313 | 0.617312 | 0.816209 | 1.226883 | 0.849583 | +0.043275 |
| D+7 | 0.626139 | 1.011821 | 0.666813 | 0.946383 | 1.474423 | 0.970360 | +0.081359 |

## Protocol and integrity

- Exactly the approved two target-date annual harmonics and last/7/30/60-day means for Tmax and ET0. Every history ends at D-7; target steps are 8-14 after the cutoff.
- Each of 14 StandardScaler + Ridge(alpha=1, solver=svd) pipelines was fitted once on 6,501 training examples. No validation fitting, hyperparameter search or post-evaluation adjustment.
- History/labels use the original float32 diagnostic convention, with float64 feature arithmetic and fitting. Targets remain in physical units. No clipping or invented prediction intervals.
- Identical 504 target/issue/variable keys for each model, 252 observations per target. Baselines were recomputed from source observations; original climatology predictions and metrics matched exactly.
- JSON model reload and repeat-inference maximum difference: 0. Original package files verified before and after evaluation: 105.
- Negative Ridge ET0 predictions retained without clipping: 0.
- Reproduction commands, configuration/approval details and automated test results are documented in README.md and test_results.json.

## Scientific limits

These are diagnostic validation results on previously inspected years, not an independent blind test. No claim of statistical significance or deployment readiness follows from overall or per-lead differences. Leads share forecast issues and overlapping histories; their scores are not seven independent replications.
The frozen NASA POWER snapshot is retrospective and can contain revisions. The assumed D-7 cutoff may not reproduce real-time publication availability; as-issued arrival/revision logs are absent. ET0 is derived grass-reference evaporative demand from one gridded point, not measured field water use.
A linear model with one annual harmonic pair and fixed history summaries has limited nonlinear/extreme-event capacity. The 60-day contexts and training labels overlap. There is no station truth validation, geographic generalization test, interval calibration or operational monitoring.
No 2022-2026 values were used for model fitting or selection. No retraining on 2019-2021 was performed. Preserve this result even if it loses. Any future prospective test or revised model needs a separately authorized protocol; neither is executed here.
