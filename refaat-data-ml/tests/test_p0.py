"""Repository and portable combined consumer checks, independent of team backend."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.verify_legacy import verify
from scripts.export_kb_schema import schema
from make_handoffs import recipient_files

ROOT = Path(__file__).resolve().parents[1]


class P0HandoffTests(unittest.TestCase):
    def test_original_delivery_all_hashes_and_schema_export_preserved(self):
        self.assertEqual(verify(ROOT), 66)
        self.assertEqual(json.loads((ROOT / "agricultural_kb/schema.json").read_bytes()), schema())

    def test_recipient_inventories_complete_and_no_experimental_weights(self):
        backend = recipient_files(ROOT, "backend")
        for name in ("knowledge_base/agricultural_kb.json", "agricultural_kb/schema.json",
                     "examples/backend_p0.py", "AGRICULTURAL_KB_CONTRACT.md"):
            self.assertIn(name, backend)
        for role in ("backend", "ml"):
            for name, path in recipient_files(ROOT, role).items():
                self.assertTrue(path.is_file(), name)
                self.assertNotIn(path.suffix, {".pt", ".safetensors", ".zip"})

    def test_combined_consumer_from_independent_folder_without_site_packages(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            base = Path(tmp)
            for folder in ("agricultural_kb", "knowledge_base", "climate_data", "data", "examples"):
                shutil.copytree(ROOT / folder, base / folder, ignore=shutil.ignore_patterns("__pycache__"))
            code = "import sys,json; from examples.backend_p0 import example; print(json.dumps(example(),allow_nan=False)); assert not {'torch','chronos','sklearn','ortools'}.intersection(sys.modules)"
            result = subprocess.run([sys.executable, "-B", "-S", "-c", code], cwd=base, capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["planner_constraints"], [])
            self.assertEqual(value["kb_status"]["status"], "NO_LOCAL_SIGN_OFF")
            self.assertEqual(value["weather"]["coverage"]["valid_days"], 3)
            self.assertEqual(value["weather"]["status"], "complete")
            self.assertIn("quality", value["weather"])
            self.assertIn("provenance", value["weather"])
            self.assertEqual(value["evidence"]["scientific_status"], "VERIFIED")


if __name__ == "__main__":
    unittest.main()
