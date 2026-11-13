"""CLI regressions for frozen-release ET0 regeneration; standard library only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "data/validation/regenerate_et0.py"
ARCHIVE = ROOT / "docs/VALIDATION_ARTIFACTS.zip"


class RegenerationTests(unittest.TestCase):
    def run_cli(self, *args):
        # Exercise without user site packages, PYTHONPATH or implicit imports.
        result = subprocess.run([sys.executable, "-I", "-S", str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True, check=False)
        try:
            report = json.loads(result.stdout)
        except ValueError:
            self.fail(f"Expected structured result, exit {result.returncode}: {result.stderr}")
        return result.returncode, report

    def test_unknown_input_vintage_does_not_create_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            raw = folder / "newer.json"
            raw.write_text('{}', encoding="utf-8")
            output = folder / "output"
            code, report = self.run_cli("--source", raw, "--period", "historical", "--output-dir", output)
            self.assertNotEqual(code, 0)
            self.assertIn("source checksum", report["error"])
            self.assertFalse(output.exists())

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            sentinel = folder / "keep.txt"
            sentinel.write_text("user work", encoding="utf-8")
            code, report = self.run_cli("--source", folder / "absent.json", "--period", "historical", "--output-dir", folder)
            self.assertNotEqual(code, 0)
            self.assertIn("already exists", report["error"])
            self.assertEqual(sentinel.read_text(), "user work")
            self.assertEqual(list(folder.iterdir()), [sentinel])

    def test_missing_inputs_are_an_explicit_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "output"
            code, report = self.run_cli("--archive", Path(temporary) / "missing.zip", "--period", "2026", "--output-dir", output)
            self.assertNotEqual(code, 0)
            self.assertEqual(report["status"], "failed")
            self.assertFalse(output.exists())

    @unittest.skipUnless(ARCHIVE.is_file(), "local frozen inputs unavailable")
    def test_both_frozen_periods_regenerate_exact_csvs_in_isolated_python(self):
        with tempfile.TemporaryDirectory() as temporary:
            for period, filename, count in (
                ("historical", "weather_et0.csv", 9131),
                ("2026", "weather_et0_2026_Jan_Oct.csv", 304),
            ):
                output = Path(temporary) / period
                code, report = self.run_cli("--archive", ARCHIVE, "--period", period, "--output-dir", output)
                self.assertEqual(code, 0, report)
                self.assertEqual(report["days"], count)
                self.assertEqual(report["reference_checks_passed"], 12)
                self.assertTrue(report["csv_sha256_matches_frozen"])
                with zipfile.ZipFile(ARCHIVE) as archive:
                    expected = archive.read("work/validation_2026-11-10/" + filename)
                self.assertEqual((output / filename).read_bytes(), expected)
                self.assertEqual(report["csv_sha256"], hashlib.sha256(expected).hexdigest())

    @unittest.skipUnless(ARCHIVE.is_file(), "local frozen inputs unavailable")
    def test_raw_file_path_works_without_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            raw = folder / "input.json"
            with zipfile.ZipFile(ARCHIVE) as archive:
                raw.write_bytes(archive.read("work/validation_2026-11-10/power_sakha_2026_Jan_Oct_LST.json"))
            code, report = self.run_cli("--source", raw, "--period", "2026", "--output-dir", folder / "result")
            self.assertEqual(code, 0, report)
            self.assertEqual(report["days"], 304)


if __name__ == "__main__":
    unittest.main()
