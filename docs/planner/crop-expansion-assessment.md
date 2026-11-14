# Crop catalogue expansion assessment (4 → 12 crops)

**Read this if…** you're deciding whether rice, sugar beet, watermelon, strawberry, Egyptian cotton, faba bean, cantaloupe or harankash can enter the planner catalogue.

Status: Proposed, research only, not a runtime release · Owner: Amr + Astra (science review: Refaat) · Last reviewed 2026-11-14.

---

Applies to one field near Sakha, Kafr El-Sheikh. This extends the [evidence ledger](agronomy-evidence.md) and uses its classes
(**Verified / Observed / Assumed / Insufficient Evidence**). Proposed data: [agronomy-kb-extension.v0.2-proposed.json](agronomy-kb-extension.v0.2-proposed.json).
**Approval status (Amr, 2026-11-14): approved for preservation and team review only.** All eight added crops
(rice, sugar beet, watermelon, strawberry, Egyptian cotton, faba bean, cantaloupe, harankash) remain **unapproved**.
None is runtime-eligible, and none produces a verified feasible recommendation. Nothing here activates a rule.
All web research was done on 2026-11-14.

The 12 catalogue crops are not the four planning seasons. A plan still has exactly four seasons, chosen from the catalogue.

## 1. Verdicts

| Crop | Verdict | Why, in one line |
|---|---|---|
| Sugar beet | **Research-only, best local evidence** | Three Kafr El-Sheikh/Sakha trials, read in full, agree on mid-Sep to early-Oct sowing and mid/late-April harvest. Release depends on factory delivery. |
| Faba bean | **Research-only, best local evidence** | Several Sakha ARC trials put the optimum at 1 Nov. Sakha 1 was bred for faba → cotton in Kafr El-Sheikh. No absolute harvest date. |
| Egyptian cotton | **Research-only, best local evidence** | A Sakha 2022–23 trial gives sowing 25 Apr–25 May and second picking 143–175 d. An official variety map exists. A legal uprooting deadline exists but current enforcement is unverified. |
| Rice | **Research-only, legally gated** | RRTC Sakha trials agree on an early-May nursery and 25–30 d seedlings. Legal only on land in the yearly decree annex (2026: Decree 32/2026), which is unpublished per village. |
| Watermelon | **Research-only, national scope** | National guidance only (sowing mid-Feb to mid-Apr, 3–4-year wilt rotation). Sakha trials are for seed watermelon, with no dates. |
| Strawberry | **Research-only, poor local fit** | National calendar is Sep/Oct → May. No open-field Kafr El-Sheikh evidence. FAO rates it salt-sensitive. It spans the summer→winter boundary. |
| Cantaloupe | **Cannot be represented responsibly yet** | Grown in Kafr El-Sheikh (Sidi Salem 2005–06, Sakha 2012–13), but no accessible local planting, harvest or release date. |
| Harankash | **Cannot be represented responsibly yet** | Egyptian sources use the name for *Physalis peruviana* **and** *P. pubescens/pruinosa/longifolia*. No local trial, harvest end or release found. |

None of the eight has evidence that can make a plan `feasible` today. That is the same position as the original four ([§4](#4-baseline-comparison-with-the-original-four)).

## 2. Evidence matrix

IDs are proposed ledger keys. **Read** means the full text was read on 2026-11-14. **Abstract** or **snippet** means only that was accessible.
Egyptian journal pages (journals.ekb.eg), ScienceDirect, ResearchGate and FAOLEX were blocked for automated access, so many trial
records are abstract-only and must be re-read by Refaat before use.

### Rice (*Oryza sativa*), proposed `rice`, purpose `grain`

| ID | Class | Source says | Source | Limit |
|---|---|---|---|---|
| RI1 | Verified (legal, secondary report of Gazette text) | Decree 32/2026 (Ministry of Water Resources and Irrigation): 724,200 fed permitted; rice banned outside permitted areas (Law 147/2021). Village lists are in annexes not published in the article. | [Sada El-Balad, 23 Apr 2026](https://www.elbalad.news/6946667) | Field legality unknown without the annex. Year-specific. |
| RI2 | Verified (official statement via news) | Kafr El-Sheikh is one of 9 governorates. Rice only on two-turn rotation canals. Kafr El-Sheikh irrigation rotation runs 15 Apr–15 Aug 2026. | [Youm7, 27 Apr 2026](https://www.youm7.com/story/2026/4/27/7392094) | The rotation window is an **irrigation** window, not sowing. Re-check each year. |
| RI3 | Observed (read) | RRTC Sakha 2024 and 2025: nursery sown 2 May; 30-day seedlings transplanted; Giza 178, Super 302, Giza 183. | Front. Plant Sci. 2026, [PMC13352156](https://europepmc.org/article/PMC/PMC13352156), Methods | One trial. No harvest date extracted. |
| RI4 | Observed (read) | RRTC trials 2021–22: seedbed in May, transplanted after 25 d. Sakha 2016–17: transplanted at 30 d. | [PMC10780751](https://europepmc.org/article/PMC/PMC10780751); [PMC9072890](https://europepmc.org/article/PMC/PMC9072890), Methods | Nursery age recurs at 25–30 d. Not an official rule. |
| RI5 | Observed (snippet) | Giza 179 total duration is given as 135 d in one source and 122–125 d in another. | journals.ekb.eg article_302950 (blocked) | **Conflicting.** No duration may be used. |
| RI6 | Insufficient Evidence | Harvest date, drain-before-harvest, straw handling (burning banned), release, preparation. | — | Must stay unknown. |

### Sugar beet (*Beta vulgaris*), proposed `sugar_beet`, purpose `sugar`

| ID | Class | Source says | Source | Limit |
|---|---|---|---|---|
| SB1 | Observed (read; spot-checked) | Al-Hamul, Kafr El-Sheikh, 2021/22–2022/23, saline clay, cv. Pleno, sown after maize in the first week of October, harvested 27 Apr 2022 and 24 Apr 2023. The text also says "after 180 days", which conflicts with the dates (~202–208 d). | El-Sharkawy et al., PeerJ 2025, [PMC12182053](https://europepmc.org/article/PMC/PMC12182053), Methods, Table 1 | Use the dates, not "180 d". One trial. |
| SB2 | Observed (read) | Kafr El-Sheikh, 2022/23–2023/24, salt-affected clay, cv. Pleno, first week of October, harvest "180 days … in late April". | PLoS One 2026, [PMC12928445](https://europepmc.org/article/PMC/PMC12928445), Methods | Same day-count mismatch. |
| SB3 | Observed (read) | Sakha ARS, 2022/23–2023/24, ~53% clay, cv. BTS SMART 8565, sown mid-September, harvested 210 days later. | BMC Plant Biol. 2026, [PMC13539709](https://europepmc.org/article/PMC/PMC13539709), Methods | Inference: harvest about mid-April. |
| SB4 | Observed (snippet) | SCRI bulletin: roots are pulled, piled and covered with tops until factory delivery. Delta Sugar receives beet until end of June. 2026: state companies reportedly halted customary contracts. | Akhbar El-Yom and Al-Mal snippets (blocked) | Release = harvest + **unknown** delivery lag. Contract availability uncertain. |
| SB5 | Observed (snippet, greenhouse) | *Heterodera* beet-cyst nematodes in Kafr El-Sheikh on beet relatives. Greenhouse reproduction on berseem. | journals.ekb.eg article_128309 (blocked) | Possible berseem link. Not a rotation rule. |

### Watermelon (*Citrullus lanatus*, fresh fruit), proposed `watermelon`, purpose `fresh_fruit`

| ID | Class | Source says | Source | Limit |
|---|---|---|---|---|
| WM1 | Verified (national extension) | Main summer planting is sown mid-Feb to mid-Apr. The nili planting is late May–June after faba bean. Harvest continues 1–1.5 months. | Hassan 2005, Cairo Univ. extension bulletin, pp. 5 and ~11 ([third-party copy](https://archive.org/download/HorticulturalCropsFertilizationBasics/)) | Not North-Delta-specific. Some digits in the copy are illegible and were not used. |
| WM2 | Verified (national extension) | Heavy soil acceptable only if well drained and "free of salts". Wilt control includes a **3- or 4-year rotation**. | Hassan 2005, pp. 4–5 and ~19 | Saline Sakha clay fails the stated condition unless drainage and salinity are confirmed. |
| WM3 | Observed (read) | Sakha station 2009–2010: grafted **Nubian (seed) watermelon**, surface irrigation. Kafr El-Sheikh has more than a quarter of the national Nubian watermelon area. No calendar dates. | [Abd Alla et al. 2012](https://sci.tanta.edu.eg/files/7-13-Effect%20of%20grafting%20Nubian%20watermelon%20on%20its%20growth,%20flowering,%20yield%20and%20fruit%20quality.pdf), M&M | Seed crop, not fresh fruit. |
| WM4 | Observed (abstract) | Kafr El-Sheikh 2011–12, seed watermelon sown 1 and 15 Apr had less whitefly than May sowings. | Mousa 2017, EAJBS 10(8) (blocked) | Seed crop, pest trial. |

### Strawberry (*Fragaria × ananassa*), proposed `strawberry`, purpose `fresh_fruit`

| ID | Class | Source says | Source | Limit |
|---|---|---|---|---|
| ST1 | Verified (extension) | Egypt: frigo plants set early Sep–mid Oct and fruit mid-Feb until May. Fresh plants set at the same time fruit from early November. | [EL-Borai & Whitaker, UF/IFAS HS1411](https://edis.ifas.ufl.edu/publication/HS1411), p. 2 | National. No harvest end for fresh plants, no removal date. |
| ST2 | Verified (peer-reviewed review) | Transplanted Sep–Oct as a winter crop, "last in soil … till May". Rotated with cotton, soybean, maize, peanut. At least 2 years before replanting strawberry. Avoid heavy, wet soils. | [Abd-Elgawad 2019, Bull. NRC 43:7](https://doi.org/10.1186/s42269-019-0049-2), pp. 8–11 | "May" is a month, not a release date. |
| ST3 | Verified (FAO table) | Salt-sensitive: ECe 1.0 dS/m at 100% yield potential. | [Ayers & Westcot, FAO I&D 29, Table 4](https://www.fao.org/4/t0234e/T0234E03.htm) | General table. Comparable only with a field ECe by the same method. |
| ST4 | Observed (abstract) | Kafrelsheikh University strawberry trials found were **protected** (tunnels/greenhouse), not open field. | [doi:10.21608/jsas.2016.2956](https://doi.org/10.21608/jsas.2016.2956) | No open-field local evidence. |

### Egyptian cotton (*Gossypium barbadense*), proposed `egyptian_cotton`, purpose `fibre`

| ID | Class | Source says | Source | Limit |
|---|---|---|---|---|
| CT1 | Observed (read; spot-checked) | Sakha station, 2022–2023, Super Giza 94 / Extra Giza 96 / Super Giza 97, sown 25 Apr, 15 May, 25 May (the discussion says "10th May"). Preceding crop clover. Clay 50.6%, EC 1.90 dS/m. Harvest at "beginning of October". Recommends 25 Apr. | El-Ashmouny et al., BMC Plant Biol. 2026, [PMC12849427](https://pmc.ncbi.nlm.nih.gov/articles/PMC12849427/), Methods, Conclusions | One trial. Internal date inconsistency. |
| CT2 | Observed (read) | Days from sowing to **second** picking: 143–162 and 165–175 (both table blocks labelled 2022). Total pickings not stated. | Same paper, Table 5 | Range only. |
| CT3 | Verified (news report of official map) | 2026 variety map: Extra Giza 96 in Fuwwah, Mutubas and parts of Sidi Salem/Desouk; Super Giza 94 in the rest of Kafr El-Sheikh. Seed via cooperatives per the map. | [Maspero, 1 Mar 2026](https://www.maspero.eg/economy/2026/03/01/932357/) | Field markaz decides cultivar. Not the decree text. |
| CT4 | Verified (legal summary, snippet) | Resolution 1472/1994: uproot cotton before **1 Nov**; dispose of/burn stalks by 1 Feb. Resolution 1229/1998: strip bolls before uprooting. | FAOLEX via [LEAP](https://leap.unep.org/en/countries/eg/national-legislation/resolution-no-1472-1994-concerning-uprooting-cotton-shrubs-flax) (403) | Possible legal release ceiling. **Current enforcement unverified.** |

### Faba bean (*Vicia faba*, ful baladi), proposed `faba_bean`, purpose `grain`

| ID | Class | Source says | Source | Limit |
|---|---|---|---|---|
| FB1 | Observed (abstract) | Sakha ARS 2011/12–2012/13: sown 1 Oct, 1 Nov, 1 Dec. Recommends Sakha 4 sown 1 Nov plus 2 irrigations at 30 and 90 d, "Sakha district". | Attia et al. 2014, [doi:10.21608/jpp.2014.53657](https://doi.org/10.21608/jpp.2014.53657) | Trial recommendation. No harvest date. |
| FB2 | Observed (abstract) | Sakha ARS 2018–2020: 1 Oct sowing raised chocolate spot and rust compared with the 1 Nov optimum. | [doi:10.21608/mjppf.2021.169116](https://doi.org/10.21608/mjppf.2021.169116) | Supports 1 Nov. |
| FB3 | Observed (abstract) | Sakha ARS, Orobanche-infested fields: 30 Nov sowing reduced broomrape. The yield direction in the abstract is ambiguous. | [doi:10.21608/alexja.2019.28568](https://doi.org/10.21608/alexja.2019.28568) | Field infestation status matters. |
| FB4 | Verified (cultivar release, abstract) | Sakha 1 (2001): early; matures ~24 d before Giza 461; bred to precede cotton instead of berseem; demonstrated in Kafr El-Sheikh. | [doi:10.21608/jpp.2002.254204](https://doi.org/10.21608/jpp.2002.254204) | Relative maturity only. |
| FB5 | Observed (abstract) | The supplied lead (Hegab et al. 2014) is El-Bosaily on the north coast, drip-irrigated, not Sakha. Sowing later than 1 Nov reduced yield. | [doi:10.1016/j.aoas.2014.11.004](https://doi.org/10.1016/j.aoas.2014.11.004) | Different site and irrigation. |

### Cantaloupe (*Cucumis melo*), not added to the proposed KB

| ID | Class | Source says | Source | Limit |
|---|---|---|---|---|
| CA1 | Observed (read) | Sidi Salem, Kafr El-Sheikh, summers 2005–2006, cv. Ananas F1. No dates, no soil texture. | [Kafrelsheikh Univ. thesis abstract](https://kfs.edu.eg/engkfs/display.aspx?topic=2129) | Presence only. |
| CA2 | Observed (abstract) | Sakha ARS 2012–2013, furrow cut-off irrigation on clay. | [doi:10.21608/jssae.2014.49842](https://doi.org/10.21608/jssae.2014.49842) | No dates or cultivar seen. |
| CA3 | Assumed (news, unverified) | A news article attributes "July for Lower Egypt" and "sensitive to soil salinity" to an HRI report. | aboutmsr.com, 13 Feb 2025 | Primary report not found. |

Other dated cantaloupe evidence is from Assiut, reclaimed Menofia sand or a Damietta pest study, so it isn't transferable. The cultivar group is unspecified.

### Harankash (*Physalis* spp.), not added to the proposed KB

| ID | Class | Source says | Source | Limit |
|---|---|---|---|---|
| HK1 | Verified (bibliographic) | Arabic "الحرنكش" = *P. peruviana* in a Qalyubia pest study, 2012–13. | Afsah 2015, [doi:10.21608/assjm.2015.109818](https://doi.org/10.21608/assjm.2015.109818) | Entomology only. |
| HK2 | Observed (read) | *P. pubescens*, Qalyubia clay loam, furrow irrigation, 2011–13: seedbed 5 Jul, transplanted after 40 d. Harvest end not stated. | [Helaly et al. 2017, APAR 6(5)](https://medcraveonline.com/APAR/effect-of-polyethylene-mulching-type-on-the-growth-yield-and-fruits-quality-of-physalis-pubescens.html) | One trial, different species from HK1. |
| HK3 | Observed (abstracts) | Egyptian papers attach the name to *P. peruviana*, *P. pubescens*, *P. pruinosa* and *P. longifolia*. | [doi:10.21608/jfds.2019.58150](https://doi.org/10.21608/jfds.2019.58150); [doi:10.21608/jpp.2003.252516](https://doi.org/10.21608/jpp.2003.252516); [doi:10.21608/jalexu.2014.160520](https://doi.org/10.21608/jalexu.2014.160520) | **Species identity unresolved.** |

**Alternative to harankash.** Summer tomato is the only North-Delta annual fruit found with a local dated trial: Kafr El-Sheikh, saline clay (EC 2.56 dS/m), transplanted 7–9 Mar 2017/18, ripening 70–90 d after transplanting ([Bard et al. 2021](https://fagr.stafpu.bu.edu.eg/Horticulture/1163/publications/Mustafa%20Hamza%20Mohamed%20Mohamed_ASSJM_Volume%2059_Issue%202_Pages%20875-886.pdf)). The final harvest and release aren't stated, and it is Solanaceae like *Physalis*. It is a research lead, not a recommendation.

## 3. Cross-crop findings (inference, labelled)

- **Release and preparation is the universal gap.** No source for any of the eight states the first free day or the preparation days before the next crop. This is the same gap as T1 in the ledger.
- **Long and spanning occupancy.** Cotton occupies the field from late April/May to October–November. Strawberry runs from Sep/Oct to May. Sugar beet runs from Sep/Oct to late April, with deliveries possibly later. Inference: each of these constrains its neighbouring seasons. The planner handles this through dates and occupancy checks (verified synthetically, §5).
- **Permission gates are not agronomy.** Rice legality (decree annex), the cotton variety by markaz, the cotton stalk deadline and beet factory contracts are field facts to confirm. They are not crop rules.
- **Multi-year rotation intervals** come from national or review sources: cucurbits 3–4 years for watermelon wilts, strawberry at least 2 years. The planner can't evaluate these without field history (§5).
- **Salinity.** Strawberry (FAO "sensitive") and watermelon ("free of salts") conflict with typical saline Sakha clay unless the field's ECe and drainage are measured. Rice and sugar beet trials were run on salt-affected local soils, but no threshold may be encoded from them.

## 4. Baseline comparison with the original four

| Crop | Best evidence (ledger) | Same gap as new crops? |
|---|---|---|
| Wheat | W1 Verified window 15–30 Nov; W2 cultivar map | Yes: no release or preparation |
| Berseem | B1 Verified qualitative; B2 Observed Sakha cut offsets | Yes |
| Grain maize | M1 Verified May window; M2/M3 Observed | Yes |
| Grain sorghum | S1 Observed Sakha trial; S2 cultivar metadata | Yes |

Sugar beet, faba bean, cotton and rice now have local trial evidence comparable to sorghum and maize. Watermelon and strawberry are weaker than all four originals. Cantaloupe and harankash are weaker still.

## 5. Planner compatibility (tested synthetically, 2026-11-14)

Probe: a scratchpad script ran the real Milestone 2 code (`planner/candidate-generation` @ `de081ab`) with 12 catalogue crops and SYNTHETIC rules. No repo code or tests were changed.

| Question | Finding | Code change? |
|---|---|---|
| Can crops be added? | Yes. The catalogue is data-driven, and no crop IDs appear in production code. | No |
| Profile binding | **Purpose is fixed per season** (spec: "keep purpose … fixed"). Offering all 12 crops to a `grain` season evaluated only the 5 grain crops; 7 were blocked (`profile_binding_unavailable`). Swapping a grain crop for sugar beet, cotton or fruit needs a spec decision to allow purpose changes. | Policy decision |
| Coverage checks | A crop without rules is honestly `needs_review` or blocked, and the search reports `incomplete / uninstantiated_choices`. | No |
| 256 budget | 12 crops in all four seasons is 20,735 raw combinations. The budget ran out during single-season edits, and **blocked combinations consume budget**. Reported correctly as `incomplete / candidate_budget`. | Policy decision (budget, or pre-filter unsupported values) |
| Spanning crops | A winter crop released after the next summer sowing is `rejected` (`field_occupied`). Season labels set order only, so a "winter" crop sown in September is structurally allowed. | No; Yahya/Refaat must agree the slot convention |
| Multiple pickings | One `harvest_or_cut_date` (final) plus `release_date` per season. Intermediate pickings aren't modelled; they're not needed for occupancy. | No |
| Date invalidation | Crop, profile and sowing changes reset endpoints; rebuilt only from exact calendars or templates (existing behaviour). | No |
| Permission gates | Expressible as review `FactRule`s on field facts (e.g. `field.rice_permitted`). Needs adapter field-fact mapping. | No code; contract mapping |
| Multi-year intervals | `RotationRule` checks only the immediate predecessor inside the four seasons. Field history before season 1 isn't an input. | **Yes, if required** (input/contract + evaluator) |
| Versioning | Adding catalogue profiles changes all candidate IDs (evidence digest), so a new `data_release` is needed. | No; release process |

## 6. Activation checklist

The four levels are separate approvals; reaching one never implies the next.

| Crop | L1 research catalogue entry | L2 runtime after Refaat + Yahya review | L3 supported candidate choices | L4 can join a verified feasible rotation |
|---|---|---|---|---|
| Sugar beet | Ready (proposed file) | After Refaat re-reads SB1–SB3 and the SCRI window | Needs an approved sowing window or exact calendar | Needs release (delivery lag), preparation, field EC, contract |
| Faba bean | Ready | After the Sakha 4 release paper / ARC bulletin is read | Needs a verified window rule | Needs a harvest date per cultivar, release, preparation, Orobanche status |
| Egyptian cotton | Ready | After current decree texts are verified | Needs a window rule plus markaz → variety | Needs last picking, stalk removal, release, preparation |
| Rice | Ready (marked legally gated) | After the decree annex process is defined | Needs a field-legality fact and a verified cultivar duration | Needs harvest, straw handling, release, preparation |
| Watermelon | Ready (national scope flagged) | After a North-Delta fresh-fruit source is found | Not yet | Needs field ECe/drainage, cucurbit history (multi-year), release |
| Strawberry | Ready (poor-fit flagged) | After open-field local evidence | Not yet | Needs ECe, removal date, slot convention |
| Cantaloupe | **Not ready** | — | — | — |
| Harankash | **Not ready** (species unresolved) | — | — | — |

## 7. Team impact

- **Refaat.** Re-read every abstract-only or snippet item at the source; EKB was inaccessible to us. Approve or reject each assertion and its class. Obtain the RRTC/SCRI/HRI/ARC bulletins (rice cultivar durations, beet window, faba maturity, cantaloupe and watermelon North-Delta calendars). Decide the harankash species. Merge with your KB loader work without overwriting it.
- **Mahmoud.** Replay needs crop-specific stage calendars before any Tmax/ET0 exposure is shown. The only stated heat concern is cotton at Sakha (CT1: monthly Tmax 37–41 °C Jun–Sep; "late planting exposes cotton to heat stress"); no threshold is approved. FAO-56 Kc values exist for watermelon and cantaloupe but are non-Egyptian.
- **Yahya.**
  - Catalogue loading of new `crop_id`s and purposes (`sugar`, `fibre`, `fresh_fruit`) into a new `data_release`.
  - Field-fact mapping for permission gates: rice permitted, cotton markaz, beet contract.
  - A slot convention for crops spanning seasons.
  - Arabic/English names and icons in the API/frontend.
  - No shared-schema change is proposed here.
- **Amr.**
  - Decide the policy questions: purpose-change exploration, search budget/pre-filtering, multi-year rotation input.
  - When a release is loaded, run the 84 regressions plus UH-001.
  - Add a fixture with ≥5 catalogue crops to confirm honest `incomplete` reporting.
- **Moaaz.** Imagery and voice assets for any crop that reaches L1. Harankash needs a confirmed species before its imagery is chosen.

## 8. Gaps, blockers and next actions

1. **Blocker for all eight:** no field-release or preparation evidence.
2. **Rice:** the Decree 32/2026 annex for the field's village; settle the Law 147/2021 penalty articles; get RRTC cultivar durations.
3. **Cotton:** the decree text for the 2026/27 variety map; whether the 1994/1998 stalk rules are enforced now; picking count.
4. **Sugar beet:** the official SCRI sowing window; delivery lag; 2026/27 contract availability.
5. **Faba bean:** absolute maturity and harvest dates for Sakha 1/Sakha 4 (Omer et al. 2014 release paper).
6. **Watermelon / cantaloupe:** an HRI North-Delta calendar for fresh fruit; the cantaloupe cultivar group.
7. **Strawberry:** open-field Delta clay evidence; removal date.
8. **Harankash:** which species the farmer means; any North-Delta calendar. Otherwise drop it, or study tomato as a research lead.
9. **Farmer inputs** for any real plan: field ECe and drainage, markaz, rice permission, factory contract, cucurbit and strawberry history, Orobanche/nematode history.
