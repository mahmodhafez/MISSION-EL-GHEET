# Crop capabilities, evidence and farmer intake

Sakha, Kafr El-Sheikh · 14 November 2026 · sakha-agricultural-review-2026-11-14.1

The evidence supports research and scoped review. Eight crop IDs have nine planner profiles. A review candidate can be offered for a matching purpose after scope confirmation. Every crop has pending qualified approval and zero eligibility for a verified feasible rotation.

| Crop ID | Crop / purpose | Catalogue capability | Profile and permission | Qualified approval | Feasibility eligible |
|---|---|---|---|---|---|
| `wheat` | قمح / `grain` | `review_candidate` | Matching-purpose exploration | PENDING | No |
| `berseem` | برسيم / `forage_or_seed_requires_review` | `runtime_profile` | Stored generic profile; separate proposed forage profile | PENDING | No |
| `grain_maize` | ذرة شامية / `grain` | `review_candidate` | Matching-purpose exploration | PENDING | No |
| `grain_sorghum` | ذرة رفيعة / `grain` | `review_candidate` | Matching-purpose exploration | PENDING | No |
| `rice` | أرز / `grain` | `review_candidate` | Matching-purpose exploration | PENDING | No |
| `sugar_beet` | بنجر السكر / `sugar` | `review_candidate` | Matching-purpose exploration | PENDING | No |
| `egyptian_cotton` | قطن مصري / `fibre` | `review_candidate` | Matching-purpose exploration | PENDING | No |
| `faba_bean` | فول بلدي / `grain` | `review_candidate` | Matching-purpose exploration | PENDING | No |
| `watermelon` | بطيخ / `fresh_fruit` | `research_record` | No planner profile or exploration offer | PENDING | No |
| `strawberry` | فراولة / `fresh_fruit` | `research_record` | No planner profile or exploration offer | PENDING | No |
| `cantaloupe` | كنتالوب / `fresh_fruit` | `research_record` | No planner profile or exploration offer | PENDING | No |
| `harankash` | حرنكش / `fresh_fruit` | `research_record` | No planner profile or exploration offer | PENDING | No |

The real offer lists include five grain crop IDs (wheat, grain maize, grain sorghum, faba bean and rice), one forage crop via its proposed profile, one sugar crop and one fibre crop. Seed and fresh fruit have no exploration offers. A catalogue offer and an evaluated candidate are separate events.

## Intake for the same parcel and four successive seasons

| Field | What the team needs to capture | Mapping / status |
|---|---|---|
| Site and parcel | Confirm locality, field ID, same field or separate nursery/field, area and unit, target years, season order and production system. | The current private planner uses site_id, field_id and season labels. Land class, village and nursery geography need a scoped intake mapping. |
| Crop and identity | Crop ID, profile ID, purpose, named cultivar/hybrid or planting-stock identity and establishment method for every season. | SeasonInput.crop_id, profile_id and purpose. The remaining details need approved field/season mappings. |
| Crop calendar | Intended/actual sowing or main-field transplant date, harvest or last cut, first day after living occupation, actual first free day and days of preparation **after release** for each transition. | SeasonInput.sowing_date, harvest_or_cut_date, crop_end_exclusive, release_date, preparation_days_after_release. Save the known facts independently. |
| Locks and output | Exact dated crop/purpose/occupation/cut commitments, repeated pickings if relevant, whether feed quantity is a hard commitment, unit and evidence for any quantity. | Commitments, production_requirements. An exact cut different from crop end can be protected. Missing evidence for a hard output stays unresolved. |
| Soil and water | Texture, drainage, water table, measured pH, ECe test depth/date/method, ECw separately, source, canal turns, water delivery and reliability. | Field facts must carry units, method, evidence origin and confirmation. A station soil or research treatment cannot be substituted. |
| Operations and history | Predecessor and successor, previous years of rotation/disease history, residue handling, equipment/labour, storage on the parcel, trafficability and first workable day. | Confirm each transition. Pre-horizon multi-year history needs an agreed shared-contract extension. |
| Exploration | Permitted fields, alternative dates or crops, priority order and explicit farmer confirmation of the read-back scope. | ScopeRequest / ScopePreview / scope_hash. Unknowns are recorded explicitly. A confirmed unknown remains unknown, and a farmer cannot grant scientific approval. |

UH-001 already supplies the protected cut, crop/purpose locks and a seven-day scenario assumption. Do not request or present that assumption as a general turnaround. No default zero, standard salt veto, biomass delivery or automatic fertilizer credit is present.

## Assessment of the eight additions

Each entry below reports observed or published context separately from the missing decision for the farmer’s actual field. The associated machine record supplies null operational values for sowing window, harvest/last cut, crop end, release, preparation, soil exclusion, irrigation schedule and rotation restrictions.

### Rice · `rice`

**RI1 · legal reference.** MWRI Decree 32/2026 is catalogued in Gazette 87 supplement (هـ), 20 April 2026. Law 147/2021 establishes designation by the authorities. The issue PDF required a copy request. No parcel or 2027/28 annex match was established. Governorate membership cannot authorize a field. [RICE-GAZ](https://dspace.id.com.eg/items/73a3156e-4d94-4f87-9193-543eb679c2ca) · [RICE-LAW](https://gate.ahram.org.eg/media/News/2021/10/26/2021-637708424566622619-662.pdf)

**RI2 · unverified lead.** The handoff reports canal rotations and a 2026 administrative irrigation period. Neither sowing dates nor permission for the farm can be inferred from an announced water rotation. Obtain the authority's current canal schedule. [ASSESS](https://github.com/mahmodhafez/MISSION-EL-GHEET/blob/5644125a10f1866fc1d8fac84bd5de689402cc57/docs/planner/crop-expansion-assessment.md)

**RI3 · local trial.** RRTC Sakha, 2024 and 2025. Giza 178, Sakha Super 302 and Giza 183 had nursery sowing on May 2 and 30-day seedlings in transplanted plots. A nursery date sets main-field occupancy only if the nursery occupies that same parcel. The experiment did not test an optimal planting interval. [RI3](https://doi.org/10.3389/fpls.2026.1789050)

**RI4 · multi site trial.** A May seedbed and 25-day seedlings were used in 2021–22 across locations including Sakha. Another Sakha study transplanted 30-day seedlings in the 2016–17 work. These distinct breeding protocols do not establish a 25–30 day rule for direct seeding or all varieties. [RI4a](https://doi.org/10.3390/plants13010074) · [RI4b](https://doi.org/10.1016/j.sjbs.2021.12.054)

**RI5 · unresolved.** The team found incompatible Giza 179 durations. The start event and maturity/harvest endpoint for both figures are unreconciled. No duration selected. Require breeder record, named establishment system, season and endpoint. [ASSESS](https://github.com/mahmodhafez/MISSION-EL-GHEET/blob/5644125a10f1866fc1d8fac84bd5de689402cc57/docs/planner/crop-expansion-assessment.md)

**RI6 · unknown.** No release-ready date was established for the intended rice parcel. Final water withdrawal, grain harvest, soil trafficability and straw clearance must be dated individually. [RI3](https://doi.org/10.3389/fpls.2026.1789050) · [RI4a](https://doi.org/10.3390/plants13010074)

| Decision | Field assessment |
|---|---|
| Planting and establishment | Distinguish same-field nursery, off-field nursery, transplanting and direct seeding. |
| Harvest and maturity | Confirm grain maturity, harvest moisture and actual harvest. |
| Field occupancy and release | Record nursery location, main-field entry, drawdown, straw handling and first free day. |
| Land preparation | Confirm levelling, nursery/puddling or dry/direct-seeding operations and their dates. |
| Soil | Local experiments include clay; measure parcel texture and salinity using a stated method. |
| Irrigation and drainage | Require year-specific permission and real canal deliveries, drainage access and water availability. |
| Rotation | Obtain prior crop and straw treatment plus the successor sowing date. No universal pair restriction. |
| Crop purpose and cultivar | Grain rice; require cultivar and transplant versus direct-seeding system. |
| Inputs to request | village/parcel, canal, permit year/reference, establishment method, nursery parcel, dates, cultivar, last water, combine and straw clearance |

### Sugar beet · `sugar_beet`

**SB1 · local trial internal conflict.** At Al-Hamul, Pleno after maize was sown in the first week of October. The authors give harvest dates of 27 April 2022 and 24 April 2023, and also state 180 days. With sowing Oct 1–7 the elapsed intervals are 202–208 and 199–205 days respectively. Preserve reported dates and the conflicting text. No farm duration can be fitted. [SB1](https://doi.org/10.7717/peerj.19452)

**SB2 · local trial internal conflict.** Pleno on salt-affected clay in Kafr El-Sheikh, 2022/23 and 2023/24. First-week October sowing is paired with both 180 days and late April. No exact sow/harvest pair. Late April and the stated elapsed time disagree. Do not combine with SB1 or impute dates. [SB2](https://doi.org/10.1371/journal.pone.0337492)

**SB3 · local trial.** Sakha 2022/23–2023/24, BTS SMART 8565. Mid-September sowing and harvest at 210 days were part of the trial protocol. Different cultivar and management from Pleno. The protocol supplies neither a cultivar maturity constant nor the factory collection or clearance date. [SB3](https://doi.org/10.1186/s12870-026-09776-0)

**SB4 · operational unknown.** The field may still be occupied by stored roots or machinery after lifting. Contract, lifting, stacking location and field clearance must be distinguished. A delivery is relevant if storage or access actually blocks the field. A factory date alone cannot be translated into release. [ASSESS](https://github.com/mahmodhafez/MISSION-EL-GHEET/blob/5644125a10f1866fc1d8fac84bd5de689402cc57/docs/planner/crop-expansion-assessment.md) · [SB1](https://doi.org/10.7717/peerj.19452)

**SB5 · unverified lead.** The team records beet-cyst nematode evidence on related hosts and a greenhouse berseem lead. A greenhouse host record does not establish field carry-over or a universal berseem-to-beet ban. [ASSESS](https://github.com/mahmodhafez/MISSION-EL-GHEET/blob/5644125a10f1866fc1d8fac84bd5de689402cc57/docs/planner/crop-expansion-assessment.md)

| Decision | Field assessment |
|---|---|
| Planting and establishment | Record actual sowing date, the cultivar and intended factory campaign. |
| Harvest and maturity | Distinguish root lifting and quality target from trial harvest age. |
| Field occupancy and release | Record lifting, location of any stacked roots, loading access and verified first free day. |
| Land preparation | Identify seedbed work and the interval needed for the next crop after lifting and ruts. |
| Soil | Saline clay in local trials demonstrates cultivation under treatments. No farm threshold is established. |
| Irrigation and drainage | Record irrigation turns, water quality, drainage and soil trafficability for lifting. |
| Rotation | A maize predecessor was observed in SB1. Cyst-nematode rotation or a compulsory predecessor remains open. |
| Crop purpose and cultivar | Sugar extraction; distinguish Pleno from BTS SMART 8565 and other contracted cultivars. |
| Inputs to request | cultivar, factory/contract and campaign, sowing/lifting and collection dates, storage location, soil ECe and drainage, predecessor and residue operations |

### Watermelon · `watermelon`

**WM1 · national extension.** ARC bulletin 1380 (2019) separates main summer seed sowing, mid-February into April, from May/June sowing and protected/off-season systems. The team’s Hassan copy uses mid-April as an endpoint. No farm-specific endpoint is justified by the two wordings. Harvest extends over pickings. Local dates and the final pick for a fresh-fruit cultivar are unknown. [WM-ARC](https://misrelzraea.com/wp-content/uploads/2024/03/%D8%A7%D9%84%D8%A8%D8%B7%D9%8A%D8%AE.pdf) · [WM-HASSAN](https://archive.org/download/HorticulturalCropsFertilizationBasics/)

**WM2 · conditional guidance.** The team’s 2005 source reports well-drained, salt-free conditions and a 3–4 year wilt rotation. ARC discusses season and establishment systems. The interval in the 2005 copy was not independently checked. No measured ECe threshold or universal cucurbit ban follows. Prior years are missing from the four-slot input. [WM-HASSAN](https://archive.org/download/HorticulturalCropsFertilizationBasics/) · [WM-ARC](https://misrelzraea.com/wp-content/uploads/2024/03/%D8%A7%D9%84%D8%A8%D8%B7%D9%8A%D8%AE.pdf)

**WM3 · different purpose excluded.** Sakha grafting research in 2009–10 studied Nubian seed watermelon with surface irrigation. The product and harvest endpoint differ from fresh dessert watermelon. No fresh-fruit calendar can be transferred. [WM-SEED](https://sci.tanta.edu.eg/files/7-13-Effect%20of%20grafting%20Nubian%20watermelon%20on%20its%20growth,%20flowering,%20yield%20and%20fruit%20quality.pdf)

**WM4 · different purpose excluded.** A local seed-watermelon/whitefly experiment is cited in the expansion assessment. This lead addresses insect incidence on a seed crop. It establishes no fresh-fruit date or field-release rule. [ASSESS](https://github.com/mahmodhafez/MISSION-EL-GHEET/blob/5644125a10f1866fc1d8fac84bd5de689402cc57/docs/planner/crop-expansion-assessment.md)

| Decision | Field assessment |
|---|---|
| Planting and establishment | Select summer, nili or protected system, and direct seed versus transplant. |
| Harvest and maturity | Record marketable maturity and last fresh-fruit picking. Seed harvest is a different endpoint. |
| Field occupancy and release | Track final picking, vine and mulch removal, irrigation lines and first free day. |
| Land preparation | Record beds/ridges, direct sowing or transplant setup and any tunnels. Duration unknown. |
| Soil | Confirm soil ECe, drainage and rooting depth; generic descriptions do not set EC cutoffs. |
| Irrigation and drainage | Identify surface or drip system and actual water availability during fruit development. |
| Rotation | Obtain multi-year cucurbit/wilt history and named predecessor. A national sequence example does not certify rotation. |
| Crop purpose and cultivar | Fresh dessert fruit, cultivar/hybrid and rootstock if grafted. Exclude seed-purpose observations. |
| Inputs to request | fresh/seed purpose, cultivar/rootstock, season/system, sow or transplant, ECe/drainage, field history, last pick and vine removal |

### Strawberry · `strawberry`

**ST1 · national extension.** UF/IFAS describes historical frigo Sweet Charlie plantings from early September to mid-October with fruit from mid-February to May. Fresh plants set in the same period began fruiting in early November. Plant source, year, cultivar and cultivation system determine the context. First fruit is not the last pick, removal or free day. [ST1](https://ask.ifas.ufl.edu/publication/HS1411/pdf) · [ST-ARC](https://www.arc.sci.eg/files/2105/Attachment.pdf)

**ST2 · secondary review.** A national review reports a break before replanting strawberry and cautions about wet, heavy soils. The team cites at least two years and examples of other crops. Treat as a literature lead. Verify local disease pressure and dated field history. No return interval or rotation prohibition is assigned. [ST-ROT](https://doi.org/10.1186/s42269-019-0049-2)

**ST3 · standard reference.** FAO's yield-potential table lists strawberry at ECe 1.0 dS/m for the 100% reference column. Use comparable saturated-paste ECe with units, date and depth. It is a response reference, not automatic failure of a farm above that value. ECw is a different measurement. [ST-FAO](https://www.fao.org/4/t0234e/T0234E03.htm)

**ST4 · different system.** The supplied Kafrelsheikh investigation used a protected production system. Location alone does not qualify an open-field crop. Validate drainage, beds, cultivar, transplant source and picking calendar under the intended system. [ST-PROT](https://doi.org/10.21608/jsas.2016.2956)

| Decision | Field assessment |
|---|---|
| Planting and establishment | Identify fresh, plug or frigo stock and open field versus protected establishment. |
| Harvest and maturity | First fruit, last commercial picking and plant removal are separate. |
| Field occupancy and release | Long repeated harvesting can cross a season boundary. Verify last picking and clearing of plants and mulch. |
| Land preparation | Record bed formation, drainage, mulch/irrigation setup and removal duration. |
| Soil | Record saturated-paste ECe and depth. FAO response is contextual. Check suitability of heavy, wet soil. |
| Irrigation and drainage | Confirm drainage and high water table, irrigation quality and access through the picking period. |
| Rotation | Collect preceding years' crops and disease history before applying any return interval. |
| Crop purpose and cultivar | Fresh fruit; name cultivar, transplant source/physiological state and season. |
| Inputs to request | cultivar, stock type, production system, planting and picking dates, ECe/ECw and drainage, crop history, mulch and bed clearance |

### Egyptian cotton · `egyptian_cotton`

**CT1 · local trial internal conflict.** Sakha 2022–23 after clover. Abstract reports April 25, May 15 and May 25. Experimental design/Table 5 use May 10 as the middle treatment. Super Giza 94, Extra Giza 96 and Super Giza 97 were tested. Clay plot with 50.6% clay. The earliest treatment performed well within the trial. The middle date is disputed and the tested span is not an accepted planting window. [CT1](https://doi.org/10.1186/s12870-025-08076-3)

**CT2 · local trial.** Authors mention early October harvest measurements. Table 5 measures time to second picking and repeats a 2022 block label. Second picking is not identified as final field clearance. Retain the ambiguous table label and request last picking, stalk removal and release. [CT1](https://doi.org/10.1186/s12870-025-08076-3)

**CT3 · official season map.** Ministerial Decision 57/2026, arts. 6 and 8, maps Extra Giza 96 to Fuwwah, Mutubas and designated zones of Sidi Salem and Desouk. Super Giza 94 covers the remaining Kafr El-Sheikh area under art. 8. Decision concerns summer 2026 and includes specific exceptions. Obtain the relevant year and parcel district/zone. A station trial is not a legal exemption for a farmer. [COT-GAZ](https://mediadr.sis.gov.eg/bitstream/handle/123456789/123196/WQ61_20260315_9880.pdf?isAllowed=y&sequence=2)

**CT4 · unverified legal status.** The assessment cites historic stalk-uprooting measures 1472/1994 and 1229/1998. Consolidated current text, exceptions and operative season were not established. No November deadline or stalk-disposal prescription is encoded. [COT-HIST](https://leap.unep.org/en/countries/eg/national-legislation/resolution-no-1472-1994-concerning-uprooting-cotton-shrubs-flax)

| Decision | Field assessment |
|---|---|
| Planting and establishment | Match parcel and season to the legal variety map before evaluating a chosen sowing date. |
| Harvest and maturity | Record final picking; Table 5 measures only second picking. |
| Field occupancy and release | Final picking may precede removal of stalks. Record actual clearance and first access. |
| Land preparation | Record ridging/bed preparation, stalk removal and next crop’s preparation. |
| Soil | Station clay EC is a site measurement. Ask for comparable field soil and water tests. |
| Irrigation and drainage | Confirm actual canal turns, drainage and irrigation method. No general schedule derived. |
| Rotation | Clover preceded experimental cotton. Confirm actual predecessor and release. A faba-to-cotton sequence is conditional. |
| Crop purpose and cultivar | Fibre cotton, designated cultivar, multiplication/contract scheme and possible mapped exceptions. |
| Inputs to request | target year, markaz/cordon, cultivar/seed source, preceding crop, last picking, stalk removal and legal reference, irrigation and field-ready dates |

### Faba bean · `faba_bean`

**FB1 · local trial.** Sakha, 2011/12 and 2012/13. October 1, November 1 and December 1 treatments. Attia et al. selected Sakha 4 on November 1 with sowing irrigation and later irrigations on days 30 and 90 under trial conditions. A tested optimum and irrigation treatment do not set a one-day window, guaranteed canal deliveries or time to dry-grain harvest. [FB1](https://jpp.journals.ekb.eg/article_53657_ad0feeae7a02d5cde8f0c58c215ba834.pdf)

**FB2 · local literature lead.** The team links earlier sowing to greater chocolate spot and rust pressure versus November 1 in a Sakha study. Disease varies by season, cultivar and field. Obtain the original dated records before quantifying risk or blocking a date. [FB-DISEASE](https://doi.org/10.21608/mjppf.2021.169116)

**FB3 · local trial.** At Sakha, delaying from November 1 to 30 reduced broomrape spikes per plot in both seasons. The authors also report lower seed yield per feddan in the first season. A lower parasite count does not identify a yield optimum. Results apply to the tested infested fields and genotypes. [FB-BROOM](https://alexja.journals.ekb.eg/article_28568_787bd2447fd7a68c0d58b348dd6c8f77.pdf)

**FB4 · cultivar release study.** Sakha 1 matured about 24 days earlier than Giza 461 averaged across trials. The release study includes days-to-maturity tables and the potential to precede cotton. Relative earliness and trial maturity observations do not establish an absolute dry-grain harvest date, residue removal or guaranteed cotton turnaround. [FB-EARLY](https://jpp.journals.ekb.eg/article_254204_b1c29e5a0d977170c7efd4d8de89a93a.pdf)

**FB5 · nonlocal trial.** Hegab et al. studied planting date and irrigation in El-Bosaily on the northern coast under drip irrigation. Site and irrigation system differ from the target field. Do not transpose trial calendars. [FB-COAST](https://doi.org/10.1016/j.aoas.2014.11.004)

| Decision | Field assessment |
|---|---|
| Planting and establishment | Confirm dry-grain target, cultivar, proposed autumn date and field disease history. |
| Harvest and maturity | Maturity differs by genotype; record dry pods/grain readiness and actual harvest. |
| Field occupancy and release | Require residue removal and first free day, especially if the intended successor is cotton. |
| Land preparation | Record seedbed and residue operations; the Sakha study’s irrigation or crop duration gives no turnaround. |
| Soil | Confirm field texture and pest/infestation record. Record soil salinity, drainage and sampling method. |
| Irrigation and drainage | Distinguish sowing water from subsequent irrigation; obtain water availability under the farm system. |
| Rotation | Sakha 1 precedes cotton in breeding rationale. Broomrape and disease require local history. |
| Crop purpose and cultivar | Dry grain. Sakha 1 earliness and Sakha 4 sowing response belong to different cultivars. |
| Inputs to request | grain versus green pods, cultivar, broomrape/disease history, soil and irrigation, planting/harvest, clearance, intended cotton or other successor |

### Cantaloupe · `cantaloupe`

**CA1 · local trial.** Sidi Salem, Kafr El-Sheikh, summer 2005 and 2006. Ananas F1 was studied in a farm trial. Cultivar-specific presence provides no complete local calendar for a different melon group. [CA-THESIS](https://kfs.edu.eg/engkfs/display.aspx?topic=2129)

**CA2 · local trial.** Sakha clay, furrow-irrigated plots. 22-day-old Hybrid French F1 transplants were set May 28, 2012 and May 24, 2013. The paper distinguishes first picking yield from total yield. Primary methods recover cultivar and actual planting dates missing in the team summary. Two observed transplant dates do not define a sowing window or the date of the last marketable pick. [CA-FIELD](https://journals.ekb.eg/article_49842_7eb261212e68493250001e261805d3e6.pdf)

**CA3 · unverified lead.** The team cites secondary advice assigning July to Lower Egypt. No matching primary recommendation for this cultivar/production system was confirmed. The proposed July date stays unknown for use. [ASSESS](https://github.com/mahmodhafez/MISSION-EL-GHEET/blob/5644125a10f1866fc1d8fac84bd5de689402cc57/docs/planner/crop-expansion-assessment.md)

| Decision | Field assessment |
|---|---|
| Planting and establishment | Historical French F1 transplant dates and Ananas F1 local presence; local prescriptions require cultivar and system. |
| Harvest and maturity | Identify market maturity, picking programme and last harvest. |
| Field occupancy and release | Collect first and last picking plus vine/mulch clearance; no free date is stated for CA2. |
| Land preparation | Field ridges and transplanted seedlings occur in CA2. Setup and removal time for this field is unknown. |
| Soil | Sakha clay in CA2 is an observation. Soil suitability and drainage on the farm require confirmation. |
| Irrigation and drainage | Furrow cut-off was experimental. Match drip/furrow, water turns and drainage without importing a treatment. |
| Rotation | Obtain multi-year cucurbit predecessor and disease history. No approved rotation interval. |
| Crop purpose and cultivar | Cucumis melo fresh fruit; identify horticultural group, hybrid and outdoor/protected system. |
| Inputs to request | hybrid/group, field system, nursery location, transplant date, water and drainage, prior cucurbits, final pick and clearing |

### Harankash · `harankash`

**HK1 · taxonomic scope.** The intended English crop cape gooseberry is Physalis peruviana. Egyptian records also use a broad vernacular name. A Qalyubia insect survey is a species lead. Confirm the actual lot and Latin name before crop binding. The existing catalogue ID remains broad and research-only. [HK-FAO](https://openknowledge.fao.org/3/cc5044en/cc5044en.pdf) · [HK-PEST](https://doi.org/10.21608/assjm.2015.109818)

**HK2 · different species excluded.** Helaly et al. studied P. pubescens in Qalyubia clay loam with furrow irrigation. The seedbed and transplanting schedule belongs to that species. No P. pubescens planting, picking or release dates transfer to P. peruviana in Sakha. [HK-PUB](https://medcraveonline.com/APAR/effect-of-polyethylene-mulching-type-on-the-growth-yield-and-fruits-quality-of-physalis-pubescens.html)

**HK3 · taxonomic scope.** The attached assessment traces Egyptian literature using several Physalis names for related produce. Do not pool results across species. Obtain verified species, cultivar, propagation method and local field records. [ASSESS](https://github.com/mahmodhafez/MISSION-EL-GHEET/blob/5644125a10f1866fc1d8fac84bd5de689402cc57/docs/planner/crop-expansion-assessment.md) · [HK-FAO](https://openknowledge.fao.org/3/cc5044en/cc5044en.pdf)

**HK4 · nonlocal trial.** Kamal and Ghanem grew P. peruviana cv. Balady in sandy soil at Al-Nubaria in 2009 and 2010. Forty-day transplants were planted August 1 in both seasons. This is an Egyptian species-matched example. It supplies no Sakha window, end of picking or field clearance on clay. [HK-PER](https://journals.ekb.eg/article_85775_92958f210fa7e2ff659ed322ef1cec29.pdf)

| Decision | Field assessment |
|---|---|
| Planting and establishment | Confirm P. peruviana identity and planting material; assess local transplant establishment. |
| Harvest and maturity | Collect picking start/end, market-ripe fruit criteria and whether plants are carried over. |
| Field occupancy and release | A continuing stand may occupy the field after a picking season. Verify removal and first free day. |
| Land preparation | Identify beds/ridges, irrigation layout and stand removal. Local time unknown. |
| Soil | A sandy Nubaria P. peruviana trial and Qalyubia P. pubescens soil do not show target parcel fit. |
| Irrigation and drainage | Obtain field water source, irrigation method, drainage, ECw and soil ECe. |
| Rotation | Document preceding solanaceous crops and duration of stand. No approved carry-over or return rule. |
| Crop purpose and cultivar | Cape gooseberry target is P. peruviana. Local harankash planting material/cultivar remains to be identified. |
| Inputs to request | Latin species and seed/seedling evidence, cultivar, annual or retained stand, planting/pick/removal dates, drainage and previous crops |
