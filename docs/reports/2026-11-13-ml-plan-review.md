# ML plan review

**Read this if…** you own or build anything in `docs/ml/`, `ml/` or the forecast bundle.

Status: Frozen report, 13 Nov 2026 · Requested by Yahya · For review by Amr.

---

## Scope and method

Three independent read-only reviews of the ML plan (`docs/ml/*`), run 13 Nov 2026 on commit
`70891af` (`main`). No repo files were changed during the review.

1. **Consistency:** ML docs against `decisions.md`, `rejected.md`, `status/`, `team.md`,
   `backend/core-integration.md`, `backend/api-contracts.md`, `planner/blueprint.md` §9.1.
2. **Data and code:** does the data and code the plan names exist and match the docs. Ran the tests.
3. **Methodology:** framing, baselines, leakage, metrics, data sufficiency, unsourced claims.
   Checked NASA POWER facts against power.larc.nasa.gov (methodology and tutorial pages).

**Verdict: the method is sound but the docs need fixes.** The method is careful. Most problems are
documentation drift, plus an ML side channel that has little expected skill and no farmer
decision attached.

## Tests actually run (Linux, Python 3.12.3)

`python` is not installed on the review machine, so `python3` was used with the same flags.

| Suite | Ran | Pass | Skip | Skip reason |
|---|---|---|---|---|
| `ml/tests` | 3 | 2 | 1 | local source archives required (the only test that builds a real release) |
| `data/validation` | 16 | 3 | 13 | validation ZIP / frozen inputs not present |

`plan.md:23` says three tests passed. On this machine it was 2 pass, 1 skip.

## What holds up

- **No path from ML output to plan status.** `core-integration.md:77,79`, `tasks/amr.md:50,67`,
  `backend-design.md:290`, `blueprint.md:5` and `multigrid-proposal.md:52` all say this. No test
  enforces it yet (see L1).
- **Leakage controls.** Splits are by time and boundary labels are purged
  (`dataset-manifest.md:55-59`). Features use only data before the cutoff. ET0 sensitivity and QC
  columns are kept out of the inputs (`data-spec.md:56`).
- **Fair comparison and honest records.** Persistence and climatology baselines are defined, and
  every model is scored on the same 504 keys. The losing Chronos/LoRA result is kept. No
  confidence bands are invented for Ridge.
- **Numbers.** The plan's numbers are internally consistent, checked by arithmetic: 6,574 + 1,096
  = 7,670 rows; 9,131 days for 2001–2025; 504 = 36×7×2; 38 features. The coordinates, time
  standard, units and CSV hashes match `power_acquisition.json` and `et0_release_manifest.json`.
- **Git hygiene.** No model weights, CSVs, ZIPs or secrets are tracked. The largest tracked file is
  92 KB.
- **Release builder.** `prepare_shared_release.py` does the archive and member hash checks, the
  path-traversal guard, the Tmax/ET0 cross-check and the one-step publish that the docs describe.

## High

**H1. Dates were stripped from IDs, paths and boundaries across `docs/`.** This looks like a
single bulk scrub, and it reaches beyond the ML docs.
- The docs say `meg-shared--v1` (`dataset-manifest.md:7,29`, `plan.md:23`,
  `core-integration.md:62,74`). The builder writes `meg-shared-20261113-v1`
  (`prepare_shared_release.py:64`). `data_release` is the HTTP version token, so the doc's
  version would never match.
- **Broken links:**
  - `reports/-scientific-validation-fixes.md` (`ml-experiment.md`, `science.md:17,66`,
    `reproducing.md:47`, `evidence-access.md:49`)
  - `-pre-push-science-audit.md`
  - `handoff-/ARTIFACT_TRANSFER.md` (`status/ml-data.md:30`)
  - the `work/validation_/` links. That evidence exists under
    `archive-snapshot/work/validation_2026-11-10/`.
  - the reports index in `docs/README.md:65-68`.
- **Blank dates in the spec.**
  - Train/test boundaries are blank: `dataset-manifest.md:55` reads "train labels end by .", and
    `:57` reads "<= and <=". The spec can't be implemented as written.
  - The coverage cell is empty (`dataset-manifest.md:13,15`).
  - "Last reviewed" and "As of" lines are blank in several files.
- **Fix:** restore the full dated IDs and paths in one pass, using the code,
  `et0_release_manifest.json` and `refaat/data/release.json` as sources.

**H2. The docs claim a local release this checkout doesn't have.**
- `plan.md:23`, `integration-checklist.md:16`, `dataset-manifest.md:33`, `tasks/amr.md:36` and
  `tasks/refaat.md:35` say "the current workspace already has that release". `data/local/` holds
  only `.gitkeep`.
- `work/refaat-handoff-/` (`status/ml-data.md:24`) doesn't exist.
- `status/ml-data.md:5` cites commit `0122e92`, which isn't in `git log`.
- **Fix:** say where the release actually lives (Amr's machine, 13 Nov) and update the commit.

**H3. The status file asks for a bundle the ML docs say can't be produced.**
- `status/ml-data.md:16` says "Amr: write `forecast_bundle.json`".
- `model-selection.md:56`, `core-integration.md:89` and `tasks/amr.md:62` say weather data ends
  31 Oct, so the default is `unavailable`.
- **Fix:** "publish only if a valid reviewed bundle exists; absence is the expected default".

**H4. The forecast is effectively 8–14 days ahead, and nothing turns it into a farmer decision.**
- The cutoff is D−7 and the forecast covers D+1…D+7 (`ml-experiment.md:41`,
  `dataset-manifest.md:37`). Simple lag models rarely beat climatology for daily Tmax at that
  range.
- Even if Ridge wins it can't ship: it gives a single value, and the API needs quantiles
  (`dataset-manifest.md:63`). The farmer decision it should improve is still open
  (`ml-experiment.md:76-78`).
- **Fix:**
  - State up front that a tie or loss is the expected result.
  - Use a cutoff per variable. NASA's stated delay is 2–3 days for weather and 5–7 days for
    solar, so Tmax could use D−3.
  - Drop P1 Ridge first if the schedule slips.

**H5. The model that ships (climatology) has no reported interval coverage, and it uses 2001–2018
only.**
- Coverage is reported only for the LoRA adapter (`ml-experiment.md:62`).
- A fixed 2001–2018 window ignores any warming trend since.
- **Fix:**
  - Report the 10–90% interval coverage and bias on 2019–2021, by season.
  - Label it in the UI as "typical for this date, 2001–2018", never "forecast".

**H6. A live forecast would get different data products from the ones it was trained on.**
- Training used MERRA-2 weather and CERES SYN1deg solar. Recent POWER data comes from GEOS-IT and
  FLASHFlux (`data-spec.md:13`; confirmed on the POWER methodology page).
- **Fix:** measure the difference over a period both products cover before any live bundle, or
  keep the forecast `unavailable`.

## Medium

**M1. Ownership conflicts.**
- `plan.md:11,30` and `tasks/amr.md:9,46` name Amr/Astra as `meg_core` planner owners.
  `team.md:14` says Karim, blueprint §9.1 splits it by module, and status item Q1 is still open.
- Climate/replay code: blueprint §9.1 gives `climate/evaluate.py` to Mahmoud and
  `meg_core/forecast/baselines.py` to Amr. `plan.md:30` and `tasks/mahmoud.md:57` say otherwise.
- **Fix:** mark the planner owner "pending Q1"; pick one owner and location per function.

**M2. The bundle producer path differs between the ML and backend docs.**
- `backend-design.md:228` says `ml/predict.py` writes the bundle and one demo bundle is committed
  (`:138`).
- `tasks/amr.md:46` says `meg_ml/publish.py`, and `core-integration.md:108` forbids demo
  forecasts.
- **Fix:** Yahya and Amr agree one path and record it in `decisions.md`.

**M3. Gate parameters differ from blueprint §7 without being recorded.**
- Alpha grid is [1,10,100] here vs {0.1,1,10,100} in the blueprint.
- Bootstrap block length is 3 origins here vs 8.
- The 26-origin minimum is dropped.
- The plan builds on blueprint D01–D10, which are not approved yet (Q5), and on a schedule that
  conflicts with Q7/D09.
- **Fix:** list these in `plan.md:52`, link Q5/Q7, and record the outcome in `decisions.md`.

**M4. The promotion gate will almost always come back inconclusive.**
- 36 test origins make about 12 bootstrap blocks and about 9 origins per season. That is too few
  for "95% interval excludes zero" plus "no lead or season worse by more than 5%"
  (`dataset-manifest.md:61-63`).
- The 5% margin has no stated basis (`multigrid-proposal.md:46` marks it pending).
- **Fix:** compute the smallest improvement this sample can detect before running, and record 5%
  as a team choice.

**M5. No untouched test period remains.**
- 2019–2021 already selected the Chronos adapter, and the Ridge lags were designed after seeing
  those results.
- 2022–2025 has been inspected, and 2026 is consumed.
- **Fix:** register the test period now and archive daily inputs from 14 Nov
  (`dataset-manifest.md:65`).

**M6. Persistence is a weak baseline at this lead** (3.79 °C vs 2.53 °C, `model-selection.md:34-35`).
**Fix:** add a damped-anomaly baseline: climatology plus the recent anomaly scaled by a factor
fitted on training years only. It is not in `rejected.md`.

**M7. The release builder and its tests cover less than the docs imply.**
- The builder doesn't check the 27-member count, date ranges, duplicates or the
  2001–2018/2019–2021 boundaries. A missing date raises a bare `KeyError`.
- The passing tests only exercise early exits.
- There are no tests for a member checksum mismatch, a target mismatch, a wrong row count or an
  unsafe path.

**M8. The ML docs disagree on Chronos inference.** `model-selection.md:48` allows a short replay.
`integration-checklist.md:47` and `plan.md:11` rule it out.

**M9. The build commands are Windows-only.**
- `dataset-manifest.md:29`, `tasks/refaat.md:31` and `tasks/amr.md:18` use `C:/Users/Amr Hany/...`
  and PowerShell.
- The test looks for `../ML_HANDOFF.zip` instead.
- Every documented command uses `python`, which isn't installed everywhere.

**M10. The multigrid grouping rule may collapse to very few groups.** Requests that share a 1°×1°
solar cell go into the same group (`multigrid-proposal.md:21`). Cells were not counted.
**Fix:** count groups from the grid definitions before approving, or restrict to Tmax at
0.5°×0.625°.

## Low

- **L1. No test checks that planner output is identical with and without a forecast bundle.** Add
  it to `integration-checklist.md`.
- **L2. Some labels fall outside the status vocabulary.**
  - "VERIFIED AND TESTED" (`refaat-verification.json:123`, frozen; leave it)
  - "PRODUCTION CORE" (`model-selection.md:45,52`)
  - "zero validated repairs/alternatives" (`plan.md:54`)

  Use `verified`, "prototype baseline" and "zero feasible alternatives".
- **L3. The backend example bundle uses Chronos LoRA** (`backend-design.md:232-246`), which the ML
  plan won't deploy.
- **L4. Forecast status precedence differs** between `core-integration.md:87` and
  `backend-design.md:280-283`.
- **L5. The 35/40 °C heat counts have no source** (`blueprint.md:194`, `core-integration.md:81`).
  `science.md:82` requires sourced thresholds, so keep heat-stress wording out of the UI.
- **L6. The "both targets" pass is not two independent confirmations,** because ET0 depends on
  Tmax.
- **L7. Ridge is scored at a mild disadvantage.** It is fitted with squared loss but scored by MAE
  against a median.
- **L8. Some design choices are unsourced.** The lag set and the ±15-day window
  (`dataset-manifest.md:39,49`) should be marked proposed.
- **L9. The consumed test period is worded inconsistently.** It is "Jul–Oct 2026" in
  `ml-data.md:36` but "Jan–Oct 2026 quarantined" in `dataset-manifest.md:57`.
- **L10. Mahmoud's backend role is open (Q2).** `plan.md:39` assumes one.

## Not verified

- The release contents, the CSVs, the `climate_data` package and the "byte-identical" claims in
  `refaat-verification.json`. The validation ZIP and `data/local/` release are not in this
  checkout.
- The 4.96 m elevation. It was not found in `power_acquisition.json` or `power_provenance.json`.
- Whether `ml/src/meg_ml/contracts.py` counts as a shared contract that needs Yahya's sign-off.
