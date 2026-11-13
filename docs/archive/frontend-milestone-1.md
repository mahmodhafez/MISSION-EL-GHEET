# Frontend milestone 1 — execution brief

Recorded . The user requested the first frontend reference experience, conditional on permitted hackathon timing. The Season Path design is settled; this brief narrows execution, not design direction. **No application code or dependencies were added in this session.**

## Start gate

The [Space Apps Global Organizing Team's 4 November answer](https://github.com/nasa/spaceapps/discussions/1777) says project work begins on **14 November 2026 at 09:00 in the Local Event's time zone**, or the team owner's residence for the Universal Event. It permits advance topic/resource research and team formation, but says early project work can cause disqualification. The [2026 event page](https://www.spaceappschallenge.org/2026/) also lists 14–15 November. The indexed [event terms](https://www.spaceappschallenge.org/legal/) mention different days in that week only with prior express written Global Organizing Team approval.

The organizer answer was directly retrieved; direct requests for the event, terms and team-formation pages returned HTTP 502, so their corroborating text came from search-index results. No local exception or registered event is recorded in this repository. Do not infer event location from the Sakha research site or computer time zone. If the applicable event is in Egypt, the standard start is 14 November at 09:00 Egypt time; confirm registration before relying on that interpretation.

On 11 November the standard gate is closed. Before resuming, verify the applicable event/start or written exception and the user's coding authorization. Preserve prior research, design and experiment dates; their eligibility is not established by this check. Ask organizers about reuse if necessary; no contact was sent and no history was rewritten. This execution brief is the user's requested pre-event fallback, not an organizer ruling that all prior preparation is eligible.

## Scope and implementation order after the gate

Follow [DESIGN.md](../design/design.md), [ARCHITECTURE.md](../backend/architecture.md), [API_CONTRACTS.md](../backend/api-contracts.md) and [REFERENCE_SCENARIO.md](../product/reference-scenario.md). Use ui-ux-pro-max guidance already reviewed. Keep React/TypeScript/Vite/Tailwind and the existing feature folders; reducer/context handles journey presentation. Do not add a state library, animation framework, speech provider or backend business rules for this milestone.

| Order | Deliverable | Acceptance before advancing |
|---|---|---|
| 1 | Minimal runnable frontend, shared tokens, Arabic/English content and JourneyShell; welcome with language, Start and explicit Listen controls | Arabic mobile and English desktop render; direction and focus order correct; no autoplay assumption |
| 2 | Large photographic crop choices and one-question conversation; explicit correction and confirmation of the protected 20 May 2027 berseem cut | All four crop identities and purposes clear; touch/keyboard route requires no typing; choosing or simulated recognition never confirms |
| 3 | Interactive four-season path, expanded season detail, fixture Promise Test and precise calendar inset | P0 rejected; maize 15 May conflict; assumed release 21 May plus seven days; 28 May/1 June need review; zero feasible alternatives; no invented shifted maturity |
| 4 | Recovery controls and focused browser refinement | Microphone denied/unavailable, interruption, ambiguity and audio failure preserve input; Arabic mobile/English desktop screenshots reviewed, then opposite combinations |

Stop and show this reference experience before expanding the frontend. Backend computation, real save/approval, full Season Replay and ML serving are outside this frontend milestone. This does not replace the architecture's later real-backend vertical-slice acceptance.

## Boundaries, assets and components

- Reuse the component definitions in DESIGN.md: JourneyShell, SpokenPrompt/AudioControls, CropChoice/AnswerChoice, ConfirmationSummary/ProtectedCommitment, FourSeasonPath/SeasonDetail, ConflictInset, PlanStatus and RecoveryNotice.
- Keep localized copy in `frontend/src/i18n`, journey state in `app`, view components in existing feature/shared folders, tokens in `styles`, and future replaceable speech/data adapters in `services`. Separate unconfirmed choices from explicit local demo confirmation and future server snapshots. Do not maintain duplicate API models; coordinate generated types with Yahya.
- UH-001 is a fixed illustrative reference, not a React planner. Mark fixture inputs/results visibly and in any audio. Changes outside that fixture invalidate its displayed result; do not show the old rejection or review conclusion as newly calculated. No fake requests, server save or approval claims.
- Voice UI states may be deliberately simulated and labelled as such. No microphone capture or live recognition claim. Use approved recorded prompts if available; otherwise state audio unavailable and show the recovery path. No provider selection. UI confirmation is not a persisted server confirmation.
- At implementation start, select locally recognizable crop photos and Readex Pro files with verified reuse rights. Record author/source/license/attribution and crop identity; do not assume search results are licensed. Crop assets and recorded prompts are not yet supplied or approved. Illustrations support the story without suggesting yield, water savings or suitability.

## Verification and handoff

Run actual configured type-check, lint, focused interaction tests and production build once the application exists. Exercise confirmation versus selection, edit invalidation, language preservation, keyboard navigation and speech-error recovery. Inspect real browser screens at 390 px Arabic and 1280 px English, then both languages at 320/768 px, zoom/reflow and reduced motion. Check contrast/focus and readable crop/date labels; preserve screenshots for review. Report unavailable checks rather than passing them on code inspection. Intended-user usability remains a separate unexecuted protocol in DESIGN.md.

- **Astra/Amr:** implement and present the scoped reference screens after the gate; own Arabic composition and accessibility review.
- **Sol:** extend the reviewed components and integrate typed results after the first-screen review; do not expand or redesign early.
- **Karim:** implement deterministic Promise Test and constraint tests, including rejected UH-001 and unresolved checks, without manufacturing feasible repairs.
- **Yahya:** implement the existing five initial endpoints, immutable snapshots/revision checks and Pydantic/OpenAPI-generated frontend types; integrate with Sol. No new endpoints required.
- **Moaaz/Refaat:** verify crop imagery and explanation meaning; prepare approved assets without implying scientific outcomes.

Current runnable status: placeholders only; there is no package manifest or application start command. Nothing is integrated or simulated in a running UI yet. The scope, components, scientific fixture and validation sequence are ready to execute after the gate; runtime setup, asset licensing, implementation and browser evidence remain to be done.
