# MISSION EL GHEET — data and equation audit

Checked 11 November 2026. Numerical implementation and data integrity are checked; farm accuracy is not established.

## Actual data obtained

Original NASA POWER HTTP response files, URLs, retrieval times and SHA256 hashes are saved under `work/validation_2026-11-10/`.

| Period | Days | Variables | Values | Missing-value flags |
|---|---:|---:|---:|---:|
| 2001–2025 | 9,131 | 8 | 73,048 | 0 |
| January–October 2026 | 304 | 8 | 2,432 | 0 |

The research point is 31.10°N, 30.95°E near Sakha. It is not a measured farmer field. Responses use Local Solar Time and the AG community. NASA defines LST by longitude swaths; it is not civil daylight-saving time. Preserve that convention when mapping daily weather to a crop calendar. The newer response includes quick-look source products, so archive quality/version differs across periods. [NASA daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/), [NASA sources and latency](https://power.larc.nasa.gov/docs/faqs/data/).

Checked units: Tmax/Tmin/dewpoint in °C; RH in %; wind at 2m in m/s; shortwave radiation in MJ/m²/day; pressure in kPa; precipitation in mm/day. Dates are contiguous and variables aligned. These responses already use the radiation and pressure units required below. Rainfall is not irrigation supply.

## Calculation contract

Daily grass-reference ET0:

`ET0 = [0.408 Δ (Rn − G) + γ × 900/(T + 273) × u2 × (es − ea)] / [Δ + γ(1 + 0.34u2)]`

Units: mm/day; radiation MJ/m²/day; vapour pressure kPa. Set `T=(Tmax+Tmin)/2`, `G=0` for the daily reference calculation. [FAO56 Chapter 4](https://www.fao.org/4/X0490E/x0490e08.htm).

Supporting relationships:

- `e0(T)=0.6108 exp[17.27T/(T+237.3)]`.
- `es=[e0(Tmax)+e0(Tmin)]/2`; `ea=e0(Tdew)`.
- `Δ=4098e0(T)/(T+237.3)²`; `γ=0.000665P`.
- `Rn=0.77Rs−Rnl`; calculate extraterrestrial radiation from latitude/day and `Rso=(0.75+0.00002z)Ra`.
- `Rnl=4.903×10⁻⁹ × [(Tmax+273.16)⁴+(Tmin+273.16)⁴]/2 × (0.34−0.14√ea) × (1.35Rs/Rso−0.35)`.

The audit uses dewpoint rather than deriving vapour pressure from mean RH. Both are daily aggregates; this does not remove source uncertainty. [FAO56 Chapter 3](https://www.fao.org/4/X0490E/x0490e07.htm).

An explicit radiation safeguard bounds `Rs/Rso` to 0.3–1.0, following ASCE-EWRI's daily equation18, printed page20. This affects 36 days in 2001–2025; 19 would otherwise have a negative cloudiness factor. The mean ET0 difference is 0.000406 mm/day, maximum 0.302 mm/day. Raw values and sensitivity results are retained. [Original ASCE report](https://content-hub.uidaho.edu/api/public/content/9d9ea3f325e945158730b61661e8add8?v=cc545c86).

Crop demand remains `ETc(t)=Kc(t)ET0(t)` and crop-period demand is its daily sum. One mm over one hectare equals 10m³, but this is an equivalent ET volume, not pumped irrigation. Crop stages, coefficients and management must be sourced; generic stages remain declared assumptions. Averaged berseem cutting cannot calculate the exact marginal demand of another cut. [FAO56 Chapter 6](https://www.fao.org/4/X0490E/x0490e0b.htm).

## Verification performed

Twelve checks passed: nine comparisons with published FAO values, two arithmetic/unit checks and invalid-temperature rejection. Full Example18 reconstruction gives **3.880259 mm/day**, compared with published **3.88**. This now covers the supporting radiation, humidity, wind and pressure calculations, beyond the earlier core-equation-only check.

An independent implementation reproduced every saved 2001–2025 ET0 value within 3.55×10⁻¹⁵ mm/day and matched all raw weather inputs. See [independent review](validation_equations_review.md). The audit is explicitly restricted to its recorded point; latitude/day checks and unsupported polar-night handling were added after review.

Mean-RH and dewpoint methods differ by about 0.522 mm/day on average in this archive. This is method sensitivity, not an uncertainty interval. Daily mean dewpoint exceeds daily minimum temperature on 306 days; aggregation differs and this flag does not by itself prove invalid data. No silent correction to these inputs was made.

## Material accuracy limitation

A limited comparison with 11 monthly values in Aiad's published Sakha station table found material discrepancies: NASA Tmax was higher by about 2.99°C on average; RH lower by 11.55 percentage points; wind higher by 1.74m/s. This is a diagnostic against one printed table, not a quality-controlled station validation or proof that either source is correct. No bias correction was fitted, and pan evaporation was not treated as ET0. [Aiad2019, Table2](https://jenvbs.journals.ekb.eg/article_54170_dd3f51abb5d4b2a15ee54215c93d8298.pdf).

**Consequence:** use regional historical scenarios and estimated reference demand with clear provenance. Do not call these field-measured weather, calibrated irrigation amounts or validated crop outcomes. ETc applicability, the complete recommendation engine and farmer comprehension require later validation.
