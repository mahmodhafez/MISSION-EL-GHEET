"""Rebuild the 36 diagnostic origins and score keyed forecasts without fitting a model."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from statistics import fmean
from tempfile import TemporaryDirectory

from .climatology import (
    DailyTarget, QUANTILES, SeasonalClimatology, TARGETS, TRAIN_END, TRAIN_START,
    VALID_END, VALID_START, float32, iso_date, load_targets,
)

WINDOW_COLUMNS = ("partition", "issue", "context_start", "cutoff", "target_start",
                  "target_end", "context_days", "scored_days")
UNITS = {"tmax_c": "degC", "et0_mm_day": "mm/day"}
DATASET_VERSION = "sakha-power-lst-20261110-et0-v1"


@dataclass(frozen=True)
class ForecastWindow:
    issue: date
    context_start: date
    cutoff: date
    target_start: date
    target_end: date

    @classmethod
    def for_issue(cls, day: date) -> ForecastWindow:
        cutoff = day - timedelta(days=7)
        return cls(day, cutoff - timedelta(days=59), cutoff,
                   day + timedelta(days=1), day + timedelta(days=7))

    def targets(self) -> Iterator[date]:
        for offset in range(7):
            yield self.target_start + timedelta(days=offset)


def load_windows(path: Path | str) -> list[ForecastWindow]:
    """Verify the exact 36 pre-existing monthly diagnostic issues and all cutoffs."""
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        if reader.fieldnames != list(WINDOW_COLUMNS):
            raise ValueError(f"Unexpected window columns: {reader.fieldnames}")
        rows = list(reader)
    expected = [ForecastWindow.for_issue(date(year, month, 15))
                for year in range(2019, 2022) for month in range(1, 13)]
    if len(rows) != len(expected):
        raise ValueError("Expected exactly 36 diagnostic origins")
    for row, window in zip(rows, expected):
        if set(row) != set(WINDOW_COLUMNS) or row["partition"] != "diagnostic_validation":
            raise ValueError("Only diagnostic_validation windows may enter this evaluation")
        for key in ("issue", "context_start", "cutoff", "target_start", "target_end"):
            if iso_date(row[key]) != getattr(window, key):
                raise ValueError(f"Wrong {key} for diagnostic issue {window.issue}")
        if row["context_days"] != "60" or row["scored_days"] != "7":
            raise ValueError(f"Wrong window length for diagnostic issue {window.issue}")
    return expected


@dataclass
class DiagnosticData:
    training: tuple[DailyTarget, ...]
    validation: dict[date, DailyTarget]
    windows: list[ForecastWindow]

    def contexts(self) -> Iterator[tuple[ForecastWindow, tuple[DailyTarget, ...]]]:
        """Yield only the 60 eligible historical days for each prescribed issue."""
        periods = {row.day: row for row in self.training}
        periods.update(self.validation)
        for window in self.windows:
            context = tuple(periods[window.context_start + timedelta(days=i)] for i in range(60))
            yield window, context


def load_diagnostic_data(data_dir: Path | str) -> DiagnosticData:
    """Load fixed inputs, strict splits and the dated diagnostic window ledger."""
    root = Path(data_dir)
    with (root / "release.json").open(encoding="utf-8") as stream:
        release = json.load(stream)
    if (release.get("dataset_version") != DATASET_VERSION
            or release.get("site_id") != "sakha_31.10_30.95"
            or release.get("time_standard") != "LST"):
        raise ValueError("Unexpected diagnostic data release, site or time standard")
    for name in ("fit_targets.csv", "diagnostic_validation_targets.csv", "forecast_windows.csv"):
        info = release.get("files", {}).get(name, {})
        data = (root / name).read_bytes()
        if len(data) != info.get("bytes") or hashlib.sha256(data).hexdigest() != info.get("sha256"):
            raise ValueError(f"Release digest mismatch: {name}")
    train = load_targets(root / "fit_targets.csv", TRAIN_START, TRAIN_END)
    validation = load_targets(root / "diagnostic_validation_targets.csv", VALID_START, VALID_END)
    windows = load_windows(root / "forecast_windows.csv")
    return DiagnosticData(tuple(train), {row.day: row for row in validation}, windows)


def seasonal_predictions(reference: SeasonalClimatology,
                         windows: Iterable[ForecastWindow]) -> Iterator[dict]:
    """Forecast using known calendar dates only, without access to validation truth."""
    for window in windows:
        for target_day in window.targets():
            estimates = reference.for_date(target_day)
            for variable in TARGETS:
                yield {"issue": window.issue.isoformat(), "cutoff": window.cutoff.isoformat(),
                       "target_date": target_day.isoformat(), "variable": variable,
                       "lead_from_issue": (target_day - window.issue).days,
                       "step_from_cutoff": (target_day - window.cutoff).days,
                       **estimates[variable]}


def distribution_scores(rows: list[dict]) -> dict:
    """Aggregate errors in original target units with equal weight per scored date."""
    errors = [row["q50"] - row["truth"] for row in rows]
    result = {"mae": fmean(map(abs, errors)), "rmse": math.sqrt(fmean(e*e for e in errors)),
              "bias": fmean(errors)}
    if "q10" in rows[0]:
        losses = []
        for row in rows:
            for quantile, probability in QUANTILES:
                residual = row["truth"] - row[quantile]
                losses.append(max(probability * residual, (probability - 1) * residual))
        result.update(interval_80_coverage=fmean(row["q10"] <= row["truth"] <= row["q90"] for row in rows),
                      interval_mean_width=fmean(row["q90"] - row["q10"] for row in rows),
                      mean_pinball_loss=fmean(losses))
    return result


def score_predictions(dataset: DiagnosticData, forecasts: Iterable[Mapping]) -> tuple[list[dict], dict]:
    """Score each keyed issue/variable/target day once; recompute truth from the data.

    Required fields: issue, target_date, variable, q50. Optional q10 and q90 must
    appear together on every forecast when a probabilistic comparison is requested.
    """
    expected = {(w.issue, day, target): w for w in dataset.windows for day in w.targets() for target in TARGETS}
    visited = set()
    scored = []
    interval_mode = None
    for row in forecasts:
        try:
            issue, day, target = iso_date(row["issue"]), iso_date(row["target_date"]), row["variable"]
            key = (issue, day, target)
            if key not in expected or key in visited:
                raise ValueError(f"Unexpected or duplicate forecast key {key}")
            window = expected[key]
            if "cutoff" in row and iso_date(row["cutoff"]) != window.cutoff:
                raise ValueError(f"Incorrect supplied cutoff for {key}")
            lead = (day - issue).days
            step = (day - window.cutoff).days
            for name, correct in (("lead_from_issue", lead), ("step_from_cutoff", step)):
                if name in row and str(row[name]) != str(correct):
                    raise ValueError(f"Incorrect supplied {name} for {key}")
            intervals = "q10" in row
            if intervals != ("q90" in row) or (interval_mode is not None and interval_mode != intervals):
                raise ValueError("Use either complete q10/q50/q90 or q50 alone for every row")
            interval_mode = intervals
            names = ("q10", "q50", "q90") if intervals else ("q50",)
            if any(isinstance(row[name], bool) for name in names):
                raise ValueError(f"Boolean prediction for {key}")
            quantiles = {name: float(row[name]) for name in names}
            values = list(quantiles.values())
            if not all(map(math.isfinite, values)) or values != sorted(values):
                raise ValueError(f"Nonfinite or crossed quantiles for {key}")
            truth = float32(getattr(dataset.validation[day], target))
        except (TypeError, KeyError) as exc:
            raise ValueError(f"Invalid prediction fields: {exc}") from exc
        scored.append({"issue": issue.isoformat(), "cutoff": window.cutoff.isoformat(),
                       "target_date": day.isoformat(), "variable": target,
                       "lead_from_issue": lead, "step_from_cutoff": step, "truth": truth, **quantiles})
        visited.add(key)
    if visited != set(expected):
        raise ValueError(f"Missing {len(expected)-len(visited)} required forecasts")
    results = {}
    for target in TARGETS:
        selected = [row for row in scored if row["variable"] == target]
        results[target] = {**distribution_scores(selected), "unit": UNITS[target],
                           "scored_target_days": len(selected), "mae_by_lead_1_to_7": [
                               fmean(abs(row["q50"]-row["truth"]) for row in selected if row["lead_from_issue"] == lead)
                               for lead in range(1, 8)]}
    return scored, results


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(data_dir: Path, output_dir: Path) -> dict:
    """Write 366 calendar slots, 504 keyed scored predictions and the measured scores."""
    if output_dir.exists():
        raise FileExistsError(f"Choose a new output directory: {output_dir}")
    inputs = load_diagnostic_data(data_dir)
    reference = SeasonalClimatology(inputs.training, TRAIN_START, TRAIN_END, research=True)
    forecasts = seasonal_predictions(reference, inputs.windows)
    scored, metrics = score_predictions(inputs, forecasts)
    calendar = []
    for slot in range(366):
        day = date(2000, 1, 1) + timedelta(days=slot)
        point = reference.for_date(day)
        record = {"month_day": day.strftime("%m-%d"), "support_days": point["support_days"],
                  "reference_start": point["reference_start"], "reference_end": point["reference_end"],
                  "method": point["method"]}
        for target in TARGETS:
            record.update({f"{target}_{q}": point[target][q] for q, _ in QUANTILES})
        calendar.append(record)
    input_hashes = {}
    for filename in ("fit_targets.csv", "diagnostic_validation_targets.csv", "forecast_windows.csv"):
        input_hashes[filename] = hashlib.sha256((data_dir / filename).read_bytes()).hexdigest()
    report = {"dataset_version": DATASET_VERSION, "site_id": "sakha_31.10_30.95",
              "method": reference.method, "reference_start": reference.reference_start,
              "reference_end": reference.reference_end, "split": "diagnostic_validation",
              "origin_count": len(inputs.windows), "train_rows": len(inputs.training),
              "validation_rows": len(inputs.validation), "source_sha256": input_hashes,
              "metrics": metrics}
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    # Stage a complete set first. Destination publication is a directory rename.
    with TemporaryDirectory(dir=output_dir.parent) as tmp:
        staged = Path(tmp) / "baseline"
        staged.mkdir()
        _write_csv(staged / "calendar_reference.csv", calendar)
        _write_csv(staged / "scored_predictions.csv", scored)
        (staged / "metrics.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
        staged.rename(output_dir)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New directory for derived results")
    args = parser.parse_args()
    results = run(args.data, args.output)
    print(json.dumps(results["metrics"], indent=2))


if __name__ == "__main__":
    main()
