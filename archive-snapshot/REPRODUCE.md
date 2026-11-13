# Reproducing the validation evidence

Packaged 11 November 2026. This is an evidence archive, not the application. Extract into a NEW directory and retain `outputs/` and `work/` paths. Keep the ZIP as the immutable original. Never rerun write-producing scripts against the only copy of the evidence.

## Contents and integrity

`ARTIFACT_MANIFEST.json` lists each original file, workspace-relative path, size and SHA256. Original files are byte-preserved. Generated archive-root notes are listed separately and are not self-hashed. Verify manifest hashes after extraction; ZIP CRC checks alone do not establish scientific validity.

Read `outputs/HANDOFF.md` for current approvals, the four specification snapshots for implementation requirements, and `outputs/validation_model_execution.md` / `outputs/validation_data_equations.md` for measured findings. Older audits retain historical not-yet-tested wording; later verdicts and execution records supersede that status. Packaging did not run experiments.

## Runtime preparation (only when reproduction is wanted)

Use Python 3.12, preferably the recorded 3.12.14, and an isolated environment. The original tested environment was Windows, PyTorch 2.9.1+cu128, RTX 3050 Laptop 4 GB and 24 GB system RAM. GPU/model scripts assume CUDA; CPU reproduction is not verified. Driver, package and numerical differences may prevent bitwise equality. No environment or dependency wheels are bundled.

From the extraction root, create an environment with `python -m venv .validation-venv`. Install the recorded CUDA build using `.validation-venv/Scripts/python.exe -m pip install torch==2.9.1+cu128 --index-url https://download.pytorch.org/whl/cu128`, then install the remaining frozen requirements using `.validation-venv/Scripts/python.exe -m pip install -r work/validation_2026-11-10/model_test/installed_requirements.txt`. These are future setup instructions, not commands executed during packaging. Network/package availability and NVIDIA driver compatibility remain prerequisites. Do not install a different version silently.

In PowerShell, dot-source `work/validation_2026-11-10/model_test/configure_env.ps1`. It places temporary/cache files inside the extracted tree. The pinned base checkpoint and configs are already present; no Hugging Face account/download is needed for existing model inference. Applicable Chronos library LICENSE/NOTICE are preserved at their original `.validation-venv/.../licenses/` paths; that directory alone is NOT a runnable environment.

## Reproduction sequence

Run the following with `.validation-venv/Scripts/python.exe`, from a disposable extracted copy. Script arguments and paths below were inspected, but these commands were not rerun for this handoff.

1. `work/validation_2026-11-10/audit_weather.py` regenerates historical weather/ET0 and its audit from saved NASA bytes, including twelve reference/unit/input checks.
2. `work/validation_2026-11-10/audit_weather.py --source power_sakha_2026_Jan_Oct_LST.json --suffix _2026_Jan_Oct` regenerates the 2026 outputs. Compare their hashes/values against the originals before interpreting model differences.
3. `work/validation_2026-11-10/model_test/verify_model_artifacts.py` checks saved predictions, target alignment, cutoff, scores, adapter records and data hashes without training; it writes `artifact_verification.json`.
4. Optional inference reproduction: `work/validation_2026-11-10/model_test/evaluate_holdout.py` loads existing adapters, selects between `smoke20_verified` and `adaptation200` by recorded validation scores, then overwrites held-out predictions/metrics. This is a replay of a consumed test, never a new assessment.
5. Optional training reproduction: `work/validation_2026-11-10/model_test/run_model_test.py --steps 20 --run-id reproduction20`, then `--steps 200 --run-id reproduction200`. These new IDs protect original runs. The evaluator has hard-coded original candidate names; to evaluate newly trained adapters, make a documented copy of the evaluator and change those names in the disposable tree. Do not replace original evidence to manufacture a fresh test.

`check_station_table.py` reproduces the limited printed-table diagnostic, not station-ground-truth validation. `work/readiness_2026-11-10/check_readiness.py` is the earlier limited sample check, not the full audit. Download scripts are archived for provenance; do not invoke them just to reproduce calculations because new downloads may contain revised data and overwrite snapshots.

## Interpretation and reproducibility limits

The accepted executed runs are `smoke20_verified` and `adaptation200`; `smoke20` failed reload consistency and is retained as negative evidence. `reload_diagnosis` records the investigation. The current training script includes the evaluation-mode/precision fix; the exact pre-fix script was not separately versioned. Seeds/configurations are in source and results. No claim of resumable optimizer state or bitwise retraining is made.

LoRA ran successfully, but seasonal climatology had the lowest MAE in the recorded limited held-out assessment. Keep those results even if later experiments differ. The June 2026 pinned model revision, archive vintages, simulated D−7 cutoff, 14-step prediction and scored steps 8–14 are material conditions. Independent agricultural accuracy, decision benefit, speech performance and usability remain unvalidated. See `MISSING_ARTIFACTS.md` before treating this package as complete scientific validation.
