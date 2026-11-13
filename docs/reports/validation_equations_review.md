# Independent review of weather and ET0 calculations

**Post-review update, 11 November:** the audit now asserts its declared source-point geometry, validates latitude/day ranges and rejects unsupported zero-clear-sky-radiation conditions. The original findings below describe the reviewed version; the numerical outputs for Sakha remain unchanged. A later printed monthly station-table diagnostic is recorded separately in the data audit, and is not an ET0 calibration.

Reviewed . Scope: `audit_weather.py`, `weather_audit.json`, `weather_et0.csv`, the saved POWER response and its provenance, plus the locally saved ASCE-EWRI 2005 reference. No implementation or data files were changed. This review concerns numerical consistency, not local agricultural validation.

**Finding:** no equation or unit error was found for the saved research point near Sakha. An independent expression of the daily calculation reproduced all 9,131 saved ET0 values to floating-point precision. Three input/reuse weaknesses remain; they do not change this particular dataset's results.

## Fresh checks performed

| Check | Result |
|---|---|
| Original response checksum versus audit report | Exact SHA-256 match: `212bf82f9b2baf09eed440a5a5a6d889891964da2448a7c06a57deb3954f20bf` |
| Saved response geometry | Longitude 30.95, latitude 31.1, elevation 4.96 m; matches the audit's fixed latitude |
| Every source weather value versus CSV | All 73,048 values matched across 9,131 dates and eight variables |
| Independent daily ET0 recomputation | Maximum absolute difference: 3.55 × 10^-15 mm/day |
| Re-execution of fixture section without running file-writing code | All 12 checks passed: nine published-reference checks and three arithmetic/input checks |
| FAO56 Example 18 reconstruction | 3.880259447 mm/day, compared with published 3.88 mm/day |
| Daily radiation-floor flags | 36 days below the 0.3 radiation ratio; 19 days with a negative unbounded cloud factor |
| Floor sensitivity independently recomputed | Mean absolute difference 0.000405885 mm/day; maximum 0.301850 mm/day |

The independent all-row calculation was separately expressed in the review process; it was not a call to `reference_et0`. The published fixture and boundary probes additionally exercised the original functions in isolation. The original top-level script was not rerun, so its saved outputs were not overwritten.

## Equations and units

The code implements the daily grass-reference Penman–Monteith expression with `G = 0`, daily mean temperature from the minimum and maximum, vapour pressure in kPa, 2 m wind in m/s, and radiation in MJ/m²/day. It returns ET0 in mm/day. Its pressure factor, saturation-pressure average, slope, albedo, radiation geometry, longwave temperature conversion and daily aerodynamic constants agree with the cited FAO equations. [FAO56 Chapters 2–4; opened in this review](https://www.fao.org/4/x0490e/x0490e06.htm).

The saved POWER metadata explicitly supplies radiation in MJ/m²/day and pressure in kPa, so neither an additional kWh conversion nor a Pa conversion is needed. `WS2M` already represents 2 m wind; the 10 m conversion belongs only to the published fixture. Rainfall is retained but is not incorrectly subtracted from ET0. The 365-day solar-geometry denominator follows the published expression, including the use of calendar day-of-year. Daily `G = 0` is the reference-surface approximation, not a finding that the actual field exchanges no soil heat. [FAO56 Chapter 3; OPENED](https://www.fao.org/4/x0490e/x0490e07.htm).

The full published example is a useful equation fixture, but it does not validate Sakha weather or forecast skill. The source itself reports 3.88 mm/day before rounding to 3.9; the reconstruction is consistent with that distinction. [FAO56 Chapter 4, Example 18; OPENED](https://www.fao.org/4/x0490e/x0490e08.htm).

## Cloudiness safeguard and humidity interpretation

The lower bound is explicitly supported by **ASCE-EWRI 2005 Equation 18, printed page 20** (PDF page 31 in the saved file): the daily/monthly `Rs/Rso` ratio is limited to 0.3–1.0. The code retains FAO56's constants, including 4.903 × 10^-9, while borrowing that daily safeguard. Describe it as **FAO56 ET0 with the documented ASCE daily cloudiness bound**, rather than an entirely unmodified FAO56 implementation. [Original ASCE report URL; relevant saved text inspected locally](https://content-hub.uidaho.edu/api/public/content/9d9ea3f325e945158730b61661e8add8?v=cc545c86).

**The 19 negative values are raw cloudiness factors, not negative ET0 estimates.** The report records zero negative final ET0 values. The code preserves the raw ratio and an unbounded-floor comparison rather than silently clipping final ET0.

Daily dewpoint exceeds daily minimum air temperature on 306 days. This merits review of temporal aggregation and humidity consistency; it is not, by itself, proof that those daily records are impossible. The alternative mean-RH calculation differs by an average absolute 0.522 mm/day. It is a method sensitivity, not a measured error or uncertainty interval. Neither method is independently validated against a station here.

## Reuse weaknesses to address before broadening the audit

1. **Fixed latitude is not asserted against the response.** Every row calls the function with 31.10. That is correct for the saved geometry, but changing the input file to another point could silently calculate radiation at the old latitude. Derive or explicitly validate coordinates before reuse.
2. **Latitude and day-of-year domains are unchecked.** Fresh probes accepted latitude 100° and day 0, returning finite ET0 values. Validate legal geographic and calendar inputs rather than relying on the trigonometric clamp. This did not affect the current valid point/dates.
3. **Zero clear-sky radiation is unhandled.** A polar-night probe raised `ZeroDivisionError` at `Rs/Rso`. Either restrict and enforce the supported geography or define a separately supported polar/low-radiation method. No such condition occurred at Sakha.

## Limits on claims

The evidence supports **a reproducible numerical calculation over the saved historical gridded series**, with published fixtures and recorded safeguards. It does not establish field-scale accuracy, local calibration, irrigation requirements, crop-water savings, soil-health improvement, crop-coefficient validity, or meaningful model skill.

The maximum computed ET0 is 14.049 mm/day on ; the stored input is hot, dry and windy. Retain it for meteorological review rather than cap it because it looks large. Local station/lysimeter comparison and seasonal bias analysis remain outstanding. The simple `Kc × ET0` fixture checks multiplication only; it does not validate crop stages, berseem cuts, water stress or a crop-demand pipeline. Current historical archives are also not historical publication vintages or observations available at a past forecast issue time.
