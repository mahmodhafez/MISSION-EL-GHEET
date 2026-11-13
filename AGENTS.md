# MISSION EL GHEET: agent and contributor guide

This file is the **only** project instruction file. Codex and Antigravity read it directly; Claude
Code reads it through `CLAUDE.md`. Don't create `GEMINI.md`, `.cursorrules`, `.agents/rules/` or
any other tool-specific rules file with different content. Change this file instead, so every
agent follows the same rules.

## What this is

A bilingual (Egyptian Arabic RTL / English LTR), voice- and picture-first crop-rotation planner
for farmers near Sakha, Egypt, built for NASA Space Apps 2026. The farmer says what must stay
(e.g. "the berseem cut on 20 May"); a deterministic **Promise Test** checks four consecutive
seasons for conflicts, offers at most two evidence-supported alternatives, and compares them on
historical NASA POWER weather. ML forecasting is a separate, experimental side channel that can
never decide feasibility.

Stack (approved): React + TypeScript + Vite + Tailwind · FastAPI + Pydantic · SQLite · Python 3.12.
Shared domain logic is planned as a standalone `meg_core` package (see `docs/planner/blueprint.md` §9.1).

| Path | What lives there | Real code yet? |
|---|---|---|
| `backend/` | FastAPI app (`app/`), tests | No, empty placeholders |
| `frontend/` | React app (`src/features/*`) | No, empty placeholders |
| `ml/` | Shared-release builder (`tools/`), tests, future experiments | Builder + 3 tests |
| `data/validation/` | NASA POWER / ET0 audit and regeneration scripts | Yes, 16 tests |
| `data/local/` | Assembled data release (mostly git-ignored) | Partial, see `docs/status/ml-data.md` |
| `work/ux-phase-2/`, `work/ux-phase-3/` | Standalone HTML wireframes and the Fieldlight prototype | Yes (design artifacts) |
| `archive-snapshot/`, `work/*` (other) | Frozen evidence from the 13 Nov recovery snapshot | Don't edit |
| `docs/` | Everything written. Start at `docs/README.md` | n/a |

## Read before doing anything

1. `docs/rules/working.md`: how to work here (scope, honesty, science rules).
2. `docs/rules/git.md`: branches, commits, PRs. **Several people and agents share this repo.**
3. The status file for your area in `docs/status/`.

## Routing: if you're doing X, read Y

| If you're… | Read |
|---|---|
| Asking "is X built? what's next? who owns it?" | `docs/status/README.md`, then `docs/status/<area>.md`, then `docs/team.md` |
| Working on the backend / API | `docs/backend/backend-design.md`, `docs/backend/api-contracts.md` (§0 overrides the rest) |
| Wiring the planner or ML into the backend | `docs/backend/core-integration.md`, `docs/planner/blueprint.md` §9.1 |
| Working on planner rules or candidate search | `docs/planner/planner-spec.md`, `docs/planner/blueprint.md`, `docs/product/reference-scenario.md` |
| Building frontend screens | `docs/design/design.md` (interaction), `docs/design/fieldlight.md` (visual), `docs/planner/frontend-handoff.md` |
| Writing any farmer-facing words | `docs/design/design.md` §4 status language, `docs/product/product.md` |
| Touching weather, ET0, units, evidence | `docs/science/science.md`, `docs/science/data-spec.md` |
| Working on ML / forecasts | `docs/ml/plan.md`, `docs/ml/model-selection.md`, `docs/ml/dataset-manifest.md` |
| About to propose an idea | `docs/rejected.md`: check it isn't already turned down |
| Unsure what a term means (UH-001, P0, R1, Astra, LST…) | `docs/glossary.md` |
| Writing or reorganising docs | `docs/rules/docs.md` |

## Rules that cause the most damage when broken

- **Change only what was asked.** Don't edit another area's files, contracts or docs on the way.
- **Never invent science or results.** No made-up crop coefficients, dates, yields, savings,
  test results or "it works" claims. Unknown stays unknown. Say what you actually ran.
- **UH-001 is supposed to fail.** The reference farmer's current plan is `rejected`, R1/R2 are
  `needs_review`, and there are **zero** feasible alternatives. Don't "fix" this.
- **Shared contracts change only by agreement.** API schemas, `meg_core.contracts` and the
  data release need sign-off from every owner they touch (see `docs/team.md`).
- **Never push to `main` directly, never force-push, never commit data/model files or secrets.**

## Commands that exist today

```sh
python -I -S -m unittest discover -s data/validation -p "test_*.py" -v   # 16 tests; 13 skip without the validation ZIP
python -I -S -m unittest discover -s ml/tests -v                        # 3 tests
node work/ux-phase-2/check-wireframes-v3.cjs                            # wireframe smoke check
node work/ux-phase-3/check-hybrid.cjs                                   # Fieldlight prototype check
```

No app install/run commands exist yet. Add them here when the first app code lands.

## Facts worth knowing on day one

- `backend/` and `frontend/` contain only `.gitkeep` files. Docs once assumed backend code
  existed when it didn't; check the tree before you believe a doc.
- The big evidence ZIP (`docs/VALIDATION_ARTIFACTS.zip`, ~470 MB) and model weights are **not in
  git**. Request them from Amr/Refaat (`docs/archive/handoff-/ARTIFACT_TRANSFER.md`).
- Many older docs contain Windows paths from Amr's machine (`C:/Users/Amr Hany/...`). They are
  history, not paths you should expect to exist.
- Status words have exact meanings: `feasible | rejected | needs_review` for plans;
  `verified | proposed | open` for evidence. Don't add a vague `valid` or `ok`.
- ET0 is reference atmospheric demand. It is not irrigation water use.
- Older docs are verbose and say "not authorized" a lot. Current authority is `docs/status/`,
  `docs/decisions.md` and the specs listed in `docs/README.md`.

## Before you finish a task

Update `docs/status/<area>.md` in the same commit as the code: what changed, its date, and what
you actually verified. If you learned a durable fact, put it in the matching topic file and date
it. Don't grow this file; it's a router.
