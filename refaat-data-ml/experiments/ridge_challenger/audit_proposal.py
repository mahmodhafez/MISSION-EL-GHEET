"""Pre-approval audit: reproduce existing baselines without fitting Ridge/scalers.

Run from project root:
python -B -m experiments.ridge_challenger.audit_proposal --output experiments/ridge_challenger/audit.json
Only the requested output file is written. Existing files are never overwritten.
"""
import argparse
import csv
from datetime import date, timedelta
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

from climate_data.climatology import SeasonalClimatology, TARGETS, float32
from climate_data.evaluation import (
    distribution_scores, load_diagnostic_data, score_predictions, seasonal_predictions,
)
from verify_package import verify

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run():
    config_bytes = (HERE / "config.json").read_bytes()
    config = json.loads(config_bytes)
    verified_files = verify(ROOT)
    data = load_diagnostic_data(ROOT / "data")
    for name, expected in config["input_sha256"].items():
        require(hashlib.sha256((ROOT / "data" / name).read_bytes()).hexdigest() == expected,
                "Proposed input hash mismatch: " + name)
    first = date.fromisoformat(config["training"]["start"]) + timedelta(days=66)
    last = date.fromisoformat(config["training"]["end"]) - timedelta(days=7)
    require(first.isoformat() == config["training"]["first_issue"], "First training issue mismatch")
    require(last.isoformat() == config["training"]["last_issue"], "Last training issue mismatch")
    require((last-first).days + 1 == config["training"]["examples_per_target_per_lead"], "Training count mismatch")
    require(len(data.training) == config["training"]["daily_rows"], "Training rows mismatch")
    require(len(data.validation) == config["validation"]["daily_rows"], "Validation rows mismatch")
    reference = SeasonalClimatology.from_csv(ROOT / "data/fit_targets.csv")
    seasonal = list(seasonal_predictions(reference, data.windows))
    with (ROOT / "ML_HANDOFF/reference/scored_predictions.csv").open(encoding="utf-8", newline="") as stream:
        preserved = list(csv.DictReader(stream))
    seasonal_scored, seasonal_metrics = score_predictions(data, seasonal)
    require(len(preserved) == len(seasonal_scored), "Baseline prediction count differs")
    for actual, expected in zip(seasonal_scored, preserved, strict=True):
        for key, value in actual.items():
            if isinstance(value, (float, int)):
                require(float(expected[key]) == value, "Baseline prediction value differs: " + key)
            else:
                require(expected[key] == value, "Baseline prediction identity differs: " + key)
    recorded = json.loads((ROOT / "ML_HANDOFF/reference/metrics.json").read_bytes())["metrics"]
    require(seasonal_metrics == recorded, "Recomputed climatology metrics differ from preserved metrics")
    persistence = []
    for window, history in data.contexts():
        require(len(history) == 60 and history[-1].day == window.cutoff, "Context/cutoff mismatch")
        require(history[0].day == window.issue-timedelta(days=66), "Context starts at wrong day")
        for target_day in window.targets():
            for target in TARGETS:
                persistence.append({"issue": window.issue.isoformat(), "target_date": target_day.isoformat(),
                                    "cutoff": window.cutoff.isoformat(), "variable": target,
                                    "q50": float32(getattr(history[-1], target))})
    persistence_scored, persistence_metrics = score_predictions(data, persistence)
    key = lambda row: (row["issue"], row["target_date"], row["variable"])
    require({key(r) for r in seasonal_scored} == {key(r) for r in persistence_scored}, "Unpaired baseline dates")
    # This fixture check is diagnostic only; it never supplies predictions or features.
    with (ROOT / "provenance/experiment/archived_scores.csv").open(encoding="utf-8", newline="") as stream:
        archived = [r for r in csv.DictReader(stream) if r["run"] == "smoke20" and r["method"] == "persistence"]
    require(len(archived) == 2, "Missing archived persistence comparator")
    for row in archived:
        require(abs(persistence_metrics[row["target"]]["mae"]-float(row["mae"])) <=
                config["comparison"]["baseline_reproduction_absolute_tolerance"], "Persistence reference differs")
    metrics = []
    per_lead = []
    for name, rows in (("seasonal_climatology", seasonal_scored), ("persistence", persistence_scored)):
        for target in TARGETS:
            selected = [r for r in rows if r["variable"] == target]
            require(len(selected) == 252, "Wrong sample count")
            # Strip climatology intervals for the point-only comparison.
            points = [{"truth": r["truth"], "q50": r["q50"]} for r in selected]
            metrics.append({"model": name, "target": target, **distribution_scores(points), "samples": len(points)})
            for lead in range(1, 8):
                points = [{"truth": r["truth"], "q50": r["q50"]} for r in selected if r["lead_from_issue"] == lead]
                require(len(points) == 36, "Wrong lead sample count")
                per_lead.append({"model": name, "target": target, "lead_from_issue": lead,
                                 **distribution_scores(points), "samples": len(points)})
    require(verify(ROOT) == verified_files, "Original package changed during audit")
    return {
        "status": "PROPOSAL_PENDING_USER_APPROVAL",
        "ridge_fitted": False, "scaler_fitted": False, "ridge_outputs": "NOT YET GENERATED",
        "previous_frozen_ridge_spec_found": False,
        "search_scope": "existing project paths/config filenames and recursive Python/JSON/Markdown text; only historical no-Ridge statements found",
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "unchanged_package_files_verified_before_and_after": verified_files,
        "input_sha256": config["input_sha256"], "python": platform.python_version(),
        "installed_packages": {name: importlib.metadata.version(name) for name in config["execution"]["packages_pinned_to_observed_environment"]},
        "training_issue_bounds_from_calendar": {"first": first.isoformat(), "last": last.isoformat(), "count": (last-first).days+1},
        "training_features_constructed": False,
        "baseline_predictions_match_existing_climatology_reference_exactly": True,
        "baseline_dates_identical": True,
        "baseline_metrics": metrics, "baseline_metrics_by_lead": per_lead,
        "interpretation": "Baseline-only audit; no Ridge result, model selection or independent test evaluation"
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Choose a new audit output file")
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in ("status", "ridge_fitted", "config_sha256", "baseline_metrics")}, indent=2))
