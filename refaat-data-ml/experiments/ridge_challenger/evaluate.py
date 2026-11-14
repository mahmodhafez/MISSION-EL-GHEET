"""Paired diagnostic evaluation of one frozen Ridge model and two fixed baselines."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path

from climate_data.climatology import SeasonalClimatology, TARGETS, float32
from climate_data.evaluation import distribution_scores, load_diagnostic_data, score_predictions, seasonal_predictions
from verify_package import verify
from .common import APPROVED_SHA256, HERE, ROOT, code_hashes, environment, load_config, output_path, require, sha256, write_csv, write_json
from .train import load_model, predict_contexts

MODELS = ("seasonal_climatology", "persistence", "ridge")
OUTPUT_NAMES = ("predictions.csv", "metrics.csv", "per_lead_metrics.csv", "comparisons.csv",
                "per_lead_comparisons.csv", "metrics.json", "comparison_report.md")


def baselines(dataset):
    reference = SeasonalClimatology.from_csv(ROOT / "data/fit_targets.csv")
    seasonal = [{key: row[key] for key in
                 ("issue", "cutoff", "target_date", "variable", "lead_from_issue", "step_from_cutoff", "q50")}
                for row in seasonal_predictions(reference, dataset.windows)]
    persistence = []
    for window, history in dataset.contexts():
        for day in window.targets():
            for target in TARGETS:
                persistence.append({"issue": window.issue.isoformat(), "cutoff": window.cutoff.isoformat(),
                                    "target_date": day.isoformat(), "variable": target,
                                    "q50": float32(getattr(history[-1], target))})
    return {"seasonal_climatology": seasonal, "persistence": persistence}


def summarize(model, scored):
    overall, by_lead = [], []
    for target in TARGETS:
        rows = [r for r in scored if r["variable"] == target]
        require(len(rows) == 252, "Expected exactly 252 scored dates per target")
        unit = "degC" if target == "tmax_c" else "mm/day"
        overall.append({"model": model, "target": target, "unit": unit,
                        **distribution_scores(rows), "samples": len(rows)})
        for lead in range(1, 8):
            selected = [r for r in rows if r["lead_from_issue"] == lead]
            require(len(selected) == 36, "Expected exactly 36 scored samples at each lead")
            by_lead.append({"model": model, "target": target, "unit": unit, "lead_from_issue": lead,
                            "step_from_cutoff": lead+7, **distribution_scores(selected), "samples": len(selected)})
    return overall, by_lead


def compare_metrics(metrics, per_lead=False):
    result = []
    for target in TARGETS:
        for lead in (range(1, 8) if per_lead else [None]):
            rows = {r["model"]: r for r in metrics if r["target"] == target
                    and (not per_lead or r["lead_from_issue"] == lead)}
            require(set(rows) == set(MODELS), "Unpaired model metric rows")
            for baseline in MODELS[:2]:
                for metric in ("mae", "rmse"):
                    original, challenger = rows[baseline][metric], rows["ridge"][metric]
                    difference = original-challenger
                    result.append({"target": target, "unit": rows[baseline]["unit"],
                                   **({"lead_from_issue": lead} if per_lead else {}),
                                   "baseline": baseline, "metric": metric, "baseline_value": original,
                                   "ridge_value": challenger, "baseline_minus_ridge": difference,
                                   "improvement_percent": 100*difference/original if original != 0 else None,
                                   "ridge_result": "WIN" if difference > 0 else "LOSS" if difference < 0 else "TIE"})
    return result


def verify_baseline_outputs(scored, metrics, config):
    with (ROOT / "ML_HANDOFF/reference/scored_predictions.csv").open(encoding="utf-8", newline="") as stream:
        reference = list(csv.DictReader(stream))
    require(len(reference) == len(scored["seasonal_climatology"]), "Climatology reference length changed")
    for actual, expected in zip(scored["seasonal_climatology"], reference, strict=True):
        for key, value in actual.items():
            require(value == (float(expected[key]) if isinstance(value, (int, float)) else expected[key]),
                    "Climatology prediction differs from preserved reference")
    expected_metrics = json.loads((ROOT / "ML_HANDOFF/reference/metrics.json").read_bytes())["metrics"]
    for row in metrics:
        if row["model"] == "seasonal_climatology":
            for metric in ("mae", "rmse", "bias"):
                require(row[metric] == expected_metrics[row["target"]][metric], "Climatology metrics differ")
    with (ROOT / "provenance/experiment/archived_scores.csv").open(encoding="utf-8", newline="") as stream:
        expected_persistence = {r["target"]: float(r["mae"]) for r in csv.DictReader(stream)
                                if r["run"] == "smoke20" and r["method"] == "persistence"}
    require(set(expected_persistence) == set(TARGETS), "Missing archived persistence benchmark")
    for row in metrics:
        if row["model"] == "persistence":
            require(abs(row["mae"]-expected_persistence[row["target"]]) <=
                    config["comparison"]["baseline_reproduction_absolute_tolerance"], "Persistence MAE differs")


def report_text(result):
    metrics, leads, deltas = result["overall"], result["by_lead"], result["comparisons"]
    lines = ["# Ridge challenger: measured diagnostic validation", "",
             "One approved configuration, 14 direct models, CPU. Training 2001-2018; diagnostic validation 2019-2021.",
             "Config SHA256: `" + APPROVED_SHA256 + "`.", "",
             "## Overall measured comparison", "",
             "| Model | Target | MAE | RMSE | Bias (prediction - actual) | Samples |",
             "|---|---|---:|---:|---:|---:|"]
    for target in TARGETS:
        for model in MODELS:
            row = next(r for r in metrics if (r["target"], r["model"]) == (target, model))
            lines.append(f"| {model} | {target} ({row['unit']}) | {row['mae']:.9f} | {row['rmse']:.9f} | {row['bias']:+.9f} | {row['samples']} |")
    lines += ["", "## Absolute and relative differences", "",
              "Positive difference = baseline minus Ridge, so positive values favor Ridge. Bias is signed above; smaller absolute bias is better.", "",
              "| Target | Baseline | Metric | Baseline - Ridge | Improvement % | Ridge result |",
              "|---|---|---|---:|---:|---|"]
    for row in deltas:
        lines.append(f"| {row['target']} | {row['baseline']} | {row['metric']} | {row['baseline_minus_ridge']:+.9f} | {row['improvement_percent']:+.4f}% | {row['ridge_result']} |")
    lines += ["", "## Interpretation by target", ""]
    for target in TARGETS:
        for baseline in MODELS[:2]:
            rows = [r for r in deltas if r["target"] == target and r["baseline"] == baseline]
            gain = next(r for r in rows if r["metric"] == "mae")
            square = next(r for r in rows if r["metric"] == "rmse")
            per = [r for r in result["comparisons_by_lead"] if r["target"] == target and r["baseline"] == baseline]
            counts = {metric: sum(r["ridge_result"] == "WIN" for r in per if r["metric"] == metric) for metric in ("mae", "rmse")}
            ridge_bias = next(r["bias"] for r in metrics if r["target"] == target and r["model"] == "ridge")
            base_bias = next(r["bias"] for r in metrics if r["target"] == target and r["model"] == baseline)
            lines.append(f"- **{target} vs {baseline}:** MAE {gain['ridge_result']}, {gain['improvement_percent']:+.4f}% improvement; RMSE {square['ridge_result']}, {square['improvement_percent']:+.4f}%. Lower MAE at {counts['mae']}/7 leads; lower RMSE at {counts['rmse']}/7 leads. Absolute bias: Ridge {abs(ridge_bias):.6f}, baseline {abs(base_bias):.6f}.")
    lines += ["", "## Per-lead comparison", "",
              "Each row uses 36 identical issue/target pairs. Full MAE/RMSE/Bias/count for every model and lead are in per_lead_metrics.csv; absolute/percentage differences are in per_lead_comparisons.csv."]
    for target in TARGETS:
        lines += ["", "### " + target, "",
                  "| Lead | Clim MAE | Persist MAE | Ridge MAE | Clim RMSE | Persist RMSE | Ridge RMSE | Ridge Bias |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for lead in range(1, 8):
            rows = {r["model"]: r for r in leads if r["target"] == target and r["lead_from_issue"] == lead}
            numbers = [rows[m][metric] for metric in ("mae", "rmse") for m in MODELS]
            lines.append(f"| D+{lead} | " + " | ".join(f"{v:.6f}" for v in numbers) + f" | {rows['ridge']['bias']:+.6f} |")
    lines += ["", "## Protocol and integrity", "",
              "- Exactly the approved two target-date annual harmonics and last/7/30/60-day means for Tmax and ET0. Every history ends at D-7; target steps are 8-14 after the cutoff.",
              "- Each of 14 StandardScaler + Ridge(alpha=1, solver=svd) pipelines was fitted once on 6,501 training examples. No validation fitting, hyperparameter search or post-evaluation adjustment.",
              "- History/labels use the original float32 diagnostic convention, with float64 feature arithmetic and fitting. Targets remain in physical units. No clipping or invented prediction intervals.",
              "- Identical 504 target/issue/variable keys for each model, 252 observations per target. Baselines were recomputed from source observations; original climatology predictions and metrics matched exactly.",
              f"- JSON model reload and repeat-inference maximum difference: {result['repeat_prediction_max_abs_error']:.3g}. Original package files verified before and after evaluation: {result['original_package_files_verified']}.",
              f"- Negative Ridge ET0 predictions retained without clipping: {result['negative_ridge_et0_predictions']}.",
              "- Reproduction commands, configuration/approval details and automated test results are documented in README.md and test_results.json.",
              "", "## Scientific limits", "",
              "These are diagnostic validation results on previously inspected years, not an independent blind test. No claim of statistical significance or deployment readiness follows from overall or per-lead differences. Leads share forecast issues and overlapping histories; their scores are not seven independent replications.",
              "The frozen NASA POWER snapshot is retrospective and can contain revisions. The assumed D-7 cutoff may not reproduce real-time publication availability; as-issued arrival/revision logs are absent. ET0 is derived grass-reference evaporative demand from one gridded point, not measured field water use.",
              "A linear model with one annual harmonic pair and fixed history summaries has limited nonlinear/extreme-event capacity. The 60-day contexts and training labels overlap. There is no station truth validation, geographic generalization test, interval calibration or operational monitoring.",
              "No 2022-2026 values were used for model fitting or selection. No retraining on 2019-2021 was performed. Preserve this result even if it loses. Any future prospective test or revised model needs a separately authorized protocol; neither is executed here.", ""]
    return "\n".join(lines)


def evaluate(model_path=HERE / "model_parameters.json", output_dir=HERE):
    config = load_config()
    environment(config)
    output_dir = Path(output_dir).resolve()
    require(output_dir.is_relative_to(HERE), "Results must stay inside experiment directory")
    for name in OUTPUT_NAMES:
        output_path(output_dir / name)
    original_count = verify(ROOT)
    model_path = Path(model_path)
    model_hash_before = sha256(model_path)
    bundle = load_model(model_path)
    dataset = load_diagnostic_data(ROOT / "data")
    forecasts = baselines(dataset)
    forecasts["ridge"] = predict_contexts(bundle, dataset.contexts())
    repeated = predict_contexts(load_model(model_path), dataset.contexts())
    repeated_diff = max(abs(a["q50"]-b["q50"]) for a, b in zip(forecasts["ridge"], repeated, strict=True))
    require(repeated_diff <= 1e-10, "Repeated predictions differ")
    metrics, leads, prediction_rows, scored_by_model = [], [], [], {}
    paired_keys = None
    for model in MODELS:
        scored, _ = score_predictions(dataset, forecasts[model])
        keys = {(r["issue"], r["target_date"], r["variable"]) for r in scored}
        require(len(keys) == 504 and (paired_keys is None or keys == paired_keys), "Model prediction dates differ")
        paired_keys = keys
        scored_by_model[model] = scored
        overall, per_lead = summarize(model, scored)
        metrics.extend(overall)
        leads.extend(per_lead)
        for row in scored:
            prediction_rows.append({"model": model, **{k: v for k, v in row.items() if k != "q50"},
                                    "prediction": row["q50"]})
    verify_baseline_outputs(scored_by_model, metrics, config)
    comparisons = compare_metrics(metrics)
    comparisons_by_lead = compare_metrics(leads, per_lead=True)
    require(verify(ROOT) == original_count and sha256(model_path) == model_hash_before, "Input/model changed during evaluation")
    load_config()
    result = {"specification_id": config["specification_id"], "config_sha256": APPROVED_SHA256,
              "model_sha256": model_hash_before, "dataset_version": config["dataset_version"],
              "split": "diagnostic_validation_2019_2021_NOT_BLIND", "origin_count": 36,
              "input_sha256": config["input_sha256"], "overall": metrics, "by_lead": leads,
              "comparisons": comparisons, "comparisons_by_lead": comparisons_by_lead,
              "paired_keys_per_model": len(paired_keys), "prediction_rows_total": len(prediction_rows),
              "repeat_prediction_max_abs_error": repeated_diff, "baseline_reference_checks_passed": True,
              "original_package_files_verified": original_count,
              "negative_ridge_et0_predictions": sum(r["q50"] < 0 for r in scored_by_model["ridge"] if r["variable"] == "et0_mm_day"),
              "evaluation_implementation_sha256": code_hashes(), "evaluated_utc": datetime.now(timezone.utc).isoformat()}
    write_csv(output_dir / "predictions.csv", prediction_rows)
    write_csv(output_dir / "metrics.csv", metrics)
    write_csv(output_dir / "per_lead_metrics.csv", leads)
    write_csv(output_dir / "comparisons.csv", comparisons)
    write_csv(output_dir / "per_lead_comparisons.csv", comparisons_by_lead)
    write_json(output_dir / "metrics.json", result)
    with (output_dir / "comparison_report.md").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(report_text(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=HERE / "model_parameters.json")
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args()
    result = evaluate(args.model, args.output_dir)
    print(json.dumps({"overall": result["overall"], "comparisons": result["comparisons"]}, indent=2))
