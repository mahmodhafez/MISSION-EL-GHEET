# Voice-first interaction plan and page labs (UX Phase 4)

**Read this if…** you're designing or building any screen's voice behaviour, or reviewing the Phase 4 labs.

Status: Proposed 13 Nov 2026 by Yahya, needs Amr's review; implemented in the app 14 Nov (`frontend/`) · Owner: Amr · Last reviewed 14 Nov 2026.

Builds on [design.md](design.md) (interaction, accessibility, status language) and [fieldlight.md](fieldlight.md) (visuals); it changes neither. Evidence: [voice-first research report](../reports/2026-11-13-voice-first-research.md). Labs: [work/ux-phase-4/](../../work/ux-phase-4/index.html).

---

## 1. The product flow these labs cover

The farmer says or taps what they will grow in each of the four seasons and what must stay. The app reads it back, the farmer confirms once, and the deterministic **Promise Test** checks the plan. It explains any conflict, shows **at most two** rule-checked alternatives (zero is a valid answer), and lets the farmer save for review with a spoken takeaway. Past weather (NASA history) and the 7-day outlook are optional side views.

**ML never fixes conflicts, shifts dates or ranks plans.** Date changes and alternatives come only from the planner rules; the outlook is context for near-term actions on a plan that already holds (decisions 11 and 13 Nov; confirmed by Yahya 13 Nov 2026 for this plan). UI copy says "check the plan", never "AI optimises".

| Lab | Page | Main job |
|---|---|---|
| 00 | Voice dock (shared) | Every voice state in words; push-to-talk; barge-in; fallback |
| 01 | Welcome | Logo + Start (audio unlock), two picture choices, practice turn |
| 02 | Choose crops per season | Clickable four-season strip on top; a few words + pictures per question; never assume a year |
| 03 | What must stay | Lock what must not change; field facts as pictures; one explicit confirm |
| 04 | Promise Test | Conflict as two pictures; Why? as four steps; Other dates / Save |
| 05 | Other dates & alternatives | Zero/one/two feasible; dates to check; before/after; check again with a date |
| 06 | Past weather | One picture per screen; honest unavailable; meters not connected |
| 07 | Next 7 days | Side note; picture + few words per status; seven day tiles |
| 08 | Save & summary | Four crops, the one problem, one Save; full summary spoken |

## 2. Voice rules (proposed)

1. **Push-to-talk, one utterance per press.** No always-listening. Android Chrome has no on-device Web Speech and unreliable continuous mode (report, browser section).
2. **Same question, two ways to answer.** Pictures and the mic are on screen together. Touch alone completes every page (design §1).
3. **One dock, one place for all audio,** at the bottom: [Repeat/Stop] [what is happening, in words] [mic]. Every state is named in words: ready, speaking, listening, working it out, didn't hear, didn't understand, mic off, sound off.
4. **Short on screen, full in voice.** The screen shows the key words (crop, date, status) with pictures; the full sentence is spoken and can be replayed. Never a printed paragraph (Yahya, 13 Nov: “too much reading”).
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
- **Visual first, one idea per screen** (Yahya, 13 Nov round 2): a few words, a picture, at most one main action plus a way back. Details are spoken or behind “for the engineer”. If a screen needs a legend, it has too much on it.
- **The four seasons look the same everywhere:** a strip of four arched cards (crop picture, name, date with a cut or sow icon). It sits on top of every question in lab 02 at every width and is tappable; later screens reuse it for before/after and the summary.
- **Numbers are digits** (Arabic-Indic in Arabic) on screen; month names stay words. **Arabic year ranges read right-to-left: the earlier year sits on the right** (“٢٠٢٧/٢٠٢٦” on screen for winter 2026/27). Each year is its own `<bdi>` so its digits never break (Yahya, 14 Nov). English ranges stay left-to-right. The spoken `speech` variant still spells numbers (voice-generation.md §4).
- **Maize is “ذرة شامية” on screen,** never plain “ذرة”, which is ambiguous; the “which ذرة?” question appears only when the farmer *says* “ذرة”, never after a tap.
- **Crop pictures are coloured illustrations** (green clover with cream flowers, yellow cob, golden ear, red-brown grain head). Outline icons were too abstract. Real photos and a recognition test are still required.
- **Purpose is asked only when a crop has more than one** (berseem is always feed, wheat always grain in the labs). The list per crop is a placeholder for the crop catalogue.
- **The season is the headline** on every lab 02 question: a big winter (cloud) or summer (sun) card with “Season 1 of 4” and its years; the question sits smaller under it.
- **Dates are limited to the season and to the future.** Month buttons show only the season's months, each with its year, so touch input never asks for a year; months and days before today are disabled. A spoken date outside the season or in the past gets a one-line reason. **Placeholder windows:** winter October→May, summer April→October. The planner spec says crop profiles set the supported dates, so these windows need the planner owner's sign-off (open question 6).
- **The practice mic is the picture itself** (lab 01): tap, talk, tap again; the labs simulate the result and never open the real microphone.
- **Many crops (reviewed KB, 8 offerable):** all crops on one screen, never paged: row tiles (picture | name | 44 px listen
  button inset 8 px) in full rows, 2 columns below 820 px, 4 above. One "needs review" note beside the question instead of a
  badge per tile. Research-only crops (watermelon, strawberry, cantaloupe, harankash) are not selectable (no planner profile);
  showing them greyed as "still being studied" is an open option.
- **Arabic direction:** Back and forward arrows mirror in RTL; Arabic year ranges keep the earlier year on the right; Arabic
  decimals use "٫". Names never break inside a word; an icon stays on the same line as its date.
- **Every width, not just two:** the layout is checked at 360, 390, 430, 600, 650, 700, 768, 820, 900 (short), 1024 (short),
  1280 and 1440 px for clipped text, overlap, overflow, word breaks, buttons touching borders and scrolling.
- Logo: `media/brand/mission-el-gheet-logo.svg` (plus cream-gold and currentColor variants), supplied by Yahya 13 Nov.
- Targets stay at design.md sizes: 48 px minimum, 56–60 px primary, 84 px mic (76 px on phone).

## 3a. Planner output the labs follow (snapshot, still changing)

Checked 14 Nov 2026 against `origin/planner/candidate-generation` at `de081ab` (Milestones 1–2, Amr + Astra), by running `tools/planner_cli.py plan` on `uh001.json` and `synthetic-mixed.json`. **The planner team is still adding to this output (Yahya, 14 Nov); re-check the labs when it changes.**

| Planner output | Where it shows in the labs |
|---|---|
| Journey `check` vs `explore`; exploration needs explicit permissions + scope readback + `exploration_confirmed` | Lab 03: what must stay → what may change (date / crop chips) → “this is what we will check” → one confirm. “Nothing may change” = check only |
| Scope issues: `blocked` (e.g. `profile_binding_unavailable`), `excluded`; missing inputs | Lab 03 readback lines: “cannot be checked” (red dashed), “unknown” (grey dashed) |
| `current.status` + first reason `sowing_before_protected_cut` and `preparation_shortfall` (`earliest_sowing_date`) | Lab 04 conflict pictures; “Why?” steps |
| `feasible_alternatives` (≤2 shown), `review_investigations`, `rejected_candidates` | Lab 05 date cards (review), layout state (feasible) |
| `changes` (direct edit vs dependent; endpoints → unknown) | Lab 05 before/after strip; harvest “?” |
| Unknown checks driving `needs_review` (harvest mapping, irrigation, soil, cultivar…) | Lab 05 “why it needs review” tiles (top four; full list for the engineer) |
| `search.status` `incomplete` + `uninstantiated_choice_ids` | Lab 05 “not checked · search incomplete” line |
| Missing input `plan.s1.sowing_date` | Lab 02 asks the berseem sowing date (past allowed, “I don't remember” = unknown) |
| Assumptions, sources, policy `pending_team_review`, SYNTHETIC banner | Engineer details only (not on farmer screens yet) |



Static HTML in `work/ux-phase-4/` sharing `lab.js`/`lab.css`, using the Phase 3 fonts and the UH-001 fixture. Each lab has a state picker, a farmer-utterance simulator, problem injection (silence, not understood, mic denied, sound unavailable), Arabic/English, phone width and optional real browser voice (labelled; quality varies). Recognition, planning, forecasts and saving are simulated. Crop drawings are placeholders. Arabic wording is draft for native Egyptian review.

**Round 2 (13 Nov, Yahya's review):** intro screen removed; distinct intent pictures; centred buttons; lab 02 strip on top at all widths; purpose per crop; lab 03 reduced to one “what must stay?” screen (it used to re-read every season); digits on screen; calendar icon for dates; lab 04 conflict as pictures and Why? as steps; lab 05 “draft” screen replaced by “check again with this date?”; labs 06–08 rebuilt as calm one-picture screens.

Verified 13 Nov 2026 (after round 2): `node work/ux-phase-4/check-labs.cjs` passes. A local headless-Chromium run (not in the repo) stepped every state in both languages at 1280 px and 390×760 with no script errors, no horizontal overflow and no step needing scroll. Not verified: real devices, real speech recognition, screen readers, farmer comprehension.

## 5. Open questions

1. ~~Recorded voice vs browser TTS.~~ **Decided 13 Nov (Yahya): audio is generated with ElevenLabs** from the reviewed templates; see [voice-generation.md](../backend/voice-generation.md). Still open: which Egyptian Arabic voice (Amr signs off).
2. **Recognition vocabulary.** Constrain to crops, months, numbers, yes/no/confirm? Needs an ar-EG trial on Android phones near Sakha (design §7 already calls for it).
3. **Feasible badge colour** `#245C45` sits close to action green `#17634B`. Keep (words + icon carry meaning) or change?
4. **Practice turn** on first use: keep, shorten, or replace with a facilitator demo?
5. **Desktop parity:** confirm the side-column season context during questions is acceptable to Amr.
6. **Season month windows.** Which months count as winter and summer at Sakha for date input (placeholders above), and should they come from the crop profiles instead? Needs Karim (planner) and Amr.
