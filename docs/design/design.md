# MISSION EL GHEET — Season Path design foundation

**Read this if…** you're designing or building any screen: interaction, accessibility, status language, components.

Status: Approved ; **§2 colours/type superseded by [Fieldlight](fieldlight.md)** · Owner: Amr. Last reviewed .

**Approved direction (11 Nov):** Season Path / سكة المواسم, "Show, Speak, Choose, Confirm". Rendered quality and farmer usability are not yet tested.

Related: [product](../product/product.md), [UH-001](../product/reference-scenario.md), [architecture](../backend/architecture.md), [API](../backend/api-contracts.md), [science](../science/science.md), [status](../status/design.md).

## 1. Product experience

The primary outcome is independent farmer understanding and use, including limited reading ability and digital experience. Present a helpful agricultural journey, with one manageable decision at a time and a visible four-season context. Borrow only the Season Table's precise conflict inset and the Field Ledger's explanation hierarchy and Evidence Card clarity. Keep one visual identity.

- **Show:** locally recognizable crop photographs, visible answer choices and four connected seasons. Illustrations establish context; they never establish agricultural evidence.
- **Speak:** short Egyptian Arabic questions and feedback, with equivalent English. Spoken guidance and takeaway are core requirements, not decorative controls.
- **Choose:** touch, pictures or voice complete the primary journey. Typing is an optional fallback, never required. Speech is never the only input method.
- **Confirm:** repeat complete crops, purposes, dates, years, quantities, units, assumptions and protected commitments. Recognition creates proposals; only a separate explicit action confirms them. Silence never confirms.

Use respectful adult language and authored bilingual templates. Avoid unrestricted chat, technical dashboards, form walls, childish mascots, celebratory validation effects and unsupported visual outcomes. Demo origin remains visibly and audibly illustrative.

## 2. Visual system

### Color roles

Use semantic tokens rather than local component color choices. The warm canvas and terracotta action color carry the brand. Green is reserved for a supported feasible status, never general decorative success.

| Token | Value | Use |
|---|---|---|
| canvas | #FFF7E8 | Main warm sand background |
| surface | #FFFFFF | Answer and explanation surfaces |
| ink | #342B25 | Primary text |
| muted-ink | #64564B | Supporting readable text |
| action | #963F2D | Primary button with white text |
| action-hover | #7D3224 | Pointer hover only; touch does not depend on hover |
| selection | #F9E6DC | Selected answer background; also use action-colored border and explicit selection mark |
| sky | #DDECF0 | Illustration field; no status meaning |
| harvest | #E7B94F | Illustration accent; no small white text |
| control-border | #89766A | Necessary control boundaries |
| divider | #DED3C4 | Decorative separators only |
| focus | #153F70 | Visible focus outline with surface-colored separation |
| protected-ink / surface | #283F73 / #EDF0FA | Lock and protected value |
| feasible-ink / surface | #245C45 / #EAF3EC | Feasible under applicable rules and stated assumptions |
| rejected-ink / surface | #9C3027 / #FBEDE9 | Demonstrated conflict |
| review-ink / surface | #805000 / #FFF2D5 | Required checks unresolved |
| unavailable-ink / surface | #4D5864 / #EEF1F4 | Unknown, unavailable or non-current result |

Every status has text, an appropriate symbol and spoken meaning. Do not use color alone, pale borders as the only selection cue, or brand colors as scientific status. Verify actual contrast in rendered states before acceptance, including focus, errors and disabled controls.

### Typography and composition

- **Readex Pro** is the primary family for Arabic and English. Use 400 for body, 500 for controls, 600 for questions; avoid unnecessary weights. Retain script-appropriate sans-serif fallbacks. Confirm font files/licensing and shaping before implementation; no font dependency is installed by this document.
- Starting scales: Arabic body 20 px / 1.7 line height; English 18 px / 1.55; controls 18–20 px; questions 28–36 px mobile and up to 44 px desktop. Essential dates and statuses are never small metadata. Supporting technical detail stays at least 16 px.
- Use relative sizing and allow text enlargement. Tune optical size by script rather than forcing identical line boxes. No Arabic tracking, all-caps treatment, clipped diacritics, or fixed-height text containers.
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64 px. Mobile page gutters start at 16 px; desktop at 32 px. Question text is roughly 28–36 em wide. Desktop content maximum approximately 1200 px.
- Corners: 12 px controls, 20 px answer tiles, 24 px scene panels. Use thin borders and restrained shadows only where separation is needed. Avoid excessive pills, glass effects and decorative gradients.
- One dominant question/conclusion, one primary next action. Quiet secondary controls remain visible. A few substantial panels replace a grid of cards.

### Images, illustrations and icons

Crop selection uses real, consistently framed photographs. Show sufficient whole-plant structure and a useful identifying detail where necessary. Distinguish grain maize, grain sorghum, wheat and multicut berseem; show purpose separately. A photograph must not imply an identified cultivar or guaranteed crop performance. Catalogue presence is not local suitability approval.

Story illustrations use mature, restrained shapes, natural crop proportions, warm field colors and limited texture. A connecting path expresses season order, not a parcel boundary, distance or duration. No implied lush yields, wilted failure, irrigation savings or improved soil. Avoid stereotyped characters and unnecessary avatars.

Moaaz prepares a consistent asset set; Amr and Refaat review recognition and scientific implications. Record asset origin, usage rights, crop identity and alt/spoken labels. No asset generation or third-party upload is authorized here. Prefer compressed, size-reserved images; essential crop recognition must survive slow loading with labels and audio. Use one consistent outline icon style, with visible labels for actions; no emoji controls.

## 3. Journey, navigation and confirmation

At entry, present العربية and English as large choices with listen controls and a clear start action. Do not request microphone permission on arrival. An explicit start/listen action enables audio; browser autoplay failure exposes a prominent play control.

Keep Back, Repeat, Change and Help consistently located at relevant steps. The audio control says Listen, Stop or Repeat according to actual state. A four-crop overview shows progress without requiring knowledge of menus, tabs or breadcrumbs. No sidebar or compulsory swipe navigation.

| View | Goal and principal action | Key interaction/state |
|---|---|---|
| Welcome | Understand and begin | Language choice; short optional spoken introduction |
| Crop and context conversation | Answer one question; Continue | Photo answers; touch/voice; explicit “I don't know”; progressively collect the complete four-season input and required context |
| Commitments and confirmation | Hear/check facts; Confirm and check | Protect crop, purpose or date through a named choice; editable summary and full spoken readback |
| Promise Test | Understand conflict; Explore permitted changes | Exact date inset with protected cut; all four seasons remain accessible |
| Investigations | Understand preserved, changed and unknown; Inspect | Feasible alternatives separate from review investigations and rejected candidates; selecting creates no approval |
| Season Replay | Understand available historical evidence; Continue | Optional detail disclosure; honest unavailable states never block saving intentions |
| Evidence and takeaway | Keep exact plan and checks; Save draft for review | Separate feasibility, save and approval states; matching version-bound spoken takeaway |

For touch-only date entry, use sequential day/month/year choices with large controls and spoken selected values, plus a full-date confirmation. Month/year lists and labelled day choices replace complex calendar navigation. Do not require typing or assume a year. Explain and confirm area units; never silently convert hectares to feddans. Purpose uses labelled picture/audio choices (for example grain versus forage). Unknown answers remain explicit facts, not zero or an inferred default.

Individual answers remain editable proposals until the complete input is explicitly confirmed. Break readback into manageable groups, with repeat/change on each and final confirmation of the whole snapshot. Changing a protected commitment requires its own acknowledgment of old and new values. Initially, lock changes remain unavailable until the approved commitment-change flow exists.

## 4. Signature screens and scientific boundaries

### Promise Test and the four-season path

UH-001 always follows the exact fixture. Lead with the protected berseem cut on **20 May 2027**, then explain that maize sowing on **15 May 2027** occurs earlier on the same field. Proposed short copy: “ميعاد الذرة قبل حشة البرسيم اللي حضرتك ثبّتها. مش هنلغي الحشة.” Detail playback includes both full dates and the year.

The precise inset shows 15 May, the protected 20 May cut, assumed first free date 21 May and seven full preparation days. A hatched overlap and annotation communicate the conflict without color dependence. Under that assumption 28 May is calendar-compatible, not an agronomic recommendation. The illustration never performs a fictional repair.

The main path shows four connected, numbered seasons: berseem forage, grain maize, grain wheat, grain sorghum. Display dates, purposes, locks and uncertainty. Equal overview sections communicate sequence, not proportional duration; only the detail inset uses a date scale. Current intended dates are illustrative, not validated crop durations.

R1 (28 May 2027) and R2 (1 June 2027) are **timing investigations requiring review**. There are **zero validated feasible alternatives**. Changing maize sowing makes unsupported harvest/release endpoints unknown; later checks need reevaluation. Keep later intentions labelled without inventing later collisions or implying preserved old maturity. Do not instantiate a season-4 maize replacement without supported profiles/dates.

No drag-to-reschedule interaction is needed. Named permitted date choices are clearer and match the contracts. Inspecting a variant previews differences; adopting it creates a draft, then explicit confirmation and reevaluation are required.

### Status and evidence language

| Axis | Display rule |
|---|---|
| Protected | “ثابت باختيارك / Protected by your choice”; a retained commitment, not guaranteed harvest or sufficient feed |
| Feasible | “ممكن حسب الشروط الموضّحة / Feasible under stated conditions”; no field-performance guarantee |
| Rejected | “الخطة فيها تعارض / Plan has a conflict”; identify the demonstrated cause |
| Needs review | “محتاج مراجعة زراعية / Needs agricultural review”; never label safe to plant |
| Saved review draft | “مسودة محفوظة للمراجعة / Saved draft for review”; saving does not change plan feasibility |

Arabic copy receives native Egyptian review and user comprehension testing. Keep contract statuses intact; these are presentation labels, not new enums. A confirmed farmer report is not verified scientific evidence. A saved review draft can retain rejected P0. Approval is available only for a current feasible plan under the contract, never for Hussein's rejected plan.

The Evidence Card orders information: status and saved state → preserved commitments → changes/conflict → assumptions and outstanding checks → sources/details. It uses the same Season Path palette and typography with quieter composition. Card and audio refer to the exact same confirmed plan/evidence version. No stale audio can represent new edits. Audio generation failure does not erase a saved card, but fails spoken-takeaway acceptance.

### Season Replay and experimental forecast

Use “These seasons in past weather” with NASA POWER attribution. Explain temperature and reference atmospheric water demand in short spoken terms; keep ET0 notation, equations, method versions, coverage and source records in engineer detail. Preserve the method label **FAO56 ET0 with the ASCE daily cloudiness bound**. ET0 is not irrigation use. Unsupported ETc stays unavailable; missing crop heat thresholds prevent crop-risk claims.

When supported, compare matching historical blocks with consistent chart scales, explicit dates/units, durations, crop-free gaps and retained production commitments. Provide text/audio equivalents, not hover-only values. Never invent curves, totals, winners or savings to fill a composition. P0 remains rejected in any diagnostic comparison. Missing profiles/data yield a named reason and continuation to the review draft.

Forecast is a contextual section, not a compulsory journey step. UH-001 is **not applicable** because the choice is outside the seven-day horizon. No forecast records are invented. For a later eligible action, show experimental status, issue/cutoff/target dates, provenance and uncertainty; stale/unavailable states withhold actionable records. Forecasting never validates a rotation. Preserve the documented lack of demonstrated trained-model superiority; do not market operational benefit.

## 5. Accessibility, speech and responsive behavior

Target WCAG 2.2 AA plus project touch targets of at least 48 × 48 CSS px, normally 56 px for principal controls, with at least 8 px separation. Verify normal text at 4.5:1 and necessary UI boundaries at 3:1. Semantic buttons, groups, headings, labelled inputs and ordered-list timelines support keyboard/screen-reader use. Focus follows logical reading order, remains visible and returns to the trigger after disclosures. Announce concise results without repeatedly reading the whole page or competing with screen-reader speech.

Audio is interruptible, never overlapping. After user activation, prompts can accompany progression; provide a persistent sound preference, stop and repeat. Do not play text-to-speech over active recognition. Distinguish idle, permission request, listening, processing, proposed answer, clarification and failure. No fake live waveforms or confirmed transcripts. Disclose transmission before microphone consent; provider/retention choices remain unapproved. Recorded or cached demonstrations must be labelled audibly and visibly.

Touch plus spoken guidance must complete the journey after microphone denial. If playback also fails, pictures/text remain available, but independent no-reading completion is unproven; show help and do not count assisted completion as independent success. Assistance does not imply an integrated adviser service or external messaging.

| Recovery | Required behavior |
|---|---|
| Denied/unavailable microphone | Preserve facts; offer picture/touch answers with playback, optional typing and help; do not repeatedly prompt for permission |
| Silence, negation or ambiguous crop/date/unit | No confirmation; ask one clarification, read back the full value, offer visible choices |
| Interruption | Stop promptly; discard responses from interrupted/superseded recognition; repeat safely |
| Loading/network failure | Name operation and offer retry; retain input; no fabricated progress or silent successful mock fallback |
| Zero feasible alternatives | Show blocking reasons and separate investigations; allow save for review without relaxing locks |
| Missing evidence | State what is missing and which conclusion is unavailable; never show zero |
| Failed save | Persistent unsaved label and spoken error; retry safely; cached input is not a server save |
| Material edit | Stop old audio immediately; mark dependent results non-current; reconfirm and reevaluate |
| Language switch | Preserve values, facts and approval state; stop old-language audio; replay in selected language; no revision solely for translation |
| Forecast stale/unavailable | Explain dates/reason and keep the main journey usable |

Mobile is the primary composition: vertical four-season path, short question, large answer choices, and a reachable primary action. The overview remains accessible without becoming a large sticky obstruction. Expand the active season in place; no mandatory horizontal scrolling. Desktop uses a panoramic path and adjacent explanation when content fits; the questions and decision order remain identical. Comparison becomes stacked before/after on phones, aligned on desktop. No dense farmer tables.

Use content-driven breakpoints, starting near 48 rem and 64 rem; validate at 320, 390, 768 and 1280 CSS px, landscape, text enlargement and 400% zoom/reflow. Sticky controls must not hide content/focus or the software keyboard. Respect safe areas and browser zoom.

Arabic uses RTL layout with logical properties; English uses LTR. Desktop season order begins at the reading start, explicitly numbered 1–4; mobile order is top-to-bottom in both. Chronological date axes include explicit earlier/later labels. Isolate mixed-direction dates/numbers/units; never reverse digit strings, media icons or crop photos mechanically. Use named Gregorian months and complete years. Initial display uses Arabic-Indic numerals in Arabic and Latin numerals in English, subject to comprehension testing; canonical ISO values and units stay unchanged.

Motion communicates selection, progression or affected dependencies: 120–180 ms control feedback, 200–280 ms chapter transitions, restrained easing and immediate interruptibility. No parallax, continuous decorative movement, forced animation waits or shaking errors. Reduced motion replaces movement with immediate state/focus changes or brief fades; information is never motion-only.

## 6. Reusable component handoff

These are proposed frontend component names, not API changes. Astra builds references; Sol extends the reviewed system rather than inventing per-screen variants.

| Component/pattern | Responsibility and required states |
|---|---|
| JourneyShell + SeasonOverview | Language, progress, Back/Help, responsive scene and primary action; RTL/LTR, zoom, reduced motion |
| SpokenPrompt + AudioControls | Authored question/explanation; play/stop/repeat, unavailable, interrupted, version mismatch |
| CropChoice + AnswerChoice | Photo, purpose, spoken label; selected/unselected, focus, unavailable image; selection is not confirmation |
| DateChoice + QuantityChoice | Large staged touch choices and unit/year readback; ambiguous/unknown/correction states |
| ConfirmationSummary + ProtectedCommitment | Grouped facts and unknowns; edit/confirm; protected old/new acknowledgment where supported |
| FourSeasonPath + SeasonDetail | Semantic order, crop/date/purpose/lock presentation; intended versus unknown endpoints |
| ConflictInset | Date-accurate overlap, release/preparation assumptions and equivalent spoken/text explanation |
| PlanStatus + InvestigationComparison | Separate status axes and preserved/changed/unknown; zero alternatives and review-only investigations |
| EvidenceDisclosure + ReplayPanel | Sources, units, common periods and unavailable metrics; no client-invented science |
| EvidenceCard + SaveFeedback | Exact plan/version takeaway; unsaved, saving, saved review draft, failed, superseded; later approval/revocation states |
| RecoveryNotice | Consistent reason, retry/change/help; accessible announcement and focus recovery |

Keep view state distinct from working proposals, confirmed snapshots and server results. Consume generated contract types; do not recreate scientific or feasibility logic in components. Centralize localized template parameters, tokens and status mapping. Keep UI-only fixtures schema-conformant and explicitly labelled. Never present a fixture playback as tested live speech.

## 7. Prioritized reference-screen implementation plan

**No implementation is authorized yet.** After explicit authorization:

1. **Astra: smallest rendered foundation.** Establish tokens, JourneyShell, photo choices, prompt/audio states and four-season overview. Render welcome → crop question → protected-cut confirmation in Arabic mobile and English desktop, then check the opposite combinations. Use labelled UH-001 fixtures and disclosed recorded prompts where necessary. Acceptance: no typing required, obvious start/back/repeat/change, complete-date confirmation, microphone-denied touch route. No claim of working live speech.
2. **Astra with Karim/Yahya: core reference screen and real slice.** Establish the approved five endpoints and generated types; render confirmed UH-001 → real Promise Test with conflict inset and zero alternatives. Inspect all four seasons and documented R1/R2 review presentation without inventing candidate service results. Acceptance: 20 May retained, 15 May conflict explained, unknown endpoints honest, no approval or fabricated repair. Preserve first-slice backend scope; review fixtures remain visibly fixtures until candidate work is implemented.
3. **Visual checkpoint before frontend expansion.** Show actual browser screenshots and inspect interactions on real phones. Review Arabic/English, keyboard/focus, contrast, reflow, loading/error and reduced motion. User reviews first screens; record requested changes. Do not build the whole frontend before this checkpoint.
4. **Sol: extend the approved references.** Add candidate/revision flow, historical replay states and version-bound saved review draft/takeaway in architecture milestone order. Save must be demonstrated against real persistence before acceptance. Add forecast status presentation without creating outputs. Obtain a second visual/integration review and run the usability pilot once the core journey, audio and save behavior are actually testable.

Start the authorized Egyptian Arabic speech/device feasibility trial alongside milestone 1, not at the end. Provider access, transmission/retention and paid-service approvals remain separate. Amr coordinates UI and usability; Moaaz owns supporting visual/audio assets; Refaat checks scientific presentation; Karim/Yahya own planner/contracts/persistence. No model switch, delegation, dependency purchase or implementation is executed by this plan.

## 8. Small formative usability protocol

Proposed first round: six consenting Egyptian Arabic-speaking adults, preferentially farmers near Sakha, varying age, reading confidence and smartphone experience; include at least three with limited reading or digital confidence. Recruitment is not yet arranged. Use fictional Hussein data, no real field records, no need to disclose reading scores. Consent to participation and recording are separate; observation notes can replace recordings. English receives equivalent task/accessibility checks with suitable users, reported separately from the Egyptian farmer pilot.

Use the participant's familiar phone where practical, with sound available. State only that this is an unfinished fictional planning tool, not agricultural advice. Start at welcome; give task goals orally without naming controls. Do not demonstrate navigation. Do not require think-aloud while audio plays; ask brief retrospective questions. Target 20–30 minutes with breaks. Observe independent attempt first; only then provide a standardized hint if requested or stalled, logging that task as assisted. Record help control use separately from human coaching.

| Task | Observable evidence |
|---|---|
| Begin and choose language | First action, time to start, wrong turns, requests for instruction |
| Select crop and purpose | Correct berseem/maize/wheat recognition; distinguish sorghum; corrections and confused images |
| Protect and confirm 20 May 2027 | Correct full date/purpose readback; explain what protection means without a harvest guarantee |
| Explain the Promise Test | In own words, connect 15 May maize with the later protected 20 May cut on the same field |
| Inspect review investigations | Explain that 28 May/1 June are not confirmed planting recommendations and need agricultural review |
| Save and hear takeaway | Correctly identify saved review draft, retained commitment, rejection and unresolved checks |
| Recover | Complete an assigned microphone-denied, ambiguous-date or failed-save task; repeat/back/change without losing facts |

Counterbalance microphone-denied and voice-enabled starting routes. Spread additional injected failures across participants to avoid excessive fatigue. Test real recognition separately from deliberately simulated ambiguity; disclose simulations and record which path was used. Log task outcome as independent / assisted / incomplete, elapsed time, wrong selections, repeated prompts, hesitation longer than 10 seconds, recovery attempts, factual misunderstandings and severity. Report counts, not impressive percentages from six participants.

Proposed iteration gate: at least 5/6 independently complete each critical task and explain the conflict; **zero participants leave believing a review investigation is safe to plant or a failed save succeeded**. Any such critical misunderstanding triggers redesign and a fresh check. Fewer than 5/6 on a task triggers focused revision. These are formative decision rules, not statistical validation or proof of universal usability. Report recruitment limitations, assistance, device failures and missing audio separately; never count a coached or simulated-live journey as independent live success.

## 9. Acceptance and research limits

Design approval selects a direction; rendered visual approval and implementation authorization are separate. No current application/browser, contrast, speech or intended-user results are claimed here. The primary ui-ux-pro-max skill's written guidance informed this foundation; its search script could not run because Python was unavailable on PATH. No complementary design skill was used.

Implementation references: [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and the [Readex Pro source/license](https://github.com/ThomasJockin/readexpro). A font's availability or an accessibility checklist does not prove farmer comprehension. Verify the visual system through real rendered screens, exact contract fixtures, actual-device interaction and the observed user tasks above.
