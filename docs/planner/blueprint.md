# Climate-aware rotation planner: implementation blueprint

Ownership confirmed by Amr, 2026-11-13: [team roster](../team.md) supersedes older assignments. This update changes ownership only; shared API approval remains pending.

**Read this if…** you're building the planner, replay or baselines, or need the `meg_core` package layout (§9.1).

Status: Proposed ; D01–D10 await Amr's approval (status Q5) · Owner: Amr / Amr + Astra. Last reviewed .

 finalization — **PROPOSED FOR AMR'S REVIEW. No implementation authorization.** Scientific audit dated 12 November is retained unchanged.

**13 November deadline handoff:** the subsequent [final execution package](../ml/plan.md) selects Refaat's reproduced daily D+1…D+7 climatology protocol and one conditional 14-model daily Ridge experiment for the deadline, superseding this document's weekly experiment as the immediate work plan. Weekly/Chronos/C3S work remains deferred research. Standalone core interfaces and agricultural safeguards below remain the integration baseline; Amr/Astra retain the sole planner workstream. Follow the latest user authorization for implementation, not this historical approval heading.

This package comprises this blueprint, [machine-readable knowledge draft](agronomy-kb.v0.1.json), [Astra handoff](frontend-handoff.md), and [audit record](audit.json). Existing approved specifications remain authoritative until the decisions below are accepted. The user's current instruction establishes Fieldlight Hybrid with botanical arched season cards as the visual direction and assigns Mahmoud climate analysis; older status/ownership wording is superseded only on those points.

## 1. Recommended architecture and actual starting point

Build **one catalogue-driven deterministic planner, Amr + Astra's Promise Test, and an independent historical POWER replay engine**, within Yahya's approved FastAPI/Pydantic/SQLite architecture. Keep React presentation and generated TypeScript contracts; preserve Fieldlight Hybrid. Use verified frozen weather bytes. Generate schedules from versioned crop evidence and confirmed permissions, never scenario-ID branches. Return unresolved candidates as `needs_review`, not recommendations. A farmer can save a review draft even when no feasible option exists.

The smallest defensible model set is seasonal climatology plus persistence as research comparators, with **one bounded direct Ridge regression experiment** after P0 integration. LightGBM is an optional challenger, not a dependency of the demo. Preserve and report the existing trained Chronos-2 LoRA experiment; optionally evaluate its pinned base model on the new target protocol. Do not repeat fine-tuning to satisfy an ML slogan. C3S and AquaCrop are separate future research. None may influence hard feasibility.

### What was inspected

Inspected AGENTS, README, PRODUCT, SCIENCE, DATA_SPEC, ML_EXPERIMENT, ML_MULTIGRID_PROPOSAL, ARCHITECTURE, API_CONTRACTS (including overriding §0), BACKEND_DESIGN, REFERENCE_SCENARIO, PLANNER_SPEC, AGRONOMY_EVIDENCE, EVIDENCE_ACCESS, HANDOFF, PROJECT_STATUS, DESIGN, reproduction documents, validation scripts/manifests, folder inventory and available Git refs. Current HEAD is `aa7f9a2`; main and the locally cached `origin/docs/backend-design` contain placeholder application folders, not an executable backend/frontend/ML pipeline. Existing scientific Python checks and standalone HTML wireframes are real code. No pyproject/package manifest or app startup exists in this checkout. This is a statement about inspected files, not Yahya's unseen work.

Amr clarified on 13 November that Yahya's deliverables are backend documentation and architecture, not implemented backend code. BACKEND_DESIGN, ARCHITECTURE and API_CONTRACTS are available and govern later integration. **Standalone planner/climate/ML implementation does not wait for a backend.** `docs/CLIMATE_AWARE_PLANNER.md` remains unavailable in the inspected checkout and cached branch tree; no fetch/merge was performed. Its exact seven facts and complete SB-001 plans cannot be verified. Only that proposal's crosswalk and complete SB-001 acceptance case remain pending; they do not block implementing the general engine.

### Decisions requiring approval

| ID | Existing contract / conflict | Recommended explicit decision |
|---|---|---|
| D01 | PRODUCT FR-02 expects an entered plan; discrete exploration expects farmer-chosen values | Add a goal-driven preparation step that derives finite choices from the KB, presents the allowed exploration scope for confirmation, then uses the same Promise Test. Do not require manual selection of every date. |
| D02 | API crop IDs enumerate four crops | Make crop IDs catalogue-resolved strings; keep purpose/status enums. Unknown IDs still fail validation. Add a fifth synthetic crop only in extensibility tests. Coordinate generated client change. |
| D03 | PLANNER_SPEC requires a concrete supported calendar for feasibility | Exact trial templates are sufficient for **review generation and historical exposure**, not transferable feasible advice. Future variable windows need separately validated endpoint mappings. No implicit duration. |
| D04 | BACKEND_DESIGN suggests regenerated runtime CSV and different columns | Release the original archived CSV bytes, with a typed in-memory adapter and sidecar QC/provenance. Keep exact scientific tests unchanged. The runtime loader accepts `rh_percent`, not a silently rewritten `rh_pct` CSV. |
| D05 | SCIENCE replay proposes applicable endpoint recalculation | Preserve that route for supported plans; explicitly add `hypothetical_review` fixed-calendar replay for review cases. Map declared endpoints without presenting that mapping as phenology. Missing endpoints cannot receive whole-plan metrics. |
| D06 | Existing forecast contract is daily D+1…D+7; requested experiment is weekly W1…W4 | Keep v1 daily API unchanged. Store weekly results in research artifacts. Any future weekly bundle/endpoint needs its own discriminated schema and approved migration; never squeeze weekly means into daily records. |
| D07 | PRODUCT FR-06 requires an improved trained contribution; HANDOFF retains Chronos/LoRA | Preserve historical training evidence and the unmet usefulness requirement. Make new training conditional research; explicitly waive new training as a hackathon acceptance condition if approved. No claim that the old requirement was fulfilled. |
| D08 | Older API sections reserve `/replays`; BACKEND_DESIGN uses scenario-scoped paths | Follow API §0 and BACKEND_DESIGN §5: `/scenarios/{id}/replay` and `/scenarios/{id}/evidence-cards`. Reconcile examples and `parameters` versus `params` before schema generation; recommend wire `parameters`, TTS request `params`, internal canonical parameter object. |
| D09 | User requests Nov 13–14 execution; status records unresolved event start gate | Use the schedule below as staffing blocks conditional on authorized event timing. Confirm event rules before application work; this planning task does not certify eligibility. |
| D10 | Backend work is documentation; CLIMATE_AWARE_PLANNER is unavailable | Implement standalone packages using §9.1 now after blueprint approval; integrate through existing documented APIs later. Defer only the missing proposal crosswalk and full SB-001 case. |

No OR-Tools: four slots, finite evidence-backed choices and a 256-tuple cap do not justify another dependency or solver semantics. Consider CP-SAT only after measured search truncation prevents useful coverage, with multi-field/resource constraints and a documented constraint encoding. A solver cannot manufacture missing agronomy.

## 2. Final model decision table

Complexity estimates concern isolated component work after data/contracts are ready; integration is scheduled separately.

| Component | Exact model/algorithm | Purpose | Inputs | Outputs | Required datasets | Must train/fine-tune? | Evaluation protocol | Complexity | Owner | MVP / Optional / Research | Acceptance criteria | Fallback behavior |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Candidate generation | Lazy ordered finite enumeration, max 256 raw alternatives | Derive reviewable four-season schedules | Confirmed goals, scope, locks, typed templates | Candidates, changes, search coverage | KB + farmer facts | No | Non-fixture generation, cap, determinism, permission tests | Medium, 5–7 h | Amr + Astra | MVP | No fixture branching, no invented endpoints, extensible IDs | Empty/incomplete result with exact gaps |
| Promise Test | Existing registry and three-valued rule reduction | Enforce commitments/calendar/applicability | Candidate, snapshot, required-topic registry | rejected / needs_review / feasible | KB rules + confirmed facts | No | UH-001; negative and synthetic positive cases | Medium, 5–7 h | Amr + Astra | MVP | Hard fail wins; every mandatory topic covered | Unknown prevents feasibility |
| Historical evaluator | Paired calendar-block replay | Describe exposure | Schedule intervals + same historical blocks | Tmax, ET0, duration, paired distributions | Frozen 2001–2025 CSV | No | Hand arithmetic, missing/leap policies, symmetric pairing | Medium, 5–6 h | Mahmoud | MVP | Identical anchors and units; no water-saving inference | Partial/unavailable with excluded blocks |
| Climatology | Circular ±15-day seasonal distribution; weekly analog means | Strong seasonal comparator | Only training observations available by cutoff | Daily or weekly point/empirical quantiles | Frozen real Tmax/ET0 | Estimate reference distribution; no ML training | Rolling-origin protocol below | Low, 2 h | Amr | MVP research baseline | No future labels; exact date semantics | Unavailable if insufficient support |
| Persistence | Last observed value; last 7-day mean secondary | Detect whether history adds value | Cutoff history | Constant future weekly means | Same data | No | Identical issue dates/horizons | Low, <1 h | Amr | MVP research comparator | Same information boundary | Unavailable on missing context |
| Supervised baseline | Standardized direct Ridge, 8 target/horizon models | Test predictable anomaly beyond seasonality | Lag/rolling/calendar features | W1–W4 mean Tmax/ET0 | Same data + split manifest | Yes, conditional one bounded experiment | Purged expanding validation; future locked assessment | Low, 3–4 h | Amr + Refaat | Optional P1 | Reproducible training and honest comparison, not required win | Climatology; retain losing result |
| Tree challenger | CPU LightGBM regression_l1, 8 models | Test limited nonlinear gain | Identical features/labels | Same weekly targets | Same data | Yes, only after Ridge/P0 | Four fixed configurations, same folds | Medium, 2–3 h extra | Amr | Optional P2 | Predeclared skill gate, no extra data leakage | Stop; no runtime dependency |
| Foundation model | Pinned amazon/chronos-2, zero-shot weekly series | Compare pretrained forecast | Past complete weekly Tmax/ET0 | Same four weekly targets, quantiles | Archived checkpoint + weekly series | No; pretrained weights already local | Same origins/cutoffs; pretraining-overlap caveat | Medium, 2–3 h | Amr | Optional P2 | Fits resource budget; no selective scoring | Skip on OOM/time/failure |
| Existing LoRA | Archived adaptation200 | Preserve actual trained evidence | Original 60-day daily setup | Original saved daily assessment | Archive adapters, predictions/protocol | Already trained; no new fit | Saved-artifact reproduction; consumed assessment | Low audit | Refaat | MVP evidence, optional inference | Retain negative finding | Report artifact results only |
| New LoRA | Rank 8/alpha 16, ≤200 updates | Research adaptation to new protocol | Newly registered training examples | New versioned adapter | Real chronological weekly data | Yes, future gate only | Reload/update/resource proof + fresh test | High relative to deadline | Amr | Research | Requires separate justified protocol and budget | Abandon hackathon run |
| Seasonal outlook | C3S equal-system ensemble, cross-validated bias adjustment | Monthly mean anomaly context | Forecast members and matching hindcasts | Monthly anomalies/tercile probabilities | C3S + independent monthly verification | No foundation training; fit correction/calibration | Held-out-year hindcast skill by lead/month | High, >1 day | Mahmoud | Research P2 | Local positive skill with uncertainty | `regional_skill_not_demonstrated` |
| Crop response | FAO AquaCrop calibrated by crop/site | Future stress/yield/water research | Soil, crop, management, weather | Validated simulations only | Field calibration/validation data | Calibration required | Independent seasons/fields; stress and yield observations | Multiweek research | Refaat + agronomist | Research | Required inputs and external validation | ETc/yield/irrigation/productivity unavailable |

Abandon for this build: multi-month daily weather promises, duplicated-grid training, new deep architectures, AutoML sweeps, ML suitability scores, generic soil scores and any synthetic crop-outcome labels. No model currently demonstrates better farmer decisions.

## 3. Real-data audit and acquisition inventory

The read-only `audit_saved_evidence.py` passed on Python 3.13.5 in this session: 16 member integrity checks, 9,435 days, 75,480 original values, maximum independent ET0 difference 0.0 mm/day, saved model/baseline metrics reproduced. Both CSV byte hashes and archive hash match. This does not rerun training, verify all weight tensors, reconstruct all bootstrap intervals, or validate field weather accuracy. The user's Linux 14/16 result and ≤3.6e-15 differences remain separate evidence; no test was relaxed.

Archive: `d284b3162a2dd5bbde8bcb37ae3090adcf080a5d044a4e25b2c96836b4cee95f`, 468,781,522 bytes. Prefix below is `work/validation_/` inside the ZIP.

| Dataset / official source and URL | Coverage / resolution / variables and units | Availability, cleaning, derived features | Provenance / licensing / owner / consumers |
|---|---|---|---|
| [NASA POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/); exact requests in `data/validation/power_acquisition.json` | 31.10 N, 30.95 E; returned elevation 4.96 m; daily LST, 2001–2025 and Jan–Oct 2026. Native products differ in resolution; not parcel measurements. Tmax/Tmin/dewpoint °C, RH %, WS2M m/s, solar MJ/m²/day, pressure kPa, rain mm/day | Available raw JSON in ZIP: `power_sakha_2001_2025_LST.json`, `power_sakha_2026_Jan_Oct_LST.json`. Validate dates/units/fill -999/physics; no interpolation. Meteorological versus solar native cell identity still unresolved for multigrid | Request, UTC retrieval, actual source lists and hashes preserved. NASA attribution and source terms captured before redistribution. Refaat; ET0/replay/ML |
| Frozen `weather_et0.csv` | 9,131 daily rows, –; above fields + ET0 mm/day and two sensitivity columns | Available; SHA256 `17141df82f6300c051257c21fb9ac3d9f5f1627fd32cbc8c07bc9296c477bde8`. Copy bytes, do not regenerate for runtime. Sensitivities are not independent targets | Derived FAO56 + ASCE bound, source/generator hashes; original bytes and notices preserved. Refaat; replay, ML |
| Frozen `weather_et0_2026_Jan_Oct.csv` | 304 daily rows, –10-31 | Available; SHA256 `c4d5929fd0d4d55c416ee45d5ebd21502142994afbc76b00c6f20e1b349ee36e`. Development/consumed assessment only; incomplete year excluded from default replay | Additional GEOSIT/FLASHFLUX listed by source; no invented per-day transition. Refaat; diagnostic ML |
| ARC/FAO/Egyptian journal crop sources | W1–W3, B1–B2, M1–M4, S1–S2 in [AGRONOMY_EVIDENCE](agronomy-evidence.md); exact URLs/locators also in KB draft | Published windows, trial calendars, cultivars, maturity ranges. Available as source ledger; several PDFs inaccessible in this session. Required reacquisition and double transcription before runtime activation | Observation is distinct from recommendation and transfer assumption. Article access is not redistribution permission. Refaat; KB, planner |
| Current local operational crop calendars | Target-year seed availability, harvest criterion, removal, preparation, cultivar-dependent endpoints | Missing for complete transferable four-season plans. Obtain dated extension/agronomist evidence and confirmed operational facts; no universal duration fill | Named scope, reviewer, source/date and methods required. Refaat/Amr + Astra; feasibility |
| Actual field and farmer facts | Texture; EC dS/m with extraction/depth/date; pH method; drainage/water table; irrigation restrictions; crop purpose/quantity/locks | Missing until intake or measurements. Trial soil stays a research profile. No imputed soil, irrigation or biomass | Farmer reports/measurements separate from science status. Local controlled storage; no real records on unauthenticated public demo. Amr/Yahya; planner |
| Saved ML artifacts | Base checkpoint, LoRA adapters, installed requirements, evaluation protocol, NPZ predictions, results | Present inside ZIP; saved scores reproduced, no weights loaded. Training 2001–18, diagnostic 2019–21, consumed Jul–Oct 2026. Freeze new split manifest | Pin revision `29ec3766d36d6f73f0696f85560a422f50e8498c`; Apache-2.0 notices per recorded model/library. Amr/Refaat; research |
| [C3S monthly seasonal forecasts/hindcasts](https://cds.climate.copernicus.eu/datasets/seasonal-monthly-single-levels?tab=overview) | Global 1° grid, monthly; catalogue hindcasts 1993–2016, forecasts 2017 onward; actual system coverage must be checked. 2m mean temperature K; precipitation rate m/s | Not acquired; optional. Convert K→°C, rate→monthly mm using exact seconds only after checking product metadata. Store every system/version/member/init/lead | CDS licences, including additional non-European contribution terms; authenticated acquisition approval if needed. Mahmoud; optional outlook |
| [ERA5 monthly single levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=overview) or quality-controlled station mean temperature | Same target month and variable as C3S; never use Tmax as monthly mean temperature truth | Pending optional verification dataset. Evaluate reanalysis dependence; station data preferable if accessible and QC documented | Separate source/hash/grid/units and CDS terms. Mahmoud; C3S verification |
| AquaCrop calibration/validation | Crop cultivar phenology, canopy, rooting, harvest index, stress response; layered soil hydraulic properties; salinity and water quality; initial water; irrigation dates/depths/efficiency; fertility/weeds/mulch; weather/CO2; observed yield, biomass, canopy and soil water | Missing. Weather alone is insufficient. See [FAO input requirements](https://www.fao.org/aquacrop/overview/input-requirements/en/) and [crop response manual](https://www.fao.org/4/i2800e/i2800e.pdf) | Version/model terms and site calibration records; independent validation seasons. Refaat plus agronomic collaborator; future only |

### Data-to-decision pipeline and concrete loaders

All paths below are intended modules after approval, not claims that implementations exist. **The standalone package mapping in §9.1 supersedes backend-hosted computational paths below and in the roadmap.** Backend paths remain thin integration adapters; the algorithms are implemented once in the independent packages.

1. `data/validation/release_weather.py` (Refaat) reads **allowlisted ZIP members**, verifies archive and member hashes against committed manifests, then copies frozen CSV bytes to a new `data/release/weather/` directory. Reject overwrite, traversal, unexpected members and changed inputs. No bulk extraction or weight release. Keep raw inputs local; decide small-source distribution separately.
2. `backend/app/core/appdata.py` loads `manifest.json`, `catalogue/{crops,rules,sources,templates}.json`, messages and weather once. Validate all hashes, IDs, units, mandatory topic coverage and both languages before marking the release ready. The archived CSV has `rh_percent` and sensitivity columns, no `qc`; an adapter supplies normalized typed rows and validated QC sidecar metadata without changing source bytes.
3. `backend/app/planner/catalogue.py` indexes `crop_id`, purpose, cultivar, locality/land class, template observed dates, transfer permission, source refs, eligibility gates and rule IDs. `planner/generate.py` consumes only those fields plus farmer horizon, permissions, locks and goals. It never consumes weather as eligibility evidence.
4. `planner/{dates,registry,evaluate,status,promise_test}.py` consumes candidate `s,h,e,r,p`, required evidence topics, field measurements and commitments. Output codes identify source rule and missing paths. Crop ID is data, not a four-value switch.
5. `replay/{mapping,metrics}.py` consumes immutable plan intervals and `date,tmax_c,et0_mm_day` plus QC, source and method metadata. Optional weather context uses rain/Tmin only with named metrics. Output is per-block exposure and paired differences; ET0 never becomes a crop-response target.
6. `ml/data.py` loads the **same verified frozen files**, exposes only permitted history at each issue cutoff, and generates labels from observed future rows for training/evaluation only. `ml/{features,splits,baselines,train_ridge,evaluate}.py` consumes Tmax/ET0 histories initially; derived ET0 is not an independent ground-truth measurement. Other six predictors are optional later ablations, with availability manifests.
7. `ml/experiments/weekly_v1/` contains protocol, split/origin manifest and result metadata; large predictions/models remain ignored under `ml/artifacts/`. `forecast/bundle.py` validates the unchanged daily bundle. Weekly experiments are never automatically published to it.
8. `services/evidence_service.py` joins exact snapshot/result refs, release hash, selected template evidence, rule outcomes, replay exclusions and optional forecast status into a saved card. `frontend/src/services/api.ts` consumes generated types; components render server facts and wording, without reimplementing scientific calculations.

The runtime release manifest binds file bytes plus loader, mapping, metric and rule-code versions (or code hashes). A single public `data_release` remains the approved version handle; internal method identities remain auditable. Any algorithm-affecting change requires a new release. Cache keys include release and method identity, never only a calendar name.

## 4. Agricultural KB and evidence gaps

`docs/planner/agronomy-kb.v0.1.json` is a **versioned machine-readable planning artifact**, not an approved runtime catalogue. It transcribes the existing ledger into sourced assertions and typed trial templates; no fixture is used as agronomic evidence. Each assertion carries units, evidence status, origin, applicability, source locator, review state and permitted use. Source hashes unavailable in the ledger remain null with reasons. A source statement's historical `verified` label does not approve transfer or activation. Refaat must double-check source extraction; Amr + Astra must approve rule effect; Yahya validates schema before promoting it into D8's runtime release.

Runtime schema: `Crop{id,names,purposes,profiles[]}`; `Profile{id,crop_id,purpose,cultivar,scope,assertion_ids,template_ids,required_topics}`; `Template{id,source_refs,observed_calendar,endpoint_semantics,transfer_policy,unknowns}`; `Rule{id,version,effect,required_for,applicability,assertion_ids,explanation_code}`. Use the existing `Fact` and `SourceRef` semantics; nulls require reasons. Conditions reference registered Python functions, never executable JSON expressions.

Evidence classes remain distinct: NASA source product, scientifically derived ET0/date subtraction, reported trial observation, farmer report/measurement, proposed year transfer, and illustrative fixture. A farmer can confirm an assumption without scientifically validating it.

### Template selection and variable windows

Select by purpose → locality/land class → cultivar/type → available evidence and requested season → explicit farmer permission. Known incompatibility excludes a template; missing applicability produces a review gate. For a trial-calendar investigation, transplant month/day and relative year offsets only when the farmer accepts that **hypothetical calendar basis**. Store original trial dates and the separate target-year assumption. Do not turn a trial's elapsed days into a generic duration function.

Sakha maize SC10 15 May–20 September is a real **2016 trial calendar** in W3; the trial is saline and managed, not general validation of non-saline/unknown fields. Hybrid-888 sorghum 15 June–20 September is a real **2012 trial calendar** in S1 after barley, not proof for a wheat predecessor. These can drive exploratory calendar candidates in the pilot with explicit applicability unknowns. They do not justify a continuous sowing interval or feasible rotation.

The ledger also provides two distinct berseem trial years, another sorghum date, wheat observations, and late-maize observations. Use all reviewed records compatible with scope, not only SB-001. For a new date inside an advisory window, lack of endpoint support leaves dates unknown/uninstantiated; May preference does not supply a harvest date. Future variable windows require a validated cultivar/date/management mapping, explicit uncertainty and supported concrete release/preparation evidence; evaluate bounds conservatively and retain unknowns if overlap cannot be decided. A maturity range, GDD model or AquaCrop default is not that mapping.

### Gap register

The following seven groups are this blueprint's register, **not a claimed transcription of the missing Yahya proposal**. Crosswalk its exact seven items when supplied.

| Gap | Missing evidence | Blocks | Owner / closure criterion |
|---|---|---|---|
| G1 | Target-year cultivar identity, local suitability and seed availability | Feasible maize/wheat/sorghum selection | Refaat; applicable dated source plus farmer seed confirmation |
| G2 | Sowing-dependent harvest/final cut and crop-end mapping, including berseem regrowth | Concrete transferable crop calendar; full replay when endpoints null | Refaat/Amr + Astra; scoped source or documented operational plan, no arbitrary duration |
| G3 | Removal, access/workability and first free field date | Occupancy pass | Farmer + agronomist; confirmed applicable operational basis |
| G4 | Transition-specific preparation days/operations for all three transitions | Next sowing pass | Amr + Astra; evidence applies to predecessor, equipment and soil condition |
| G5 | Field salinity method/depth, drainage, water table and relevant soil suitability | Field applicability | Refaat; compatible field data or explicitly unresolved gate |
| G6 | Irrigation access/timing/restrictions and cultivar management applicability | Supported operational feasibility | Farmer/Refaat; evidence of constraints, not assumed unlimited supply |
| G7 | Complete four-season intentions, predecessor/successor applicability, hard production quantities | Complete SB-001, succession coverage, feed/grain quantity promises | Amr/Amr + Astra; all slots supplied; source-supported checks. Crop presence never proves quantity |

Additional optional gaps: Kc/stage inputs block ETc; crop-specific heat-response calibration blocks heat-risk/yield labels; prospective weather vintages and fresh outcomes block operational ML claims; C3S hindcasts/verification block outlook skill. No generic hard rotation prohibition, nitrogen credit or soil improvement magnitude is established by the inspected ledger.

## 5. Exact planner algorithm

Goal entry adds a proposed `POST /api/v1/planning-scopes` preview endpoint: receive unconfirmed field/horizon/goals/allowed crops and protected facts, return missing inputs plus finite source-labelled choices. No state change or approval. After a full readback, materialize exactly four `SeasonInput` records (unknown facts allowed) and existing `ExplorationChoice` records; confirm through `POST /scenarios`. Persist the selected scope and its release with the snapshot. New choices derived from a changed release require renewed confirmation. If this endpoint is deferred, a server catalogue-driven scope builder may be called by scenario creation only with an explicitly confirmed scope; never infer permission from an omitted field.

```text
prepare_scope(draft, release):
  normalize catalogue aliases, canonical dates, units; never guess ambiguous dates
  validate one field, four ordered season slots, horizon, goals, lock shapes
  identify missing critical facts; retain null + reason
  select compatible KB profiles/templates within user-authorized crops/purposes
  derive finite crop/profile/date choices; label trial-year transfers as proposed
  return choices + source refs + missing facts for explicit scope confirmation

promise_test(confirmed_snapshot, immutable_catalogue):
  validate confirmation, release, identifiers, field and protected commitments
  evaluate current plan against every mandatory planning topic
  scope = canonical confirmed discrete choices; never alter protected values
  seen = {}; evaluated = []; uninstantiated = []; raw_count = 0
  for tuple in lazy_minimal_edit_order(scope):
    if raw_count == 256: mark incomplete(candidate_budget); break
    raw_count += 1                  # duplicates/invalid combinations count too
    bind compatible crop/profile/template jointly
    if proven incompatible: record bounded exclusion reason; continue
    if no date/profile can be instantiated: record evidence gap; continue
    recompute supported dependent h/e/r/p; invalidate all unsupported old endpoints
    keep independent downstream farmer intentions; never silently shift them
    key = canonical facts + evidence semantics + release + input revision
    if exact duplicate: merge choice provenance; continue
    checks = Amr + Astra.evaluate_all(plan, snapshot, catalogue)
    # all seasons, 3 transitions, every earlier known occupation bound
    status = rejected if applicable hard fail else
             needs_review if mandatory topic missing/unknown else feasible
    retain checks even after first failure; store stable candidate hash
  rank within status partitions using explainable lexicographic changes
  choose <=2 materially distinct feasible alternatives
  retain bounded review/rejected investigations and exact search coverage
  return PlanningResult; no climate or ML call in this pure function

service_compare(snapshot_ref, candidate_refs, requested_metric):
  load immutable current refs; reject stale/mismatched release with 409
  assign comparison_basis: checked_constraints or hypothetical_review
  map all complete requested intervals to the same eligible historical blocks
  compute exposure and paired differences; preserve status and gaps
  attach optional dated forecast status separately; never change eligibility
  save evidence card only on explicit request, as review_draft unless eligible
```

Normalize known malformed same-season dates to 422; valid but conflicting cross-season dates return a 200 planning result. Lack of confirmed exploration permission means no generation. A lock remains intact even when its coexistence with another season is impossible. Incomplete input may produce a review draft or an empty search; never invent remaining seasons as real facts.

Use PLANNER_SPEC's interval convention: `s <= h < e <= r`, crop `[s,e)`, occupancy `[s,r)`, preparation `[r,r+p)`, next sowing `>=r+p`. Unknown p is not zero; a proven bound can establish failure but not pass. Half-open crop-end derivation `h+1` requires an explicit last-crop-day interpretation; it does not establish release.

Ordering: hard-status partitions first; minimal-change default is edited slots, direct decisions, unknown displacement count, total absolute known sow-date shift, canonical key. No crop-substitution penalty hidden in a weighted score. Review candidates receive the same transparent edit order within their own list. User-selected climate sorting is an explicit **within-status, comparable-basis** view; undefined metrics sort last, report exclusions, never promote `needs_review`. Do not call lower ET0 “better” without the user selecting the descriptive metric. Show duration/requirements alongside it.

Bounds: retain the existing proposed 256 raw alternative budget, max 32 values per individual choice and 32 choice records, max 64 KiB request (engineering defaults for approval). Search completeness refers only to confirmed finite scope. `evaluated_count` excludes current plan, duplicates and uninstantiated branches. Enumerate minimal edited-slot layers before lexicographic values; do not sample randomly. Return at most 256 materialized candidates; UI initially expands 2 feasible and 5 review rows with remaining rows accessible. Payload limit failures are explicit, not silent drops.

Let C be four slots, B=256, R mandatory rule checks, K returned plans, Y eligible historical blocks, L crop days per plan. Lazy enumeration costs O(B(C+R+C²)) plus O(K log K) ordering, space O(K(C+R)) for retained explanations. Prefix sums for Tmax, ET0 and threshold counts cost O(T) weather preprocessing; interval maxima can initially scan L. Replay O(KYL) worst case and O(KY) result memory; at this dataset size no queue/solver is needed. Cache parsed weather once and use a bounded 256-entry replay LRU keyed by release, exact canonical intervals, mapping/basis/cutoffs, paired plan set and anchor selection. Cache locale-independent numbers only. Benchmark 256-tuple requests on the demo laptop, proposed target <2 seconds excluding cold startup; failure is explicit, never falsely complete. Do not use time limits to choose different winners.

## 6. Historical climate method

Historical analysis is a replay of gridded source products, **not future prediction or field measurement**. Default data window is complete 2001–2025; Jan–Oct 2026 is excluded from this default rather than mixed into incomplete annual blocks.

Anchor the earliest calendar year of the plan to y; preserve every date's month/day and relative year offset across all four seasons. A winter 2026 to autumn 2028 plan needs three calendar years; eligible default anchors are 2001–2023, subject to coverage and leap policy. Do not claim 25 full four-season samples. Pair all candidates on the intersection of eligible blocks. Explicit Feb 29 mapped to a non-leap year excludes the block for everyone; otherwise intervening leap days count. For applicable endpoint models recompute and re-evaluate mapped calendars. For a hypothetical calendar, map declared endpoints and locks, rerun calendar checks, and retain unresolved agronomy rather than claiming historical feasibility.

Crop interval is `[s,e)`, not removal/preparation. If only an inclusive harvest date is supplied, an explicit `harvest_is_last_crop_day` hypothetical assumption permits `e=h+1` for descriptive analysis only. If that assumption is absent, period metrics are unavailable. Separately expose specified date-interval analysis without calling it a complete rotation. Never use a null release as crop end.

For each plan/block/season report: scheduled days N, valid Tmax and ET0 counts, coverage fractions; mean Tmax (°C), maximum daily Tmax (°C); counts of Tmax **>=35°C** and **>=40°C** and percentages of N (descriptive cutoffs only); mean ET0 (mm/day) and sum ET0 (mm). Whole-plan totals sum disjoint crop periods only; an overlapping rejected plan must not double-count a day into a purported whole-field total. Show crop-free days separately, without crediting them as water savings.

Require 100% valid coverage for each requested metric's interval. For paired comparisons, exclude a block from that metric for **both/all** plans if any plan lacks a required day. For a joint multi-metric view use the intersection across required metrics; don't compare means drawn from different year sets. Partial availability names the affected metrics and exact missing dates. No zero-fill, interpolation, or shortened denominator hidden from users.

Within each block calculate candidate minus baseline. Report n, each plan's median/mean, year-to-year SD and min/max, paired mean/median differences, and counts of negative/zero/positive differences. Historical percentiles describe the sample, not calibrated probabilities for 2027. Do not attach significance claims from overlapping multi-year blocks without a dependence-aware analysis. Cache exact values; round only presentation (e.g. Tmax 1 decimal, ET0 mean 2, sum 1), never compare rounded values.

For SB-001, if 20 September is explicitly treated as last included crop day, maize May 15–Sep 20 covers **129 days**, sorghum June 15–Sep 20 **98 days**: a 31-day exposure difference. Exclusive date subtraction is 128/97 days; explain the endpoint convention. Show ET0 total **and** mm/day, temperature mean/max, counts **and** percent of days. The shorter period may mechanically lower total ET0; it does not show lower irrigation requirements, yield loss or water productivity. Optional common-date June 15–Sep 20 diagnostics separate calendar duration effects, but are not whole-crop comparisons. Numerical weather totals must be generated by the future engine; none is invented here.

`hypothetical_review` labels every comparison involving review candidates; a rejected reference additionally retains its conflict and a `hypothetical_rejected_reference` reason. No weather metric changes its status. ETc, yield, irrigation demand, productivity and crop-stage heat risk return null/unavailable with required-data reasons.

## 7. Forecast experiment protocol

### Baselines and issue-time discipline

Preserve the old experiment and its exact 31-day baseline implementation as immutable reproduction. The following is a **new named protocol**, not a retroactive change to the reported scores.

Define issue D on a fixed weekly sequence (Monday LST date); common historical cutoff C=D−7. W1 target days D+1…D+7; W2 D+8…14; W3 D+15…21; W4 D+22…28. Weekly labels are arithmetic means of all seven observed Tmax values (°C) and ET0 rates (mm/day), **not weekly maximum Tmax or total ET0**. No missing target day is allowed. All comparators use identical origin/target validity masks. Revised POWER history provides retrospective pseudo-real-time evaluation; actual operational vintages are absent.

Calendar baseline: exclude Feb 29 from the reference pool; assign month/day to a 365-day calendar. For a daily target j, take only eligible training observations with circular calendar distance <=15 days. Point mean is the sample arithmetic mean; empirical quantiles use sorted linear interpolation at index (n−1)q. Predict Feb 29 from an explicitly labelled 50:50 mixture of Feb 28 and Mar 1 reference pools. Require >=10 distinct eligible years and >=200 valid daily samples for daily output; otherwise unavailable. These thresholds are proposed engineering support gates, not universal statistical guarantees.

Weekly baseline: for each historical training year and target week, construct 31 same-season seven-day analog blocks with start shifts −15…+15 days. Keep only blocks whose **entire label period was in the permitted training observations by C**. Weight each eligible year equally, then analog starts equally within year. Require >=10 years with >=20 complete analog blocks each. Use weighted mean and empirical quantiles of weekly means. Feb-29 starts use the same explicit two-anchor mixture; preserve actual consecutive seven-day blocks. Overlapping analogs are not independent samples. Do not sum daily quantiles for weekly intervals. Daily and weekly baselines are evaluated against their corresponding targets.

Nonstationarity: primary baseline uses the expanding permitted history; predeclare one trailing-15-complete-years sensitivity comparator. Do not choose a window after final-test inspection. Report performance by season/era and bias; historical change is not handled by silently fitting future trends. A future trend-adjusted model would need a separate train-only fit and evaluation.

### What to train, exactly

Recommend direct Ridge before LightGBM: this is the simpler regularized lag/calendar comparator already proposed in ML_EXPERIMENT, with fewer tuning freedoms on about 25 annual cycles. It is a methodological preference, not evidence it will win. Standardization uses training-only means/SD; constant features map to zero. Fit eight independent models (two targets × four horizons) to weekly observed target minus the issue-specific seasonal baseline, adding that baseline back at prediction. Store each residual baseline's permitted training cutoff to prevent leakage.

Features initially use **only Tmax and ET0**: daily lags 0,1,2,3,6,13,27,55 relative to C; trailing means and population SD over 7,14,28,56 days ending C; latest 7-day mean minus preceding 7-day mean. Known calendar features: sine/cosine first and second annual harmonics at D and each target week's midpoint, plus lead-week identity in metadata (models are separate). No future measured weather, centered rolling averages, realized harvest data or 2026 outcome features. Other observed channels require separate availability/audit and a fixed ablation budget.

Use weekly training origins (about 52/year before exclusions; exact counts emitted). Baseline residual labels also require the stated ten-year reference support at each training origin, so the early years are warm-up history, not usable residual training rows; report this substantial effective-sample reduction. Require all 56 history days and seven target days; exclude incomplete origin/horizon with reasons. Do not backfill or interpolate from future data. Missing inference context gives unavailable. Training labels are real observations, never Chronos predictions. Eight Ridge models with alpha in {0.1,1,10,100}; choose one shared alpha by equal-weight mean MAE skill across eight target/horizon cells on development folds, normalized by their climatology MAE. Report raw per-cell metrics too; this research selector is not a farmer suitability score.

Optional LightGBM: same eight direct residual targets and features, CPU only; `objective=regression_l1`, learning_rate=.03, max_bin=63, lambda_l2=10, deterministic=true, force_col_wise=true, fixed threads/seed. Four configurations: num_leaves {7,15} × min_data_in_leaf {30,60}, max_depth=4, <=300 trees, early stopping 30 rounds on the current validation fold. Freeze best iteration rule and package versions. No GPU setup or dependency install unless approved. The official guidance recommends controlling leaf complexity and minimum leaf data to limit overfit; it supplies no claim of weather skill. [LightGBM tuning](https://lightgbm.readthedocs.io/en/stable/Parameters-Tuning.html), [parameters](https://lightgbm.readthedocs.io/en/stable/Parameters.html).

### Splits, metrics, promotion and stop rules

Development folds: train 2001–2015 / validate 2016–18; train 2001–2018 / validate 2019–21. Require training label endpoints <= the training boundary **and** <= the validation-origin cutoff; purge straddling origins (up to 28-day label tail). Freeze features/configuration before scoring 2022–2025 as a diagnostic backtest. Those years and Jan–Oct 2026 are **not newly untouched tests**; the foundation model's pretraining contents are not fully known. Retain consumed 2026 scores solely as historical evidence, not tuning targets or a fresh win.

For prospective evidence, register T0 after protocol/model freeze; first issue is the next Monday after T0 with complete permitted history, archive input bytes and forecasts before targets occur, and assess 12 months for seasonal coverage. A 12-origin interim feasibility check is not operational validation; do not tune against it and keep calling it untouched. Refit permitted data only on a preregistered schedule with hyperparameters fixed. At issue D every training label must be observed by C; actual channel availability may force an older cutoff and a new declared horizon bridge or unavailable status.

Report MAE, RMSE, bias by variable, lead, season and all origins; coverage/excluded counts and inference latency/resources. Forecast skill = 1 − MAE_model/MAE_baseline, using the stronger predeclared climatology/persistence comparator on identical targets (zero denominator → undefined). Confidence intervals resample paired contiguous 8-origin blocks, 2,000 replicates with fixed seed; preserve all leads/variables per origin. Small seasonal cells remain descriptive. Use raw units; no MAPE near zero ET0, pooled °C/mm errors or isolated winning dates.

Proposed research promotion gate: >=5% aggregate MAE improvement for each target, paired 95% block-bootstrap improvement interval above zero, and no lead/season degradation >5%; minimum 26 valid origins per claimed season/lead. Insufficient evidence means inconclusive, not success. These thresholds require approval before scoring. Farmer benefit additionally needs agronomically permissible near-term alternatives and a separate decision study; statistical skill alone does not satisfy it.

Ridge/LightGBM point forecasts need no invented quantiles. Optional probabilities are a separate calibration run: fit three quantile LightGBM models per target/horizon (24 total) only with new budget approval; evaluate pinball loss, 80% interval coverage and width, calibration by lead/season. Fit calibration only on earlier validation residuals, freeze before test. Chronos empirical quantiles are also uncalibrated until checked. Proposed interval gate: 75–85% empirical coverage for nominal 80%, with uncertainty and width no worse than climatology; do not claim exact confidence from that tolerance alone.

Stop after the fixed Ridge grid and, if authorized, the four LightGBM configurations. Losing or inconclusive results are final for the hackathon. No additional tuning motivated by final scores. Baseline remains the reporting default; a failed model cannot hold up planning, replay or save.

### Chronos matrix and 4 GB GPU

Preserve archived daily base-versus-LoRA scores: climatology 1.656°C / .523 mm/day; LoRA 1.988 / .640; base 2.000 / .644. Tiny LoRA gains over base did not establish useful improvement.

Optional experiment matrix: (1) weekly zero-shot pinned base with 104 complete weekly history bins; (2) same base with 52 bins only if the 104-bin memory smoke fails, recorded as resource fallback, not a performance search. Define bins relative to D: last observed bin ends C; predict five weekly steps, discard bridge C+1…D and score steps 2–5 for W1–W4. Disable cross-learning between origins; log exact target alignment. Compare to the same weekly baselines/Ridge. The existing daily LoRA adapter has a different sampling frequency/objective; **do not represent it as weekly-adapted**. Its original saved daily experiment remains evidence; daily 35-step forecasts aggregated to weekly means would be a separate optional evaluation, and averaged daily quantiles are not weekly quantiles.

No new downloads: use pinned archived weights after checksum validation. Batch one, measured free VRAM, fixed dtype, explicit eval/inference mode; cap peak allocated VRAM at 3.0 GiB and experiment wall time at 2 hours including setup. One OOM retry with shorter context is allowed; then stop. CPU fallback only if already available and within budget. The archived 60-day/14-step run used about 1.27 GB reserved memory, but this does not guarantee new-context memory. A 1,024-step API capacity is not weather predictability. [Official Chronos model card](https://huggingface.co/amazon/chronos-2).

New LoRA and multigrid are deferred: require verified distinct meteorological/solar source-cell overlap groups, group-wise spatial splits, shared temporal holdout, fresh assessment and logged parameter updates/reload checks. Crops, coordinates within the same cells and copied series never add independent sites. Retain ML_MULTIGRID_PROPOSAL as an unexecuted research proposal.

## 8. Seasonal outlook and future crop response

C3S is **off the critical path**. Start with monthly mean 2m temperature only; precipitation is secondary and must demonstrate regional skill and usefulness in this irrigated setting. The official CDS collection distinguishes monthly ensemble outlooks from detailed daily weather; neither monthly anomaly nor a warm tercile is a daily Tmax extreme or crop-stage stress estimate. [C3S dataset](https://cds.climate.copernicus.eu/datasets/seasonal-monthly-single-levels?tab=overview), [postprocessed anomalies](https://cds.climate.copernicus.eu/datasets/seasonal-postprocessed-single-levels?tab=overview).

Proposed research initialization: nominal , only runs actually published by the demo retrieval time; verify each system's true initialization and release timestamp, including lagged ensembles. Request target December 2026–February 2027 using valid-time coordinates, not assumed numeric lead labels. No claim that those files were downloaded. May 2027 is outside this chosen three-month scope.

Map Sakha to the nearest valid land grid cell on the returned grid, retain requested/returned coordinates, distance, mask and method; test bilinear sensitivity without claiming field downscaling. Use matching system/version/member/init-month/lead hindcasts, common years across included systems. Catalogue advertises 1993–2016 hindcasts; actual systems may differ, so eligibility is based on downloaded metadata. Verify against monthly mean 2m temperature from independent QC station data or clearly labelled ERA5; do not compute mean temperature as Tmax alone or silently substitute (Tmax+Tmin)/2 for verified monthly observations.

For each init-month/lead/system use leave-one-year-out additive temperature bias correction (subtract training hindcast mean, add training observation mean). Compute observation terciles from training years only, derive member probabilities, weight systems equally rather than over-weighting larger ensembles. Cross-fit any probability calibration in inner training folds; small samples argue for simple shrinkage toward climatology rather than complex quantile mapping. Assess anomaly correlation, RMSE skill, CRPS/CRPSS and tercile Brier skill/reliability against climatology, with year-block uncertainty. Register choices before evaluation. Enable a region/month/lead only with positive out-of-sample CRPSS/Brier skill and uncertainty supporting usefulness; otherwise unavailable. Precipitation needs a separate zero-aware distribution/unit treatment, not temperature's additive correction.

No C3S credentials/data or Sakha skill results exist in this checkout. Missing service, data, matching hindcasts or demonstrated skill returns a specific reason. Do not substitute a decorative outlook. A future `SeasonalOutlookProvider` accepts site/init/target-months and returns status, system versions, provenance, calibrated monthly quantities and skill; keep it separate from both daily ForecastBundle and planner rules.

AquaCrop can support a future calibrated crop-response study, not solve missing inputs now. Its weather-driven water productivity framework requires local crop, soil and management characterization and validation observations; multi-cut berseem needs explicit supported model capability and calibration. The inventory lists missing inputs. Separate calibration and external validation seasons/fields, report yield/biomass/soil-water errors and uncertainty before any stress/irrigation claim. Do not integrate AquaCrop into the hackathon. [FAO AquaCrop](https://www.fao.org/aquacrop), [FAO crop yield response](https://www.fao.org/4/i2800e/i2800e.pdf).

## 9. API, state and persistence contract

Keep Yahya's layers and three SQLite tables: scenario revisions, immutable results, evidence cards. No new database/queue/auth architecture. The unauthenticated MVP is controlled local or synthetic-only remote; it is not ready for public real-farmer records. `expected_revision` transactions and current release checks prevent stale saves. Do not reintroduce superseded idempotency/session/revocation APIs.

Preserve `Fact`, `SourceRef`, `RuleEvaluation`, `PlanEvaluation`, `Candidate`, `PlanningResult`, `ReplayResult`, `EvidenceCard` and ForecastBundle. Add typed catalogue template metadata and a required-topic coverage list; add `comparison_basis`, metric denominator, source interval and exclusion metadata to replay, after coordinated schema review. A `feasible` status means passes all documented applicable checks, not blanket agronomic safety. Farmer confirmation never upgrades evidence.

| Endpoint under `/api/v1` | Concrete responsibility |
|---|---|
| `GET /health`, `GET /catalogue?locale=` | Release readiness and validated catalogue/prompts/sources |
| `POST /planning-scopes` (proposed addition) | Read-only goal-to-finite-scope preview; no status claim or persistence |
| `POST /scenarios`, `GET /scenarios/{id}`, `POST /scenarios/{id}/revisions` | Existing confirmed snapshot flow; four slots, unknowns explicit |
| `POST /scenarios/{id}/promise-test`, `GET /results/{id}?locale=` | Stored deterministic result from server snapshot |
| `POST /scenarios/{id}/replay` | Resolve server plan refs; compute paired historical evidence |
| `POST /scenarios/{id}/evidence-cards`, `GET /evidence-cards/{id}` | Explicit draft save; approval only for feasible/current |
| `GET /forecast?action_dates=` | Existing daily bundle status, no weekly coercion |
| `POST /speech/interpret`, `/speech/tts` | Existing deterministic proposals and version-bound audio |

Proposed replay request (schematic IDs, no computed result):

```json
{"revision":1,"data_release":"proposed-release","baseline_ref":{"result_id":"r1","candidate_id":"maize"},"plan_refs":[{"result_id":"r1","candidate_id":"sorghum"}],"comparison_basis":"hypothetical_review","requested_metrics":["mean_tmax_c","sum_et0_mm","mean_et0_mm_day"],"anchor_policy":"all_complete_2001_2025"}
```

Example **unavailable** response fragment, not a claimed complete existing v1 response:

```json
{"schema_version":"1.0","status":"unavailable","comparison_basis":"hypothetical_review","data_release":"proposed-release","plan_statuses":["needs_review","needs_review"],"shared_blocks":[],"metrics":[{"metric_id":"sum_et0_mm","value":null,"unit":"mm","status":"unavailable","reason_code":"crop_end_unknown"}],"reason_codes":["complete_schedule_missing"],"assumptions":[],"exclusions":[]}
```

A real available metric additionally carries plan/block refs, N, valid-day count, source/method refs and numeric value; schema validation rejects missing lineage. Never invent numbers in contract examples. Pydantic definitions generate OpenAPI/TypeScript; runtime response checks and shared fixtures supplement static typing. Use discriminated forecast status handling; non-available forecasts expose no actionable numbers. Precedence: requested action outside horizon → not_applicable; relevant action with missing/invalid bundle → unavailable; expired valid bundle → stale. Resolve existing daily “all 14 records” versus request filtering wording with Yahya before implementation; recommend full validated bundle and an explicit applicable-date list.

Integration signatures: `generate(snapshot, catalogue)->CandidateSet`; `promise_test(snapshot,catalogue)->PlanningResult`; `replay(plans,weather,policy)->ReplayResult` are pure. Service functions load/store/render. `load_daily_bundle(path)->ValidatedBundle|Unavailable` performs only file/schema work. No PyTorch import in backend. Cache results by revision/release/canonical request; code/method identity is release-bound. Audio cache additionally binds locale, template version and spoken parameters. SQLite writes are short transactions; computation runs outside the write lock, with revision rechecked before save.

### 9.1 Standalone Python packages: authoritative implementation layout

This section finalizes code placement, not new product scope. Keep the approved pure-domain boundary and existing API semantics. Two installable local packages avoid FastAPI, SQLite, GPU or server dependencies in scientific tests. Use Pydantic already approved for shared validation; do not introduce a second handwritten wire schema.

| Package / module | Exact interface | Responsibility / owner |
|---|---|---|
| `packages/meg-core/src/meg_core/contracts/` | Existing Fact, SourceRef, ScenarioSnapshot, SeasonInput, RuleEvaluation, PlanEvaluation, Candidate, PlanningResult and ReplayResult; new DTOs below | Single shared Pydantic definitions, with Yahya reviewing API compatibility; backend `app/schemas/` re-exports these domain types and owns HTTP envelopes |
| `meg_core/knowledge/load.py` | `load_knowledge(release_dir: Path, expected_release: str) -> KnowledgeBase` | Refaat: explicit file I/O, hashes, source/ID/unit/scope checks; immutable validated result |
| `meg_core/planner/scope.py` | `prepare_scope(request: ScopeRequest, kb: KnowledgeBase) -> ScopePreview` | Amr + Astra: source-driven finite authorized choices and missing paths, pure |
| `meg_core/planner/generate.py` | `generate(snapshot: ScenarioSnapshot, kb: KnowledgeBase, policy: SearchPolicy) -> GenerationResult` | Amr + Astra: bounded enumeration, dependent-date invalidation, deduplication and provenance, pure |
| `meg_core/planner/constraints.py` | `evaluate(plan: tuple[SeasonInput, ...], snapshot: ScenarioSnapshot, kb: KnowledgeBase) -> PlanEvaluation` | Amr + Astra: existing Promise Test registry/date/status semantics, pure |
| `meg_core/planner/service.py` | `plan(snapshot: ScenarioSnapshot, kb: KnowledgeBase, policy: SearchPolicy) -> PlanningResult` | Pure orchestration of current evaluation, generation, candidate evaluation and ordering; no storage/HTTP/climate |
| `meg_core/climate/load.py` | `load_weather(release_dir: Path, expected_release: str) -> WeatherDataset` | Refaat: frozen-byte validation and typed adapter; no regeneration |
| `meg_core/climate/mapping.py` | `map_blocks(plans: tuple[ResolvedPlan, ...], weather: WeatherDataset, policy: ReplayPolicy) -> BlockMapping` | Mahmoud: paired anchors, interval and leap semantics, pure |
| `meg_core/climate/evaluate.py` | `evaluate_history(plans: tuple[ResolvedPlan, ...], weather: WeatherDataset, policy: ReplayPolicy) -> ReplayResult` | Mahmoud: metric-specific common coverage, exposure and paired differences, pure |
| `meg_core/forecast/baselines.py` | `predict_baseline(history: ForecastHistory, request: WeeklyForecastRequest, config: BaselineConfig) -> WeeklyForecastResult` | Amr: climatology/persistence only; no model libraries, no hidden clock or network |
| `ml/src/meg_ml/{data,features,splits}.py` | `build_examples(weather: WeatherDataset, protocol: ExperimentProtocol) -> ExampleSet` | Amr/Refaat: issue/cutoff/label manifests, train-only feature transformations |
| `ml/src/meg_ml/{ridge,lightgbm,chronos}.py` | `fit(train: ExampleSet, validation: ExampleSet, config: ModelConfig) -> ModelArtifact`; `predict(artifact: ModelArtifact, history: ForecastHistory, request: WeeklyForecastRequest) -> WeeklyForecastResult` | Amr: isolated optional model-specific dependencies; zero-shot Chronos uses `load_pretrained` instead of `fit` |
| `ml/src/meg_ml/evaluate.py` | `evaluate_predictions(predictions: PredictionSet, truth: TargetSet, protocol: ExperimentProtocol) -> EvaluationReport` | Amr/Refaat: paired metrics, exclusions, uncertainty and frozen selection criteria |

`meg-core` depends only on standard library and approved Pydantic. `meg-ml` depends on `meg-core` and approved experiment extras; core never imports `meg_ml`, FastAPI or SQLite. Tests live in `packages/meg-core/tests/` and `ml/tests/`; backend tests cover adapters later. Each package gets its own pyproject with the shared package installed locally; no publishing or new registry is needed. Standard-library CSV processing suffices; no pandas dependency is required in core.

**Additional DTOs (required fields unless explicitly nullable):**

- `KnowledgeBase`: release ID, manifest SHA256, source/assertion/profile/template/rule maps, mandatory topic registry. Maps cannot be mutated after loading. `WeatherDataset`: release/hash/site/LST/method metadata, ordered unique `WeatherRow` records (`date`, eight source values, ET0, per-variable QC); null numeric values require a reason. Sensitivity columns remain lineage-only fields.
- `ScopeRequest`: four ordered season slots and horizon, field facts, goals, protected commitments, allowed crop/purpose/profile IDs and proposed transfer permission. `ScopePreview`: release, canonical scope hash, explicit choices/template IDs, proposed facts/assumptions, missing paths. Confirmation binds the exact hash and release; preview itself does not authorize search.
- `SearchPolicy`: raw budget=256 and deterministic ordering version. `GenerationResult`: materialized candidates, raw count, uninstantiated choice IDs, exclusions, complete/incomplete and reason. Results must distinguish raw tuples from evaluated unique candidates; no generated timestamps affect ordering.
- `ResolvedPlan`: immutable current-plan or candidate reference, four season facts, prior PlanEvaluation, release. `ReplayPolicy`: requested metric IDs, comparison basis, historical range, endpoint/leap/coverage versions. `BlockMapping`: shared anchor IDs, per-plan/per-season mapped intervals, metric-specific exclusions. Unknown endpoints remain unknown.
- `ForecastHistory`: site, source release/hash, ordered observations, per-channel actual cutoff and available-at metadata (nullable with retrospective reason). `WeeklyForecastRequest`: issue date, common cutoff, target variables, lead weeks 1–4, exact target start/end dates, retrospective/prospective mode. `WeeklyForecastResult`: status/reasons, request, method/model identity, source release, records with variable/unit/lead/start/end/point estimate, optional ordered quantiles and calibration identity. Non-available results contain no prediction records. This is a research DTO, **not** daily ForecastBundle v1.
- `ExperimentProtocol`: immutable ID/hash, source release, origins/splits/purge rules, feature definitions, baseline support, model grid/seeds/budget and selection criteria. `ExampleSet`: features, real labels, variable/lead, issue/cutoff/target interval, split and exclusion log. `ModelArtifact`: run/model/config identity, fit cutoff, protocol/data hashes, feature order/transforms, artifact hash and optional parameter-update evidence. `EvaluationReport`: per-target/lead/season metrics, n/exclusions, paired baseline IDs and uncertainty method; no combined farmer score.

Loaders raise typed `ReleaseValidationError` or `KnowledgeValidationError` with safe path/code details; malformed domain inputs raise validation errors. Scientific incompleteness returns explicit unknown/unavailable results, not exceptions or fabricated defaults. Algorithm functions accept all dates/configuration explicitly and do no I/O. Local drivers serialize actual results to files; a file export is not a persisted backend Evidence Card.

**Integration without waiting:** implement `meg_core` contracts first from existing API §0 and BACKEND_DESIGN, reviewed once for the approved deltas. Yahya later writes adapters in `backend/app/{planner,replay,forecast,services}/`; they import these functions, resolve refs, render translations, add IDs/time and persist. No duplicate domain implementation or move is required. Domain JSON schemas can be exported before OpenAPI exists and generate Astra's types. Before backend integration, schema examples are clearly marked fixtures and cannot claim HTTP save success. Weekly research remains separate from the approved daily bundle adapter.

**Exact implementation order:** (1) contracts, package skeleton and schema round-trips; (2) release/KB loaders and standalone CLI input/output; (3) constraints/status and UH-001; (4) scope preparation and generic generator with non-fixture cases; (5) weather loader, mapping and paired metrics; (6) standalone plan→evaluate→replay JSON demonstration and reproducibility checks; (7) baseline/feature/split pipeline without fitting; (8) bounded Ridge training only when authorized and planner/climate core is working; (9) optional challengers; (10) backend/frontend adapters and persisted end-to-end journey as the integration workstream becomes available. Steps 1–8 do not require a running backend; UI/adapter preparation can run in parallel. The earlier P0 integration gate for optional ML means standalone core integration at step 6, not waiting for FastAPI.

**Remaining data gates finalized:** source PDFs/hashes/terms and two-person extraction review; operational cultivar/calendar/crop-end/release/preparation and field/irrigation facts G1–G7; complete SB-001 and unavailable proposal's seven-gap crosswalk; source-cell identities for multigrid; fresh issue-time weather vintages/outcomes for prospective ML; C3S hindcasts/verification/calibration; AquaCrop field calibration/validation. Only relevant capabilities are gated. Frozen POWER history already audited is sufficient to implement loaders, historical analysis and retrospective baseline experiments now after approval; no repeated archive audit is required to finalize this plan.

## 10. Reference scenarios and acceptance matrix

**UH-001 unchanged:** protected final berseem cut 2027-05-20; maize 2027-05-15; current rejected. Assumed release May 21 plus seven full days gives May 28 conditional arithmetic. May 28 and June 1 investigations remain needs_review; changed maize endpoints unknown unless separately supported. Exactly zero feasible alternatives; retain original four seasons from REFERENCE_SCENARIO, no invented later collision. Near-term forecast not applicable; save review draft, never approval.

**SB-001 pending full fixture:** only supplied season intervals are maize May 15–Sep 20, 2027 and hybrid-888 sorghum June 15–Sep 20, 2027. The user reports two complete needs_review plans, but they are not present here. Do not invent their other three seasons, fields, locks or seven-gap wording. Until Yahya supplies the complete fixture, support a labelled season-interval method test, not a four-season API acceptance claim. Once supplied, use the same unchanged other-season facts and compare only on their actual shared block set; retain needs_review. Trial evidence does not prove either rotation feasible.

| Test | Expected result / assertion | Owner |
|---|---|---|
| Incomplete facts, ambiguous date/unit | Nulls retain reasons; ambiguous values require correction; no silent defaults | Yahya/Amr |
| Unsupported crop ID | 422 unresolved ID; catalogue remains extensible | Yahya |
| Known template mismatch | Exclude with reason; unknown scope remains review | Amr + Astra |
| Invalid same-season calendar | 422 for reversed structural dates; valid outside-preference date is not automatically rejected | Amr + Astra/Yahya |
| Protected cut, crop, purpose | Never mutate locks; sow on/before protected final cut fails | Amr + Astra |
| Missing duration/end/release/preparation | Unknown planning topic; no feasibility, no fabricated replay interval | Amr + Astra |
| Cross-season and nonadjacent overlap | Hard failure even across an unknown middle season; equality at supported ready date passes | Amr + Astra |
| Empty/no candidate | Explain no feasible result in searched scope; distinguish complete exhaustion from evidence/budget truncation | Amr + Astra |
| Multiple review candidates | Separate list, stable edit ordering; no approval button or success color | Astra |
| Non-fixture generation | Vary goals/crops/horizon from KB; adding a reviewed template changes output without code changes or scenario IDs | Amr + Astra/Refaat |
| Unknown required rule topic | Registry coverage prevents vacuous feasible result | Amr + Astra |
| Synthetic all-known positive case | Feasible only in test namespace; never runtime crop evidence | Amr + Astra |
| Missing NASA date/ET0 | Paired block exclusion for all candidates; no zero fill, affected metric unavailable | Mahmoud |
| Leap and cross-year mapping | Feb-29 exclusions shared; intervening leap day counted; winter continuity retained | Mahmoud |
| Unequal crop durations | 129 vs 98 days under declared inclusive endpoints; totals and rates visible | Mahmoud/Astra |
| Symmetry and identity | identical plans difference zero; A−B = −(B−A); same weather blocks | Mahmoud |
| Provenance tampering | Hash/unit/source mismatch rejected; client `verified` cannot activate evidence | Refaat/Yahya |
| Model/C3S absent, stale or failed | Explicit independent status; planning/replay/save still work | Yahya |
| Feature leakage | Every feature date <=C; every fitted label available; purge boundary-spanning targets; no random split | Amr/Refaat |
| Quantile and week alignment | Reject nonfinite/crossed values; bridge step excluded; no averaged daily quantiles | Amr |
| Arabic/English | Same IDs, locks, dates, numbers/status/source refs; authored equivalent speech | Amr/Astra |
| Revision race / failed save | 409, old evidence non-current, failed save not shown saved; stale audio stopped | Yahya/Astra |
| Browser journey after implementation | Real API on desktop and phone widths in both languages; no mock success, keyboard/touch recovery | Astra/Amr |

No application acceptance test above has run in this planning task. Existing scientific tests remain untouched; future application tests belong in the approved backend/frontend suites. Browser testing is deferred until implementation.

## 11. Two-day execution and ownership

Day 1/2 below mean authorized work blocks on November 13/14, subject to D09. Estimates assume six contributors with 6–8 focused hours each day and no major environment failures. Backend availability must be reconciled first; if genuinely starting from placeholders, complete the P0 journey before expanding voice/provider work. Estimates are person-hours, not promises. Owners implement in isolated branches/worktrees; only Yahya edits shared Pydantic contracts and generated API outputs, Amr + Astra planner logic, Mahmoud replay, Refaat release data, Astra frontend, Amr experiment/wording. No agents are spawned by this planning task.

Each row's acceptance is its Definition of Done; all require reviewed diff, relevant passing checks and an honest status entry.

| Stream / priority / day | Owner | Deliverable and files | Dependencies / hours | Acceptance and integration | Failure fallback |
|---|---|---|---|---|---|
| Contract reconciliation P0 D1 start | Yahya + Amr | Current branch/proposal crosswalk; approved delta in API/BACKEND docs, source revision recorded | Amr approval; 2 h | No hidden conflict, exact SB-001 and seven gaps known or explicitly blocked; team freezes contract | Keep existing API and omit blocked expansion |
| A Data P0 D1 | Refaat | Frozen weather release builder, manifest, QC sidecar; `data/release/weather`, `data/validation/release_weather.py` | ZIP present; 3 h | Original hashes/row counts/units; no weights/raw archive committed; loader works offline | Fail weather component explicitly, continue planning |
| B Crop evidence P0 D1 | Refaat + Amr + Astra | Review/promote KB to `data/release/catalogue/{crops,rules,sources,templates}.json` | Reacquire missing pages; 4 h | All four crops; original trial years, scope and unknowns retained; two-person extraction review | Leave assertions inactive; empty/review search with named gaps |
| D Promise Test P0 D1 | Amr + Astra | `planner/dates.py`, rules, evaluate/status; UH golden test | Schemas/KB; 5 h | UH expected statuses and locks exact; negative/unknown/coverage tests | Restrict checked rules transparently; no feasibility claims |
| C Candidate generator P0 D1–D2 | Amr + Astra | `planner/generate.py`, `enumerate.py`, scope builder tests | Rules/templates; 5 h | Generates from KB for non-fixture inputs, 256 cap, endpoint invalidation, stable order | Return supported investigations only; no fabricated full plan |
| I API/storage P0 D1 | Yahya | Approved schemas, core loader, SQLite/store, catalogue/scenario/planning routers, OpenAPI/TS export | Reconciliation; 6 h | Real create→evaluate→retrieve, stale revisions 409, hash failures explicit | Controlled local prototype, no remote real data |
| E Historical P0 D1–D2 | Mahmoud | `replay/mapping.py`, `metrics.py`, unit fixtures and scientific report | Frozen release/plan models; 5 h | Common blocks, duration/units, missing/leap/symmetry checks; no water claims | Unavailable affected metrics, retain period-only diagnostics |
| I Replay/card integration P0 D2 morning | Yahya | `services/{replay,evidence}_service.py`, routers and card persistence | E + planner + schemas; 4 h | Real replay refs, immutable review save/reload, currentness | Save draft without replay with explicit reason |
| I React journey P0 D1–D2 | Astra | Intake/goals, season timeline, promise-test, replay/evidence-card features; typed services/hooks | Approved handoff/API; 10 h | Fieldlight arches, RTL/LTR, explicit scope confirmation, real API, no frontend science | Smaller connected journey, unresolved draft; never mock integrated success |
| I Voice/content P0 D1–D2 | Amr + Yahya/Astra | Authored bilingual backend messages, fixed prompt audio, speech adapters and touch recovery | Existing approved voice interfaces; 4 h | Full dates/units/status replay; denied/absent mic usable; no transcript persistence | Device voice or recorded prompts with actual capability label; document accessibility gap |
| F Lightweight ML P1 D2 only after gate | Amr + Refaat | `ml/{data,splits,features,baselines,train_ridge,evaluate}.py`, registered protocol/results | Frozen data; P0 integrated; 4 h | Same origins, eight models, leakage checks, baseline table, negative result retained | Historical experiment + climatology evidence only |
| G Chronos P2 D2 | Amr | Optional weekly zero-shot diagnostic report, ignored local outputs | F complete and P0 stable; 2 h cap | Pinned weights, measured resources, matched targets; no fresh-test claim | Skip; no new LoRA |
| H Seasonal P2 D2 | Mahmoud | Data/skill feasibility note only; no service commitment | P0 replay stable; 1 h | Official system/init/hindcast inventory; unavailable if no skill | No outlook numbers |
| J End-to-end P0 D2 afternoon | All; Amr accountable | Real local demo, tests, fresh-clone/release startup notes, updated status | P0 integrations; 8 team h | Two languages, UH, non-fixture search, paired evidence, draft save/reload, provider failures | Cut optional work; present remaining limitations explicitly |

Core critical path: approved shared contracts → KB loader and Promise Test → generic generator → frozen-weather paired replay → standalone integrated JSON demonstration. API/React/persisted cards are a parallel integration path, not prerequisites for Python development. Apply §9.1's module mapping to the task table above; backend-hosted algorithm paths are adapters only. Data release, rule implementation, replay math and Fieldlight shell can proceed concurrently against frozen interfaces. Amr's content/audio work precedes optional ML where assigned.

Day 1 core checkpoint (end of authorized block): validated standalone release/KB loader, real Promise Test output and UH-001 statuses; HTTP is not required. If absent, all P1/P2 stops. Day 2 midday core checkpoint: non-fixture KB generation and paired historical evaluation through the standalone driver with schema-validated JSON. Optional ML may start after this core checkpoint; it does not wait for FastAPI. The separate application checkpoint remains a real API/React journey with a saved review draft; its absence must be reported, never hidden by local-file exports. Last 3 hours: freeze features, run relevant failures/restart/demo rehearsal, repair only blockers. A fixture-only demo does **not** satisfy the generic planner requirement; report that incompleteness rather than rename it a data-driven engine.

## 12. Demo, risks and prioritized next actions

Demo sequence: enter needs and field facts → confirm a protected commitment and permitted exploration scope → request candidate generation → inspect real rule results and unknowns → open source-backed historical weather → compare clearly labelled intervals/plans with totals and duration-normalized metrics → save/reload the exact review draft. Show UH-001 as a regression demonstration, then a second non-fixture request driven by the KB (with unknowns visible). Use SB-001 only when its full plan is supplied; otherwise show a clearly titled two-season-interval comparison, not a completed four-season plan.

Real outputs possible from existing evidence: calendar conflicts and conditional day arithmetic; rule-linked missing-data explanations; generated trial-template investigations; historical Tmax/ET0 exposure, shared-block differences and duration; saved source-linked draft. Actual numeric climate results are future computations, not numbers prewritten in this plan. Trained-ML evidence is the reproduced old negative result; any new experiment reports what actually happens.

Additional data are required for field-applicable complete feasible schedules, crop response, actual irrigation/yield/productivity and operational forecast skill. User intentions and target-year transfers are assumptions. UH-001 is fictional; synthetic tests are isolated; preview speech/save animations must never masquerade as live services. No fabricated future weather, recommendation success, probability, farmer benefit, water saving or yield advantage may appear in the demo or pitch.

Offline: with local backend and frozen release, planning, historical replay and SQLite save need no NASA connection. Browser reload, uncached speech and remote-host access are separate capabilities; no full offline/PWA promise. Forecast absence is explicit. Cached audio and recorded prompts are labelled; no backend means local unsaved draft only. Evidence cards distinguish saved server state from browser cache.

| Risk | Mitigation / fallback |
|---|---|
| Unavailable CLIMATE_AWARE_PLANNER proposal | Preserve existing available contracts; defer only exact seven-gap/SB-001 crosswalk, not standalone implementation |
| Source page inaccessible or ambiguous | Keep ledger-derived draft inactive pending double review; cite access limitation |
| No real feasible four-season alternative | Deliver conflict/review support honestly; missing agronomy is a scientific limit, not a UI defect |
| Linux byte regeneration variation | Use frozen bytes and unchanged hash checks; keep numerical reproduction and byte reproduction separate |
| Model loses, fails or cannot run | Report result/absence; climatology and core planner remain independent |
| Source product vs station bias | State gridded regional nature; no fabricated correction or field truth |
| Stale schema/release/response | Freeze shared contracts, generated clients, transactional revision checks and version-bound audio/cards |
| Schedule overload | P0 gates stop optional training/outlook; reserve final integration time |

**Single recommendation:** approve the deterministic KB-driven planner + unchanged Promise Test + paired frozen-POWER replay architecture, with a conditional Ridge research experiment and no new LoRA/C3S/AquaCrop runtime integration.

**Exact next actions:** (1) Amr reviews D01–D10 and §9.1; (2) implement the shared contracts and standalone loaders; (3) Amr + Astra builds constraints/generation, Mahmoud climate evaluation and Amr baseline/split preparation against Refaat's releases; (4) integrate the standalone plan/replay demonstration; (5) run the authorized bounded ML experiment if time remains; (6) Yahya and Astra integrate HTTP, React and saved cards through the documented adapters. Obtain the missing proposal/full SB-001 independently; do not wait for backend implementation. Stop here before implementation.
