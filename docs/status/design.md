# Status: design / UX

**Read this if…** you're asking "which design is approved and what's still open?"

**As of **, last commit `0122e92`. Owner: Amr. If this is far behind `git log`, trust git.

---

## Approved

| What | Date | Where |
|---|---|---|
| Season Path interaction model ("Show, Speak, Choose, Confirm") | 11 Nov | [design.md](../design/design.md) §1, §3–§6 |
| UX Phase 1 + five refinements | 11 Nov | [ux-phase-1.md](../design/ux-phase-1.md) |
| Fieldlight Hybrid visual identity (arched botanical season cards) | 12 Nov (confirm, Q8) | [fieldlight.md](../design/fieldlight.md), `work/ux-phase-3/fieldlight-hybrid.html` |

`design.md` §2 (sand/terracotta palette) is **superseded** by Fieldlight. Its interaction,
accessibility and status-language sections still apply.

**13 Nov:** `work/ux-phase-3/` restored to `main` from the handoff branch (`0122e92`). It had
been dropped by a `/work/*` ignore rule. Content unchanged except two links to renamed docs
(now `docs/design/fieldlight.md`, `docs/reports/phase-3-visual-options.md`). Verified:
`check-hybrid.cjs` and `check-preview.cjs` pass. No browser check run.

## In flight

- **Voice-first page labs (UX Phase 4)**, proposed 13 Nov by Yahya, for Amr's review:
  [voice-first.md](../design/voice-first.md), `work/ux-phase-4/index.html`. Nine labs (voice dock +
  eight pages), one step per screen with no scrolling. Verified 13 Nov: `check-labs.cjs` passes; a
  local headless-Chromium run of every state (AR/EN, 1280 px and 390×760) had no script errors,
  overflow or scrolling. Not verified on devices, with real speech or with farmers.
- **13 Nov, round 2 after Yahya's review** ([voice-first.md](../design/voice-first.md) §3–§4): less text and
  one idea per screen, a shared four-season strip, coloured crop pictures, digits on screen, lab 03 cut to
  “what must stay?”, labs 05–08 simplified, logo added in `media/brand/`. Verified the same way: `check-labs.cjs`
  passes; headless-Chromium run of all 33 states (AR/EN, 1280 px and 390×760) has no script errors, overflow
  or scrolling. Not verified on devices, with real speech or with farmers.
- **13 Nov, round 3:** lab 01 practice mic is a tappable picture (simulated result); lab 02 shows the season as the
  headline and limits dates to the season's months (placeholder windows, open question 6 in voice-first.md) and to
  dates after today. Same checks pass.

## History of the design rounds

V1 → V2 → V3 wireframes (12 Nov) → three visual options → Fieldlight Hybrid. Reviews:
[V2](../reports/-wireframe-v2-review.md), [V3](../reports/-wireframe-v3-review.md),
[visual options](../reports/-phase-3-visual-options.md).

## Not done

- Real-browser check of the final prototypes in both languages at phone and desktop width.
- Real crop photographs (the botanical SVGs are placeholders); crop recognition test.
- The proposed six-person farmer usability protocol ([design §8](../design/design.md)) has not run.
