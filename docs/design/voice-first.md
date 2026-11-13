# Voice-first interaction plan and page labs (UX Phase 4)

**Read this if…** you're designing or building any screen's voice behaviour, or reviewing the Phase 4 labs.

Status: Proposed 13 Nov 2026 by Yahya, needs Amr's review · Owner: Amr · Last reviewed 13 Nov 2026.

Builds on [design.md](design.md) (interaction, accessibility, status language) and [fieldlight.md](fieldlight.md) (visuals); it changes neither. Evidence: [voice-first research report](../reports/2026-11-13-voice-first-research.md). Labs: [work/ux-phase-4/](../../work/ux-phase-4/index.html).

---

## 1. The product flow these labs cover

The farmer says or taps what they will grow in each of the four seasons and what must stay. The app reads it back, the farmer confirms once, and the deterministic **Promise Test** checks the plan. It explains any conflict, shows **at most two** rule-checked alternatives (zero is a valid answer), and lets the farmer save for review with a spoken takeaway. Past weather (NASA history) and the 7-day outlook are optional side views.

**ML never fixes conflicts, shifts dates or ranks plans.** Date changes and alternatives come only from the planner rules; the outlook is context for near-term actions on a plan that already holds (decisions 11 and 13 Nov; confirmed by Yahya 13 Nov 2026 for this plan). UI copy says "check the plan", never "AI optimises".

| Lab | Page | Main job |
|---|---|---|
| 00 | Voice dock (shared) | Every voice state in words; push-to-talk; barge-in; fallback |
| 01 | Welcome | Silent first screen, Start unlocks audio, two intentions, practice turn |
| 02 | Choose crops per season | One question per screen; pictures + mic; staged dates; never assume a year |
| 03 | Readback & protect | Grouped readback; "must this stay?"; one explicit confirm |
| 04 | Promise Test | Conflict first, what is kept, exact date inset, three next steps |
| 05 | Alternatives | Zero/one/two feasible; review dates separate; inspect → draft → reconfirm |
| 06 | Past weather | What history shows and does not; honest unavailable |
| 07 | Next 7 days | Experimental outlook as a side note; four contract statuses |
| 08 | Save & takeaway | Plan status vs save status; takeaway for the exact version |

## 2. Voice rules (proposed)

1. **Push-to-talk, one utterance per press.** No always-listening. Android Chrome has no on-device Web Speech and unreliable continuous mode (report, browser section).
2. **Same question, two ways to answer.** Pictures and the mic are on screen together. Touch alone completes every page (design §1).
3. **One dock, one place for all audio,** at the bottom: [Repeat/Stop] [what is happening, in words] [mic]. Every state is named in words: ready, speaking, listening, working it out, didn't hear, didn't understand, mic off, sound off.
4. **The screen shows what the voice says.** Where the headline already is the spoken sentence, no duplicate caption; otherwise a caption shows the words.
5. **Confirm implicitly, commit explicitly.** A single answer is said back and shown as "I heard … · Change", then the app moves on. A multi-fact sentence gets a check card. The whole snapshot gets one explicit confirm with a clear intent ("confirm"), not a bare "yeah" (design §3 already keeps answers as proposals until the final readback).
6. **Two misses, then pictures.** First miss: short reprompt with an example. Second: pictures become the main route; the mic stays available.
7. **Ask for the mic on first tap,** after one spoken line on why and that audio is sent to be understood. Never on arrival, never again after a refusal.
8. **Interruptible.** A mic tap stops speech first; speech and listening never overlap; language switch and material edits stop old audio.
9. **Tap to hear** on every picture and status, with its own button (never nested in the answer button).
10. **No free advice.** Off-script questions ("what should I plant instead?", "which is best?", "how much should I irrigate?") get fixed templates that redirect.
11. **Clarify ambiguous words with pictures,** e.g. "ذرة" → maize or sorghum. Never guess a crop, date, year or unit.

## 3. Layout rules (proposed)

- **One step = one screen. No scrolling** at 390×760 (phone) or in an 820-px-tall desktop frame. Raised by Yahya 13 Nov after Phase 3 needed a lot of scrolling.
- During questions the four seasons are a compact top strip (phone) or a side column (desktop); the full path appears on review steps. Desktop review uses Fieldlight's arched cards in one row.
- Cards align on a fixed grid: picture | text | action, centred vertically; dates never wrap mid-date; equal-height cards with actions on one baseline.
- Targets stay at design.md sizes: 48 px minimum, 56–60 px primary, 84 px mic (76 px on phone).

## 4. What the labs are and are not

Static HTML in `work/ux-phase-4/` sharing `lab.js`/`lab.css`, using the Phase 3 fonts and the UH-001 fixture. Each lab has a state picker, a farmer-utterance simulator, problem injection (silence, not understood, mic denied, sound unavailable), Arabic/English, phone width and optional real browser voice (labelled; quality varies). Recognition, planning, forecasts and saving are simulated. Crop drawings are placeholders. Arabic wording is draft for native Egyptian review.

Verified 13 Nov 2026: `node work/ux-phase-4/check-labs.cjs` passes. A local headless-Chromium run (not in the repo) stepped every state in both languages at 1280 px and 390×760 with no script errors, no horizontal overflow and no step needing scroll. Not verified: real devices, real speech recognition, screen readers, farmer comprehension.

## 5. Open questions

1. ~~Recorded voice vs browser TTS.~~ **Decided 13 Nov (Yahya): audio is generated with ElevenLabs** from the reviewed templates; see [voice-generation.md](../backend/voice-generation.md). Still open: which Egyptian Arabic voice (Amr signs off).
2. **Recognition vocabulary.** Constrain to crops, months, numbers, yes/no/confirm? Needs an ar-EG trial on Android phones near Sakha (design §7 already calls for it).
3. **Feasible badge colour** `#245C45` sits close to action green `#17634B`. Keep (words + icon carry meaning) or change?
4. **Practice turn** on first use: keep, shorten, or replace with a facilitator demo?
5. **Desktop parity:** confirm the side-column season context during questions is acceptable to Amr.
