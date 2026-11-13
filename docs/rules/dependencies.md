# Dependency and supply-chain rules

**Read this if…** you're about to add, update or install a package (npm or Python), or run an installer.

Status: Approved 14 Nov 2026 (Yahya) · Owner: Yahya · Last reviewed 14 Nov 2026.

Agents follow these rules without being asked. A package is code that runs on our machines and in the app, so every
new package or version is treated as a security decision.

---

## 1. The rules

1. **Minimum age 14 days.** Never install or lock a package version published less than 14 days ago. This applies to
   indirect (transitive) packages too, and to tools such as pnpm and pip themselves.
2. **Exact versions.** Direct dependencies are pinned to one exact version (`1.2.3`, never `^1.2.3`, `~`, `>=` or `latest`).
3. **Hashed lock files, committed.** `frontend/pnpm-lock.yaml` (integrity hash per package) and
   `backend/requirements.lock` (sha256 per file). Install only from the lock file.
4. **No install scripts.** Python installs wheels only (no `setup.py` runs). pnpm 10 blocks dependency install scripts;
   allowing one needs a reviewed entry in `pnpm.onlyBuiltDependencies` and a note in the PR.
5. **Pinned tools.** pnpm comes only through corepack at the version and sha512 hash in `frontend/package.json`
   (`packageManager`). Don't use a global `pnpm`, `npx <tool>@latest` or `pip install --upgrade pip`.
6. **Few dependencies.** Prefer the standard library and what is already installed. A new package needs a reason in the
   PR: what it does, who maintains it, how many indirect packages it brings, and that it passes the age check.
7. **Fail closed.** If a registry lookup, hash or age check fails, stop and report it. Don't retry with checks turned off.
8. **No secrets in packages or config.** Keys live only in local git-ignored `.env` files (see `backend/.env.example`).

## 2. How each rule is enforced

| Where | Setting | Effect |
|---|---|---|
| `frontend/.npmrc` | `minimum-release-age=20160` (minutes) | pnpm ≥ 10.16 refuses versions younger than 14 days while resolving, including transitive ones |
| `frontend/.npmrc` | `save-exact=true` | `pnpm add` writes exact versions |
| `frontend/package.json` | `"packageManager": "pnpm@10.34.9+sha512.…"` | corepack downloads that pnpm and checks its hash before running it |
| `backend/pip.conf` (copied to `backend/.venv/pip.conf`) | `uploaded-prior-to = P14D` | pip ≥ 26.2 ignores files uploaded less than 14 days ago |
| `backend/pip.conf` | `only-binary = :all:`, `require-hashes = true` | wheels only; every install needs a matching sha256 |
| `backend/requirements.lock` | exact versions + all sha256 hashes, includes `pip==26.2.2` | the venv is rebuilt from the lock alone (`--no-deps`) |
| `scripts/check_dependency_age.py` | checks both lock files | fails on a missing hash, a non-exact direct npm version, or a locked version younger than 14 days |

## 3. Commands

```sh
# Frontend: install exactly the lock (pnpm via corepack, hash-checked)
cd frontend && COREPACK_ENABLE_DOWNLOAD_PROMPT=0 corepack pnpm install --frozen-lockfile

# Backend: create the venv from the lock
python3 -m venv backend/.venv && cp backend/pip.conf backend/.venv/pip.conf
backend/.venv/bin/pip install --require-hashes --no-deps --only-binary :all: -r backend/requirements.lock

# Before every commit that touches a lock file
python3 -I scripts/check_dependency_age.py
```

**Adding or updating a Python package:** edit `backend/requirements.in` (exact pin, version ≥ 14 days old), resolve in a
throwaway venv under the config (`PIP_CONFIG_FILE=backend/pip.conf … pip install --no-require-hashes -r backend/requirements.in`),
then regenerate the lock with `scripts/lock_python.py` (it records each upload date) and rebuild the venv from it.

**Adding or updating an npm package:** `corepack pnpm add -E name@x.y.z` (version ≥ 14 days old); pnpm applies the age
rule to everything it pulls in. Review the lockfile diff for new indirect packages.

Then run the age check, and say in the commit/PR what was added and why.

## 4. Incidents

| Date | What happened | Fix |
|---|---|---|
| 14 Nov 2026 | Before pnpm was pinned, `corepack pnpm --version` downloaded and ran the latest pnpm (12.18.0, newer than 14 days) to print its version. | Removed it from the corepack cache; pinned pnpm 10.34.9 by hash. |
| 14 Nov 2026 | The first backend install pulled 4 indirect Python packages younger than 14 days (`annotated-doc`, `anyio`, `click`, `typing-inspection`). | Re-resolved under `uploaded-prior-to = P14D`, locked with hashes, rebuilt the venv from the lock. |
