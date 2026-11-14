"""Explicitly record a new repository delivery manifest; never alters source data.

Run only after reviewing changes. Original manifest is verified before writing.
Generated outputs, archives, caches and local environments are never packaged.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .verify_legacy import verify

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache", ".mypy_cache",
                 ".ruff_cache", ".agents", ".codex", ".aws", ".vscode", "outputs", "dist", "build"}


def candidates(root=ROOT):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if (not path.is_file() or any(p in EXCLUDED_DIRS for p in relative.parts) or
                path.suffix.lower() in {".zip", ".pyc", ".pyo", ".log"} or
                path.name == ".env" or path.name.startswith(".env.") or
                relative.as_posix() == "PACKAGE_MANIFEST.json"):
            continue
        yield relative.as_posix(), path


def write(root=ROOT):
    verify(root)
    manifest = {"package": "project", "dataset_version": "sakha-power-lst-20261110-et0-v1",
                "repository_version": "p0-kb-20261113-v1", "hash_algorithm": "SHA256",
                "original_delivery_manifest": "provenance/legacy_delivery/PACKAGE_MANIFEST.json", "files": {}}
    for name, path in candidates(root):
        data = path.read_bytes()
        manifest["files"][name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    (root / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return len(manifest["files"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", required=True)
    parser.parse_args()
    print("Recorded P0 repository manifest:", write(), "files")
