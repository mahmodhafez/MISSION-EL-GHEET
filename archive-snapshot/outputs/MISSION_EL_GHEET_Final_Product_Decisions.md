# MISSION EL GHEET — agreed product direction

**Validation update, 11 November 2026:** this is the earlier design decision record, not a validated product specification. Actual tests subsequently confirmed NASA data access, reference calculations and local LoRA execution, but did not establish useful forecast improvement. Consult [the current validation verdict](MISSION_EL_GHEET_Validation_Verdict.md) before using this record for final documentation or implementation decisions.

Decision record: 10 November 2026. Scope finalized for implementation; performance and local applicability remain subject to the checks below. This record carries forward the existing concept rather than adding core features.

## Purpose and boundary

Help a farmer protect essential crop commitments, understand conflicts across four consecutive cropping seasons, compare useful feasible alternatives and approve an understandable plan. Start with one locality near Sakha and a small, locally supported crop catalogue. Wheat, berseem, grain maize and grain sorghum remain candidate crops; offering a crop requires applicable rules, including cultivar restrictions where relevant.

## Seven core features

1. **Complete Arabic and English experience.** Egyptian-Arabic and English speech, familiar crop pictures, one question at a time, spoken confirmation of dates and units, and spoken explanations. Large confirm/change/repeat controls; picture/audio choices, typing and adviser assistance provide recovery. Language switching preserves the same facts and approvals. Independent usability by farmers who cannot read remains to be tested.
2. **Farmer commitments and local context.** Collect the current plan, relevant local soil information, irrigation constraints, crop characteristics and grain/forage priorities. Distinguish protected requirements from negotiable preferences. Do not silently invent missing critical inputs.
3. **Promise Test.** Explicit agricultural rules identify conflicts and show how they propagate into later seasons. A protected commitment changes only with the farmer's approval.
4. **Useful alternatives.** Compare the current plan with up to two meaningfully different feasible options. After hard constraints are enforced, select options relevant to farmer priorities with explicit trade-offs and minimal unnecessary changes. Date-only changes are timing variants. There is no unsupported combined best-farming score; no valid alternative is an allowed result.
5. **Season Replay.** Compare the same candidates under the same consecutive historical weather blocks using POWER temperature and FAO56 ET0, with conditional ETc based on sourced crop coefficients and stages. Keep demand, duration and production commitments visible together. Include sourced sequence indicators and soil restrictions; do not present them as measured soil improvement. Seasonal berseem estimates do not determine the exact demand of an additional cut.
6. **Trained near-term outlook experiment.** Fine-tune a pretrained time-series model on suitable NASA-derived history; Chronos-2 with LoRA is the first selected experiment. Predict regional daily maximum temperature and calculated ET0 for seven days beyond the issue date. It may inform an already feasible near-term timing choice; it does not select or predict the success of the four-season rotation.
7. **Approved plan and understandable takeaway.** Provide spoken next steps in the selected language and an evidence card with matching dates, units, sources, assumptions and outstanding adviser checks.

## Fine-tuning decision

Fine-tuning is training that starts from a pretrained model. LoRA trains small adapters while retaining the base weights. NASA numerical time series belong in this forecasting experiment; the speech interface uses a separate existing speech-recognition system. NASA weather records are not speech-training labels.

Chronos-2 and documented LoRA support make this a supported experiment, not a proven local solution. Its fit on a 4 GB GPU and its value with limited local series must be measured. We will compare the adapted model against the unchanged pretrained model, persistence, seasonal climatology and a simple fitted baseline. Actual updates and results must be recorded. If the experiment loses, the product may use a better baseline; the trained experiment and its result remain part of the work.

ET0 targets are calculated from NASA gridded meteorological and radiation products, not directly observed crop demand or soil health. Keep chronological training, validation and test periods separate; enforce information available at each issue date, account for publication latency, and evaluate uncertainty and lead-day errors. POWER's stated delays mean forecasting seven steps after the last available record is not automatically forecasting the next seven days from today. Current archives also do not reconstruct historical publication vintages.

A candidate use case is comparing two agronomically permitted sowing dates within the coming week. Predicted atmospheric demand and temperature provide additional context; they do not establish irrigation availability, germination, yield or the better date without relevant agronomic rules. Demonstrating decision usefulness is a required evaluation task.

## Evidence status at finalization

**Checked:** one browser-accessible seven-day POWER sample; its dates, units and 49 numeric values; a FAO56 reference-equation example; local RTX 3050 with 4 GB memory; current primary documentation for the selected model and fine-tuning method.

**Not yet validated:** full historical dataset and repeatable application download route; the complete NASA-to-ET0/ETc pipeline; locally applicable crop rules and coefficients; model training, memory use, forecast skill and decision usefulness; speech performance; farmer usability; agricultural outcomes.

The next implementation milestone is one locally reviewed farmer case from confirmed input through conflict explanation, historical comparison and spoken takeaway, while data preparation and the ML experiment proceed in parallel. No new package installations, model downloads or application architecture commitments were made by this decision record.

## References and related evidence

- [Chronos-2 model card](https://huggingface.co/amazon/chronos-2).
- [AutoGluon: Chronos fine-tuning and limitations](https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-chronos.html#fine-tuning).
- [NASA POWER: sources, units and latency](https://power.larc.nasa.gov/docs/faqs/data/).
- [Readiness checks and quality plan](MISSION_EL_GHEET_Readiness_and_Quality_Plan.md).
- [Saved numerical check results](../work/readiness_2026-11-10/readiness_checks.json).
