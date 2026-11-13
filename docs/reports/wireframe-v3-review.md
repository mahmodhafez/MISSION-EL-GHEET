# Wireframe V3 — review

. **Low-fidelity iteration, pending user review.** Open [Wireframe V3](../../work/ux-phase-2/season-path-wireframes-v3.html) directly in a local browser. No server or installation is needed. [V2](../../work/ux-phase-2/season-path-wireframes.html) and its checks remain untouched by this iteration. `preview-v3.html` is an identical standalone copy included in the publication checkpoint so the parity check also runs from a clone.

Season Path remains the approved direction. This artifact implements design interactions in standalone HTML; it is not React, a planner, live speech, scientific computation or persistent storage. Approved scientific documents, architecture and contracts are unchanged. Guidance: `ui-ux-pro-max`, focused on progress and accessible navigation; no complementary design skill.

## V2 critique → V3 changes

These are design judgments from the specifications, not findings from user research.

| V2 view / classification | Farmer with little reading / digital experience | Farmer seeking speed | Engineer requiring precision | V3 response |
|---|---|---|---|---|
| Welcome — KEEP benefit; REPLACE language entry | Hidden language and duplicate setup concepts obstruct entry | Starting should require no setup | Translation must preserve facts | Arabic default, working header Arabic/English controls, one Start and one speaker. Illustration stays schematic. Start moved above it following rendered inspection. |
| Intake — KEEP crop pictures; REPLACE fixture-only progression | Other selections previously hit a dead end | Repeated questions and forced protection slow progress | Unknowns and corrections must be usable | All four catalogue crops work in every season; crop then essentials, optional crop/purpose/date protection, unknown dates, touch day/month/year and optional typed dates. Field details use disclosure. |
| Confirmation — IMPROVE; REMOVE repeated confirmation pages | Long simultaneous readback strains memory | Review once, correct only what changed | Need exact dates, units and assumptions | One input confirmation with per-season date disclosures and short sequential spoken-script sections. Full script is available on request. Unknowns can be confirmed as unknown. |
| Season overview — REPLACE optional-only placement; KEEP detailed overview | Losing the four-season context makes questions disconnected | Direct return to a previous season reduces navigation | Changes must invalidate later checks | Persistent compact path with current/reviewed/remaining positions, crop drawings, protection and uncertainty. Detailed dates remain expandable. Edited seasons lose their reviewed marker. |
| Promise Test / investigations — KEEP conflict metaphor; IMPROVE branches | Same-field occupation needs explanation before arithmetic | Opening a date must not adopt it | Preserve locks, endpoints and result dependencies | Two dates on one field, optional proportional May inset, separate inspect/explicit adoption. Adoption clears unsupported maize harvest/release and old results. Generic plans reach review without borrowing P0. |
| NASA replay — REPLACE text-only dead end | “Weather” can be mistaken for a forecast or irrigation advice | Useful context should be accessible without finishing a comparison | Need metrics, periods, methods and provenance | Four selectable historical lenses; explicitly empty chart frame. Dataset availability is separate from unconnected values and blocked paired rotation comparison. Return restores the inspected candidate. |
| Evidence Card — KEEP takeaway; REPLACE save gate | Saved can sound like safe to plant | Edited or incomplete inputs need a normal completion route | Exact version, unknowns and sources must survive | Any draft can be reviewed, explicitly confirmed and simulated-saved. Input confirmation, protected commitments, evaluation, saving and agricultural feasibility are separate statements. Failed save preserves input. |

Removed the fake English notification and fixture-only dead ends. Kept one large **اسمع** control per view, including failure states; the adjacent microphone is **جاوب / اتكلم**. No launch voice/manual mode or role selection. Engineer access is disclosure within the same journey.

## Review route

- **Generic:** Start → choose crop → optional dates/protection → next season → field context → confirm input → review → Evidence Card → simulated save. Unknown crops, dates, measurements and preparation stay unknown.
- **Hussein:** expand “جرّب حكاية عم حسين”, open the fixture and review four prefilled seasons. Explicit confirmation reveals **P0 rejected**, protected **20 May 2027** cut, conflicting **15 May 2027** maize, **zero validated feasible alternatives**.
- **Investigations:** inspect **28 May** or **1 June**, both **needs_review**. Return changes nothing. The separate “Use date in draft only” action changes sowing, retains protections, clears unsupported maize endpoints and invalidates old confirmation/evaluation/save status. Reconfirmation leads to an unresolved review draft, not a new computed recommendation.
- **Protected corrections:** old and new values appear together; an explicit commitment-change acknowledgment is required. Cancelling preserves the original. Switching languages also translates this pending correction.
- **Optional context:** NASA history and “طقس الأيام الجاية” return to the originating view. Outlook has seven dated **layout slots only**, with no predictions. The illustrative issue date is ; saved data ending 31 October cannot support a live November forecast. Stale/unavailable examples withhold values.
- **Recovery:** reviewer controls expose speech recognition, silence/ambiguity, denied/unavailable microphone, playback failure, network failure and failed save. No permission requests, recording, network calls or persistence occur. A transcript is a proposal; it cannot confirm a commitment. The primary speaker opens a script simulation, not actual sound.

## Feature coverage

“Designed” describes wireframe interaction coverage, not implemented or validated product functionality.

| Capability | V3 coverage | Remaining dependency / limit |
|---|---|---|
| Bilingual accessible interaction | Designed across farmer views, prompts, statuses, editing and navigation | Speech provider/recordings, screen-reader and independent no-reading tests remain unvalidated. |
| Four connected seasons | Designed: persistent path, progressive intake, direct correction and details | Crop drawings are recognition placeholders; arbitrary agronomic schedules are not evaluated. |
| Protected commitments | Designed: optional crop/purpose/date protection and separately acknowledged changes | Server-confirmed immutable snapshots and real commitment APIs are not integrated. |
| Promise Test | Designed UH-001 explanation and generic review/error route | Deterministic computation remains backend work. Unknown is an evidence state, not an extra PlanStatus enum. |
| Candidate investigations | Designed inspect/adopt/invalidate route for R1/R2 | Zero validated feasible repairs. Feasible appears only in a clearly labelled synthetic status example. |
| NASA historical replay | Partially designed: four lenses, empty graph, source/method disclosure, return | No displayed measurements; data binding, sourced heat thresholds and complete shared-block comparisons remain outstanding. ETc is withheld. |
| Evidence Card and agricultural review | Designed for original, edited and incomplete drafts; simulated save/failure | No actual save, external adviser service, approval or version-bound audio integration. |
| Optional Chronos outlook | Optional concept designed: seven dates, experimental/unavailable/stale states, engineering details | No current forecast records or valid issue-specific cutoff. Recorded LoRA did not beat seasonal climatology; July–October holdout remains consumed. |

Historical context explicitly distinguishes temperature, hot-day exposure, reference atmospheric demand and variability. ET0 remains **FAO56 ET0 with the ASCE daily cloudiness bound**, mm/day, not irrigation quantities. No yield, savings, agronomic repair, forecast output or numeric comparison is fabricated. Full paired comparison remains unavailable until endpoints and checks are supported. Source timestamps/hashes and exact calculation releases are described as not connected, not invented.

## Verification

Run `node work/ux-phase-2/check-wireframes-v3.cjs` from the repository root. It checks JavaScript syntax and executes the actual inline script in a minimal DOM stub. Tests cover all ten requested journeys, plus commitment preservation, language parity, one speaker, unknown versus zero, navigation, HTML structure, preview equality and absence of network/microphone/storage calls. It does not run an implemented planner or validate agricultural outcomes.

**Rendered inspection was partial:** Brave opened the real local V3 file. Arabic welcome and crop-selection layouts were observed, and Start opened the first crop question. Inspection exposed a low Start position and loss of path visibility on navigation; these informed subsequent refinements. Repeated user-input conflicts then interrupted browser control. Per the user's continuation instruction, further automation was skipped. The final refinements, English desktop, all rendered recovery states, small physical devices, zoom, keyboard traversal and screen-reader behavior have **not** received a complete browser pass. The earlier screenshots do not establish final-layout approval.

Structural checks are not usability testing. No users were recruited, no actual speech played or recognized, no contrast measurements or empirical crop recognition tests were performed. Touch sizes, focus and reduced-motion handling are specified in CSS but still require rendered verification.

## Review decisions and next step

Review the compact path's information load, crop→essentials pacing, optional date/protection controls, and the distinction between “review draft saved” and agricultural approval. Decide whether the historical lenses explain enough without suggesting unavailable measurements. These are V3 proposals, not new approved product requirements.

After review, perform a small formative test with two farmers with limited literacy/digital experience, two reading farmers and two agricultural engineers. Give tasks without coaching: begin, identify crops, protect/correct a cut, explain the conflict, inspect without adopting, save an unresolved draft, and recover from denied microphone access. Observe hesitation, errors, time, assistance and explanations in participants' own words. Record incorrect “safe to plant” interpretations separately. Frozen scripts may support a moderated wireframe walkthrough, but facilitator-read prompts must not count as independent voice usability; approved audio and actual provider testing are needed for that claim.

Stop here for V3 review. Amr owns UX decisions; Refaat reviews scientific meaning; Moaaz reviews future recognizable assets; Karim/Yahya retain planner/contract ownership. No high-fidelity design, React, dependencies, backend work, commits or pushes are part of this iteration.
