# Status: planner (`meg_core`)

**Read this if…** you're asking "does the Promise Test / candidate search exist?"

**As of 2026-11-13**, base `a832b6b`, Milestone 1 on `planner/promise-test`.
Owner(s): Amr + Astra. Milestone 1 evaluator implemented; shared-contract integration pending.

---

## Next up

1. Yahya approves and binds shared contracts; Refaat supplies the reviewed loaded KB.
2. Amr reviews Milestone 1. Candidate generation/service orchestration waits for explicit
   Milestone 2 authorization; neither was implemented here.

## In flight

Milestone 1 worktree: `tmp/planner-promise-test` beneath the recovery checkout. Based on the
fetched recovery branch `a832b6b`; fetched `origin/main` remains `70891af`. No open PRs were
found at task start. Milestone 1 is prepared for the authorized feature-branch commit and push; recovery checkout is preserved.

## Built and verified

- Built 2026-11-13: `packages/meg-core/src/meg_core/planner/constraints.py`, with private
  immutable views, structural validation, lock/occupancy/preparation predicates, finite
  source-backed calendar/window/field/rotation predicates, mandatory coverage and status reduction.
- Verified 2026-11-13: **43 focused unittest tests passed, 0 failed, 0 skipped**, using local
  CPython **3.13.5** with `-I -S`; see [call boundary and test command](../planner/planner-spec.md#milestone-1-implementation-boundary-2026-11-13).
- Also checked: source/test byte compilation, Python 3.12 grammar parsing and whitespace in
  all nine Python files; tracked documentation diff whitespace. Recovery checkout stayed clean.
- UH-001: P0 `rejected`, May 20 cut retained, `sowing_before_protected_cut` first; May 28 and
  June 1 fixtures `needs_review`; **zero feasible repairs**. Changed S2 endpoints remain unknown.
  No invented S2→S3/S3→S4 failure. Soil/drainage, irrigation, cultivar, stages, sorghum and feed
  review reasons remain present. The recovered S1 sowing date is blank and stays unknown.
- All-known positive evidence is isolated, explicitly synthetic test data. Empty KB/rule/topic
  registries cannot make a plan feasible. No source research or runtime agronomic release was created.

## Built, not verified

- Python 3.12 execution: no local interpreter found; no interpreter or tool was installed.
- Shared Pydantic/JSON round-trips, HTTP adapters, loader integration and adapter-level forecast
  invariance remain untested because those implementations are absent. The evaluator's imports
  and input views are structurally independent of forecasts, weather, I/O and ML.

## Designed/approved, not built

- [Planner spec](../planner/planner-spec.md): generation, scope and service orchestration remain unimplemented.
- [Blueprint](../planner/blueprint.md): shared contracts, release loaders and integrated demonstration remain pending.
- [Agronomy KB draft](../planner/agronomy-kb.v0.1.json) + [evidence ledger](../planner/agronomy-evidence.md). KB not yet promoted to runtime.

## Known problems

- SB-001 full definition and `CLIMATE_AWARE_PLANNER.md` are missing from the repo.
- No second evidence-backed scenario with a feasible alternative exists yet (research goal).
- No loaded, approved agricultural KB is available. The evaluator consumes private in-memory
  rule views; it does not load or promote `agronomy-kb.v0.1.json`.
- Quantified production requirements remain explicit unknowns: no supported production predicate
  exists in the supplied release. Hard requirements prevent feasibility; soft feed questions do not.

## Open questions

- Yahya: bind the private views to `meg_core.contracts`, confirm `Explanation.params` versus
  `parameters` (internal code follows API §0's `params`), bind the correct current/candidate
  `plan_ref`, and map normalized slot labels/field paths/preparation units. No public Pydantic
  types, HTTP schemas or contract files were added or changed.
- Refaat + Yahya: agree the loaded KB-to-predicate mapping, mandatory-topic coverage and source
  approval gates. Source/hash validation stays in Refaat's loader. Registry additions require
  authored explanation templates; this code renders no natural-language advice.
- Yahya: later test identical agricultural results with forecast bundles present, missing,
  invalid and unavailable through the real adapter. No fabricated integration test is claimed.
