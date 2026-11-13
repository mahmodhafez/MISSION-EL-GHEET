# Team and ownership

**Read this if…** you need the current assignment, module owner or reviewer.

Status: Confirmed by Amr, 2026-11-13. This roster supersedes earlier ownership assignments; historical records remain unchanged.

| Person | Owns | Implementation boundaries |
|---|---|---|
| **Amr + Astra** | Standalone deterministic planner, four-season candidate generation, Promise Test/agricultural constraints, planner tests, UH-001 regression and integration acceptance; ML coordination and final frontend polish | `packages/meg-core/src/meg_core/planner/`, `packages/meg-core/tests/`, `docs/planner/`; coordinate frontend polish with Yahya |
| **Yahya** | FastAPI backend lead; shared Pydantic/API contracts, routes, adapters, persistence/integration; Fieldlight React implementation; deployment coordination | `backend/`, shared `meg_core/contracts/`, `frontend/`, `docs/backend/` |
| **Mahmoud** | Historical NASA climate evaluator / Season Replay, Tmax and ET0 analysis, structured climate evidence and evaluator tests; coordinate interfaces with Yahya/Refaat | `meg_core/climate/{mapping,evaluate}.py` and evaluator tests under `packages/meg-core/tests/`; no new ML training unless explicitly reassigned |
| **Refaat / Ahmed** (Ahmed Mohamed Refaat — same person) | Agricultural KB validation/loader, scientific data engineering/source verification, existing climatology baseline, optional bounded Ridge experiment, scientific validation of ML outputs | `data/`, `meg_core/knowledge/load.py`, `meg_core/climate/load.py`, coordinated baseline/Ridge modules in `ml/src/meg_ml/`, `docs/science/` |
| **Moaaz** | Motion graphics, multimedia, crop/voice assets and final 30-second demonstration video | `media/`; coordinate presentation assets with Yahya/Amr |

Karim is not participating. Earlier references to his assignment do not authorize current work.
Module paths under `meg_core` are relative to `packages/meg-core/src/meg_core/`; they are implementation targets, not a claim that code exists.

## Decisions and review

- Amr decides product scope, visual direction and ML coordination; Refaat validates scientific meaning and data.
- Yahya owns shared API/Pydantic contracts; affected planner, climate, data and frontend owners review changes. The shared API contract awaits Yahya's final approval.
- FastAPI is the chosen backend. Fieldlight Hybrid is the approved frontend design.
- No trained forecast is required for P0. Historical analysis and agricultural validation remain independent of optional forecasts.
- Recovered NASA historical/climatology inputs are local and Git-ignored at `data/local/shared-20261113-v1/`; this is a verified subset, not a complete application release.
- Phase 3 frontend assets still need safe transfer from the original checkout, coordinated by Yahya/Amr.
- Planner, backend, React frontend and historical evaluator implementation are pending in the inspected repository. See [current status](status/README.md).
