"""Release-builder regressions: corruption and incomplete exports must not publish."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ml/tools/prepare_shared_release.py"


class SharedReleaseTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.exists(), "shared release builder is not implemented")
        spec = importlib.util.spec_from_file_location("prepare_shared_release", SCRIPT)
        self.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.builder)

    def test_changed_archive_is_rejected_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = root / "bad.zip"
            bad.write_bytes(b"not the approved archive")
            out = root / "release"
            with self.assertRaisesRegex(ValueError, "checksum"):
                self.builder.build(bad, ROOT / "docs/VALIDATION_ARTIFACTS.zip", out)
            self.assertFalse(out.exists())

    def test_existing_destination_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "marker"
            marker.write_text("preserve")
            with self.assertRaises(FileExistsError):
                self.builder.build(Path("unused"), Path("unused"), root)
            self.assertEqual(marker.read_text(), "preserve")

    def test_real_release_matches_sources_and_has_no_weights(self):
        refaat = ROOT.parent / "ML_HANDOFF.zip"
        science = ROOT / "docs/VALIDATION_ARTIFACTS.zip"
        if not refaat.exists() or not science.exists():
            self.skipTest("local source archives required")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "release"
            result = self.builder.build(refaat, science, out)
            self.assertEqual(result["alignment"]["dates"], 7670)
            self.assertEqual(result["alignment"]["numeric_mismatches"], 0)
            self.assertEqual(result["release_id"], "meg-shared-20261113-v1")
            self.assertFalse((out / "refaat/data/sakha_daily.csv").exists())
            self.assertEqual(result["files"]["weather/weather_et0.csv"]["sha256"],
                             "17141df82f6300c051257c21fb9ac3d9f5f1627fd32cbc8c07bc9296c477bde8")
            self.assertFalse(any(out.rglob("*.safetensors")))
            self.assertEqual(json.loads((out / "manifest.json").read_text())["alignment"], result["alignment"])


if __name__ == "__main__":
    unittest.main()
