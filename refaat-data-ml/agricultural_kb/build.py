"""Deterministically import the recovered 2026-11-11 research, without approving it."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

from .loader import AgriculturalKB
from .validation import KBError, strict_json

ROOT = Path(__file__).resolve().parents[1]
LEDGER = "MISSION_EL_GHEET_Crop_Rule_Ledger.csv"
REGISTER = "MISSION_EL_GHEET_Evidence_Register.csv"
CROPS = {"Wheat": ("wheat", "Wheat", "grain"), "Berseem": ("berseem", "Berseem", "forage_or_seed_requires_review"),
         "Maize": ("grain_maize", "Grain maize", "grain"), "Grain sorghum": ("grain_sorghum", "Grain sorghum", "grain")}


def verify_sources(directory):
    manifest = strict_json((directory / "MANIFEST.json").read_bytes())
    for name, expected in manifest["files"].items():
        if Path(name).name != name:
            raise KBError("INVALID_SOURCE", name, "Expected flat research source paths")
        payload = (directory / name).read_bytes()
        if len(payload) != expected["bytes"] or hashlib.sha256(payload).hexdigest() != expected["sha256"]:
            raise KBError("SOURCE_INTEGRITY", name, "Research source changed")
    if not {LEDGER, REGISTER}.issubset(manifest["files"]):
        raise KBError("INVALID_SOURCE", "MANIFEST.json", "Missing ledger/register hashes")


def _rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise KBError("INVALID_SOURCE", path.name, "Missing or duplicate CSV headers")
        rows = list(reader)
        if any(None in r or any(v is None for v in r.values()) for r in rows):
            raise KBError("INVALID_SOURCE", path.name, "Malformed CSV row")
        return rows


def build_document(source_dir=None):
    directory = ROOT / "sources/agriculture" if source_dir is None else Path(source_dir)
    verify_sources(directory)
    ledger, register = _rows(directory / LEDGER), _rows(directory / REGISTER)
    if [r["Rule ID"] for r in ledger] != [f"C{i:02d}" for i in range(1, 28)]:
        raise KBError("INVALID_SOURCE", LEDGER, "This importer expects the frozen C01-C27 ledger")
    evidence_rows = {}
    for item in register:
        match = re.fullmatch(r"Crop rules . (C[0-9]{2})", item["Research area"])
        if match:
            if match[1] in evidence_rows:
                raise KBError("INVALID_SOURCE", REGISTER, "Ambiguous crop evidence link")
            evidence_rows[match[1]] = item
    if set(evidence_rows) != {r["Rule ID"] for r in ledger}:
        raise KBError("INVALID_SOURCE", REGISTER, "Missing crop evidence mapping")
    sources, evidence, rules = {}, [], []
    for row in ledger:
        rid = row["Rule ID"]
        erow = evidence_rows[rid]
        for left, right in (("Source URL", "Source URL"), ("Scientific source title", "Source title"),
                            ("Source date/version", "Source date/version"),
                            ("Current verification status", "Evidence status")):
            if row[left] != erow[right]:
                raise KBError("INVALID_SOURCE", rid, "Ledger/evidence disagreement: " + left)
        if row["Named local reviewer / sign-off"] != "Pending":
            raise KBError("INVALID_SOURCE", rid, "New sign-off requires a reviewed release, not automatic import")
        key = row["Source URL"] + "\n" + row["Source date/version"]
        sid = "SRC_" + hashlib.sha256(key.encode()).hexdigest()[:16]
        sources[sid] = {"source_id": sid, "title": row["Scientific source title"],
                        "url": row["Source URL"], "version": row["Source date/version"]}
        evidence.append({"evidence_id": erow["Evidence ID"], "source_ids": [sid],
                         "scientific_status": erow["Evidence status"], "claim": erow["Claim or proposed rule"],
                         "locality": erow["Geographic applicability"], "crop_context": erow["Crop/cultivar applicability"],
                         "units": erow["Units"], "locator": erow["Relevant page/section/table"],
                         "limitations": erow["Limitations"], "review_required": erow["Expert review required"],
                         "notes": erow["Notes"], "source_opened": erow["Source opened"], "review_date": erow["Review date"]})
        crop_ids = [c[0] for c in CROPS.values()] if row["Crop name"] == "All four" else [CROPS[row["Crop name"]][0]]
        rules.append({
            "rule_id": rid, "crop_ids": crop_ids,
            "rule_type": re.sub(r"[^a-z0-9]+", "_", row["Rule type"].lower()).strip("_"),
            "rule_label": row["Rule type"],
            "parameters": {"source_text": row["Proposed value or range"], "units": row["Units"]},
            "research_context": {"locality": row["Locality"], "cultivar": row["Crop type/cultivar"],
                                 "season": row["Season or study context"]},
            "source_ids": [sid], "evidence_ids": [erow["Evidence ID"]],
            "scientific_status": row["Current verification status"],
            "local_applicability": {"status": "NOT_APPLICABLE" if rid == "C22" else "PENDING",
                                    "locality_ids": ["sakha"], "reviewer": None, "reference": None},
            "approval": {"status": "PENDING", "reviewer": None, "approved_on": None,
                         "reference": None, "scope_sha256": None},
            "enforcement": {"status": "DISABLED", "constraint": None}, "conditions": {},
            "unresolved_requirements": [row["Assumptions and limitations"],
                                        "Document local applicability, cultivar, purpose and field conditions.",
                                        "Obtain named agronomic sign-off and review the structured planner constraint."],
            "source_activation_note": row["Planner activation or use"],
            "source_review_requirement": row["Local review required"],
            "source_sign_off": row["Named local reviewer / sign-off"],
        })
    document = {"schema_version": "agricultural-kb/1", "kb_version": "crop-research-20261111-v1",
                "provenance": {"ledger": "sources/agriculture/" + LEDGER,
                               "evidence_register": "sources/agriculture/" + REGISTER,
                               "source_manifest": "sources/agriculture/MANIFEST.json"},
                "localities": [{"locality_id": "sakha", "name": "Sakha pilot review scope",
                                "climate_site_id": "sakha_31.10_30.95"}],
                "crops": [{"crop_id": cid, "display_name": name, "purpose": purpose,
                           "rule_ids": [r["rule_id"] for r in rules if cid in r["crop_ids"]]}
                          for cid, name, purpose in CROPS.values()],
                "sources": sorted(sources.values(), key=lambda s: s["source_id"]), "evidence": evidence, "rules": rules}
    AgriculturalKB(document)
    return document


def serialize(document):
    return (json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=ROOT / "sources/agriculture")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    content = serialize(build_document(args.sources))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(content)
    print("Created research KB; all local approvals remain pending:", args.output)
