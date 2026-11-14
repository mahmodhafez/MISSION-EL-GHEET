# Status: backend / API

**Read this if…** you're asking "is the API built? what's next on the backend?"

**As of 2026-11-14**, branch `chore/final-integration` (pushed; PR to `main` pending review). Owner: Yahya. If this is far
behind `git log`, trust git.

---

## Built and verified

FastAPI app, package `backend.app`, run from the repo root:
`backend/.venv/bin/uvicorn backend.app.main:app --port 8787`. It wraps the real `meg_core` planner
(`packages/meg-core`), Refaat's reviewed agricultural KB and Mahmoud/Amr's Season Replay.

| Endpoint (`/api/v1`) | State |
|---|---|
| `GET /health` | Real: data release, forecast bundle present/missing, speech interpreter configured or not |
| `GET /catalogue[?first_winter_year]` | Real: `catalogue_view` of the reviewed KB. 8 offerable crops (wheat, berseem forage, maize, sorghum, rice, faba bean, sugar beet, Egyptian cotton), all `approval: pending`; 4 research records (watermelon, strawberry, cantaloupe, harankash) not offerable |
| `POST /scenarios/from-answers` | Real: app answers → planner snapshot. Farmer facts `farmer_report`; profile bound later by exact crop + purpose; everything the app does not collect is an explicit confirmed unknown (`not_collected`); locks → commitments; permissions → exploration choices |
| `POST /scenarios`, `GET /scenarios/{id}`, `POST /scenarios/{id}/revisions` | Real: planner-shaped input; `expected_revision`, 409 on conflict; SQLite (3 tables, WAL) |
| `POST /scenarios/{id}/promise-test?locale=` | Real planner: per-request KB for the scenario's season labels → `bind_profiles` → scope preview → explicit confirmation → `service.plan`. Stored as codes + params; response adds `rendered` |
| `GET /results/{id}?locale=` | Real: stored result, `current` flag, re-rendered in the requested language without re-running the planner |
| `POST /scenarios/{id}/evidence-cards`, `GET /evidence-cards/{id}` | Real: saves a `review_draft`; plan status unchanged; refuses a result from an old revision |
| `POST /scenarios/{id}/replay` | Real: `compare_sowing_windows` (14-day windows, NASA POWER 2001–2025 + Refaat climatology), statuses echoed from the stored Promise Test, never changed |
| `POST /speech/interpret` | Real code: Gemini strict extraction + deterministic validation when `MEG_GEMINI_API_KEY` is set; otherwise `unavailable`. **Not tested with a real key** |
| `GET /forecast` | Honest status only: `not_applicable` outside 7 days, else `unavailable` (no bundle reader yet) |
| `POST /speech/tts` | Lookup only (D7): `not_generated` until ElevenLabs audio exists |

- **Reviewed KB:** `sakha-agricultural-review-2026-11-14.1`, hash-checked at load (`MEG_DATA_RELEASE_PATH=reviewed`, the
  default). 27 rules, **0 enforceable** (no local sign-off), so every plan is `rejected` or `needs_review`, never `feasible`.
  Errors: out-of-scope site 422, missing/altered KB 503. The UH-001 planner fixture stays selectable for the golden test.
- **Bilingual templates (D4):** `app/i18n/messages.json`; each rendered item is `{code, version, text, speech}`; text uses
  digits, speech spells numbers in Egyptian Arabic words (draft for native review).
- **Verified (14 Nov):** `pytest backend/tests` 69 passed (incl. UH-001 golden = planner CLI; UH-001 answers on the reviewed
  KB = rejected `sowing_before_protected_cut`, 28 May / 1 Jun `needs_review`, 0 feasible, search incomplete; replay echoes
  statuses); planner 118 OK. The full UH-001 browser journey against the running backend passed at 12 widths, AR/EN.
- **Supply chain:** `backend/requirements.lock` (exact + sha256, 23 packages incl. pip 26.2.2), `backend/pip.conf`
  (14-day minimum age, wheels only, hashes required). Rules: [dependencies.md](../rules/dependencies.md).
- **Handoffs applied:** [KB integration](../agronomy/yahya-kb-integration-handoff.md) (Amr) and
  [Season Replay integration](../climate/season-replay-integration-handoff.md) (Mahmoud/Amr), both on `chore/final-integration`.

## Next up

| # | Task | Notes |
|---|---|---|
| 1 | Review and merge the `chore/final-integration` PR | Reviewers: Amr (planner, KB, replay, frontend), Refaat (data, KB), Mahmoud (replay) |
| 2 | Ask preparation days and harvest dates in the app; map them in `from-answers` | Without them the planner cannot compute `preparation_shortfall` ("why"), unlike the fixture |
| 3 | Approve Refaat's KB schema and Amr's adapter conventions (year/leap, topic map) | Formal sign-off still pending; code already uses them |
| 4 | Test Gemini with a key and a set of real Egyptian Arabic recordings; verify the model ID | Backend design §8.3 |
| 5 | Shared Pydantic contracts and OpenAPI → TypeScript types | Requests still carry planner JSON; frontend types are handwritten |
| 6 | Forecast bundle reader (ML contract) | Optional; must not block P0 |
| 7 | Voice audio: Moaaz generates and reviews with ElevenLabs once wording is final | [voice-generation.md](../backend/voice-generation.md) |

## Known problems

- 4.6 MB of CSVs and two ZIPs under `refaat-data-ml/` are committed, against the no-data-in-git rule (Refaat to decide).
- Four KB rules cite only private team documents (Amr's review F3); harmless while nothing is enforced.
- `api-contracts.md` body still mixes superseded text (Q6); §0b records what is actually implemented.
- No auth or sessions (MVP decision); a remote demo must serve synthetic scenarios only.

## Open questions

See Q4, Q6 in the [overview](README.md).
