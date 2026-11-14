"""Unit tests for the Season Replay & Climatology CLI."""

import io
import json
import sys
import unittest
from contextlib import redirect_stdout

from backend.app.replay.cli import main


class TestReplayCLI(unittest.TestCase):
    def test_cli_climatology(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = main(["climatology", "--date", "2027-05-28", "--ref", "historical_2001_2025"])
        self.assertEqual(exit_code, 0)
        output = json.loads(f.getvalue())
        self.assertEqual(output["status"], "complete")
        self.assertEqual(output["reference_id"], "historical_2001_2025")
        self.assertIn("tmax_c", output["quantiles"])
        self.assertIn("et0_mm_day", output["quantiles"])

    def test_cli_climatology_default_is_evaluated_baseline(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = main(["climatology", "--date", "2027-05-28"])
        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(f.getvalue())["reference_id"], "ml_fit_2001_2018")

    def test_cli_compare_uh(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = main(["compare-uh", "--years", "2015,2016"])
        self.assertEqual(exit_code, 0)
        output = json.loads(f.getvalue())
        self.assertEqual(output["scenario"]["scenario_id"], "UH-001")
        self.assertEqual(output["scenario"]["original_plan_status"], "rejected")
        self.assertEqual(output["layer_a_historical"]["years_used"], [2015, 2016])

    def test_cli_windows_text_is_bilingual(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = main(["windows", "--dates", "2027-05-28,2027-06-01", "--years", "2015,2016", "--text"])
        self.assertEqual(exit_code, 0)
        text = f.getvalue()
        self.assertIn("not a full crop-season analysis", text)
        self.assertIn("مش توقع للطقس", text)

    def test_cli_replay_requires_explicit_plans(self):
        with self.assertRaises(SystemExit):
            main(["replay", "--anchors", "2015"])

    def test_cli_evidence_card(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = main(["evidence-card", "--sow", "2027-05-28"])
        self.assertEqual(exit_code, 0)
        output = json.loads(f.getvalue())
        self.assertEqual(output["input_ref"]["scenario_id"], "UH-001")
        self.assertEqual(output["plan_status"], "needs_review")
        self.assertEqual(output["decision_state"], "review_draft")
        self.assertEqual(output["climate_evidence"]["years_used"], 25)


if __name__ == "__main__":
    unittest.main()
