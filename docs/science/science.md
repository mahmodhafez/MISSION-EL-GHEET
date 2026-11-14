# MISSION EL GHEET — science contract

**Read this if…** you're touching dates/intervals, ET0/ETc, replay metrics or evidence labels.

Status: Approved  · Owner: Refaat. Last reviewed .

**VERIFIED** means demonstrated by the recorded audit or a cited source, within its stated scope. **REQUIREMENT** means required product behaviour, not implemented evidence. **PROPOSED** means a reviewable modelling choice. **OPEN** identifies unresolved evidence or decisions. The [validation verdict](../reports/MISSION_EL_GHEET_Validation_Verdict.md) governs readiness. Interaction belongs in [PRODUCT.md](../product/product.md), data contracts in [DATA_SPEC.md](data-spec.md), and training/results in [ML_EXPERIMENT.md](../ml/ml-experiment.md).

## 1. Local evidence and its limits

**APPROVED SCOPE:** use one Sakha/Kafr El-Sheikh research scenario, as recorded in [HANDOFF.md](../archive/handoff.md). This is locality approval, not scientific validation of a farmer's field. Published soil retains its source-reported experimental measurements, never a measurement of the farmer's field. Preserve all four candidate crops: wheat, berseem, grain maize and grain sorghum; evidence gates govern which can support a claimed feasible option.

**VERIFIED:** a Sakha trial grew Giza 168 wheat from ** to **, followed by Single Hybrid 10 maize from **15 May to **. Its 0–20 cm soil had 57.18% clay, pH 8.48 measured in 1:2.5 suspension, and EC 6.43 dS/m in saturated-paste extract. This was an irrigation/amendment experiment on saline soil. These observations do not establish hard planting windows, universal durations, or stress-free crop demand. [Aiad 2019, pp. 148–150/Table 1](https://jenvbs.journals.ekb.eg/article_54170_dd3f51abb5d4b2a15ee54215c93d8298.pdf).

**VERIFIED:** Ministry/ARC bulletin 1429/2023 recommends **May for old-land maize** and fertile, well-drained, aerated, non-saline soil; its different new-land guidance must not be transferred indiscriminately. **PROPOSED:** May is the conservative catalogue preference interval. Dates outside that support are not automatically biologically impossible. The saline trial above is not representative proof of the bulletin's preferred conditions. [Original bulletin, pp. 4–5](https://misrelzraea.com/wp-content/uploads/2024/03/%D9%86%D8%B4%D8%B1%D8%A9-%D8%A7%D9%84%D8%B0%D8%B1%D8%A9-%D9%86%D9%87%D8%A7%D8%A6%D9%89-copy_compressed.pdf).

**VERIFIED:** FAO distinguishes Lower-Egypt multicut Miskawi berseem from single-cut Fahl and describes establishment/drainage limitations. This supports explicit crop-type and forage/seed distinctions, not promised cut dates or feed quantities. [FAO Egyptian Clover, pp. 65–68](https://www.fao.org/4/i3500e/i3500e.pdf). **SOURCE-REPORTED OBSERVATIONS:** the later [agronomy ledger](../planner/agronomy-evidence.md), B2/M3/M4/S1, records named local berseem, later-sown maize and hybrid-888 grain-sorghum trials. Preserve their experimental dates and management scope; the earlier [Nubaria sorghum trial](https://link.springer.com/article/10.1186/s42269-019-0155-1) is a separate observation. **OPEN:** transferable date/cultivar/field-specific eligibility, harvest/release and preparation. Local trial existence does not establish a validated substitute for Hussein's fictional field. The [targeted audit](../reports/scientific-validation-fixes.md) distinguishes prior source checks from this session's executable reproduction.

## 2. Four-season feasibility

**REQUIREMENT:** preserve confirmed protected crops, forage cuts and other commitments. Evaluate four consecutive cropping seasons on the same field, including crop occupation, harvest/removal, preparation intervals, supported planting dates, and declared soil/irrigation constraints. Unknown critical inputs stay unknown. Preserving a planned cut does not guarantee its biomass or livestock feed sufficiency.

**PROPOSED deterministic contract:** enumerate combinations of supported crop profiles and discrete farmer-approved date choices for each season. Occupation is \([s_i,r_i)\): sowing inclusive; release is the first free date after harvest/removal. With preparation lasting \(p_i\) days, require \(s_{i+1}\ge r_i+p_i\). An unknown preparation interval is not zero. Changing sowing reruns the source-supported maturity/release mapping; never invent a fixed duration. Classify each combination as **feasible** when all checks pass, **rejected** for a demonstrated violation, or **needs review** for missing evidence/input; only feasible combinations become offered repairs.

Choose distinct feasible options relevant to confirmed farmer priorities, minimizing unnecessary edits among otherwise equivalent options. Do not impose crop-preservation over those priorities or combine trade-offs into one score. Stable crop/date ordering resolves equivalent display ties reproducibly.

**REQUIREMENT:** show the current plan and up to two meaningfully distinct feasible alternatives. Label a date-only change a timing variant. Keep grain/forage purpose, duration, remaining commitments and trade-offs visible. No combined “best farming” score; no valid alternative is an acceptable answer. Any infeasibility explanation must distinguish an actual constraint conflict from missing catalogue evidence.

**PROPOSED test:** a protected 20 May berseem cut conflicts with 15 May same-field maize sowing. Both dates cannot stand; the cut remains protected. The 20 May cut is a declared test input, not an agronomic recommendation. A repair needs a supported subsequent planting/release case and preparation interval. Do not invent a downstream conflict or silently remove forage.

## 3. Reference atmospheric demand

**VERIFIED:** the saved POWER series and independent calculation audit reproduce daily grass-reference ET0 for the recorded research point. **REQUIREMENT:** call it **FAO56 ET0 with the ASCE daily cloudiness bound**, in mm/day:

\[
ET_0=\frac{0.408\Delta(R_n-G)+\gamma\frac{900}{T+273}u_2(e_s-e_a)}{\Delta+\gamma(1+0.34u_2)},\qquad T=(T_{max}+T_{min})/2,\quad G=0.
\]

Here temperature is °C, wind at 2 m is m/s, vapour pressure is kPa, and radiation is MJ/m²/day. Daily G=0 is a reference-surface approximation. [FAO56 chapter 4](https://www.fao.org/4/X0490E/x0490e08.htm).

Supporting equations use supplied pressure P in kPa, dewpoint temperature, latitude φ in radians, elevation z in metres and calendar day-of-year J:

\[
e^\circ(T)=0.6108\exp\left(\frac{17.27T}{T+237.3}\right),\quad e_s=\frac{e^\circ(T_{max})+e^\circ(T_{min})}{2},\quad e_a=e^\circ(T_{dew})
\]
\[
\Delta=\frac{4098e^\circ(T)}{(T+237.3)^2},\quad\gamma=0.000665P
\]
\[
d_r=1+0.033\cos(2\pi J/365),\quad\delta=0.409\sin(2\pi J/365-1.39),\quad\omega_s=\arccos(-\tan\phi\tan\delta)
\]
\[
R_a=\frac{24(60)}{\pi}(0.0820)d_r[\omega_s\sin\phi\sin\delta+\cos\phi\cos\delta\sin\omega_s],\quad R_{so}=(0.75+0.00002z)R_a
\]
\[
q=\min(1,\max(0.3,R_s/R_{so})),\quad R_{ns}=0.77R_s
\]
\[
R_{nl}=4.903\times10^{-9}\frac{(T_{max}+273.16)^4+(T_{min}+273.16)^4}{2}(0.34-0.14\sqrt{e_a})(1.35q-0.35),\quad R_n=R_{ns}-R_{nl}.
\]

These retain FAO56's constants and solar geometry, including its 365 denominator. [FAO56 chapter 3](https://www.fao.org/4/X0490E/x0490e07.htm). The q-bound follows [ASCE-EWRI 2005, Eq. 18/p. 20](https://content-hub.uidaho.edu/api/public/content/9d9ea3f325e945158730b61661e8add8?v=cc545c86). Preserve raw ratios and sensitivity; do not silently clip final ET0. Reject unsupported zero-clear-sky-radiation cases and invalid inputs; assert source-point geometry before reuse.

**VERIFIED:** twelve numerical checks passed, including full FAO Example 18 reconstruction (3.880259 versus 3.88 mm/day), and independent reproduction of every saved 2001–2025 value. **OPEN:** field accuracy. A limited station-table comparison showed material weather differences; it is neither quality-controlled calibration nor proof either source is correct. Daily humidity-method differences remain sensitivity, not error bounds. [Calculation audit](../reports/validation_data_equations.md), [independent review](../reports/validation_equations_review.md).

**11 November targeted recheck:** [offline executable validation](../reports/scientific-validation-fixes.md) reproduced both saved periods (9,435 days) and the archived twelve-check calculation for each period. Station arithmetic uses eleven full matching months, November 2015–September 2016, equally weighted across months. Its wind conversion assumes the archived transcription's km/day at 2 m, divided by 86.4 to m/s; that primary table/height has not been freshly reverified. These differences must not be presented as a validated station bias, calibration, or crop-demand error bound.

## 4. Conditional crop demand

**VERIFIED method:** \(ET_c(t)=K_c(t)ET_0(t)\); seasonal demand sums daily values. This describes standard, non-stressed crop conditions. **OPEN:** applicable local coefficients, stage durations, cultivar/harvest definitions and management. Generic reference coefficients alone do not validate a local curve. [FAO56 chapter 6](https://www.fao.org/4/X0490E/x0490e0b.htm).

**PROPOSED conditional curve:** hold \(K_{c,ini}\) during the initial stage; interpolate linearly to \(K_{c,mid}\) during development; hold it through mid-season; interpolate to \(K_{c,end}\) during late season. Source-labelled stage lengths define the boundaries and must sum to the crop period. Evaluate the curve at each day's midpoint; sum from sowing inclusive to crop-end exclusive, excluding subsequent removal/preparation days. Endpoint coefficients belong to stage boundaries. **OPEN:** local lengths, coefficients and this daily discretization need approval before crop-specific claims; no default stage lengths are invented.

**REQUIREMENT:** enable a crop-specific comparison only with traceable assumptions and applicability labels; otherwise show ET0 or explicitly exploratory sensitivity scenarios. Averaged berseem cutting supports seasonal approximation, not the exact marginal demand of another cut. Equivalent ET volume is not irrigation withdrawal: 1 mm over 1 ha equals 10 m³. Do not infer irrigation delivery, yield, savings or profitable choice from lower ETc.

## 5. Season Replay and sequence indicators

**PROPOSED:** replay each complete candidate over identical consecutive historical calendar-year blocks, with the same point, area, horizon and completeness rules. Preserve winter-to-summer continuity; do not cherry-pick separate favourable years for each season. Calendar mapping, leap days and stage assumptions must match across candidates.

**PROPOSED mapping:** preserve sowing month/day and relative year offsets, then recompute crop endpoints using the approved profile. Exclude an anchor block for **all** candidates when an explicit date such as 29 February cannot be represented; report that exclusion rather than silently shifting a commitment. Otherwise include intervening leap days in actual elapsed durations. Rerun feasibility after mapping, using the same included block set for every comparison. This is an untested, reproducible convention, not a validated phenology model.

Compare each candidate A with baseline B **within each block y**: \(d_y=M_y(A)-M_y(B)\). Summarize paired differences, spread and reversals, alongside duration and grain/forage commitments. Report in-crop demand separately from crop-free intervals; an empty field cannot earn an unexplained water-saving advantage. Tmax exposure indicators need sourced thresholds before receiving crop-risk labels.

If the current plan is rejected or needs review, retain it visibly as the farmer's reference, with its conflicts. Its hypothetical weather diagnostics must not be labelled a feasible rotation or used to claim savings against an achievable baseline.

**REQUIREMENT:** retain a calendar-only comparator using the same feasibility rules. For the small usefulness check, hold the confirmed inputs and candidate plans fixed; compare calendar-only explanations with added paired weather evidence. Record whether the added evidence identifies a trade-off and whether the user can explain it; no ranking reversal is required. This exploratory check is neither held-out forecast validation nor proof of farm benefit. Historical replay is not a four-season forecast.

**REQUIREMENT:** report sourced legume presence, crop-family repetition, rooting characteristics and crop-free duration as planning indicators. **PROPOSED definitions:** count distinct known families and adjacent same-family transitions; show legume seasons and sourced root descriptors; measure crop-free gaps from crop-end to next sowing. Unknown families/roots remain unknown, and a crop-free gap is not measured bare ground. These indicators do not quantify nitrogen retained, disease suppression or soil-health improvement. Short-term trained outlooks cannot create agronomic eligibility; their separate usefulness gate remains open.

## 6. Scientific acceptance gates

**OPEN:** establish field-specific applicability within the approved Sakha research locality, sorghum eligibility, cultivar-specific stage/release assumptions, multicut schedules, catalogue family/rooting sources and feasible distinct repairs. Before claiming validation, test protected commitments, impossible repairs, unknown inputs, year boundaries and comparator symmetry. Recheck equations after changes, preserve source/unit provenance, and conduct stage/humidity sensitivity analysis. A successful calculation establishes numerical consistency; local agronomy, farmer comprehension and beneficial outcomes require separate evidence.

**12 November checkpoint boundary:** [reviewable regeneration source and instructions](reproducing.md) preserve the audited method and frozen hashes. Exact raw inputs remain local-only; public end-to-end reproduction is incomplete. The station comparison, complete crop profiles, ETc applicability and real feasible UH-001 repair remain unresolved. P0 rejected; R1/R2 needs_review; zero validated alternatives. A [separate multi-grid ML proposal](../ml/multigrid-proposal.md) changes none of these conclusions.
