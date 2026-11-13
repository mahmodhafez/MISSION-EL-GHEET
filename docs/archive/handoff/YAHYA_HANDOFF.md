# Complete pre-cleanup handoff for Yahya

Repository: https://github.com/Amrhany06/MISSION-EL-GHEET

Recovery branch: `handoff/full-project-precleanup-`. Use the branch HEAD shown by GitHub; the final publication SHA is also supplied in the delivery message. Do not merge cleanup into main automatically or rewrite this recovery branch. Create a separate cleanup branch.

## Reading map

- Product/science authority: `docs/product/product.md`, `SCIENCE.md`, `DATA_SPEC.md`, `ML_EXPERIMENT.md`, `REFERENCE_SCENARIO.md`, `HANDOFF.md`, and current `PROJECT_STATUS.md`.
- Backend: `docs/backend/architecture.md`, `BACKEND_DESIGN.md`, `API_CONTRACTS.md`. These are design/interface documents, not executable FastAPI/Pydantic/OpenAPI implementations.
- Planner: `docs/planner/blueprint.md`, `ASTRA_PLANNER_HANDOFF.md`, `PLANNER_SPEC.md`, `PLANNER_RESEARCH_HANDOFF.md`; evidence in `AGRONOMY_EVIDENCE.md` and `docs/planning/{agronomy-kb.v0.1,audit}.json`. Preserve conflicting/historical proposals for review; publication does not approve them.
- All eight ML handoffs: `docs/ml/plan.md`, `MODEL_SELECTION.md`, `DATASET_MANIFEST.md`, `INTEGRATION_CHECKLIST.md`, `AMR_ML_TASK.md`, `MAHMOUD_ML_TASK.md`, `REFAAT_ML_TASK.md`, `YAHYA_ML_PLANNER_CONTRACT.md`. These include the three individual assignments.
- UI: `docs/design/design.md`, UX/wireframe reviews, Phase 3 visual/refinement documents, `work/ux-phase-2/` and `work/ux-phase-3/`. Fieldlight HTML/CSS/JS, tokens, fonts/licenses, previews and verification scripts are preserved.
- Earlier ignored document copies: `work/publish_ux_/clean-checkout/docs/`, including its original `YAHYA_HANDOFF.md`. Historical archive docs/code: `archive-snapshot/`; treat their status statements as dated evidence.

## Code that exists

Scientific audit/regeneration source and tests are in `data/validation/`. Shared-release builder and tests are in `ml/tools/` and `ml/tests/`. Refaat's delivered climatology/evaluation/example source, tests, requirements and provenance exist in both `work/refaat-handoff-/` and `data/local/shared--v1/refaat/`; data payloads require the separate transfer. Historical training/evaluation/download code is under `archive-snapshot/work/validation_/`. Standalone UI prototypes and checks exist under `work/ux-phase-*`.

`backend/` and `frontend/` application trees are placeholders. No implemented integrated planner/API/persistence/React application was located in this repository. References to `meg_core` or teammate work in plans are not proof that those implementations are present. JSON catalogue/evidence and design tokens exist; executable shared schemas and generated clients remain implementation work. No runtime behavior or scientific finding was changed by this snapshot.

## Ownership and cleanup

Yahya: API, persistence/revisions and replay integration; Karim: planner/candidates/constraint tests; Amr: frontend/UI supervision, integration and ML; Refaat: data/evidence/numerical validation and ML; Mahmoud: bounded ML/baseline work per current individual assignment; Moaaz: assets/motion/storytelling. Earlier roster text remains historical; use current assignment files and confirm conflicts with owners.

On a separate branch Yahya may reorganize documents, source, fixtures and duplicate snapshots. Preserve originals in this recovery commit, maintain traceability and relative links, and coordinate interface/ownership changes. Do not silently combine alternate implementations or convert proposals into approved requirements.

## Fetch and begin cleanup

```sh
git clone https://github.com/Amrhany06/MISSION-EL-GHEET.git
cd MISSION-EL-GHEET
git fetch origin handoff/full-project-precleanup-
git switch --track origin/handoff/full-project-precleanup-
git rev-parse HEAD
git switch -c cleanup/yahya-preintegration
```

For an existing clone, first preserve any local edits, then run the fetch/switch commands (omit clone/cd). Never reset a dirty checkout. Obtain separate artifacts using `ARTIFACT_TRANSFER.md`. Inventories and checksums are in this directory. Missing source PDFs and environment/model limitations remain documented in `archive-snapshot/MISSING_ARTIFACTS.md`.
