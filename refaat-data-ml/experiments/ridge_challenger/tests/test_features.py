"""Pre-fit approval, chronological boundaries and feature leakage tests; no fitting."""
import copy
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
import numpy as np

from climate_data.climatology import DailyTarget, float32, phase
from climate_data.evaluation import load_diagnostic_data
from experiments.ridge_challenger.common import APPROVED_SHA256, HERE, ROOT, load_config
from experiments.ridge_challenger.features import FEATURE_NAMES, feature_vector, training_matrices, training_rows
from experiments.ridge_challenger.train import new_pipeline


def sample_history(issue, values=None):
    values = list(range(1, 61)) if values is None else values
    return tuple(DailyTarget(issue-timedelta(days=66)+timedelta(days=i), float(v), float(v)/10)
                 for i, v in enumerate(values))


class FeatureAndBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()
        cls.rows = training_rows(cls.config)
        cls.matrices = training_matrices(cls.rows, cls.config)

    def test_approval_and_exact_hash(self):
        self.assertEqual(hashlib.sha256((HERE / "config.json").read_bytes()).hexdigest(), APPROVED_SHA256)
        self.assertEqual((HERE / "config.sha256").read_text().split()[0], APPROVED_SHA256)
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            config = Path(tmp) / "config.json"
            approval = Path(tmp) / "approval.json"
            changed = copy.deepcopy(self.config)
            changed["ridge"]["parameters"]["alpha"] = 2
            config.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "configuration changed"):
                load_config(config_path=config)
            approval.write_text(json.dumps({"approved": False}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "approval"):
                load_config(approval_path=approval)

    def test_exact_feature_order_and_fixed_estimator(self):
        self.assertEqual(FEATURE_NAMES, ("target_annual_sin", "target_annual_cos", "tmax_last",
            "tmax_mean_7", "tmax_mean_30", "tmax_mean_60", "et0_last", "et0_mean_7", "et0_mean_30", "et0_mean_60"))
        pipeline = new_pipeline(self.config)
        self.assertEqual(pipeline.named_steps["ridge"].get_params(), self.config["ridge"]["parameters"])
        self.assertEqual(pipeline.named_steps["scale"].get_params(), self.config["preprocessing"]["parameters"])
        self.assertFalse(hasattr(pipeline.named_steps["ridge"], "coef_"))

    def test_hand_calculated_history_statistics_and_float32(self):
        issue = date(2010, 8, 10)
        history = sample_history(issue)
        vector = feature_vector(issue, history, 3)
        self.assertEqual(vector.dtype, np.float64)
        np.testing.assert_array_equal(vector[2:6], [60, 57, 45.5, 30.5])
        expected = [float32(6)] + [math.fsum(float32(i/10) for i in range(61-n, 61))/n for n in (7, 30, 60)]
        np.testing.assert_array_equal(vector[6:10], expected)
        theta = 2*math.pi*phase(issue+timedelta(days=3))/366
        np.testing.assert_array_equal(vector[:2], [math.sin(theta), math.cos(theta)])

    def test_calendar_leap_and_year_wrap(self):
        for target in (date(2020, 2, 29), date(2020, 3, 1), date(2019, 3, 1), date(2020, 1, 1)):
            issue = target-timedelta(days=1)
            vector = feature_vector(issue, sample_history(issue), 1)
            slot = (date(2000, target.month, target.day)-date(2000, 1, 1)).days
            self.assertAlmostEqual(vector[0], math.sin(2*math.pi*slot/366), places=15)
            self.assertAlmostEqual(vector[1], math.cos(2*math.pi*slot/366), places=15)
        self.assertEqual(phase(date(2020, 3, 1)), phase(date(2019, 3, 1)))

    def test_rejects_missing_duplicate_future_and_unordered_context(self):
        issue = date(2020, 3, 1)
        valid = sample_history(issue)
        invalid = [valid[:-1], (*valid, valid[-1]), tuple(reversed(valid)),
                   (valid[0], *valid[:-1]),
                   (*valid[:-1], DailyTarget(issue-timedelta(days=6), 20.0, 3.0))]
        for history in invalid:
            with self.subTest(length=len(history)), self.assertRaises(ValueError):
                feature_vector(issue, history, 1)

    def test_rejects_fill_nonfinite_and_invalid_leads(self):
        issue = date(2020, 3, 1)
        history = sample_history(issue)
        for value in (float("nan"), float("inf"), -999.0, True, "20"):
            bad = (*history[:-1], DailyTarget(history[-1].day, value, 2.0))
            with self.assertRaises(ValueError):
                feature_vector(issue, bad, 1)
        for lead in (0, 8, True, 1.5, "1"):
            with self.assertRaises(ValueError):
                feature_vector(issue, history, lead)

    def test_all_training_examples_and_labels_within_authorized_bounds(self):
        matrices = self.matrices
        self.assertEqual((matrices.issues[0], matrices.issues[-1], len(matrices.issues)),
                         (date(2001, 3, 8), date(2018, 12, 24), 6501))
        self.assertEqual(matrices.issues[0]-timedelta(days=66), date(2001, 1, 1))
        self.assertEqual(matrices.issues[-1]+timedelta(days=7), date(2018, 12, 31))
        for lead in range(1, 8):
            self.assertEqual(matrices.x[lead].shape, (6501, 10))
            for target in ("tmax_c", "et0_mm_day"):
                expected = [float32(getattr(self.rows[(issue+timedelta(days=lead)-date(2001, 1, 1)).days], target))
                            for issue in matrices.issues]
                np.testing.assert_array_equal(matrices.y[target, lead], expected)
        for i, issue in enumerate(matrices.issues):
            self.assertEqual(issue, matrices.issues[0]+timedelta(days=i))
            self.assertLessEqual(issue+timedelta(days=7), date(2018, 12, 31))

    def test_training_features_are_as_of_for_every_issue(self):
        for i, issue in enumerate(self.matrices.issues):
            cutoff_index = (issue-timedelta(days=7)-date(2001, 1, 1)).days
            expected_tmax = float32(self.rows[cutoff_index].tmax_c)
            expected_et0 = float32(self.rows[cutoff_index].et0_mm_day)
            for lead in range(1, 8):
                self.assertEqual(self.matrices.x[lead][i, 2], expected_tmax)
                self.assertEqual(self.matrices.x[lead][i, 6], expected_et0)
                np.testing.assert_array_equal(self.matrices.x[lead][i, 2:], self.matrices.x[1][i, 2:])

    def test_training_loader_needs_no_validation_file(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            directory = Path(tmp)
            (directory / "fit_targets.csv").write_bytes((ROOT / "data/fit_targets.csv").read_bytes())
            self.assertEqual(training_rows(self.config, directory), self.rows)
            with (directory / "fit_targets.csv").open("ab") as stream:
                stream.write(b"\n")
            with self.assertRaisesRegex(ValueError, "identity"):
                training_rows(self.config, directory)

    def test_training_rejects_boundary_extension_and_gaps(self):
        for rows in (self.rows[1:], (*self.rows, DailyTarget(date(2019, 1, 1), 20.0, 3.0)),
                     (*self.rows[:-1], DailyTarget(date(2019, 1, 1), 20.0, 3.0))):
            with self.assertRaises(ValueError):
                training_matrices(rows, self.config)

    def test_validation_future_perturbations_do_not_change_features(self):
        dataset = load_diagnostic_data(ROOT / "data")
        window, history = next(dataset.contexts())
        self.assertEqual(history[-1].day, date(2019, 1, 8))
        modified = copy.deepcopy(dataset)
        for day in modified.validation:
            if day > window.cutoff:
                modified.validation[day] = DailyTarget(day, 10000.0, 10000.0)
        _, modified_history = next(modified.contexts())
        for lead in range(1, 8):
            np.testing.assert_array_equal(feature_vector(window.issue, history, lead),
                                          feature_vector(window.issue, modified_history, lead))


if __name__ == "__main__":
    unittest.main()
