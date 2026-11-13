# Status: backend / API

**Read this if…** you're asking "is the API built? what's next on the backend?"

**As of **, last commit `0122e92`. Owner: Yahya. If this is far behind `git log`, trust git.

---

## Next up

| # | Task | Notes |
|---|---|---|
| 0 | Get [ML contract](../backend/ml-contract.md) reviewed by Amr/Refaat/Mahmoud; deliver `contracts/forecast_bundle.v1.schema.json` + examples | Unblocks the ML team |
| 1 | Reconcile [backend design](../backend/backend-design.md) with `meg_core` ([blueprint §9.1](../planner/blueprint.md)) | Backend becomes thin adapters around `meg_core` planner/climate. Resolve Q3, Q4 in [overview](README.md). |
| 2 | Fold API §0 into the body of [api-contracts.md](../backend/api-contracts.md) | Remove superseded `plan_version`, idempotency, sessions, old endpoint names. Q6. |
| 3 | Skeleton: `pyproject` (uv), `core/`, `schemas/`, SQLite store, `/health`, `/catalogue`, OpenAPI export → TS types | Backend design §12 step 1 |
| 4 | Scenario endpoints + `promise-test` with storage; bilingual template rendering | §12 step 4; needs planner P0 evaluator |
| 5 | Replay, then evidence cards; `/speech/interpret`, `/speech/tts`; forecast from bundle | §12 steps 5–8 |
| 6 | Voice audio: pick voices, write `build_prompt_audio.py`, generate once templates and scenarios are final | [voice-generation.md](../backend/voice-generation.md) (proposed 13 Nov). Provider ElevenLabs, offline only, decided 13 Nov. `/speech/tts` serves pre-generated files only. Nothing generated yet. |

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
