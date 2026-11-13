# Scientific validation and bounded corrections

. Scope: the user's listed issue areas, actual repository files and selected evidence in the local validation ZIP. No separately authored Yahya issue list was found in the repository; the rows below audit the supplied priorities without attributing invented quotations to him. This is a targeted implementation/recheck, not a new research programme or scientific approval of crop repairs.

## Findings

| Finding | Classification | Evidence and disposition |
| --- | --- | --- |
| Science/data summaries still list research-locality approval as pending | **CONFIRMED DEFECT** | HANDOFF already records Sakha approval. Corrected SCIENCE/DATA_SPEC wording; field eligibility stays open. |
| Science summary implies the sorghum evidence is only nonlocal | **CONFIRMED DEFECT** | Later AGRONOMY_EVIDENCE S1 records a Sakha hybrid-888 grain trial; B2/M3/M4 also add scoped local observations. Linked those observations, retaining all transfer/release/field gates and all four crops. Original research ledger unchanged. |
| Published soil is falsely assigned to Hussein | **UNVERIFIED CLAIM** | REFERENCE_SCENARIO explicitly leaves salinity/pH/drainage/water table unknown. SCIENCE and both agronomy ledgers distinguish the saline trial. No executable catalogue exists to contradict that contract. Preserve Aiad's source-reported 0–20 cm clay/pH/EC and measurement methods; do not discard observations because applicability is unknown. |
| POWER/station calculation mixes calendar years or wind units | **UNVERIFIED CLAIM** | Archived script selects complete November 2015–September 2016 monthly means, Tmax/Tmin in °C, RH in percentage points and WS2M in m/s. Archived table transcription claims km/day at 2 m; division by 86.4 is correct under that assumption. No 10 m conversion is needed for WS2M. Arithmetic reproduces; primary table transcription/height was not freshly verified. |
| Printed-table differences establish measured station bias | **EXISTING DOCUMENTED LIMITATION** | Eleven equal-weight monthly differences reproduce: Tmax +2.994535°C, Tmin −1.531444°C, RH −11.553671 percentage points, wind +1.736051 m/s. These are differences against a transcription, not a calibrated bias estimate. Daily station records, QC, instrument/exposure and observation-day definitions are absent. No bias correction fitted. |
| Exact acquisition is difficult to reproduce from a clone | **CONFIRMED DEFECT** | Exact requests and metadata existed inside the ignored ZIP, but numerical reproduction required discovering/extracting it and the model-oriented setup. Added portable metadata, standard-library read-only checks and minimal instructions below. Raw data remain local-only; no claim of a complete distributable production release. |
| ET0 is being used as crop water or irrigation demand | **UNVERIFIED CLAIM** | Existing contracts explicitly separate them. ETc remains **unavailable** for these profiles without applicable Kc and stages; no new ETc output, default stage lengths, heat thresholds, irrigation totals or crop ranking was introduced. The archived constant-Kc multiplication fixture is only arithmetic. |
| Local Kc/stages and complete feasible crop repairs are missing | **EXISTING DOCUMENTED LIMITATION** | SCIENCE/PLANNER_SPEC/AGRONOMY_EVIDENCE document the gaps. Local plot calendars do not validate a transferred release/preparation mapping or standard-condition crop curve. No outcomes changed. |
| Published ML MAE or baseline comparison is incorrect | **UNVERIFIED CLAIM** | Independently rescored saved numeric predictions; reproduced persistence and training-only climatology from source CSVs. All four MAEs match within 0.000003 in the target's unit. Climatology remains better in this sample. No new training or inference. |
| Training/evaluation used different saved dataset vintages | **UNVERIFIED CLAIM** | Both held-out CSV hashes match actual archived bytes; historical CSV hash also matches both accepted training runs. Different source-product lists between the 2001–2025 and 2026 exports are real, documented product provenance differences. They are not evidence of a byte-level train/evaluation mismatch. Historical issue-time snapshots are absent: that remains an **EXISTING DOCUMENTED LIMITATION**. |
| Forecast intervals/provenance justify operational confidence | **EXISTING DOCUMENTED LIMITATION** | LoRA nominal 80% coverage is 91/119 = 76.47% Tmax and 84/119 = 70.59% ET0; mean widths 6.724053°C and 1.964170 mm/day. Archived source and protocol support Chronos-2/LoRA, D−7 cutoff, 14 steps, scored steps 8–14, 60-day history and cross-learning disabled. No interval calibration or farmer-decision validation exists. |
| Minimal collection/retention/consent is underspecified for deployment | **EXISTING DOCUMENTED LIMITATION** | Architecture already restricts synthetic remote sessions, consent and raw-audio retention. Added PRIVACY_ASSUMPTIONS with minimum data and distinct confirmation/transmission/research consent boundaries. Exact hosted expiry, logs/backups and provider terms remain decisions, not implemented controls or legal certification. |
| Obtain paired quality-controlled station observations or prospective forecasts | **OPTIONAL IMPROVEMENT** | Appropriate follow-up for future accuracy claims. Requires its own access/protocol review; no broad research, new experiment, correction model or data collection performed here. |

The original seven restored validation reports and ZIP remain unchanged historical evidence. Online primary-source check: NASA's [daily API documentation](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) was accessible and confirms the point-request format and explicit LST convention. The cited [Aiad PDF](https://jenvbs.journals.ekb.eg/article_54170_dd3f51abb5d4b2a15ee54215c93d8298.pdf), article page and EKB mirror timed out during targeted access. Its original PDF is also absent from the package. Current checks therefore establish arithmetic against the saved transcription, not fresh source-table validation; no speculative year/unit/height change was made.

## Exact acquisition and minimal preparation

[power_acquisition.json](../../data/validation/power_acquisition.json) copies the two original provenance objects, including exact URLs/query parameters, UTC retrieval timestamps, HTTP status, sizes, SHA256, source lists, API version **v2.10.3**, fill value and response units. Its historical coordinate-status wording is retained as recorded metadata; HANDOFF governs current locality approval.

- 2001–2025 request: `https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MAX%2CT2M_MIN%2CT2MDEW%2CRH2M%2CWS2M%2CALLSKY_SFC_SW_DWN%2CPS%2CPRECTOTCORR&community=AG&longitude=30.95&latitude=31.10&start=&end=&format=JSON&time-standard=LST`
- January–October 2026 uses that exact request with `start=&end=`.
- Retrieved respectively `T18:30:43.237314+00:00` and `T23:27:30.138361+00:00`. Response SHA256 respectively `212bf82f9b2baf09eed440a5a5a6d889891964da2448a7c06a57deb3954f20bf` and `6a957d31aff96ab9b6de604f1ed5bd0def3ee364e742458d5f0e4e9aa37b8700`.

To reproduce the **frozen** calculation, use the local ZIP. With Python 3.12+ and no third-party packages, run from repository root:

```powershell
python data/validation/audit_saved_evidence.py --archive docs/VALIDATION_ARTIFACTS.zip
python -m unittest discover -s data/validation -p 'test_*.py' -v
```

The checker verifies manifest hashes for consumed members, request metadata, source units/geometry, all dates/values, binary64 ET0, the stored monthly transcription, saved numeric NPY/NPZ predictions, data-vintage hashes, target/persistence dates, reconstructed climatology, metrics and static method provenance. It executes no archived code, makes no network calls and writes only JSON to stdout. NumPy is unnecessary; the limited NPY reader accepts only finite C-order little-endian floats, never pickled objects. No archive extraction is required. Missing/corrupt evidence yields nonzero exit and a failed JSON report; archive-dependent tests explicitly skip if the local ZIP is absent, which does not validate the science.

For a **new** acquisition, choose a new empty release directory. Example below is an instruction, not a download executed in this audit:

```powershell
$powerRecorded = (Get-Content data/validation/power_acquisition.json -Raw | ConvertFrom-Json).releases[0]
$powerRelease = 'data/local/power-new-release'
New-Item -ItemType Directory -Path $powerRelease -ErrorAction Stop
$powerFile = Join-Path $powerRelease 'response.json'
$powerResponse = Invoke-WebRequest -Uri $powerRecorded.url -OutFile $powerFile -PassThru
$powerBody = Get-Content -LiteralPath $powerFile -Raw | ConvertFrom-Json
@{
    url = $powerRecorded.url; retrieved_utc = [DateTime]::UtcNow.ToString('o')
    http_status = [int]$powerResponse.StatusCode; http_headers = $powerResponse.Headers
    sha256 = (Get-FileHash -LiteralPath $powerFile -Algorithm SHA256).Hash.ToLowerInvariant()
    bytes = (Get-Item -LiteralPath $powerFile).Length
    response_header = $powerBody.header; response_units = $powerBody.parameters
    geometry = $powerBody.geometry
} | ConvertTo-Json -Depth 20 | Set-Content -Encoding utf8 (Join-Path $powerRelease 'provenance.json')
```

A new response may differ because NASA revises products. Assign a new release ID and retain its actual sources/version/hash; do not replace or evaluate it under the old release ID. The saved-evidence checker intentionally audits the old fixed release, not arbitrary new responses. Normalize date keys to ISO without moving LST boundaries; require aligned unique contiguous dates and expected units. Preserve raw precision; missing/fill values become explicit unavailable data, never imputed zeros. No radiation ×3.6, pressure reconversion or WS2M height correction applies to the saved units. Calculate ET0 under SCIENCE's ASCE-bound method; preserve QC flags and source/release/method identity before integration. Production provenance-column expansion remains pending. Crop-specific demand stays unavailable without applicable stages/Kc.

For the original twelve published/unit/input fixtures, extract only `audit_weather.py` and the two raw POWER JSON members into a **new disposable directory**, retaining the names beneath `work/validation_/` from the ZIP. From that copied directory run `python audit_weather.py`, then `python audit_weather.py --source power_sakha_2026_Jan_Oct_LST.json --suffix _2026_Jan_Oct`. These scripts write outputs; never run them over the only evidence copy. Both were actually rerun here in `work/scientific_validation_/archived_audit_replay/`.

## Executed verification and limits

Runtime actually used: `C:/Users/Amr Hany/AppData/Roaming/uv/python/cpython-3.13.5-windows-x86_64-none/python.exe` (Python **3.13.5**). This is standard-library numerical reproduction, not a recreation of the original Python 3.12.14/CUDA model environment. Shell PATH contained no Python launcher; no dependency/environment installation was needed.

| Check | Actual result |
| --- | --- |
| Read-only independent checker | PASS: 16 consumed archive members hash-checked; 9,435 dates, 75,480 raw values; every saved ET0 matched (maximum absolute difference 0.0 mm/day in this runtime). 38 floor days across both periods, including the original 36 in 2001–2025. Numerical consistency only. |
| Original archived `audit_weather.py` in fresh directory, both commands above | PASS: 12 checks per period; 9,131 and 304 rows. Both regenerated CSV SHA256 values exactly match archived originals. FAO Example 18 remains 3.880259447 mm/day. |
| Saved ML predictions, baselines and intervals | PASS: 17 weekly origins, 119 values per target. MAE, reported RMSE/bias/pinball/lead metrics, coverage and widths reproduce within 0.000003; training-only climatology reconstructed, persistence cutoff checked. |
| Regression suite | PASS: 11 tests, including wrong MAE/coverage/vintage/request/POWER units/station year or wind transcription, wrong forecast horizon/cross-learning and missing evidence. Initial eight tests failed before the checker existed; three additional regressions failed against the incomplete checker before the corresponding checks were added. |
| Documentation / protected-file checks | PASS, separate from scientific tests: seven Markdown files, 40 existing local links and ten documented archive-only targets; tables/fences/UTF-8/whitespace. Seven historical reports byte-preserved; 22 protected file hashes unchanged. Both acquisition objects equal archived metadata. `git diff --check` and `python -m py_compile data/validation/audit_saved_evidence.py data/validation/test_audit_saved_evidence.py` passed. |

| Forecast | Recomputed Tmax MAE (°C) | Recomputed ET0 MAE (mm/day) |
| --- | ---: | ---: |
| Persistence | 2.409664 | 0.753159 |
| Training-only climatology | 1.655546 | 0.523405 |
| Unchanged Chronos-2 | 2.000234 | 0.644224 |
| LoRA Chronos-2 | 1.987569 | 0.640063 |

Differences at finer precision than the reports reflect binary32 versus binary64 metric reduction. The recorded bootstrap intervals were inspected but not independently regenerated. No GPU training/inference/reload rerun, parameter-tensor update remeasurement, independent station/lysimeter truth, full source-table visual check, ETc validation, planner/API tests, frontend build or browser/integration tests ran. The application directories remain placeholders; documentation/fixture arithmetic is not an implemented planner result.

## Gates and next steps

- **No approved API or architecture changes made.** Any proposed semantics/schema change requires Amr/Refaat/Karim/Yahya review; this work adds standalone scientific tooling only.
- **Reference truth unchanged:** P0 rejected; R1/R2 needs_review; zero validated feasible alternatives. Protected cut and later nonconflicting fixture dates remain unchanged. No ETc or forecast recommendation is enabled.
- **Refaat:** obtain the exact source table with years/variable/wind-height labels and station provenance before upgrading the diagnostic; establish applicable crop stages/releases/field constraints before scientific eligibility claims.
- **Amr + Refaat:** approve a bounded fresh ML protocol, uncertainty/usefulness criteria and an eligible near-term decision before any new experiment. Consumed July–October 2026 data are not a fresh test.
- **Amr + Yahya:** decide provider/transmission, session/log/backup retention and deletion before hosted or real-participant collection, per [privacy assumptions](../product/privacy.md). No approval is needed to retain the bounded corrections delivered here; unresolved decisions gate later expansion.

## 12 November pre-push follow-up

The original eleven-test record above describes the 11 November run. The [pre-push audit](-pre-push-science-audit.md) records a later rerun, five additional generation regressions and isolated clean-source reproduction. [REPRODUCING_SCIENCE.md](../science/reproducing.md) replaces manual extraction as the recommended ET0 generation route: the original generator is reviewable repository source, byte-preserved with a frozen manifest; the wrapper never overwrites an existing output directory. Exact input distribution remains an explicit public reproducibility gap. No method, reference outcome, archived report, API, UX artifact or ML result was rewritten. The [multi-grid experiment](../ml/multigrid-proposal.md) is proposed only.
