# MISSION EL GHEET — actual model test results

Completed 11 November 2026. Verdict: **local LoRA execution verified; useful forecasting improvement not established.**

## What ran

An isolated workspace environment used Python3.12.14, PyTorch2.9.1+cu128, chronos-forecasting2.3.2, PEFT0.18.1 and Transformers5.22.2. No application or external account was created. The public Chronos-2 checkpoint was downloaded at immutable revision `29ec3766d36d6f73f0696f85560a422f50e8498c`; its 477,930,472-byte weight file matched the published SHA256. Commit history places that revision on 5 June 2026.

Two-target inputs were historical regional Tmax and ET0 calculated from POWER. The bounded experiment used 60-day contexts, 14 prediction steps, batch size4, LoRA rank8, learning rate1e-5 and a fixed seed. Of 120,684,576 parameters, **1,206,912 (about1%)** were trainable adapters. All194 adapter tensors changed. Separate20- and200-update runs completed on the RTX3050 Laptop GPU with4GB memory.

The200-update fit took **40.31 seconds** including its wrapper/save operations, with **1,267,588,608 bytes peak allocated GPU memory** and1,270,874,112 bytes peak reserved. These figures apply only to this small configuration; they exclude download/setup time and other applications' GPU memory. They do not promise larger-context or production performance.

## Reproducibility correction

The first smoke run correctly failed its reload check. Investigation found that the training routine left training mode and mixed-precision forward wrappers attached. Repeated predictions were inconsistent. Evaluation now explicitly sets evaluation mode and removes the training precision wrapper before comparison with an FP32 reloaded checkpoint.

The verified20-step rerun and200-step run both passed the unchanged0.001 reload tolerance. The200-step run's maximum checked difference was0.000602. Original failing logs and the diagnostic reproduction are retained. Do not use the failed run's metrics.

## Time separation and fair comparisons

- Training:2001–2018.
- Diagnostic validation:36 monthly issue dates in2019–2021. The200-step adapter was selected by lower ET0 validation MAE, as declared before held-out prediction.
- Held-out check:17 non-overlapping weekly origins during July–October2026,119 target days per variable, after the pinned checkpoint revision. No local fitting or selection used those outcomes.
- Every forecast used only values through issue date minus7days. Fourteen steps were predicted; steps8–14 represent the farmer's next7days. All comparators had the same information cutoff. Cross-learning across origins was disabled.
- Baselines: last available value and training-only seasonal climatology. Climatology used a31-day calendar window and empirical quantiles.

This is retrospective evaluation using a currently downloaded, partly revised archive and simulated latency. It is not an archive of forecasts genuinely issued in2026. Pretraining overlap with the older validation years is unknown; the later test dates reduce that concern but do not eliminate the archive-vintage limitation.

## Held-out results

Lower mean absolute error (MAE) is better.

| Forecast | Tmax MAE, °C | ET0 MAE, mm/day |
|---|---:|---:|
| Last available value |2.410|0.753|
| Seasonal climatology |**1.656**|**0.523**|
| Unchanged Chronos-2 |2.000|0.644|
| LoRA-adapted Chronos-2 |1.988|0.640|

The adapter's reductions relative to unchanged Chronos-2 were only0.0127°C and0.00416mm/day. Descriptive weekly bootstrap intervals for both improvements include zero. Seasonal climatology scored better in this sample; the limited test does not establish a universal model ranking.

The adapter's nominal80% intervals covered **76.5%** of Tmax outcomes and **70.6%** of ET0 outcomes. Their mean widths were6.72°C and1.96mm/day. These intervals have not been calibrated for farmer-facing confidence claims.

## Decision

The claim **“we can fine-tune this pretrained model on this laptop”** now has direct evidence for the tested configuration. The claim **“fine-tuning improves this farmer decision”** does not.

Retain this as a completed first experiment and a required research workstream, not a validated forecast recommendation. The tested outlook should not choose a sowing date or override agricultural constraints. A future experiment could examine additional predictors, calendar information, recent training periods or an appropriate weather forecast baseline, but must preserve a fresh evaluation protocol; do not repeatedly tune against this test until it looks successful.

With the user's requirement for meaningful trained ML, the concept cannot honestly be labelled fully validated on this evidence. The planner and historical replay remain separately supportable. No crop outcomes, irrigation benefits, farmer usability or field truth were validated by these forecasting scores.

Evidence: `work/validation_2026-11-10/model_test/` contains the pinned checkpoint provenance, installed environment, run logs, adapter weights, protocol, saved predictions and results. Main result files: [200-step run](../work/validation_2026-11-10/model_test/adaptation200/results.json), [held-out scores](../work/validation_2026-11-10/model_test/holdout_results.json), [protocol](../work/validation_2026-11-10/model_test/evaluation_protocol.json).
