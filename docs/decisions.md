# Decisions

**Read this if…** you need to know what's settled. Newer entries win over older ones and over any
spec text that disagrees. Append new decisions at the bottom of the right section; don't edit old
ones. Mark a replaced decision **(superseded by …)** instead.

Last reviewed . Sources: the archived status and handoff files and the specs linked below.

---

## Product and scope

| Date | Decision | By | Detail |
|---|---|---|---|
| 11 Nov | Sakha (Kafr El-Sheikh) is the research locality. Published soil ≠ farmer's field. | User/Amr | [handoff](archive/handoff-.md) |
| 11 Nov | Keep all four crops (wheat, berseem, grain maize, grain sorghum) and all seven features (FR-01…07). Removing one needs Amr's approval. Sorghum stays evidence-gated. | User/Amr | [product](product/product.md) |
| 11 Nov | PRODUCT, SCIENCE, DATA_SPEC, ML_EXPERIMENT approved as working specs. | User/Amr | [handoff](archive/handoff-.md) |
| 11 Nov | UH-001 (Uncle Hussein) is the reference case: P0 `rejected`, R1/R2 `needs_review`, zero feasible alternatives. | Team | [reference scenario](product/reference-scenario.md) |
| 11 Nov | Egyptian Arabic + English voice is core. No speech provider or paid service chosen yet. | User/Amr | [product](product/product.md) |

## Architecture and backend

| Date | Decision | By | Detail |
|---|---|---|---|
| 11 Nov | Architecture approved: React/TS/Vite/Tailwind; modular FastAPI/Pydantic; SQLite; generated TS types from OpenAPI; no event sourcing, queues, microservices or accounts. | User/Amr | [architecture](backend/architecture.md) |
| 11 Nov | First slice = 5 domain endpoints: catalogue, create scenario, get scenario, new revision, Promise Test. | User/Amr | [API contracts §3](backend/api-contracts.md) |
| 12 Nov | Backend design D1–D8 approved: pure planner/replay; 3-table SQLite, single `revision`, no idempotency keys/sessions in MVP; ML only via precomputed `forecast_bundle.json`; backend-owned bilingual templates; browser Web Speech first; deterministic transcript parsing (no LLM); cached TTS endpoint; one `data_release` token. | User | [backend design](backend/backend-design.md), [API §0](backend/api-contracts.md) |
| 13 Nov | Shared domain logic goes in standalone `meg_core` (and `meg_ml`) packages; backend adds thin adapters later. **Standalone Python work doesn't wait for the backend.** Partly overrides the `backend/app/planner/` layout in backend design §2. | Amr | [blueprint §9.1](planner/blueprint.md) |

## Design

| Date | Decision | By | Detail |
|---|---|---|---|
| 11 Nov | Interaction model: **Season Path / سكة المواسم**, "Show, Speak, Choose, Confirm". No typing needed in the primary journey. | User/Amr | [design](design/design.md) |
| 11 Nov | UX Phase 1 approved, with five refinements (optional commitment-first, progressive seasons, distinct states…). | User/Amr | [UX phase 1](design/ux-phase-1.md) |
| 12 Nov | Visual identity: **Fieldlight Hybrid** with botanical arched season cards. Replaces the sand/terracotta palette in design.md §2. | Amr | [fieldlight](design/fieldlight.md), commit `7f7fb6b` |

## ML and data

| Date | Decision | By | Detail |
|---|---|---|---|
| 11 Nov | Keep the Chronos-2 + LoRA experiment and its **negative** result (climatology won). Forecasting stays independent of planning. | User/Amr | [ML experiment](ml/ml-experiment.md) |
| 13 Nov | For the deadline: Refaat's seasonal climatology is the forecast baseline; one optional CPU Ridge experiment (Mahmoud, ≤3 h, only at Amr's go). New Chronos/LoRA, LightGBM and C3S deferred. | Amr | [ML plan](ml/plan.md), [model selection](ml/model-selection.md) |
| 13 Nov | One data/evaluation protocol: `meg-daily7-ridge-v1` on release `meg-shared--v1`. | Amr/Refaat | [dataset manifest](ml/dataset-manifest.md) |

## Process

| Date | Decision | By | Detail |
|---|---|---|---|
| 13 Nov | Cleanup happens on `cleanup/yahya-preintegration`; `handoff/full-project-precleanup-` stays frozen; nothing merges to `main` automatically. | Amr | [handoff](archive/handoff-/YAHYA_HANDOFF.md) |
| 13 Nov | Docs reorganised into `docs/<area>/`; one `AGENTS.md` for all agents; per-area status files; git rules in `rules/git.md`. | Yahya | this cleanup |
