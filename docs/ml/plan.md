# Final execution plan — 

**Read this if…** you're doing any ML or forecast work before the deadline.

Status: Current,  · Owner: Amr. Last reviewed .

Deadline: **14 November, 12:00 Cairo**. Functional application target: **today**. This package narrows the existing blueprint; it does not authorize a second planner or change approved HTTP contracts. [MODEL_SELECTION](model-selection.md) owns model decisions; [DATASET_MANIFEST](dataset-manifest.md) owns the one data/evaluation protocol; role files reference them rather than redefining them.

## Decision and actual state

Keep Amr/Astra's standalone `meg_core` planner assignment, Karim's Promise Test semantics, frozen POWER historical evaluation and Yahya's documented FastAPI adapter. **Adopt Refaat's existing `climate_data` loader, seasonal climatology and keyed evaluator.** Add only one conditional CPU Ridge experiment. Do not install or train Chronos for the deadline. Keep existing Chronos/LoRA evidence and its negative result.

Refaat's actual delivered research location is `C:/Users/Amr Hany/Downloads/ML_HANDOFF.zip`, not an unspecified folder. All 28 ZIP members were inventoried; all seven Python files, documentation, manifests and result metadata were inspected. It contains no notebooks, trained weights or new ML architecture. It is a role-specific export, **not the complete underlying project**: `data/sakha_daily.csv`, rebuild pipeline, original raw weather and a mentioned backend climate evaluator are absent. Their existence elsewhere is not assumed. Originals remain untouched. Available evidence is enough for the selected common experiment; no need to wait for the missing full project.

Current checkout still has no `packages/meg-core` or implemented `meg_ml`/backend. That does not negate work in Astra's separate workstream. Coordinate its exact branch/path before integration, never recreate or overwrite it. The interrupted earlier dependency installation installed no Pydantic/NumPy/sklearn/pytest/torch in `.venv`. No training or app integration has run in this task.

## Verified reuse

- Refaat archive SHA256: `6990e8e2ef02db325812773f607e6e96cf027b820ee851f887d2b5e1a14cff4b`.
- All **27 manifest-listed files** match their hashes; the manifest itself is the 28th ZIP member. The older packaged QA report says 26 verified files; current direct count is 27. Do not edit the original report.
- Supplied checker passed five commands, including **10 tests**, on installed Python 3.13.5. Baseline reference, predictions and metrics were byte-identical to supplied outputs. [Current verification](refaat-verification.json).
- Both targets on all **7,670 dates** in Refaat's fit/validation files match Amr's frozen weather CSV numerically exactly. Same point, units, source hashes and ET0 method; no spatial/data expansion.
- A new bounded standard-library release assembler, [prepare_shared_release.py](../../ml/tools/prepare_shared_release.py), creates `data/local/shared--v1` with 30 byte-preserved files and a manifest; no model weights. Three tests passed after first failing for the missing builder. This is data packaging, not a new scientific calculation.

## Single implementation sequence and ownership

| Priority / order | Owner | Work / output | Budget / dependency |
|---|---|---|---|
| P0 1 | Refaat | Verify/share canonical release and extraction manifest; training-ready split CSVs already exist | 1 h; starts now, no installs |
| P0 2 | Amr + Astra | Continue existing KB loader, generator, Promise Test and historical evaluator in `meg_core`; no duplicate in `meg_ml` | Main workstream, 4–6 h; release and shared contracts |
| P0 3 | Mahmoud | Reproduce Refaat baseline, add persistence and thin adapter; send working evidence to Yahya | ≤1 h; common release, CPU |
| P0 4 | Amr + Yahya | Agree adapter imports, validate JSON, wire unavailable ML plus real historical evidence and saved draft | 2 h alongside backend; no model required |
| P1 5 | Refaat | Build leakage-safe train/development rows and features as specified centrally | ≤1.5 h after P0 data; no GPU |
| P1 6 | Mahmoud | One Ridge grid and diagnostic score after Amr's explicit compute go | ≤90 min including implementation/run; maximum 10 min fitting; stop for backend |
| P0/P1 7 | Amr | Accept/reject artifact, review paired errors and resource use; package only eligible outputs | ≤1 h; no required GPU work |
| P0 8 | Amr + Yahya/Astra | Integrated real JSON → API → Fieldlight flow, missing-model/offline cases | Reserve ≥2 h tonight |
| P2 | Nobody before deadline | New LoRA, LightGBM, C3S, weekly 1–4 experiments, multigrid, ensembles | Deferred; no installations |

**Compute allocation:** Amr owns the heaviest useful work—planner integration, acceptance and any necessary large-data/archived-model inspection. His verified RTX 3050 Laptop has 4096 MiB, driver 621.14; no torch/CUDA runtime was installed or tested. GPU work has weak expected benefit here. Mahmoud gets bounded CPU Ridge, not GPU training, and returns to Yahya's backend work after at most 3 ML hours. Refaat gets data preparation/validation; ask for his hardware report before allocating extra compute, never infer it from Amr's computer.

## Cairo stop/go schedule

- **Today 15:30:** release shared; Astra worktree/path and shared types agreed; baseline reproduction available. If later, execute immediately without extending optional work.
- **18:00:** standalone non-fixture planner/replay JSON working or defects identified. If missing, suspend P1 and focus on integration.
- **21:00:** real app reaches review-draft save, even with no forecast model. No mock scientific success. Freeze optional ML if this fails.
- **Tomorrow 09:00:** backend/frontend integrated, real data and error states tested; no new model exploration.
- **10:00:** release candidate freeze; repair only blockers.
- **11:15:** final restart/offline/demo rehearsal and submission preparation. Keep 45 minutes before noon.

## Explicit narrowing of earlier blueprint

The final deadline protocol is **daily Tmax/ET0, D+1…D+7**, not weekly W1…W4. Refaat already implements it and Yahya's approved daily bundle supports it. The new Ridge therefore has **14 direct models**, not the blueprint's eight weekly models. Use Refaat's **366-slot median/quantile** calendar method, not the proposed 365-slot mean/weekly analog variant. These are deliberate research-scope decisions recorded here; old results remain untouched. No HTTP migration is required. No new fine-tuning is planned.

Agricultural KB statements remain source-scoped and pending runtime promotion; no new rule became approved through this ML review. Six real trial-template records can support explicitly hypothetical investigations, not universal recommendations. Missing field fit, durations/endpoints, clearance/preparation or irrigation facts remain unknown. UH-001 stays rejected; May 28/June 1 needs_review; zero validated repairs. Missing full SB-001/proposal affects only that regression case. NASA descriptive exposure never clears a required agronomic check.

## Immediate commands

All owners start from their role file: [Amr](tasks/amr.md), [Mahmoud](tasks/mahmoud.md), [Refaat](tasks/refaat.md). Yahya uses [contract handoff](../backend/core-integration.md). Existing commands are explicitly distinguished from implementation-target commands. [Integration checklist](integration-checklist.md) records what remains unverified.
