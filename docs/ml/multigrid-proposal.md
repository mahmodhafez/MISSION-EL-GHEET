# Proposed multi-grid-cell ML experiment

**Read this if…** you're considering a multi-location ML experiment.

Status: Proposed, not approved,  · Owner: Amr. Last reviewed .

. **PROPOSED; NOT APPROVED OR EXECUTED.** No regional weather was downloaded, grid IDs established, model trained or performance measured for this proposal. It is separate from the completed single-point experiment in [ML_EXPERIMENT.md](ml-experiment.md). Approval must freeze the actual cells, release, splits, budget and decision thresholds before acquisition/training. It changes no planner rule, API or architecture.

## Question and scope

Does bounded adaptation on several genuinely distinct POWER source-cell groups improve future regional Tmax/derived ET0 forecasts over a single-cell adapter, unchanged Chronos-2 and simple baselines? Evaluate future Sakha performance separately from transfer to unseen groups. More coordinates, crops or nominal farms are not automatically more independent samples. No yield, ETc, irrigation-saving or four-season eligibility target is proposed.

Keep the same eight POWER variables, AG/LST convention and FAO56 ET0 with the ASCE daily cloudiness bound. Targets remain `tmax_c` and calculated `et0_mm_day`; training inputs initially remain only their histories. Additional predictors or model families would be a separate amendment.

## Cell selection and provenance before acquisition

Propose a cap of **12 distinct source-cell groups**, with Sakha in training: eight training, two spatial-validation and two spatial-test groups, subject to verified availability. These counts are an engineering proposal, not evidence that twelve independent or representative agricultural settings exist. Select from an explicitly approved Egyptian regional extent using location/coverage metadata before inspecting forecast errors; no coordinates or local soil classes are invented here.

NASA documents meteorology at 0.5° × 0.625° and solar at 1° × 1°, and warns that nearby requests may repeat information. Its daily API says parameters retain native source resolution. Use product-specific native-cell identities rather than rounding requested coordinates or assuming one common grid. [NASA download guidance](https://power.larc.nasa.gov/docs/tutorials/), [daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/).

Construct overlap groups: connect requests sharing a meteorological **or** solar source cell; place the whole connected component in one spatial partition. Check identities against source grid definitions and response metadata. Unknown cell identity blocks an independence claim; actual equal-series/hash checks are additional diagnostics, not proof of independent measurement. Distinct groups can still share regional weather events, so report spatial dependence and avoid counting each cell-day as independent replication.

Freeze a separate research manifest containing proposed/actual coordinates, returned geometry/elevation, per-product cell IDs with derivation/version, overlap-group ID, partition, years, requested variables/units/LST, exact request, retrieval timestamp/status, raw hash, response sources/API version, missingness and ET0 method/code hash. Preserve each response's actual sources; do not invent source transitions from a whole-response list. New downloads form a **new** dataset release; never substitute them under the existing single-point hashes. A preliminary cap is twelve point acquisitions per approved time block, eight variables per request; number of blocks, storage, retries and request pacing need approval. No acquisition is performed by this document.

## Time and geography separation

| Purpose | Proposed rule |
| --- | --- |
| Local adaptation | Fit only training groups, using 2001–2018 initially; no final-test labels in training, scaling or imputation. Reassess the old training-period choice explicitly before registration rather than silently extending it. |
| Development | Use 2019–2021 diagnostic origins for train groups and spatial-validation groups; any hyperparameter/calibration choices consume those observations. Unknown foundation-model pretraining overlap makes these diagnostics, not independent operational evidence. |
| Historical supplementary periods | 2022–2025 may diagnose failure modes only if declared before use. They are not automatically post-checkpoint or untouched final tests. |
| Consumed assessment | July–October 2026 Sakha assessment is already consumed. Do not select cells, tune models or claim a fresh test from it. Corresponding regional weather dates should also be treated as diagnostic because events and outcomes are correlated across cells. |
| Final future assessment | Register time T0 after protocol approval and after pinning checkpoint/adapter selection. Reserve a future target period beginning after T0, with all calibration complete before its targets. Prefer twelve complete months to cover seasons; exact dates/duration require approval. If only a shorter period is feasible, restrict claims to that period. |
| Spatial test | Keep the two test groups out of all parameter fitting, selection and calibration. Their permissible pre-issue histories can supply forecast context. Score their future period once under the frozen model; report transfer separately from Sakha's temporal test. |

For issue date D, retain the tested common cutoff D−7, 60 complete context days, 14 prediction steps, and score only steps 8–14 = D+1…D+7. Record actual per-channel last-available dates and archive retrieval vintages. Simulated historical latency remains retrospective; prospective forecasts require saving input bytes and predictions at issuance, before outcomes arrive. Missing critical inputs yield unavailable forecasts, not future-value filling.

## Bounded comparison and scoring

Compare latest-available persistence; seasonal climatology; one regularized lag/calendar regression; unchanged pinned Chronos-2; a same-release single-Sakha-cell LoRA adapter; and a multi-group LoRA adapter. Use identical target dates, cutoff and missingness policy. Define the tuning budget before any fitting: propose one 200-update run for each adapter, rank 8/alpha 16, learning rate 1e-5, batch size 4, fixed seed and cross-learning across origins disabled. Any repeats, changes in context/predictors or extra configurations require a predeclared budget amendment. Log genuine adapter parameter updates, peak resources, evaluation mode and save/reload tolerance; none is assumed to succeed.

For strict spatial transfer, fit regression and pooled seasonal climatology on training groups only. A site-specific climatology fitted on a test group's earlier history is a useful additional local-history comparator, but must be labelled as local fitting and reported separately from strict transfer. Persistence and allowed inference context use only information available by the cutoff. Shared calendar features are known in advance; realized future weather is not.

Report MAE/RMSE/bias, q10/q50/q90 pinball loss, nominal 80% coverage and interval width by target, lead, season and cell group; show unavailable counts and any predeclared extreme-heat subset. Macro-average group scores to prevent longer series dominating. Estimate uncertainty with paired date blocks shared across cells and spatial-group blocks; retain covariance instead of resampling individual cell-days. Fix block lengths and repeat count before final scoring. Do not sum daily quantiles into a weekly-total confidence interval.

Proposed usefulness gate for review: at least 5% MAE improvement over the strongest predeclared deployable simple comparator, paired block-bootstrap improvement interval excluding zero, and no material target/season degradation. Proposed interval gate: nominal 80% coverage within an agreed tolerance, with useful width, assessed separately by target. The 5% margin, coverage tolerance, degradation limit, sample sufficiency and decision-usefulness criterion are **pending approval**, not retrospectively chosen success thresholds. Calibration uses earlier validation only and is frozen before final scoring. Report losing or inconclusive results.

## Approval and handoff

Amr/Refaat must approve the domain/cell manifest and overlap policy, fresh dates, one-versus-many comparison budget, reproducible source release, thresholds and calibration policy. An actual farmer-decision study additionally needs agronomically permitted near-term actions, consent and a separate protocol. Privacy/hosting remain governed by [PRIVACY_ASSUMPTIONS.md](../product/privacy.md).

Output artifacts would be a versioned raw/source/split manifest, verified ET0 data, training/reload evidence and timestamped predictions/metrics, all distinct from the consumed experiment. No new scores are available. No forecast can establish crop applicability or overturn protected commitments. **UH-001 remains P0 rejected, R1/R2 needs_review, zero validated feasible alternatives.**
