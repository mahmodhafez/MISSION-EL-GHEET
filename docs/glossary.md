# Glossary

**Read this if…** a doc uses a term or code you don't recognise.

Last reviewed .

---

| Term | Meaning |
|---|---|
| **Promise Test** | The deterministic check of a four-season plan against protected commitments and agricultural rules. Returns `feasible`, `rejected` or `needs_review`. |
| **Season Path / سكة المواسم** | The approved interaction model: a visible four-season path, one question at a time. "Show, Speak, Choose, Confirm". |
| **Fieldlight (Hybrid)** | The approved visual identity: pale-green canvas, botanical arched season cards. See `design/fieldlight.md`. |
| **Season Replay** | Comparing plans on the same historical NASA POWER weather years. Historical evidence, not a forecast. |
| **Evidence Card** | The saved takeaway for one exact plan version: dates, sources, assumptions, open checks, plus matching audio. |
| **UH-001** | "Uncle Hussein", the fictional reference scenario. Expected result: P0 rejected, zero feasible alternatives. |
| **P0** | Hussein's current plan (rejected: maize sowing on 15 May clashes with the protected berseem cut on 20 May). |
| **R1 / R2** | Timing variants that move maize sowing to 28 May / 1 Jun. Both `needs_review`, not feasible. |
| **SB-001** | A second scenario mentioned in planning docs; its full definition is missing from the repo. |
| **feasible / rejected / needs_review** | Plan statuses. Hard failure → rejected; unresolved required check → needs_review; otherwise feasible. |
| **verified / proposed / open** | Evidence statuses. Independent of farmer confirmation (`unconfirmed / confirmed / confirmed_unknown`). |
| **ET0** | FAO-56 reference evapotranspiration (with the ASCE daily cloudiness bound). Atmospheric demand on reference grass, **not** irrigation use. |
| **ETc** | Crop evapotranspiration = Kc × ET0. Unavailable unless sourced crop coefficients and stages exist. |
| **NASA POWER** | NASA's gridded daily weather API. Point 31.10° N, 30.95° E; community AG. |
| **LST** | Local Solar Time, POWER's day convention. Not Egyptian civil time. |
| **`data_release`** | The single version token naming the catalogue, rules and weather data a result was computed with. |
| **`meg_core` / `meg_ml`** | Planned standalone Python packages for shared contracts, planner, climate and baselines (`meg_core`) and ML experiments (`meg_ml`). Not created yet. |
| **`forecast_bundle.json`** | The precomputed, schema-validated file the ML side hands to the backend. |
| **KB** | The agronomy knowledge base draft: `planner/agronomy-kb.v0.1.json`. |
| **D1–D8** | Backend design decisions (12 Nov), in `backend/backend-design.md`. |
| **D01–D10** | Planner blueprint decisions awaiting approval, in `planner/blueprint.md` §1. |
| **FR-01…FR-07** | The seven functional requirements in `product/product.md`. |
| **Astra / Sol** | Names older docs give to frontend build workstreams: Astra builds the reference screens, Sol extends them. They seem to be AI-agent sessions run by Amr; confirm with Amr. |
| **Chronos-2 + LoRA** | The pretrained forecasting model and the fine-tuning method tried on 11 Nov. Lost to seasonal climatology. |
| **Seasonal climatology** | Forecast = historical distribution for that calendar day (±15 days). The current baseline. |
| **Validation ZIP** | `docs/VALIDATION_ARTIFACTS.zip`, ~470 MB of frozen weather, ET0, predictions and weights. Not in git. |
