# Status: planner (`meg_core`)

**Read this if…** you're asking "does the Promise Test / candidate search exist?"

**As of 2026-11-13**, last commit `2b83f5c` (M1, pushed). Milestone 2 is uncommitted on `planner/candidate-generation`.
Owner(s): Amr + Astra. M1 evaluator and M2 generation/service are implemented. Shared-contract integration is pending.
Resume and run instructions: [implementation handoff](../planner/implementation-handoff.md).

---

## Next up

1. Amr authorizes the Milestone 2 commit/push (manual CLI acceptance passed 2026-11-13).
2. Yahya binds `prepare_scope` / `service.plan` and the private views to shared contracts. Refaat supplies the reviewed loaded KB.

## In flight

Milestone 2 worktree: `tmp/planner-candidate-generation` (branch `planner/candidate-generation`, from `2b83f5c`).
All M2 code, tests, CLI and docs are uncommitted. Nothing is staged or pushed. The M1 worktree `tmp/planner-promise-test` is unchanged.

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

- Built 2026-11-13 (Amr + Astra): M2 `scope.prepare_scope`,
  `generate.generate`, `service.plan`, with permission binding, catalogue choices, lazy 256-budget search,
  dependency invalidation, stable IDs and reuse of the M1 evaluator. Also built: manual CLI `packages/meg-core/tools/planner_cli.py`
  with three fixtures.
- Verified 2026-11-13: **84 tests passed, 0 failed, 0 skipped** (43 M1 + 21 generation + 18 boundary + 2 CLI),
  using CPython 3.13.14 with `-I -S`. The 2 failures + 3 errors left in `test_search_boundaries.py` were fixed
  in the implementation ([details](../planner/implementation-handoff.md#tests-run-2026-11-13-cpython-31314-windows)).
  Python 3.12 grammar, `py_compile` and `git diff --check` are clean.
- UH-001 through generic generation: current `rejected` (`sowing_before_protected_cut`), May 28 and June 1
  `needs_review`, cut unchanged, **0 feasible**. The S4 maize choice is blocked, so search is `incomplete`.
- Manual acceptance 2026-11-13: Amr ran the [handoff CLI commands](../planner/implementation-handoff.md#manual-testing-windows-powershell)
  and reported that all of them passed.

## Built, not verified

- Python 3.12 execution: no local interpreter found; no interpreter or tool was installed.
- Shared Pydantic/JSON round-trips, HTTP adapters, loader integration and adapter-level forecast
  invariance remain untested because those implementations are absent. The evaluator's imports
  and input views are structurally independent of forecasts, weather, I/O and ML.

## Designed/approved, not built

- Search budget 256 and ordering `minimal-edits-v1-proposed` are **proposed**, pending team review.
- [Blueprint](../planner/blueprint.md): shared contracts, release loaders and integrated demonstration remain pending.
- [Agronomy KB draft](../planner/agronomy-kb.v0.1.json) + [evidence ledger](../planner/agronomy-evidence.md). KB not yet promoted to runtime.

## Known problems

- SB-001 full definition and `CLIMATE_AWARE_PLANNER.md` are missing from the repo.
- No second evidence-backed scenario with a feasible alternative exists yet (research goal).
- No loaded, approved agricultural KB is available. The evaluator consumes private in-memory
  rule views; it does not load or promote `agronomy-kb.v0.1.json`.
- Blocked exclusions repeat once per raw combination (noisy, not wrong).
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
