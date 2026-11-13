"""Package existing research evidence; does not execute research scripts."""
from pathlib import Path
import hashlib, json, zipfile

root = Path(__file__).resolve().parent.parent
out = root / 'outputs/VALIDATION_ARTIFACTS.zip'
if out.exists():
    raise SystemExit('Archive already exists; refusing to overwrite.')
files = []
for directory in ['work/validation_2026-11-10', 'work/readiness_2026-11-10', 'work/agronomy']:
    for p in (root / directory).rglob('*'):
        if p.is_file() and not any(x in p.relative_to(root).parts for x in ('cache', 'tmp', '__pycache__')):
            files.append(p)
files += list((root / 'outputs').glob('*.md'))
license_dir = root / '.validation-venv/Lib/site-packages/chronos_forecasting-2.3.2.dist-info/licenses'
files += [p for p in license_dir.iterdir() if p.is_file()]
files += [Path(__file__).resolve()]
files = sorted(set(files))
def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''): h.update(b)
    return h.hexdigest()
entries = [{'path': p.relative_to(root).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in files]
required = ['power_sakha_2001_2025_LST.json', 'power_sakha_2026_Jan_Oct_LST.json', 'weather_et0.csv', 'weather_et0_2026_Jan_Oct.csv', 'audit_weather.py', 'weather_audit.json', 'weather_audit_2026_Jan_Oct.json', 'model_test/checkpoint/model.safetensors', 'model_test/checkpoint/config.json', 'model_test/adaptation200/training/finetuned-ckpt/adapter_model.safetensors', 'model_test/smoke20_verified/training/finetuned-ckpt/adapter_model.safetensors', 'model_test/evaluate_holdout.py', 'model_test/run_model_test.py', 'model_test/holdout_results.json', 'model_test/holdout_predictions.npz', 'model_test/evaluation_protocol.json', 'model_test/installed_requirements.txt']
missing = [p for p in required if not (root / 'work/validation_2026-11-10' / p).is_file()]
assert not missing, missing
repro = '''# Reproducing the validation evidence

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
'''
gaps = '''# Missing, excluded and not-yet-created artifacts

## Required existing computational evidence

All required raw POWER responses, derived ET0 files, audit/check scripts, base checkpoint/config, accepted LoRA adapters, training/evaluation source, frozen package list, metrics, predictions and protocol were found. See the manifest for exact files. Other saved failed/diagnostic runs are retained too.

## Local source-copy gaps

`work/agronomy/` contains download failure records, not the requested PDFs. Missing attempted files include `aiad_2019.pdf`, `sugita_2017.pdf`, `egyptian_clover_fao.pdf`, and `maize_arc.pdf`. Errors include HTTP 403/503, timeout and closed connection. Other online references cited by the specifications (including the later maize bulletin, Darwesh, Kubota and sorghum sources) are not saved as local copies in these artifact directories. Links/locators remain in the scientific documents. ASCE PDF/text are included. No sources were redownloaded for packaging.

## Not created or not separately preserved

- No locally validated crop catalogue, complete Kc/stage data, field soil survey, raw station/lysimeter benchmark, farmer interview or speech/usability result.
- No application/planner implementation, automated scenario acceptance results, real-time forecast vintage archive or fresh follow-up experiment.
- No separate saved pre-fix training-script version for the failed smoke run; current source contains the correction. No optimizer/scheduler checkpoint for exact mid-training resume.
- No standalone script for the separately reported independent all-row equation review was located; its written audit is included. The main ET0 calculation/test source and saved numerical audit are included.
- No exact offline environment image, dependency-wheel bundle or driver installer. Frozen versions and setup instructions are included. The base-model upstream model card/license file was not downloaded separately; provenance URLs and library LICENSE/NOTICE are included. Check upstream terms before external redistribution.

## Deliberate exclusions

The installed virtual environment (except existing Chronos LICENSE/NOTICE), caches, temporary files and Python bytecode are excluded. They add bulk and machine-specific state rather than research evidence. Unrelated submitted videos/PDFs and attachments are not validation artifacts. Existing Markdown audit/specification files are preserved unchanged; their historical status language is explained in REPRODUCE.md. New HANDOFF and REFERENCE_SCENARIO copies are included for context.
'''
manifest = {'format_version': 1, 'preserves_workspace_relative_paths': True, 'missing_required': missing, 'entries': entries, 'generated_archive_notes': ['REPRODUCE.md','MISSING_ARTIFACTS.md','ARTIFACT_MANIFEST.json']}
with zipfile.ZipFile(out, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=3, allowZip64=True) as z:
    for p in files: z.write(p, p.relative_to(root).as_posix())
    z.writestr('REPRODUCE.md', repro)
    z.writestr('MISSING_ARTIFACTS.md', gaps)
    z.writestr('ARTIFACT_MANIFEST.json', json.dumps(manifest, indent=2))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for entry in entries:
        h=hashlib.sha256()
        with z.open(entry['path']) as f:
            for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
        assert h.hexdigest()==entry['sha256'], entry['path']
        assert digest(root/entry['path'])==entry['sha256'], 'Source changed: '+entry['path']
report={'archive':str(out), 'bytes':out.stat().st_size, 'sha256':digest(out), 'original_files':len(entries), 'zip_entries':len(entries)+3, 'missing_required':missing, 'crc':'passed', 'all_entry_sha256':'passed', 'sources_unchanged':'passed', 'experiments_rerun':False}
(root/'work/handoff_package_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
