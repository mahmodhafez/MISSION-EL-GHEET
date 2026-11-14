"""Verify the immutable files listed at delivery time. New result files are permitted."""
import hashlib
import json
from pathlib import Path

def verify(directory: Path) -> int:
    manifest = json.loads((directory/"PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    for name, expected in manifest["files"].items():
        path = directory/name
        with path.open("rb") as handle:
            actual = hashlib.file_digest(handle,"sha256").hexdigest()
        if actual != expected["sha256"] or path.stat().st_size != expected["bytes"]:
            raise ValueError(f"Delivery file changed: {name}")
    return len(manifest["files"])

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print("Verified", verify(root), "files against PACKAGE_MANIFEST.json")

