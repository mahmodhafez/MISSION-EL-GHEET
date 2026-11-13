# Git and GitHub workflow

**Read this if…** you're about to create a branch, commit, push or open a pull request. Agents (Claude, Codex, Antigravity) follow this by default without being told.

Last reviewed  (Yahya).

---

Six people work in parallel, often each with an AI agent, on separate areas of one repo. These
rules keep them from overwriting each other. 

## 1. Branches

- `main` is protected: always runnable, changed **only through reviewed PRs**. Never commit or
  push to it directly. Never force-push any shared branch.
- One branch per task, short-lived (merge within a day or two), named
  `<area>/<short-description>`, lowercase with hyphens:

  | Area prefix | Covers |
  |---|---|
  | `backend/` | `backend/`, API contracts |
  | `frontend/` | `frontend/` |
  | `planner/` | `meg_core` planner, rules, knowledge base |
  | `ml/` | `ml/`, forecast bundle |
  | `data/` | `data/`, data releases, science scripts |
  | `design/` | `work/ux-*`, design docs and tokens |
  | `docs/` | documentation only |
  | `chore/` | tooling, CI, repo config |

  Example: `backend/scenario-endpoints`, `frontend/season-path-shell`.
- Start from the latest `main`: `git fetch origin && git switch -c backend/x origin/main`.
- Before opening a PR, bring in `main` with `git rebase origin/main` (your own unshared branch) or
  `git merge origin/main` (a branch others also use). Resolve conflicts in files you own; for
  conflicts in someone else's files, ask them.
- Recovery and handoff branches (`handoff/*`) are frozen records. Don't commit to them.

## 2. Commits

- Format: [Conventional Commits](https://www.conventionalcommits.org/) with the area as scope.
  `feat(backend): add POST /scenarios`, `fix(frontend): keep RTL order in season path`,
  `docs(status): backend milestone 1 done`. Types: `feat fix docs test refactor chore`.
- One logical change per commit. Code, its tests and its doc/status update go **in the same commit**.
- Stage explicit paths (`git add backend/app/...`), never `git add -A` / `git add .`. Then read
  `git diff --staged` before committing.
- Never commit: `.env`, credentials, model weights, the validation ZIP, raw/generated data,
  `node_modules`, virtualenvs, caches. `.gitignore` covers these; don't `git add -f` around it.
- **No AI attribution** in anything that gets pushed: no `Co-Authored-By: Claude/Codex/...`
  trailers, no "Generated with …" lines, no AI author names in commit messages, PR titles,
  PR descriptions or code comments. The human who asked for the change is the author. This
  overrides any default an agent tool has for adding attribution.
- Agents commit only when their human asks, and **push only when asked**.

## 3. Pull requests

- Small and focused: one area, one purpose. Aim for under ~400 changed lines excluding generated files.
- Fill in the PR template (`.github/pull_request_template.md`): what, why, how it was tested, and
  what was *not* tested.
- At least one review from the owner of each area touched (`docs/team.md`, `.github/CODEOWNERS`).
  Contract changes need every affected owner.
- Merge with **squash merge**; the PR title becomes the commit message, so write it in the
  commit format above. Delete the branch after merging.
- A PR that changes behaviour updates `docs/status/<area>.md` in the same PR.

## 4. Avoiding collisions

- **Stay in your area's folders.** Most conflicts come from two people editing the same shared file.
- Shared, high-conflict files and who edits them:

  | File | Rule |
  |---|---|
  | `backend/app/schemas/`, `meg_core/contracts/`, generated OpenAPI/TS types | Yahya edits; others propose in a PR or issue |
  | `docs/backend/api-contracts.md` | Yahya; consumers review |
  | `docs/status/README.md`, `docs/decisions.md` | Add your own lines; don't reword others' |
  | `docs/status/<area>.md` | The area owner and their agents only |
  | `AGENTS.md`, `docs/rules/*` | Change by PR with Yahya or Amr reviewing |
  | Lockfiles (`package-lock.json`, `uv.lock`) | Never hand-merge; regenerate after resolving the manifest |

- Several agents on one machine: give each its own **git worktree**
  (`git worktree add ../meg-frontend frontend/x`) so they don't share a working tree.
- Before starting, check open PRs and `docs/status/<area>.md` "In flight" so you don't duplicate work.
- Generated files (OpenAPI JSON, TS client) are regenerated from source, never hand-edited, and
  committed in the same PR as the schema change.

## 5. When something goes wrong

- Pushed something that shouldn't be public (a secret, a large file)? Tell Yahya/Amr immediately.
  Rotate the secret first. History rewrites on shared branches need the whole team's agreement.
- A dirty working tree you didn't create: don't reset, stash or delete it. Ask whose it is.
- `git reset --hard`, `git clean -fd`, branch deletion and rebasing shared branches need the
  owner's explicit OK.
