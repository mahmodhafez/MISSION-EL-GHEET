# Docs index

**Read this if…** you're looking for a document. Every doc is listed here with its status.

**Approved** = agreed spec, follow it · **Proposed** = awaiting a decision · **Frozen** = dated
evidence, never edited · **Archive** = superseded, history only.

---

## Start here

| Doc | What it's for |
|---|---|
| [status/README.md](status/README.md) | Phase, blockers, open questions; links to each area's status |
| [team.md](team.md) | Who owns what, who decides |
| [decisions.md](decisions.md) | Every settled decision, dated |
| [rejected.md](rejected.md) | Ideas already turned down or deferred |
| [glossary.md](glossary.md) | UH-001, P0, ET0, Astra… |
| [rules/working.md](rules/working.md) · [rules/git.md](rules/git.md) · [rules/docs.md](rules/docs.md) | How to work, branch/commit/PR, write docs |
- [rules/dependencies.md](rules/dependencies.md): supply-chain rules: 14-day minimum package age, exact pins, hashed locks, no install scripts.

## Specs by area

| Area | Doc | Status | Owner |
|---|---|---|---|
| Product | [product/product.md](product/product.md): purpose, FR-01…07, recovery checks | Approved 11 Nov | Amr |
| Product | [product/reference-scenario.md](product/reference-scenario.md): UH-001 inputs and expected result | Approved 11 Nov | Team |
| Product | [product/privacy.md](product/privacy.md): data and consent assumptions | Draft | Amr + Yahya |
| Science | [science/science.md](science/science.md): equations, intervals, evidence limits | Approved 11 Nov | Refaat |
| Science | [science/data-spec.md](science/data-spec.md): data files, schemas, provenance | Approved 11 Nov | Refaat |
| Science | [science/reproducing.md](science/reproducing.md): how to rerun the scientific checks | Current | Refaat |
| Science | [science/evidence-access.md](science/evidence-access.md): report hashes and local-only files | Current | Refaat |
| Backend | [backend/architecture.md](backend/architecture.md): system boundaries, journey, milestones | Approved 11 Nov | Yahya |
| Backend | [backend/voice-generation.md](backend/voice-generation.md): generating all app audio with ElevenLabs (gates, voices, run, checks) | Proposed 13 Nov | Yahya |
| Backend | [backend/backend-design.md](backend/backend-design.md): modules, SQLite, ML bundle, voice, i18n (D1–D8) | Approved 12 Nov; needs `meg_core` update (Q3) | Yahya |
| Backend | [backend/api-contracts.md](backend/api-contracts.md): wire types and endpoints (**§0 overrides**) | Approved 12 Nov | Yahya |
| Backend | [backend/ml-contract.md](backend/ml-contract.md): **the ML ↔ backend forecast bundle contract** | Proposed 13 Nov | Yahya |
| Backend | [backend/core-integration.md](backend/core-integration.md): backend ↔ `meg_core` / `climate_data` calls | Proposed 13 Nov | Yahya |
| Planner | [planner/blueprint.md](planner/blueprint.md): planner architecture, D01–D10, `meg_core` layout §9.1 | Proposed 13 Nov (Q5) | Amr / Karim |
| Planner | [planner/planner-spec.md](planner/planner-spec.md): rules, search, UH-001 walkthrough | Approved source copy 11 Nov | Karim |
| Planner | [planner/agronomy-evidence.md](planner/agronomy-evidence.md): source ledger | Current 11 Nov | Refaat |
| Planner | [planner/agronomy-kb.v0.1.json](planner/agronomy-kb.v0.1.json), [audit.json](planner/audit.json): machine-readable KB draft | Proposed | Refaat / Karim |
| Planner | [planner/research-handoff.md](planner/research-handoff.md): compatibility review of the planner research | Current 11 Nov | Karim / Yahya |
| Planner | [planner/implementation-handoff.md](planner/implementation-handoff.md): M1/M2 code, interfaces, tests, manual CLI, resume steps | Draft 13 Nov | Amr + Astra |
| Planner | [planner/frontend-handoff.md](planner/frontend-handoff.md): frontend tasks for the planner UI ("Astra") | Proposed 13 Nov | Amr |
| ML | [ml/plan.md](ml/plan.md): deadline execution plan | Current 13 Nov | Amr |
| ML | [ml/model-selection.md](ml/model-selection.md): which models are used, deferred or rejected | Current 13 Nov | Amr |
| ML | [ml/dataset-manifest.md](ml/dataset-manifest.md): the single data/evaluation protocol | Current 13 Nov | Refaat |
| ML | [ml/integration-checklist.md](ml/integration-checklist.md): tick-box acceptance list | Working checklist | Amr |
| ML | [ml/ml-experiment.md](ml/ml-experiment.md): Chronos-2/LoRA spec and actual results | Approved 11 Nov | Amr |
| ML | [ml/tasks/amr.md](ml/tasks/amr.md), [refaat.md](ml/tasks/refaat.md), [mahmoud.md](ml/tasks/mahmoud.md): individual assignments | Current 13 Nov | each person |
| ML | [ml/multigrid-proposal.md](ml/multigrid-proposal.md): multi-cell experiment | Proposed, not approved | Amr |
| Design | [design/design.md](design/design.md): Season Path interaction, accessibility, components (§2 colours superseded) | Approved 11 Nov | Amr |
| Design | [design/fieldlight.md](design/fieldlight.md): Fieldlight Hybrid visual rules and tokens | Approved 12 Nov (Q8) | Amr |
| Design | [design/ux-phase-1.md](design/ux-phase-1.md): journey review and refinements | Approved 11 Nov | Amr |
| Design | [design/voice-first.md](design/voice-first.md): voice rules, one-screen layout, Phase 4 page labs | Proposed 13 Nov | Amr |

## Reports (frozen, dated)

| Report | Topic |
|---|---|
| [2026-11-13-ml-plan-review](reports/2026-11-13-ml-plan-review.md) | ML plan review: consistency, data/code, methodology |
| [2026-11-13-voice-first-research](reports/2026-11-13-voice-first-research.md) | Voice-first UI evidence for low-literacy users; Web Speech on Android |
| [validation_accessibility_alignment](reports/validation_accessibility_alignment.md) | Accessibility and challenge alignment |
| [validation_models](reports/validation_models.md) | Why Chronos-2 + LoRA |
| [validation_agronomy](reports/validation_agronomy.md) | Agronomy evidence for Sakha |
| [validation_data_equations](reports/validation_data_equations.md) | POWER data and ET0 equations |
| [validation_equations_review](reports/validation_equations_review.md) | Independent ET0 review |
| [validation_model_execution](reports/validation_model_execution.md) | Actual LoRA training results |
| [MISSION_EL_GHEET_Validation_Verdict](reports/MISSION_EL_GHEET_Validation_Verdict.md) | Overall readiness verdict |
| [-scientific-validation-fixes](reports/-scientific-validation-fixes.md) | Science doc corrections |
| [-pre-push-science-audit](reports/-pre-push-science-audit.md) | Pre-push checkpoint review |
| [-wireframe-v2-review](reports/-wireframe-v2-review.md), [v3](reports/-wireframe-v3-review.md) | Wireframe iterations |
| [-phase-3-visual-options](reports/-phase-3-visual-options.md) | Three visual identities compared |

The first seven are byte-identical copies of files in the validation ZIP (hashes in
[evidence-access](science/evidence-access.md)), so their internal links point at the ZIP's
original layout.

## Archive

| Doc | Superseded by |
|---|---|
| [archive/project-status-.md](archive/project-status-.md) | `status/` |
| [archive/handoff-.md](archive/handoff-.md) | `decisions.md`, `team.md` |
| [archive/frontend-milestone-1-.md](archive/frontend-milestone-1-.md) | `status/frontend.md` (its event-start-gate research is still Q7) |
| [archive/handoff-/](archive/handoff-/) | Recovery snapshot inventory, artifact transfer and Yahya's handoff |

Older originals: branch `handoff/full-project-precleanup-` and `archive-snapshot/`.

## Old → new paths

Docs moved on . If a script or an old note uses a former path, see
[archive/path-map-.txt](archive/path-map-.txt).

- [13 November recovery and contract review](reports/2026-11-13-recovery.md): verified local subset, remaining contract decisions and implementation boundaries.
