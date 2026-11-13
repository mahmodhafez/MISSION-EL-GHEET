# Refaat / Ahmed — KB, scientific data and climatology

**Read this if…** you need the scientific release, KB loader or baseline owner.

Status: Confirmed by Amr, 2026-11-13. Refaat and Ahmed are the same person.

- Own agricultural KB validation and `packages/meg-core/src/meg_core/knowledge/load.py`; retain applicability, source evidence and explicit unknowns.
- Own scientific data engineering/source verification, `data/` and `packages/meg-core/src/meg_core/climate/load.py`.
- Own the existing climatology baseline and scientific validation of ML outputs; an optional bounded Ridge regression experiment requires Amr's go after P0 work. Coordinate exact ML files before implementation.
- NASA historical/climatology subset is recovered locally at `data/local/shared-20261113-v1/` and Git-ignored; [canonical dates/hashes](../dataset-manifest.md). Do not claim it is the complete application/KB release.
- Coordinate planner evidence with Amr + Astra, historical evaluator inputs with Mahmoud and shared Pydantic/API contracts with Yahya (final approval pending).
- No trained forecast is required for P0. Do not block planner/historical implementation on an optional experiment.

Acceptance: immutable validated KB/weather inputs, source/hash/unit checks and honest missing-evidence reasons. Keep draft KB evidence draft until scientifically approved. Existing climatology tests must remain reproducible.
