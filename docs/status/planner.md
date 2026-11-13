# Status: planner (`meg_core`)

**Read this if…** you're asking "does the Promise Test / candidate search exist?"

**As of 2026-11-13**, inspected base `70891af`. Owner(s): Amr + Astra. Implementation pending unless explicitly verified below.

---

## Next up

Implementation order from [blueprint §9.1](../planner/blueprint.md):

1. `meg_core` contracts + package skeleton + schema round-trip tests.
2. Release/KB loaders.
3. Constraints/status + **UH-001 golden test** (P0 rejected, R1/R2 needs_review, 0 alternatives).
4. Scope preparation + bounded generator (budget 256).
5. Weather loader, block mapping, paired replay metrics.
6. Standalone plan → evaluate → replay JSON demo.

## In flight

Assigned to Amr + Astra; implementation pending. No planner package was found on any fetched remote branch during recovery. Coordinate unpublished local work before creating overlapping files.

## Built and verified

Nothing in this repo.

## Designed, not built

- [Planner spec](../planner/planner-spec.md) (11 Nov): dates, rules, search, UH-001 walkthrough.
- [Blueprint](../planner/blueprint.md) (12–13 Nov): architecture, D01–D10 (pending approval), packages.
- [Agronomy KB draft](../planner/agronomy-kb.v0.1.json) + [evidence ledger](../planner/agronomy-evidence.md). KB not yet promoted to runtime.

## Known problems

- SB-001 full definition and `CLIMATE_AWARE_PLANNER.md` are missing from the repo.
- No second evidence-backed scenario with a feasible alternative exists yet (research goal).

Confirmed assignment update, 2026-11-13: [team roster](../team.md) governs current ownership. FastAPI and Fieldlight Hybrid are chosen; shared API approval is pending. No trained forecast is required for P0. Recovered NASA/climatology subset is local and Git-ignored; Phase 3 frontend assets await safe transfer.
