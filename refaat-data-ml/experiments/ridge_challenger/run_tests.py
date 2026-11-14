"""Record actual pre-fit or post-fit checks as JSON, without modifying P0 artifacts."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from .common import HERE, ROOT, output_path, write_json


def run(phase, output):
    output = output_path(output)
    scope = "experiments/ridge_challenger/tests"
    commands = ([["-m", "unittest", "discover", "-s", scope, "-p", "test_features.py", "-v"]]
                if phase == "prefit" else [
                    ["-m", "unittest", "discover", "-s", scope, "-p", "test_experiment.py", "-v"],
                    ["-m", "unittest", "discover", "-s", "tests", "-p", "test_ml.py", "-v"],
                    ["verify_package.py"]])
    records = []
    for args in commands:
        result = subprocess.run([sys.executable, "-B", *args], cwd=ROOT,
                                env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
                                capture_output=True, text=True, encoding="utf-8", timeout=240)
        log = (result.stdout + result.stderr).replace(str(ROOT), "<project>")
        match = re.search(r"Ran (\d+) tests? in", log)
        records.append({"command": "python -B " + " ".join(args), "exit_code": result.returncode,
                        "tests_run": int(match[1]) if match else None, "output": log})
        print(log, flush=True)
        if result.returncode:
            break
    report = {"phase": phase, "recorded_utc": datetime.now(timezone.utc).isoformat(), "commands": records,
              "status": "PASSED" if all(r["exit_code"] == 0 for r in records) else "FAILED",
              "tests_run": sum(r["tests_run"] or 0 for r in records)}
    write_json(output, report)
    if report["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("prefit", "postfit"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.phase, args.output)
