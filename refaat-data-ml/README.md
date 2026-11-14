# MISSION EL GHEET • Sakha data engineering

**P0 update, 13 November 2026:** The original climate runtime, source data, ML splits and reference results are unchanged. The recovered crop research is now a callable, validated [Agricultural KB](BACKEND_HANDOFF/AGRICULTURAL_KB_CONTRACT.md): four crops, 27 source-linked rules, 18 scientifically `VERIFIED`, **zero local sign-offs and zero enforceable planner constraints**. Research parameters remain source text until an agronomist approves their local interpretation. Run `python -m agricultural_kb` and `python -m examples.backend_p0` from this root.

**Recipients:** [Yahya / Backend](BACKEND_HANDOFF/START_HERE.md) · [Mahmoud / ML](ML_HANDOFF/START_HERE.md) · [VS Code setup and repository layout](REPOSITORY_GUIDE.md) · [P0 assessment and acceptance](reports/P0_IMPLEMENTATION.md). No actual team backend was supplied or tested. Yahya must approve the new KB schema and its constraint semantics before planner integration.

The root `PACKAGE_MANIFEST.json` now describes the P0 repository revision. The original manifest and the original bytes of the five updated delivery files are preserved under `provenance/legacy_delivery/`. `python -m scripts.verify_legacy` verifies all 66 original delivery hashes; `python verify_package.py` verifies the current revision. The climate release `data/release.json` and its hashes are unchanged. Keep `.gitattributes` when committing so checkout cannot rewrite scientific line endings.

**تسليم سخا:** مهندس الـML يبدأ من [دليل الـML](ML_HANDOFF/START_HERE.md) عشان يعيد Seasonal Climatology. مهندس الـBackend يبدأ من [دليل الـBackend](BACKEND_HANDOFF/START_HERE.md) عشان يقرأ الطقس ويقارن خطط بمواعيد محددة. كل الحسابات محلية، والمرجع والنتايج مربوطين بنفس نسخة البيانات. ده مشروع Data Engineering؛ تشغيله في تطبيق الفريق لسه محتاج كود التطبيق.

**Release:** `sakha-power-lst-20261110-et0-v1`; site `sakha_31.10_30.95`; method `fao56-dewpoint-asce-floor-v1`. Two original NASA POWER Daily AG/LST captures, 2001-01-01 to 2025-12-31 and 2026-01-01 to 2026-10-31. This is one gridded point, not an on-farm station. All 9,435 dates are present.

## Run from an extracted project root

Use Python 3.11+ in a writable local directory. No dependencies to install. In these examples select an unused location for each output. On Windows you can substitute `py -3` for `python`.

```console
python verify_package.py
python rebuild.py --output rebuilt_release
python -m climate_data.ml_example --data data
python -m climate_data.evaluation --data data --output my_baseline
python -m climate_data.backend_example --data data --out my_example.json
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -p test_pipeline.py -v
```

For the full recorded acceptance sequence in one command run `python check_handoff.py --output my_verification.json`. It tests the actual public commands in disposable directories and verifies the outputs against packaged references, including the KB approval gates. To produce current recipient ZIPs run `python make_handoffs.py --output outputs/handoffs` from the verified full project. Both recipient archives have an independent `START_HERE.md`, runtime, data, tests and SHA256 manifest. Neither needs the other ZIP. The backend ZIP includes the KB and preserved agricultural research. Old climate-only ZIPs in Downloads are superseded for the P0 backend handoff.

| Start here | What it establishes |
|---|---|
| [Data dictionary](SHARED_DATA_DICTIONARY.md) | Names, types, units, date conventions, flags and partitions. |
| [Input archive map](provenance/input_archives.json) | Hashes of both original ZIPs and the exact paths, lengths and digests of the 20 reused members. Both old archives stay unchanged. |
| [Source receipts and hashes](provenance/source_manifest.json) | Coverage, API metadata, geometry, raw and receipt hashes. The runtime has a preserved copy of the earlier source index in `data/source_manifest.json`. |
| [Pipeline measurements](reports/pipeline.json) and [outlier limits](reports/seasonal_screen_bounds.csv) | All-row integrity, numerical differences, source hashes, daily flags and original reference checks; monthly fences fitted on training only. |
| [ML metrics](ML_HANDOFF/reference/metrics.json) and [Chronos archive locator](provenance/CHRONOS_HISTORY.md) | Reproduced diagnostics and separately identified, consumed research evidence. |
| [Backend contract](BACKEND_HANDOFF/CONTRACT.md) and [worked example](BACKEND_HANDOFF/example_response.json) | Seven public functions, date/coverage semantics, versioned responses and two four-season candidate plans. |
| [Readiness decision](reports/HANDOFF_READINESS.md) and [execution records](reports/qa/) | Acceptance status, actual runs and limitations. |

## How a release is built

1. `rebuild.py` verifies the archive-member inventory. `climate_data.pipeline` pins both raw responses, two acquisition receipts and two archived comparison CSVs. It rejects duplicate JSON keys at any level, NaN/Infinity, wrong schema/units/query/site and any missing, extra, repeated or invalid day. It never fills missing inputs. All release gates raise explicit exceptions even under `python -O`.
2. Parse all eight meteorological quantities at their source units. Hard gates reject fill/nonfinite values, inverted extremes, nonphysical temperature, nonpositive pressure, RH outside 0…100, negative radiation/wind/rain. Review-only conditions do not delete rows; retain raw solar ratio, vapour-pressure deficit, source-mix and monthly training-only 3-IQR flags separately. The partial recent capture is not a complete civil year.
3. `climate_data.et0.calculate_daily_et0` recomputes daily FAO-56 Penman–Monteith short-grass ET₀ from weather. Use mean temperature, saturation pressure averaged at the extrema, actual vapour pressure at dewpoint, surface pressure in kPa, wind already at 2 m, incoming solar in MJ/m²/day, and G=0. At the reported elevation (4.96 m) compute clear-sky radiation; only the longwave cloudiness ratio has the documented ASCE bound [0.3,1]. No weather observations or final ET₀ values are clipped. The two separate sensitivity columns use mean RH, or remove just the 0.3 floor. See the original [method note](sources/original/audit_method_notes.md); its historical relative links belong to the original audit ZIP.
4. For **every day**, compare all eight original weather values and all three computed ET₀ pathways to the archived CSV (ET₀ absolute tolerance 1e−10 mm/day). Only after these comparisons pass do exports retain the reference's exact decimal strings, preserving old experiment inputs across minor math-library differences. The original hash-pinned scientific suite runs on disposable copies, independently of the shared public calculation and with its historical assertions enabled. The new public negative/regression tests exercise the shared implementation as well.
5. Produce `sakha_daily.csv`, `quality_flags.csv`, the fit and diagnostic target splits, a 36-origin diagnostic-only window CSV, the runtime source manifest and `release.json`. Output directories must be new; successful builds publish completed files together. Read `data/release.json` for release-level hashes. `PACKAGE_MANIFEST.json` covers files present in the corresponding ZIP.

## Interpretation and ownership

The ML calendar reference uses 2001–2018 only; the application descriptive reference uses complete years 2001–2025. Neither is a real-time forecast or demonstrates crop water use. Heat is exposure above a development-only historical threshold, not damage. For replay, the planner supplies dates and protected commitments. Climate reports totals, duration-normalized comparisons, shared history, flags and exclusions; it neither constructs a plan nor confirms agricultural feasibility. A future blind test, station validation and actual app integration require inputs beyond this frozen snapshot.

