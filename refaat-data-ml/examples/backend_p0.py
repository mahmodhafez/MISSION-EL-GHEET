"""Yahya's local consumer example: python -m examples.backend_p0 (prints JSON)."""
import argparse
import json
from pathlib import Path

from agricultural_kb import load_kb
from climate_data.backend import ClimateStore

ROOT = Path(__file__).resolve().parents[1]


def example(data_dir=None, kb_file=None):
    kb = load_kb(kb_file)
    climate = ClimateStore(ROOT / "data" if data_dir is None else data_dir)
    wheat = kb.get_crop("wheat")
    rules = kb.get_rules(crop_id="wheat", locality="sakha")
    evidence = kb.get_evidence(rules[0]["evidence_ids"][0])
    return {"contract_version": "backend-p0-example/1", "kb_status": kb.get_status(locality="sakha"),
            "crop": wheat, "approved_rules": kb.get_approved_rules(locality="sakha"),
            "planner_constraints": kb.get_enforceable_rules(locality="sakha"),
            "pending_rules": kb.get_pending_rules(locality="sakha"),
            "evidence": evidence, "source": kb.get_sources(evidence["source_ids"][0]),
            "weather": climate.get_daily_weather("2020-02-28", "2020-03-01"),
            "et0": climate.calculate_et0_summary("2020-02-28", "2020-03-01"),
            "climatology": climate.get_climatology("2028-02-29"),
            "climate_release": climate.get_data_provenance()}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--data", type=Path)
    cli.add_argument("--kb", type=Path)
    args = cli.parse_args()
    print(json.dumps(example(args.data, args.kb), ensure_ascii=True, indent=2, allow_nan=False))
