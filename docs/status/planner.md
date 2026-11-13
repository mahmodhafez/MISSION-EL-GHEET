# Status: planner (`meg_core`)

**Read this if…** you're asking "does the Promise Test / candidate search exist?"

**As of **, last commit `0122e92`. Owner: **disputed**, see Q1 in the [overview](README.md). If this is far behind `git log`, trust git.

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

Unknown. Docs say Amr/"Astra" may have a planner package on a separate branch or machine. **Not
visible in this repo.** Find out before starting so it isn't built twice.

## Built and verified

Nothing in this repo.

## Designed, not built

- [Planner spec](../planner/planner-spec.md) (11 Nov): dates, rules, search, UH-001 walkthrough.
- [Blueprint](../planner/blueprint.md) (12–13 Nov): architecture, D01–D10 (pending approval), packages.
- [Agronomy KB draft](../planner/agronomy-kb.v0.1.json) + [evidence ledger](../planner/agronomy-evidence.md). KB not yet promoted to runtime.

## Known problems

- SB-001 full definition and `CLIMATE_AWARE_PLANNER.md` are missing from the repo.
- No second evidence-backed scenario with a feasible alternative exists yet (research goal).
