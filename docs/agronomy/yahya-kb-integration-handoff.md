# Agricultural KB integration handoff (for Yahya)

**Read this if…** you're switching the backend from the UH-001 planner fixture to Refaat's reviewed KB release.

Status: Proposed (not a published contract) · Owner: Amr + Astra (planner), science Refaat · Last reviewed 2026-11-14 · Branch `review/agronomy-kb-final`.

---

## Release

- **ID:** `sakha-agricultural-review-2026-11-14.1`, site `sakha`.
- **Files:** `packages/meg-core/src/knowledge_base/sakha-agricultural-review-2026-11-14.1/`
  (`manifest.json`, `agricultural_kb.json`, `catalogue.json`, `review.json`). They ship inside the package and are
  verified by SHA-256 at load time.
- **State:** 27 rules, **0 enforceable**, so every plan is `rejected` or `needs_review`, never `feasible`.

Put `packages/meg-core/src` on the import path (your adapter already does this for `meg_core`).

## Calls

```python
from meg_core.agricultural_release import load_reviewed_release, bind_profiles, catalogue_view
from agricultural_kb import KBError
from meg_core.planner._validation import InputValidationError

release = load_reviewed_release()                       # once per process; KBError if a file is missing or altered
built = release.for_planner(site_id=snapshot.input.site_id,                         # only "sakha"
                            season_labels=tuple(s.season_label for s in snapshot.input.seasons))
seasons = bind_profiles(snapshot.input.seasons, built.kb)                           # crop_id + purpose -> profile
snapshot = replace(snapshot, data_release=release.version, input=replace(snapshot.input, seasons=seasons))
# ...then prepare_scope / plan_service with built.kb exactly as you do today.
```

Build `built` **per request**: rules are mapped per season label, so the scenario's labels matter.

## Crops and purposes (from `catalogue_view(release, built)`)

| crop_id | Planner profiles (profile_id → purpose) | Offerable purposes | Level |
|---|---|---|---|
| wheat, grain_maize, grain_sorghum, rice, faba_bean | same id → `grain` | grain | review candidate |
| sugar_beet | `sugar_beet` → `sugar` | sugar | review candidate |
| egyptian_cotton | `egyptian_cotton` → `fibre` | fibre | review candidate |
| berseem | `berseem` → `forage_or_seed_requires_review`; `berseem-forage-proposed` → `forage` | forage | runtime profile + proposal |
| watermelon, strawberry, cantaloupe, harankash | none | none | research record (show as information only) |

Each entry also carries `names` (ar-EG/en), `approval` ("pending"), `conflicts`, `blockers`, `kb_rules`,
`enforced_profiles` (empty today) and `feasibility_eligible` (false).

## Backend changes (`backend/app/planner/adapter.py`, not applied)

1. **Load the release.** Replace `load_release(<uh001 fixture>)` with `load_reviewed_release()` at startup. Use
   `release.version` as `data_release`.
2. **Run the Promise Test.** In `run_promise_test`, after decoding:
   - build `built = release.for_planner(...)`
   - `bind_profiles(...)`
   - set `data_release`
   - use `built.kb` for `prepare_scope` and `plan_service`
3. **Catalogue endpoint.** Return `catalogue_view(release, built)` instead of every profile `crop_id`. Today
   `Release.catalogue()` would present review candidates as plain choices.
4. **Errors:**

   | Exception | Response |
   |---|---|
   | `InputValidationError("profile_binding_unresolved")` | 422 with `field_paths` |
   | `KBError("OUTSIDE_RELEASE_SCOPE")` | 422 |
   | `KBError("KB_UNAVAILABLE" / "SOURCE_INTEGRITY" / "INVALID_KB")` | 503, honest unavailable |

## Frontend changes (`frontend/src/domain/catalogue.ts`)

- **Purposes.** `Purpose` must accept `sugar` and `fibre`. Berseem forage is offered via the proposal profile.
- **Badges.** Show a "needs review / بيحتاج مراجعة" badge on every offerable crop (none is approved). Research
  records are shown as information, never as selectable plan crops.
- **Art.** Only 4 crops have art today; others show the unknown picture.
- **Grouping.** `crop_id`s are stable and unchanged from the planner. Group by `crop_id`, not `profile_id` (berseem
  has two profiles).

## Smoke test

```powershell
cd packages\meg-core
python -I -S -m unittest discover -s tests            # expect 118 OK (3 skipped without MEG_AGRI_KB)
$env:PYTHONPATH = "src"; python tools\reviewed_uh001.py   # expect current rejected, 2 needs_review, feasible 0
```

## Integration order

1. Merge `review/agronomy-kb-final` (it contains Refaat's `cae1703` and the catalogue).
2. Apply the adapter change and run your API tests with UH-001.
3. Apply the frontend purposes and badges.
4. The Season Replay route patch is separate (`climate/season-replay-hardening`).
