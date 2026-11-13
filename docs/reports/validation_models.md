# MISSION EL GHEET — forecast model decision audit

**11 November execution update:** Actual local LoRA training and held-out evaluation have now run. Hardware execution passed; useful improvement did not. Read [the actual model results](validation_model_execution.md) before the initial source audit below. Any initial “not installed/trained” wording describes the earlier state and is superseded by that result.

Audit date: . Scope: the required trained-ML experiment for a seven-day regional Tmax and FAO-56 reference evapotranspiration (ET₀) outlook for one Sakha-area pilot. Deploying a successful forecast remains conditional; the training experiment itself is a user requirement. This document does not change Promise Test or Season Replay.

## Verdict

**Retain Chronos-2 with LoRA as the first model experiment. Do not yet commit to fine-tuned forecasts as a validated product capability.** The model, adapter method and public checkpoint exist. Local training feasibility, improvement over simpler forecasts, calibrated uncertainty and useful changes to eligible near-term decisions remain unproved.

The forecasting task is scientifically meaningful: use information available on an issue date to predict later regional weather and weather-derived reference demand. Calculating future ET₀ from later weather is a legitimate reference target; it does not make forecasting that future value a trivial equation imitation. It becomes leakage if later weather is supplied as an input. The labels are POWER-based reference estimates, not measured field ET, soil moisture, irrigation requirement, yield or soil improvement.

Fine-tuning is justified only if adaptation improves held-out performance or decision usefulness. Starting from pretrained weights is not evidence of improvement over a small TCN, persistence or seasonal climatology.

## What is actually verified

| Item | Evidence and limit |
|---|---|
| Candidate | Amazon's public Chronos-2 card describes 120M parameters, native multivariate/past-covariate support and multi-step quantiles. This matches two related targets plus available historical weather. It is a general forecasting model. [Model card](https://huggingface.co/amazon/chronos-2) |
| Public metadata access | The configuration and weight-file metadata opened without an access gate. The weights are listed as 478 MB; no weights were downloaded or loaded. [File listing](https://huggingface.co/amazon/chronos-2/tree/main) |
| Configuration | The inspected config specifies 12 layers, width 768, 12 heads, 16-step input/output patches, an 8,192-step maximum context and 21 quantiles. These are capacities, not recommended settings for this pilot. A 30–60-day context is allowed but may be short for annual seasonality. [Public config](https://huggingface.co/amazon/chronos-2/blob/main/config.json) |
| Checkpoint identity | The weight page shows source commit prefix `95a9710` and SHA256 `ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42`. This is published metadata, not a locally verified checksum. Freeze an immutable revision and verify the downloaded checksum when a training run is authorized. [Weight metadata](https://huggingface.co/amazon/chronos-2/blob/main/model.safetensors) |
| Release | The repository currently lists v2.3.2 as latest; its changes include LoRA-loader compatibility and forecast precision fixes. Use a pinned, tested release rather than a moving branch. [Official releases](https://github.com/amazon-science/chronos-forecasting/releases) |
| License | The model card declares Apache-2.0; the library contains Apache License 2.0. Preserve required license/notices and record changes when distributing derivative software or model artifacts. Dataset terms remain a separate matter. [Library license](https://github.com/amazon-science/chronos-forecasting/blob/v2.3.2/LICENSE) |

The inspected package declares Python ≥3.10, PyTorch ≥2.2 and <3, Transformers ≥4.41 and <6, Accelerate ≥1.1 and <2, NumPy ≥1.21 and <3, Einops ≥0.7 and <1, and pandas ≥2 and <4. Its optional extras include PEFT ≥0.18.1 and <1. These are declared compatibility ranges, not a verified Windows environment or a reason to install every optional dependency. [Versioned package metadata](https://github.com/amazon-science/chronos-forecasting/blob/v2.3.2/pyproject.toml)

## LoRA is supported, but the two interfaces differ

Prefer the direct `chronos-forecasting` library for this focused experiment; AutoGluon is not required. In the inspected direct implementation, `Chronos2Pipeline.fit` supports `finetune_mode="lora"` but defaults to **full** tuning. Its default adapter has rank 8 and alpha 16, targeting attention projections and an output projection. Its batch count includes target and covariate series. The method copies the base model onto the same device, which matters for peak memory. If PEFT is unavailable, it warns and falls back to full tuning. Check the logged trainable-parameter count and fail the run if LoRA is not active. [Versioned direct implementation](https://github.com/amazon-science/chronos-forecasting/blob/v2.3.2/src/chronos/chronos2/pipeline.py)

Current AutoGluon exposes `fine_tune=True` and defaults its Chronos-2 wrapper to LoRA through `fine_tune_mode="lora"`; the similarly named options are not interchangeable with the direct API. It also enables cross-learning by default. Do not batch backtest examples from different issue dates together for cross-learning: another example's later context can disclose a target-period observation. For this single locality, group only variables available at the same issue date and disable cross-item learning. [AutoGluon model documentation](https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-model-zoo.html)

## Hardware and data adequacy

The stated hardware is RTX 3050 with 4 GB VRAM and 24 GB system RAM; the second RTX 4050's VRAM is unconfirmed. Neither training memory nor runtime has been measured. A 478 MB checkpoint does not imply a 478 MB training footprint. LoRA reduces trainable state but does not remove base weights, activations, temporary copies and framework overhead.

Official AutoGluon guidance reports testing on a 24 GiB A10G and warns that fine-tuning with limited data can degrade accuracy. Its example recommendation of more than 100 series is a heuristic, not a hard API requirement or proof that a long single series cannot adapt. Our one-locality case does not satisfy that example. [Official fine-tuning and hardware guidance](https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-chronos.html)

A later smoke test should use one GPU, a short context and the smallest batch that preserves the chosen target/covariate group. Measure peak allocated/reserved VRAM, system memory, update time, adapter save/reload and inference latency. Try a bounded short run before committing to a tuning schedule. Do not claim the 3050 is sufficient or the 4050 is faster enough without those measurements. CPU inference support is not evidence of acceptable CPU training time.

At this audit's initial local inspection, `work/readiness_/power_sample_provenance.json` documented only seven historical days at provisional 31.10°N, 30.95°E. `readiness_checks.json` recorded a core FAO-equation reference check, explicitly excluding the full POWER-to-ET₀ pipeline. A separate data-validation task is obtaining the longer archive; its final report must supersede this initial status before training. The provisional coordinate is not a confirmed farm.

Even 25 calendar years at one point provide repeated seasons, not 25 independent locations. Report complete years, missing blocks, observed source changes and hot/extreme-event counts. Do not create artificial sample size by duplicating crops, farms or coordinates in the same source cell. POWER documents native meteorological resolution of 0.5° × 0.625° and solar resolution of 1° × 1°; nearby coordinate queries can return the same information. If additional locations are ever used, deduplicate by native cells and split by both dates and spatial groups. [NASA archive guidance](https://power.larc.nasa.gov/docs/tutorials/)

## Forecast issue-date contract

1. Fix an issue timestamp, daily time convention and output dates. For an issue date D, the farmer-facing outlook covers D+1 through D+7. If the data task uses LST, retain LST throughout processing/evaluation and describe its relationship to the displayed local calendar. The API defaults to LST and also supports UTC. [Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
2. NASA reports typical latency of 2–3 days for meteorology and 5–7 days for solar. These are not guaranteed cutoffs. Record actual last-available dates for every input channel; calculated ET₀ cannot be fresher than its slowest required input. [NASA latency FAQ](https://power.larc.nasa.gov/docs/faqs/data/)
3. The simplest auditable first experiment uses a common complete cutoff C and predicts through D+7, scoring only D+1…D+7. For C=D−7, that requires 14 model steps; the displayed seven days are steps 8–14. A nominal seven-step forecast from C would end at D and contain no future days for the user. Train and evaluate the relevant longer lead times.
4. A richer experiment can retain fresher meteorological covariates with per-channel missingness/age, but must reproduce those availability masks at **every** training and validation origin. A generic fit on complete historical rows does not establish that contract. Never fill a missing recent value from observations arriving after D. Calendar features may be known ahead; realized future weather may not.
5. Historical POWER is revised: climate-quality meteorology replaces quick-look products after about 2–3 months, and other corrections occur. Present-day archives with simulated latency therefore support a **retrospective latency-aware evaluation**, not a true historical real-time replay. Start recording retrieval times, response versions and future issued forecasts for prospective validation. [NASA revision guidance](https://power.larc.nasa.gov/docs/tutorials/)

## Pretraining and evaluation leakage

Chronos-2's published training table includes Weatherbench, USHCN and Temperature-Rain, among other sources. No exact Sakha POWER exclusion or complete per-record cutoff audit has been established here. Different dataset names do not prove independence from the same historical weather events. [Original technical report, Appendix A](https://arxiv.org/html/2510.15821v1)

Freeze a checkpoint whose weight timestamp predates the final test period. Prefer post-checkpoint dates for the final assessment, and keep their labels out of local fine-tuning, calibration and model selection. An older holdout can still diagnose adaptation, but label its unknown pretraining overlap. A 2001–2025 archive alone does not provide a full post-October-2025 year. This limitation is separate from NASA's archive revisions and from ordinary train/test leakage.

Use chronological rolling origins, with all training targets ending before the validation period and all tuning/calibration ending before final test targets. Context from earlier dates is legitimate; target leakage across split boundaries is not. Fit any external scaler, climatology, missing-data rules and calibration only from permissible earlier data. Do not randomly split overlapping windows. Report uncertainty using time blocks or non-overlapping evaluation weeks rather than treating overlapping seven-day windows as independent replicates.

## Small, fair experiment and decision gates

Compare four forecasts on the same output dates and availability contract: latest-available-value persistence; a training-only seasonal climatology; unchanged Chronos-2; and the LoRA-adapted checkpoint. The original small TCN can be an additional comparator if already implemented, but is not required to assess whether LoRA helps the pretrained checkpoint. No broad architecture search is needed.

Pre-register a small tuning budget and validate 30 versus 60 days of context. Consider annual calendar features rather than silently assuming a short history identifies the season. Keep the test untouched. For each target separately report median MAE in °C or mm/day, quantile loss, interval coverage/width, and performance by lead day and season. Evaluate extreme-heat cases separately. Avoid combining both targets' raw numerical losses without scaling or separate reporting. Quantile outputs are marginal forecasts: summing seven daily quantiles does not produce a calibrated quantile of the weekly total.

| Gate | Evidence required to pass | If unmet |
|---|---|---|
| Data/reference | Reproducible historical export; unit/missingness checks; independently checked full ET₀ calculation; split manifest | Do not fine-tune or publish forecast scores. |
| Execution | Verified LoRA mode, memory/runtime within the available machine and time budget, reproducible adapter reload | Required training experiment remains incomplete. An unchanged-model result alone does not satisfy it; retain the planner while resolving execution. |
| Skill | Validation-selected adapter improves the predeclared metric over unchanged Chronos-2 and useful simple baselines; untouched test confirms useful improvement without unacceptable degradation in another target/season | Do not claim adaptation is better. Report negative findings. |
| Uncertainty | Held-out coverage and interval width are acceptable for the intended display; any calibration uses earlier held-out data | Show experimental estimates without confidence claims or defer use. |
| Decision relevance | At least two agronomically permitted, farmer-acceptable near-term dates exist; the forecast changes a clearly defined exposure comparison, and retrospective/prospective scoring supports that comparison | Do not present the model as optimizing a date or rotation. |

The outlook can compare weather exposure for permitted actions inside the next week; it cannot supply skill for dates months away. It should not overturn field-release, crop-calendar or forage/grain constraints. Weather-score improvement alone does not establish higher yield, reduced irrigation, healthier soil or financial benefit. If all eligible dates are beyond D+7, or uncertainty cannot distinguish them, keep the four-season comparison grounded in its transparent historical analysis and state that the short-term outlook does not resolve the choice.

Initial source audit performed no model installation, weight download, loading, training or inference. The user has now approved an isolated local execution test. Its measured results will be appended; approval or installation alone does not pass the empirical decision gates.
