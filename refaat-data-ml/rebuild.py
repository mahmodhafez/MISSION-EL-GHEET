"""Rebuild this fixed offline release. Run from any directory with Python 3.11+."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
DATASET = "sakha-power-lst-20261110-et0-v1"
METHOD = "fao56-dewpoint-asce-floor-v1"
SITE = "sakha_31.10_30.95"
RUNTIME_FILES = ("sakha_daily.csv", "quality_flags.csv", "fit_targets.csv",
                 "diagnostic_validation_targets.csv", "forecast_windows.csv", "source_manifest.json")

def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()

def verify_inputs() -> None:
    receipts = json.loads((ROOT / "provenance/input_archives.json").read_text(encoding="utf-8"))
    for entry in receipts["members"]:
        path = ROOT / entry["local"]
        if path.stat().st_size != entry["bytes"] or digest(path) != entry["sha256"]:
            raise ValueError(f"Input does not match source archive: {path.name}")

def finish_release(data: Path) -> None:
    """Attach archived source metadata and the exact permissible diagnostic issue list."""
    shutil.copyfile(ROOT / "sources/audit_source_manifest.json", data / "source_manifest.json")
    source = ROOT / "sources/original/forecast_windows.csv"
    with source.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        windows = [row for row in reader if row["partition"] == "diagnostic_validation"]
        columns = reader.fieldnames
    if len(windows) != 36 or len({row["issue"] for row in windows}) != 36:
        raise ValueError("Unexpected diagnostic issue list")
    with (data / "forecast_windows.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(windows)
    release = {
        "dataset_version": DATASET, "et0_method_version": METHOD, "site_id": SITE,
        "latitude_deg_n": 31.10, "longitude_deg_e": 30.95, "grid_elevation_m": 4.96,
        "community": "AG", "time_standard": "LST", "api_version": "v2.10.3",
        "start_date": "2001-01-01", "end_date": "2026-10-31",
        "files": {name: {"bytes": (data/name).stat().st_size, "sha256": digest(data/name)}
                  for name in RUNTIME_FILES},
        "source_manifest": "source_manifest.json",
        "partitions": {"fit": ["2001-01-01","2018-12-31",6574],
                       "diagnostic_validation": ["2019-01-01","2021-12-31",1096],
                       "reserve_not_blind": ["2022-01-01","2025-12-31",1461],
                       "2026_quarantine": ["2026-01-01","2026-10-31",304]},
    }
    (data/"release.json").write_text(json.dumps(release, indent=2)+"\n",encoding="utf-8",newline="\n")

def rebuild(destination: Path) -> None:
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f"Choose a new build directory: {destination}")
    verify_inputs()
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Stage on the same filesystem. A failed calculation cannot publish a partial snapshot.
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".sakha-build-") as stage:
        build = Path(stage) / "release"
        subprocess.run([sys.executable, "-B", "-m", "climate_data.pipeline",
                        "--sources", str(ROOT/"sources"), "--output", str(build)], cwd=ROOT,check=True)
        finish_release(build/"data")
        if destination.exists():
            raise FileExistsError(destination)
        build.rename(destination)
    print("Rebuilt release in", destination)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    rebuild(parser.parse_args().output)

