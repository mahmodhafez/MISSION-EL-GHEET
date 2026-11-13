# Wireframe V2 — review notes

. Revised the existing [Phase 2 wireframe](../../work/ux-phase-2/season-path-wireframes.html) after a screen-by-screen V1 critique. Season Path remains the identity. This is an interactive grayscale design artifact, not React/application implementation, high-fidelity approval, live speech, a planner or persistence.

## Critique → changes

The three perspectives below are design evaluations, not findings from interviews or usability tests.

| V1 screen | Classification | Non-reading farmer | Reading farmer | Agricultural engineer | V2 change |
|---|---|---|---|---|---|
| Welcome | REPLACE entry; REMOVE duplicate listening | Abstract route choices precede understanding; audio icons absent | Multiple setup decisions slow entry | No extra mode/account needed | One Start action, one large speaker; optional commitment-first shortcut inside intake |
| Crop/intake | IMPROVE; REMOVE repeated purpose/protection pages | Crossed image boxes give no crop cue; mic feedback is a notice | Repeated crop/purpose/protection questions | Date/edit controls do not meaningfully change values | Approximate distinct crop drawings, combined crop/purpose choices; large mic/speaker; one protection step; working date choices/typing and area/preparation edits |
| Confirmation | REPLACE three-page review | Long readback groups and repeated navigation burden recall | Three pages before a separate timeline/check | Precision needed, but not all expanded at once | One summary, expandable season/context details, correction, one explicit confirmation; confirmation is never planting approval |
| Four-season path | KEEP; IMPROVE; REMOVE mandatory stop | Long date list dominates crop sequence | Extra page duplicates review | Exact sowing/end/release still needed | Optional overview with numbered crop drawings and per-season date disclosure; return to prior context |
| Promise Test / investigations | IMPROVE | Arithmetic arrives before the central conflict is clear | Too many competing continuation actions | Must retain assumptions, missing endpoints and status | Crop/date conflict first; calendar arithmetic in disclosure; review status prominent; Return is primary during inspection, adoption separately disclosed |
| NASA Season Replay | KEEP; IMPROVE | Jargon and open technical explanation dominate | Optional feature should be quick to understand/leave | Source, method, units and shared-period constraints matter | Short purpose and honest unavailable state; engineer details collapsed; exact investigation/date context restored on return |
| Evidence Card | IMPROVE; REMOVE extra post-save playback | Saved can sound like safe to plant | Repeated audio and diagnostic controls distract | Same version, sources and outstanding checks required | One speaker, distinct plan/storage statements; save success/failure explicitly simulated; no approval or fabricated calculation |

Shared changes: speaker icon above **اسمع**; microphone above **جاوب** or **اتكلم**; no voice/manual mode selection. One primary decision at a time, visible selection feedback, substep-aware Back, retained manual corrections and focus restoration. Reviewer screen navigation and voice-state injection are outside the farmer flow. The optional state sheet keeps feasible separate from Hussein and separates save failure from plan rejection.

## Inspect V2

Open `work/ux-phase-2/season-path-wireframes.html` directly in a local browser; no server, install or network is needed. `preview.html` is an identical standalone copy included in the publication checkpoint so the parity check also runs from a clone. Start follows the touch journey; Review tools expose individual screens and seven voice states. Mobile/Desktop buttons change the review composition. “اسمع” exposes the proposed spoken script; it does not play sound. Microphone states are simulated; no permission or recording occurs.

Suggested review: Start → select berseem → protect 20 May 2027 → maize → wheat → sorghum → context → summary → explicit confirmation → rejected P0. Inspect either date, visit NASA replay and return, then leave without changes. Separately try adoption: it produces an unconfirmed draft and withholds old results. Review the simulated save and failure states. Manual changes invalidate both the old result and its spoken script.

## Verification and limits

- `node work/ux-phase-2/check-wireframes.cjs`: syntax and minimal-DOM navigation/state checks pass. Coverage includes seven views, one speaker per view, the touch route, Back, explicit confirmation, speech proposals/failures, inspection/adoption, replay return, manual edits, invalid dates/quantities, stale-result/audio guards, optional protection, save/failure separation, twelve state examples, desktop switching, preview parity and no network/mic/storage calls.
- These checks do **not** measure actual rendering, Arabic shaping, touch size, contrast, screen-reader output, audio or user comprehension. V1-specific expectations were replaced for the deliberately revised flow; a real empty-selection invalidation bug was found and fixed.
- Browser inspection could not run: the Playwright import failed with a missing default export; browser access host was unavailable; Computer Use then stopped because it could not confidently determine Brave's current URL to enforce policy. No alternate browser automation was attempted after that stop. No screenshots or browser-pass claims.
- Crop drawings are low-fidelity placeholders, not verified recognition assets. Real crop photography, native Egyptian wording/comprehension, exact voice timing and English parity need later review. English is explicitly marked as a later preview, not presented as working translation.
- This is a bounded Hussein walkthrough. Other crop selections are visibly outside the fixture and do not inherit its result; the generic intake/crop-lock-change flow is not implemented. No actual read-free completion, speech, save, scientific calculation or agricultural outcome is validated.

## Decisions for this review

Approve or revise the single-summary confirmation, combined crop/purpose choices, optional season overview, and secondary explicit adoption action. Test whether farmers understand the distinction between “needs agricultural review” and “safe to plant” before advancing fidelity. Preserve P0 rejected, R1/R2 needs_review, zero validated alternatives. Stop for user review before Phase 3.
