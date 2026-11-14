"""Extract and verify independent recipient ZIPs without importing from this root."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from zipfile import ZipFile


def verify(handoffs):
    results = {}
    for role in ("backend", "ml"):
        archive = handoffs / (role.upper() + "_HANDOFF.zip")
        with tempfile.TemporaryDirectory(dir=handoffs.parent) as tmp:
            extracted = Path(tmp)
            with ZipFile(archive) as handle:
                for name in handle.namelist():
                    if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts or "\\" in name or ":" in name:
                        raise ValueError("Unsafe archive member")
                handle.extractall(extracted)
            result = subprocess.run([sys.executable, "-B", "check_handoff.py", "--output", "outputs/acceptance.json"],
                                    cwd=extracted, env={**os.environ, "PYTHONPATH": "", "PYTHONIOENCODING": "utf-8"},
                                    text=True, encoding="utf-8", capture_output=True, timeout=300)
            if result.returncode:
                raise RuntimeError(role + " extraction failed:\n" + result.stdout + result.stderr)
            results[role] = {"archive": archive.name, "bytes": archive.stat().st_size,
                             "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                             "acceptance": json.loads((extracted / "outputs/acceptance.json").read_bytes())}
            print(role, "independent extraction passed", flush=True)
    return {"status": "VERIFIED AND TESTED", "actual_team_backend_tested": False, "recipients": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoffs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Use a new evidence file")
    result = verify(args.handoffs.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
