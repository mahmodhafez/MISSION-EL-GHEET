# Phase 3 — visual identity options

**Proposals for Amr’s approval.** The Season Path interaction model remains the foundation. This study does not replace the approved DESIGN.md, amend scientific requirements or authorize React implementation. V2/V3 remain untouched.

Open [the visual comparison](../../work/ux-phase-3/index.html) directly in a browser. At widths above 1080 CSS px it shows the same screen in all three identities side by side; smaller screens stack them. Select one direction for a full desktop composition or the phone-width preview. The screen selector exposes all eight signature views, in Arabic and English. Controls demonstrate visual responses only; use V3 for the fuller interaction model.

## 1. Audit of the existing direction

| Before | After proposed | Why |
|---|---|---|
| Season Path, Show → Speak → Choose → Confirm | Preserve the four-season context, voice/picture choices and explicit confirmation | These are the product’s interaction identity, independent of styling. |
| Warm sand, terracotta action, repeated rounded panels | Compare three complete visual treatments; recommend indigo/ivory with ochre route markers | Terracotta can work, but resembles rejection red. Indigo separates the main action from agricultural outcome colours. |
| Large crop photographs for recognition | Preserve that requirement; original botanical SVG drawings in this study are explicitly placeholders | Images must distinguish berseem, maize, wheat and sorghum in local recognition testing. Attractive illustrations cannot substitute for that evidence. |
| Large language choice at entry in the original design document | Retain V3’s quiet header switch, Arabic default | Language is immediately available without adding a compulsory setup question. |
| Farmer assembles dates before seeing value | Two intentions converge on the same constraints, commitments and four-season workspace | “Explore” starts with needs and known context. Unknown dates are not silently supplied. Generation remains evidence-dependent. |
| Optional weather links can feel secondary | Give Season Replay a named archive panel and consistent, prominent entry from planner, comparison and evidence | Historical context is a recognizable product feature, not a dashboard widget. |
| General forecast presentation | Separate historical archive, proposed seasonal outlook and existing experimental seven-day outlook | These differ in time horizon, source, uncertainty and current scientific support. |
| Fixed control dimensions risk clipping Arabic | Minimum heights, expanding text, script-aware font stacks and logical layout | Large targets should survive long labels and zoom, rather than constrain them. |

Abandon oversized decorative hero areas in task screens, status-by-colour alone, repeated ornamental cards, generic dashboard navigation and an implication that “protected” or “saved” means agriculturally feasible. There is no mascot, decorative gradient, glass layer or animation sequence in this study.

## 2. Three identities

### A — Earth & Hands / وشّ الأرض

**Personality:** familiar, patient, tactile. A warm illustrated field canopy frames the question; gently shaped crop compartments suggest the field rather than an administrative form. Terracotta controls, olive illustration lines and harvest accents keep the relationship human. Noto Naskh Arabic is used only for large headings; Readex carries body text and controls. English uses Georgia headings and Readex body.

The distinctive treatment is the generous field scene, Naskh title rhythm, asymmetric voice-control corner and rounded candidate panels. Use consistent outlined icons, slightly softened corners, crop photographs with warm neutral backgrounds, and quiet cut-paper botanical illustration. No artificial paper dirt under text. Navigation stays in the shared Season Path, never an illustrated map the farmer must decipher.

**Egyptian connection:** cultivated field divisions, crop forms, spoken Egyptian wording and the cut/feed commitment—not pyramids, costumes, decorative hieroglyphs or a stereotyped farmer character. These associations are design hypotheses, not evidence of cultural preference.

**Risk:** warmer and more emotional, but Naskh may be slower for short control-like headings; terracotta can resemble rejection red. Keep all functional text in sans serif, red confined to explicit rejection labels, and avoid excessive illustrative height. Medium asset/art-direction effort.

### B — Fieldlight / نهار الغيط

**Personality:** clear, practical, optimistic. White working surfaces, dark green actions and light botanical accents create a contemporary agricultural tool. Noto Sans Arabic gives generous clear shapes; Readex is the English companion. Voice controls are paired, broad and directly aligned. Crops use photographic cutouts or consistent neutral-background photographs; illustration is a sparse field silhouette.

The distinctive treatment is open composition: ruled candidate rows rather than enclosing every item in a card, numbered circular progress points, minimal framing and a compact question scene. Icons are uniform two-pixel outlines. Touch selection uses border, check and spoken label together. Navigation and exact dates are visually straightforward.

**Egyptian connection:** full crop names and purpose, local crop recognition, plain spoken prompts and outdoor legibility. Green alone does not make it locally meaningful.

**Risk:** easiest to implement, but closest to common agricultural branding. Green actions can be mistaken for a successful agricultural check; feasible outcomes therefore also require the explicit status label, check symbol and completed evidence. Strong utility, weaker memorability.

### C — Season Ledger / دفتر المواسم — recommended

**Personality:** a capable field companion with a clear record of what was agreed. Warm ivory, deep indigo, restrained ochre and readable Readex Pro in both scripts. The numbered path, margin rule and paper-like Evidence Card make commitments traceable without turning the interface into a spreadsheet.

The distinctive treatment is the ochre field margin, squared but comfortable controls, ruled season sequence, inset protected value and candidate “review slips.” The large outlined speaker has a small ochre offset edge; the microphone uses solid indigo. Crop drawings add warmth, while essential crop identification eventually uses verified photographs. Icons are original consistent outlines; do not introduce differently weighted library icons per screen.

**Egyptian connection:** an abstract field-path mark, familiar crops, useful Egyptian Arabic and the idea of keeping a reliable record. The ledger is a design metaphor, not a claim that all farmers use notebooks. Avoid bureaucratic stamps, official seals and faux government styling.

**Risk:** can become too formal or dense if every item receives a rule or folio number. Use the ledger treatment for commitments and evidence, not every question. “دفتر المواسم” names the design direction; the product remains MISSION EL GHEET / الغيط and its journey remains سكة المواسم. Medium effort, primarily shared components rather than bespoke artwork.

## 3. Accessible palette specification

Values below are complete role palettes. White `#FFFFFF` is the label colour on all primary action/hover fills. Accent fills are decorative or use the theme’s dark ink; never use small white text on ochre or mint.

| Role | A Earth & Hands | B Fieldlight | C Season Ledger |
|---|---|---|---|
| Canvas | #FFF7E8 | #F4F8F3 | #F7F3E8 |
| Surface | #FFFCF5 | #FFFFFF | #FFFEFA |
| Primary ink | #342B25 | #16352B | #202D48 |
| Supporting ink | #64564B | #496459 | #536078 |
| Primary action | #963F2D | #17634B | #293E69 |
| Action hover | #7D3224 | #104D3A | #1D2F53 |
| Secondary / illustration ink | #4D5C35 | #254D62 | #76531E |
| Accent | #E7B94F | #D6E7A3 | #D9AD47 |
| Selected / subdued surface | #F2E8D8 | #E6F0E7 | #ECEEEB |
| Necessary border | #89766A | #6C8175 | #788296 |
| Focus | #153F70 | #1849AD | #854513 |

Semantic colours deliberately remain consistent across all three proposals:

| Meaning | Ink / surface | Non-colour signal |
|---|---|---|
| Protected | #283F73 / #EDF0FA | Lock + exact retained value + “protected by your choice” |
| Feasible | #245C45 / #EAF3EC | Check + conditions; only after current supported checks. No real feasible UH-001 card exists. |
| Rejected | #9C3027 / #FBEDE9 | Cross in circle + named conflict |
| Needs review | #805000 / #FFF2D5 | Warning triangle + explicit agricultural-review wording |
| Unknown / unavailable | #4D5864 / #EEF1F4 | Missing-value dash/question and reason, never a zero |
| Saved draft | #283F73 / #EDF0FA | Record icon/double rule + save state separately from plan status |
| Historical evidence | #244B53 / #ECF4F3 | Solid archive rule, source and historical dates |
| Future outlook | #574168 / #F2EDF6 | Dashed boundary, issue/validity dates and explicit probabilistic label |
| Disabled | #555C64 / #E9ECEE | Disabled semantics, dashed boundary and adjacent reason |

Historical boundaries use `#647E87`; future boundaries use `#796386`. [Contrast report](../../work/ux-phase-3/contrast-report.json) is generated by the check script. It tests opaque sRGB normal text at 4.5:1 and essential borders/focus against relevant backgrounds at 3:1. These calculations do not establish sunlight usability, rendered font legibility or full WCAG compliance. Never lower essential status opacity.

## 4. Typography, assets and controls

The previews bundle unmodified font files and their OFL notices from the official Google Fonts repository: [Readex Pro](https://github.com/google/fonts/tree/main/ofl/readexpro), [Noto Naskh Arabic](https://github.com/google/fonts/tree/main/ofl/notonaskharabic), [Noto Sans Arabic](https://github.com/google/fonts/tree/main/ofl/notosansarabic). Files are local, with no runtime font-network dependency. The production team should ship only the approved family and required weights/subsets after verifying Arabic shaping and retaining licenses.

| Rule | Proposed C system |
|---|---|
| Family / fallback | Readex Pro → Tahoma → Arial → sans-serif; no synthetic weight or Arabic tracking |
| Body | Arabic 20 px / 1.7; English 18 px / 1.6 |
| Question | Mobile 30 px / 1.5; desktop 40 px; weight 600 |
| Subheading / dates | 21–24 px; important protected date never metadata |
| Controls | 18–20 px, weights 500–600, intrinsic multiline height |
| Support / metadata | Support 16 px. Only nonessential provenance/reviewer metadata may be 12–14 px. Critical date/status labels remain prominent. |
| Spacing | 4, 8, 12, 16, 20, 24, 32, 40, 48, 64 px; ≥8 px between targets |
| Targets | Minimum 48×48 px; normal 56 px; primary 60 px; voice about 104×96 px |
| Shape | 6 px control/panel corners, restrained border; no blanket pill shape |
| Focus | 3 px ochre-brown outline, 2 px light separation; focus survives dark actions |
| Selection | Explicit checked state, high-contrast border and spoken label; no automatic confirmation |
| Error / warning | Inline named reason, retain answer and show repair action; no shake or colour-only cue |
| Loading | Stable prompt and retained input; textual “checking” state with cancellation/retry, no invented percentage |
| Disabled | Legible label plus reason; do not turn an unavailable recommendation into a tantalizing dead button |

Form inputs use the same minimum target, visible label and optional unknown action. Dates keep large day/month/year choices with manual typing in disclosure. Crop choices use identical image framing, names and purpose; unknown/image-failure retains label, listening and help. Photo approval requires origin/license, locally recognizable crop identity and farmer testing. The included SVGs are new in-repository vector assets, not downloaded photos or proof of cultivar.

The provisional brand mark abstracts four parallel field paths with a destination dot. It is not a NASA mark and implies no NASA endorsement. Do not animate it in Phase 3.

## 5. Eight signature screens

| Screen | Visual emphasis and retained interaction |
|---|---|
| Welcome | One benefit, speaker and two large intention choices: “عندي خطة” / “لسه بختار”. No mode, role or mandatory language setup. |
| Intake / commitment | Picture or speech beside the same question. Highlight the protected cut and complete year; selection remains proposed until explicit confirmation. Explore asks needs before dates. |
| Four-season planner | Numbered crop sequence, retained lock and status; investigations beneath it. Explore shows unknown slots and a useful next input, not a fabricated generated plan. |
| Promise Test | Same-field visual connects 15 May maize and 20 May cut. The precise inset reveals 21–27 May preparation and 28 May boundary as assumptions, not approval. |
| Candidate comparison | Review slips show what stays, changes and remains unknown. Opening details does not adopt a candidate. Both R1/R2 remain needs_review; zero feasible repairs. |
| NASA replay | Distinct solid archive panel, historical period and selectable explanatory lenses. Empty, explicitly unavailable graph frame rather than fabricated curves. ET0 is not irrigation. |
| Seasonal outlook | Dashed future panel, empty issue/target periods, visibly unavailable. No percentages, default seasonal categories, forecast winner or fabricated confidence band. |
| Evidence Card | Quiet paper composition with version, actual plan status, save state, locks, questions and engineer disclosure. Saved status cannot recolour rejection as success. |

Both intentions converge on the same input/constraint model, confirmations, Season Path, checks and Evidence Card. The new exploration path is authorized as a **UX proposal** here. The current planner enumerates confirmed discrete choices; broader schedule generation needs an explicit catalogue/input contract decision. Do not turn “explore” into unrestricted ML suggestions or silently grant permission to change commitments.

Seasonal climate outlook is also a **new concept**, not the existing Chronos API. Source/provider, variables, spatial applicability, issue/valid period, baseline, probabilistic categories, calibration, skill and missing/stale policy require scientific review and later contract approval. Chronos remains a separate experimental seven-day Tmax/ET0 workstream, with its negative climatology comparison preserved. Neither validates a crop schedule. These proposals do not modify SCIENCE, PLANNER_SPEC or API_CONTRACTS.

## 6. Responsive, RTL and evidence rules

Phone: one primary conclusion, vertically stacked candidates; compact numbered path with readable crop labels and expandable details. Do not introduce a permanently oversized sticky header that hides the question. Desktop: question/voice scene next to the same content, maximum working width about 1160 px. At 700 px and below, return to one column. The review gallery’s three-column layout is for judging directions, not a farmer dashboard.

Use logical margins/borders and reading-start alignment. RTL sequence begins at the right; LTR begins at the left. Keep numeric values and units isolated, Gregorian months explicit and canonical dates unchanged. Do not mirror speaker/microphone icons or crop images. Dates and axes must state chronology, not depend on arrow direction. Test 320/390/768/1280 px, 200% text and 400% reflow before component approval.

For future supported climate charts: solid historical series and labelled periods; future distributions use dashed boundaries, named quantiles/categories and dates. Always include units and text/audio equivalents. Identical comparison scales and common historical blocks; no hover-only values. Never draw plausible-looking example data. The current graph frame deliberately has no curve, numeric axis, probability bar or crop-risk scale.

Phase 3 uses static composition. Proposed later feedback is 120 ms selection and ≤160 ms disclosure, interruptible; keyboard changes are immediate. Reduced motion removes spatial movement. No parallax, waveform suggesting real capture, looping crop growth or celebratory feasible animation.

## 7. Independent critique and recommendation

These are design judgments, not measured user scores.

| Criterion | A Earth & Hands | B Fieldlight | C Season Ledger |
|---|---|---|---|
| Farmer ease | Warm entry; scene height must stay controlled | Most direct control hierarchy | Clear retained decisions; avoid bureaucratic density |
| Accessibility / bilingual | Body is strong; Naskh headings need testing | Strong sans clarity; green/status confusion risk | One bilingual family; clear functional colours |
| Distinctiveness | Strong narrative imagery | Familiar category language | Strong route-and-record identity |
| Emotional connection | Strongest warmth | Practical and fresh | Respectful, calm competence; needs crop imagery |
| Scientific trust | Requires clear separation of art/status | Clean, but green must not imply validity | Best connection between plan, assumptions and evidence |
| Consistency | More bespoke art treatments to govern | Simplest reusable surfaces | Shared margin/path/card grammar across screens |
| Practicality | Medium; crop/photo art direction | Lowest effort | Medium; mostly token/component work |
| 30-second demo | Beautiful entry; avoid spending time on scenery | Immediate, less memorable | Cut → conflict → investigation → review card reads clearly |
| Mobile | Rounded surfaces consume some width | Most compact | Good with restrained rules and intrinsic text sizing |

**Recommend C, Season Ledger**, with its own warm botanical illustrations and generous voice controls. Do not combine all three palettes or keep A’s large scene on every C task screen. Its principal risks are formality, long Arabic labels in compact season cells and an excessive emphasis on recordkeeping. Test those before locking the system. A is the strongest alternative if Amr prioritizes warmth; B if rapid implementation and maximum simplicity dominate.

## 8. React-team handoff and validation

[Machine-readable token proposal](../../work/ux-phase-3/tokens.proposal.json) names primitives, semantics, typography, spacing, control sizes and responsive rules. Adopt only after direction approval; do not copy all preview themes into the application.

1. Astra: establish one reviewed `JourneyShell`, `VoiceControls`, `ProtectedCommitment`, `CropChoice`, `SeasonPath`, `StatusMessage`, `CandidateInvestigation`, `EvidencePanel` and `EvidenceCard`; start with Arabic mobile intake + Promise Test and English desktop equivalents. Use authored V3 state decisions, not preview notifications as production behavior.
2. Sol: extend approved components to both intention paths, comparisons and replay without inventing new card/button variants. Keep localization, visual components, journey state and speech adapters separate. Unknown remains explicit; revisions invalidate old result/audio/save states.
3. Karim/Yahya: keep rule execution and candidate validity server-owned. Review exploration-generation implications before changing contracts. Refaat: gate historical metrics, thresholds and any seasonal provider. Moaaz: prepare licensed crop-photo recognition assets and restrained illustration.
4. Before expanding: inspect real browser screenshots, touch/keyboard/focus, denied microphone, audio failure, unknowns and bilingual reflow; then conduct uncoached farmer comprehension testing. No provider, dependencies, React app, backend or training are added by this study.

Verification command: `node work/ux-phase-3/check-preview.cjs`. It checks syntax, 64 template combinations, both intention branches, bilingual content, fixture claims, single audio controls, local links, bundled font headers/licenses and calculated contrast pairs. It is not a browser or usability test.

Browser evidence: the real local page loaded in Brave with the Arabic identity content and bundled typography. The narrow browser viewport stacked comparisons; repeated user-input conflicts prevented safe maximization, side-by-side screenshot review and full mobile/desktop inspection. Browser control was stopped. Final text-size refinements and the complete eight-screen matrix still need visual verification. No screen-reader, sunlight, physical-phone or farmer-usability validation is claimed.

**Approval requested:** A, B or C as the visual identity; its font/colour/shape language; and the two-intention welcome treatment. Seasonal outlook remains a labelled concept until separately sourced and approved. Stop at this review—no automatic DESIGN.md replacement or application implementation.
