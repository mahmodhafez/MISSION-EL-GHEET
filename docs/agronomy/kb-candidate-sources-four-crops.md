# Candidate KB evidence: rice, faba bean, sugar beet, Egyptian cotton

**Read this if…** you're adding these four crops to the reviewed Sakha agricultural KB, or checking where a number on the
farmer's "What research says" card would come from.

Status: Proposed, **not used by the app** · Owner: Refaat (science review), compiled by Yahya + Claude agents · Last reviewed 2026-11-14.

> **14 Nov decision (Yahya):** the app offers only wheat, berseem, maize and sorghum, the crops with reviewed KB
> evidence ([decisions](../decisions.md)). Nothing below reaches farmers. It is a reading list for a future KB release,
> and only if Refaat reviews and accepts each item.

---

## Why this exists

The app offers 8 crops, but the reviewed KB (`sakha-agricultural-review-2026-11-14.1`) has evidence for only 4: wheat,
berseem, maize and sorghum. Rice, faba bean, sugar beet and cotton therefore show no research on the result screen. This
file collects candidate evidence for the other four. Each item is in the **same record shape as the KB evidence**
(`claim`, `locality`, `crop_context`, `units`, `locator`, `limitations`, source title/URL/version, `source_opened`), so
Refaat can transcribe it. Nothing here is in the KB, enforced or approved.

It **adds to** [crop-expansion-assessment.md](../planner/crop-expansion-assessment.md) (Amr + Astra, 14 Nov; rows
RI1–6, SB1–5, CT1–4, FB1–5). Those rows are not repeated here, so read both.

**Same sources as the current KB first.** The KB already cites FAO-56 (`SRC_78fabec1fd8604d7`) and the Global Yield Gap
Atlas, Egypt (`SRC_8bbfb83d46a7befb`). Their rows for the four crops are in §1 and reuse those source IDs. §2–§5 add
new sources of the same kind as the KB's existing ones: peer-reviewed Egyptian field trials (EKB journals), preferably at
Sakha or in Kafr El-Sheikh.

**How each item was read** (`opened` column):
- **Full text:** the page or PDF itself was read, and the locator points into it.
- **Abstract:** EKB (journals.ekb.eg) blocked automated access with a bot page and HTTP 429. The agents read the publisher's
  own abstract word for word through the DOAJ article API or OpenAlex. Refaat must check the full text (tables, pages)
  before sign-off, as for the `Observed (abstract)` rows in the assessment.
- Numbers are copied exactly. Nothing was converted (1 feddan = 4,200 m²).

## 1. Sources already in the KB

### Global Yield Gap Atlas, Egypt, Table 1 (`SRC_8bbfb83d46a7befb`)

> **Citation fix needed:** the URL the KB cites (`https://yieldgap-test.containers.wur.nl/egypt`) is now a "Not found"
> placeholder, and `yieldgap.org/egypt` returns 404. The text was read from Wayback snapshots, which are identical:
> [9 Sep 2024](https://web.archive.org/web/20240909020412/https://yieldgap-test.containers.wur.nl/egypt) and
> [18 Jan 2025](https://web.archive.org/web/20250118115849/https://www.yieldgap.org/egypt). This also affects the
> existing wheat and maize evidence (E036, E037, C14). The KB citation should record the archive URL.

Table caption: "Table 1. Sowing and harvest window for the main crops and cropping systems in the Nile delta and in Upper
Egypt". DAS = days after sowing; EMV / MLMV = early / medium-to-late maturity varieties. Opened: full text (archive).

| Crop | Type | Claim | Exact table cells | Locator | Limitations |
|---|---|---|---|---|---|
| rice | sowing_window | Sowing window. 1 May to 15 Jun | "Rice \| 1 May – 15 Jun. \| EMV: 110-115 DAS MLMV: 120-140 DAS" | Table 1, Nile delta, Rice | Says *sowing*, not transplanting, and gives no transplanting date. Variety not named. |
| rice | duration | Harvest 110–115 DAS (early varieties), 120–140 DAS (medium/late) | same row | Table 1, Nile delta, Rice, harvest column | Counted from sowing. Varieties not named. |
| egyptian_cotton | sowing_window | Sowing window. 15 Apr to 15 May | "Cotton \| 15 Apr. – 15 May \| 160 – 170 DAS" | Table 1, Nile delta, Cotton | Variety not named. |
| egyptian_cotton | duration | Harvest 160–170 days after sowing | same row | Table 1, Nile delta, Cotton, harvest column | Variety not named. |
| sugar_beet | sowing_window | Sowing windows. 1st: 1 Aug to 30 Aug. 2nd: 1 Sep to 30 Sep. 3rd: 20 Oct to 10 Nov | "1st: 01 Aug. – 30 Aug. 2nd: 01 Sep. – 30 Sep. 3rd: 20 Oct. – 10 Nov." | Table 1, Nile delta, Sugar beet | Three staggered windows. |
| sugar_beet | harvest_window | Harvest windows. 1st: 1 Feb to 28 Feb. 2nd: 1 Mar to 31 Mar. 3rd: 1 Apr to 31 May | "1st: 01 Feb. – 28 Feb. 2nd: 01 Mar. – 31 Mar. 3rd: 01 Apr. – 31 May" + comment "The crop is planted three times a year and is harvested based on the needs of factories." | Table 1, Nile delta, Sugar beet, harvest + comments | Harvest is set by the factory, not by crop maturity. |
| faba_bean | — | **Not listed** in Table 1 (no region) | — | — | Needs a local source (§3). |

### FAO-56, chapter 6, Tables 11 and 12 (`SRC_78fabec1fd8604d7`)

Source: [fao.org/4/x0490e/x0490e0b.htm](https://www.fao.org/4/x0490e/x0490e0b.htm), Allen et al. 1998. Both tables are on that page. Opened: full text.
Table 11 footnote: stage lengths "are indicative of general conditions … The user is strongly encouraged to obtain
appropriate local information". Table 12 values are for subhumid climates (RHmin ≈ 45 %, u2 ≈ 2 m/s). Kc mid and end
need climate adjustment (Eq. 62), and footnote 1 applies to every Kc ini (it rises toward 1.0–1.2 with frequent wetting).
None of the values below are adjusted.

| Crop | Type | Claim | Exact cells | Locator | Limitations |
|---|---|---|---|---|---|
| rice | stage_lengths | Initial 30, development 30, mid 60, late 30, total 150 days (planted Dec; May) | "Rice \| 30 \| 30 \| 60 \| 30 \| 150 \| Dec; May \| Tropics; Mediterranean" | Table 11, i. Cereals, Rice, 1st row | Not Egypt-specific. The other row (180 d, May) is Tropics only. |
| rice | standard_kc_references | Initial 1.05, mid 1.20, end 0.90–0.60, max height 1 m | "Rice \| 1.05 \| 1.20 \| 0.90-0.60 \| 1" | Table 12, i. Cereals, Rice | Generic reference. |
| faba_bean | stage_lengths | Initial 20, development 30, mid 35, late 15, total 100 days (planted Mar/Apr) | "… \| 20 \| 30 \| 35 \| 15 \| 100 \| Mar/Apr \| Mediterranean" | Table 11, e. Legumes, Faba bean, broad bean, Mediterranean row | A spring planting, not the Delta's Nov sowing. The Nov rows (235 d dry, 175 d green) are Europe. |
| faba_bean | standard_kc_references | Dry/seed: initial 0.5, mid 1.15, end 0.30. Fresh: 0.5, 1.15, 1.10. Max height 0.8 m | "- Fresh \| 0.5 \| 1.15² \| 1.10 \| 0.8"; "- Dry/Seed \| 0.5 \| 1.15² \| 0.30 \| 0.8" | Table 12, e. Legumes, Fababean (broad bean); footnote 2 | Footnote 2 covers tall-stalk legumes. **Do not use** the "Beans (green) … Calif., Egypt, Lebanon" Table 11 row: that is *Phaseolus*, not faba bean. |
| sugar_beet | stage_lengths | Nov planting. Mediterranean: 45 / 75 / 80 / 30 = 230 days. Arid regions: 35 / 60 / 70 / 40 = 205 days | "45 \| 75 \| 80 \| 30 \| 230 \| November \| Mediterranean"; "35 \| 60 \| 70 \| 40 \| 205 \| November \| Arid Regions" | Table 11, d. Roots and Tubers, Sugarbeet | Generic regions, not Egypt. |
| sugar_beet | standard_kc_references | Initial 0.35, mid 1.20, end 0.70, max height 0.5 m | "Sugar Beet \| 0.35 \| 1.20 \| 0.70⁵ \| 0.5" | Table 12, d. Roots and Tubers; footnote 5 | Footnote 5: Kc end is up to 1.0 if irrigated in the last month. |
| egyptian_cotton | stage_lengths | Initial 30, development 50, mid 60, late 55, total 195 days (planted Mar–May) | "Cotton \| 30 \| 50 \| 60 \| 55 \| 195 \| Mar-May \| Egypt; Pakistan; Calif." | Table 11, g. Fibre Crops, Cotton, 1st row | The only FAO row naming Egypt. Shared with Pakistan and California. |
| egyptian_cotton | standard_kc_references | Initial 0.35 (fibre-crop group), mid 1.15–1.20, end 0.70–0.50, max height 1.2–1.5 m | "g. Fibre Crops \| 0.35"; "Cotton \| \| 1.15-1.20 \| 0.70-0.50 \| 1.2-1.5" | Table 12, g. Fibre Crops header + Cotton row | Kc ini comes from the group header. |

## 2. Sugar beet: Egyptian sources

| # | Type | Claim | Locality / cultivars | Locator | Source | Opened |
|---|---|---|---|---|---|---|
| SB-N1 | trial_sowing_dates | Trial sowing dates. 1 Sep, 1 Oct, 1 Nov. 1 Oct gave the highest root and sugar yields; impurities rose with delay to 1 Nov | Sakha, Kafr El-Sheikh, 2009/10–2010/11; Del 937, Carolla, LP13, Samba, Baraca | Abstract | Al-Labbody 2012, Fayoum J. Agric. Res. & Dev. 26(1):86–92, [doi:10.21608/fjard.2012.194679](https://doi.org/10.21608/fjard.2012.194679) | Abstract |
| SB-N2 | trial_sowing_dates | Trial sowing dates. 1 Sep, 1 Oct, 1 Nov. 1 Sep and 1 Oct gave the highest root and sugar yields, on a par | Sakha ARS, 2008/09–2009/10; Florima, Cleopatra, Heracule, Avantage, Alamas | Abstract | Enan, Abd El-Aal & Shalaby 2011, Fayoum J. Agric. Res. & Dev. 25(2):51–66, [doi:10.21608/fjard.2011.195503](https://doi.org/10.21608/fjard.2011.195503) | Abstract |
| SB-N3 | duration | Harvest ages 180, 195, 210 days tested; 210 days gave the highest sucrose, purity and yields. Early (1 Sep) sowing may need longer than 210 | same as SB-N2 | Abstract | same as SB-N2 | Abstract |
| SB-N4 | trial_sowing_dates | Trial sowing dates. 15 Oct, 15 Nov; harvest at 180 and 210 days. 15 Oct with 210 days was best | Sakha ARS, 2009/10–2010/11; Kawemira, Carolla, Farida | Abstract | Aly 2012, J. Plant Production 3(9):2439–2449, [doi:10.21608/jpp.2012.84990](https://doi.org/10.21608/jpp.2012.84990) | Abstract |
| SB-N5 | trial_sowing_dates | Trial sowing dates. 10 Oct, 25 Nov. 10 Oct gave significantly higher root, top and sugar yields | Sakha ARS, clay, 2003/04–2004/05; cultivar not named | Abstract | Nemeat Alla, Zalat & Badr 2007, J. Plant Production 32(11):8859–8866, [doi:10.21608/jpp.2007.221127](https://doi.org/10.21608/jpp.2007.221127) | Abstract |
| SB-N6 | trial_sowing_dates | Three sowing dates from 17 Aug to 16 Oct (the middle date is not in the abstract). 16 Oct (Santoline) gave the highest root and recoverable-sugar yields; 17 Aug (Steel) gave the highest sucrose | El-Hamoul, Kafr El-Sheikh (Delta Sugar farm), 2020/21–2021/22 | Abstract | Ibraheim et al. 2024, Egyptian Sugar Journal 21, [doi:10.21608/esugj.2024.259521.1047](https://doi.org/10.21608/esugj.2024.259521.1047) | Abstract |
| SB-N7 | local_crop_coefficient_evidence | Seasonal Kc 0.82 / 0.75 / 0.68 (modified Penman), 0.87 / 0.79 / 0.72 (Radiation), 1.3 / 1.19 / 1.08 (modified Blaney) at 3317.6 / 2792.6 / 2267.6 m³/fed | Sakha ARS | Abstract | Abd El-Wahab & Nemeat Alla 2002, J. Soil Sci. & Agric. Eng. 27(3):1943–1953, [doi:10.21608/jssae.2002.253791](https://doi.org/10.21608/jssae.2002.253791) | Abstract |
| SB-N8 | seasonal_water_use | Consumptive use 2560 m³/fed (1.2 CPE) to 1709 m³/fed (0.8 CPE); applied 3150 / 2830 / 2370 m³/fed | Sakha ARS, 2009/10–2010/11 | Abstract | El-Hadidi, Ibrahim & Eid 2012, J. Soil Sci. & Agric. Eng. 3(3):373–387, [doi:10.21608/jssae.2012.53876](https://doi.org/10.21608/jssae.2012.53876) | Abstract |
| SB-N9 | seasonal_water_use | Consumptive use 1878.67 (furrows) and 1818.88 m³/fed (raised beds); applied 2802.00 and 2553.55 m³/fed | Sakha ARS, 2013/14–2014/15 | Abstract | Moursi & El-Mansoury 2015, J. Soil Sci. & Agric. Eng. 6(8):983–999, [doi:10.21608/jssae.2015.42796](https://doi.org/10.21608/jssae.2015.42796) | Abstract |
| SB-N10 | seasonal_water_use | Farmer practice: consumptive use 2381 and 2210 m³/fed; applied 3678 and 3562 m³/fed | Sakha ARS farm, salt-affected soil, 2016/17–2017/18 | Abstract | Zoghdan et al. 2019, J. Soil Sci. & Agric. Eng. 10(1):41–50, [doi:10.21608/jssae.2019.36665](https://doi.org/10.21608/jssae.2019.36665) | Abstract |
| SB-N11 | sowing_window | National calendar: planted Aug–Sep, harvested Mar–Apr; grown mainly in the Delta | Egypt (national) | p. 6 | USDA FAS GAIN, Egypt Sugar Annual EG2023-0006, 24 Apr 2023 ([PDF](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Sugar%20Annual_Cairo_Egypt_EG2023-0006.pdf)) | Full text |
| SB-N12 | harvest_window | National harvest Feb–Mar | Egypt (national) | p. 7 | USDA FAS GAIN, EG2024-0011, 19 Aug 2024 ([PDF](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Sugar%20Annual_Cairo_Egypt_EG2024-0011.pdf)) | Full text |

**Conflicts.**
- **Best sowing date.** The Sakha trials prefer 1 Sep–mid-Oct, and every one found November worse. That range is a
  reading across the trials, not a quoted claim.
- **GYGA** gives three windows from 1 Aug.
- **USDA GAIN.** The 2023 and 2024 reports disagree on harvest (Mar–Apr vs Feb–Mar). Both are trade summaries and rank
  below the trials.
- **Harvest age.** The Sakha trials favour 210 days. FAO's Mediterranean November row totals 230 days.
- **Kc.** SB-N7 values are seasonal and depend on the ET0 method, so they are not FAO-56 stage Kc.

## 3. Rice: Egyptian sources

Rice in the Delta is sown in a nursery and transplanted. GYGA (§1) counts days from *sowing*; the sources below separate
nursery sowing from transplanting where they say so. EKB papers on Sakha rice trials could not be opened (bot block). The
leads are listed under "Not opened".

| # | Type | Claim | Locality / cultivars | Locator | Source | Opened |
|---|---|---|---|---|---|---|
| RI-N1 | transplanting_window | Nursery sowing "within the first 3 weeks of May"; transplant 25–35-day-old seedlings at 20 × 20 cm | Egypt, RRTC Sakha programme; 1990s cultivars (Giza 171–181 era) | Section III, item 1, p. 72 | Badawi 1996, *Rice agronomic research in Egypt*, Cahiers Options Méditerranéennes 15(1):71–76, [PDF](https://om.ciheam.org/om/pdf/c15-1/CI010958.pdf) (same sentence in Badawi 1997, [c24-2/CI011091](https://om.ciheam.org/om/pdf/c24-2/CI011091.pdf)) | Full text |
| RI-N2 | trial_sowing_dates | Trial sowing dates. 20 May, 1 Jun, 10 Jun: 9.33, 7.92, 5.34 t/ha; loss 140 then 260 kg/ha/day | Egypt, RRTC; cultivar, year, site not stated | Table 1, p. 73 | same as RI-N1 | Full text |
| RI-N3 | trial_sowing_dates | Trial sowing dates. 20 Apr, 1 May, 10 May, 20 May (26-day seedlings). 20 Apr gave the highest grain yield, 20 May the lowest | Sakha (RRTC), 2011; Sakha 104, Sakha 105, Hybrids H1, H2 | Abstract (the only page in the file) | Abou Khalifa, *Response of some rice varieties to different sowing dates*, 3rd Int. Conf., Fac. Agric., Benha Univ. (file dated 2012), [PDF](https://mail.fagr.bu.edu.eg/images/Third_International_Conference_Researches/20.pdf) | Full text (abstract page) |
| RI-N4 | trial_sowing_dates | Trial sowing dates. 1 Mar, 20 Mar, 10 Apr, 1 May (30-day seedlings). 1 May is the "typical planting date … without being subjected to cold stress" | Sakha ARS, 2018–2019; 34 genotypes incl. Giza 176/177/179, Sakha 101/104/107 | Methods; Conclusions | El-Refaee et al. 2024, BMC Plant Biol. 24:713, [doi:10.1186/s12870-024-05423-8](https://doi.org/10.1186/s12870-024-05423-8) ([PMC11282823](https://europepmc.org/article/PMC/PMC11282823)) | Full text |
| RI-N5 | trial_sowing_dates | Trial sowing dates. 1 May, 15 May, 30 May (30-day seedlings). 1 May gave the highest hybrid seed yield | Sakha ARS, 2019–2020; restorer lines Giza 178R/179R/181R × CMS | Abstract; Methods §2; Table 4 | Gaballah et al. 2021, Sustainability 13(6):3229, [doi:10.3390/su13063229](https://doi.org/10.3390/su13063229) | Full text |
| RI-N6 | duration | Growth duration: Giza 177 and Sakha 102 120 days; Giza 178 and Sakha 101 135 days; Giza 171 155 days | Egypt, RRTC | §I.1, pp. 39–40 | Badawi & Ghanem 1999, *Water use efficiency in rice culture*, Cahiers Options Méditerranéennes 40:39–45, [PDF](https://om.ciheam.org/om/pdf/c40/CI020442.pdf) | Full text |
| RI-N7 | duration | Broadcast-seeded tanks: Giza 177 124 days, Giza 179 122 days, Sakha 107 127 days (sown 1 and 3 Jun, harvested 3–10 Oct) | Sakha ARS, 2017–2018 | Methods p. 8282; Tables 3, 5, 7 | Darwesh & Hadifa 2020, Plant Archives 20(2):8279–8290, [PDF](https://www.plantarchives.org/20-2/8279-8290%20(7070).pdf) | Full text |
| RI-N8 | duration | Days to 50 % heading (30-day seedlings): Sakha 101 108.33, Sakha 104 101.00, Giza 177 95.00, Sakha 105 95.00 | RRTC farm, Sakha, 2017 | Table 2, parent rows | Abd El-Aty et al. 2022, Saudi J. Biol. Sci. 29(4):2691–2697, [doi:10.1016/j.sjbs.2021.12.054](https://doi.org/10.1016/j.sjbs.2021.12.054) | Full text |
| RI-N9 | duration | FAO country profile: Giza 177 110 days; Sakha 102 120–130; Sakha 101 130–140; Giza 178 140–150. Planting months 4–5, harvest 9–11 | Egypt (national, ~2000) | Egypt profile, variety and cropping-season tables | FAO Rice Information Vol. 3 (2002), [y4347e0o](https://www.fao.org/4/y4347e/y4347e0o.htm) | Full text |
| RI-N10 | seasonal_water_use | Lysimeter ET per season: 697.2 mm (Giza 177), 737.2 (Giza 179), 795.2 (Sakha 107); ET + percolation 1231.1, 1296.4, 1397.4 mm | Sakha ARS, 2017–2018, broadcast-seeded tanks | Tables 3, 5, 7, two-season means | Darwesh & Hadifa 2020 (as RI-N7) | Full text |
| RI-N11 | local_crop_coefficient_evidence | Measured ETa (mm/day), Jun–Sep: 5.0–5.6, 5.0–5.6, 6.1–6.6, 6.2–6.5. The Kc in the same table (1.07, 1.16, 1.19, 1.04) is **FAO's, not measured** | Sakha ARS, 2017–2018 | Table 9; Methods | Darwesh & Hadifa 2020 (as RI-N7) | Full text |
| RI-N12 | seasonal_water_use | Applied water: every 4 days 9 240 (Giza 177), 10 626 (Giza 178), 11 550 m³/ha (Giza 176); RRTC every 3 days 16 200 m³/ha | Egypt, RRTC (cites Nour et al. 1997; RRTC 1996) | Tables 2–3, p. 41 | Badawi & Ghanem 1999 (as RI-N6) | Full text |

**Conflicts.**
- **Sowing.** RRTC's statement is first 3 weeks of May. The trials agree that late May or June is worse, but differ on the
  best early date (20 Apr in RI-N3, 1 May in RI-N4/N5). GYGA says sowing 1 May – 15 Jun.
- **Duration.** It differs by source: Giza 177 is 110 / 120 / 124 days, and Giza 178 is 135 vs 140–150. No source says
  whether it counts from nursery sowing or transplanting. Nothing was found for Sakha 106, Sakha 108 or Hybrid 1.
- **Water.** No locally derived rice Kc was found. Lysimeter ET (697–795 mm) is far below applied water (924–1620 mm,
  converted): ET is not irrigation.
- Existing rows RI1–RI2 (rice is legal only on land in the yearly decree annex) still gate the crop. That is a field
  permission, not agronomy.

**Not opened (EKB bot block; snippets only):** articles 292716 and 357699 (Sakha 2021–22, 12 cultivars, 20 Apr / 10 May /
30 May); 36266, 71515, 46859 (sowing date × genotype, Sakha); 110578 (hybrid seed sowing dates); 2859 (Moursi &
Abdelkhalek 2015, lysimeter ETa ≈ 6 mm/day); 55105 (Sakha Super 300). Sugita et al. 2017, Hydrol. Sci. J. 62:1618,
[doi:10.1080/02626667.2017.1341631](https://doi.org/10.1080/02626667.2017.1341631): eddy-covariance ET for rice and
cotton at Sakha. Its repository was down; it is the best lead for a measured Kc.

## 4. Egyptian cotton: Egyptian sources

| # | Type | Claim | Locality / cultivars | Locator | Source | Opened |
|---|---|---|---|---|---|---|
| CT-N1 | trial_sowing_dates | Trial sowing dates. 25 Apr, 10 May, 25 May. 25 Apr was best; 10 May and 25 May cut yield by 28.1 and 50.1 % (Super Giza 94), 35.5 and 51.3 % (Extra Giza 96), 30.8 and 47.1 % (Super Giza 97) | Sakha Research Station (CRI), clay, preceding crop clover, 2022–2023 | Methods; Results; Table 4 | El-Ashmouny et al. 2026, BMC Plant Biol. 26:162, [doi:10.1186/s12870-025-08076-3](https://doi.org/10.1186/s12870-025-08076-3) ([PMC12849427](https://europepmc.org/article/PMC/PMC12849427)) | Full text |
| CT-N2 | duration | Days from sowing to **second** picking, 1st block: 25 Apr 150/160/156; 10 May 152/162/157; 25 May 143/150/148. 2nd block: 168/173/170; 169/175/171; 165/168/167 (SG94 / EG96 / SG97) | same | Table 5, "NDFS until the second picking" | same | Full text |
| CT-N3 | trial_sowing_dates | Trial sowing dates. 2018: 15 Apr, 28 Apr, 7 May, 17 May, 27 May. 2019: 15 Apr, 25 Apr, 8 May, 18 May, 29 May. The first date was best for most traits; Giza 94 was least affected by delay | Sakha ARS; Giza 86, 92, 94 | English abstract | Ibrahim et al. 2022, J. Adv. Agric. Res. 27(2):449–458, [doi:10.21608/jalexu.2022.147004.1071](https://doi.org/10.21608/jalexu.2022.147004.1071) | Abstract |
| CT-N4 | trial_sowing_dates | Trial sowing dates. 25 Mar, 10 Apr, 25 Apr. 25 Mar gave significantly higher seed-cotton yield | Sakha ARS, 1998–1999; Giza 88 (older cultivar) | Abstract | Ali & El-Sayed 2001, EJAR 79(1):221–232, [doi:10.21608/ejar.2001.397369](https://doi.org/10.21608/ejar.2001.397369) | Abstract |
| CT-N5 | trial_sowing_dates | Trial sowing dates. 15 Apr (normal), 15 May (late). Giza 97, 95, 94 were the most stable under late sowing | Sakha ARS, 2018–2019; Giza 86, 92, 94, 95, 96, 97 | Abstract | Shaker et al. 2020, Menoufia J. Plant Prod. 5(2):91–105, [doi:10.21608/mjppf.2020.170358](https://doi.org/10.21608/mjppf.2020.170358) | Abstract |
| CT-N6 | trial_sowing_dates | Trial sowing dates. 15 Apr, 15 May. 15 Apr significantly increased seed-cotton yield | Sakha ARS, 2013–2014; hybrid Giza 86 × 10229 | Abstract | Abdel-Aal et al. 2015, Fayoum J. Agric. Res. Dev. 29(1):13–26, [doi:10.21608/fjard.2015.191765](https://doi.org/10.21608/fjard.2015.191765) | Abstract |
| CT-N7 | trial_sowing_dates | Trial sowing dates. 15 Apr, 15 May. 15 Apr significantly increased open bolls, boll weight and yield | Sakha ARS, 2018–2019; Giza 96 | Abstract | Deshish et al. 2020, Menoufia J. Plant Prod. 5(12):413–422, [doi:10.21608/mjppf.2020.172384](https://doi.org/10.21608/mjppf.2020.172384) | Abstract |
| CT-N8 | duration | Occupies the land about 6–7 months (maize about 4); most Delta cotton follows temporary berseem, a sizeable share follows faba bean | Egypt (national) | Slide 2; "Planting date" slides | Negm (Cotton Research Institute), *Best practices for high cotton yields in Egypt*, ICAC/ACRDN, 15 Sep 2017, [PDF](https://icac.org/wp-content/uploads/2024/12/2-Md-Negm-Global-Best-Practices.pdf) | Full text |
| CT-N9 | sowing_window | Lower Egypt optimum sowing "from mid-March to the end of May" (CRI agronomist, press quote) | Lower Egypt / Delta | Article body | Parlmany, 30 Jan 2026, [597202](https://www.parlmany.com/News/2/597202/) | Full text |
| CT-N10 | seasonal_water_use | Consumptive use 2629.18 (60 cm furrows) and 2442.74 m³/fed (120 cm beds); traditional irrigation 2917.74 and 2760.81 m³/fed | Sakha ARS, summers 2013–2014 | Abstract | Moursi & Yehia 2016, J. Soil Sci. & Agric. Eng. 7(1):21–34, [doi:10.21608/jssae.2016.39333](https://doi.org/10.21608/jssae.2016.39333) | Abstract |
| CT-N11 | local_crop_coefficient_evidence | Seasonal "crop coefficient" max 0.67 (beds, 80 % FC); minimum consumptive use 1576 m³/fed | El-Karada Water Management Research Station, Kafr El-Sheikh, 2008–2009; Giza 86 | Abstract | Mady et al. 2011, Misr J. Agric. Eng. 28(3):630–649, [doi:10.21608/mjae.2011.104998](https://doi.org/10.21608/mjae.2011.104998) | Abstract |

**Conflicts.**
- **Window.** The GYGA window is 15 Apr – 15 May (§1). The press quote (CT-N9) says mid-Mar to end-May, but it is not a
  peer-reviewed or ARC source. Every Sakha trial found its earliest tested date best, and CT-N1 shows about 50 % yield
  loss by 25 May.
- **Inconsistencies in CT-N1.** The abstract says 15 May where the Methods and tables say 10 May, and Table 5 labels both
  season blocks "2022". This matches existing row CT1.
- **Duration.** GYGA gives 160–170 DAS. FAO-56's Egypt row totals 195 days. CT-N2 runs to the second picking only.
- **Kc.** CT-N11's 0.67 is a single seasonal value with an undefined method. It is **not** an FAO stage Kc. No local stage
  Kc was found; Sugita et al. 2017 (see rice) is the lead.
- **Preceding crop.** CT-N1 (clover) and CT-N8 (berseem, faba bean) both bear on the berseem-cut conflict in UH-001.

**Not opened:** an EKB Kafr El-Sheikh trial reportedly favouring 30 Mar for Giza 94 (article 298159, snippet only); EKB
article 214029 (genotypes bred for sowing in the first week of April); El-Marsafawy et al. 2018, Water 10(9):1168
(CROPWAT for Kafr El-Sheikh, 403); El Sabagh et al. 2018, Open Agric. 3:684 (Giza 94, Sakha; the abstract does not give
the dates).

## 5. Faba bean: Egyptian sources

No official Delta sowing window (ARC/FCRI) was found, and GYGA has no faba bean row. Most Sakha faba bean papers are on EKB
and could not be opened; existing rows FB1–FB5 in the assessment cover several of them from abstracts.

| # | Type | Claim | Locality / cultivars | Locator | Source | Opened |
|---|---|---|---|---|---|---|
| FB-N1 | duration | Growing seasons 17 Nov – 15 May (1999/2000) and 15 Nov – 10 May (2000/2001) | Sakha ARS, furrow irrigation; Giza 461 (old cultivar) | Thesis final abstract, p. 1 | Kassab, *Towards effective water management for some field crops in North Nile Delta region*, Benha Univ. thesis (1999–2001 experiments), [PDF](https://www.bu.edu.eg/portal/uploads/discussed_thesis/finalabsrtract/10797968.pdf) | Abstract (thesis) |
| FB-N2 | seasonal_water_use | Seasonal consumptive use 38.9, 43.4, 45.8 cm (60 cm furrows) and 33.5, 36.8, 39.9 cm (120 cm) at 2.5 / 5.0 / 7.5 cm depth; best-yield treatment 37.3 cm (1568 m³/fed, 1806 kg/fed) | same | Main findings 2-B and 3 | same | Abstract (thesis) |
| FB-N3 | seasonal_water_use | Highest mean consumptive use 1819.3 and 1695.7 m³/fed; applied water 1400.4–2041.9 m³/fed | Sakha ARS; cultivar not named | Abstract | Ibrahim, Abd El-Salam, Abbas & Kassab 2007, Annals Agric. Sci. Moshtohor 45(1):463–468, [record](https://bu.edu.eg/staff/hassanramadan6-publications/7164) | Abstract |
| FB-N4 | seasonal_water_use | Total consumptive use 31.85 cm (Delta), 39.03 (Middle Egypt), 41.73 (Upper Egypt); WUE 0.944 kg/m³ | Egypt, 1979–81 trials | AGRIS abstract | Tawadros et al. 1983, *Water relations*, in Saxena & Stewart (eds), *Faba bean in the Nile Valley*, ICARDA, pp. 87–94, [AGRIS](https://agris.fao.org/search/en/records/6471c41677fd37171a6edb24) | Abstract |
| FB-N5 | local_crop_coefficient_evidence | Blaney-Criddle seasonal coefficient K = 0.58, maximum in March | Egypt, 1979–81 | AGRIS abstract | same as FB-N4 | Abstract |
| FB-N6 | trial_sowing_dates | Trial sowing dates. 1 Oct, 15 Oct, 1 Nov, 15 Nov, 1 Dec. Growth and yield fell when sowing was later than 1 Nov; best at 1 Nov with full irrigation | El-Bosaily, Beheira (north coast, **not Sakha**), drip, 2011/12–2012/13; Sakha 3 | Thesis abstract | Hegab 2015, M.Sc. thesis, Ain Shams Univ., [PDF](https://research.asu.edu.eg/bitstream/12345678/26265/1/G4990.pdf) (journal version = existing row FB5) | Abstract (thesis) |
| FB-N7 | trial_sowing_dates | Trial sowing dates. 25 Oct, 25 Nov. All 11 genotypes performed better at 25 Oct | Bilbeis and Elkhatara (sandy soils, east Delta fringe), 2020–2021; Sakha 1/3/4, Giza 3/843, Misr 3, Nubaria 3/4/5, others | Abstract; Results; Tables 2–4 | El-Abssi et al. 2024, Sci. Rep. 14:9224, [doi:10.1038/s41598-024-59079-3](https://doi.org/10.1038/s41598-024-59079-3) ([PMC11035625](https://europepmc.org/article/PMC/PMC11035625)) | Full text |
| FB-N8 | trial_sowing_dates | Trial sowing dates. 1 Oct, 15 Oct, 1 Nov, 15 Nov. Highest yield at 1 Nov for all four cultivars in both seasons | Tamia, Fayoum (Middle Egypt, non-local), drip; Sakha 1, Giza 3, Nubaria 1, Misr 1 | Abstract; Methods p. 1432 | Tawfik et al. 2018, Middle East J. Agric. Res. 7(4):1431–1443, [PDF](https://www.curresweb.com/mejar/mejar/2018/1431-1443.pdf) | Full text |

**Conflicts.**
- **Sowing.** The opened trials point to about 1 Nov as the best single date, but none is on Sakha clay under furrow
  irrigation. That matches existing rows FB1/FB2 (Sakha, from abstracts). Leave the window `open` until an EKB paper or
  ARC bulletin is read in full.
- **Duration.** It rests on one old Giza 461 trial (about 176–180 days, counted by us from the season dates). Modern
  cultivars (Sakha 1/3/4) are described as earlier, so don't apply it to them.
- **FB-N2 and FB-N3** are probably the same 1999–2001 experiment with different headline numbers. Cite one, not both.
- **Kc.** FB-N5 is a Blaney-Criddle K, not an FAO-56 Kc: never combine it with Penman-Monteith ET0. No local Kc was found.

**Not opened (EKB, highest priority for Refaat):** Attia et al. 2014
([doi:10.21608/jpp.2014.53657](https://doi.org/10.21608/jpp.2014.53657), Sakha, 1 Oct/1 Nov/1 Dec = FB1);
[doi:10.21608/alexja.2019.28568](https://doi.org/10.21608/alexja.2019.28568) (Orobanche, = FB3);
[doi:10.21608/mjppf.2021.169116](https://doi.org/10.21608/mjppf.2021.169116) (= FB2);
[doi:10.21608/sinjas.2022.121008.1092](https://doi.org/10.21608/sinjas.2022.121008.1092) (Sakha, 15 Oct / 15 Nov per snippet);
jssae article 166865 (North Delta consumptive use, 170.2–370.5 mm per snippet); Sakha 1 and Sakha 4 release papers
([doi:10.21608/jpp.2002.254204](https://doi.org/10.21608/jpp.2002.254204),
[doi:10.12816/0011687](https://doi.org/10.12816/0011687)), the likely source for days to maturity.

## What Refaat needs to do

1. Fix the GYGA citation URL to the archive copy (affects existing E036, E037, C14 too).
2. Open the EKB full texts for the items marked "Abstract", and the "Not opened" lists. A normal browser works; only
   automated access is blocked.
3. Choose which items become KB evidence. Where sources conflict (rice duration, cotton window, beet harvest), record the
   conflict rather than averaging.
4. Add the crops to the KB release. The backend's research notes pick up any rule whose `source_text` follows the
   existing patterns (`D Mon to D Mon`, `D Mon, D Mon, D Mon`, `N sowing yielded A and B days`) with no code change;
   other text is shown as "more from the sources".
