"""Inspect commit candidates for size, duplication, secrets and workspace coupling.

No file content or matched secret values are included in the report. This is a
bounded pattern scan, not a claim that no possible credential can exist.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

from .update_package_manifest import candidates

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b"),
    "openai_project_key": re.compile(r"\bsk-proj-[A-Za-z0-9_-]{25,}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential_assignment": re.compile(r'''(?im)^\s*(?:api_key|secret_key|access_token|password)\s*[:=]\s*["'][^"'\s]{16,}["']'''),
}


def audit():
    sizes, groups, findings, paths = [], defaultdict(list), [], []
    excluded = {"reports/qa/p0_repository_audit.json"}
    for name, path in candidates():
        if name in excluded:
            continue
        payload = path.read_bytes()
        sizes.append({"path": name, "bytes": len(payload)})
        groups[hashlib.sha256(payload).hexdigest()].append(name)
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeError:
            continue
        for category, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append({"path": name, "category": category})
        if (path.suffix == ".py" and name != "scripts/audit_repository.py" and
                name.startswith(("agricultural_kb/", "climate_data/", "examples/", "scripts/"))):
            if re.search(r"[A-Za-z]:[\\/]Users[\\/]|/Users/|/home/[^/\s]+/", text):
                paths.append(name)
    sizes.sort(key=lambda s: (-s["bytes"], s["path"]))
    return {"scope": "versionable candidates, excluding generated outputs and this report",
            "files_scanned": len(sizes), "total_bytes": sum(s["bytes"] for s in sizes),
            "largest_files": sizes[:10], "over_10_mb": [s for s in sizes if s["bytes"] > 10_000_000],
            "byte_identical_groups": sorted([names for names in groups.values() if len(names) > 1]),
            "credential_pattern_findings": findings, "runtime_absolute_user_paths": paths,
            "git_directory_present": (ROOT / ".git").exists(),
            "scientific_files_deleted": False,
            "limitation": "Pattern-based scan of commit candidates; private research reference URLs are retained as provenance."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))
    if result["credential_pattern_findings"] or result["runtime_absolute_user_paths"]:
        raise SystemExit(1)
