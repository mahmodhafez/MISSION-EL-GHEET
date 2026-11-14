# MISSION EL GHEET — Backend design

**Read this if…** you're writing backend code: module layout, SQLite, ML bundle, i18n, voice.

Status: Approved (D1–D8); D6 superseded 14 Nov (Gemini). §2 and §12 are the original plan; **see "As built" below for what exists** · Owner: Yahya. Last reviewed 14 Nov 2026.

Approved by the user on  (decisions D1–D8 below). This document defines the backend code structure, runtime data, persistence, the ML ↔ backend interface, and the voice and bilingual design. It is the implementation map for [ARCHITECTURE.md](architecture.md). Wire types live in [API_CONTRACTS.md](api-contracts.md). Planner semantics live in [PLANNER_SPEC.md](../planner/planner-spec.md). Where this document simplifies an earlier contract for the hackathon MVP, [API_CONTRACTS.md §0](api-contracts.md#0-mvp-revision-) records the change.

Design goal: a backend that is correct, testable and small enough for two developers to build during the hackathon. Keep the scientific rules strict; keep the machinery around them simple.

## As built (14 Nov 2026)

What exists on `chore/final-integration`, where it differs from the plan below. Endpoint states: [status/backend.md](../status/backend.md).

| Planned (below) | Built |
|---|---|
| Planner rules in `backend/app/planner/` (§2) | Planner lives in `packages/meg-core` (Amr + Astra). `backend/app/planner/` has only `adapter.py` (planner JSON codec, reviewed-KB release, per-request `bind_profiles`) and `answers.py` (app answers → snapshot) |
| `backend/app` run from `backend/` | One package `backend.app`, run from the repo root (`uvicorn backend.app.main:app`), tests `pytest backend/tests` |
| `data/release/` committed (D8) | Reviewed KB ships inside `meg_core` (hash-pinned); climate data in `refaat-data-ml/data` |
| Deterministic parsers (D6) | Gemini strict extraction + validation (§8.3), untested with a key |
| Replay in `backend/app/replay/` by Yahya | Built by Mahmoud, hardened by Amr; served at `POST /scenarios/{id}/replay` |
| Templates in `data/release/content/` | `backend/app/i18n/messages.json` (+ `formatting.py`, `render.py`) |
| pydantic-settings, uv | Plain dataclass `Settings` from `MEG_*` env / `backend/.env`; hashed `requirements.lock` + `pip.conf` (dependency rules) |
| Default port 8000 | 8787 (8000 is often taken on dev machines) |

## Approved decisions

| # | Decision |
|---|---|
| D1 | Layered modules with one dependency direction. `planner/` and `replay/` are pure Python: no I/O, no FastAPI, no database. |
| D2 | SQLite with three tables and a single scenario `revision`. No idempotency keys, sessions, CSRF or approval revocation in the MVP. |
| D3 | ML connects through a precomputed, schema-validated `forecast_bundle.json`. The backend never imports PyTorch or model code. |
| D4 | Prompts, explanations, readbacks and takeaways are backend-owned templates with `text` and `speech` variants. UI labels stay in the frontend. |
| D5 | Speech recognition starts with the browser Web Speech API (`ar-EG`, `en-US`). A server-side provider such as Azure can be added behind the same interface later. |
| D6 | ~~Transcript interpretation is deterministic, one parser per answer type, driven by an editable lexicon. No LLM in the MVP.~~ **Superseded 14 Nov (Yahya):** a Gemini Flash model extracts the answer fields from the transcript into a strict JSON schema, with `null` for anything not said. The backend validates every value; Gemini only proposes. See §8.3. |
| D7 | Text-to-speech uses pre-generated prompt audio plus a cached backend endpoint behind a provider adapter. The provider remains to be selected. |
| D8 | A runtime data release is committed under `data/release/`, hashed in a manifest, and loaded and validated once at startup. |

## 1. Layers and dependency direction (D1)

```
api/            thin HTTP routers: validate, call a service, return a schema
  │
services/       orchestration: load snapshot → compute → render → store
  │
  ├── planner/  PURE  rule evaluation, status reduction, candidate enumeration
  ├── replay/   PURE  historical mapping and paired metrics
  ├── forecast/       load and validate the ML bundle; decide forecast status
  ├── i18n/           codes + typed params → Arabic/English text and speech text
  └── speech/         transcript → proposed fact; text-to-speech cache
  │
store/          SQLite repositories        core/  config, AppData, errors
schemas/        Pydantic wire models (single source → OpenAPI → TypeScript)
```

Rules:

- Imports point downward only. `planner/` and `replay/` import only `schemas/` and the standard library (plus pandas for replay). They never import `store`, `api`, `services` or `fastapi`.
- Only `services/` touches `store/`.
- Routers contain no business logic.
- `planner/` emits explanation codes and typed parameters. It never produces display text. `i18n/` renders text.

Ownership: Karim owns `planner/` and its tests. Yahya owns `api/`, `services/`, `store/` and `core/`. Amr and Refaat own `ml/` and the forecast bundle. Content (`messages`, `lexicon`) is shared, with Amr reviewing wording and Refaat reviewing scientific meaning.

## 2. Module tree

```
backend/
  pyproject.toml              managed with uv; fastapi, uvicorn, pydantic, pydantic-settings,
                              pandas, httpx, pytest, ruff, mypy
  .env.example                every setting below, with safe defaults; no secrets
  app/
    main.py                   create_app(): Settings → load AppData → init DB → mount routers
    core/
      config.py               Settings (pydantic-settings, env prefix MEG_)
      appdata.py              AppData: frozen container built once at startup
      errors.py               error envelope and exception handlers
    schemas/
      common.py               Fact, SourceRef, Explanation, RenderedExplanation, ErrorEnvelope
      scenario.py             ScenarioInput, SeasonInput, Commitment, ExplorationChoice,
                              Confirmation, ScenarioSnapshot
      planning.py             RuleEvaluation, PlanEvaluation, Candidate, PlanningResult
      replay.py               ReplayResult and metrics
      forecast.py             ForecastBundle (the ML contract), ForecastResult
      evidence.py             EvidenceCard
      speech.py               InterpretRequest, SpeechProposal, TtsRequest, TtsResponse
    api/
      catalogue.py  scenarios.py  planning.py  replay.py  forecast.py  evidence.py  speech.py
      deps.py                 get_appdata(), get_db(), locale parameter
    services/
      scenario_service.py     create and revise scenarios (expected-revision transaction)
      planning_service.py     snapshot → planner.promise_test → store → render
      replay_service.py       plans + weather → replay.metrics → store → render
      evidence_service.py     assemble, save and (if feasible and current) approve a card
    planner/                  PLANNER_SPEC.md lives here
      dates.py                interval arithmetic: occupation, release, s(i+1) ≥ r(i) + p(i)
      registry.py             rule_id → (function, effect, required_for, explanation codes)
      rules/
        occupancy.py          single_field_occupancy, transition_preparation
        commitments.py        commitment_preserved
        profile_support.py    profile_calendar_support, profile_field_support
        windows.py            window_preference
        requirements.py       production_requirement, demand_support
      evaluate.py             evaluate_all(plan, snapshot, catalogue) → RuleEvaluation[]
      status.py               hard failure → rejected; unresolved → needs_review; else feasible
      enumerate.py            permitted-choice product, endpoint invalidation, ranking
      promise_test.py         public entry point: promise_test(snapshot, catalogue) → PlanningResult
    replay/
      mapping.py              anchor-year block mapping
      metrics.py              crop-period ET0, Tmax summaries, paired differences
    forecast/
      bundle.py               load and validate forecast_bundle.json; reload when the file changes
      service.py              available | stale | not_applicable | unavailable
    i18n/
      render.py               render(code, params, locale, variant) → text
      formatting.py           dates, numerals, units, spoken numbers, bidi isolation
    speech/
      interpret/
        lexicon.py            load lexicon.<locale>.json; normalise Arabic spelling
        parsers.py            crop, yes_no, date, area, unknown, choice
        interpret.py          dispatch by answer_type → SpeechProposal
      tts.py                  TtsProvider protocol, provider adapters, disk cache
    store/
      schema.sql              the three tables in §4
      db.py                   sqlite3 connection per request, WAL mode, foreign keys on
      repositories.py         ScenarioRepo, ResultRepo, EvidenceRepo
  tests/
    unit/planner/  unit/replay/  unit/i18n/  unit/speech/  unit/forecast/
    api/                      FastAPI TestClient end-to-end tests
    golden/uh001_expected.json
```

Expected size: about 2,000–3,000 lines of Python, most of it in `planner/`, `speech/interpret/` and tests.

## 3. Runtime data release (D8)

```
data/release/                         COMMITTED; every file hashed in manifest.json
  manifest.json                       data_release id, file list + SHA256, POWER request URL,
                                      units, ET0 method id, weather coverage
  catalogue/crops.json                4 crops, profiles, calendar evidence, unknown reasons
  catalogue/rules.json                rule metadata: id, version, effect, required_for,
                                      explanation codes, source refs
  content/messages.ar-EG.json         prompt, explanation, readback and takeaway templates
  content/messages.en.json
  content/lexicon.ar-EG.json          Egyptian Arabic words and phrases → canonical values
  content/lexicon.en.json
  content/prompts.json                question catalogue: question_id, answer_type, field path,
                                      choices, audio file per locale
  weather/sakha_daily_2001_2025.csv   regenerated by data/validation/regenerate_et0.py and
                                      checked against et0_release_manifest.json hashes
  fixtures/uh001_input.json           UH-001 ScenarioInput exactly as REFERENCE_SCENARIO.md
data/forecasts/forecast_bundle.json   written by ml/; one demo bundle committed
```

- `data_release` is a single string, for example `meg-2026-11-14.1`. It replaces the separate catalogue, rules, source-manifest, mapping and coverage version IDs. Every stored result records the `data_release` it was computed with.
- Startup loads everything into one frozen `AppData` object and fails fast if a hash mismatches, an ID does not resolve, a unit is unexpected, a message code used by `rules.json` is missing in either language, or a lexicon file is malformed.
- Weather CSV columns: `date,tmax_c,tmin_c,tdew_c,rh_pct,wind2_m_s,solar_mj_m2_day,pressure_kpa,rain_mm_day,et0_mm_day,qc`. Constant metadata (site, LST, source, method) lives in `manifest.json`, not on every row.
- Raw POWER responses stay out of Git, as already arranged in `data/validation/`.

## 4. Persistence (D2)

```sql
CREATE TABLE scenarios (
  id                TEXT    NOT NULL,
  revision          INTEGER NOT NULL CHECK (revision >= 1),
  input_json        TEXT    NOT NULL,   -- ScenarioInput
  confirmation_json TEXT    NOT NULL,   -- Confirmation
  data_release      TEXT    NOT NULL,
  created_at        TEXT    NOT NULL,   -- RFC3339 UTC
  PRIMARY KEY (id, revision)
);                                       -- current revision = MAX(revision)

CREATE TABLE results (
  id            TEXT PRIMARY KEY,
  scenario_id   TEXT    NOT NULL,
  revision      INTEGER NOT NULL,
  kind          TEXT    NOT NULL CHECK (kind IN ('promise_test', 'replay')),
  data_release  TEXT    NOT NULL,
  json          TEXT    NOT NULL,       -- PlanningResult or ReplayResult (codes + params only)
  created_at    TEXT    NOT NULL,
  FOREIGN KEY (scenario_id, revision) REFERENCES scenarios (id, revision)
);

CREATE TABLE evidence_cards (
  id             TEXT PRIMARY KEY,
  scenario_id    TEXT    NOT NULL,
  revision       INTEGER NOT NULL,
  result_id      TEXT    NOT NULL REFERENCES results (id),
  decision_state TEXT    NOT NULL CHECK (decision_state IN ('review_draft', 'approved')),
  json           TEXT    NOT NULL,
  created_at     TEXT    NOT NULL,
  FOREIGN KEY (scenario_id, revision) REFERENCES scenarios (id, revision)
);
```

- Scenario IDs are random UUIDs generated by the server.
- A revision write runs `BEGIN IMMEDIATE`, reads `MAX(revision)`, compares it with `expected_revision`, and inserts `MAX + 1`. A mismatch returns `409` with `current_revision`. A retried request after success also gets `409`, and the client reloads with `GET`. This replaces idempotency keys.
- Results and cards are immutable. A result or card is **current** only if its `revision` equals the scenario's current revision and its `data_release` equals the running release. This is computed on read, never stored.
- Results store codes and parameters only. Text is rendered on read in the requested locale, so a language switch never touches storage.
- Approval is a card with `decision_state = approved`. It is allowed only when the result's plan is `feasible` and current. A new revision makes every older card non-current automatically.

## 5. Endpoints and build order

All paths are under `/api/v1`. Read endpoints that return explanations take `?locale=ar-EG|en` (default `ar-EG`).

| Milestone | Endpoint | Purpose |
|---|---|---|
| 1 | `GET /health` | Liveness, `data_release`, forecast bundle status |
| 1 | `GET /catalogue` | Crops, profiles, rules metadata, prompt catalogue |
| 1 | `POST /scenarios` | Create a confirmed scenario (revision 1) |
| 1 | `GET /scenarios/{id}` | Current snapshot |
| 1 | `POST /scenarios/{id}/revisions` | Confirmed full replacement with `expected_revision` |
| 1 | `POST /scenarios/{id}/promise-test` | Evaluate the current revision, store and return `PlanningResult` |
| 1 | `GET /results/{id}` | Re-fetch a stored result, rendered in `?locale=` |
| 2 | `POST /speech/interpret` | Transcript → `SpeechProposal` |
| 2 | `POST /speech/tts` | Rendered speech text → cached audio URL |
| 2 | `GET /audio/{sha}.mp3` | Serve cached audio (static) |
| 3 | `POST /scenarios/{id}/replay` | Historical comparison for the current revision |
| 4 | `POST /scenarios/{id}/evidence-cards` | Save a review draft, or approve if feasible and current |
| 4 | `GET /evidence-cards/{id}` | Card plus computed currency |
| 5 | `GET /forecast?action_dates=` | Forecast status and records from the ML bundle |

The first vertical slice is milestone 1 plus the UH-001 golden test: confirmed UH-001 → real Promise Test → P0 `rejected`, protected 20 May cut preserved, bilingual conflict text, zero feasible alternatives.

## 6. ML ↔ backend interface (D3)

```
ml/  (separate venv: torch, chronos, scikit-learn)       backend/
  train.py     → ml/artifacts/          (gitignored)
  evaluate.py  → skill vs climatology and persistence
  predict.py --issue-date D --method M
     └─ validates against forecast_bundle.schema.json
     └─ writes data/forecasts/forecast_bundle.json ──────► forecast/bundle.py
                                                             load, validate, reload on change
                                                           forecast/service.py
                                                             decide status per request
                                                           GET /api/v1/forecast
```

### 6.1 The contract

The Pydantic model `ForecastBundle` in `backend/app/schemas/forecast.py` is the single source. `make schemas` exports it to `ml/contract/forecast_bundle.schema.json`, and `ml/predict.py` validates against that file before writing. CI validates the committed bundle.

```json
{
  "schema_version": "1",
  "method": "chronos2_lora_r200",
  "method_kind": "trained_ml",
  "model_ref": "amazon/chronos-2@29ec3766+adapter_r200",
  "issued_at": "2026-11-14T06:00:00Z",
  "issue_date": "2026-11-14",
  "site_id": "sakha",
  "data_through": {"power_met": "", "power_solar": ""},
  "valid_until": "2026-11-15",
  "skill": {
    "assessment_period": "/",
    "mae": {"tmax_c": 1.988, "et0_mm_day": 0.640},
    "climatology_mae": {"tmax_c": 1.656, "et0_mm_day": 0.523},
    "interval_coverage_80": {"tmax_c": null, "et0_mm_day": 0.706}
  },
  "experimental": true,
  "records": [
    {"variable": "tmax_c", "unit": "degC", "target_date": "2026-11-15",
     "lead_day": 1, "q10": 21.4, "q50": 23.0, "q90": 24.6}
  ]
}
```

| Field | Rule |
|---|---|
| `method` | Free string naming exactly what produced the numbers, e.g. `climatology_doy31`, `persistence`, `chronos2_lora_r200`, `nwp_mos_ridge_v1`. Never label a baseline as a trained model. |
| `method_kind` | `baseline` or `trained_ml`. |
| `model_ref` | Model and adapter identity, or `null` for a baseline. |
| `data_through` | Last valid input date per channel. NASA solar data can lag more than a week. |
| `valid_until` | Last date on which this bundle may be presented as current. |
| `skill` | The method's own assessment and the climatology comparison on the same period. The UI shows it. A bundle without `skill` is rejected. |
| `records` | Exactly 7 lead days per variable (`tmax_c` in `degC`, `et0_mm_day` in `mm/day`), ordered quantiles `q10 ≤ q50 ≤ q90`, finite values. |

### 6.2 Backend behaviour

`GET /forecast?action_dates=2026-11-16,2026-11-18` returns a `ForecastResult`:

| Status | When |
|---|---|
| `unavailable` | File missing, invalid or failing the schema. Reason code `bundle_missing` or `bundle_invalid`. |
| `stale` | Today (Africa/Cairo) is after `valid_until`. No actionable records. Issue and target dates are still reported. |
| `not_applicable` | No requested action date falls within the bundle's target dates. UH-001 lands here. |
| `available` | Otherwise. Records for the requested dates, plus `method`, `method_kind` and `skill`. |

- The bundle is re-read when its modification time changes, so the ML team can publish a new forecast without restarting the backend.
- A forecast never changes planner eligibility or locks (ARCHITECTURE.md).
- Which method is published is an ML-team decision based on evaluation. The backend behaves identically for every method.

## 7. Bilingual design (D4)

### 7.1 Where text lives

| Text | Owner | File |
|---|---|---|
| UI chrome: buttons, headings, generic errors | Frontend | `frontend/src/i18n/{ar-EG,en}.json` |
| Question prompts, explanations, readbacks, takeaways | Backend | `data/release/content/messages.{ar-EG,en}.json` |

The backend owns result wording because the screen, the spoken audio and the saved Evidence Card must say the same thing for the same version.

### 7.2 Message format

```json
{
  "sowing_before_protected_cut": {
    "version": 1,
    "params": {"season_id": "season", "sowing_date": "date", "protected_cut_date": "date"},
    "text":   "ميعاد زراعة الذرة {sowing_date:long} قبل حشة البرسيم المحمية {protected_cut_date:long}.",
    "speech": "ميعاد الذرة يوم {sowing_date:spoken} جاي قبل حشة البرسيم اللي حضرتك ثبّتها يوم {protected_cut_date:spoken}."
  }
}
```

- Every code exists in both languages with identical `params`. Startup fails otherwise.
- Templates are authored Egyptian Arabic, never machine-translated.
- Placeholders take a format: `long` (written date), `short`, `spoken` (date or number in words), `unit` (number with spoken unit).

### 7.3 Rendering in responses

Stored results hold `{code, params}`. On read, the API adds the rendered forms:

```json
{"code": "sowing_before_protected_cut",
 "params": {"season_id": "s2", "sowing_date": "2027-05-15", "protected_cut_date": "2027-05-20"},
 "template_version": 1,
 "locale": "ar-EG",
 "text": "ميعاد زراعة الذرة ١٥ مايو ٢٠٢٧ قبل حشة البرسيم المحمية ٢٠ مايو ٢٠٢٧.",
 "speech": "ميعاد الذرة يوم خمستاشر مايو ألفين سبعة وعشرين جاي قبل ..."}
```

### 7.4 Formatting (`i18n/formatting.py`)

- Arabic display uses Arabic-Indic digits; English uses Latin digits. Canonical values stay ISO.
- Gregorian month names in both languages. Always include the year.
- Spoken Egyptian Arabic numbers via a lookup table covering days 1–31, quantities 0–100 and years 2000–2099.
- Units: `feddan`, `qirat` and `ha` are spoken with the number ("واحد فدان", "نص فدان"). Never converted silently.
- Mixed-direction values are wrapped in Unicode isolation marks (FSI…PDI).

### 7.5 Language switching

- `locale` is not part of `ScenarioInput`. It is a query parameter on reads.
- Switching language: the frontend stops audio, re-fetches `GET /results/{id}?locale=en` and plays the new readback. No new revision, no recomputation, approval state unchanged.

## 8. Voice input (D5, D6)

### 8.1 Flow

```
Question (question_id, answer_type) → play prompt audio
   │
   ├─ tap a picture/choice ───────────────────────────────┐
   └─ press mic → disclose transmission → browser STT     │
        (ar-EG or en-US) → transcript                     │
           │                                              │
     POST /speech/interpret                               │
           ▼                                              ▼
     SpeechProposal (status: ready | needs_clarification | unknown | no_match)
           │
     play readback ("عشرين مايو ألفين سبعة وعشرين، صح؟")
           │
     separate explicit Confirm (button, or a new voice turn) → fact confirmed in the UI
           │
     end of intake → POST /scenarios with all confirmed facts
```

- Touch and voice produce the same proposed field.
- Recognition never confirms. Confirmation is always a separate action after the full readback. Silence never confirms.
- Raw audio never reaches the backend in the MVP. Only the transcript is sent, and it is not stored or logged.

### 8.2 Speech recognition (D5)

The MVP uses the browser Web Speech API with `lang = "ar-EG"` or `"en-US"`. The frontend wraps it in a `SpeechRecognizer` interface (`start`, `stop`, `onResult`, `onError`) so a server-side provider can replace it without changing screens.

| Situation | Behaviour |
|---|---|
| API missing (e.g. Firefox, some iOS) | Hide the mic button; touch and prompt audio remain |
| Permission denied | Do not re-prompt; continue with touch |
| No result or timeout | Offer repeat, choices or help; nothing advances |

Chrome's implementation sends audio to Google. The microphone disclosure must say so before permission is requested (PRIVACY_ASSUMPTIONS.md).

### 8.3 Interpretation (D6, Gemini extraction)

Decided 14 Nov 2026 (Yahya): **Gemini extracts the facts the farmer said; it never decides, advises or chats.** Model: `gemini-3.8-flash` (check the exact ID on Google's model page before wiring it). The call is made by the backend only; the key never reaches the browser.

`POST /speech/interpret` keeps its request:

```json
{"question_id": "s1_final_cut_date", "answer_type": "date", "locale": "ar-EG",
 "transcript": "عشرين مايو", "context": {"season_order": 1, "issue_date": "2026-11-14"}}
```

**What the backend sends to Gemini:** the transcript, the current `question_id`, the allowed values from the data-release catalogue (crop IDs, purposes) and this fixed instruction: *extract only what the speaker said; return `null` for every field that was not said; never guess a year, unit, crop or date; never add advice or text outside the schema.* Structured output is required (`response_mime_type: application/json` with the schema below), temperature 0.

**Extraction schema (strict; every field nullable, no extra keys):**

```json
{
  "seasons": [
    {"order": 1,
     "crop": "berseem | grain_maize | grain_sorghum | wheat | unknown | null",
     "crop_said": "the words used, only when ambiguous (e.g. \"ذرة\"), else null",
     "purpose": "forage | grain | null",
     "sowing_date":   {"day": 1, "month": 1, "year": null},
     "last_cut_date": {"day": 20, "month": 5, "year": null},
     "must_stay": true}
  ],
  "area": {"value": null, "unit": "feddan | qirat | hectare | null"},
  "answer": {"yes_no": "yes | no | null", "confirm": null, "dont_know": null},
  "ambiguous": [{"path": "seasons[1].crop", "said": "ذرة", "options": ["grain_maize", "grain_sorghum"]}],
  "off_topic": false
}
```

- A date part not said is `null` (`"year": null` for “20 May”). The backend resolves a missing year only from the season being asked and always reads it back with the year (design/voice-first.md §3).
- `seasons` lists only seasons the speaker mentioned. `must_stay` is `true` only when the farmer said it must not change; otherwise `null`, never `false` by default.
- `unknown` crop or `dont_know: true` means the farmer said “I don't know”; that becomes `confirmed_unknown` after readback, never a guess.
- `off_topic: true` (for example “what should I plant?”) returns the fixed redirect template; Gemini's own words are never shown or spoken.

**Backend validation after Gemini (deterministic):** reject the whole reply as `no_match` if it is not valid JSON for the schema; drop any value outside the catalogue enums; check day/month ranges, the season's months and that a planned date is not in the past; negation is checked again on the transcript (a negated protected value never becomes permission to change it). Timeout or provider error → `no_match`, and the screen points to the pictures.

**Response:** the existing `SpeechProposal`, one per extracted field. **Proposed contract change (Yahya, shared-contract owner; Amr reviews frontend impact):** `POST /speech/interpret` returns `{"proposals": [SpeechProposal, ...], "ambiguous": [...], "off_topic": bool}` so one sentence can fill several fields (lab 02 “opening sentence”). Single-field answers return a list of one.

- Recognition and extraction never confirm. The readback and the separate explicit confirm (§8.1) are unchanged.
- The transcript is sent to Google for extraction and is not stored or logged by us. Check the Gemini API data terms for the tier we use; the mic disclosure must say the words are sent to Google to be understood.
- Test before relying on it: a set of real Egyptian Arabic recordings per answer type, scored field by field (correct, wrong, null when said, value when not said). No accuracy figure exists yet.
- Open: send the audio itself to Gemini instead of the browser transcript (would replace D5 and the “no audio upload” rule). Not decided.

## 9. Voice output (D7)

| Audio | Source | Works offline |
|---|---|---|
| Fixed prompts and help lines (both languages) | Generated once by `scripts/build_prompt_audio.py` or recorded by the team; stored in `frontend/public/audio/{locale}/{question_id}.{text_sha8}.mp3` | Yes |
| Dynamic sentences (dates, conflicts, takeaways) | Pre-generated per scenario by the same script; `POST /speech/tts` looks up the file → `GET /audio/{sha}.mp3`, else `unavailable` | Yes |
| Fallback | Browser `speechSynthesis` if a matching voice exists, labelled "device voice"; otherwise text plus "audio unavailable" | Yes |

`POST /speech/tts`

```json
{"locale": "ar-EG", "code": "sowing_before_protected_cut",
 "params": {"season_id": "s2", "sowing_date": "2027-05-15", "protected_cut_date": "2027-05-20"}}
```

Returns `{"status": "ready", "audio_url": "/api/v1/audio/3fa1….mp3", "template_version": 1, "voice": "<elevenlabs voice_id>", "cached": true}` or `{"status": "unavailable", "reason_code": "not_generated"}` (no pre-generated file for these params; changed 13 Nov 2026 from `provider_unavailable` because nothing is generated live).

- The client sends a code and params, never free text, so the backend cannot be used to speak arbitrary advice.
- Cache key: SHA256 of `locale + voice + template_version + rendered speech text`. A changed plan produces new params and therefore a new file, so old audio cannot narrate a new plan.
- `TtsProvider` is a small protocol (`synthesize(text, locale) → bytes`). **Provider: ElevenLabs, offline only (Yahya, 13 Nov 2026).** All audio is pre-generated by the build script; at runtime `POST /speech/tts` only returns an already generated file or `unavailable`, and the deployed backend holds no provider key. See [voice-generation.md](voice-generation.md).
- `scripts/prewarm_audio.py` renders and caches every UH-001 sentence so the demo plays without network access.

## 10. Configuration, errors and logging

| Setting (`MEG_` prefix) | Default |
|---|---|
| `DATA_DIR` | `data/release` |
| `DB_PATH` | `backend/var/meg.sqlite3` (gitignored) |
| `FORECAST_BUNDLE` | `data/forecasts/forecast_bundle.json` |
| `AUDIO_CACHE_DIR` | `backend/var/audio` (gitignored) |
| `TTS_PROVIDER` | `none` |
| `TTS_AZURE_KEY`, `TTS_AZURE_REGION` | unset |
| `CORS_ORIGINS` | `http://localhost:5173` |

- Errors use the envelope in API_CONTRACTS §6. A cross-season conflict is a `200` planning result, never an error.
- Logs contain request ID, path, status, duration and error code. Never transcripts, audio or full scenario bodies.
- Local development: Vite proxies `/api` to `uvicorn backend.app.main:app --port 8787` (run from the repo root; `MEG_API_URL` overrides). Demo: FastAPI serves the built frontend from one process (not built yet).

## 11. Testing

| Layer | Tests |
|---|---|
| `planner/` | PLANNER_SPEC §7 cases; UH-001 golden result (`tests/golden/uh001_expected.json`) compared field by field, ignoring generated IDs and timestamps |
| `replay/` | Synthetic ET0 series with hand-computed sums and paired differences |
| `i18n/` | Every code renders in both languages with identical params; Arabic digits, spoken dates and units |
| `speech/` | Case families from the accessibility protocol, per parser, including negation and corrections |
| `forecast/` | Each status from crafted bundles; schema rejection of malformed bundles |
| `api/` | Milestone-1 journey through TestClient; `409` on stale revision; `422` on structural errors |
| Contract | OpenAPI export and generated TypeScript types match the committed copies; the committed forecast bundle validates |

CI runs `ruff`, `mypy`, `pytest` and the contract checks on every pull request.

## 12. Build sequence

1. **Yahya:** project skeleton, `core/`, `schemas/` for milestone 1, `store/`, `/health` and `/catalogue`, OpenAPI export and TypeScript generation.
2. **Refaat with Karim:** `data/release/` — `crops.json`, `rules.json`, `uh001_input.json`, the weather CSV and the manifest.
3. **Karim:** UH-001 golden test first, then `planner/dates.py`, rules, `evaluate.py` and `status.py` until P0 passes.
4. **Yahya:** scenario endpoints and `promise-test` with storage; `i18n/` rendering with the first messages in both languages.
5. **Amr with Yahya:** `speech/interpret/` parsers and lexicon; `/speech/tts` with prewarmed UH-001 audio.
6. **Karim:** `enumerate.py` for R1/R2 and synthetic positive cases.
7. **Yahya with Refaat:** replay; then evidence cards.
8. **Amr with Refaat:** `ml/predict.py` writing the bundle; `forecast/` service.
