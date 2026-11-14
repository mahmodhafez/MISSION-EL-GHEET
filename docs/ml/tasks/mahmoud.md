# Mahmoud — historical NASA evaluator / Season Replay

**Read this if…** you are implementing historical climate evaluation.

Status: Confirmed by Amr, 2026-11-13; implementation pending. Supersedes the earlier ML/Ridge assignment.

- Own `packages/meg-core/src/meg_core/climate/mapping.py` and `evaluate.py`, plus evaluator tests under `packages/meg-core/tests/`.
- Implement historical NASA Tmax/ET0 analysis and structured climate evidence using frozen weather; retain units, LST dates, coverage, paired anchors and exclusions.
- Coordinate typed interfaces with Yahya and loaders/source metadata with Refaat / Ahmed. Agricultural validation stays with Amr + Astra.
- Use the recovered, Git-ignored `data/local/shared-20261113-v1/` subset and its manifest; see [dataset specification](../dataset-manifest.md).
- No new ML training unless explicitly reassigned. No trained forecast is required for P0.
- Follow [blueprint §9.1](../../planner/blueprint.md) for existing target callables; shared contracts await Yahya's final approval. Do not alter API shapes independently.

Acceptance: deterministic historical evaluation with explicit missing coverage and structured evidence; focused mapping/evaluator tests. Never turn historical metrics into crop eligibility or agricultural status.
