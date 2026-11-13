# Team and ownership

**Read this if…** you need to know who owns a folder, who reviews a change, or who decides.

Status: current as of , from Amr's recovery handoff
(`archive/handoff-/YAHYA_HANDOFF.md`). Last reviewed .

---

| Person | GitHub | Owns | Main folders |
|---|---|---|---|
| **Yahya** Alaaeldin Mohamed | `@Yahya-alaa` | Backend: API, persistence/revisions, replay integration, shared Pydantic schemas. Also works on frontend. Docs structure. | `backend/`, `docs/backend/`, `docs/rules/` |
| **Amr** Hany Mahmoud | `@Amrhany06` | Frontend/UI supervision and integration, ML, final product calls. Repo owner. | `frontend/`, `work/ux-*`, `docs/design/`, `ml/` |
| **Karim** Mohamed Samy | _unknown_ | Planner: candidate generation, constraint rules, tests | `meg_core/planner/`, `docs/planner/` |
| **Refaat** (Ahmed Mohamed Refaat) | _unknown_ | Data and evidence releases, numerical validation, ML with Amr | `data/`, `docs/science/` |
| **Mahmoud** Ahmed Hafez | _unknown_ | Bounded ML/baseline work (≤3 h, per `ml/tasks/mahmoud.md`), climate replay mapping | `ml/`, `meg_core/climate/` |
| **Moaaz** Mostafa Elzaghawy | _unknown_ | Crop pictures, motion, storytelling, demo video | `media/` |

Everyone collaborates across these lines, but **changes in another owner's folder go through that
owner's review.** Add missing GitHub handles here and in `.github/CODEOWNERS`.

## Who decides

| Decision | Decides | Must be consulted |
|---|---|---|
| Product scope, feature removal, visual direction | Amr | Team |
| API contract / shared schemas | Yahya | Amr (frontend impact), Karim (planner), Refaat (scientific fields) |
| Planner rules and statuses | Karim | Refaat (evidence), Yahya (contract) |
| Scientific meaning, data releases | Refaat | Amr |
| ML model selection | Amr | Refaat |

## Ownership conflicts still open

Older docs assign the planner differently. See "Open questions" in `docs/status/README.md`.
Until Amr confirms, the table above (from his latest handoff) is current.
