"""Fit only the approved 14 direct Ridge pipelines on 2001-2018, once per run."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_info, threadpool_limits

from .common import APPROVED_SHA256, HERE, code_hashes, environment, load_config, output_path, require, sha256, write_json
from .features import FEATURE_NAMES, feature_vector, training_matrices, training_rows


def new_pipeline(config):
    return Pipeline([("scale", StandardScaler(**config["preprocessing"]["parameters"])),
                     ("ridge", Ridge(**config["ridge"]["parameters"]))])


def export_pipeline(pipeline, target, lead):
    scaler, estimator = pipeline.named_steps["scale"], pipeline.named_steps["ridge"]
    return {"target": target, "lead_from_issue": lead, "step_from_cutoff": lead+7,
            "training_rows": int(scaler.n_samples_seen_), "feature_count": int(scaler.n_features_in_),
            "scaler": {"mean": scaler.mean_.tolist(), "var": scaler.var_.tolist(), "scale": scaler.scale_.tolist()},
            "ridge": {"coef": estimator.coef_.tolist(), "intercept": float(estimator.intercept_),
                      "solver": estimator.solver_}}


def restore_pipelines(bundle):
    config = load_config()
    require(bundle["config_sha256"] == APPROVED_SHA256 and bundle["configuration"] == config,
            "Model was not produced by the approved configuration")
    require(bundle["feature_names"] == list(FEATURE_NAMES), "Model feature order mismatch")
    expected = {(v, h) for v in config["targets"] for h in range(1, 8)}
    restored = {}
    for record in bundle["models"]:
        key = record["target"], record["lead_from_issue"]
        require(key in expected and key not in restored, "Unexpected or duplicate model")
        require(record["training_rows"] == 6501 and record["feature_count"] == 10
                and record["step_from_cutoff"] == key[1]+7 and record["ridge"]["solver"] == "svd",
                "Wrong model training/forecast metadata")
        pipeline = new_pipeline(config)
        scaler, model = pipeline.named_steps["scale"], pipeline.named_steps["ridge"]
        for field in ("mean", "var", "scale"):
            array = np.asarray(record["scaler"][field], dtype=np.float64)
            require(array.shape == (10,) and np.isfinite(array).all(), "Invalid scaler parameters")
            setattr(scaler, field + "_", array)
        require((scaler.scale_ > 0).all() and (scaler.var_ >= 0).all(), "Invalid scaler variance/scale")
        scaler.n_features_in_ = model.n_features_in_ = 10
        scaler.n_samples_seen_ = np.int64(6501)
        model.coef_ = np.asarray(record["ridge"]["coef"], dtype=np.float64)
        model.intercept_ = float(record["ridge"]["intercept"])
        require(model.coef_.shape == (10,) and np.isfinite(model.coef_).all() and np.isfinite(model.intercept_),
                "Invalid Ridge coefficients")
        model.solver_, model.n_iter_ = "svd", None
        restored[key] = pipeline
    require(set(restored) == expected, "Missing direct model")
    return restored


def load_model(path):
    path = Path(path)
    expected = path.with_suffix(path.suffix + ".sha256").read_text(encoding="ascii").split()[0]
    require(sha256(path) == expected, "Saved model integrity check failed")
    bundle = json.loads(path.read_bytes())
    restore_pipelines(bundle)
    return bundle


def predict_contexts(bundle, contexts):
    """Only sliced histories are supplied. No validation truth is accepted here."""
    config = load_config()
    pipelines = restore_pipelines(bundle)
    records = []
    with threadpool_limits(limits=config["execution"]["blas_thread_limit"]):
        for window, history in contexts:
            require(len(history) == 60, "Require exactly 60 days at inference")
            require(history[-1].day == window.cutoff, "Forecast cutoff/history mismatch")
            for h in range(1, 8):
                vector = feature_vector(window.issue, history, h).reshape(1, -1)
                target_date = list(window.targets())[h-1]
                require((target_date-window.issue).days == h and (target_date-window.cutoff).days == h+7,
                        "Invalid forecast target alignment")
                for v in config["targets"]:
                    value = float(pipelines[v, h].predict(vector)[0])
                    require(np.isfinite(value), "Nonfinite prediction")
                    records.append({"issue": window.issue.isoformat(), "cutoff": window.cutoff.isoformat(),
                                    "target_date": target_date.isoformat(), "variable": v,
                                    "lead_from_issue": h, "step_from_cutoff": h+7, "q50": value})
    return records


def train(destination, data_dir=None):
    config = load_config()
    destination = output_path(destination)
    require(not destination.with_suffix(destination.suffix + ".sha256").exists(), "Existing model hash file")
    env = environment(config)
    matrices = training_matrices(training_rows(config, data_dir), config)
    started = datetime.now(timezone.utc).isoformat()
    models = []
    fitted_predictions = {}
    with threadpool_limits(limits=config["execution"]["blas_thread_limit"]):
        # One fit for each direct target/lead component. No search or refit.
        for v in config["targets"]:
            for h in range(1, 8):
                load_config()  # recheck freeze immediately before fitting
                pipeline = new_pipeline(config)
                pipeline.fit(matrices.x[h], matrices.y[v, h])
                fitted_predictions[v, h] = pipeline.predict(matrices.x[h])
                models.append(export_pipeline(pipeline, v, h))
        env["threadpools_during_fit"] = [{k: p.get(k) for k in
            ("user_api", "internal_api", "prefix", "version", "num_threads", "threading_layer", "architecture")}
            for p in threadpool_info()]
    bundle = {"artifact_version": "ridge-direct-json/1", "config_sha256": APPROVED_SHA256,
              "configuration": config, "input_sha256": {"fit_targets.csv": config["input_sha256"]["fit_targets.csv"]},
              "feature_names": list(FEATURE_NAMES), "models": models,
              "training_first_issue": matrices.issues[0].isoformat(), "training_last_issue": matrices.issues[-1].isoformat(),
              "fit_calls": len(models), "validation_rows_used_for_fit": 0,
              "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
              "environment": env, "implementation_sha256": code_hashes()}
    load_config()
    # Verify JSON round-trip for every fitted pipeline, with no additional fits.
    restored = restore_pipelines(json.loads(json.dumps(bundle, allow_nan=False)))
    with threadpool_limits(limits=1):
        differences = [float(np.max(np.abs(prediction-restored[key].predict(matrices.x[key[1]]))))
                       for key, prediction in fitted_predictions.items()]
    require(max(differences) <= 1e-10, "Model serialization changes predictions")
    bundle["all_pipelines_json_roundtrip_max_abs_error"] = max(differences)
    write_json(destination, bundle)
    destination.with_suffix(destination.suffix + ".sha256").write_text(
        sha256(destination) + "  " + destination.name + "\n", encoding="ascii", newline="\n")
    return bundle


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "model_parameters.json")
    args = parser.parse_args()
    result = train(args.output)
    print(json.dumps({"models_fitted": len(result["models"]), "rows_per_model": 6501,
                      "config_sha256": result["config_sha256"], "validation_rows_used_for_fit": 0}, indent=2))
