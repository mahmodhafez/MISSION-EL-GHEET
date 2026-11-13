# Project status: overview

**Read this if…** you want the big picture: phase, deadline, blockers, and where docs contradict each other.
Per-area detail is in the files below; each area owner keeps their own file.

**As of **, last commit `0122e92` (recovery snapshot) + docs cleanup on
`cleanup/yahya-preintegration`. If this is far behind `git log`, trust git.

| Area | File | Owner |
|---|---|---|
| Backend / API | [backend.md](backend.md) | Yahya |
| Frontend | [frontend.md](frontend.md) | Yahya (implementation), Amr (polish) |
| Planner (`meg_core`) | [planner.md](planner.md) | Amr + Astra |
| ML and data | [ml-data.md](ml-data.md) | Amr + Refaat / Ahmed; Mahmoud owns historical evaluation |
| Design / UX | [design.md](design.md) | Amr |

---

## Where we are

**Specs are written; application code is not.** `backend/` and `frontend/` are empty
placeholders, and the `meg_core` planner package doesn't exist in this repo yet. What does exist and run:
the NASA POWER/ET0 audit scripts (`data/validation/`), the shared-data release builder (`ml/tools/`),
Refaat's climatology baseline package, and standalone HTML design prototypes (`work/ux-phase-*`).

Target: NASA Space Apps 2026 (14–15 Nov). Internal deadline per [ML plan](../ml/plan.md):
**14 Nov 12:00 Cairo** for a working app. See Q7.

## Launch blockers (cross-area)

| # | Blocker | Owner | State |
|---|---|---|---|
| 1 | First vertical slice: confirmed UH-001 → real Promise Test → bilingual conflict on screen, zero alternatives | Yahya + planner owner + Amr | Not started |
| 2 | `meg_core` contracts + UH-001 P0 evaluator | Planner owner + Yahya | Not started |
| 3 | Packaged `data_release` the backend can load at startup | Refaat | Partly assembled locally; see ml-data |
| 4 | Validation ZIP + `ML_HANDOFF.zip` transferred to whoever runs full checks | Amr / Refaat | Not in git; see [artifact transfer](../archive/handoff-/ARTIFACT_TRANSFER.md) |
| 5 | Speech: Web Speech API tried on a real phone in Egyptian Arabic | Amr | Not started |
| 6 | Demo plan: local laptop vs remote host | Amr + Yahya | Hosting not approved |

## Open questions and contradictions between docs

Answer these and record the answer in `../decisions.md`; don't settle them quietly in code.

| # | Question | What the docs say | Who answers |
|---|---|---|---|
| Q1 | Who builds the planner? | RESOLVED 2026-11-13: Amr + Astra; Karim is not participating. | Amr confirmed |
| Q2 | Mahmoud assignment | RESOLVED 2026-11-13: historical NASA evaluator / Season Replay; no new ML training unless reassigned. | Amr confirmed |
| Q3 | Planner code location | [Backend design §2/§12](../backend/backend-design.md) puts rules in `backend/app/planner/`; [blueprint §9.1](../planner/blueprint.md) (newer) puts them in `packages/meg-core` with backend adapters. Decision log follows §9.1. Backend design still needs updating. | Yahya (update doc) |
| Q4 | Where does the runtime data release live? | Backend design D8: committed `data/release/`. Dataset manifest: `data/local/shared--v1/` (git-ignored, partly force-added) | Yahya + Refaat |
| Q5 | Are blueprint decisions D01–D10 approved? | Blueprint says "proposed for Amr's review"; the 13 Nov ML plan builds on it as if approved | Amr |
| Q6 | API contract body vs §0 | §0 (12 Nov) overrides `plan_version`, idempotency keys, sessions/401/403, `/replays`, `/forecast-assessments`, but the old text is still in the body. Also `parameters` vs `params` (blueprint D08). | Yahya (fold §0 into body) |
| Q7 | Deadline vs event start rule | [Frontend milestone 1](../archive/frontend-milestone-1-.md): Space Apps project work may start only 14 Nov 09:00 local. ML plan: app due 14 Nov 12:00 Cairo, target "today" (13 Nov). Pre-event work could be an eligibility risk. | Amr |
| Q8 | Fieldlight approved? | RESOLVED 2026-11-13: Fieldlight Hybrid approved; Yahya implements React. Phase 3 assets await safe transfer. | Amr confirmed |
| Q9 | FR-06 (trained ML must improve a farmer decision) | Unmet. Blueprint D07 proposes waiving it as a hackathon acceptance condition. | Amr |
| Q10 | Who are "Astra" and "Sol"? | Frontend build workstreams in older docs, probably AI-agent sessions | Amr |
| Q11 | Speech TTS provider, hosting, data retention | None chosen or approved | Amr + Yahya |

## History

The pre-cleanup status log (146 lines of session notes, 11–13 Nov) is preserved at
[archive/project-status-.md](../archive/project-status-.md).

Recovery update, 2026-11-13: verified historical/climatology subset installed locally; canonical dataset IDs/dates restored. All remote branches inspected; no application implementation found. Shared schema/release and planner ownership remain unresolved. See [recovery evidence and decisions](../reports/2026-11-13-recovery.md).

Final team update, 2026-11-13: [confirmed roster](../team.md) supersedes historical ownership in specifications/recovery reports. FastAPI backend, React frontend, deterministic planner and historical evaluator are pending implementation. No trained forecast is required for P0. NASA/climatology subset remains local and Git-ignored. Yahya’s final shared API approval and application release binding remain pending; Phase 3 assets still require safe transfer.
