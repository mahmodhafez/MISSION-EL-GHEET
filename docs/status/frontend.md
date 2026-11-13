# Status: frontend

**Read this if…** you're asking "is the React app built? what screens exist?"

**As of 2026-11-13**, inspected base `70891af`. Owner(s): Yahya (implementation), Amr (final polish). Implementation pending unless explicitly verified below.

---

## Next up

| # | Task | Notes |
|---|---|---|
| 1 | Vite + React + TS + Tailwind shell; Fieldlight tokens; Arabic RTL / English LTR switch | Tokens: `work/ux-phase-3/tokens.fieldlight-hybrid.proposal.json` |
| 2 | Reference screens: welcome → crop picture question → protected-cut confirmation → four-season path | [design §7](../design/design.md), [frontend handoff](../planner/frontend-handoff.md) |
| 3 | Promise Test screen on labelled UH-001 fixtures, then against the real backend | Fixtures must be visibly labelled |
| 4 | Evidence Card, replay, forecast status | After backend milestones 2–4 |

## In flight

Nothing recorded.

## Built and verified

Nothing in `frontend/`. It contains only `.gitkeep` placeholders under `src/{app,components,features,hooks,i18n,services,styles}`.

## Standalone prototypes (not the app)

| Prototype | Path | Checks |
|---|---|---|
| Wireframe V2 | `work/ux-phase-2/season-path-wireframes.html` | `check-wireframes.cjs` passes (13 Nov) |
| Wireframe V3 (fullest interaction model) | `work/ux-phase-2/season-path-wireframes-v3.html` | `check-wireframes-v3.cjs`: 14 groups pass (13 Nov) |
| Fieldlight Hybrid (approved look) | `work/ux-phase-3/fieldlight-hybrid.html` | `check-hybrid.cjs` passes (13 Nov) |

These are minimal-DOM checks only. **No real browser, screen-reader, speech or farmer usability test has been done.**

## Open questions

Q1, Q7, Q8, Q10 in the [overview](README.md).

Confirmed assignment update, 2026-11-13: [team roster](../team.md) governs current ownership. FastAPI and Fieldlight Hybrid are chosen; shared API approval is pending. No trained forecast is required for P0. Recovered NASA/climatology subset is local and Git-ignored; Phase 3 frontend assets await safe transfer.
