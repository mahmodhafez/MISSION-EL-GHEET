# ML ↔ backend contract

**Read this if…** you produce forecasts (ML team) or serve them (backend). This is the only
interface between the two sides.

Status: **Proposed **, needs review by Amr, Refaat and Mahmoud. Owner: Yahya.
Consolidates [backend design §6](backend-design.md), [core integration](core-integration.md)
§forecast, and the [dataset manifest](../ml/dataset-manifest.md). Where those disagree, this doc
proposes the answer and lists it under "Decisions needed".

---

## 1. The boundary in one picture

```
ML side (ml/, own venv, any libraries)              Backend (no torch, no sklearn)
───────────────────────────────────────              ─────────────────────────────
train / evaluate (research, anything goes)
        │
publish_daily_bundle()  ── validates against ──►  contracts/forecast_bundle.v1.schema.json
        │                                                    ▲
        ▼                                                    │ same schema
data/forecasts/forecast_bundle.json  ─────────────►  load_bundle() → status → GET /api/v1/forecast
data/forecasts/forecast_bundle.provenance.json
```

- **The only thing that crosses is two JSON files.** The backend never imports ML code and never
  runs a model. ML never imports backend code and never calls the API.
- No bundle file is a valid state. The backend returns `unavailable` and everything else
  (planner, replay, Evidence Card) still works.
- A forecast can never change plan feasibility, locks or crop eligibility. It only adds context
  to near-term actions on a plan that's already feasible.

## 2. Files

| File | Written by | Committed? | Notes |
|---|---|---|---|
| `contracts/forecast_bundle.v1.schema.json` | Yahya (exported from the Pydantic model) | Yes | The single schema both sides validate against |
| `contracts/examples/bundle.valid.climatology.json` + `bundle.invalid.*.json` | Yahya | Yes | Fixtures for both sides' tests |
| `data/forecasts/forecast_bundle.json` | ML publisher only | One reviewed demo bundle, yes | Written atomically (temp file + rename) |
| `data/forecasts/forecast_bundle.provenance.json` | ML publisher | With the bundle | Traceability sidecar (§4) |

Research outputs (prediction CSVs, model files, metrics) stay under `ml/` and are **not** the bundle.

## 3. `forecast_bundle.json` v1

```json
{
  "schema_version": "1",
  "method": "climatology_doy366_pm15",
  "method_kind": "baseline",
  "model_ref": null,
  "issued_at": "2026-11-14T06:00:00Z",
  "issue_date": "2026-11-14",
  "site_id": "sakha",
  "data_release": "meg-shared--v1",
  "data_through": {"tmax_c": "", "et0_mm_day": ""},
  "valid_until": "2026-11-15",
  "skill": {
    "assessment_id": "diag-2019-2021-36origins",
    "assessment_period": "/",
    "n_forecasts": 252,
    "mae": {"tmax_c": 0.0, "et0_mm_day": 0.0},
    "reference_method": "persistence",
    "reference_mae": {"tmax_c": 0.0, "et0_mm_day": 0.0},
    "interval_coverage_80": {"tmax_c": 0.0, "et0_mm_day": 0.0}
  },
  "experimental": true,
  "records": [
    {"variable": "tmax_c", "unit": "degC", "target_date": "2026-11-15",
     "lead_day": 1, "q10": 21.4, "q50": 23.0, "q90": 24.6}
  ]
}
```

The numbers above are **placeholders showing shape only**. Real values come from the evaluation run.

| Field | Type / rule |
|---|---|
| `schema_version` | `"1"` exactly. Breaking changes → `"2"` + both sides updated together. |
| `method` | Exact name of what produced the numbers. Never call a baseline a trained model. |
| `method_kind` | `baseline` \| `trained_ml` |
| `model_ref` | Model/adapter identity; `null` for baselines. |
| `issued_at` | RFC3339 UTC timestamp of publishing. |
| `issue_date` | Local calendar date (D). Lead day 1 = D+1. |
| `site_id` | `sakha` (the only site). |
| `data_release` | Release ID the inputs came from; must match the manifest the method used. **New field** (see Decision 4). |
| `data_through` | Last real input date per target. Must not be invented. |
| `valid_until` | Last date the bundle may be shown as current (Africa/Cairo). |
| `skill` | Required. The method's own scores **and** a reference method's scores on the same keys and period. A bundle without `skill` is rejected. |
| `experimental` | Always `true`. |
| `records` | Exactly **14**: 2 variables × lead days 1–7, one per (variable, lead_day). |
| `records[].variable` / `unit` | `tmax_c`/`degC` or `et0_mm_day`/`mm/day`. No other pairs. |
| `records[].target_date` | = `issue_date + lead_day`. |
| `records[].q10, q50, q90` | Finite numbers, `q10 ≤ q50 ≤ q90`. `q50` is the median. |

## 4. Provenance sidecar

`forecast_bundle.provenance.json`: `bundle_sha256`, `data_release` + manifest SHA256, input
file hashes, method/model revision, protocol ID (`meg-daily7-ridge-v1`), fit period, calibration
status, code commit, and a free-text `limitations` list. The backend checks `bundle_sha256` and
otherwise only stores it for the Evidence Card.

## 5. What the backend rejects (→ `unavailable`, reason `bundle_invalid`)

Schema failure · wrong `schema_version` · not exactly 14 records · duplicate (variable, lead) ·
wrong unit · non-finite value · crossed quantiles · `target_date ≠ issue_date + lead_day` ·
missing `skill` · sidecar hash mismatch · file over 1 MiB.

## 6. How the backend serves it

`GET /api/v1/forecast?action_dates=2026-11-16,2026-11-18` → `ForecastResult`. The status is checked in this order:

| # | Status | When |
|---|---|---|
| 1 | `not_applicable` | No requested action date is within D+1…D+7 of today. **UH-001 lands here** (decisions months ahead), whether or not a bundle exists. |
| 2 | `unavailable` | Bundle missing (`bundle_missing`) or invalid (`bundle_invalid`). |
| 3 | `stale` | Today (Africa/Cairo) is after `valid_until`, or the requested dates aren't covered by this bundle. No records returned; dates still reported. |
| 4 | `available` | Records for the requested dates + `method`, `method_kind`, `skill`. |

The backend re-reads the file when its modification time changes, so no restart is needed. It
behaves the same for every method; choosing which method to publish is the ML team's decision.

## 7. Who does what

| # | Task | Owner | Blocks |
|---|---|---|---|
| 1 | Pydantic `ForecastBundle` → export `contracts/forecast_bundle.v1.schema.json` + valid/invalid example files | Yahya | everyone below; **first deliverable** |
| 2 | `ml/src/meg_ml/publish.py`: `publish_daily_bundle(bundle, output) -> Path`; validates against the schema, writes atomically, writes the sidecar | Amr | — |
| 3 | Climatology adapter producing 14 records for any issue date (Refaat's 366-slot ±15 method, unchanged) | Mahmoud | — |
| 4 | Skill block for climatology vs persistence on the 36 diagnostic origins (2019–2021) using Refaat's scorer | Mahmoud / Refaat | — |
| 5 | Backend `forecast/bundle.py` (load + validate + mtime reload) and `forecast/service.py` (status table above) + tests on the example files | Yahya | — |
| 6 | Optional Ridge experiment: research only, **not published** (point-only, see Decision 2) | Mahmoud, at Amr's go | — |

**The ML team can start tasks 3 and 4 now.** Neither needs the schema file or the backend.

## 8. Decisions needed (Amr, with Refaat)

1. **Can a current bundle exist at all?** Weather data ends . History-based methods
   (persistence, Ridge, Chronos) need context up to D−7, so they can't be current in mid-November.
   Options: (a) publish **calendar-only climatology** for today, labelled as such; (b) Refaat
   fetches fresh POWER data as a *new* release; (c) publish nothing, so the app shows `unavailable`.
   Proposed: (a), and (b) only if there's time.
2. **Point-only methods.** Ridge and persistence give no quantiles. Proposed: keep quantiles
   required in v1, so they stay research-only. Making `q10`/`q90` nullable would be a v1 change.
3. **Skill period.** Backend design §6.1's example uses the consumed Jul–Oct 2026 Chronos numbers.
   Proposed: report the 2019–2021 diagnostic period by default, and label the consumed period if it's shown.
4. **`data_release` in the bundle.** Proposed as a new required field so a forecast is tied to its inputs.
5. **Status order.** §6.2 of backend design checks `unavailable` first; core-integration checks
   the horizon first. Proposed: horizon first (table above), so UH-001 is always `not_applicable`.
6. **Schema location.** Proposed: top-level `contracts/`, not `ml/contract/`, because both sides own it.

After review, these answers go into `docs/decisions.md` and backend design §6 gets updated to match.
