# MISSION EL GHEET — data handoff for Refaat

11 November 2026. Owner: **Ahmed Mohamed Refaat**. This defines logical research files and validation rules, not a database, service architecture or new implementation. **VERIFIED** identifies inspected evidence; **REQUIREMENT** is the agreed data contract; **PROPOSED** needs implementation review; **OPEN** marks missing evidence. Equations and agronomic interpretation belong in [SCIENCE.md](SCIENCE.md); experiment splits and forecast outputs belong in [ML_EXPERIMENT.md](ML_EXPERIMENT.md).

## 1. Required sources and actual coverage

**VERIFIED:** original NASA POWER daily point responses were saved for provisional Sakha coordinates **31.10° N, 30.95° E**, community **AG**, time standard **LST**. The returned grid elevation is **4.96 m**, not a surveyed field elevation. Coverage is 2001-01-01–2025-12-31 (**9,131 days**) and 2026-01-01–2026-10-31 (**304 days**): **75,480 values** across eight variables, with aligned dates and no missing-value flags. This confirms these exports, not every future request or field representativeness. [NASA daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/).

The saved response headers report API v2.10.3; 2001–2025 sources are MERRA2/SYN1DEG/POWER; the 2026 response additionally names GEOSIT/FLASHFLUX. Preserve each response's source list without inventing date-level source transitions. POWER combines products with different native resolutions; a requested point is not field-scale observation, and nearby requests may share source cells. [NASA data guidance](https://power.larc.nasa.gov/docs/tutorials/).

| POWER variable | Normalized field | Unit in downloaded response | Role |
|---|---|---|---|
| T2M_MAX | `tmax_c` | °C | Replay, ET0, ML target |
| T2M_MIN | `tmin_c` | °C | ET0 |
| T2MDEW | `tdew_c` | °C | Actual vapour pressure for ET0 |
| RH2M | `rh_percent` | % | Quality/sensitivity check |
| WS2M | `wind2_m_s` | m/s at 2 m | ET0 |
| ALLSKY_SFC_SW_DWN | `solar_mj_m2_day` | MJ/m²/day | ET0 |
| PS | `pressure_kpa` | kPa | ET0 |
| PRECTOTCORR | `rain_mm_day` | mm/day | Weather context; not irrigation supply |

**REQUIREMENT:** POWER is the only core NASA dataset. Crop rules and soil profiles require primary agricultural sources; start with the exact source ledger in [the agronomy audit](validation_agronomy.md). Preserve wheat, berseem, grain maize and grain sorghum entries even when eligibility is unresolved. No HLS/IMERG downloads, invented station labels or extra sensors are required.

## 2. Reproducible preparation

1. Preserve original response bytes, request parameters, UTC retrieval timestamp, HTTP status, response header, units and SHA256. A refresh creates a new dataset release; it never silently replaces evaluated data.
2. Parse date keys into ISO `YYYY-MM-DD`; retain the source LST day boundary. Do not convert daily labels through Egyptian daylight-saving time. Sort, check leap days, and require unique site/date/time-standard/release keys. Conflicting duplicates fail validation.
3. Convert the documented fill value (currently −999) to null plus a quality flag. Never turn missing rain into zero. Verify units before normalization: this response already supplies radiation in MJ/m²/day and pressure in kPa; no ×3.6 or second pressure conversion is appropriate.
4. Retain raw numeric precision and use float64 calculations. Compute `et0_mm_day` under the versioned method in SCIENCE; round only for presentation. Preserve cloud-ratio, input-quality and method flags. Do not substitute mean RH for missing dewpoint without a separately declared method.
5. Do not impute or smooth the audited series. For later missing data, mark affected days and block dependent conclusions until a documented policy is approved. Missing RH/rain alone does not invalidate ET0 when all required equation inputs remain valid.

Dates, calculations and sources must remain traceable from raw response to replay/ML output. Current archives are revised products, not historical issue-time snapshots; simulated availability must be labelled accordingly. [NASA availability FAQ](https://power.larc.nasa.gov/docs/faqs/data/).

## 3. Logical schemas

**REQUIREMENT:** UTF-8 text, ISO dates, UTC retrieval times; numeric values remain numbers, unknowns are null with a reason. IDs are stable strings; every scientific assertion links to a source and page/table/section. Use evidence labels `verified`, `proposed`, `open`; record farmer confirmation separately. These contracts describe expected exports, not files already generated.

### `sites.json` and `source_manifest.json`

Site fields: `site_id`, Arabic/English name, latitude/longitude, coordinate status, elevation value/unit/source, locality scope and known source-cell metadata. Unknown native-cell identifiers stay null.

Source fields: `source_id`, publisher/title, URL, version/year, retrieval time, file hash, locator, geographic/temporal scope, original units and license/terms URL/status. API entries also contain exact request and response metadata. A document's publication date is not a measurement date; usable access does not establish redistribution permission.

### `weather_et0.csv`

Required columns: `site_id`, `date`, `time_standard`, the eight normalized fields above, `et0_mm_day`, `et0_method_id`, `source_id`, `dataset_release`, `qc_status`, `qc_flags`. Numerical fields are nullable only with an explanation; ET0 is null if required inputs are missing/invalid. `qc_status` is `pass`, `review` or `invalid`; `qc_flags` is a semicolon-separated list of documented codes, empty when none.

The saved audit CSVs already contain the date, eight weather fields and ET0. Their two additional columns, `et0_rhmean_approx_mm_day` and `et0_without_cloud_floor_mm_day`, are sensitivity outputs, **not extra independent ML targets**. Adding the provenance columns is a handoff task; do not imply it has already happened.

### `crop_catalogue.json`

Each `profile_id` identifies crop, purpose, cultivar/type, locality and management assumptions. Required groups:

- Identity: stable `crop_id` (`wheat`, `berseem`, `grain_maize`, `grain_sorghum`), Arabic/English names, grain/forage/seed purpose, crop family, legume status and sourced rooting descriptors. Unknown depth stays null.
- Calendar: **separate** observed trial dates, recommended planting intervals, and assumed durations. Include source year, locality/land class, harvest endpoint and applicability. “May preferred” is not “June biologically impossible.”
- Demand: reference surface, initial/development/mid/late stage lengths, Kc initial/mid/end, cutting basis, coefficient adjustment conditions and sources. Unresolved values remain null; never borrow a grain curve for forage or a seasonal average for an exact extra cut. [FAO coefficient framework](https://www.fao.org/4/X0490E/x0490e0b.htm).
- Rules: `rule_id`, condition, effect (`hard`, `preference`, `review`), evidence status, applicability and source locator. Do not promote a trial observation into a universal hard constraint. Farmer locks are stored separately.

### `soil_profiles.json`

Fields: `profile_id`, origin (`published_study`, `field_measurement`, `farmer_report`, `unknown`), site scope, source, sampling date and **measurement-level** depth/method/value/unit. Include texture, pH, EC and any supported field-capacity/wilting-point information. Preserve raw values alongside justified normalization.

Keep Aiad's saline trial and Darwesh's different trial separate. EC extraction methods and pH suspension ratios matter. Gravimetric water content cannot become volumetric water content without compatible bulk density. No unsupported salinity threshold or generic “Sakha soil” is acceptable. Exact study profiles and limitations are in the [agronomy ledger](validation_agronomy.md).

### `scenario_inputs.json` and `replay_manifest.json`

Scenario fields: ID/version, `illustrative` or `farmer_confirmed` origin, locality, soil profile or unknown reason, field area with unit, four ordered crop-profile/date entries, harvest/release/preparation assumptions, protected commitments, negotiable bounds, farmer priority order and irrigation restrictions/availability status. Grain/forage quantities describe **requirements**, not predicted production. Every critical input retains its source and confirmation status. Public fixtures contain no identifiable farmer audio or private records.

Replay manifest fields: plan versions, `feasible`/`rejected`/`needs_review` status, shared historical block IDs and anchor years, calendar/leap policy, data release, ET0/Kc method versions, assumptions, common coverage/missing policy and metric definitions. Exact mapping and interval semantics follow SCIENCE; unresolved policy prevents a reproducible numerical claim.

### ML handoff

Export only the permitted histories and target columns; the executed experiment uses `tmax_c` and `et0_mm_day`. The split/origin manifest records issue date, input cutoff, context start/end, target dates, partition, model revision and data vintage. Future weather is excluded from inputs; crop copies are not independent samples. Splits, consumed-test restrictions and forecast-output fields are specified once in [ML_EXPERIMENT.md](ML_EXPERIMENT.md).

## 4. Acceptance checks and expected delivery

**REQUIREMENT:** deliver the raw responses/manifests, normalized weather, crop/source/soil catalogues, labelled scenarios, replay/ML manifests and a short quality report listing counts, failures, unresolved fields and exclusions.

Check date coverage and duplicates; Tmin ≤ Tmax; RH within 0–100%; nonnegative wind/radiation/rain; positive pressure; finite required values. Keep plausible-range warnings separate from hard physical failures. Daily mean dewpoint above daily Tmin is a review flag, not automatic rejection. Preserve the solar-ratio floor diagnostics and flag any unexpected negative ET0 rather than silently clipping it.

Reproduce the reference fixtures and sample/all-row outputs after calculation changes. Ensure foreign IDs resolve, all four seasons retain their purpose/locks, coefficients have applicable sources, and every ML row obeys its issue-time cutoff. Missing source, stage or eligibility evidence must remain visible in the quality report.

**VERIFIED starting artifacts:** [2001–2025 provenance](../work/validation_2026-11-10/power_provenance.json), [2026 provenance](../work/validation_2026-11-10/power_provenance_2026_Jan_Oct.json), [historical weather](../work/validation_2026-11-10/weather_et0.csv), [2026 weather](../work/validation_2026-11-10/weather_et0_2026_Jan_Oct.csv), and [saved-artifact verification](../work/validation_2026-11-10/model_test/artifact_verification.json). Preserve their hashes and distinguish these inspected files from the proposed expanded handoff schemas.

**OPEN delivery gates:** pilot approval; applicable cultivar/stage/cutting/preparation rules; grain-sorghum eligibility; compatible field-soil information; a fresh ML assessment plan. No adviser, field survey, raw station truth or locally validated yield labels are available in this handoff.
