# MISSION EL GHEET — validation verdict

. This report supersedes earlier readiness statements. It records a completed first audit and bounded model experiment, not a fully validated farming product.

## Decision

**The data/calculation foundation is reproducible, and local fine-tuning works. The complete idea is not yet ready to be called validated.** The main unresolved requirement is that trained ML must improve a concrete farmer decision. The tested outlook has not demonstrated that value. Some crop rules and the accessible interaction also remain unvalidated.

Do not interpret this as evidence that fine-tuning can never help. It is the result of two bounded configurations, one location and a small seasonal test. It is enough to reject an unsupported claim of established superiority.

## Readiness by component

| Component | Evidence obtained | Verdict |
|---|---|---|
| POWER access and integrity | Original HTTP downloads: 9,435 days, 75,480 values across 2001–October2026; date alignment, units and missing flags checked | Passed for these records; field representativeness is separate |
| ET0 mathematics | Twelve checks; full FAO example3.880259 versus3.88; independent all-row reproduction; explicit cloudiness bound | Numerical checks passed |
| ETc and crop assumptions | Standard equation and coefficient sources identified; arithmetic checked | Local stages/cutting/management applicability incomplete |
| Published local context | Sakha soil profiles, wheat–maize trial dates and a2023 maize bulletin located | Supports a labelled research scenario, not every crop repair |
| Chronos-2 LoRA execution | Real20- and200-update runs, saved adapters, verified parameter changes and reload | Passed for tested RTX3050 configuration |
| Forecast improvement | Later17-week test,119 days per target; four comparators; uncertainty checked | Useful superiority not demonstrated |
| Arabic/English speech and accessibility | Existing service capabilities and recovery design checked | No service call or intended-user test completed |
| End-to-end planner and farmer benefit | Design and acceptance criteria only | Not implemented or validated |

## Fine-tuning result

The200-update adapter was selected using earlier validation data. The subsequent July–October2026 test was after the pinned checkpoint revision and used seven-day-old input cutoffs consistently. Lower MAE is better:

| Method | Tmax MAE, °C | ET0 MAE, mm/day |
|---|---:|---:|
| Last available value |2.410|0.753|
| Seasonal climatology |**1.656**|**0.523**|
| Unchanged Chronos-2 |2.000|0.644|
| LoRA-adapted Chronos-2 |1.988|0.640|

Fine-tuning's small gains over the unchanged model are not robust in the descriptive weekly uncertainty check. Its nominal80% ET0 interval covered70.6% of outcomes. The test is too limited for broad seasonal, geographic or farming claims.

On this configuration,200 updates took40.31seconds and peak allocated GPU memory was1.27GB decimal. The1.21million trainable parameters were real LoRA adapters. Setup/download time is excluded. A training-mode/precision issue found by the reload test was diagnosed and corrected before accepting results.

**Conclusion:** fine-tuning feasibility is confirmed; meaningful forecasting benefit and decision usefulness remain open. Keeping a required trained-ML workstream does not justify using its output as validated advice.

## Concept supported by the current evidence

MISSION EL GHEET remains a farmer-facing Arabic/English rotation-planning assistant built around: **“Tell us what must stay. Hear what can change.”**

The farmer answers one short spoken question at a time, uses familiar crop pictures, and hears crops, dates, quantities and units repeated before confirmation. Picture/audio choices, typing and adviser assistance support recovery. English provides the same functionality and preserves the same approved facts.

The farmer protects essential grain/forage commitments and supplies local soil and irrigation constraints. Explicit crop rules check four consecutive seasons. The planner explains conflicts and offers up to two meaningfully different feasible alternatives with minimal unnecessary changes. It never changes protected requirements without approval. A date-only option is labelled a timing variant; no valid alternative is an acceptable result.

Season Replay compares candidates under the same consecutive historical weather blocks. It uses temperature, reference ET0 and conditional crop ETc, showing duration and production commitments alongside demand. Sourced crop-family/legume/rooting characteristics and soil restrictions inform eligibility or explanations. These are planning indicators, not measured soil-health gains. No combined best-farming score is proposed.

An approved plan produces a spoken takeaway and matching evidence details. The short trained outlook remains a separate research experiment for eligible near-term actions. It cannot establish four-season suitability, irrigation supply, yield or soil improvement, and it has not yet demonstrated useful skill over the simpler seasonal comparator.

This is an evidence-informed **prototype concept**, not the final validated idea requested. Because meaningful trained ML is a firm requirement, final approval should not silently assume that gate has passed.

## Decisions arising from the audit

1. **Keep Sakha as the research scenario.** Public data exist; no adviser was assumed or invented. Describe published soil as a study profile, never a measurement of the user's field. The examined saline trial needs particular care when discussing standard-condition ETc.
2. **Treat wheat, berseem and grain maize as the better-supported initial candidates.** Grain sorghum should not be offered as a locally validated substitute yet. This proposed catalogue narrowing requires the user's approval, not a silent scope change.
3. **Keep crop rules evidence-labelled.** Recommended windows, observed trial dates and modeling assumptions are different. Crop-stage curves, field preparation time and exact forage-cut effects still need an explicit defensible treatment. Unsupported entries cannot be described as agronomically verified.
4. **Keep the fine-tuning requirement open.** The executed experiment is real, but its benefit is unproved. Another justified experiment would need a fresh evaluation plan; do not keep tuning against the consumed test until it wins.
5. **Test accessibility on the working interaction.** Speech documentation is not proof that farmers who cannot read can confirm and act on a plan. No independent-usability or farm-benefit claim is currently supported.

No application architecture, hosted speech subscription, production deployment or full documentation programme was started. The isolated model environment and evidence files are retained in the workspace. Implementation/documentation decisions remain for the user's later approval.

## Audit records

- [Data, equations and their limits](validation_data_equations.md)
- [Independent equation review](validation_equations_review.md)
- [Crop and soil evidence ledger](validation_agronomy.md)
- [Model sources and methodological audit](validation_models.md)
- [Actual model execution and held-out results](validation_model_execution.md)
- [Speech, accessibility and challenge alignment](validation_accessibility_alignment.md)
- [Saved-artifact verification](../work/validation_/model_test/artifact_verification.json)

Original data, response hashes, calculation checks, model weights/adapters, logs, frozen package versions and predictions are under `work/validation_/`. Earlier files with “Final” in their names describe design decisions and do not override this verdict.
