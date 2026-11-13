# Rejected and deferred ideas

**Read this if…** you're about to propose something. Don't re-propose these without new
information. If you have new information, say what changed.

**Rejected** = decided against. **Deferred** = not for the hackathon MVP and can come back later.
Last reviewed .

---

## Product and planning

| Idea | Status | Why | Date / source |
|---|---|---|---|
| A combined "best farming score" to rank plans | Rejected | Hides trade-offs; no evidence supports one number | 11 Nov, [architecture](backend/architecture.md) |
| Showing a third alternative when evidence supports fewer | Rejected | Zero or one alternative is a valid answer; never fabricate | 11 Nov, [product FR-04](product/product.md) |
| Making UH-001 succeed (a feasible repair) | Rejected | Current evidence gives zero validated repairs; a second, *separate* evidence-backed scenario is the goal instead | 11 Nov, [reference scenario](product/reference-scenario.md) |
| Unrestricted chat; free-text advice from a model | Rejected | Advice must come from checked rules + authored templates | 11 Nov, [product](product/product.md) |
| Autonomous field/irrigation actuation | Rejected | Out of scope | 11 Nov, [product](product/product.md) |
| Extra HLS/IMERG satellite features | Rejected | Out of scope | 11 Nov, [product](product/product.md) |
| Treating ET0 as irrigation use, or claiming water/yield savings | Rejected | Scientifically wrong | [science](science/science.md) |

## Backend

| Idea | Status | Why | Date / source |
|---|---|---|---|
| Event sourcing, workflow engine, generic rule engine / user-written rule expressions | Rejected | Too heavy; explicit Python rules keyed by ID | 11 Nov, [architecture](backend/architecture.md) |
| DB server, Kubernetes, microservices, queues, user accounts | Rejected | Not needed for a local prototype | 11 Nov, [architecture](backend/architecture.md) |
| Handwritten duplicate API types on the frontend | Rejected | Generate from OpenAPI | 11 Nov, [architecture](backend/architecture.md) |
| Running PyTorch / model inference inside the backend | Rejected | ML talks to backend only via `forecast_bundle.json` | 12 Nov, [backend design D3](backend/backend-design.md) |
| LLM for transcript interpretation | ~~Deferred~~ **Reversed 14 Nov: adopted** (Gemini strict extraction) | Was: deterministic per-question parsers for MVP | 12 Nov, D6; reversed 14 Nov, [decisions](decisions.md) |
| Idempotency keys, sessions, CSRF, approval revocation | Deferred | `expected_revision` gives retry safety in MVP | 12 Nov, D2 |
| Regenerating the weather/ET0 CSV with renamed columns | Rejected | Ship original frozen bytes + typed adapter | 13 Nov, [blueprint D04](planner/blueprint.md) |

## ML

| Idea | Status | Why | Date / source |
|---|---|---|---|
| New Chronos-2 / LoRA training before the deadline | Deferred | Already lost to climatology; GPU time not justified | 13 Nov, [model selection](ml/model-selection.md) |
| LightGBM | Deferred | Extra dependency over one Ridge experiment | 13 Nov, same |
| C3S seasonal outlook | Deferred | No validated Sakha skill/data | 13 Nov, same |
| AquaCrop crop modelling | Deferred | Needs field calibration | 12 Nov, [blueprint](planner/blueprint.md) |
| Training on duplicated grid cells / invented outcomes | Rejected | Scientifically invalid | 13 Nov, [model selection](ml/model-selection.md) |
| Weekly forecast means squeezed into the daily API records | Rejected | Needs its own schema | 12 Nov, [blueprint D06](planner/blueprint.md) |

## Design

| Idea | Status | Why | Date / source |
|---|---|---|---|
| Terracotta as the main action colour | Rejected | Reads like the "rejected" red | 12 Nov, [phase 3 options](reports/-phase-3-visual-options.md) |
| Dashboard tiles instead of arched season cards | Rejected | Fieldlight Hybrid keeps botanical arches | 13 Nov, [frontend handoff](planner/frontend-handoff.md) |
| Drag as the only way to change a date | Rejected | Needs keyboard/touch alternatives and explicit confirmation | 11 Nov, [architecture](backend/architecture.md) |
| Compulsory language-choice screen at start | Rejected | Arabic default + header switch | 12 Nov, [phase 3 options](reports/-phase-3-visual-options.md) |
