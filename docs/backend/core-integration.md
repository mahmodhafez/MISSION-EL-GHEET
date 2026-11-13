# Yahya — stable planner/climate/ML integration handoff

**Read this if…** you're wiring `meg_core` planner/climate or Refaat's `climate_data` into the backend.

Status: Proposed  · Owner: Yahya. Last reviewed .

Preserves [API §0](api-contracts.md) and [backend design](backend-design.md) D1–D8. Available code and proposed adapters are listed separately below. The `meg_core` planner package is not in this repo yet, so no integration has been tested. Planner ownership is confirmed as Amr + Astra (2026-11-13; see docs/team.md).

## 1. Packages and exact call boundaries

| Boundary | Callable / import path | Availability |
|---|---|---|
| Existing baseline | `from climate_data.climatology import SeasonalClimatology, DailyTarget`; `SeasonalClimatology.from_csv(path: Path\|str) -> SeasonalClimatology`; `.for_date(day: date\|str) -> dict` | Reused unchanged in assembled `refaat/` directory; tested |
| Existing data/scoring | `from climate_data.evaluation import load_diagnostic_data, seasonal_predictions, score_predictions`; `load_diagnostic_data(path)->DiagnosticData`; `.contexts()->Iterator[(ForecastWindow,tuple[DailyTarget,...])]`; `score_predictions(ds,forecasts)->(list[dict],dict)` | Tested research interface; backend must not score requests against future truth |
| Shared core types | `meg_core.contracts`: ScenarioSnapshot,SearchPolicy,PlanningResult,ResolvedPlan,ReplayPolicy,ReplayResult,KnowledgeBase,WeatherDataset | Blueprint/Astra implementation target; obtain exact exported schema from that workstream |
| Knowledge/weather | `meg_core.knowledge.load.load_knowledge(release_dir: Path, expected_release: str)->KnowledgeBase`; `meg_core.climate.load.load_weather(release_dir: Path, expected_release: str)->WeatherDataset` | Core targets, Refaat data compatible; do not duplicate loaders in backend |
| Planner | `meg_core.planner.service.plan(snapshot: ScenarioSnapshot,kb: KnowledgeBase,policy: SearchPolicy)->PlanningResult` | Amr + Astra target; pure, deterministic, no ML dependency |
| Historical | `meg_core.climate.evaluate.evaluate_history(plans: tuple[ResolvedPlan,...],weather: WeatherDataset,policy: ReplayPolicy)->ReplayResult` | Core target; pure, no forecast dependency |
| Optional ML | `meg_ml.baselines.predict_persistence(context,window)->list[Prediction]`; `meg_ml.ridge.predict_ridge(artifact,context,window)->list[Prediction]` | Refaat / Ahmed optional research targets, CPU only; Ridge not published to daily API without quantile contract |
| Bundle publishing | `meg_ml.publish.publish_daily_bundle(bundle: ForecastBundle,output: Path)->Path` | Amr target; schema-validated atomic output, research notebooks unnecessary |
| Backend consumption | `app.forecast.bundle.load_bundle(path: Path)->ForecastBundle\|BundleUnavailable`; `app.forecast.service.assess_forecast(request: ForecastAssessmentRequest,bundle: ForecastBundle\|BundleUnavailable)->ForecastAssessment` | Proposed callable names for Yahya's already approved modules; thin adapters, no new HTTP endpoint |

Local reuse path today: set `PYTHONPATH` to `data/local/shared--v1/refaat` for `climate_data`. For final packaging, vendor its three public module files byte-for-byte once inside the ML distribution and record their original hashes. Do not install a similarly named package from PyPI. `meg-core`/`meg-ml` use blueprint paths; no competing `meg_ml.planner` or second agricultural catalogue. Core cannot import ML, FastAPI, SQLite or torch. Backend can depend on core shared Pydantic types; no research dependencies.

## 2. Inputs and output schemas

Use approved Fact/ScenarioSnapshot/PlanningResult/ReplayResult models unchanged in meaning. Their **single** exported Pydantic JSON Schema is authoritative. Backend may re-export these in `app/schemas/`, adding HTTP transport models without reimplementing domain validation. No silent enum/version/endpoint changes. New scope-preview and `hypothetical_review` fields from the blueprint remain proposed additive contract work coordinated with Astra/Yahya; runtime only after the shared schema is agreed.

Planner input requires four ordered season facts, field context, explicit unknown reasons, confirmed locks and exploration permissions. `SearchPolicy` includes raw_budget256 and deterministic ordering version. `ResolvedPlan` has immutable plan/candidate ref,release, four seasons and prior evaluation; server resolves it, not arbitrary client status. `ReplayPolicy` supplies requested metrics,comparison basis,anchor range,coverage/leap/endpoint policies. Unknown crop endpoints cannot become whole-plan metric values.

Forecast adapter models below are **internal proposed models**, mapped to existing `GET /api/v1/forecast?action_dates=` and the existing ForecastResult envelope. No public API replacement:

```text
ForecastAssessmentRequest (extra fields forbidden):
  now: RFC3339 UTC timestamp; issue_date: ISO date
  action_dates: unique ISO date list (1..28)
  site_id: literal "sakha"
  expected_data_release: nonempty string
ForecastAssessment:
  status: available | unavailable | stale | not_applicable
  reason_codes: string[]
  issue_date: ISO date | null; input_cutoff: ISO date | null
  experimental: literal true
  method: string | null; method_kind: baseline | trained_ml | null
  model_ref: string | null; data_through: object | null; skill: object | null
  records: ForecastRecord[] (empty for every non-available status)
```

`now` is supplied by server clock, never trusted from an HTTP client. Snapshot dependencies and `data_release` are attached by the service using existing `DependencyRef`. No locale in computation; renderer supplies Egyptian Arabic/English from codes/parameters.

Daily `ForecastBundle` remains BACKEND_DESIGN §6: `schema_version="1"`,method,method_kind,model_ref,issued_at,issue_date,site_id,data_through,valid_until,skill,experimental=true,records. Exactly14 records =2 variables×7 lead days. Record fields: variable (`tmax_c|et0_mm_day`),unit (`degC|mm/day` matched),target_date,lead_day1…7,q10,q50,q90 finite ordered. Target_date=issue_date+lead_day. No missing/duplicate keys. Bundle's `skill` belongs to that method and includes the same-period climatology comparison; absent skill invalidates the bundle.

Source manifest travels with the bundle as `forecast_bundle.provenance.json`, containing `bundle_sha256`,common data release/manifest hash,source file hashes,method/model revision,protocol ID,fit dates,calibration status,code hash and limitations. This **sidecar** adds traceability without changing the approved wire object. Proposed source-site mapping: bundle `sakha` maps only to dataset `sakha_31.10_30.95` with exact31.10/30.95; mismatch rejects. Validate sidecar before serving; a bundle byte change invalidates its association.

Current Ridge is point-only. A scalar fit cannot be relabelled q10/q50/q90 or given fake zero-width uncertainty. Do not publish it through this bundle. Research CSVs use Refaat's keyed scorer, as defined centrally. Weekly results and C3S are deferred and never coerced into daily records.

## 3. Valid examples and semantics

Valid internal request example (schematic call at a historical issue; not a current forecast):

```json
{"now":"T00:00:00Z","issue_date":"","action_dates":[""],"site_id":"sakha","expected_data_release":"meg-shared--v1"}
```

Valid internal response when no bundle was installed:

```json
{"status":"unavailable","reason_codes":["bundle_missing"],"issue_date":null,"input_cutoff":null,"experimental":true,"method":null,"method_kind":null,"model_ref":null,"data_through":null,"skill":null,"records":[]}
```

Existing Promise Test HTTP request remains:

```json
{"revision":1,"data_release":"meg-shared--v1"}
```

This request's release must equal the actual deployed application release; the assembly identifier above is illustrative until Yahya binds crop/rule files in the application release. A complete PlanningResult is produced by Astra's shared model, not a stub supplied here. Regression assertions: current.status=`rejected`, feasible_alternatives=[], two May28/June1 investigations=`needs_review`, protected May20 cut preserved. No status is selected by weather metrics.

Status reduction: any applicable hard failure→rejected; otherwise any mandatory planning topic unknown/uncovered→needs_review; otherwise feasible under checked documented constraints. Missing optional ETc alone does not reject a plan. Required agricultural applicability unknown cannot be waived by a good climate comparison or farmer confirmation. Save review draft for rejected/review plans; approval only feasible and current.

Historical replay reports actual frozen weather over mapped past blocks. `hypothetical_review` retains prior plan statuses. Crop days,temperature means/maxima,descriptive >=35/40°C counts,ET0 totals/rates and shared years retain units/denominators/exclusions/source refs. No yield,irrigation,heat-damage probability or generic risk score. Known agronomic requirements are checked in Promise Test; unsourced physiological thresholds remain unavailable.

## 4. Startup, availability and resource policy

Load/check small KB/weather release once; startup fails on invalid **core** source hashes/units. An absent/invalid optional model/bundle never fails the core app. Do not load torch or GPU models in FastAPI. Precomputed bundle only; no inference/training in HTTP request handling. On file change validate a complete new bundle+sidecar, then atomically swap the immutable snapshot; never serve partially written records. On invalid replacement return unavailable, not the old bundle presented as current. Serialize publication by one owner.

Proposed internal precedence: valid requested action outside supported D+1…7 horizon→not_applicable; otherwise missing/invalid bundle→unavailable; expired or issue-mismatched bundle→stale; otherwise available. For malformed bundle whose dates cannot be trusted, use unavailable, never derive a horizon from invalid metadata. UH-001's May2027 actions relative to fixture issue are not_applicable independent of model installation. Yahya should encode this precedence in shared tests to resolve older prose ambiguity.

For history-dependent methods require actual context through D−7 (or an explicitly revised protocol), not a made-up latest date. Current data endOct31, so Nov13 Ridge/Chronos cannot be called current. Calendar-only seasonal expectation may use its fixed fit reference without latest context, **only with explicit baseline method/source dates and limitations**; do not falsify data_through to D−7. Treat empirical quantiles as uncalibrated. No current bundle was published by this task.

Engineering bounds to measure: bundle<=1MiB,parse/validate<=1s,request budget2s,planner256 raw tuples. Use validated row/date limits before parsing scientific data; a malformed oversized file is unavailable. Pure core timeouts are service errors, not a complete-search result. Forecast timeout→unavailable. Cache historical metrics by exact plan refs/release/method/anchor selection; no GPU or network necessary. A 503 is for core operational failure; an optional capability unavailable remains200 with explicit status.

Map shared validation errors to422; stale scenario/release to409; unknown scientific information to typed unknown/unavailable values. Errors expose safe code/field paths, not stack traces or raw farmer input. Preserve revision/release currency and original source refs on Evidence Cards. Logs contain request IDs and timings, not transcripts or credentials.

## 5. Integration tests and commands

Runnable now, no backend required:

```powershell
python -m unittest discover -s ml/tests -v
Push-Location data/local/shared--v1/refaat
python verify_package.py
python -m unittest discover -s tests -p test_ml.py -v
python -m climate_data.ml_example --data data
Pop-Location
```

Adapter tests Yahya/Amr implement next: schema-generated example round-trip;14 dated records;wrong unit/nonfinite/crossed quantile/missing skill/changed sidecar reject;absent/invalid/stale/out-of-horizon branches;missing model does not prevent planner/replay;failed/review plans cannot be approved;late revision invalidates replay/card;source method/date survives bilingual rendering. Test with crafted synthetic bundle values clearly marked test-only, not demo forecasts.

Final backend command once implemented: backend's own test runner for `tests/unit/forecast`, `tests/api`, and core package tests. Exact command depends on Yahya's pyproject; do not claim an uncreated `make schemas` or test target ran. Export `ml/contract/forecast_bundle.schema.json` from his shared ForecastBundle and validate the published bundle against it. The planner/replay import names above are blueprint targets requiring a one-time mapping to Astra's actual code; no research notebook execution is required.
