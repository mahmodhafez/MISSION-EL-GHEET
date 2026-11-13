# Refaat — one training-ready release and scientific validation

**Read this if…** you're Refaat, or need to know the data-release tasks.

Status: Assignment, . Last reviewed .

## A. Mission

Provide real, traceable input files and leakage-safe feature/split artifacts. Your supplied package already has a useful CPU baseline and evaluator; preserve it. Do not produce a second weather dataset by redownloading or reserializing frozen evidence. [DATASET_MANIFEST](../dataset-manifest.md) is the single protocol.

## B. Environment setup

P0 uses Python3.11+ standard library; prefer the package's original3.12.14 or existing3.12.x. Current audit ran3.13.5 successfully. No GPU assumed; no package installation required for data preparation, CSV features or supplied tests.

```powershell
py -3.12 --version
py -3.12 -m venv .venv-data
.venv-data/Scripts/python.exe -c "import os,platform; print(platform.python_version(), platform.platform(), os.cpu_count())"
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
```

Optional hardware inventory: `nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader`; missing command is fine. Linux: `python3.12 -m venv .venv-data`, `.venv-data/bin/python`, `free -h`. Do not install torch/CUDA, NumPy or sklearn for P0. Extra available compute can independently verify hashes/QC and feature audits after hardware is known; it does not create independent training sites.

## C. Data acquisition

Actual delivered path: `C:/Users/Amr Hany/Downloads/ML_HANDOFF.zip`. Same archive should be shared to colleagues or send the small assembled release. SHA256 is recorded in FINAL_ML_PLANNER_PLAN. Original raw POWER and frozen weather are in `docs/VALIDATION_ARTIFACTS.zip`; prefix `work/validation_/`. Extract only frozen `weather_et0.csv` and `weather_et0_2026_Jan_Oct.csv` for common runtime, preserve their bytes. Raw `power_sakha_2001_2025_LST.json` and `power_sakha_2026_Jan_Oct_LST.json` stay local for numerical checks, with corresponding provenance files. No need to distribute checkpoints or full ZIP.

Existing commands from repo root on a machine without the assembled output:

```powershell
.venv-data/Scripts/python.exe ml/tools/prepare_shared_release.py --refaat "C:/Users/Amr Hany/Downloads/ML_HANDOFF.zip" --science docs/VALIDATION_ARTIFACTS.zip --output data/local/shared--v1
.venv-data/Scripts/python.exe -m unittest discover -s ml/tests -v
```

This workspace already has that release; do not overwrite it. On receipt, compare all manifest file hashes. Expected target CSV schema `date,tmax_c,et0_mm_day`; LST,°C,mm/day. Keep `rh_percent`, already-normalized radiation/pressure and original ET0 sensitivity columns in archived weather. A typed loader maps names without rewriting source files.

`ML_HANDOFF.zip` is not your full project: `sakha_daily.csv` and rebuild pipeline are absent even though release metadata references them. Supply the complete source project separately only if useful; **do not block today's release**. Its missing backend evaluator is not assumed implemented or reusable. The current assembly combines your actual files with Amr's already verified frozen CSVs.

## D. Model acquisition

None. You own data and scientific checks, not new GPU training. Reuse local climatology/evaluator for consistency checks; do not install/download model weights. Offline operation is supported by supplied archives. Missing source pages remain unresolved; no fabricated calibration/labels.

## E. Implementation

Own `ml/src/meg_ml/{data,features,splits}.py`, corresponding tests, and `data/local/features-daily7-v1/`. Keep research originals untouched. Public signatures: `load_release(path: Path) -> DatasetRelease`; `build_features(context: tuple[DailyTarget,...], target_date: date) -> tuple[float,...]`; `build_examples(release: DatasetRelease, protocol: ExperimentProtocol) -> ExampleSet`.

Implement central38-feature order with training-only context. Emit keyed X/y tables, origins, exclusion counts, feature_schema and manifest; do not fit StandardScaler yourself—Mahmoud fits it on each allowed train fold. Precompute no full-dataset means/trends. Distinguish inner fit/tune and final fit/diagnostic rows. Every example records cutoff, context and label bounds. Reject overlapping train-label/validation cutoffs and wrong units. Never expose future QC fields to predictors.

Implementation-target command (after modules exist, not currently executable):

```powershell
$env:PYTHONPATH='ml/src;data/local/shared--v1/refaat'
.venv-data/Scripts/python.exe -m meg_ml.data --release data/local/shared--v1 --protocol meg-daily7-ridge-v1 --output data/local/features-daily7-v1
.venv-data/Scripts/python.exe -m unittest discover -s ml/tests -p 'test_data*.py' -v
```

Also review `docs/planner/agronomy-kb.v0.1.json` with Astra: source/locator/units/cultivar/management scope, observed calendar versus transferred assumption, applicability and all required gaps. Provide a source review ledger; do not silently promote pending rules to approved or modify planner code. One field and four seasons remain the planner scope. Crop-specific response labels are absent.

## F. Evaluation

Verify delivered targets match frozen NASA-derived data (already checked7670dates×2; keep automated guard). Test duplicates,missing dates,fill−999,nonfinite values,leap day,wrong units,modified bytes and wrong issue windows. Test feature invariance when rows after cutoff change; training scalers/thresholds must not depend on validation. Check all actual split boundaries and target days using the central protocol.2022–25 is inspected reserve;2026 consumed quarantine, not untouched test.

Source QA flags are review evidence, not independent station truth. The original cross-platform byte regeneration failures must not be relaxed; runtime uses frozen bytes. No new score constitutes evidence of irrigation saving or yield improvement.

## G. Deliverables

- `data/local/shared--v1/` and manifest, shared intact across three machines.
- `data/local/features-daily7-v1/{feature_schema.json,origins.csv,manifest.json}` plus keyed X/y partition files as centrally specified.
- `ml/artifacts/data-review-v1/quality_report.json`: counts,units,missingness,alignment,leakage checks and failed/unrun checks.
- `ml/artifacts/data-review-v1/agronomy_gaps.json`: assertion IDs,source access/review status,scope and unresolved requirement; no fabricated values.
- Machine capability report, exact Python version and reproduction commands.

## H. Completion criteria

Mahmoud can verify release and reproduce504 baseline predictions without downloads. Features have38 documented fields and correct cutoffs; changing future data cannot alter them. All generated files are checksum-bound, original files unchanged, and agronomic uncertainty remains visible. Train-ready delivery is files plus tests, not only notes.

## I. Time and dependencies

P0 release≤1h; P1 features≤1.5h; source/gap review≤1.5h in parallel with Astra. Start now with existing builder/supplied tests. If optional features slip, hand over already working fit/validation targets and baseline immediately. Do not block historical analysis for optional crop-response/C3S data. First action: verify the release and share it with Amr/Mahmoud; report actual hardware.
