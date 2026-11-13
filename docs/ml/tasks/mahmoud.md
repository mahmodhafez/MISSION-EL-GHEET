# Mahmoud — climatology adapter and one bounded Ridge comparison

**Read this if…** you're Mahmoud, or need to know the climatology/Ridge tasks.

Status: Assignment, . Last reviewed .

## A. Mission

Deliver a reproducible CPU baseline immediately, then one Ridge challenger only with Amr's compute go. ML time cap **3 hours total**; coordinate this window with Yahya and return to backend work. No primary Chronos assignment. Model/data authority: [MODEL_SELECTION](../model-selection.md), [DATASET_MANIFEST](../dataset-manifest.md).

## B. Environment setup

P0 baseline uses Python3.11+ standard library; prefer3.12.x matching Refaat's3.12.14. No pip install for it. Report hardware first; GTX1650Ti memory/driver/runtime are not assumed:

```powershell
py -3.12 --version
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
py -3.12 -c "import os,platform; print(platform.platform(), os.cpu_count())"
```

Missing `nvidia-smi` does not block CPU work. Do not install CUDA. For P1 only, after agreeing time and installation:

```powershell
py -3.12 -m venv .venv-ridge
.venv-ridge/Scripts/python.exe -m pip install numpy==2.2.6 scipy==1.15.3 scikit-learn==1.6.1 joblib==1.4.2 threadpoolctl==3.6.0
.venv-ridge/Scripts/python.exe -m pip check
.venv-ridge/Scripts/python.exe -c "import numpy,scipy,sklearn; print(numpy.__version__,scipy.__version__,sklearn.__version__)"
$env:OMP_NUM_THREADS='2'
$env:OPENBLAS_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
```

Pins freeze a conventional CPU Ridge stack compatible with Python3.12; not a newest-version claim. [sklearn1.6.1 dependencies](https://pypi.org/project/scikit-learn/1.6.1/), [NumPy2.2.6](https://pypi.org/project/numpy/2.2.6/). Linux uses `.venv-ridge/bin/python` and shell `export` for thread settings. No pandas/notebook/torch/lightgbm dependency. If offline and wheels unavailable, use standard-library baseline and stop P1; do not spend the evening fixing CUDA.

## C. Data acquisition

Receive the assembled `data/local/shared--v1` from Refaat; manifest binds original bytes. Inputs: `refaat/data/fit_targets.csv`, `diagnostic_validation_targets.csv`, `forecast_windows.csv`, `release.json`, and Refaat's generated feature files/manifest. Exact dates, units and hashes are centralized. No fresh NASA download, no2026 fitting, no QC future features.

Run existing code immediately from its copied package root:

```powershell
Push-Location data/local/shared--v1/refaat
py -3.12 verify_package.py
py -3.12 -m unittest discover -s tests -p test_ml.py -v
py -3.12 -m climate_data.evaluation --data data --output ../../../../ml/artifacts/mahmoud-baseline-v1
Pop-Location
```

Use a new output directory if already present. These commands work before `meg_ml` exists. Expected baseline:504 keyed rows, MAE2.534365°C/.583124mm/day, not the different2026 scores.

## D. Model acquisition

Climatology is local source code, no pretrained weights. Ridge is trained from scratch,14 small direct models; no download or fine-tuning. Save numeric coefficients/scalers in `ridge.npz` plus metadata. CPU and a few GB free RAM suffice as an engineering budget, to be measured. No GPU memory assumption is needed. Offline fallback: unchanged local climatology.

## E. Implementation

Own `ml/src/meg_ml/baselines.py`, `ridge.py`, `evaluate.py`, `cli.py` and corresponding `ml/tests/test_{baselines,ridge,evaluate}.py`. Refaat owns `data.py/features.py/splits.py`; Amr publisher/contracts. Do not edit Yahya's backend or Astra's planner.

Implement `predict_persistence(context, window) -> list[Prediction]`, `fit_ridge(train, validation, config) -> ModelArtifact`, `predict_ridge(artifact, context, window) -> list[Prediction]`. Reuse `climate_data.evaluation.score_predictions` for the final36-origin diagnostic, preserving original bytes in the reuse source. Keep predictor inputs context-only; validation truth belongs to scorer. Central protocol specifies all14 models,38 features,3 alphas,inner split,refit and units. Do not add residual targets, weekly aggregation,extra predictors or another search.

Implement CLI targets (not present yet; acceptance commands **after implementation**):

```powershell
$env:PYTHONPATH='ml/src;data/local/shared--v1/refaat'
.venv-ridge/Scripts/python.exe -m meg_ml.cli ridge --release data/local/shared--v1 --features data/local/features-daily7-v1 --output ml/artifacts/ridge-daily7-v1
.venv-ridge/Scripts/python.exe -m unittest discover -s ml/tests -v
```

No training until Amr explicitly approves the compute. CLI refuses existing output and writes run/predictions/metrics/model files only after successful validation. Do not make tests train on the entire dataset; use small synthetic mathematical regression cases for serialization/fit behavior, with labels clearly test-only.

## F. Evaluation

Central protocol is binding: inner2001–2015/2016–2018 selection, refit2001–2018,36 diagnostic2019–2021 origins; D−7 cutoff; D+1…7 real labels. Test feature-date maximum<=cutoff, purged boundaries, no validation fitting, exact key coverage, persistence hand calculation, scaler isolation, model save/reload prediction equality, missing-context unavailability and malformed predictions. No random split or recomputed2026 “test”.

Success includes a losing result. Compare per-target MAE/RMSE/bias/lead/season and paired uncertainty. Ridge point predictions have no calibrated quantiles and are research-only under current daily API. Stop after3 alphas,10minutes compute,or90minutes total P1; capture failures and return to backend. No LightGBM fallback search.

## G. Deliverables

`ml/artifacts/mahmoud-baseline-v1/{calendar_reference.csv,scored_predictions.csv,metrics.json}`; `ml/artifacts/ridge-daily7-v1/{ridge.npz,run.json,feature_schema.json,predictions.csv,metrics.json,comparison.json}` if authorized. Publish code/tests in your agreed branch; share ignored artifacts with manifest, not via Git weights. Report elapsed CPU/RAM and dependency freeze.

## H. Completion criteria

Refaat's10 tests pass; exact baseline reproduced; Ridge reproduces after reload and satisfies all leakage/key tests; comparison labels diagnostic and states winner/inconclusive honestly. Yahya receives baseline adapter/contract, not notebooks. No trained model is marked production merely because fitting succeeds.

## I. Time and dependencies

P0 baseline/reuse≤1h starts immediately with release. P1≤90min after Refaat's feature manifest and Amr's go; remaining30min handoff. Stop optional work if Yahya needs backend support or P0 app gate fails. First command is `verify_package.py` above; report hardware without assigning GPU jobs.
