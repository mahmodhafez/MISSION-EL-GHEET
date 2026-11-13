# Working rules

**Read this if…** you're about to change anything in this repo, as a person or an agent.

Last reviewed  (Yahya). Replaces the old root `AGENTS.md` rule list.

---

## 1. Scope: change only what was asked

- Touch only the files the task names or clearly needs. No drive-by refactors, renames or
  restyling.
- Each area has an owner (`docs/team.md`). To change someone else's area, ask them or open a PR
  they review. Don't fix it quietly.
- **If a change would alter an approved spec, contract or screen design, stop.** Describe the
  before/after and wait for the owner.
- Plan first for anything bigger than a small fix: a short written plan, approved before you code.

## 2. Honesty: say what is true, not what is hoped

These docs were once full of statements that sounded finished but weren't. The planning docs
of 12 Nov assumed backend code existed; it was documentation only. Write so that can't happen again.

- Separate **documented**, **built**, **tested** and **scientifically supported**. They are four
  different claims.
- Report what you actually ran, with the command and result. If a check was skipped or failed,
  say so.
- Never upgrade "should work" to "works", or "built" to "verified", unless you saw it run.
- Fixtures and mock data are labelled as fixtures in code, UI and docs. A network failure must
  never fall back silently to a successful mock.

## 3. Science and data (non-negotiable)

- Never fabricate observations, crop coefficients (Kc), growth stages, dates, yields, irrigation
  savings or soil benefits. Missing evidence becomes `unknown` / `needs_review` with a reason.
- Unknown is not zero. Unknown salinity stays unknown; unknown preparation days are not 0.
- ET0 (FAO-56 with the ASCE daily cloudiness bound) is **reference** atmospheric demand, not
  irrigation use. Report ETc as unavailable unless sourced coefficients and stages exist.
- Keep NASA POWER metadata, units and **LST** day labels. Don't shift weather days through
  Egyptian daylight-saving time.
- Frozen evidence files (the validation ZIP, `data/validation/audit_weather.py`, the
  `docs/reports/` files) are byte-preserved. Don't edit, reformat or regenerate them.
- Published Sakha trial soil is a research profile, never the farmer's field.
- Negative results stay recorded. Seasonal climatology beat the fine-tuned Chronos-2/LoRA model,
  and nobody may hide or reword that.

## 4. Planner and backend

- The planner is deterministic and pure: no I/O, HTTP, database, weather or ML calls inside it.
- Plan status is exactly `feasible | rejected | needs_review`. Hard failures beat unknowns.
- Protected farmer commitments are never relaxed silently. Lock changes need explicit confirmation.
- Zero alternatives is a valid answer. Offer at most two feasible alternatives; never invent a third.
- No combined "best farming score". Explain trade-offs instead.
- Speech and transcripts only *propose* facts. Silence or recognition alone never confirms.
- ML/forecast output can't create crop eligibility, change locks or validate a rotation.
- Explanations come from authored bilingual templates (`code` + `params`), never free text from a model.

## 5. Frontend

- Arabic RTL and English LTR have equal function. Use logical CSS properties.
- The primary journey needs no typing; touch, pictures and voice cover it. Speech is never the only way.
- Follow the approved visual system (`docs/design/fieldlight.md`) and interaction model
  (`docs/design/design.md`). New visual variants need Amr's approval.
- No agricultural rules in React. The UI shows backend/core results; it doesn't compute them.

## 6. ML

- Chronological train/validation/test splits; no future information in inputs.
- Compare against seasonal climatology and persistence before claiming anything.
- The 2026 Jul–Oct assessment period is already consumed and can't serve as a fresh test.
- Record real parameter updates and metrics, or nothing.

## 7. Dependencies, secrets and privacy

- Add a dependency only when the task needs it, and pin its version. Note it in the PR.
- Secrets live in `.env` (git-ignored). Commit only `.env.example` with names, never values.
- Don't upload or commit real farmer recordings or personal data. Demos use synthetic scenarios.
- No paid service, speech provider or hosting is approved yet. Ask before signing up for anything.

## 8. Verification before you call it done

- Run the tests for what you touched (commands in `AGENTS.md`).
- For UI: open it in a real browser, in both Arabic and English, phone and desktop width.
- For shared contracts: check every consumer still validates.
- Write down anything you could not run, and why.
