"""Regenerate a frozen Sakha ET0 release with the byte-preserved audited script.

No downloads, model execution, crop demand, or changed calculation methodology.
Inputs must match the declared historical checksums. Output must be a new folder.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def regenerate(args):
    output = args.output_dir.resolve()
    if output.exists():
        raise ValueError("Output directory already exists; choose a new directory")
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "et0_release_manifest.json").read_text(encoding="utf-8"))
    period = manifest["periods"][args.period]
    acquisition = json.loads((root / "power_acquisition.json").read_text(encoding="utf-8"))["releases"][period["acquisition_index"]]
    generator = (root / manifest["generator"]["path"]).read_bytes()
    if digest(generator) != manifest["generator"]["sha256"]:
        raise ValueError("Audited generator checksum mismatch")
    if args.archive is not None:
        with zipfile.ZipFile(args.archive) as archive:
            raw = archive.read(period["archive_member"])
    else:
        raw = args.source.read_bytes()
    if digest(raw) != period["source_sha256"] or period["source_sha256"] != acquisition["sha256"]:
        raise ValueError("Frozen source checksum mismatch; a refresh is a different dataset release")
    # All source checks occur before creating/writing anything. Never extract ZIP paths.
    output.mkdir(parents=True, exist_ok=False)
    (output / "audit_weather.py").write_bytes(generator)
    (output / period["source_filename"]).write_bytes(raw)
    (output / "source_provenance.json").write_text(json.dumps(acquisition, indent=2) + "\n", encoding="utf-8")
    command = [sys.executable, "-I", "-S", str(output / "audit_weather.py"),
               "--source", period["source_filename"], "--suffix", period["suffix"]]
    run = subprocess.run(command, capture_output=True, text=True, check=False)
    if run.returncode:
        raise ValueError("Audited generator failed; partial outputs remain unvalidated: " + run.stderr.strip())
    audit = json.loads((output / period["audit_filename"]).read_text(encoding="utf-8"))
    checks = audit["reference_checks"]
    if len(checks) != 12 or not all(check["passed"] for check in checks) or audit["days"] != period["days"]:
        raise ValueError("Reference checks or date count failed")
    csv_sha256 = digest((output / period["csv_filename"]).read_bytes())
    if csv_sha256 != period["csv_sha256"]:
        raise ValueError("CSV checksum differs from frozen output; inspect runtime/numerical differences")
    result = {
        "status": "passed", "release_id": manifest["release_id"], "period": args.period,
        "method": manifest["method"], "python": sys.version.split()[0],
        "source_sha256": digest(raw), "generator_sha256": digest(generator),
        "csv_sha256": csv_sha256, "csv_sha256_matches_frozen": True,
        "days": audit["days"], "reference_checks_passed": len(checks),
        "output_dir": str(output), "limitation": "Numerical reproduction, not field/ETc/planner validation",
    }
    (output / "reproduction_result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument("--archive", type=Path, help="Local-only frozen validation ZIP")
    sources.add_argument("--source", type=Path, help="Original raw POWER response matching the frozen checksum")
    parser.add_argument("--period", choices=("historical", "2026"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory; existing paths are rejected")
    args = parser.parse_args()
    try:
        result = regenerate(args)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(json.dumps({"status": "failed", "error": str(error)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
