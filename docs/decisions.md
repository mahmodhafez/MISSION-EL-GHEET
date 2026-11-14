# Decisions

**Read this if…** you need to know what's settled. Newer entries win over older ones and over any
spec text that disagrees. Append new decisions at the bottom of the right section; don't edit old
ones. Mark a replaced decision **(superseded by …)** instead.

Last reviewed . Sources: the archived status and handoff files and the specs linked below.

---

## Product and scope

| Date | Decision | By | Detail |
|---|---|---|---|
| 11 Nov | Sakha (Kafr El-Sheikh) is the research locality. Published soil ≠ farmer's field. | User/Amr | [handoff](archive/handoff.md) |
| 11 Nov | Keep all four crops (wheat, berseem, grain maize, grain sorghum) and all seven features (FR-01…07). Removing one needs Amr's approval. Sorghum stays evidence-gated. | User/Amr | [product](product/product.md) |
| 11 Nov | PRODUCT, SCIENCE, DATA_SPEC, ML_EXPERIMENT approved as working specs. | User/Amr | [handoff](archive/handoff.md) |
| 11 Nov | UH-001 (Uncle Hussein) is the reference case: P0 `rejected`, R1/R2 `needs_review`, zero feasible alternatives. | Team | [reference scenario](product/reference-scenario.md) |
| 11 Nov | Egyptian Arabic + English voice is core. No speech provider or paid service chosen yet. | User/Amr | [product](product/product.md) |
| 14 Nov | **The app offers only the four crops with reviewed evidence** (wheat, berseem, grain maize, grain sorghum), back in line with the 11 Nov scope. Rice, faba bean, sugar beet and cotton stay in the catalogue as research-only, with `kb_evidence: false`, and are not offered. Farmer-facing facts come only from the reviewed KB and NASA POWER. | Yahya | [candidate sources](agronomy/kb-candidate-sources-four-crops.md) |

## Architecture and backend

| Date | Decision | By | Detail |
|---|---|---|---|
| 11 Nov | Architecture approved: React/TS/Vite/Tailwind; modular FastAPI/Pydantic; SQLite; generated TS types from OpenAPI; no event sourcing, queues, microservices or accounts. | User/Amr | [architecture](backend/architecture.md) |
| 11 Nov | First slice = 5 domain endpoints: catalogue, create scenario, get scenario, new revision, Promise Test. | User/Amr | [API contracts §3](backend/api-contracts.md) |
| 12 Nov | Backend design D1–D8 approved: pure planner/replay; 3-table SQLite, single `revision`, no idempotency keys/sessions in MVP; ML only via precomputed `forecast_bundle.json`; backend-owned bilingual templates; browser Web Speech first; deterministic transcript parsing (no LLM); cached TTS endpoint; one `data_release` token. | User | [backend design](backend/backend-design.md), [API §0](backend/api-contracts.md) |
| 13 Nov | Text-to-speech provider for D7 is **ElevenLabs, used offline only**: all app audio is pre-generated from the reviewed templates once scenarios and templates are final; the running app never calls ElevenLabs. Voice choice still needs Amr's sign-off. | Yahya | [voice generation](backend/voice-generation.md) |
| 14 Nov | Backend is one package `backend.app` run from the repo root; the default data release is Refaat's reviewed Sakha KB (`sakha-agricultural-review-2026-11-14.1`) with 0 enforceable rules; Season Replay served at `/replay`. Final integration on `chore/final-integration`. | Yahya | [backend status](status/backend.md) |
| 14 Nov | **Gemini Flash interprets speech** (supersedes the “deterministic parsing, no LLM” part of D1–D8): the backend sends the transcript to Gemini, which returns a strict JSON extraction with `null` for anything not said; the backend validates every value and only proposes; readback and explicit confirm unchanged. `/speech/interpret` gains a list of proposals (proposed contract change). | Yahya | [backend design §8.3](backend/backend-design.md#83-interpretation-d6-gemini-extraction) |
| 14 Nov | ElevenLabs audio generation and listening review are done by Moaaz (media). | Yahya | [voice generation](backend/voice-generation.md) |
| 14 Nov | **Gemini hears the farmer's audio** (supersedes D5 browser Web Speech for input and the “transcript only, no audio upload” rule): the browser records one push-to-talk clip, the backend forwards it to Gemini, which returns the same strict extraction. Audio is not stored or logged. `/speech/interpret` accepts audio (proposed contract change). Not built yet. | Yahya | [backend design §8.2](backend/backend-design.md#82-speech-recognition-d5) |
| 14 Nov | **Public hosting for the judges, no password.** Paid and write endpoints get per-IP limits sized well above a judge's use, global daily ceilings, provider-side spending caps, and voice falls back to pictures when a limit is hit. Voice clips: 15 s per answer, 30 s for the opening sentence, 256 KB upload cap. Not built yet. | Yahya | [backend design §10a](backend/backend-design.md#10a-public-hosting-and-abuse-limits) |
| 14 Nov | **Hosting: frontend on Vercel, backend on Render's free plan kept awake by UptimeRobot**; frontend calls the backend directly (CORS limited to the Vercel URL). Rate limits and body caps built. | Yahya | [hosting](backend/hosting.md) |
| 14 Nov | **App voice = sentences recorded once with pauses where the changing words go, plus each changing word recorded once**; the browser plays piece + word + piece. One catalogue of every spoken sentence (`frontend/src/voice/catalogue.json` + backend templates). Generation stays offline (ElevenLabs or a human); sentences without clips use the labelled device voice. | Yahya | [voice build](../backend/scripts/voice_build/README.md) |
| 14 Nov | Voice slot-filling rules adopted: ask one missing field by name, never re-ask what was given, “I don't know” is an answer, show what was understood, cover the wait. | Yahya | [voice-first §2a](design/voice-first.md#2a-filling-in-missing-details-adopted-14-nov-yahya) |
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
| 13 Nov | Cleanup happens on `cleanup/yahya-preintegration`; `handoff/full-project-precleanup-` stays frozen; nothing merges to `main` automatically. | Amr | [handoff](archive/handoff/YAHYA_HANDOFF.md) |
| 13 Nov | Docs reorganised into `docs/<area>/`; one `AGENTS.md` for all agents; per-area status files; git rules in `rules/git.md`. | Yahya | this cleanup |
| 14 Nov | **Dependency rules:** minimum release age 14 days for every package and tool (enforced by pnpm `minimum-release-age` and pip `uploaded-prior-to`), exact pins, hashed lock files, wheels only, no install scripts, pnpm pinned by hash via corepack. | Yahya | [rules/dependencies.md](rules/dependencies.md) |
