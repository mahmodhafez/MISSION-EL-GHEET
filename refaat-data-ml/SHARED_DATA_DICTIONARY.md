# Sakha data dictionary

Release `sakha-power-lst-20261110-et0-v1` contains one regional POWER point, `sakha_31.10_30.95`. The historical and recent receipts document two separate captures. All CSVs use a header, comma separator, decimal point and ascending observation dates within a time series. Load dates explicitly as ISO calendar dates and physical quantities as floating-point numbers. Daily LST labels represent local solar days. Do not pass them through Cairo civil-time or daylight-saving conversions.

## Source and processing fields

| Field | Type / unit | Meaning |
|---|---|---|
| site_id | string | Fixed query at 31.10° N, 30.95° E. GeoJSON returns longitude first and grid elevation 4.96 m. Single-site target-only CSVs carry this field once in the accompanying release.json. |
| date | ISO YYYY-MM-DD | Inclusive daily observation date, used to align measurements, targets and quality records. |
| snapshot | enum | historical (2001–2025) or recent (Jan–Oct 2026), linked to source_manifest.json. |
| partition | enum | fit (2001–18), diagnostic_validation (2019–21), reserve_not_blind (2022–25) or 2026_quarantine. |
| tmax_c | float °C | T2M_MAX, daily maximum 2 m air temperature. First model target. |
| tmin_c | float °C | T2M_MIN, daily minimum 2 m air temperature. |
| tdew_c | float °C | T2MDEW, daily 2 m dew/frost point used for actual vapour pressure. |
| rh_percent | float % | RH2M, daily 2 m relative humidity used in the alternate humidity path. |
| wind2_m_s | float m/s | WS2M, daily 2 m wind speed. Already at the reference height. |
| solar_mj_m2_day | float MJ/m²/day | ALLSKY_SFC_SW_DWN, incident surface shortwave radiation. Already a daily energy total. |
| pressure_kpa | float kPa | PS, surface pressure. |
| rain_mm_day | float mm/day | PRECTOTCORR, corrected precipitation. |
| et0_mm_day | float mm/day | Second model target. Daily FAO-56 grass-reference ET₀ using dewpoint and the ASCE radiation-ratio bound. |
| et0_rhmean_approx_mm_day | float mm/day | Sensitivity using mean RH with mean saturation pressure. |
| et0_without_cloud_floor_mm_day | float mm/day | Dewpoint sensitivity removing only the 0.3 lower cloud-ratio bound. The upper cap of 1 remains. |

The canonical `data/sakha_daily.csv` contains the four metadata columns and all eleven numeric columns above. `fit_targets.csv` and `diagnostic_validation_targets.csv` contain exactly `date,tmax_c,et0_mm_day` in that order. Daily weather at a **target date** may be used to verify an outcome after it becomes available. Expose an input to a predictive model only if that value had arrived by the issue timestamp.

## Quality flags

`data/quality_flags.csv` joins to the canonical table on `snapshot,date` for this site. Flags are integers 0/1, ratios and pressure are floats, and column lists and dispositions are strings.

| Field | Meaning when set |
|---|---|
| hard_invalid | Physical-input gate failure. The rigid release builder rejects an invalid snapshot before publication. Every published row in this release has 0. |
| rs_above_rso | Incoming shortwave exceeds computed clear-sky radiation (ratio > 1). |
| raw_ratio_below_0_3 | Raw Rs/Rso < 0.3, activating the lower longwave cloudiness bound. |
| negative_unbounded_cloud_factor | 1.35 × raw ratio − 0.35 < 0. Can coincide with raw_ratio_below_0_3. |
| negative_vpd | Calculated saturation minus actual vapour pressure is negative. |
| negative_et0 | Calculated reference ET is negative. Preserve the flag for scientific review. |
| dew_above_tmin | Daily dewpoint exceeds daily minimum temperature. Aggregates need not describe the same instant. |
| rs_over_rso | Raw daily incoming shortwave / clear-sky shortwave, dimensionless. |
| vpd_kpa | Saturation minus actual vapour pressure, kPa. |
| mixed_sources_in_response | The *response header* for this period also lists low-latency products. A day-specific source cannot be inferred. |
| seasonal_3iqr_columns | Pipe-separated columns outside monthly Q1−3×IQR or Q3+3×IQR using training-only 2001–18 thresholds. Empty string means none. Zero-IQR screens are disabled. |
| qc_disposition | retain or retain_review. Statistical and daily diagnostic flags trigger review. Header-level mixed_sources_in_response is independent of this disposition: recent rows may have retain. Both dispositions preserve the observation; neither is an independent station check. |

## Evaluation windows

`data/forecast_windows.csv` contains 36 diagnostic rows, one per issue on the 15th of each month in 2019–2021. `partition` = diagnostic_validation. `issue`, `context_start`, `cutoff`, `target_start`, `target_end` are ISO dates. `context_days` and `scored_days` are integer counts. The endpoints in this file are inclusive. Context is D−66 through D−7, scored targets D+1 through D+7. Forecast from the cutoff for 14 steps and score steps 8–14. Earlier archived outcomes are eligible as later context only under the stated availability assumption.

## Version and provenance

`data/source_manifest.json` contains archived API URLs, parameter IDs, units, date bounds, capture UTC, SHA256 of original response bytes and archived derived CSVs, point geometry, and product-family lists. The recent header adds GEOSIT/FLASHFLUX to MERRA2/SYN1DEG/POWER. Version v2.10.3 refers to the daily API. `data/release.json` binds the packaged normalized files to site, method, and checksums. `PACKAGE_MANIFEST.json` verifies the files actually delivered to each recipient. The project’s `provenance/input_archives.json` identifies original ZIP members even when those members are not distributed in a role-specific package.

ET₀ measures reference atmospheric demand. Crop water use, soil-water balance, irrigation withdrawal, yield and agronomic feasibility require additional evidence and belong to different decisions.
