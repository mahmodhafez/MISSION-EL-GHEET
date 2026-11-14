"""Post-fit scientific checks. No additional forecast model is fitted in these tests."""
import copy
import csv
from datetime import date
import json
import math
from pathlib import Path
from statistics import fmean
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from climate_data.climatology import DailyTarget, float32
from climate_data.evaluation import distribution_scores, load_diagnostic_data, score_predictions
from experiments.ridge_challenger.common import APPROVED_SHA256, HERE, ROOT, load_config, output_path, sha256
from experiments.ridge_challenger.evaluate import baselines, compare_metrics, evaluate
from experiments.ridge_challenger.features import FEATURE_NAMES, feature_vector, training_matrices, training_rows
from experiments.ridge_challenger.train import load_model, predict_contexts, restore_pipelines, train


class ExperimentResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()
        cls.bundle = load_model(HERE / "model_parameters.json")
        cls.result = json.loads((HERE / "metrics.json").read_bytes())
        cls.dataset = load_diagnostic_data(ROOT / "data")
        cls.matrices = training_matrices(training_rows(cls.config), cls.config)
        with (HERE / "predictions.csv").open(encoding="utf-8", newline="") as stream:
            cls.predictions = list(csv.DictReader(stream))

    def test_frozen_config_model_identity_and_exact_fit_scope(self):
        self.assertEqual(self.bundle["config_sha256"], APPROVED_SHA256)
        self.assertEqual(self.bundle["configuration"], self.config)
        self.assertEqual(self.bundle["fit_calls"], 14)
        self.assertEqual(self.bundle["validation_rows_used_for_fit"], 0)
        self.assertEqual(self.bundle["training_first_issue"], "2001-03-08")
        self.assertEqual(self.bundle["training_last_issue"], "2018-12-24")
        self.assertEqual(len(self.bundle["models"]), 14)
        self.assertEqual(self.bundle["environment"]["packages"], self.config["execution"]["packages_pinned_to_observed_environment"])
        self.assertTrue(all(p["num_threads"] == 1 for p in self.bundle["environment"]["threadpools_during_fit"]))

    def test_each_scaler_matches_only_training_statistics(self):
        for record in self.bundle["models"]:
            x = self.matrices.x[record["lead_from_issue"]]
            self.assertEqual(record["training_rows"], 6501)
            np.testing.assert_allclose(record["scaler"]["mean"], x.mean(axis=0), rtol=1e-12, atol=1e-12)
            np.testing.assert_allclose(record["scaler"]["var"], x.var(axis=0, ddof=0), rtol=1e-12, atol=1e-12)
            np.testing.assert_allclose(record["scaler"]["scale"], x.std(axis=0, ddof=0), rtol=1e-12, atol=1e-12)
        # A synthetic scaler-only unit fixture checks the approved zero-variance policy.
        scaler = StandardScaler(**self.config["preprocessing"]["parameters"])
        transformed = scaler.fit_transform(np.array([[2.0, 0.0], [2.0, 4.0]]))
        np.testing.assert_array_equal(scaler.scale_, [1.0, 2.0])
        np.testing.assert_array_equal(transformed, [[0.0, -1.0], [0.0, 1.0]])

    def test_saved_coefficients_satisfy_approved_ridge_normal_equations(self):
        # Independent mathematical check of training labels, alpha, intercept and scaling.
        with threadpool_limits(limits=1):
            for record in self.bundle["models"]:
                v, h = record["target"], record["lead_from_issue"]
                x = (self.matrices.x[h]-np.asarray(record["scaler"]["mean"]))/np.asarray(record["scaler"]["scale"])
                coef = np.asarray(record["ridge"]["coef"])
                intercept = record["ridge"]["intercept"]
                residual = self.matrices.y[v, h]-(x@coef+intercept)
                np.testing.assert_allclose(x.T@residual, self.config["ridge"]["parameters"]["alpha"]*coef,
                                           atol=2e-6, rtol=1e-7)
                self.assertLess(abs(residual.mean()), 1e-10)

    def test_reload_repeat_predictions_match_saved_values_no_refitting(self):
        before = sha256(HERE / "model_parameters.json")
        with patch.object(Ridge, "fit", side_effect=AssertionError("Inference attempted model fitting")), \
             patch.object(StandardScaler, "fit", side_effect=AssertionError("Inference attempted scaler fitting")):
            first = predict_contexts(self.bundle, self.dataset.contexts())
            second = predict_contexts(load_model(HERE / "model_parameters.json"), self.dataset.contexts())
        expected = [float(r["prediction"]) for r in self.predictions if r["model"] == "ridge"]
        np.testing.assert_allclose([r["q50"] for r in first], expected, rtol=0, atol=1e-10)
        np.testing.assert_array_equal([r["q50"] for r in first], [r["q50"] for r in second])
        self.assertEqual(before, sha256(HERE / "model_parameters.json"))
        self.assertEqual(self.bundle["all_pipelines_json_roundtrip_max_abs_error"], 0.0)

    def test_future_truth_perturbation_cannot_change_same_issue_predictions(self):
        window, history = next(self.dataset.contexts())
        changed = copy.deepcopy(self.dataset)
        for day in changed.validation:
            if day > window.cutoff:
                changed.validation[day] = DailyTarget(day, -10000.0, 10000.0)
        modified_window, modified_history = next(changed.contexts())
        original = predict_contexts(self.bundle, [(window, history)])
        modified = predict_contexts(self.bundle, [(modified_window, modified_history)])
        self.assertEqual(original, modified)
        # A value actually available at C may change the corresponding features.
        changed.validation[window.cutoff] = DailyTarget(window.cutoff, 10000.0, 10000.0)
        _, available_change = next(changed.contexts())
        self.assertFalse(np.array_equal(feature_vector(window.issue, history, 1),
                                       feature_vector(window.issue, available_change, 1)))

    def test_all_models_have_identical_252_target_dates_and_point_only_outputs(self):
        expected_keys = {(w.issue.isoformat(), day.isoformat(), v)
                         for w in self.dataset.windows for day in w.targets() for v in self.config["targets"]}
        self.assertEqual(len(self.predictions), 1512)
        for model in ("ridge", "persistence", "seasonal_climatology"):
            rows = [r for r in self.predictions if r["model"] == model]
            self.assertEqual(len(rows), 504)
            self.assertEqual({(r["issue"], r["target_date"], r["variable"]) for r in rows}, expected_keys)
            for row in rows:
                self.assertEqual(int(row["step_from_cutoff"]), int(row["lead_from_issue"])+7)
                self.assertNotIn("q10", row)
                self.assertNotIn("q90", row)
                self.assertEqual(float(row["truth"]), float32(getattr(
                    self.dataset.validation[date.fromisoformat(row["target_date"])], row["variable"])))

    def test_all_overall_and_per_lead_metrics_independently_recomputed(self):
        for table in (self.result["overall"], self.result["by_lead"]):
            for metric in table:
                rows = [r for r in self.predictions if r["model"] == metric["model"] and
                        r["variable"] == metric["target"] and ("lead_from_issue" not in metric or
                        int(r["lead_from_issue"]) == metric["lead_from_issue"])]
                errors = [float(r["prediction"])-float(r["truth"]) for r in rows]
                self.assertEqual(metric["samples"], len(errors))
                self.assertAlmostEqual(metric["mae"], fmean(abs(e) for e in errors), places=13)
                self.assertAlmostEqual(metric["rmse"], math.sqrt(fmean(e*e for e in errors)), places=13)
                self.assertAlmostEqual(metric["bias"], fmean(errors), places=13)
        fixture = distribution_scores([{"truth": 1.0, "q50": 3.0}, {"truth": 5.0, "q50": 4.0}])
        self.assertEqual(fixture, {"mae": 1.5, "rmse": math.sqrt(2.5), "bias": 0.5})

    def test_differences_percentages_and_win_loss_directions(self):
        for rows in (self.result["comparisons"], self.result["comparisons_by_lead"]):
            for row in rows:
                delta = row["baseline_value"]-row["ridge_value"]
                self.assertEqual(row["baseline_minus_ridge"], delta)
                self.assertEqual(row["improvement_percent"], 100*delta/row["baseline_value"])
                self.assertEqual(row["ridge_result"], "WIN" if delta > 0 else "LOSS" if delta < 0 else "TIE")
        self.assertEqual(compare_metrics(self.result["overall"]), self.result["comparisons"])

    def test_reproduced_baselines_and_scorer_rejection_of_unpaired_dates(self):
        expected = json.loads((HERE / "audit.json").read_bytes())["baseline_metrics"]
        for model, forecasts in baselines(self.dataset).items():
            scored, measured = score_predictions(self.dataset, forecasts)
            for target, scores in measured.items():
                reference = next(r for r in expected if r["model"] == model and r["target"] == target)
                for metric in ("mae", "rmse", "bias"):
                    self.assertEqual(scores[metric], reference[metric])
            with self.assertRaises(ValueError):
                score_predictions(self.dataset, forecasts[:-1])
            with self.assertRaises(ValueError):
                score_predictions(self.dataset, [forecasts[0], *forecasts])

    def test_model_corruption_and_missing_components_rejected(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            path = Path(tmp) / "model.json"
            path.write_bytes((HERE / "model_parameters.json").read_bytes()+b"\n")
            path.with_suffix(".json.sha256").write_text(sha256(HERE / "model_parameters.json"), encoding="ascii")
            with self.assertRaisesRegex(ValueError, "integrity"):
                load_model(path)
        incomplete = copy.deepcopy(self.bundle)
        incomplete["models"].pop()
        with self.assertRaisesRegex(ValueError, "Missing"):
            restore_pipelines(incomplete)

    def test_outputs_and_config_protected_against_overwrite(self):
        before = sha256(HERE / "model_parameters.json")
        with self.assertRaisesRegex(ValueError, "new output"):
            train(HERE / "model_parameters.json")
        with self.assertRaisesRegex(ValueError, "new output"):
            evaluate()
        with self.assertRaisesRegex(ValueError, "inside"):
            output_path(ROOT / "outside_ridge_test.json")
        self.assertEqual(before, sha256(HERE / "model_parameters.json"))
        self.assertEqual(sha256(HERE / "config.json"), APPROVED_SHA256)

    def test_independence_from_p0_backend_and_other_trained_models(self):
        for module in ("agricultural_kb", "climate_data.backend", "climate_data.replay", "torch", "chronos", "ortools"):
            self.assertNotIn(module, sys.modules)


if __name__ == "__main__":
    unittest.main()
