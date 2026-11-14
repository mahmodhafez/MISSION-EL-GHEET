"""Fail if any locked dependency was published less than MIN_DAYS ago (docs/rules/dependencies.md).

- frontend: every pnpm-lock.yaml entry must carry an integrity hash; the DIRECT dependencies in package.json
  are checked against npm publish times. Transitive npm packages are age-limited by pnpm itself while
  resolving (.npmrc minimum-release-age), so they are not re-fetched here (full npm records are large).
- backend: every requirements.lock entry must have sha256 hashes and is checked against PyPI upload time.
Network or registry errors fail closed. Stdlib only.

  python3 -I scripts/check_dependency_age.py            # 14 days
  python3 -I scripts/check_dependency_age.py --days 21
"""
import argparse
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent


def get_json(url: str, attempts: int = 3) -> dict:
    """Up to 3 tries for flaky networks; still fails closed if every try fails."""
    for i in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except OSError:
            if i == attempts - 1:
                raise
            time.sleep(2 * (i + 1))
    raise RuntimeError("unreachable")


def npm_entries(lock: pathlib.Path):
    """Yield (name, version, has_integrity) from the `packages:` section of a pnpm v9 lockfile."""
    text = lock.read_text(encoding="utf-8")
    section = text.split("\npackages:\n", 1)[1].split("\nsnapshots:\n", 1)[0]
    for block in re.split(r"\n(?=  \S)", section):
        m = re.match(r"\s*'?(@?[^@'\s]+)@([^':(\s]+)'?:", block)
        if m:
            yield m.group(1), m.group(2), "integrity:" in block


def pypi_entries(lock: pathlib.Path):
    text = lock.read_text(encoding="utf-8")
    for m in re.finditer(r"^([A-Za-z0-9_.\-]+)==([^\s\\]+) \\\n((?:\s+--hash=sha256:[0-9a-f]{64}(?: \\)?\n?)+)", text, re.M):
        yield m.group(1), m.group(2), True


def npm_time(name: str, version: str) -> str:
    meta = get_json("https://registry.npmjs.org/" + urllib.parse.quote(name, safe="@"))
    return meta["time"][version]


def pypi_time(name: str, version: str) -> str:
    files = get_json(f"https://pypi.org/pypi/{name}/{version}/json")["urls"]
    return min(f["upload_time_iso_8601"] for f in files)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    days = ap.parse_args().days
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    jobs = []
    npm_lock, py_lock = ROOT / "frontend" / "pnpm-lock.yaml", ROOT / "backend" / "requirements.lock"
    if npm_lock.exists():
        entries = list(npm_entries(npm_lock))
        unhashed = [(n, v) for n, v, h in entries if not h]
        for n, v in unhashed:
            print(f"FAIL npm {n}@{v}: no integrity hash in pnpm-lock.yaml")
        pkg = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
        direct = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        for n, v in direct.items():
            if not re.fullmatch(r"\d+\.\d+\.\d+", v):
                print(f"FAIL npm {n}: '{v}' is not an exact version")
                unhashed.append((n, v))
        jobs += [("npm", n, v, True, npm_time) for n, v in direct.items()]
        print(f"npm lockfile: {len(entries)} entries, {len(entries) - sum(1 for e in entries if not e[2])} with integrity hashes")
        if unhashed:
            return 1
    if py_lock.exists():
        jobs += [("pypi", n, v, h, pypi_time) for n, v, h in pypi_entries(py_lock)]
    if not jobs:
        print("no lock files found")
        return 1

    def check(job):
        eco, name, version, hashed, when = job
        try:
            t = datetime.fromisoformat(when(name, version).replace("Z", "+00:00"))
        except Exception as e:  # network or registry error: fail closed
            return eco, name, version, None, f"lookup failed: {e}"
        problem = "no integrity hash" if not hashed else (f"published {t:%Y-%m-%d}, younger than {days} days" if t > cutoff else "")
        return eco, name, version, t, problem

    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(check, jobs))
    bad = [r for r in results if r[4]]
    newest = max((r for r in results if r[3]), key=lambda r: r[3])
    counts = {e: sum(1 for r in results if r[0] == e) for e in ("npm", "pypi")}
    for eco, name, version, _, problem in bad:
        print(f"FAIL {eco} {name}@{version}: {problem}")
    print(f"{'FAIL' if bad else 'PASS'}: {counts['npm']} npm + {counts['pypi']} PyPI locked packages; minimum age {days} days; "
          f"newest {newest[1]}@{newest[2]} ({newest[3]:%Y-%m-%d}).")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
