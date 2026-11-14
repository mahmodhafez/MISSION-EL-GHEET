# MISSION EL GHEET — API contracts v1

**Read this if…** you're implementing or consuming the HTTP API. **§0 overrides everything below it.**

Status: Approved · Owner: Yahya. Last reviewed 14 Nov 2026. **§0b records what is actually implemented.**

Boundaries: [architecture](architecture.md). Scientific meaning: [data spec](../science/data-spec.md), [science](../science/science.md). Implement these types in Pydantic and generate OpenAPI and frontend types from them; don't hand-write duplicates.

## 0. MVP revision, 

The user approved [BACKEND_DESIGN.md](backend-design.md) decisions D1–D8. Where this section conflicts with later sections, this section wins. Scientific meaning, planner semantics, statuses and the UH-001 expected result are unchanged.

| Topic | MVP contract |
|---|---|
| Versions | One `data_release` string replaces `catalogue_version`, `rules_version`, `source_manifest_version`, `mapping_version` and `coverage_policy_version` in requests, results and `DependencyRef`. The ET0 method ID stays in the release manifest. |
| Revisions | One scenario `revision`. `InputRef = {scenario_id, revision}`. `PlanRef` for the farmer's current plan is the same pair; `plan_version` is dropped. A candidate is identified by `{result_id, candidate_id}`. |
| Locale | `locale` is removed from `ScenarioInput`. Read endpoints take `?locale=ar-EG|en`. `Confirmation.locale` stays as a record of the language used to confirm. |
| Area | `area` is `Fact<number>` with `unit: ha|feddan|qirat`, stored as the farmer stated it. No silent conversion. |
| Retry safety | `expected_revision` checks replace `Idempotency-Key`. A retry after success returns `409` with `current_revision`; the client reloads. |
| Sessions | No sessions, cookies, CSRF or `401/403` in the MVP. Scenario IDs are random UUIDs. A remote demo serves synthetic scenarios only. |
| Approval | An Evidence Card is saved as `review_draft`, or as `approved` only when its plan is `feasible` and current. Revocation and the commitment-change acknowledgment flow are deferred. |
| Rendered text | Every `Explanation` in a response also carries `template_version`, `locale`, `text` and `speech`, rendered from backend templates. Stored results keep only `code` and `params`. |
| Forecast | `ForecastResult` is derived from the ML team's `forecast_bundle.json` (§5 and BACKEND_DESIGN §6). It carries `method`, `method_kind`, `model_ref` and `skill`; records carry `lead_day`. |
| Speech | `POST /speech/interpret` (transcript → proposal) and `POST /speech/tts` (code + params → cached audio) replace the earlier `/speech/proposals` and `/speech/playback` reservations. |

MVP endpoints are listed in BACKEND_DESIGN §5 and in §3 below.

## 0b. As implemented, 14 Nov 2026 (`chore/final-integration`)

Where the running API differs from the text below, this section describes reality. Proposed for sign-off by the owners in
[team.md](../team.md); the frontend uses exactly these shapes (`frontend/src/services/http/httpAdapter.ts`).

| Endpoint | Request | Response |
|---|---|---|
| `GET /catalogue[?first_winter_year=2026]` | — | `{data_release, crop_ids (offerable **and** with reviewed-KB evidence: wheat, berseem, grain_maize, grain_sorghum), crops: catalogue_view[] + kb_evidence, profiles[], runtime, note}` |
| `POST /scenarios/from-answers` | `{first_winter_year, journey: check|explore, seasons[4]: {season_id, crop_id|unknown|null, purpose, sowing_date: ISO|unknown|null, last_cut_date}, locks{season_id: bool}, permissions[{season_id, field: sowing_date|crop_id, allowed_values[]}], confirm_exploration}` | Scenario `{id, revision, data_release, input, created_at, updated_at}` |
| `POST /scenarios` / `revisions` | Planner-shaped `{snapshot, exploration, confirm_exploration}` (+ `expected_revision`) | Scenario; 409 `revision_conflict`, 409 `data_release_mismatch`, 422 `invalid_snapshot` |
| `POST /scenarios/{id}/promise-test?locale=ar-EG|en` | — | `{result_id, scenario_id, revision, data_release, synthetic, exploration_confirmed, preview, result: PlanningResult, rendered}` |
| `GET /results/{id}?locale=` | — | `{…, payload: {result, …}, current, rendered}` |
| `POST /scenarios/{id}/evidence-cards` | `{result_id}` | `{card_id, scenario_id, revision, result_id, kind: review_draft, plan_status, data_release}`; 409 `result_not_current` |
| `POST /scenarios/{id}/replay` | `{sow_dates[1..4], window_days=14, result_id?}` | `{status: ok, replay}` or `{status: unavailable, reason}`; 422 `invalid_replay_request` |
| `POST /speech/interpret` | `{question_id, locale, transcript, season_order}` (today) · **proposed 14 Nov:** multipart audio clip + same fields | `{status: ok, extraction}` (strict schema, backend design §8.3) / `no_match` / `unavailable` |
| `GET /forecast?action_dates=` | — | `{status: not_applicable|unavailable, reason}` |

- `rendered` = `{locale, headline, conflicts[], why, options[], coverage[], review_reasons[], takeaway}`, each item
  `{code, version, text, speech}`. Stored results keep codes and params only.
- **Proposed 14 Nov, additive, needs Amr's sign-off:** `rendered.research` (optional; `null` on fixture releases) =
  `{caveat, seasons[{season_id, crop_id, crop, notes[], other[]}], empty_seasons[], empty_hint}`. Each note is
  `{rule_id, kind, title, text, speech, window, farmer_date, placement: before|inside|after|null, days_outside, dates[], where, source}`.
  These are sourced, **unenforced** reviewed-KB rules shown beside the farmer's dates (`backend/app/planner/research.py`).
  They never change plan status. Only exact date/day patterns are parsed; anything else goes to `other` with its English source text.
- `/speech/interpret` returns the validated extraction, not yet the proposed `proposals[]` list. Audio input (Gemini hears the clip, backend design §8.2) is a proposed change, not built: clip ≤ 30 s and ≤ 256 KB (413 above). Public endpoints are rate-limited (429 + `Retry-After`, backend design §10a).
- Errors: one envelope `{error: {code, message, field_paths}}`; KB out of scope 422, KB missing/altered 503.

## 1. Common conventions

- Base path `/api/v1`; JSON UTF-8; schema version `1.0`. Stable opaque string IDs; positive integer revisions/versions. Never derive identity from translated labels or list position.
- All model fields listed below are required unless marked optional. Nullable means the key remains present with `null`; omitted is not unknown. Empty arrays mean none. Reject extra request fields, invalid enums and nonfinite numbers.
- Gregorian dates are `YYYY-MM-DD`. Agricultural dates are local calendar dates without UTC conversion. System timestamps are RFC3339 UTC. Weather days retain `time_standard: "LST"`; do not shift them through Egyptian daylight-saving time.
- API locale is `ar-EG` or `en`. Canonical dates, IDs and numeric values do not change with locale. Quantities carry explicit units; no silent hectare/feddan conversion.
- `EvidenceStatus = verified | proposed | open`; `ConfirmationStatus = unconfirmed | confirmed | confirmed_unknown`. These are independent axes. A confirmed report is not a verified measurement.
- `PlanStatus = feasible | rejected | needs_review`. UI translates these consistently; do not add an ambiguous `valid` flag.
- Scientific assertions link to versioned sources/locators. Code rules also identify their specification basis; mathematical conflicts need no invented agronomy citation.

### Primitive records

| Record | Fields and invariants |
|---|---|
| `SourceRef` | `source_id: string`, `locator: string` (page/table/section or exact fixture section). Source metadata resolves in the pinned source manifest. |
| `Fact<T>` | `value: T\|null`, `unit: string\|null`, `unknown_reason: string\|null`, `origin: farmer_report\|field_measurement\|published_study\|illustrative\|derived\|unknown`, `evidence_status: EvidenceStatus`, `confirmation_status: ConfirmationStatus`, `source_refs: SourceRef[]`. Null value requires a nonempty reason; known value requires reason null. Units required for quantities; non-quantities use null. Derived facts include source/input dependencies in the enclosing result. |
| `PlanRef` | `plan_id: string`, `plan_version: positive integer`. |
| `InputRef` | `scenario_id: string`, `scenario_revision: positive integer`, `plan_ref: PlanRef`. |
| `DependencyRef` | `input_ref: InputRef`, `catalogue_version: string`, `rules_version: string`; replay/forecast extend this with their own versions. |
| `Explanation` | `code: string`, `parameters: object` validated per code, `source_refs: SourceRef[]`. Authored Arabic/English templates render the same parameters. No arbitrary advice text from a model. |

Unknown-value example (valid JSON; a single `Fact<number>`, not a complete scenario):

```json
{
  "value": null,
  "unit": "dS/m",
  "unknown_reason": "no_field_measurement",
  "origin": "unknown",
  "evidence_status": "open",
  "confirmation_status": "confirmed_unknown",
  "source_refs": []
}
```

## 2. Catalogue and confirmed input

`CatalogueResponse`: `schema_version`, `catalogue_version`, `rules_version`, `source_manifest_version`, `crops: CropProfile[]`, `rules: RuleDefinition[]`, `sources: SourceMetadata[]`. SourceMetadata follows DATA_SPEC's source manifest, including URL, hash/version, scope, locator and terms status; unresolved metadata is explicit.

`CropProfile`: `profile_id`, `crop_id` (`wheat|berseem|grain_maize|grain_sorghum`), `purpose` (`grain|forage|seed`), `names: {ar-EG: string, en: string}`, `cultivar: Fact<string>`, `applicability`, `calendar`, `demand`, `sequence_indicators`, `rule_ids: string[]`. The grouped fields follow DATA_SPEC: separately typed trial observations, recommended intervals and assumed/source-supported mappings; nullable stages/Kc with reasons; sourced family/legume/root descriptors. A retained profile can have unresolved eligibility. Catalogue presence does not imply recommendation permission. Do not borrow a grain profile for forage.

`RuleDefinition`: `rule_id`, `version`, `effect: hard|preference|review`, `required_for: planning|etc|explanation`, `evidence_status`, `applicability`, `source_refs`, `explanation_code`. Applicability records locality, land class, crop purpose/cultivar and relevant management conditions with explicit unknowns. Rule evaluator code owns execution, not user-provided expressions.

`ScenarioInput`:

| Field | Type / constraint |
|---|---|
| `origin` | `illustrative\|farmer_confirmed`; demo confirmation never changes illustrative origin. |
| `issue_date` | Date. Fixture issue date is fixed, not replaced by today's date. Locale is not part of the input (§0). |
| `site_id`, `field_id` | Stable IDs; one field, no subdivisions/intercropping in this prototype. Weather query point is not a parcel measurement. |
| `area` | `Fact<number>` with `unit: ha\|feddan\|qirat`, positive when known, kept in the unit the farmer confirmed. |
| `soil` | Object of facts: `texture`, `salinity`, `ph`, `drainage`, `water_table`; measurement metadata preserves depth/method/source. A published soil is never assigned as measured field soil. |
| `irrigation` | `mode: Fact<string>`, `availability: Fact<string>`, `restrictions: Fact<string>[]`; unknown delivery/reliability stays unknown. |
| `production_requirements` | Array `{requirement_id, purpose, quantity: Fact<number>, season_ids: string[]}`; requirements are not predicted production. |
| `seasons` | Exactly four `SeasonInput` records, `order` 1–4, distinct stable IDs, consecutive season labels. Unknown dates allowed as facts; known structurally impossible same-season dates fail validation. Cross-season occupancy conflicts are valid planner inputs. |
| `commitments` | `Commitment[]` below. |
| `exploration` | `ExplorationChoice[]` below; absent permission is not permission to change. |
| `priority_order` | Ordered unique codes from `minimize_changes`, `understand_demand`, `understand_sequence`; locks always precede negotiable priorities. No combined score. |

`SeasonInput`: `season_id`, `order`, `season_label`, `crop_id: Fact<string>`, `purpose: Fact<string>`, `profile_id: Fact<string>`, `sowing_date: Fact<date>`, `harvest_or_cut_date: Fact<date>`, `crop_end_exclusive: Fact<date>`, `release_date: Fact<date>`, `preparation_days_after_release: Fact<integer>`. Non-null identities resolve to compatible catalogue entries. Preparation is nonnegative; unknown is not zero. Crop end excludes removal/preparation; release is first free field date. The assumed day after a cut is labelled illustrative, never automatically verified.

When known, require sowing <= harvest/cut < crop_end_exclusive <= release. These are structural interval checks, not validation of the declared crop calendar. Soil texture/drainage are string facts; salinity/pH/water-table depth are numeric facts. Each measured soil fact additionally carries `measurement: {sample_date: date|null, depth_cm: {from: number, to: number}|null, method: string|null, unknown_reasons: object}`; null metadata needs a field-specific reason. Preserve raw measurement units/methods; do not compare incompatible EC extractions or invent conversions. Non-measured facts use `measurement: null`.

`Commitment`: `commitment_id`, `season_id`, `kind: crop|purpose|occupation_through|harvest_or_cut_date`, `protected_value: Fact<string>`. Date-valued kinds use ISO dates. Confirmation is explicit; no preference can override a lock.

`ExplorationChoice`: `choice_id`, `season_id`, `field: sowing_date|crop_id|profile_id`, `allowed_values: string[]` (nonempty, unique, typed/validated by field). Only discrete choices are enumerated initially. Crop/profile changes must preserve protected purpose and resolve applicability. Unsupported branches remain review-required or uninstantiated, not fabricated plans.

`Confirmation`: `explicit: true`, `method: touch|keyboard|voice`, `locale`, `presentation_version: string`. Voice confirmation means a separate explicit confirmation action, not mere transcript arrival. Server sets confirmation time. Known submitted facts must be confirmed; nulls must be confirmed_unknown. Scientific evidence status is never upgraded by this action.

`ScenarioSnapshot`: `schema_version`, `input_ref`, `input: ScenarioInput`, `confirmation: Confirmation`, `confirmed_at: UTC timestamp`, `catalogue_version`, `rules_version`. Snapshots are immutable. The server assigns IDs and starts revision/plan_version at 1; each accepted material confirmation increments both by one initially, even for soil-only changes. Do not copy the revision from a fixture ID into production state blindly.

## 3. Minimum first-slice endpoints

Only these domain endpoints are required for milestone 1 (MVP paths per §0). Local unconfirmed drafts do not need a general server draft API. A small `GET /health` is operational, not a new product feature.

| Endpoint | Request | Response |
|---|---|---|
| `GET /catalogue` | `?locale=` | `200 CatalogueResponse`, including `data_release` and the prompt catalogue. |
| `POST /scenarios` | `{input: ScenarioInput, confirmation: Confirmation, data_release}` | `201 ScenarioSnapshot` at revision 1; creates an explicitly confirmed scenario atomically. |
| `GET /scenarios/{id}` | None | `200 ScenarioSnapshot` for the current confirmed revision. |
| `POST /scenarios/{id}/revisions` | `{expected_revision, input: ScenarioInput, confirmation: Confirmation, data_release}` | `200 ScenarioSnapshot`; full replacement input becomes the next revision atomically. `409` if `expected_revision` is not current. Changed locks rejected initially. |
| `POST /scenarios/{id}/promise-test` | `{revision, data_release}` and `?locale=` | `200 PlanningResult` for that revision, stored; compute from saved facts, never client-supplied statuses. `409` if the revision is not current. |
| `GET /results/{id}` | `?locale=` | `200` stored result rendered in the requested language, with computed `current: boolean`. |

First-slice scope: confirmed UH-001 → actual backend evaluation → real bilingual conflict explanation. The initial planner must report required unknowns and zero feasible alternatives; fuller candidate enumeration can follow. An empty list with incomplete search is not an exhaustive infeasibility proof. Lock changes remain unavailable until the explicit acknowledgment flow below is implemented.

Example Promise Test request (`POST /scenarios/{id}/promise-test?locale=ar-EG`), assuming the server returned revision 1:

```json
{
  "revision": 1,
  "data_release": "meg-2026-11-14.1"
}
```

This release name is a proposed example identifier, not a claim of an existing data release.

## 4. Planner result and UH-001 acceptance

`RuleEvaluation`: `rule_id`, `rule_version`, `effect`, `required_for`, `outcome: pass|fail|unknown|not_applicable`, `season_ids: string[]`, `commitment_ids: string[]`, `explanation: Explanation`, `missing_input_paths: string[]`. A source-backed not_applicable decision is not an unknown disguised as a pass.

`PlanEvaluation`: `plan_ref`, `status: PlanStatus`, `checks: RuleEvaluation[]`, `preserved_commitment_ids: string[]`, `assumptions: Explanation[]`. All applicable hard failures take precedence over unresolved checks; unknown required planning checks otherwise produce needs_review. Preference failures alone do not reject. Missing ETc coefficients alone do not determine planning status.

`Candidate`: `candidate_id`, `kind: timing_variant|crop_change|combined`, `plan: SeasonInput[4]`, `changes: {season_id, field, before: Fact, after: Fact}[]`, `evaluation: PlanEvaluation`, `tradeoffs: Explanation[]`. Candidate plan references are immutable server result snapshots, not confirmed farmer selections. Unsupported shifted endpoints become unknown; old intended endpoints can be described in changes but cannot masquerade as supported recalculations.

`PlanningResult`: `schema_version`, `result_id`, `dependencies: DependencyRef`, `created_at`, `current: PlanEvaluation`, `feasible_alternatives: Candidate[]` (0–2, each feasible), `review_investigations: Candidate[]` (each needs_review), `rejected_candidates: Candidate[]` (each rejected), `search: {status: complete|incomplete, evaluated_count: integer, scope_choice_ids: string[], uninstantiated_choice_ids: string[], limit_reason: string|null}`. Search completeness is only relative to the declared scope. Lists must not silently promote review candidates into offered feasible repairs.

UH-001 input truth is defined once in [REFERENCE_SCENARIO.md](../product/reference-scenario.md). Required mapping/checks:

| Item | Expected contract value |
|---|---|
| Origin / issue | `illustrative`, ``; 1 ha; Sakha research point. |
| P0 seasons | Berseem forage  → cut 2027-05-20/release 2027-05-21; grain maize 2027-05-15 → harvest 2027-09-20/release 2027-09-21; wheat grain 2027-11-20 → harvest 2028-04-25/release 2028-04-26; sorghum grain 2028-06-01 → harvest 2028-09-21/release 2028-09-22. Dates are illustrative intentions. |
| Locks | Berseem occupation/final cut through 20 May 2027; season-2 maize grain and season-3 wheat grain crop/purpose commitments. |
| P0 status | `rejected`: same-field maize sowing precedes protected berseem cut. Return unresolved soil, irrigation, cultivar/stage, sorghum and forage-quantity reasons too. |
| Calendar arithmetic | Assumed release 2027-05-21 plus seven days = 2027-05-28. This is conditional arithmetic, not agronomic approval. |
| R1 / R2 | S2 sowing 2027-05-28 / 2027-06-01; both `timing_variant`, `needs_review`; changed harvest/release mapping unresolved. |
| Feasible alternatives | `[]`; no validated repairs. No invented season-2→3 or season-3→4 collision. |
| S4 maize exploration | Permitted but uninstantiated until profiles/dates support a candidate; report in search metadata. |
| Forecast / completion | `not_applicable`; save review draft, not approve a feasible recommendation. |

Example conflict explanation fragment (not an entire PlanningResult):

```json
{
  "code": "sowing_before_protected_cut",
  "parameters": {
    "season_id": "s2",
    "sowing_date": "2027-05-15",
    "protected_cut_date": "2027-05-20"
  },
  "source_refs": [{"source_id": "UH-001-v1", "locator": "sections 2-3"}]
}
```

## 5. Later endpoints and result contracts

Implement these with their feature milestones, not as first-slice boilerplate. Endpoint names are reserved; provider-specific transport remains contingent on provider review.

| Endpoint | Request / result boundary |
|---|---|
| `POST /replays` | InputRef, candidate/result references, baseline PlanRef, requested block IDs, dataset release and mapping/calculation versions → ReplayResult. Server resolves immutable plans. |
| `POST /forecast-assessments` | InputRef, permitted near-term action dates, issue date → ForecastResult; applicability checked before expensive inference. |
| `POST /evidence-cards` | InputRef, planning result ID, nullable replay ID, nullable forecast ID → saved review/unapproved EvidenceCard. No implicit approval. |
| `GET /evidence-cards/{id}` | Saved card plus current/superseded/revoked state. |
| `POST /scenarios/{id}/approvals` | Expected revision, PlanRef, evidence card ID, explicit Confirmation → approved record after transactional currentness/feasibility checks. |
| `POST /scenarios/{id}/approval-revocations` | Expected revision, approval ID, explicit action → revoked record. Retain historical snapshot, revoke current authority. |
| `POST /scenarios/{id}/commitment-changes` | Expected revision, complete proposed input, Confirmation, explicit acknowledgments `{commitment_id, previous_value, new_value}` → new confirmed snapshot. Validate all and only changed locks; recompute before new approval. |
| `POST /speech/interpret` | `{question_id, answer_type, locale, transcript, context}` → SpeechProposal. Superseded 14 Nov: audio clip, sent to Gemini (backend design §8.2). Not stored or logged. See BACKEND_DESIGN §8. |
| `POST /speech/tts` | `{locale, code, params}` → `{status, audio_url, template_version, voice, cached}` or `unavailable` with reason. No caller-supplied free text. See BACKEND_DESIGN §9. |
| `GET /forecast` | `?action_dates=` (comma-separated ISO dates) → ForecastResult derived from the ML bundle. Replaces `POST /forecast-assessments` in the MVP. |

`ReplayResult`: `result_id`, `dependencies`, `plan_refs`, `baseline_ref`, `plan_statuses`, `status: available|partial|unavailable`, `dataset_release`, `source_manifest_version`, `et0_method_id`, `kc_method_id: string|null`, `mapping_version`, `coverage_policy_version`, `shared_blocks: {block_id, anchor_year, start_date, end_date}[]`, `exclusions: {block_id, reason_code}[]`, `metrics`, `paired_differences`, `assumptions`, `reason_codes`. Each metric has `metric_id`, plan/block reference, `value: number|null`, `unit`, `status: available|unavailable`, `reason_code: string|null` and source/method references. Missing value requires reason. No common eligible blocks means unavailable. Partial means explicitly identified metrics unavailable, not silently incomparable periods.

Pair differences are candidate minus baseline within the same block. Summaries identify metric, number of paired blocks, spread and reversals. Temperature exposure risk labels require sourced thresholds. Missing coefficients/stages suppress ETc; no misleading zero. Hypothetical rejected-plan diagnostics retain status and cannot imply achievable savings. Exact mapping/metric definitions follow SCIENCE, not ad hoc frontend calculations.

MVP forecast source: the backend reads the ML team's `forecast_bundle.json`, whose schema is the Pydantic `ForecastBundle` defined in BACKEND_DESIGN §6. `ForecastResult` additionally carries `method`, `method_kind: baseline|trained_ml`, `model_ref: string|null`, `data_through` and `skill`. `ForecastRecord` additionally carries `lead_day` (1–7). `adapter_run_id` and `source_vintage` move to bundle-level `model_ref` and `data_through`. The rest of this paragraph and the next remain the semantic rules.

`ForecastResult`: `dependencies`, `status: available|unavailable|stale|not_applicable`, `reason_codes`, `issue_date`, `input_cutoff: date|null`, `experimental: true`, `records: ForecastRecord[]`. Available results contain exactly seven dated records per target (`tmax_c`, `et0_mm_day`) for D+1…D+7. Non-available results expose no actionable records. Reason codes distinguish model absence, timeout, invalid/missing history, expired targets and outside-horizon choice.

`ForecastRecord`: `issue_date`, `input_cutoff`, `target_date`, `variable`, `unit` (`degC|mm/day`), finite ordered `q10`, `q50`, `q90`, `model_revision`, `adapter_run_id`, `source_vintage: {dataset_release, retrieved_at, sha256}`, `experimental: true`, `stale: boolean`. Preserve daily LST convention. Validate the cutoff-to-target bridge: the recorded D−7 setup needs 14 prediction steps to reach D+7. Quantiles are experimental, not calibrated farmer confidence guarantees; do not sum daily quantiles into weekly quantiles. Never label climatology output as Chronos output.

`EvidenceCard`: `evidence_card_id`, `input_ref`, `planning_result_id`, `replay_id: string|null`, `forecast_id: string|null`, `plan_status`, `decision_state: review_draft|unapproved|approved|revoked`, `currency: current|superseded`, `preserved_commitment_ids`, `changes`, `assumptions`, `outstanding_checks`, `source_refs`, `takeaway: {template_id, template_version, parameters}`, `created_at`. A review draft may retain a rejected plan; saving it does not make its status needs_review or feasible. Approved requires feasible and current. Approval does not imply scientific validation. Audio generation failure returns explicit unavailable status while preserving the saved card; it does not satisfy spoken-takeaway acceptance.

`SpeechProposal`: `proposal_id`, `base_input_ref: InputRef|null` (null for new intake), `locale`, `proposed_fields`, `ambiguities: {field_path, reason_code}[]`, `transcript: string|null`, `transcript_retained: boolean`, `provider_id`, `status: ready|needs_clarification|unavailable`. Proposed facts always unconfirmed. No retained raw recording by default. Ignore responses for superseded input or interrupted recognition sessions. Silence never confirms; a negation must not silently alter a lock.

## 6. Versions, errors and approval safety

Store scenario head and immutable snapshots in ordinary SQLite tables. Check expected_revision and write the next revision atomically. A successful material confirmation invalidates dependent current approval; a failed save leaves server state unchanged and UI marked unsaved. Local edits immediately mark prior results non-current in the working UI and stop playback. Unchanged language/presentation edits do not increment material revisions. Validate evidence/source metadata against trusted releases; client-supplied `verified` labels cannot upgrade farmer reports or override catalogue facts.

MVP (§0): idempotency keys and sessions are deferred; `expected_revision` provides retry safety. The remainder of this paragraph applies only if they are reintroduced. Idempotency-Key is required for state-changing POSTs. Look it up by session, endpoint and key, retaining a request-content fingerprint; repeated identical input returns the original result, different content under the same key returns 409. Protect approval/revocation races in a transaction; same expected revision alone does not replace checking current approval state. Server-owned status, timestamps and versions cannot be supplied as proof by the client.

Changing catalogue/rules/data/calculation dependencies makes affected results stale for the active configuration; retain old records for reproducibility. Recompute required dependencies and reconfirm before approval. Client accepts a response only if input and dependency references match its active request. Approvals verify all referenced results belong to that snapshot and are current. Forecast absence and unavailable optional ETc do not themselves block approval of an otherwise feasible plan; missing critical planning evidence does.

Use additive compatible schema evolution within v1; coordinate enum additions with generated clients. Breaking semantics require a new major API version. Stable operation IDs and schema-validated shared fixtures are checked in CI. Generated types do not replace runtime validation.

Error envelope: `{error: {code: string, message_key: string, field_paths: string[], retryable: boolean, request_id: string, current_revision: integer|null}}`. No stack traces, secrets or raw recordings in errors/logs.

| HTTP | Meaning |
|---|---|
| 200/201 | Successful operation, including a rejected/needs_review planning result or an explicitly unavailable optional capability. |
| 400 | Invalid request framing, such as missing required idempotency key. |
| 401/403 | Missing session authorization or forbidden access/lock action in the remote demo. |
| 404 | Record absent or not accessible to this session. |
| 409 | Stale revision/dependencies, mismatched idempotency payload, unconfirmed lock change or ineligible approval. |
| 422 | Invalid shape/type/unit/date, unresolved identifiers or structural invariants. Cross-season conflicts belong in PlanningResult, not 422. |
| 429 | Bounded rate/resource limit; retry metadata supplied. |
| 503 | Core operation unavailable (for example persistence failure); no success claim. |

Expected tests: schema round-trip/unknowns, four-season identity/order, lock preservation, UH-001, late-response races, idempotency, approval/revocation and failed saves, common replay blocks/leap policy/units, forecast dates/staleness, identical bilingual parameters and speech ambiguity/recovery. Examples here describe expected behavior, not executed acceptance results.
