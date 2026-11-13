# Astra implementation handoff — pending blueprint approval

Current assignment override, confirmed by Amr 2026-11-13: [team roster](../team.md) governs ownership. Amr + Astra own planner/generation/Promise Test/tests; Yahya owns FastAPI/shared contracts and Fieldlight React; Mahmoud owns historical evaluation, with no new ML training; Refaat / Ahmed owns KB/data/climatology and optional bounded Ridge. No trained forecast is required for P0. Shared API approval remains pending.

**Read this if…** you're building the planner screens in the frontend.

Status: Proposed  · Owner: Amr. Last reviewed .

13 November coordination update: Amr/Astra own the sole planner implementation. The [deadline execution package](../ml/plan.md) reuses Refaat's daily baseline and assigns optional bounded Ridge work to Refaat / Ahmed; it creates no competing planner. Latest user authorization governs coding. Keep the shared core interfaces below; future backend integration does not block standalone work.

Use only after Amr approves [FINAL_PLANNER_BLUEPRINT.md](blueprint.md) and applicable implementation timing. Do not start from this handoff alone. This document specifies frontend work; it does not assign Astra changes to Amr + Astra's rules, Yahya's schemas, Refaat's evidence or Mahmoud's metrics.

## Start condition

1. Read AGENTS and Yahya's existing backend documentation. Amr confirmed that backend work is documentation/architecture, not implemented code. Do not wait for a running backend.
2. Read API_CONTRACTS §0, BACKEND_DESIGN, REFERENCE_SCENARIO, the blueprint decisions D01–D10 and the approved Fieldlight Hybrid artifacts under `work/ux-phase-3/`. Preserve botanical arched season cards, existing tokens, typography and responsive direction. Do not replace them with dashboard tiles or restyle the science experience.
3. Use blueprint §9.1's standalone shared Pydantic contracts and exported JSON schemas as the initial type source; replace the transport binding with generated OpenAPI when the HTTP adapter exists. No separate handwritten scientific response schema. Contract review is bounded to the listed deltas, not another architecture session.
4. Use an isolated branch/worktree; coordinate shared-file ownership. No commits/pushes/deployment without separate instruction.

## Modules and deliverables

**Standalone-first integration assignment:** after approval, Astra may implement the integration driver at `packages/meg-core/src/meg_core/cli.py` and its integration tests, using Amr + Astra/Refaat/Mahmoud's public functions in blueprint §9.1. Define `python -m meg_core.cli plan --release PATH --input SNAPSHOT.json --output RESULT.json` and `replay --release PATH --input RESOLVED_PLANS.json --policy POLICY.json --output REPLAY.json`. Validate input with shared schemas, write actual results to a new output path, reject overwrite, return nonzero on invalid input/release, and return zero with explicit unavailable status for legitimate missing scientific capability. Never implement replacement rules in the driver. Tests run directly against packages without FastAPI, SQLite, CUDA or model downloads.

For frontend development before HTTP exists, use an injected `PlannerClient` interface with `catalogue`, `prepareScope`, `createScenario`, `reviseScenario`, `promiseTest`, `replay`, `saveEvidence`, and `getEvidence` methods matching the documented request/response schemas. An explicitly labelled development adapter can load real standalone result exports; unsupported server persistence returns unavailable. It must not masquerade as integrated save or manufacture scientific results. The HTTP adapter later uses the same interface. This permits coding now after approval while preserving the final real-backend acceptance requirement.

| Module | What Astra implements | Boundary |
|---|---|---|
| `frontend/src/services/api.ts` and generated types beside it | Typed catalogue, scope-preview, scenario create/revise, Promise Test, replay and evidence save/read requests; abort and active-reference guards | Types generated from Yahya's Pydantic/OpenAPI; no independent wire schema |
| `src/app/` and `src/hooks/` | Reducer/context for unconfirmed draft, confirmed snapshot, pending request, current results and selected investigation | Material edits invalidate result/card/audio locally; locale-only edits preserve revision |
| `src/features/farmer-intake/` | Two entry choices: check my rotation / explore from my needs; four slots, goals, context, crop permissions, protected commitments and explicit unknowns | Scope from server KB; no hardcoded dates, crop duration defaults or automatic lock removal |
| `src/features/season-timeline/` | Fieldlight botanical arched cards, connected four-season path, visible commitments, complete spoken dates, unknown endpoint treatment | Render canonical server dates; do not infer harvest/release in React |
| `src/features/promise-test/` | Current-plan conflict, up to two feasible alternatives, separate review investigations and rejected diagnostics; edit counts and search completeness | No merged suitability score, no success styling for review, no status computed from weather |
| `src/features/season-replay/` | Historical evidence panel with comparison basis, shared years, duration, Tmax mean/max, descriptive thresholds, ET0 totals/rates, exclusions, source access | All metrics from backend; no fake charts, inferred irrigation savings or aggregation of daily quantiles |
| `src/features/evidence-card/` | Explicit Save review draft, actual save progress/error, persisted reload and current/superseded indicator | A rejected plan saved as draft remains rejected; no implied recommendation approval |
| `src/features/forecast/` | Separate available/unavailable/stale/not_applicable display using current daily contract; existing negative model finding where relevant | Weekly research data have no approved runtime endpoint; do not synthesize a weekly UI API |
| `src/i18n/`, shared controls | UI chrome translations, RTL/LTR layout, date bidi isolation, confirm/change/repeat/back; speech status and touch recovery | Backend owns scientific explanation text/speech and typed parameters |

## Required interaction sequence

Goal entry must ask what can change and what must stay. Show a short source-labelled scope readback, including trial-template assumptions and unresolved facts. Explicit confirmation precedes `POST /scenarios`; silence or recognition alone never confirms. The user need not select each crop/date manually, but must authorize the search scope.

Request Promise Test against the server revision. Keep current plan, review investigation and farmer-adopted draft distinct. Inspecting a candidate does not adopt or approve it. Adoption creates a working draft; confirmation creates a new revision and reruns checks. MVP lock editing is unavailable until the approved acknowledgement flow exists; show the reason rather than silently changing a protected fact.

Open NASA evidence only for supported intervals. Put `hypothetical_review` and plan status beside the comparison heading and in spoken text. Show scheduled days and ET0 mm/day beside total mm. Use labels equivalent to “historical days at or above 35°C,” never “heat damage probability.” Null metrics display an understandable reason, not zero, empty bars or placeholders resembling predictions.

Saving calls the real backend and reports success only after an acknowledged persisted card. A network or database failure leaves an unsaved draft and retry path. Stop old speech on material edit, language switch, cancellation or stale response. Never play a previous revision's takeaway as the current plan.

## Interfaces and invariants

- Use `/api/v1` and scenario-scoped replay/card endpoints from BACKEND_DESIGN §5, not older reserved alternatives.
- Respect single `revision` and `data_release`. Reject late responses whose active scenario/revision/release no longer match; cancellation alone is insufficient.
- Preserve `Fact.value=null`, unit, unknown reason, origin, evidence status, confirmation status and source refs. Confirmation is not scientific verification.
- Use statuses exactly `rejected`, `needs_review`, `feasible`. Display separate `feasible_alternatives`, `review_investigations`, `rejected_candidates` and search metadata.
- UH-001: current rejected, May 28 and June 1 review-only, zero feasible alternatives, no fabricated downstream conflicts, forecast not applicable, review save only.
- SB-001 full plan is blocked until Yahya supplies it; never fill its missing seasons from UH-001. A period-only diagnostic must be visibly named as such.
- Keep fixture origin audible/visible. A non-fixture request must call the generic KB-driven backend, not a fixture-result map.
- No real farmer records to a public unauthenticated deployment. No transcript logging or browser-embedded service keys.

## Acceptance / Definition of Done

Run real frontend/backend integration for catalogue → needs/scope → explicit confirmation → Promise Test → source-backed replay → saved/reloaded review card. Run UH-001 and a non-fixture catalogue-generated case. Verify no scenario ID branches in frontend planning behavior. Test stale revision, missing weather, no candidates, multiple review candidates, unavailable forecast, denied mic, interrupted audio, failed save and language switching.

Inspect actual application in Arabic RTL and English LTR at phone and desktop widths, with keyboard and touch-sized controls. Check arched card layout, legibility, focus, status wording and source/unknown labels. Preserve the approved identity. Use existing design/testing skills selectively; no new design system or state dependency without approval.

Run available typecheck/lint/build and relevant component/integration tests. Record exact commands and results. Browser validation of rendering is not farmer usability evidence; a no-reading comprehension claim needs actual participants and documented assistance. Missing dynamic audio is an accessibility limitation, even when touch works.

Deliver reviewed frontend diff, real API verification evidence, screenshots of both language layouts, unresolved issues and concise PROJECT_STATUS update. No scientific values may be invented to satisfy a screen. If core integration is incomplete, stop optional animation/forecast embellishment and report the actual gap.

## Work order

1. API boundary, reducer, Fieldlight shell and catalogue intake.
2. Goal/scope confirmation, real Promise Test and UH-001 states.
3. Generic KB candidate review and selection; source/unknown explanations.
4. Paired historical evidence with correct duration and basis labels.
5. Real review-draft save/reload, audio consistency and failure recovery.
6. Bilingual rendered integration checks and demo rehearsal.

Estimated frontend effort: 10 focused person-hours plus shared integration/testing; standalone CLI adapter and contract tests add approximately 2 hours if assigned to Astra. First deliverable is the tested standalone integration adapter, then the six frontend steps above. If time fails, reduce optional display detail; retain the complete honest journey and expose unavailable capabilities.
