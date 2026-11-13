"""Offline regressions for the evidence checker; no application/planner claims."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "data/validation/audit_saved_evidence.py"
ARCHIVE = ROOT / "docs/VALIDATION_ARTIFACTS.zip"
PREFIX = "work/validation_2026-11-10/"


@unittest.skipUnless(ARCHIVE.is_file(), "local-only validation archive required")
class EvidenceAuditTests(unittest.TestCase):
    def run_audit(self, archive):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--archive", str(archive)],
            capture_output=True, text=True, check=False,
        )
        try:
            report = json.loads(result.stdout)
        except ValueError:
            self.fail(f"Checker must emit JSON; exit={result.returncode}: {result.stderr}")
        return result.returncode, report

    def altered_archive(self, folder, member, edit):
        """Change evidence AND its package checksum to exercise semantic checks."""
        with zipfile.ZipFile(ARCHIVE) as source:
            names = [n for n in source.namelist()
                     if n == "ARTIFACT_MANIFEST.json" or
                     (n.startswith(PREFIX) and n.endswith((".json", ".csv", ".npz", ".py")))]
            contents = {n: source.read(n) for n in names}
        name = PREFIX + member
        contents[name] = edit(contents[name])
        manifest = json.loads(contents["ARTIFACT_MANIFEST.json"])
        for entry in manifest["entries"]:
            if entry["path"] == name:
                entry.update(bytes=len(contents[name]), sha256=hashlib.sha256(contents[name]).hexdigest())
        contents["ARTIFACT_MANIFEST.json"] = json.dumps(manifest).encode()
        target = Path(folder) / "altered.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as output:
            for name, raw in contents.items():
                output.writestr(name, raw)
        return target

    def check_mutation(self, member, edit, message):
        with tempfile.TemporaryDirectory() as folder:
            archive = self.altered_archive(folder, member, edit)
            code, report = self.run_audit(archive)
        self.assertNotEqual(code, 0)
        self.assertEqual(report["status"], "failed")
        self.assertIn(message, report["error"])

    def test_saved_evidence_reproduces_scores_and_interval_counts(self):
        before = ARCHIVE.stat().st_mtime_ns
        code, report = self.run_audit(ARCHIVE)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["weather"]["days"], 9435)
        self.assertEqual(report["ml"]["days_per_target"], 119)
        self.assertAlmostEqual(report["ml"]["scores"]["fine_tuned"]["tmax_c"]["mae"], 1.987569, places=5)
        self.assertEqual(report["ml"]["scores"]["fine_tuned"]["et0_mm_day"]["covered"], 84)
        self.assertEqual(report["ml"]["scores"]["fine_tuned"]["tmax_c"]["covered"], 91)
        self.assertEqual(ARCHIVE.stat().st_mtime_ns, before)

    def test_wrong_reported_mae_is_rejected(self):
        def edit(raw):
            report = json.loads(raw)
            report["scores"]["fine_tuned"]["tmax_c"]["mae"] = 0.1
            return json.dumps(report).encode()
        self.check_mutation("model_test/holdout_results.json", edit, "mae")

    def test_wrong_interval_coverage_is_rejected(self):
        def edit(raw):
            report = json.loads(raw)
            report["scores"]["fine_tuned"]["et0_mm_day"]["interval_80_coverage"] = 0.8
            return json.dumps(report).encode()
        self.check_mutation("model_test/holdout_results.json", edit, "interval_80_coverage")

    def test_dataset_vintage_mismatch_is_rejected(self):
        def edit(raw):
            report = json.loads(raw)
            report["input_hashes"]["weather_et0.csv"] = "0" * 64
            return json.dumps(report).encode()
        self.check_mutation("model_test/holdout_results.json", edit, "dataset-vintage mismatch")

    def test_wrong_station_year_is_rejected(self):
        self.check_mutation("check_station_table.py",
                            lambda raw: raw.replace(b'"2015-11"', b'"1999-11"'),
                            "station month coverage")

    def test_wrong_station_wind_conversion_is_detected(self):
        # A self-consistent package can still contain wrong scientific units.
        self.check_mutation("check_station_table.py",
                            lambda raw: raw.replace(b'70.30', b'7030.0'),
                            "station diagnostic")

    def test_wrong_power_units_are_rejected(self):
        def edit(raw):
            report = json.loads(raw)
            report["parameters"]["PS"]["units"] = "Pa"
            return json.dumps(report).encode()
        self.check_mutation("power_sakha_2001_2025_LST.json", edit, "POWER units")

    def test_request_metadata_must_match_saved_source(self):
        def edit(raw):
            report = json.loads(raw)
            report["url"] = report["url"].replace("latitude=31.10", "latitude=32.10")
            return json.dumps(report).encode()
        self.check_mutation("power_provenance.json", edit, "acquisition request")

    def test_seven_step_method_cannot_claim_next_week_from_d_minus_seven(self):
        self.check_mutation("model_test/evaluate_holdout.py",
                            lambda raw: raw.replace(b'prediction_length=14', b'prediction_length=7'),
                            "forecast-method provenance")

    def test_cross_learning_between_issue_dates_is_detected(self):
        self.check_mutation("model_test/evaluate_holdout.py",
                            lambda raw: raw.replace(b'cross_learning=False', b'cross_learning=True'),
                            "forecast-method provenance")

    def test_incomplete_evidence_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / "empty.zip"
            with zipfile.ZipFile(archive, "w"):
                pass
            code, report = self.run_audit(archive)
        self.assertNotEqual(code, 0)
        self.assertEqual(report["status"], "failed")


if __name__ == "__main__":
    unittest.main()
