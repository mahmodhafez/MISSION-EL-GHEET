# Fieldlight + botanical season arches

**Read this if…** you're choosing colours, type, spacing or the season-card look.

Status: Approved  (confirm, status Q8) · Owner: Amr. Last reviewed .

Open [the hybrid preview](../../work/ux-phase-3/fieldlight-hybrid.html). The [three original options](../../work/ux-phase-3/index.html) and earlier wireframes are kept for reference. (This doc originally said "pending approval"; it's logged as approved on 12 Nov, see [decisions](../decisions.md).)

| Before | Refined treatment | Why |
|---|---|---|
| Fieldlight’s small four-column crop sequence | Generous botanical arches on desktop; connected vertical rows with arched portraits on phones | Makes the seasons memorable without shrinking labels or controls. |
| Voice buttons share the question’s open space | A dedicated pale-green voice panel, large speaker/mic symbols and 112px-tall controls | Listening and speaking are first-class actions, alongside touch. All audio remains simulated. |
| Repeated compact labels and long desktop content | Larger dates/status labels, open candidate rows and a separate next-step panel | Distinguishes commitments, review investigations and the farmer’s next action. |

## Visual rules

- Keep Fieldlight’s canvas **#F4F8F3**, white surfaces, ink **#16352B**, action **#17634B**, hover **#104D3A**, supporting ink **#496459**, botanical accent **#D6E7A3**, and focus **#1849AD**. New botanical portrait ground: **#EDF3E4**. Green actions never signify agricultural approval.
- Retain independent semantic colours: protected **#283F73 / #EDF0FA**; rejected **#9C3027 / #FBEDE9**; review **#805000 / #FFF2D5**; unknown **#4D5864 / #EEF1F4**. Each includes a symbol and explicit wording.
- Use the existing local **Noto Sans Arabic** for Arabic and **Readex Pro** for English, with Tahoma/Arial fallbacks. No new downloads. Arabic body 20px; questions 28px mobile / 36px desktop; season names 21–22px; essential statuses at least 16px. No Arabic letter spacing or fixed-height text clipping.
- Reserve arches for botanical season portraits. Ordinary panels/buttons use 12px corners. Desktop cards have a 120px rounded top; mobile portrait windows use a 56px rounded top. Text and controls sit outside the curved area.
- Above 1000px, four season cards share the row. At 701–1000px, use two columns. At 700px and below, use one vertical path: a 96px botanical portrait beside flexible text, with 48px-minimum detail controls. Narrower layouts reduce image width before text size. The **Phone width** review control demonstrates this treatment independently of the browser width.
- Voice controls are 112px tall; primary actions at least 60px; detail controls at least 48px. Focus is a visible 3px blue outline. Selection retains explicit labels/borders; disabled controls retain legible reasons. Existing error, unknown, simulation and reduced-motion handling are reused. No decorative motion added.
- Promise Test uses a restrained red same-field panel with two large dates. Its blue protected commitment remains separate. Historical evidence uses a solid teal archive rule and dated provenance; future outlook keeps a dashed, explicitly uncertain treatment. Empty plots contain no invented series or values.

## Scope and science

The preview opens on the refined planner. Its screen selector also exposes Promise Test, NASA Season Replay, welcome/intention, intake, comparisons and Evidence Card using the same system. Both entry intentions are retained: check an existing plan or explore from needs and known constraints. Exploration shows unknown slots, not a fabricated generated schedule. Candidate dates in the Hussein example remain investigations, never feasible recommendations.

Hussein remains P0 rejected, 20 May 2027 cut protected, 15 May maize conflicting, 28 May and 1 June requiring agricultural review, zero validated feasible repairs. NASA history remains 2001–2025 regional evidence with unconnected numeric display; ET0 is reference atmospheric demand, not irrigation. Full paired comparison is unavailable. Speech, planning and save actions are visual simulations; the Phase 2 wireframe remains the fuller interaction reference.

## Tokens, verification and handoff

[Hybrid token proposal](../../work/ux-phase-3/tokens.fieldlight-hybrid.proposal.json) records palette, typography, arch geometry, targets, breakpoints and state rules. It supersedes nothing until approval. Original `tokens.proposal.json` stays intact.

Minimal check: `node work/ux-phase-3/check-hybrid.cjs` covers syntax, local dependencies, requested screen templates, both intentions, bilingual rendering and key text/action colour pairs. These are template checks, not browser screenshots, physical-device testing, screen-reader testing or farmer usability validation. No new browser inspection was performed for this refinement.

After approval, the React team should implement the shared VoicePanel, BotanicalSeasonCard/SeasonPath, CommitmentStrip, InvestigationRow, HistoricalEvidencePanel and EvidenceCard using these tokens. Keep localized content, state and scientific providers separate. Begin with the three reviewed reference screens; do not infer planner rules from this preview. Crop drawings remain existing recognition placeholders and need farmer recognition review.

**Approval focus:** the Fieldlight/arch combination, vertical mobile path and voice panel hierarchy. Stop before React or further implementation.
