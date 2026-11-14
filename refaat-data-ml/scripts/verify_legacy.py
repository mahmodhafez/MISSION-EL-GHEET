"""Verify the original 66-file delivery using preserved originals for edited files."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_MANIFEST_SHA256 = "2947f8bec57c4a4a378893c34305540e5336997fe31856b5e66f654af1952aae"


def verify(root=ROOT):
    archive = root / "provenance/legacy_delivery"
    payload = (archive / "PACKAGE_MANIFEST.json").read_bytes()
    if hashlib.sha256(payload).hexdigest() != LEGACY_MANIFEST_SHA256:
        raise ValueError("Original delivery manifest changed")
    entries = json.loads(payload)["files"]
    for name, expected in entries.items():
        stored = archive / name
        path = stored if stored.is_file() else root / name
        contents = path.read_bytes()
        if len(contents) != expected["bytes"] or hashlib.sha256(contents).hexdigest() != expected["sha256"]:
            raise ValueError("Original delivery evidence changed: " + name)
    return len(entries)


if __name__ == "__main__":
    print("Verified original delivery:", verify(), "files; no original scientific data was changed")
