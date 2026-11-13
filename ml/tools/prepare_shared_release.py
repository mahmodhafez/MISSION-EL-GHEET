"""Assemble checked, byte-preserved handoff data; no training or ET0 regeneration.

Run with Python 3.11+. This never executes code from an archive. Existing output
directories and changed evidence are rejected, and publication is atomic.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tempfile
import zipfile

REFAAT_SHA = "6990e8e2ef02db325812773f607e6e96cf027b820ee851f887d2b5e1a14cff4b"
SCIENCE_SHA = "d284b3162a2dd5bbde8bcb37ae3090adcf080a5d044a4e25b2c96836b4cee95f"
WEATHER = {
    "weather_et0.csv": "17141df82f6300c051257c21fb9ac3d9f5f1627fd32cbc8c07bc9296c477bde8",
    "weather_et0_2026_Jan_Oct.csv": "c4d5929fd0d4d55c416ee45d5ebd21502142994afbc76b00c6f20e1b349ee36e",
}


def digest(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def build(refaat: Path, science: Path, output: Path) -> dict:
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Choose a new output directory: {output}")
    for path, expected in ((refaat, REFAAT_SHA), (science, SCIENCE_SHA)):
        if digest(path) != expected:
            raise ValueError(f"Archive checksum mismatch: {Path(path).name}")
    files = {}
    with zipfile.ZipFile(refaat) as rz, zipfile.ZipFile(science) as sz:
        package_bytes = rz.read("PACKAGE_MANIFEST.json")
        package = json.loads(package_bytes)
        for name, meta in package["files"].items():
            relative = PurePosixPath(name)
            if relative.is_absolute() or ".." in relative.parts or "\\" in name or ":" in name:
                raise ValueError("Unsafe package member")
            content = rz.read(name)
            if len(content) != meta["bytes"] or hashlib.sha256(content).hexdigest() != meta["sha256"]:
                raise ValueError(f"Member checksum mismatch: {name}")
            files["refaat/" + name] = content
        files["refaat/PACKAGE_MANIFEST.json"] = package_bytes
        for name, expected in WEATHER.items():
            content = sz.read("work/validation_2026-11-10/" + name)
            if hashlib.sha256(content).hexdigest() != expected:
                raise ValueError(f"Weather checksum mismatch: {name}")
            files["weather/" + name] = content
    historical = {row["date"]: row for row in csv.DictReader(io.StringIO(files["weather/weather_et0.csv"].decode()))}
    count = 0
    for name in ("fit_targets.csv", "diagnostic_validation_targets.csv"):
        for row in csv.DictReader(io.StringIO(files["refaat/data/" + name].decode())):
            for variable in ("tmax_c", "et0_mm_day"):
                if float(row[variable]) != float(historical[row["date"]][variable]):
                    raise ValueError(f"Target mismatch: {row['date']} {variable}")
            count += 1
    if count != 7670:
        raise ValueError("Unexpected target row count")
    manifest = {
        "release_id": "meg-shared-20261113-v1",
        "dataset_version": package["dataset_version"],
        "site_id": "sakha_31.10_30.95", "time_standard": "LST",
        "et0_method_id": "fao56-dewpoint-asce-floor-v1",
        "archives": {"ML_HANDOFF.zip": REFAAT_SHA, "VALIDATION_ARTIFACTS.zip": SCIENCE_SHA},
        "alignment": {"dates": count, "targets_per_date": 2, "numeric_mismatches": 0},
        "missing_from_refaat_subset": ["data/sakha_daily.csv", "rebuild.py", "backend climate evaluator", "model weights"],
        "limitations": ["retrospective revised POWER products", "native cell IDs unknown", "2026 consumed; not fresh test", "no crop applicability validation"],
        "files": {name: {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
                  for name, content in sorted(files.items())},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as scratch:
        staged = Path(scratch) / "release"
        staged.mkdir()
        for name, content in files.items():
            path = staged / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (staged / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        if output.exists():
            raise FileExistsError(output)
        staged.rename(output)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refaat", required=True, type=Path)
    parser.add_argument("--science", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = build(args.refaat, args.science, args.output)
    print(json.dumps({"release_id": result["release_id"], "files": len(result["files"]), "alignment": result["alignment"]}))
