# Separate scientific artifact transfer

No immutable public artifact download URL is available. Request exact files from Amr/Refaat using team file sharing; do not substitute freshly fetched weather or model revisions for frozen evidence. Nothing was deleted locally.

- `docs/VALIDATION_ARTIFACTS.zip`: current location is that path in Amr's project workspace; 468781522 bytes; SHA256 `d284b3162a2dd5bbde8bcb37ae3090adcf080a5d044a4e25b2c96836b4cee95f`. Contains frozen raw weather, derived ET0, saved predictions and base/adapted model weights. All 87 member names/sizes/checksums are in `ARCHIVE_MEMBERS.json`; `ARCHIVE_DISPOSITION.json` identifies which authored source/docs were additionally published under `archive-snapshot/` and which members require transfer.
- `ML_HANDOFF.zip`: source location recorded by the builder is `C:/Users/Amr Hany/Downloads/ML_HANDOFF.zip`; required SHA256 `6990e8e2ef02db325812773f607e6e96cf027b820ee851f887d2b5e1a14cff4b`. Request it from Refaat/Amr, or transfer the complete assembled `data/local/shared--v1/` directory including its manifest. The external ZIP's current availability was not independently checked in this repository inventory.
- Every excluded local raw JSON/CSV, including duplicate replay outputs and Refaat fit/diagnostic/reference CSVs, has its exact repository-relative current location, size, checksum and reason in `LOCAL_INVENTORY.json` (`decision=exclude`). Locations resolve from `C:/Users/Amr Hany/Downloads/MISSION EL GHEET/`. The assembled release's manifest and Refaat package manifests are published; package verification requires the separately transferred CSVs. Do not interpret a partial Git package as a complete dataset.
- Environments/caches/bytecode and generated logs/patches are excluded individually in the same inventory. They remain local and are not required source. Recreate environments from published requirements; original GPU environment portability is unverified.

After transferring both ZIPs (put the science ZIP at `docs/VALIDATION_ARTIFACTS.zip`):

```powershell
Get-FileHash docs/VALIDATION_ARTIFACTS.zip -Algorithm SHA256
Get-FileHash C:/transfer/ML_HANDOFF.zip -Algorithm SHA256
python ml/tools/prepare_shared_release.py --refaat C:/transfer/ML_HANDOFF.zip --science docs/VALIDATION_ARTIFACTS.zip --output data/local/shared-transfer-
python -I -S data/validation/audit_saved_evidence.py --archive docs/VALIDATION_ARTIFACTS.zip
python -I -S data/validation/regenerate_et0.py --archive docs/VALIDATION_ARTIFACTS.zip --period historical --output-dir work/yahya-replay/historical
python -I -S data/validation/regenerate_et0.py --archive docs/VALIDATION_ARTIFACTS.zip --period 2026 --output-dir work/yahya-replay/2026
```

Use fresh output directories. See `docs/science/reproducing.md` and `docs/ml/dataset-manifest.md` for method, tests, boundaries and expected hashes. The archive includes checkpoint/download provenance and scripts; historical training is not guaranteed bitwise reproducible and no new model experiment was run. Missing primary-source PDFs, original station observations and other never-created inputs cannot be obtained from this snapshot; consult `archive-snapshot/MISSING_ARTIFACTS.md` and source locators rather than inventing them.
