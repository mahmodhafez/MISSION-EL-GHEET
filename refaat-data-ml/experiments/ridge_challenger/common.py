"""Pinned experiment identity and integrity checks. No P0 code is modified."""
from __future__ import annotations
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APPROVED_SHA256 = "3978160d209fdfb4dc024d11a9efe1f81b52c19647d2b0d31d962f686ab8c1bc"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_config(config_path=None, approval_path=None):
    config_path = HERE / "config.json" if config_path is None else Path(config_path)
    approval_path = HERE / "approval.json" if approval_path is None else Path(approval_path)
    require(sha256(config_path) == APPROVED_SHA256, "Approved configuration changed; refusing execution")
    approval = json.loads(approval_path.read_bytes())
    require(approval.get("approved") is True and approval.get("status") == "APPROVED_AND_FROZEN"
            and approval.get("config_sha256") == APPROVED_SHA256, "Explicit approval/freeze record missing")
    return json.loads(config_path.read_bytes())


def verify_input(config, name, data_dir=None):
    directory = ROOT / "data" if data_dir is None else Path(data_dir)
    path = directory / name
    require(sha256(path) == config["input_sha256"][name], "Input identity mismatch: " + name)
    return path


def environment(config):
    versions = {name: importlib.metadata.version(name)
                for name in config["execution"]["packages_pinned_to_observed_environment"]}
    require(versions == config["execution"]["packages_pinned_to_observed_environment"],
            "Package versions differ from approved configuration")
    require(platform.python_version() == config["execution"]["python_observed"],
            "Python version differs from approved environment")
    return {"python": platform.python_version(), "platform": platform.platform(), "packages": versions}


def output_path(path):
    target = Path(path).resolve()
    require(target.is_relative_to(HERE) and target != HERE, "Experiment outputs must stay inside ridge_challenger")
    require(not target.exists(), "Choose a new output path: " + target.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def write_csv(path, rows):
    require(bool(rows), "No output rows")
    with Path(path).open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def code_hashes():
    return {p.name: sha256(p) for p in sorted(HERE.glob("*.py"))}
