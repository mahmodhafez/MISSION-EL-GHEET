# How docs are organised and kept true

**Read this if…** you're writing, moving or updating any document.

Last reviewed  (Yahya).

---

## Where things go

| Kind of content | Goes in | Lifespan |
|---|---|---|
| How to work here | `docs/rules/` | Edited in place, by PR |
| What's built, in flight, next, blocked | `docs/status/<area>.md` | Changes nearly every session |
| Who owns what | `docs/team.md` | Edited when roles change |
| A settled decision | `docs/decisions.md` (one dated line + link) | Append-only |
| An idea turned down | `docs/rejected.md` | Append-only |
| Standing spec for an area | `docs/<area>/` (`product`, `science`, `backend`, `planner`, `ml`, `design`) | Kept current, edited in place |
| Evidence, audits, design reviews | `docs/reports/YYYY-MM-DD-<topic>.md` | **Frozen** once written |
| Superseded docs | `docs/archive/` | Never edited; kept for history |
| Term definitions | `docs/glossary.md` | Edited in place |

Index every new doc in `docs/README.md`.

## Every topic file opens the same way

```markdown
# Title

**Read this if…** <one sentence: who needs this>

Status: Approved <date, by whom> | Proposed | Draft · Owner: <name> · Last reviewed <date>.

---
```

## Writing rules

- **Short.** If a sentence restates a rule found elsewhere, replace it with a link. Don't repeat
  "this does not authorise X" disclaimers; the status line covers it.
- **Date everything**: decisions, approvals, builds, reviews. Use ``.
- **Say who decided.** "Amr approved Fieldlight (12 Nov)" is a decision; "we went with Fieldlight" is a guess.
- **Mark unverified things as unverified.** Built ≠ tested ≠ verified on a device.
- **One home per fact.** Status files link to specs; specs don't carry progress logs.
- **Same change, same commit.** Code that changes a documented fact updates the doc too.
- **Never write secret values**, only key names.
- Verification logs (which hashes matched, which checks ran) go in a dated report in
  `docs/reports/`, not into specs or status files. Status gets one line and a link.

## Status files (`docs/status/`)

Each area has its own status file, so two people never edit the same one. Each opens with:

```markdown
**As of **, last commit `abc1234`. If this is far behind `git log`, trust git.
```

Sections, in order: **Next up · In flight · Built and verified · Built, not verified ·
Designed/approved, not built · Known problems · Open questions.** Rules:

1. Update it in the same commit as the code.
2. Update the "As of" date and commit every time.
3. Date every status change ("built 14 Nov").
4. Only the person who saw it run moves something to "verified".
5. Move finished items down; trim when the file passes ~120 lines.

`docs/status/README.md` holds only cross-area items: phase, deadline, launch blockers, and
contradictions between docs. **Write contradictions down there rather than settling them quietly.**

## Conflicts between docs

When two docs disagree: the newer **dated decision** in `docs/decisions.md` wins, then the spec's
own override section (e.g. API contracts §0), then the newer spec. If it's still unclear, add it
to "Open questions" in `docs/status/README.md` and ask the owner. Don't pick one yourself.
