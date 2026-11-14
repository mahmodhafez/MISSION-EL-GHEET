"""Build the independent recipient ZIPs from the full, verified project tree, offline."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
NAMES = {"project":"MISSION_EL_GHEET_DATA_ENGINEERING.zip", "ml":"ML_HANDOFF.zip",
         "backend":"BACKEND_HANDOFF.zip"}
BASE = ["requirements.txt","verify_package.py","check_handoff.py","SHARED_DATA_DICTIONARY.md",
        "climate_data/__init__.py","climate_data/climatology.py","data/release.json",
        "data/source_manifest.json","data/quality_flags.csv","data/fit_targets.csv",
        "provenance/input_archives.json","provenance/source_manifest.json",
        "sources/power_provenance.json","sources/power_provenance_2026_Jan_Oct.json"]
ML = ["climate_data/evaluation.py","climate_data/ml_example.py","data/diagnostic_validation_targets.csv",
      "data/forecast_windows.csv","tests/test_ml.py","tests/fixtures/diagnostic_baseline.json",
      "provenance/CHRONOS_HISTORY.md","provenance/experiment/evaluation_protocol.json"]
BACKEND = ["climate_data/backend.py","climate_data/replay.py","climate_data/backend_example.py",
           "climate_data/et0.py","tests/test_et0.py","tests/test_backend.py","data/sakha_daily.csv",
           "tests/test_kb.py", "examples/backend_p0.py", "knowledge_base/agricultural_kb.json"]

def recipient_files(root: Path, role: str) -> dict[str,Path]:
    folder = "ML_HANDOFF" if role == "ml" else "BACKEND_HANDOFF"
    mapping = {name:root/name for name in BASE + (ML if role=="ml" else BACKEND)}
    names = (["START_HERE.md","reference/calendar_reference.csv","reference/scored_predictions.csv",
              "reference/metrics.json"] if role=="ml" else ["START_HERE.md","CONTRACT.md","AGRICULTURAL_KB_CONTRACT.md","example_response.json"])
    mapping.update({name:root/folder/name for name in names})
    if role == "backend":
        for directory in ("agricultural_kb", "sources/agriculture"):
            mapping.update({p.relative_to(root).as_posix(): p for p in (root/directory).iterdir()
                            if p.is_file() and p.suffix in {".py", ".json", ".csv", ".md"}})
    evidence = f"reports/qa/{role}.json"
    if (root/evidence).is_file():
        mapping[evidence] = root/evidence
    return mapping

def write_archive(files: dict[str,Path], role: str, dest: Path) -> None:
    if role not in NAMES or not files:
        raise ValueError("Unknown or empty package")
    if dest.exists():
        raise FileExistsError(dest)
    manifest = {"package":role,"dataset_version":"sakha-power-lst-20261110-et0-v1",
                "hash_algorithm":"SHA256","files":{}}
    with ZipFile(dest,"x",compression=ZIP_DEFLATED,compresslevel=9) as out:
        def write(name: str, content: bytes) -> None:
            item = ZipInfo(name,(2026,11,10,0,0,0))  # deterministic container metadata, not a capture time
            item.compress_type = ZIP_DEFLATED
            item.create_system = 3
            item.external_attr = 0o100644 << 16
            out.writestr(item,content,compresslevel=9)
        for name,path in sorted(files.items()):
            if name == "PACKAGE_MANIFEST.json" or name.startswith("/") or ".." in PurePosixPath(name).parts:
                raise ValueError(f"Invalid package member: {name}")
            content = path.read_bytes()
            manifest["files"][name]={"bytes":len(content),"sha256":hashlib.sha256(content).hexdigest()}
            write(name,content)
        write("PACKAGE_MANIFEST.json",(json.dumps(manifest,indent=2)+"\n").encode())

def main() -> None:
    from verify_package import verify
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args=parser.parse_args()
    output=args.output.resolve()
    if output.exists():
        raise FileExistsError("Choose a new output directory")
    if json.loads((ROOT/"PACKAGE_MANIFEST.json").read_bytes())["package"] != "project":
        raise ValueError("Run from the complete project")
    verify(ROOT)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        staged=Path(tmp)/"handoffs"
        staged.mkdir()
        for role in ("ml","backend"):
            write_archive(recipient_files(ROOT,role),role,staged/NAMES[role])
        staged.rename(output)
    print("Created:",output/NAMES["ml"],"and",output/NAMES["backend"])

if __name__=="__main__":
    main()

