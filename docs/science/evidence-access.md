# Supporting reports and local-only evidence

**Read this if…** you need the hashes of the frozen reports or wonder why a link to the ZIP is broken.

Status: Current,  · Owner: Refaat. Last reviewed .

## Restored reports

Seven small original Markdown reports were copied byte-for-byte from the local validation archive into `docs/`. Originals inside the archive were not modified. Historical dates, findings and limitations are retained; this is restoration, not renewed scientific validation.

| Repository report | Original archive member | SHA256 |
|---|---|---|
| MISSION_EL_GHEET_Validation_Verdict.md | `outputs/MISSION_EL_GHEET_Validation_Verdict.md` | `36f66a1aca03d731149d28edebba04ba1ad6ddbf72a32762247829b9e5cee82c` |
| validation_accessibility_alignment.md | `outputs/validation_accessibility_alignment.md` | `4a1335f209687a0446aabdf8334fe2421b37ae27235f63f647b4b2600773c45c` |
| validation_agronomy.md | `outputs/validation_agronomy.md` | `f88155f3bb909afacf2400bc0df1ad6e1b3047985dc2f3d54f0f48a311a2c8b8` |
| validation_data_equations.md | `outputs/validation_data_equations.md` | `64e7549b44aa5a433d40ea31dc4a3d7c6911fd4da4403501c67b8869bf53ae3f` |
| validation_equations_review.md | `outputs/validation_equations_review.md` | `24c31d8b7fe26472e7e223cc6df2e6c5ffabfaf10fe4818c2d91e4750f6125bc` |
| validation_models.md | `outputs/validation_models.md` | `e9cbd5bd63f7ab81e62eb1454333028c9e6bc62f51aecf2e7acccabbc4e1f946` |
| validation_model_execution.md | `outputs/validation_model_execution.md` | `41ea90f18ab41855feda4da3d9e67278903e0715978da137781bcb8c61beda37` |

## Local-only links

The validation ZIP is intentionally ignored and is not available in a GitHub clone. HANDOFF links to this local archive. Its SHA256 is `d284b3162a2dd5bbde8bcb37ae3090adcf080a5d044a4e25b2c96836b4cee95f`.

The six unique missing Markdown report targets from the original 18 unresolved link occurrences have been restored, together with validation_models.md referenced by the supporting reports. The ten original non-Markdown targets remain local-only. The inventory below also covers links from the restored reports. Referenced archive members exist, but were not extracted. No datasets, checkpoints or result files were added to Git.

| Referring document | Original local-only target | Archive member present |
|---|---|---|
| DATA_SPEC.md | `../work/validation_/power_provenance.json` | Yes |
| DATA_SPEC.md | `../work/validation_/power_provenance_2026_Jan_Oct.json` | Yes |
| DATA_SPEC.md | `../work/validation_/weather_et0.csv` | Yes |
| DATA_SPEC.md | `../work/validation_/weather_et0_2026_Jan_Oct.csv` | Yes |
| DATA_SPEC.md | `../work/validation_/model_test/artifact_verification.json` | Yes |
| HANDOFF.md | `VALIDATION_ARTIFACTS.zip` | Local archive itself |
| MISSION_EL_GHEET_Validation_Verdict.md | `../work/validation_/model_test/artifact_verification.json` | Yes |
| ML_EXPERIMENT.md | `../work/validation_/model_test/checkpoint_provenance.json` | Yes |
| ML_EXPERIMENT.md | `../work/validation_/model_test/installed_requirements.txt` | Yes |
| ML_EXPERIMENT.md | `../work/validation_/model_test/adaptation200/results.json` | Yes |
| ML_EXPERIMENT.md | `../work/validation_/model_test/evaluation_protocol.json` | Yes |
| ML_EXPERIMENT.md | `../work/validation_/model_test/holdout_results.json` | Yes |
| validation_model_execution.md | `../work/validation_/model_test/adaptation200/results.json` | Yes |
| validation_model_execution.md | `../work/validation_/model_test/holdout_results.json` | Yes |
| validation_model_execution.md | `../work/validation_/model_test/evaluation_protocol.json` | Yes |

Original reports also mention local evidence paths in prose or code. Those paths are historical provenance, not promises of files in a clone. Keep the archive and any selectively accessed evidence in approved local storage; consult its REPRODUCE.md and MISSING_ARTIFACTS.md before reproducing research. This task did not reproduce numerical or model results.

## Subsequent targeted validation

The later [scientific validation and bounded fixes](../reports/scientific-validation-fixes.md) records executable rechecks against selected members of the unchanged local ZIP, with a portable standard-library checker and acquisition metadata. The seven original reports above remain byte-preserved historical records; their restoration-only statement describes that earlier task. No weights or new weather were downloaded, and no source PDF missing from the package was represented as locally available.

12 November: the original `audit_weather.py` is now promoted byte-for-byte into `data/validation/`, with a checksum-bound release manifest and safe fresh-directory wrapper. See [reproduction instructions and remaining input-distribution gap](reproducing.md). This exposes calculation source without distributing raw evidence, model weights or the archive. The [pre-push review](../reports/pre-push-science-audit.md) records current verification; historical reports above remain unchanged.
