# Uncle Hussein — reference scenario UH-001

Working fixture, 11 November 2026. **Uncle Hussein is fictional.** No interview, field measurement, crop result or farmer validation is implied. This complete input fixture tests the approved product; it is not a complete agronomic recommendation. Use [PRODUCT.md](PRODUCT.md), [SCIENCE.md](SCIENCE.md) and [DATA_SPEC.md](DATA_SPEC.md) unchanged.

## 1. Exact intake

Opening request: **“أنا محتاج البرسيم للمواشي لحد حشة عشرين مايو، وعايز أزرع ذرة حبوب، وبعدها قمح. ورّيني إيه اللي ينفع يتغيّر من غير ما أخسر الحشة.”**

English equivalent: “I need the berseem for my livestock through the 20 May cut. I want grain maize and then wheat. Show me what can change without losing that cut.” The year must be asked and confirmed; this fixture supplies 2027.

| Input | Exact fixture value | Evidence status |
|---|---|---|
| Scenario version | UH-001/v1; issue date 2026-11-11 | Illustrative |
| Locality | Sakha, Kafr El-Sheikh; weather query 31.10 N, 30.95 E | Approved research locality; not parcel coordinates |
| Field | One field, 1.00 hectare; no subdivision or intercropping | Illustrative assumption |
| Language | Egyptian Arabic; English switch available | Requirement |
| Reading/access | Farmer needs audio/pictures; help may be requested | Illustrative user need, not tested usability |
| Soil | Farmer reports heavy/clayey soil; no laboratory record | Illustrative report; unverified |
| Salinity, pH, drainage, water table | Unknown | Must remain unknown |
| Water | Irrigation-dependent; delivery dates, volumes and reliability unknown | Illustrative report; unresolved feasibility input |
| Feed requirement | Protect berseem occupation and final cut on 2027-05-20 | Illustrative hard commitment |
| Feed quantity | Unknown; do not infer herd needs or biomass | Open |
| Grain commitments | Grain maize in season 2 and grain wheat in season 3 | Illustrative hard crop/purpose locks |
| Preparation interval | 7 full days after release, same field | Explicit fixture assumption, not a local recommendation |
| Priorities | Preserve hard commitments; then minimize changes; then understand demand and sequence trade-offs | Illustrative confirmed order |
| Permitted exploration | Season-2 sowing: 2027-05-28 or 2027-06-01; season-4 grain sorghum may be explored against grain maize | Permission to investigate, not agricultural approval |
| Other changes | No season-1 shortening, crop-purpose change or relaxation of locks without new confirmation | Requirement |

All fixture facts must be spoken back, including “واحد هكتار”, “سبع أيام تجهيز” and full dates. Do not silently translate hectares into feddans. Confirm the unit or explain a sourced conversion first. Speech extraction produces proposed fields; confirmation creates the structured fixture.

## 2. Four-season current plan P0

Dates below are exact **farmer-intended fixture dates**. A crop end is exclusive: a harvest/cut on 20 May gives an assumed first free date of 21 May. Actual removal time is unverified. The seven-day preparation interval begins on that release date.

| Season | Crop and purpose | Intended sowing | Intended harvest/final cut | Assumed release | Status |
|---|---|---|---|---|---|
| 1: winter 2026/27 | Multicut berseem for livestock; Sakha 4 profile candidate | 2026-11-01 | **2027-05-20, protected** | 2027-05-21 | Illustrative schedule; cutting/yield unvalidated |
| 2: summer 2027 | Grain maize; Single Hybrid 10 profile candidate | 2027-05-15 | 2027-09-20 | 2027-09-21 | Crop/purpose protected; schedule copied as an illustrative calendar pattern |
| 3: winter 2027/28 | Grain wheat; Giza 168 profile candidate | 2027-11-20 | 2028-04-25 | 2028-04-26 | Crop/purpose protected; maturity/availability require review |
| 4: summer 2028 | Grain sorghum; cultivar unknown | 2028-06-01 | 2028-09-21 | 2028-09-22 | Intended catalogue entry; Sakha suitability unresolved |

A published Sakha trial observed Giza 168 wheat on 20 November 2015–25 April 2016 and Single Hybrid 10 maize on 15 May–20 September 2016. Repeating those dates in later years is an **assumption**, not a verified duration rule. Its saline experimental soil must not be assigned to Hussein's field. [Aiad 2019, pp. 149–150](https://jenvbs.journals.ekb.eg/article_54170_dd3f51abb5d4b2a15ee54215c93d8298.pdf).

The sorghum calendar resembles a **Nubaria** study, not Sakha validation. [Primary study](https://link.springer.com/article/10.1186/s42269-019-0155-1). FAO supports the distinction between multicut and single-cut berseem and identifies Delta cultivars; it does not establish Hussein's particular cutting schedule. [FAO Egyptian Clover, pp. 65–68](https://www.fao.org/4/i3500e/i3500e.pdf).

## 3. Expected Promise Test

**P0 is rejected for an explicit same-field timing conflict.** Maize sowing on 15 May precedes the protected berseem cut on 20 May. Under the assumed release/preparation convention, the first calendar-compatible next sowing is **28 May 2027**: 21 May plus seven days. This is calendar arithmetic, not an agronomic planting recommendation or executed planner result.

The season-2→3 and season-3→4 dates do not overlap under the stated fixture assumptions. Do not invent a conflict in those seasons. Changing season-2 sowing invalidates its assumed harvest/release; later checks must be rerun once an applicable maturity mapping exists. No arbitrary fixed duration may silently preserve the old harvest date.

Also return review reasons for soil/drainage, irrigation availability, crop stages, cultivar availability, sorghum eligibility and forage quantity. A crop commitment can be retained without proving grain yield or sufficient livestock feed.

Spoken explanation: **“ميعاد الذرة يوم خمستاشر مايو جاي قبل حشة البرسيم اللي حضرتك ثبّتها يوم عشرين مايو. مش هنلغي الحشة. حسب فرضية التجهيز اللي أكدناها، الأرض ممكن تبقى جاهزة من تمانية وعشرين مايو، بس لسه لازم نراجع مناسبة الزراعة في الميعاد ده.”** Speak the year in the detailed confirmation.

## 4. Alternatives: honest expected result

**Validated feasible alternatives available from this fixture: zero.** Do not populate two recommendation cards merely to fill the screen. These two permitted investigations may be shown separately as **requires review**, with audio labels:

| Investigation | Exact change | Why consider it? | Why not yet feasible/validated? |
|---|---|---|---|
| R1 — timing variant | Season-2 maize sowing 2027-05-28; keep all locks and other intentions | Removes the explicit first overlap under the seven-day assumption; within the bulletin's broad May preference | No verified shifted maturity/release, field applicability or complete four-season profile |
| R2 — timing sensitivity | Season-2 maize sowing 2027-06-01; keep all locks and other intentions | Farmer permitted this date; can expose demand/duration trade-offs if applicability is established | Current old-land guidance prefers May; June is not automatically impossible, but the available evidence does not validate this repair |

The old-land maize preference is guidance, not a hard biological cutoff. [ARC bulletin 1429/2023, pp. 4–5](https://misrelzraea.com/wp-content/uploads/2024/03/%D9%86%D8%B4%D8%B1%D8%A9-%D8%A7%D9%84%D8%B0%D8%B1%D8%A9-%D9%86%D9%87%D8%A7%D8%A6%D9%89-copy_compressed.pdf). R1/R2 are both timing variants, not distinct crop rotations. Investigating season-4 grain maize instead of grain sorghum is permitted, but remains uninstantiated until supported dates and profiles exist. Do not combine unsupported changes into a supposedly valid plan.

## 5. NASA comparison and ML behavior

Once complete, traceable profiles exist, replay P0 and permitted variants over the same eligible consecutive historical blocks. Show crop-period ET0, conditional ETc, temperature exposure, duration, crop-free gaps and protected grain/forage commitments together. Weather may reveal a different atmospheric-demand exposure after a date shift; **no direction, amount, winner or ranking reversal is asserted here**. P0 remains labelled conflicted. Missing stages suppress unsupported ETc totals; unknown crop heat thresholds preclude crop-risk claims.

At the fixture issue date, the disputed May 2027 sowings are outside the next seven days. Expected ML state: **not applicable to this choice**. The four-season flow continues normally. No future seven-day forecast is fabricated. A later near-term test requires its own issue-time inputs, permitted dates and fresh evaluation protocol.

## 6. Expected completion and recovery

Hussein can save the confirmed intentions and unresolved checks as a **review-required draft**, not approve them as a validated feasible recommendation. Takeaway:

**“حشة البرسيم يوم عشرين مايو محفوظة في الخطة. ميعاد الذرة الحالي متعارض معاها. عندنا مواعيد ممكن نراجعها، لكن مفيش بديل مؤكد لسه. هنحتفظ بخطتك وبالنقط اللي محتاجة مراجعة.”**

The English Evidence Card must carry the same scenario/version, locks, dates, conflict, assumed seven days and missing evidence. Switching language preserves facts. Failed recognition offers repeat and picture/audio choices, then typing or adviser assistance; silence never confirms. Changing the preparation interval or a lock invalidates dependent comparisons. With no adviser available, “requires review” remains unresolved rather than becoming approval.

Acceptance fixture: P0 rejected; R1/R2 require review; zero validated repairs; protected forage retained; no invented later collision, crop-water result or forecast; identical bilingual meaning; core flow works with ML unavailable. These expected outcomes have **not** been run through an implemented planner.
