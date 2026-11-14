# Status: backend / API

**Read this if…** you're asking "is the API built? what's next on the backend?"

**As of 2026-11-13**, inspected base `70891af`. Owner(s): Yahya. Implementation pending unless explicitly verified below.

---

## Built and verified (14 Nov 2026, branch `backend/milestone-1`)

FastAPI app in `backend/app/` around the real `meg_core` planner (`packages/meg-core`, merged in via `chore/app-integration`):

| Endpoint | State |
|---|---|
| `GET /api/v1/health`, `GET /catalogue` | Real. Catalogue = crops/profiles of the loaded KB |
| `POST /scenarios`, `GET /scenarios/{id}`, `POST /scenarios/{id}/revisions` (`expected_revision`, 409 on conflict) | Real, SQLite (3 tables, WAL) |
| `POST /scenarios/{id}/promise-test`, `GET /results/{id}` (with `current`) | Real planner: scope preview → explicit confirmation → `service.plan`; stored |
| `POST /scenarios/{id}/evidence-cards`, `GET /evidence-cards/{id}` | Saves a **review draft**; plan status unchanged; refuses a result from an old revision |
| `POST /speech/interpret` | Gemini strict extraction + backend validation when `MEG_GEMINI_API_KEY` is set; otherwise `unavailable` |
| `POST /scenarios/{id}/replay`, `GET /forecast`, `POST /speech/tts` | Honest statuses: `unavailable` / `not_applicable` / `not_generated` until replay, bundle and audio exist |

- **Input shape (proposed):** requests carry the planner's own JSON (`snapshot`, `exploration`, `confirm_exploration`), decoded by
  the same codec as `planner_cli.py`. Shared Pydantic contracts and the app-answers → snapshot mapping are still to do.
- **Data release:** the UH-001 planner fixture KB, labelled `runtime_release: false`. No runtime agronomy KB exists yet (Refaat).
- **ML parts** (replay, forecast, new crops) are stubbed by agreement (14 Nov): new crops arrive through the KB; the 8-crop
  expansion on `planner/crop-expansion-assessment` is research-only and not wired.
- **Verified:** `pytest` 12 passed, including the golden test that the API result for UH-001 equals the planner CLI output
  (rejected, `sowing_before_protected_cut`, cut preserved, 0 feasible, 2 needs_review, search incomplete). A live uvicorn run
  answered health and the UH-001 Promise Test the same way. Not verified: a real Gemini call (no key used), load, auth.
- **Supply chain:** `backend/requirements.lock` (exact + sha256, 23 packages incl. pip 26.2.2), `backend/pip.conf`
  (14-day minimum age, wheels only, hashes required). Rules: [dependencies.md](../rules/dependencies.md).

## Next up

| # | Task | Notes |
|---|---|---|
| 0 | Get [ML contract](../backend/ml-contract.md) reviewed by Amr/Refaat/Mahmoud; deliver `contracts/forecast_bundle.v1.schema.json` + examples | Optional forecast follow-up; must not block P0 planner/history |
| 1 | Reconcile [backend design](../backend/backend-design.md) with `meg_core` ([blueprint §9.1](../planner/blueprint.md)) | Backend becomes thin adapters around `meg_core` planner/climate. Resolve Q3, Q4 in [overview](README.md). |
| 2 | Fold API §0 into the body of [api-contracts.md](../backend/api-contracts.md) | Remove superseded `plan_version`, idempotency, sessions, old endpoint names. Q6. |
| 3 | ~~Skeleton, SQLite store, `/health`, `/catalogue`~~ done 14 Nov; still to do: OpenAPI → TS types, frontend HTTP adapter, app answers → planner snapshot mapping | Backend design §12 step 1 |
| 4 | ~~Scenario endpoints + `promise-test` with storage~~ done 14 Nov; still to do: bilingual template rendering (D4) | §12 step 4 |
| 5 | Replay, then evidence cards; `/speech/interpret`, `/speech/tts`; forecast from bundle | §12 steps 5–8 |
| 6 | Voice audio: pick voices, write `build_prompt_audio.py`, generate once templates and scenarios are final | [voice-generation.md](../backend/voice-generation.md) (proposed 13 Nov). Provider ElevenLabs, offline only, decided 13 Nov. `/speech/tts` serves pre-generated files only. Nothing generated yet. |
| 7 | `/speech/interpret` with **Gemini strict extraction** (decided 14 Nov): schema, backend validation, Egyptian Arabic test set; settle the multi-proposal response change | [backend design §8.3](../backend/backend-design.md#83-interpretation-d6-gemini-extraction). Model ID to verify. Audio-to-Gemini still open. ElevenLabs generation/review moved to Moaaz (14 Nov). |

## In flight

Docs cleanup on branch `cleanup/yahya-preintegration` (not merged).

## Built and verified

Nothing. `backend/app/*` and `backend/tests/` contain only `.gitkeep`.

## Designed and approved, not built

- Architecture (11 Nov), backend design D1–D8 (12 Nov), API contracts v1 + §0 MVP revision (12 Nov).
- 5 first-slice endpoints + later reserved endpoints, error envelope, 3-table SQLite.
- [Core integration contract](../backend/core-integration.md): how the backend calls `meg_core` and Refaat's `climate_data`.

## Known problems

- Backend design §2 module tree and §12 build order predate the `meg_core` decision (13 Nov).
- API contracts mix superseded and current text (see Q6).

## Open questions

See Q3, Q4, Q6, Q11 in the [overview](README.md).

Confirmed assignment update, 2026-11-13: [team roster](../team.md) governs current ownership. FastAPI and Fieldlight Hybrid are chosen; shared API approval is pending. No trained forecast is required for P0. Recovered NASA/climatology subset is local and Git-ignored; Phase 3 frontend assets await safe transfer.
