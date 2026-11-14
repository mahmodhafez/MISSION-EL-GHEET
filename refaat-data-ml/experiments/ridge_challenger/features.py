"""The exact ten approved features, using a strict 60-day as-of context."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
import math
import numpy as np

from climate_data.climatology import DailyTarget, TARGETS, TRAIN_START, TRAIN_END, float32, load_targets, phase
from .common import load_config, require, verify_input

FEATURE_NAMES = (
    "target_annual_sin", "target_annual_cos", "tmax_last", "tmax_mean_7",
    "tmax_mean_30", "tmax_mean_60", "et0_last", "et0_mean_7", "et0_mean_30", "et0_mean_60",
)


def check_design(config):
    require(tuple(d["name"] for d in config["features"]["ordered_definitions"]) == FEATURE_NAMES,
            "Feature order differs from approved design")
    require(config["features"]["count"] == 10 and config["forecast"]["model_count"] == 14,
            "Unexpected feature/model count")


def feature_vector(issue: date, history: tuple[DailyTarget, ...], lead: int) -> np.ndarray:
    """No access to target labels or a whole weather frame; reject unsliced history."""
    require(type(issue) is date and type(lead) is int and 1 <= lead <= 7, "Invalid issue or lead")
    require(len(history) == 60, "Require exactly 60 complete historical days")
    first = issue - timedelta(days=66)
    channels = {target: [] for target in TARGETS}
    for index, row in enumerate(history):
        require(type(row.day) is date and row.day == first + timedelta(days=index),
                "History must be ordered, contiguous and end at D-7")
        for target in TARGETS:
            value = getattr(row, target)
            require(type(value) in (int, float) and math.isfinite(value) and value != -999,
                    "Invalid historical value")
            try:
                rounded = float32(value)
            except (OverflowError, ValueError) as exc:
                raise ValueError("Historical value cannot be represented as float32") from exc
            require(math.isfinite(rounded), "Nonfinite rounded history")
            channels[target].append(rounded)
    angle = 2 * math.pi * phase(issue + timedelta(days=lead)) / 366
    result = [math.sin(angle), math.cos(angle)]
    for target in TARGETS:
        values = channels[target]
        result.extend([values[-1], *(math.fsum(values[-n:]) / n for n in (7, 30, 60))])
    return np.asarray(result, dtype=np.float64)


@dataclass
class TrainingMatrices:
    issues: tuple[date, ...]
    x: dict[int, np.ndarray]
    y: dict[tuple[str, int], np.ndarray]


def training_rows(config=None, data_dir=None):
    config = load_config() if config is None else config
    # Deliberately load only the training CSV; never load validation in train.py.
    path = verify_input(config, "fit_targets.csv", data_dir)
    return tuple(load_targets(path, TRAIN_START, TRAIN_END))


def training_matrices(rows, config=None):
    config = load_config() if config is None else config
    check_design(config)
    require(len(rows) == 6574, "Training must cover exactly 2001-2018")
    for index, row in enumerate(rows):
        require(row.day == TRAIN_START + timedelta(days=index) and row.day <= TRAIN_END,
                "Training dates absent, repeated, out of order or outside authorized period")
        for target in TARGETS:
            value = getattr(row, target)
            require(type(value) in (float, int) and math.isfinite(value) and value != -999,
                    "Invalid training observation or label")
    first, last = TRAIN_START + timedelta(days=66), TRAIN_END - timedelta(days=7)
    issues = tuple(first + timedelta(days=i) for i in range((last-first).days + 1))
    require((first.isoformat(), last.isoformat(), len(issues)) ==
            (config["training"]["first_issue"], config["training"]["last_issue"],
             config["training"]["examples_per_target_per_lead"]), "Training construction differs from config")
    x = {h: np.empty((len(issues), len(FEATURE_NAMES)), dtype=np.float64) for h in range(1, 8)}
    y = {(v, h): np.empty(len(issues), dtype=np.float64) for v in TARGETS for h in range(1, 8)}
    for i, issue in enumerate(issues):
        start = (issue - timedelta(days=66) - TRAIN_START).days
        history = rows[start:start+60]
        for h in range(1, 8):
            target_day = issue + timedelta(days=h)
            require(TRAIN_START <= target_day <= TRAIN_END, "Training label crossed boundary")
            x[h][i] = feature_vector(issue, history, h)
            label = rows[(target_day - TRAIN_START).days]
            for v in TARGETS:
                y[v, h][i] = float32(getattr(label, v))
    require(all(np.isfinite(a).all() for a in (*x.values(), *y.values())), "Nonfinite training matrix")
    return TrainingMatrices(issues, x, y)
