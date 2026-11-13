# MISSION EL GHEET — ML experiment

Status: 11 November 2026. **REQUIREMENT:** retain a meaningful trained-ML workstream. **VERIFIED:** local LoRA training, parameter updates and adapter reload succeeded. **OPEN:** useful forecasting improvement and agricultural decision benefit have not passed validation. This is an experiment specification and evidence record, not a finalized application architecture.

## Task and boundaries

Predict daily regional maximum temperature, Tmax, and reference evapotranspiration, ET₀, for the seven dates after an issue date. Tmax comes from NASA POWER; ET₀ is calculated from POWER weather using the documented FAO-56 method. These are modeled, gridded reference targets, not independent measurements of a farmer's field. Forecasting future calculated ET₀ is meaningful provided future weather never enters the inputs. It does not establish crop water use, irrigation quantity, yield or soil improvement.

**VERIFIED:** the tested model received only the histories of these two targets, jointly. No additional weather predictors, calendar covariates, farmer history or crop identity were tested. One provisional Sakha-area point supplies one regional history; different crops or nearby farms are not independent training locations. Geographic transfer is untested. See [DATA_SPEC.md](DATA_SPEC.md) for schemas/provenance and [SCIENCE.md](SCIENCE.md) for equations and scientific limits.

## First experiment: what actually ran

**VERIFIED:** the direct Chronos-2 implementation was adapted with LoRA; AutoGluon was not used. The pinned [v2.3.2 API](https://github.com/amazon-science/chronos-forecasting/blob/v2.3.2/src/chronos/chronos2/pipeline.py) supports this method but defaults to full tuning and can fall back to full tuning if PEFT is missing. The actual run checked that trainable parameters belonged to adapters. The model and library declare Apache-2.0; preserve applicable notices when distributing derivatives. [Model card](https://huggingface.co/amazon/chronos-2), [versioned license](https://github.com/amazon-science/chronos-forecasting/blob/v2.3.2/LICENSE).

The downloaded model was `amazon/chronos-2`, revision `29ec3766d36d6f73f0696f85560a422f50e8498c`, dated 5 June 2026. Its 477,930,472-byte weight file matched SHA256 `ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42`. [Checkpoint provenance](../work/validation_2026-11-10/model_test/checkpoint_provenance.json).

| Setting | Tested value |
|---|---|
| Runtime | Python 3.12.14; PyTorch 2.9.1+cu128 |
| Model libraries | chronos-forecasting 2.3.2; PEFT 0.18.1; Transformers 5.22.2; Accelerate 1.15.0 |
| Input/context | Two targets; 60 complete historical days |
| Horizon/batch | 14 prediction steps; batch size 4 counting series |
| Adaptation | LoRA rank 8, alpha 16; learning rate 0.00001 |
| Runs/seeds | Separate 20- and 200-update runs; seed/data seed 20261111 |
| Evaluation | Quantiles 0.1/0.5/0.9; cross-learning across origins disabled |

The [installed dependency record](../work/validation_2026-11-10/model_test/installed_requirements.txt) fixes the remaining package versions. The adapters contained 1,206,912 trainable parameters out of 120,684,576 total, approximately 1%. All 194 adapter tensors changed in the 200-update run. Training used one RTX 3050 Laptop GPU with 4 GB VRAM, without distributed training. The machine had 24 GB system RAM; peak RAM use was not measured. The other RTX 4050 was not tested.

The 200-update fit took **40.31 seconds**, including wrapper/save operations. Peak allocated GPU memory was 1,267,588,608 bytes; peak reserved memory was 1,270,874,112 bytes. These measurements exclude setup/download time and other applications' GPU use. They establish feasibility only for this configuration. [Run results](../work/validation_2026-11-10/model_test/adaptation200/results.json).

**VERIFIED correction:** the original smoke run failed reload consistency. Investigation identified retained training mode and mixed-precision forward wrappers. Evaluation now explicitly calls `.eval()` and removes the training precision wrapper before comparison with the FP32 reload. Verified reruns passed the unchanged 0.001 tolerance; the 200-step maximum checked difference was 0.000602. Failed-run metrics must not be used. [Execution account](validation_model_execution.md).

## Time contract and evaluation

**VERIFIED:** fitting used 2001–2018. Diagnostic validation used 36 monthly issue dates in 2019–2021. The [protocol](../work/validation_2026-11-10/model_test/evaluation_protocol.json) declared adapter selection by lower validation ET₀ MAE before held-out prediction; this selected the 200-update adapter. Tmax was reported separately.

For issue date D, inputs ended at D−7. Predicting 14 steps made steps 8–14 correspond to D+1…D+7. A seven-step prediction from that cutoff would stop at D and would not forecast the user's next week. Every comparator used the same cutoff. NASA reports typical meteorological delays of 2–3 days and solar delays of 5–7 days; these are not availability guarantees. [NASA latency FAQ](https://power.larc.nasa.gov/docs/faqs/data/).

The held-out assessment used 17 non-overlapping weekly origins from 1 July through 21 October 2026: 119 target days per variable, after the pinned revision. Local fitting and adapter selection did not use those outcomes. Earlier validation may overlap foundation-model pretraining; this has not been ruled out.

This remains retrospective evaluation with simulated latency. POWER revises historical products, so the downloaded values are not necessarily those available on each historical issue date. [NASA archive guidance](https://power.larc.nasa.gov/docs/tutorials/). No independent station-target forecast evaluation or prospective operational evaluation was performed; the separate limited station-table weather check in [SCIENCE.md](SCIENCE.md) does not establish either.

Metrics are separate for each variable. MAE averages absolute median-forecast errors; RMSE is the square root of their mean squared errors; bias averages forecast minus target. Pinball loss averages `max(q*e, (q-1)*e)`, where `e = target - predicted quantile`, over the reported quantiles. Nominal 80% coverage counts targets between q10 and q90; width averages q90−q10. Lead days 1–7 are measured from the issue date. Uncertainty resamples whole forecast weeks, not individual correlated days.

## Results, including the negative finding

**VERIFIED:** seasonal climatology had the lowest observed MAE in this limited held-out sample. Lower is better.

| Forecast | Tmax MAE, °C | ET₀ MAE, mm/day |
|---|---:|---:|
| Last available value | 2.410 | 0.753 |
| Training-only seasonal climatology | **1.656** | **0.523** |
| Unchanged Chronos-2 | 2.000 | 0.644 |
| Selected LoRA adapter | 1.988 | 0.640 |

Climatology used a 31-day calendar window and empirical quantiles. The adapter's MAE reductions against unchanged Chronos-2 were only 0.0127°C and 0.00416 mm/day. Descriptive weekly-bootstrap 95% intervals were −0.00536…0.02925°C and −0.000922…0.009746 mm/day; both include zero. Seventeen weeks do not establish a universal ranking or reliable benefit across seasons.

The adapter's nominal 80% intervals covered 76.5% of Tmax and 70.6% of ET₀ outcomes, with mean widths of 6.72°C and 1.96 mm/day. They are not calibrated farmer-facing confidence claims. Daily quantiles must not be summed and labelled weekly-total quantiles. [Held-out evidence](../work/validation_2026-11-10/model_test/holdout_results.json).

## Forecast output contract

**PROPOSED:** one record per target date and variable contains `issue_date`, `input_cutoff`, `target_date`, `variable`, `unit`, `q10`, `q50`, `q90`, `model_revision`, `adapter_run_id`, `source_vintage`, `experimental`, and `stale`. Dates use the documented daily convention; units are °C or mm/day. `source_vintage` identifies retrieval timestamp and source snapshot/hash. Quantiles must be finite and ordered. `experimental` remains true until usefulness gates pass; `stale` identifies inputs older than the declared cutoff or an expired outlook. Missing or invalid inputs require an unavailable result, not invented quantiles. This contract is not an implemented service.

## Next experiment and integration gates

**PROPOSED:** keep persistence, seasonal climatology and unchanged Chronos-2 as comparators. Add one simple fitted baseline—regularized regression using permissible lags and calendar features—before spending effort on a larger tuning search. This fitted baseline has **not run**. Fit preprocessing and hyperparameters on training/validation only; never randomly split overlapping windows across time. Additional predictors, newer training periods and calendar information are candidate changes, not established improvements.

Declare the tuning budget, selection metric, practical improvement margin and uncertainty criteria before another assessment. Use only permitted training/validation periods for fitting and calibration. The July–October 2026 outcomes are now consumed evidence: do not tune against them and present repeated scores as a fresh test. Reserve unseen dates or collect prospective forecasts with timestamped input snapshots. No geographic holdout has run. If more sites are added, deduplicate and group splits by distinct native source cells as well as time; coordinate changes alone do not create independent sites.

**OPEN gates:** demonstrate useful improvement over strong simple baselines on fresh assessment; establish interval coverage and stability across relevant seasons; and test whether forecasts improve a specified choice between agronomically permitted, farmer-acceptable near-term dates. Acceptable error and decision margins require agreement before testing. Successful training alone passes none of these usefulness gates.

The seven-day forecast cannot rank four-season rotations or justify changes months ahead. It may eventually inform exposure comparisons within its verified horizon, while respecting field release, crop calendars and forage/grain requirements. Until usefulness passes, preserve the required ML workstream without presenting its outputs as validated recommendations. [PRODUCT.md](PRODUCT.md) governs presentation and [SCIENCE.md](SCIENCE.md) governs permissible claims.

Approval points: agree the next bounded comparison, the fresh assessment period and the farmer decision it must improve. No additional experiment or architecture commitment is authorized by this document itself.
