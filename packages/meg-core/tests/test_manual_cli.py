"""The manual-test CLI must run the real planner and its fixtures must match the test builders."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from planner_cli import encode, load, main  # noqa: E402
from test_constraints import uh001  # noqa: E402


def run(*argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = main(list(argv))
    return code, out.getvalue()


class ManualCli(unittest.TestCase):
    def test_uh001_fixture_matches_builder_and_real_result(self):
        _, snapshot, kb, *_ = load(TOOLS / "fixtures" / "uh001.json")
        _, expected_snapshot, expected_kb = uh001()
        self.assertEqual(encode(kb), encode(expected_kb))
        self.assertEqual(encode(snapshot.input.seasons), encode(expected_snapshot.input.seasons))
        code, out = run("plan", str(TOOLS / "fixtures" / "uh001.json"), "--json")
        result = json.loads(out)["result"]
        self.assertEqual(code, 0)
        self.assertEqual(result["current"]["status"], "rejected")
        self.assertEqual(result["current"]["checks"][0]["explanation"]["code"], "sowing_before_protected_cut")
        self.assertEqual(sorted(c["plan"][1]["sowing_date"]["value"] for c in result["review_investigations"]),
                         ["2027-05-28", "2027-06-01"])
        self.assertEqual(result["feasible_alternatives"], [])

    def test_unconfirmed_scope_is_refused_and_synthetic_is_labelled(self):
        code, out = run("plan", str(TOOLS / "fixtures" / "synthetic-mixed.json"), "--no-confirm")
        self.assertEqual(code, 2)
        self.assertIn("SYNTHETIC", out)
        self.assertIn("exploration_not_confirmed", out)


if __name__ == "__main__":
    unittest.main()
