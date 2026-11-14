# Planner implementation handoff (Milestones 1–2)

**Read this if…** you're continuing planner work, wiring the planner into FastAPI, or running the planner by hand.

Status: Draft · Owner: Amr + Astra · Last reviewed 2026-11-13.

---

## Resume in a new AI session

1. Work in worktree `tmp/planner-candidate-generation` (branch `planner/candidate-generation`),
   beneath the main checkout. Don't create another Milestone 2 branch. Don't reset or clean it.
2. Read `AGENTS.md`, [status](../status/planner.md), then this file.
3. Run the test command below. The expected result is **84 tests, 0 failures, 0 skips**.
4. Milestone 2 is committed and pushed (see [Worktree state](#worktree-and-commit-state)). Further commits, pushes, PRs or merges
   only on Amr's explicit authorization.

## Branches and commits

| Milestone | Branch | Commit | Remote |
|---|---|---|---|
| 1 · Promise Test | `planner/promise-test` | `2b83f5c` | pushed (`origin/planner/promise-test`) |
| 2 · Candidate generation + service | `planner/candidate-generation` | `a46500a` (on `2b83f5c`) | pushed (`origin/planner/candidate-generation`) |

## Callable interfaces (pure, standalone)

All modules live under `packages/meg-core/src/meg_core/planner/`. Put `packages/meg-core/src`
on the import path. Inputs and outputs are the **private** frozen dataclasses in `_types.py`, not shared contracts.

| Call | Purpose |
|---|---|
| `constraints.evaluate(plan, snapshot, kb) -> PlanEvaluation` | M1 Promise Test. The only source of `feasible / rejected / needs_review`. |
| `scope.prepare_scope(ScopeRequest(snapshot=…, choices=…, catalogue_choices=…), kb) -> ScopePreview` | Pure preview: canonical choices, readback issues, missing inputs, `scope_hash`. Never authorizes. |
| `generate.generate(snapshot, kb, SearchPolicy()) -> GenerationResult` | Bounded lazy search; each distinct candidate goes through `constraints.evaluate`. |
| `service.plan(snapshot, kb, SearchPolicy()) -> PlanningResult` | Current-plan evaluation, candidates split by status (≤2 feasible display groups), search coverage, exclusions. |

Authorization: `generate`/`plan` refuse exploration unless `snapshot.input.journey == "explore"`,
`exploration_confirmed is True` and `scope_hash` equals the preview hash for the same fact values,
choices and issues. The hash ignores fact `confirmation_status`, so a preview taken on unconfirmed
intake can be bound after the farmer confirms the same values. Generation itself still requires every fact
to be confirmed. Malformed input raises `_validation.InputValidationError(code, field_paths)`.

## Refaat KB adapter and twelve-crop catalogue (proposed, 2026-11-14)

Branch `planner/twelve-crop-catalogue` (worktree `tmp/planner-crop-catalogue`), built on `planner/crop-expansion-assessment`.
The adapter was copied byte-identical from the uncommitted worktree `tmp/planner-kb-adapter`, which was left untouched.
**Nothing here is scientifically approved.** Refaat's delivered KB (`crop-research-20261111-v1`) has 27 rules and
0 approved or enforceable ones.

| Call | Purpose |
|---|---|
| `kb_adapter.adapt(crops=, enforceable_rules=, kb_version=, data_release=, site_id=, season_labels=)` | Loader output → planner `KnowledgeBase`. Only rules Refaat's loader marks enforceable become rules. Everything else goes to `unmapped` with a reason. |
| `crop_catalogue.load_catalogue(doc)` | Validates [crop-catalogue.v0.1-proposed.json](crop-catalogue.v0.1-proposed.json). Refuses `feasibility_eligible` without approval, unknown levels, duplicates and non-proposed status. |
| `crop_catalogue.build_planner_kb(catalogue, refaat_crops=, enforceable_rules=, ...)` | Refaat profiles + proposed runtime profiles. Rules come only from the adapter. Rules in an unresolved conflict are held back. |
| `crop_catalogue.exploration_crop_ids(catalogue, purpose)` | Crops that may be **offered** for one purpose. The farmer must still confirm the scope. |

**Capability levels.** Each level is a separate approval.

| Level | Crops | Meaning |
|---|---|---|
| research record only | watermelon, strawberry, cantaloupe, harankash | Never a planner profile, so never shown in `available_crop_ids` and blocked if requested. |
| runtime profile | berseem (Refaat record, purpose `forage_or_seed_requires_review`) | Can bind only to a season of that exact purpose. |
| review candidate | wheat, grain maize, grain sorghum, rice, sugar beet, Egyptian cotton, faba bean; berseem via `berseem-forage-proposed` | May be offered. Without approved rules every result is `needs_review` or blocked. |
| feasibility eligible | none | Needs recorded approval. |

**Resolved as gates, not as science.**

- **Wheat window.** Refaat C01/E036 says "10 Nov to 30 Nov": a Global Yield Gap Atlas regional Nile-Delta calendar,
  read from a WUR *test* host. Ledger W1 says 15–30 Nov plus a conditional 10 Dec, from ARC bulletin 1449 2025/26 for
  old land. Different authorities. Both are kept verbatim as conflict `wheat-sowing-window`, and C01 is held from
  enforcement even if signed until the conflict is resolved.
- **Berseem purpose.** C07/E042 (Mansoura forage course) and C08/E043 (Fahl/Meskawi forage types) plus ledger B1 support
  a forage-specific *proposal*, `berseem-forage-proposed` (purpose `forage`, evidence `proposed`). Refaat must confirm
  forage vs seed and the Fahl or Meskawi type. Seed stays unsupported, and Refaat's own record is unchanged.

**Tests (2026-11-14, CPython 3.13.14).** `python -I -S -m unittest discover -s tests` in `packages/meg-core`:

- With `MEG_AGRI_KB` set to Refaat's `agricultural_kb.json`: **104 pass** (84 original + 9 adapter + 11 catalogue).
- Without it: 104 run, 3 skip.
- UH-001 on catalogue profiles: still `rejected` (`sowing_before_protected_cut`), May 28 / Jun 1 `needs_review`,
  20 May cut unchanged, release unknown, 0 feasible.
- Mutation checks confirmed both gates can fail.

**Search (P1, measured on the real engine).** Purpose filtering cuts grain-season offers to 4 crops and forage to 0.
Every case ran in ≤15 ms. With crop locks removed, crops lacking sowing evidence are blocked, and blocked combinations
**consume the 256 budget** (254/256 in one case), so the result reads `candidate_budget` rather than "evidence missing".
Proposed separately, not implemented: report an evidence-blocked value once in the scope preview instead of once per
combination. No engine change was made.

**Awaiting Yahya.** Rule-type → topic map (only `sowing_window` → `sowing_support`), `field.<key>` paths, and the
`winter-start-year-v1-proposed` year/leap convention. All are internal proposals, not a published contract. Note that
crops that become planner profiles appear in the frontend through `scope.available_crop_ids`.

## What Milestone 2 does

- **Permissions.** Explore only explicit `ExplorationChoice` / `DateRangeChoice` / `CatalogueChoice`
  records on `crop_id`, `profile_id` and `sowing_date`. Purpose, locks and unpermitted fields stay fixed. The preview
  reports choices that conflict with a protected crop (`excluded`) or name a value absent from the
  catalogue (`blocked`).
- **Generation.** Catalogue-driven, with no crop, scenario or date constants in production code. Minimal
  edited-slot layers first, lazy iteration, and duplicate merging with provenance.
- **Dependency invalidation.** A changed crop, profile or sowing resets harvest, crop end, release and
  outgoing preparation. They are rebuilt only from an exact verified `CalendarRule` or an authorized
  `PlantingTemplate`, otherwise left null with `endpoint_mapping_missing`. Protected cuts and adapter-declared
  `IndependentFact`s are kept. Later seasons never slide automatically.
- **Search coverage.** `raw_count`, `evaluated_count`, duplicates, exclusions, blocked branches,
  `uninstantiated_choice_ids` and `limit_reason` (`candidate_budget` → `uninstantiated_choices`). Exact exhaustion at the budget
  is `complete`. One further tuple means `incomplete`.
- **Identity.** `candidate-<sha256>` over input context, KB evidence (ref order ignored, versions
  counted), ordering version and canonical plan.

## Policy approval status

| Item | Value | Status |
|---|---|---|
| Raw-combination budget | 256 (`SearchPolicy.raw_budget`) | **Proposed**, pending team review |
| Choice limits | 32 records, 32 values per choice | Proposed engineering defaults |
| Ordering | `minimal-edits-v1-proposed`: edited seasons → decisions → unknown displacements → days → canonical plan | **Proposed**. Every result carries `policy_approval: pending_team_review` |

## Tests (run 2026-11-13, CPython 3.13.14, Windows)

```powershell
cd packages\meg-core
python -I -S -m unittest discover -s tests -v
```

| File | Tests | Result |
|---|---|---|
| `test_constraints.py` + `test_constraint_edges.py` (M1) | 27 + 16 = 43 | pass |
| `test_generation.py` | 21 | pass |
| `test_search_boundaries.py` | 18 | pass |
| `test_manual_cli.py` | 2 | pass |
| **Total** | **84** | **0 fail, 0 error, 0 skip** |
| `test_kb_adapter.py` + `test_crop_catalogue.py` (2026-11-14) | 9 + 11 | pass with `MEG_AGRI_KB`; 3 skip without it |

Also checked: all 21 package/test/tool files parse with Python 3.12 grammar (`ast.parse(feature_version=(3, 12))`),
`py_compile` passes and `git diff --check` is clean. **Python 3.12 runtime: not run.** No 3.12 interpreter is installed.

Fixed 2026-11-13 (the 2 failures + 3 errors Astra left in `test_search_boundaries.py`):
`prepare_scope` now type-checks the snapshot before using it (2 errors). The scope hash binds values,
not confirmation status (1 error). Evidence identity sorts `source_refs` (1 failure). The preview reports
protected-crop and catalogue readback issues (1 failure). No assertions were weakened. M1's
`test_constraints.py` import allow-list was widened by Astra to the stdlib modules `hashlib/json/heapq/itertools`
and gained a ban on `open/exec/eval/__import__` calls.

## UH-001 (generic generation, `GeneratedReference` test and `uh001.json`)

Current plan **rejected**, first reason `sowing_before_protected_cut` (May 15 sowing vs protected
2027-05-20 cut). The two investigations, S2 sowing **2027-05-28** and **2027-06-01**, come from the
exploration input and are both **needs_review**. The cut is unchanged and S2 endpoints become unknown.
**0 feasible.** Raw 5, evaluated 2. The S4 maize choice is blocked 3× (`profile_binding_unavailable`), so search is
`incomplete / uninstantiated_choices`.

## Manual testing (Windows PowerShell)

These work from any folder. The code exists only in this worktree, so commands using relative
paths from the main checkout fail with "can't open file". Set `$M` once per PowerShell window and
keep each command on one line.

```powershell
$M = "C:\Users\Amr Hany\Downloads\MISSION-EL-GHEET\tmp\planner-candidate-generation\packages\meg-core"
python -I "$M\tools\planner_cli.py" check   "$M\tools\fixtures\uh001.json"                  # 1. UH-001 Promise Test only
python -I "$M\tools\planner_cli.py" plan    "$M\tools\fixtures\synthetic-four-season.json"  # 2. generic 4-season generation
python -I "$M\tools\planner_cli.py" plan    "$M\tools\fixtures\uh001.json" --details        # 3. full result: reasons, changes, sources, coverage
python -I "$M\tools\planner_cli.py" plan    "$M\tools\fixtures\synthetic-mixed.json"        #    feasible + review + rejected + blocked
python -I "$M\tools\planner_cli.py" preview "$M\tools\fixtures\synthetic-mixed.json"        #    scope readback only
python -I "$M\tools\planner_cli.py" plan    "$M\tools\fixtures\synthetic-mixed.json" --no-confirm   # refused: exploration_not_confirmed
python -I "$M\tools\planner_cli.py" plan    "$M\tools\fixtures\uh001.json" --json > uh001-result.json  # 5. exact fields
python -I -S -m unittest discover -s "$M\tests" -v                                          # 84 tests
python -I "$M\tools\build_fixtures.py"                                                      # regenerate fixtures from test builders
```

Flags: `--details` lists every non-passing check and assumption. `--all-checks` also lists passes.
`--json` prints exact field values. Exit code 2 means the planner refused the input.

**4. Varying inputs.** Copy a fixture and edit it. Keys: `snapshot` (seasons, commitments, field_facts,
independent_facts, template permissions), `kb` (profiles, rules with a `"type"` such as `CalendarRule`),
`exploration.choices` (`{"type": "ExplorationChoice", "choice_id", "season_id", "field", "allowed_values"}`
or `{"type": "DateRangeChoice", "choice_id", "season_id", "start", "end", "step_days"}`),
`exploration.catalogue_choices`, `confirm_exploration` and `policy` (e.g. `{"raw_budget": 3}`). Setting
`confirm_exploration: true` stands in for the farmer's explicit confirmation. Unknown keys are refused.

Every check names its evidence status. Output from fixtures containing `SYNTHETIC-ONLY` evidence is
bannered SYNTHETIC. **Manual acceptance passed:** Amr ran these commands on 2026-11-13 and reported all passing.

## Limitations and dependencies

- **KB (Refaat).** No loaded, approved agricultural KB exists. Fixtures use SYNTHETIC-ONLY rules or UH-001's open
  review gates. No real calendar mapping exists, so real changed schedules stay `needs_review`.
- **Contracts (Yahya).** Private `_types.py` must be mapped to `meg_core.contracts` by the adapter.
  The mapping covers `ScopeRequest/ScopePreview/ScopeIssue`, `ExplorationChoice/DateRangeChoice/CatalogueChoice`,
  `IndependentFact`, `PlantingTemplate`, `SearchPolicy`, `Candidate/Change`, `SearchSummary` and `PlanningResult`, plus
  the M1 views. `plan_ref` stays `None` until the server binds it. The adapter must persist `scope_hash` and
  the release with the snapshot. No FastAPI route or shared contract was touched.
- **Historical evaluation (Mahmoud).** Not called and not needed. The planner has no weather, forecast or ML imports.
- **Known rough edges (not bugs against spec).** The same blocked reason is listed once per raw combination,
  so exclusions repeat. Same-context timing variants share one feasible display card by design. No second
  evidence-backed scenario with a feasible repair exists.

## Worktree and commit state

As of 2026-11-13, Milestone 2 is committed as `a46500a` and pushed to `origin/planner/candidate-generation`,
with a follow-up docs commit recording that state. It is not merged into `main` and has no PR yet.

## Next action

Open a PR from `planner/candidate-generation` when Amr asks. Then Yahya binds the interfaces above in the backend adapter.
