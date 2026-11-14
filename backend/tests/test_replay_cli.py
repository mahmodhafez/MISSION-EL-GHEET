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

    def test_cli_compare_uh(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = main(["compare-uh", "--anchors", "2015,2016"])
        self.assertEqual(exit_code, 0)
        output = json.loads(f.getvalue())
        self.assertEqual(output["scenario_id"], "UH-001")
        self.assertIn("season_2_maize_tradeoff_summary", output)
        self.assertEqual(output["agricultural_verdict"]["UH001_P0_BASELINE"], "rejected")

    def test_cli_replay_default(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = main(["replay", "--anchors", "2015,2016", "--template-year", "2026"])
        self.assertEqual(exit_code, 0)
        output = json.loads(f.getvalue())
        self.assertEqual(output["status"], "complete")
        self.assertEqual(len(output["blocks"]), 2)

    def test_cli_evidence_card(self):
        f = io.StringIO()
        with redirect_stdout(f):
            exit_code = main(["evidence-card", "--plan", "R1", "--anchors", "2015,2016"])
        self.assertEqual(exit_code, 0)
        output = json.loads(f.getvalue())
        self.assertEqual(output["input_ref"]["scenario_id"], "UH-001")
        self.assertEqual(output["plan_status"], "needs_review")
        self.assertEqual(output["decision_state"], "review_draft")


if __name__ == "__main__":
    unittest.main()
