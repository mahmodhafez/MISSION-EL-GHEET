# Reproducing the scientific checkpoint

**Read this if…** you want to rerun the scientific checks or regenerate ET0.

Status: Current,  · Owner: Refaat. Last reviewed .

. This checkpoint contains reviewable scientific scripts, not a runnable farmer application or a complete public dataset release. Python 3.12+ standard library suffices for the steps below; no model packages, CUDA, npm dependencies or account are required. In this audit the actual interpreter was Python 3.13.5. Commands assume the reviewed files have been included in the eventual commit; this audit does not commit or stage them.

## What a clean clone can and cannot reproduce

| Available material | Reproduction boundary |
| --- | --- |
| Git HEAD before this checkpoint | Specifications/placeholders; the earlier scientific checker and metadata were still untracked. No executable end-to-end regeneration path. |
| Reviewed checkpoint source alone | Generator, wrapper, expected hashes, provenance and tests are reviewable. Missing-input/no-overwrite tests run. Frozen-output and ML checks require additional inputs; skips are not validation. |
| Checkpoint plus matching raw POWER JSONs | Regenerate both approved weather/ET0 CSVs and twelve reference/unit/input checks per period using only the standard library. No ML artifact package needed for ET0. |
| Checkpoint plus local validation ZIP | Regenerate ET0 and rerun saved scientific/ML checks offline. The ZIP remains excluded from Git. |
| New request to the public NASA endpoint | Access to a current response is possible in principle, but historical revisions may change bytes. It is a new release if its hash differs; it is not guaranteed access to the frozen November 2026 input. No new data were requested here. |

**Remaining public reproducibility gap:** the two exact frozen raw responses and saved model predictions are not distributed through this repository or an approved public immutable artifact URL. A clean public clone cannot independently reproduce all approved numerical/ML outputs without obtaining those inputs separately. Before advertising full public reproducibility, approve a small source-data release or immutable external distribution after terms/provenance review. Do not publish the 469 MB validation archive or model weights to work around this gap.

## Inputs, method and versioning

[power_acquisition.json](../../data/validation/power_acquisition.json) preserves both exact request URLs, timestamps, API v2.10.3, response source lists, units and raw SHA256. [et0_release_manifest.json](../../data/validation/et0_release_manifest.json) binds the raw inputs, byte-preserved generator and expected CSV hashes to release `sakha-power--audited`.

The promoted [audit_weather.py](../../data/validation/audit_weather.py) is byte-identical to `work/validation_/audit_weather.py` inside the original ZIP, SHA256 `905a700d542c5a3e2dc7dd136e21acd7a84469d1ff940efa0836bbb63e7ee0e0`. It retains FAO56 constants, dewpoint humidity, daily G=0, source geometry, ASCE 0.3–1.0 cloudiness bound, sensitivity outputs and the original twelve checks. Its direct CLI writes next to itself; use the wrapper below to keep source/evidence immutable. `.gitattributes` disables newline conversion for this one byte-identified source file. Other files keep existing Git line-ending behavior.

The new [regenerate_et0.py](../../data/validation/regenerate_et0.py) verifies source/generator hashes, copies the committed generator and matching raw input to a **new** output directory, executes it under isolated standard-library Python, and checks exact CSV hashes. It executes reviewed repository source, never a script supplied by the ZIP. Unknown source vintage, missing input, failed checks and existing output paths fail explicitly. A failed numerical run may leave partial outputs; these are not validated. Do not import data from them or treat their existence as success.

## Exact commands

Frozen ZIP route, from repository root, using new output paths:

```powershell
python -I -S data/validation/regenerate_et0.py --archive docs/VALIDATION_ARTIFACTS.zip --period historical --output-dir work/et0-replay/historical
python -I -S data/validation/regenerate_et0.py --archive docs/VALIDATION_ARTIFACTS.zip --period 2026 --output-dir work/et0-replay/2026
python -I -S data/validation/audit_saved_evidence.py --archive docs/VALIDATION_ARTIFACTS.zip
python -I -S -m unittest discover -s data/validation -p 'test_*.py' -v
```

Alternatively, place the original raw files in ignored local storage and run without any ZIP:

```powershell
python -I -S data/validation/regenerate_et0.py --source data/local/power_sakha_2001_2025_LST.json --period historical --output-dir work/et0-from-raw/historical
python -I -S data/validation/regenerate_et0.py --source data/local/power_sakha_2026_Jan_Oct_LST.json --period 2026 --output-dir work/et0-from-raw/2026
```

Existing output folders are rejected; choose another fresh path for a repeat. Do not delete or overwrite the only evidence copy. For a fresh acquisition, retain the original bytes and new provenance as described in [SCIENTIFIC_VALIDATION_FIXES.md](../reports/scientific-validation-fixes.md); compare hashes before attempting frozen replay. The wrapper intentionally rejects revised inputs. Refresh policy/production data-release expansion needs separate review.

Expected CSV SHA256:

| Output | Days | SHA256 |
| --- | ---: | --- |
| `weather_et0.csv` | 9,131 | `17141df82f6300c051257c21fb9ac3d9f5f1627fd32cbc8c07bc9296c477bde8` |
| `weather_et0_2026_Jan_Oct.csv` | 304 | `c4d5929fd0d4d55c416ee45d5ebd21502142994afbc76b00c6f20e1b349ee36e` |

These are the original audit CSV format, including two method-sensitivity columns, not DATA_SPEC's proposed expanded production schema. Raw precision/LST and original units remain unchanged; no interpolation, bias correction, radiation/pressure reconversion or additional wind-height conversion occurs. A platform producing a different checksum must report the difference and investigate numerical/formatting compatibility, not silently revise expected values.

## Interpretation and independent acceptance

The read-only [saved-evidence checker](../../data/validation/audit_saved_evidence.py) independently expresses ET0 and rescores saved predictions, reconstructs climatology/persistence and verifies dates/input hashes. The generation wrapper reproduces the original implementation. Both establish numerical consistency, not station accuracy or field truth. Test skips on a clean clone explicitly mean evidence is unavailable. Run the explicit checker when full artifact validation is required; missing evidence is a nonzero failure.

Station-table years/height/transcription and observational provenance remain unresolved; no bias correction is fitted. Crop profiles lack complete applicable cultivar/end/release/preparation/field evidence. Missing Kc/stages keep crop ETc unavailable; ET0 is reference demand, not irrigation use. ML intervals are experimental, and July–October 2026 is already consumed holdout evidence. No new regional data, training, crop claims or application acceptance tests are implied. **P0 rejected; R1/R2 needs_review; zero validated feasible alternatives.**
