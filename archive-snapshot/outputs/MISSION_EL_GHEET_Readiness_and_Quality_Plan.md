# MISSION EL GHEET — readiness and quality plan

Prepared 10 November 2026. This is a development planning record, not a claim that the product, model or farmer benefits have been validated.

## Recommended direction

Keep the agreed product. Make its defining experience: **the farmer says what must stay; the planner reveals what conflicts, then explains the smallest permitted changes and their consequences across four seasons.**

One locality near Sakha; a locally justified crop catalogue; the current plan and up to two meaningfully different feasible alternatives; complete Arabic and English interaction. Egyptian-Arabic audio and pictures remain core. Preserve the trained seven-day outlook experiment with its separate, near-term decision role.

Do not add features to raise a subjective score. Earn stronger assessments through a coherent working example, understandable decisions, independent checks and observed user performance.

## Readiness findings

| Area | Observed evidence | Remaining work |
|---|---|---|
| NASA access | A browser request returned seven days, 1–7 October 2024, for a provisional point at 31.10°N, 30.95°E. All seven requested variables were present: 49 numeric values, matching dates, no missing flags. | Confirm the actual pilot point, obtain a longer reproducible history, and fix the application download route. The direct shell request failed DNS resolution. |
| Units | This AG response supplies radiation in MJ/m²/day and pressure in kPa. | Read metadata rather than applying assumed conversions. Preserve units and time standard in cached records. |
| ET0 equation | Independently reproducing FAO56 Example 18 with its rounded intermediate inputs gives 3.87894 mm/day versus the published 3.88. Absolute difference: 0.00106 mm/day. | Check the full weather-to-ET0 pipeline, humidity treatment, missing data and conversions. This result does not validate crop ETc or any field result. |
| Crop applicability | Egyptian Ministry/ARC sorghum bulletin 1393/2020, printed page 18, advises against tall sorghum varieties in Lower Egypt because of leaf-spot susceptibility. | Gate grain sorghum by a locally supported cultivar and management case. This is not a blanket exclusion of all sorghum. Source the other crop rules too. |
| Hardware | Local hardware query identified an RTX 3050 Laptop GPU with 4,096 MiB memory. | Benchmark the selected model on the actual machine. The second RTX 4050 laptop's memory and availability remain unverified. |
| Training environment | The inspected bundled Python environment lacks the relevant ML and speech packages. | Choose and approve the project environment and dependencies before installation. No fine-tuning, inference benchmark or speech accuracy test has run. |

The NASA sample was observed in the browser and transcribed into a local JSON file; it is not a byte-for-byte HTTP archive. Its coordinates are a research point, not a farmer's confirmed field. The sample passes structural and elementary range checks; these do not establish accuracy or local representativeness.

Evidence: [sample and provenance](../work/readiness_2026-11-10/power_sample_provenance.json), [check results](../work/readiness_2026-11-10/readiness_checks.json), [reproducible checks](../work/readiness_2026-11-10/check_readiness.py).

## Four improvements worth prioritising

### 1. Distinctiveness: make the consequence visible and audible

Start with “What must stay?” rather than a blank crop calendar. Visually protect the farmer's commitments and explain each protection aloud. Show the specific collision between commitments and crop rules, then trace any permitted change through the following seasons.

After enforcing hard constraints, prefer alternatives that differ in ways relevant to the farmer's priorities and avoid unnecessary changes. Compare the number and size of changes explicitly; do not invent an overall best-farming score. Within the bounded candidate set, check whether a smaller permitted repair exists. A date-only option is a timing variant, not a different crop rotation. If no valid repair exists, explain the conflict and ask which condition the farmer is willing to reconsider.

Each alternative uses the same explanation structure: **“We keep __. We change __. The trade-off is __. We still need to check __.”**

### 2. Story: one real dilemma, one visible consequence

Illustrative opening: a farmer needs to retain berseem for livestock while fitting the next crop and preserving a later grain commitment. Dates, cultivars and the existence of a conflict must come from a locally reviewed case, not a manufactured dramatic outcome.

Show one farmer-approved change, its downstream consequences and the historical comparison. NASA earns its place when the same feasible plans have different historical temperature exposure or estimated crop-period demand that a calendar alone does not show. A tie or uncertain difference is a legitimate result. Never force a ranking reversal.

The memorable interaction is the farmer correcting a date or unit, hearing the corrected commitment, and seeing the whole plan respond consistently. Use an actual correction interaction or label a staged test scenario; do not pass a scripted recognition failure off as live behaviour.

### 3. Accessibility: prove that the plan can be understood without reading

Ask one short spoken question at a time. Pair familiar crop pictures with spoken names. Read back crops, dates, quantities and units. Provide large confirm, change and repeat controls with audio guidance. Offer picture/audio choices, typed input and adviser help when recognition fails. Do not make successful speech recognition the only route through the product.

Arabic and English must cover the complete journey, including errors and recovery. Switching languages must preserve the same plan values, approvals and calculations. The final takeaway says what stays, what changes and what needs confirmation; written calculation details remain available to an adviser.

Proposed formative target: test with five intended users, including farmers who cannot read. At least four should be able to explain the protected commitment and proposed change using audio/pictures, with no unresolved crop/date/unit error. Record all facilitator assistance. This is a small internal learning target, not proof of independent accessibility or a population-level success rate.

### 4. Impact: demonstrate a better-informed decision

Compare the planner with a calendar-only baseline using the same farmer inputs, crop catalogue and constraints. Measure whether users can identify the conflict, distinguish the alternatives and explain their selection. Record completion, errors and assistance, not just satisfaction. Vary task order where possible and report the small sample honestly.

Keep crop-period demand, duration and grain/forage commitments together. Show sourced crop-family, legume and rooting traits where relevant; an estimated crop-free interval is not a measured bare-soil period. Local soil restrictions must affect eligibility or interpretation. These are planning indicators, not demonstrated soil-health gains. Preserving a forage crop does not establish that livestock feed quantity is sufficient.

## Technical depth that serves this experience

The deterministic planner owns feasibility and alternatives. The replay engine owns explicit temperature, FAO56 ET0 and conditional ETc calculations. Crop coefficients, stages, management assumptions and source applicability must be documented. Seasonal berseem coefficients cannot establish the exact demand of an extra cut.

Keep the proposed pretrained Chronos-2 LoRA fine-tuning experiment, subject to a resource benchmark. Compare it with the unchanged pretrained model, persistence, seasonal climatology and a simple fitted baseline. Actual parameter updates, configurations and held-out results must be recorded; a failed training run does not fulfil the trained-ML requirement.

Its targets are seven-day regional Tmax and calculated ET0, not measured farm outcomes. The ET0 labels derive from NASA gridded meteorological and radiation products combined with a reference equation. Use chronological training/validation/test separation and only information available at issue time. Historical archive revisions and NASA publication latency require explicit handling; a current archive does not reconstruct an operational vintage. Any geographic transfer claim needs held-out locations and attention to shared source grids.

Evaluate errors by lead day and season, uncertainty interval coverage, and whether additional skill changes an already eligible near-term timing choice. A short outlook must not silently determine a four-season sequence. If skill adds no decision value, report that result and use the better baseline. A smaller model can address compute limits, but cannot repair missing data or a weak decision role.

## Recommended build order and ownership

1. **Reviewed reference case:** Yahya, Ahmed and Mahmoud assemble sourced crop rules, a confirmed pilot location and manually checked feasible alternatives. Obtain local agronomic review. Amr defines the farmer's decision and required explanation.
2. **Calculation and decision path:** Ahmed establishes reproducible NASA records; Mahmoud checks ET0 and replay; Yahya checks constraints and alternatives; Karim provides data access and caching. Complete a fair calendar-versus-replay comparison.
3. **Complete bilingual farmer journey:** Amr leads interface and integration; Moaaz develops crop visuals, spoken interaction assets and presentation. Test confirmation, correction, picture fallback and language switching. Everyone reviews.
4. **ML experiment in parallel after data checks:** Amr and Mahmoud benchmark resource use and fine-tuning. Integrate the outlook only into its clearly defined near-term decision. Preserve experiment results even if the baseline wins.
5. **Observed user test and demonstration:** fix the largest comprehension and recovery problems first. Show the actual working interaction, traceable evidence and the limits of the experiment.

These are milestone gates, not guaranteed completion dates. No application stack or significant dependency has been installed by this readiness work. Keep development dates and reused components accurate; eligibility is for the organisers to clarify.

## Sources

- [NASA POWER daily API documentation](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) and [data FAQs, including latency](https://power.larc.nasa.gov/docs/faqs/data/).
- [FAO56, Chapter 4, Example 18](https://www.fao.org/4/X0490E/x0490e08.htm); [Chapter 3, weather inputs and humidity](https://www.fao.org/4/X0490E/x0490e07.htm); [Chapter 6, standard crop evapotranspiration](https://www.fao.org/4/X0490E/x0490e0b.htm).
- [Egyptian Ministry of Agriculture / Agricultural Research Center, Sorghum bulletin 1393/2020, original document hosted by Misr Elzraea](https://misrelzraea.com/wp-content/uploads/2024/03/%D8%A7%D9%84%D8%B0%D8%B1%D8%A9-%D8%A7%D9%84%D8%B1%D9%81%D9%8A%D8%B9%D8%A9-%D9%86%D9%87%D8%A7%D8%A6%D9%8A_compressed.pdf), printed page 18. This dated guidance requires current local applicability review.
- [Chronos-2 model card](https://huggingface.co/amazon/chronos-2) and [AutoGluon Chronos tutorial](https://auto.gluon.ai/stable/tutorials/timeseries/forecasting-chronos.html). Documentation supports a candidate experiment, not proven performance on these laptops or at Sakha.
