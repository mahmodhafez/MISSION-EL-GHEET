# MISSION EL GHEET — product requirements

**Read this if…** you need to know what the product must do: the seven functional requirements and recovery behaviour.

Status: Approved  · Owner: Amr. Last reviewed .

**REQUIREMENT** = intended behaviour · **VERIFIED** = checked evidence · **PROPOSED** = untested design · **OPEN** = unresolved. Acceptance criteria below have not been run yet.

## Purpose and scope

“Tell us what must stay. Hear what can change.” MISSION EL GHEET helps farmers protect essential commitments, understand conflicts across **four consecutive cropping seasons**, compare feasible alternatives and approve an understandable plan. The initial scope is one Egyptian pilot locality; **Sakha is the current research candidate**, not a confirmed deployment or a substitute for a farmer's actual field information.

The candidate catalogue retains **wheat, berseem, grain maize and grain sorghum**. Offering any crop requires applicable, evidence-labelled rules. Grain sorghum remains gated by unresolved local and cultivar suitability; retaining it does not authorize recommending it.

## Evidence boundary

**VERIFIED:** POWER record integrity, reference ET0 calculations, actual local LoRA training, parameter changes and adapter reload. **OPEN:** complete crop repairs, local ETc assumptions, Egyptian speech performance, independent no-reading usability and farmer benefit. The trained outlook has **not demonstrated useful forecast superiority** over the seasonal comparator. See the [current verdict](../reports/MISSION_EL_GHEET_Validation_Verdict.md).

## Illustrative farmer journey

**PROPOSED:** a farmer says, “البرسيم لازم يفضل” — the berseem must stay. Short questions establish its purpose, protected forage period, intended grain maize, later grain crop and fourth-season intention. Unknown facts remain unknown. Crop pictures and spoken dates support correction and confirmation.

The Promise Test checks whether the confirmed forage release, preparation interval and maize timing can coexist under applicable rules. It explains any supported conflict and its consequences for later seasons. It invents neither a release date nor a sowing deadline.

The farmer hears the current plan and any feasible alternatives, including what each changes and preserves. Historical comparison and, separately, any eligible experimental outlook explain their limits. The farmer can reject every alternative. Explicit approval produces matching spoken next steps and an Evidence Card. This is an illustrative flow, with no calculated results or promised savings.

## Seven functional requirements

### FR-01 — Complete accessible bilingual interaction

**REQUIREMENT:** full Arabic RTL and English LTR journeys, existing live speech recognition and audio playback in Egyptian Arabic and English, recorded prompts where practical, familiar pictures, short questions and large confirm/change/repeat/back controls. Picture/audio choices, typing and adviser assistance support recovery. Extracted facts require confirmation before agricultural rules run. Agricultural explanations use checked calculations and fixed bilingual templates, never free-form invented advice.

**Acceptance:** both languages complete intake through takeaway with identical facts. Speak complete dates and quantities with units; clarify ambiguity and negation. Silence never confirms. Arbitrary recognized text cannot modify locks or calculations. Test comprehension without reading or coaching; record assistance separately. See the [accessibility protocol](../reports/validation_accessibility_alignment.md).

### FR-02 — Commitments and local context

**REQUIREMENT:** collect the current four-season plan, grain/forage priorities, protected commitments, negotiable preferences, relevant soil information and irrigation constraints. Preserve the source and uncertainty of each material fact.

**Acceptance:** a protected forage requirement survives correction and translation. Unknown salinity remains unknown, never zero. Changing a relevant soil input changes eligibility, a review requirement or a sourced explanation. Published Sakha trial soils are labelled research profiles, never assigned to the farmer's field. Input meaning and provenance follow [DATA_SPEC.md](../science/data-spec.md).

### FR-03 — Promise Test

**REQUIREMENT:** explicit agricultural rules expose conflicts and propagate timing consequences through all four seasons. The farmer can explore a permitted date or priority change and hear what it changes downstream. Distinguish supported recommendations, observed trial dates and modelling assumptions. Protected commitments change only through separate, explicit farmer approval.

**Acceptance:** every reported conflict names the affected commitment, applicable rule and downstream consequence. A repair cannot silently shorten forage availability, change crop purpose or unlock a commitment. Unsupported rules produce uncertainty or a review gate, not invented agronomic certainty. Scientific applicability follows [SCIENCE.md](../science/science.md).

### FR-04 — Meaningful feasible alternatives

**REQUIREMENT:** display the current plan, including its conflicts, alongside **up to two** meaningfully different feasible alternatives on matching four-season picture timelines with spoken explanations. Enforce hard constraints first; explain farmer-relevant trade-offs while minimizing unnecessary crop substitutions and date shifts. Date-only changes are labelled timing variants. No unsupported overall farming score determines a winner.

**Acceptance:** every offered feasible alternative preserves protected commitments and passes all applicable checks. Differences and unresolved assumptions are spoken and visible. Zero or one alternative is valid; never fabricate a third strategy. Any proposed relaxation remains separate and needs explicit approval before reconsideration.

### FR-05 — Season Replay and soil-aware comparison

**REQUIREMENT:** compare candidates under the same consecutive historical NASA POWER weather blocks, using temperature, FAO56 reference ET0 and conditional ETc with sourced coefficients and stages. Present demand alongside duration and production commitments. Soil restrictions and sourced crop-family, legume, rooting and planned gap/cover indicators must influence eligibility or explanation.

**Acceptance:** comparisons identify shared weather periods and assumptions. Missing coefficients suppress unsupported ETc. Indicators never become measured soil improvement, nitrogen credit, yield or irrigation savings. Seasonal berseem estimates do not establish precise extra-cut demand. Equations and interpretation belong in [SCIENCE.md](../science/science.md).

### FR-06 — Required trained near-term experiment

**REQUIREMENT:** retain a meaningful trained-ML evaluation workstream, starting from the executed Chronos-2 LoRA experiment. Its targets are regional maximum temperature and calculated ET0 for seven explicitly dated days beyond issue date. An outlook may add context only to already feasible near-term actions; it cannot select or validate the four-season rotation.

**Acceptance:** report actual training and chronological comparisons against unchanged and simple baselines, with latency, uncertainty and decision-usefulness checks. A losing experiment remains reported; a better baseline may be used without claiming trained-model benefit. Demonstrating a trained-ML contribution that improves a concrete farmer decision remains required and unfulfilled. Evaluation details belong in [ML_EXPERIMENT.md](../ml/ml-experiment.md).

### FR-07 — Approved plan and matching takeaway

**REQUIREMENT:** explicit approval produces short spoken next steps and an Evidence Card for the **exact same plan version**, dates, units, sources, assumptions and outstanding checks. Written calculations remain available for an extension engineer; the farmer's takeaway must be understandable without reading.

**Acceptance:** replay, stop, return and help remain available. A critical correction invalidates dependent comparisons and approval until recomputed and reconfirmed. A failed save is announced. Revoking approval visibly and audibly returns the plan to unapproved; old audio cannot represent a new approved plan.

## Required recovery checks

| Condition | Observable acceptance behavior |
|---|---|
| Unknown critical input | Keep unknown; explain which conclusion cannot yet be made. |
| Missing weather | Identify affected periods; withhold unsupported comparisons and explain any permitted fallback. |
| No feasible alternatives | Explain the blocking constraints without silently relaxing them. |
| Stale outlook | Speak issue and target dates; withhold it from expired decisions. |
| Failed speech or denied microphone | Offer repeat, picture/audio, typing or adviser help; preserve confirmed facts. |
| Invalid or ambiguous unit/date | Ask for correction and replay the complete normalized value before confirmation. |
| Language switch | Preserve facts and approval state; reconfirm any materially corrected meaning. |
| Revoked approval or interrupted save | Announce the actual state; never present an unapproved or unsaved plan as approved and saved. |
| Cached demonstration | Label recorded or cached examples audibly and visibly; never present them as live recognition or calculation. |

No autonomous field or irrigation actuation is permitted. Scope excludes unrestricted chat, added HLS/IMERG features and a complete offline promise. Existing speech services remain candidates; this draft makes no provider, account, subscription or architecture commitment.
