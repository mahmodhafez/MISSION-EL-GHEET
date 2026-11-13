# Amr — ML acceptance and planner integration

**Read this if…** you're Amr, or need to know Amr's ML/integration tasks.

Status: Assignment, . Last reviewed .

## A. Mission

Own final selection, protect Astra's existing planner workstream and deliver a real data-driven application. The hardest justified work is integration and scientific acceptance, **not GPU training**. Use [MODEL_SELECTION](../model-selection.md) and [one protocol](../dataset-manifest.md). Yahya remains backend lead; this task does not modify his files unilaterally.

## B. Environment setup

Target Python3.12.x (original evidence used3.12.14); standard-library verification also passed locally on3.13.5. Current machine verified RTX3050 Laptop4096MiB, driver621.14. GPU/CUDA execution is not validated. No PyTorch/CUDA installation required. Existing `.venv` is empty of research dependencies after interrupted installation.

Existing local commands from repository root:

```powershell
$py = 'C:/Users/Amr Hany/AppData/Roaming/uv/python/cpython-3.13.5-windows-x86_64-none/python.exe'
& $py --version
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
& $py -I -S -m unittest discover -s ml/tests -v
```

For eventual typed adapter work, create an isolated environment rather than changing research originals:

```powershell
py -3.12 -m venv .venv-amr
.venv-amr/Scripts/python.exe -m pip install pydantic==2.12.5
.venv-amr/Scripts/python.exe -c "import pydantic; print(pydantic.__version__)"
```

Pydantic is the approved schema library; the pin stabilizes serialization/schema generation. Installation commands are not claimed executed. If Python3.12 launcher is absent, use an existing3.12 interpreter path; standard-library P0 verification can use `$py` now. Linux equivalent uses `python3.12 -m venv .venv-amr` and `.venv-amr/bin/python`. Do not install NumPy/sklearn unless independently reviewing Ridge artifacts; use Mahmoud's exact pins if needed. No new environment downloads may delay P0.

## C. Data acquisition

Use `data/local/shared--v1` already assembled here. On another machine receive that directory and its manifest from Refaat. Weather source is frozen NASA POWER, exact files/checksums in DATASET_MANIFEST. The `refaat/` subdirectory contains the original checked code, fit/validation data and reference outputs. Do not download POWER again or rename new bytes to the frozen release.

Keep `docs/VALIDATION_ARTIFACTS.zip` and `C:/Users/Amr Hany/Downloads/ML_HANDOFF.zip` unchanged. No additional data outside the manifest becomes a feature without review. All application data and model outputs carry source/release/method identity.

## D. Model acquisition

P0 model is Refaat's local `climate_data.climatology.SeasonalClimatology`, estimated from the supplied fit CSV; CPU, no pretrained download. Existing Chronos checkpoint `amazon/chronos-2@29ec3766d36d6f73f0696f85560a422f50e8498c` is archival only. Recorded weight size477,930,472bytes; already in validation ZIP with SHA256 `ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42`. No extraction/install/new LoRA required. Offline fallback is local climatology/history or explicit forecast unavailable.

## E. Implementation ownership

Coordinate rather than duplicate Astra's `meg_core` planner/constraints/climate implementation. Own new `ml/src/meg_ml/publish.py`, `ml/src/meg_ml/contracts.py` and `ml/tests/test_publish.py`, only after Yahya reviews bundle compatibility. Reuse Refaat code via one vendored package/import route; do not copy its algorithm into a second implementation.

Implement `validate_research_run(run_dir: Path, expected_release: str) -> AcceptanceReport`; `publish_daily_bundle(bundle: ForecastBundle, output: Path) -> Path` validates schema/finite quantiles/14 dated rows/provenance/currentness and writes atomically. `ForecastBundle` is Yahya's approved shared schema, not a competing definition. Until supplied, keep publisher contract tests pending and no current-bundle claim. Research point-only Ridge does not satisfy it; do not fabricate intervals.

Check package outputs through [Yahya contract](../../backend/core-integration.md). ML package never imports planner code to recompute statuses and never writes candidate locks. Declare any source/package re-export naming with Astra/Yahya once; no parallel scientific implementation.

## F. Evaluation and compute gate

Read Mahmoud's exact-key diagnostic results and Refaat's feature/cutoff proof. Verify raw MAE/RMSE/bias and paired comparisons; retain losing results. Require the central protocol's stopping/promotion rules. No new inference or training occurs on consumed2026 dates to claim a fresh test.

Explicitly authorize only the bounded CPU Ridge run once the standalone generic planner and replay work and Mahmoud has backend time. Do **not** authorize new Chronos/LoRA today. If the app is behind at18:00, P1 stops. If a Ridge artifact is promoted for research, verify reproducibility from metadata and output key alignment; live application remains climatology/unavailable until bundle and scientific gates are met.

## G. Deliverables

- `ml/artifacts/acceptance-<run_id>/acceptance.json`: accept/reject reasons, hashes, per-target evidence, limitations.
- `ml/contract/forecast_bundle.schema.json`: export from Yahya's single shared definition when implemented.
- `data/forecasts/forecast_bundle.json`: **only if** a valid reviewed daily bundle exists; otherwise absence is intentional and backend returns unavailable.
- Integration report with actual package paths/commands, real non-fixture planner/replay run and UH-001 status checks; no frontend/backend edits owned by others.

## H. Completion criteria

App starts without torch, GPU or model weights. Real historical replay works; UNKNOWN remains unknown; no forecast changes feasibility. Invalid/stale/out-of-horizon model output is withheld. A saved Evidence Card references actual revision/release and has review status where required. Amr signs model rejection as readily as acceptance. Do not claim app integration from package tests alone.

## I. Time and dependencies

P0: integration/acceptance4–6h coordinated with Astra/Yahya. P1 acceptance≤1h after Mahmoud/Refaat deliver; no GPU workload. P2 deferred. First action: run the three release tests above, obtain Astra's actual branch/path, and send Yahya the contract file. Do not wait for a backend to test standalone data/forecast functions.
