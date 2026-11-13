# MISSION EL GHEET — implementation handoff

11 November 2026. The user approved [PRODUCT.md](PRODUCT.md), [SCIENCE.md](SCIENCE.md), [DATA_SPEC.md](DATA_SPEC.md) and [ML_EXPERIMENT.md](ML_EXPERIMENT.md) as working specifications. Their contents remain unchanged. This approval record resolves their earlier “pilot pending approval” wording; it does not convert assumptions or failed usefulness checks into validation.

## Approved decisions

- **Sakha** is the initial research locality. Published research soil stays distinct from a farmer's field.
- Preserve the intended **wheat, berseem, grain maize and grain sorghum** catalogue and all seven product features. Incomplete evidence means a labelled assumption or review-required option, never an unsupported validated recommendation. Feature removal requires user approval.
- Keep **Chronos-2 with LoRA**. Planning a bounded follow-up with proper baselines and fresh evaluation data is approved. Existing results, including negative results, remain immutable evidence. The core application must work independently of the forecast.
- Egyptian Arabic and English voice interaction remain core. Investigate an existing speech service and recovery approach; a final provider or paid subscription requires approval.
- Next stage is architecture, API contracts and Codex frontend planning. This handoff selects no framework, hosting arrangement, database or final provider and begins no application implementation.

## Team ownership

| Owner | Responsibility |
|---|---|
| Amr Hany Mahmoud | UI/UX and ML |
| Ahmed Mohamed Refaat | Data and ML with Amr |
| Karim Mohamed samy | Backend and planning engine |
| Yahya Alaaeldin Mohamed | Backend and planning engine |
| Moaaz Mostafa Elzaghawy | Motion graphics, storytelling and video |

Everyone collaborates across these boundaries. Mahmoud Ahmed Hafez was in the earlier six-person roster but has no assignment in this latest allocation; confirm his current participation/role rather than guessing.

## Evidence and deliverables

[VALIDATION_ARTIFACTS.zip](VALIDATION_ARTIFACTS.zip) preserves workspace-relative paths. Start with `REPRODUCE.md`, `ARTIFACT_MANIFEST.json` and `MISSING_ARTIFACTS.md` inside it. It contains original POWER responses, derived weather/ET0, tests, scripts, frozen environment record, model checkpoint and adapters, protocols, metrics, predictions and audits. Package checks verify file integrity; they do not rerun or validate the experiments anew. The four approved specifications are included as unchanged snapshots.

[REFERENCE_SCENARIO.md](REFERENCE_SCENARIO.md) defines fictional Uncle Hussein's complete four-season fixture. Its expected result includes a genuine input-date conflict and **zero validated repairs** with current evidence. Review-required timing variants are not recommendation successes. The fixture also exercises the absence of a relevant short-term forecast.

Verified foundation: saved NASA access/integrity, reference ET0 arithmetic and actual local adapter training/reload. The selected adapter did not demonstrate superiority over seasonal climatology in the limited assessment. See [ML_EXPERIMENT.md](ML_EXPERIMENT.md) for exact results. No completed end-to-end planner, local crop validation, independent no-reading usability or farmer benefit is claimed.

## Requirements for the architecture and API design

These are design constraints, not finalized endpoints or infrastructure:

1. **Separate responsibilities.** Speech/extraction proposes structured facts; explicit confirmation precedes planning. Deterministic constraints generate/check candidates. Historical replay calculates comparisons. Experimental forecasting is independently unavailable, stale or inapplicable without breaking intake, conflict explanations, comparison or saved takeaway.
2. **Preserve meaning and state.** Stable crop/purpose identifiers, explicit dates/time convention, units, unknown reasons, provenance, evidence status, protected commitments and negotiable bounds must survive every boundary. Never infer missing salinity, irrigation supply or yield. Farmer confirmation and scientific verification are separate fields.
3. **Version dependent work.** Identify scenario, confirmed plan, catalogue/rules, data release and calculation versions. Editing a material input invalidates dependent comparisons and approval. Responses must identify the version they describe so a late response cannot overwrite newer facts. Audio and Evidence Card must refer to the same plan version.
4. **Represent failure honestly.** Keep feasible, rejected and needs-review states distinct. Return rule-linked reasons, missing inputs and affected seasons. Zero alternatives is valid. Review drafts must not be styled or saved as validated recommendations. A user approval is not agronomic validation.
5. **Respect protected commitments.** Candidate selection follows hard constraints, relevant priorities, distinct trade-offs and minimal unnecessary edits. No combined best-farming score. Date-only changes are timing variants; lock relaxation requires its own explicit confirmation.
6. **Make comparisons reproducible.** Use identical historical blocks and method versions; retain exclusions and assumptions. Keep demand, duration and grain/forage requirements together. Forecast output must include issue/cutoff/target dates, provenance, uncertainty and experimental status. No forecast may create crop eligibility or silently alter locks.
7. **Limit data exposure.** Plan microphone consent, speech-service disclosure, credentials outside the browser, and retention decisions before connecting a provider. Do not upload real farmer recordings or records as part of architecture exploration. This does not prevent labelled synthetic demonstrations.

## Requirements for frontend planning

Provide native Arabic RTL and English LTR journeys with equivalent functionality. Use one short spoken question at a time, crop pictures with spoken names, editable spoken confirmations, large confirm/change/repeat/back controls and audio guidance. Written cards alone do not satisfy accessibility.

Show linked four-season picture timelines, protected commitments, supported conflicts and the effects of a permitted change. Explain trade-offs using checked calculation outputs and authored bilingual templates. Keep readable calculation details for the engineer and a short spoken takeaway for the farmer. Do not ask the farmer to understand ET0 notation to complete the task.

Plan microphone-denial, ambiguous Arabic crop/date/unit recognition, interruption, network failure, repeat and language-switch states. Offer picture/audio choices and adviser assistance as well as typing. Label recorded/cached demonstrations audibly and visibly. Preserve confirmed facts across recovery. Independent usability requires intended-user testing; no provider documentation establishes it.

## Priorities and unresolved gates

| Priority | Owner | Required next-stage outcome |
|---|---|---|
| 1. Shared contracts | Amr, Karim, Yahya, Refaat | Agree state/evidence/version semantics using UH-001 before implementation |
| 2. Crop evidence | Refaat with planning team | Source cultivar, stage, cutting, release/preparation, soil and sorghum applicability; retain unresolved rows |
| 3. Planner/replay specification | Karim and Yahya | Design constraint tests and paired replay acceptance cases, including no-repair and review-required cases |
| 4. Accessible interaction | Amr; Moaaz supports explanations | Plan bilingual prototype, speech trial and no-reading comprehension tests; no provider purchase yet |
| 5. Bounded ML protocol | Amr and Refaat | Specify lag/calendar baseline, tuning budget, fresh dates, skill/uncertainty thresholds and one eligible near-term decision before new training |
| 6. Story and demonstration | Moaaz with team | Show actual verified capability, visible assumptions and honest experimental labels |

Open scientific gates include field-soil information, applicable crop curves and irrigation constraints. The consumed July–October 2026 assessment cannot become a fresh test through repeated tuning. POWER archive vintages do not reconstruct historical operational availability. Source PDFs missing from the local package and non-portable environment dependencies are listed inside the ZIP; source links remain in the specifications/audits.

No new approval of architecture, provider, subscription, deployment or application implementation is implied. Stop after these handoff deliverables; the next discussion sets architecture, API contracts and frontend planning.
