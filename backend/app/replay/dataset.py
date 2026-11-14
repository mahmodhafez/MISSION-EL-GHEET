"""Sakha NASA POWER and ET0 historical dataset loader and store."""

from __future__ import annotations

import bisect
import csv
import hashlib
import json
import math
import os
import re
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from .climatology import SeasonalClimatology

Json = dict[str, Any]
SITE_ID = "sakha_31.10_30.95"
RELEASE = "sakha-power-lst-20261110-et0-v1"
METHOD = "fao56-dewpoint-asce-floor-v1"
UNITS = {
    "tmax_c": "degC",
    "tmin_c": "degC",
    "tdew_c": "degC",
    "rh_percent": "%",
    "wind2_m_s": "m/s",
    "solar_mj_m2_day": "MJ/m2/day",
    "pressure_kpa": "kPa",
    "rain_mm_day": "mm/day",
    "et0_mm_day": "mm/day",
    "et0_rhmean_approx_mm_day": "mm/day",
    "et0_without_cloud_floor_mm_day": "mm/day",
}
FLAG_COLUMNS = (
    "hard_invalid",
    "rs_above_rso",
    "raw_ratio_below_0_3",
    "negative_unbounded_cloud_factor",
    "negative_vpd",
    "negative_et0",
    "dew_above_tmin",
    "mixed_sources_in_response",
)


class ClimateInputError(ValueError):
    """Caller supplied an invalid site, date, interval or candidate plan."""


class ClimateDataError(ValueError):
    """The cached release does not match its manifest or contract."""


def iso_day(value: str) -> date:
    """Validate ISO YYYY-MM-DD format."""
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        raise ClimateInputError("Expected a calendar date in YYYY-MM-DD format.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ClimateInputError(f"Invalid calendar date: {value}") from exc


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def descriptive(values: list[float]) -> Json:
    """Min, median, max and count across included blocks; no independence assumption."""
    from statistics import median
    if not values:
        return {"count": 0, "min": None, "median": None, "max": None}
    return {"count": len(values), "min": min(values), "median": median(values), "max": max(values)}


def resolve_data_directory(explicit_dir: str | Path | None = None) -> Path:
    """Locate or extract the verified Sakha release directory."""
    if explicit_dir is not None:
        candidate = Path(explicit_dir)
        if candidate.is_dir() and (candidate / "release.json").is_file():
            return candidate

    env_dir = os.environ.get("MEG_CLIMATE_DATA_DIR")
    if env_dir:
        candidate = Path(env_dir)
        if candidate.is_dir() and (candidate / "release.json").is_file():
            return candidate

    repo_root = Path(__file__).resolve().parents[3]
    search_paths = [
        repo_root / "data" / "local" / "sakha",
        repo_root / "data" / "processed",
        repo_root / "refaat-data-ml" / "data",
    ]
    for p in search_paths:
        if p.is_dir() and (p / "release.json").is_file():
            return p

    # Attempt git extraction from origin/data/refaat-data-ml-recovery
    extract_target = repo_root / "data" / "local" / "sakha"
    try:
        extract_target.mkdir(parents=True, exist_ok=True)
        files = [
            "sakha_daily.csv", "quality_flags.csv", "fit_targets.csv",
            "diagnostic_validation_targets.csv", "forecast_windows.csv",
            "source_manifest.json", "release.json"
        ]
        for f in files:
            target_file = extract_target / f
            if not target_file.is_file():
                blob = subprocess.check_output(
                    ["git", "show", f"origin/data/refaat-data-ml-recovery:refaat-data-ml/data/{f}"],
                    cwd=repo_root
                )
                target_file.write_bytes(blob)
        if (extract_target / "release.json").is_file():
            return extract_target
    except Exception:
        pass

    raise ClimateDataError(
        f"Sakha climate dataset not found. Checked: {[str(p) for p in search_paths]}"
    )


class ClimateStore:
    """Load once per worker from the Sakha data release; queries execute in memory."""

    def __init__(self, data_dir: str | Path | None = None, site_id: str = SITE_ID):
        if site_id != SITE_ID:
            raise ClimateInputError(f"Supported site: {SITE_ID}")
        root = resolve_data_directory(data_dir)
        self.root = root
        try:
            release = json.loads((root / "release.json").read_bytes())
            if (release["site_id"], release["dataset_version"], release["et0_method_version"]) != (
                SITE_ID, RELEASE, METHOD
            ):
                raise ClimateDataError("Unsupported release, site or ET0 method.")
            for name in ("sakha_daily.csv", "quality_flags.csv", "source_manifest.json", "fit_targets.csv"):
                contents = (root / name).read_bytes()
                entry = release["files"][name]
                if len(contents) != entry["bytes"] or hashlib.sha256(contents).hexdigest() != entry["sha256"]:
                    raise ClimateDataError(f"File identity mismatch: {name}")
            self._sources = json.loads((root / "source_manifest.json").read_bytes())
            self._source_hashes = {r["snapshot"]: r["raw_sha256"] for r in self._sources}
            if set(self._source_hashes) != {"historical", "recent"}:
                raise ClimateDataError("Missing source snapshot.")
            self._weather: dict[date, Json] = {}
            self._quality: dict[date, Json] = {}
            for row in _rows(root / "sakha_daily.csv"):
                day = iso_day(row["date"])
                if day in self._weather or row["site_id"] != SITE_ID or row["snapshot"] not in self._source_hashes:
                    raise ClimateDataError("Duplicate date or invalid metadata in daily cache.")
                weather = {field: float(row[field]) for field in UNITS}
                if any(not math.isfinite(x) for x in weather.values()):
                    raise ClimateDataError("Non-finite daily data.")
                self._weather[day] = {**weather, "date": row["date"], "snapshot": row["snapshot"]}
            for row in _rows(root / "quality_flags.csv"):
                day = iso_day(row["date"])
                if day in self._quality or row["snapshot"] != self._weather[day]["snapshot"]:
                    raise ClimateDataError("Duplicate or unaligned QC row.")
                if any(row[key] not in {"0", "1"} for key in FLAG_COLUMNS) or row["hard_invalid"] != "0":
                    raise ClimateDataError("Invalid release QC flag.")
                if row["qc_disposition"] not in {"retain", "retain_review"}:
                    raise ClimateDataError("Unknown QC disposition.")
                self._quality[day] = {
                    "flags": tuple(key for key in FLAG_COLUMNS if row[key] == "1"),
                    "statistical_columns": tuple(filter(None, row["seasonal_3iqr_columns"].split("|"))),
                    "disposition": row["qc_disposition"],
                }
            if self._quality.keys() != self._weather.keys():
                raise ClimateDataError("Daily rows and quality rows have different dates.")
            self._days = sorted(self._weather)
            if len(self._days) != 9435 or self._days[0] != date(2001, 1, 1) or self._days[-1] != date(2026, 10, 31):
                raise ClimateDataError("Unexpected fixed snapshot coverage.")
            self._fit_reference = SeasonalClimatology.from_csv(root / "fit_targets.csv")
        except (OSError, KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, (ClimateDataError, ClimateInputError)):
                raise
            raise ClimateDataError(f"Cannot load cached Sakha release: {exc}") from exc

        self._app_reference: SeasonalClimatology | None = None
        fit_days = self._slice(date(2001, 1, 1), date(2018, 12, 31))
        fit_tmax = sorted(self._weather[day]["tmax_c"] for day in fit_days)
        position = (len(fit_tmax) - 1) * 0.90
        left = int(position)
        self._threshold_c = fit_tmax[left] + (position - left) * (fit_tmax[left + 1] - fit_tmax[left])

    def _meta(self, days: list[date]) -> Json:
        snapshots = sorted({self._weather[d]["snapshot"] for d in days})
        return {
            "site_id": SITE_ID,
            "dataset_version": RELEASE,
            "et0_method_version": METHOD,
            "time_standard": "LST",
            "source_sha256": {s: self._source_hashes[s] for s in snapshots},
        }

    def _slice(self, start: date, end: date) -> list[date]:
        return self._days[bisect.bisect_left(self._days, start):bisect.bisect_right(self._days, end)]

    def _quality_summary(self, days: list[date]) -> Json:
        flags: Counter[str] = Counter()
        statistical: Counter[str] = Counter()
        reviewed = 0
        for day in days:
            info = self._quality[day]
            flags.update(info["flags"])
            statistical.update(info["statistical_columns"])
            reviewed += info["disposition"] == "retain_review"
        return {
            "review_days": reviewed,
            "flag_day_counts": dict(sorted(flags.items())),
            "statistical_column_day_counts": dict(sorted(statistical.items())),
        }

    def _range(self, start: str, end: str) -> tuple[Json, list[date]]:
        begin, finish = iso_day(start), iso_day(end)
        if finish < begin:
            raise ClimateInputError("end precedes start.")
        days = self._slice(begin, finish)
        expected = (finish - begin).days + 1
        status = "complete" if expected == len(days) else ("partial" if days else "unavailable")
        return {
            "status": status,
            "start": start,
            "end": end,
            "coverage": {
                "expected_days": expected,
                "valid_days": len(days),
                "fraction": len(days) / expected,
            },
            "quality": self._quality_summary(days),
            "provenance": self._meta(days),
        }, days

    def _metrics(self, days: list[date]) -> Json:
        if not days:
            raise ClimateInputError("An indicator window must contain at least one valid day.")
        tmax = [self._weather[day]["tmax_c"] for day in days]
        total = math.fsum(self._weather[day]["et0_mm_day"] for day in days)
        hot = sum(x >= self._threshold_c for x in tmax)
        return {
            "days": len(days),
            "et0_total_mm": total,
            "mean_et0_mm_day": total / len(days),
            "tmax_min_c": min(tmax),
            "tmax_mean_c": math.fsum(tmax) / len(days),
            "tmax_max_c": max(tmax),
            "hot_days": hot,
            "hot_day_fraction": hot / len(days),
        }

    def _heat_definition(self) -> Json:
        return {
            "threshold_c": self._threshold_c,
            "operator": ">=",
            "statistic": "pooled daily Tmax p90, linear interpolation",
            "fit_start": "2001-01-01",
            "fit_end": "2018-12-31",
            "kind": "historical_exposure",
            "note": "Empirical historical benchmark; not a physiological crop damage threshold",
        }

    def get_daily_weather(self, start: str, end: str) -> Json:
        """Inclusive LST ISO date range. Return available weather rows, coverage and daily flags."""
        result, days = self._range(start, end)
        result["units"] = UNITS.copy()
        result["rows"] = [
            {
                **self._weather[d],
                "flags": list(self._quality[d]["flags"]),
                "statistical_columns": list(self._quality[d]["statistical_columns"]),
                "disposition": self._quality[d]["disposition"],
            }
            for d in days
        ]
        return result

    def calculate_et0_summary(self, start: str, end: str) -> Json:
        """Inclusive interval. Complete days yield ET0 and Tmax statistics. Otherwise metrics are null."""
        result, days = self._range(start, end)
        result["metrics"] = None
        if result["status"] == "complete":
            metrics = self._metrics(days)
            result["metrics"] = {k: v for k, v in metrics.items() if k not in ("hot_days", "hot_day_fraction")}
        return result

    def calculate_heat_exposure(self, start: str, end: str) -> Json:
        """Count inclusive Tmax threshold exceedances; exposure only, fixed training-period p90."""
        result, days = self._range(start, end)
        result.update(definition=self._heat_definition(), hot_days=None, hot_day_fraction=None)
        if result["status"] == "complete":
            metrics = self._metrics(days)
            result.update(hot_days=metrics["hot_days"], hot_day_fraction=metrics["hot_day_fraction"])
        return result

    def get_climatology(self, target_date: str, reference: str = "historical_2001_2025") -> Json:
        """Return seasonal reference for a calendar day. Select historical_2001_2025 or ml_fit_2001_2018."""
        day = iso_day(target_date)
        if reference == "ml_fit_2001_2018":
            model = self._fit_reference
            end_year = 2018
        elif reference == "historical_2001_2025":
            end_year = 2025
            if self._app_reference is None:
                reference_days = self._slice(date(2001, 1, 1), date(end_year, 12, 31))
                self._app_reference = SeasonalClimatology.from_records(
                    (self._weather[d] for d in reference_days), "2001-01-01", "2025-12-31"
                )
            model = self._app_reference
        else:
            raise ClimateInputError("Unknown climatology reference.")
        bounds = self._slice(date(2001, 1, 1), date(end_year, 12, 31))
        leap_phase = date(2000, day.month, day.day).timetuple().tm_yday
        sample = []
        for d in bounds:
            distance = abs(date(2000, d.month, d.day).timetuple().tm_yday - leap_phase)
            if min(distance, 366 - distance) <= 15:
                sample.append(d)
        return {
            "status": "complete",
            "reference_id": reference,
            "quantiles": model.for_date(day),
            "units": {"tmax_c": "degC", "et0_mm_day": "mm/day"},
            "coverage": {"expected_days": len(sample), "valid_days": len(sample), "fraction": 1.0},
            "quality": self._quality_summary(sample),
            "provenance": self._meta(sample),
        }

    def get_data_provenance(self) -> Json:
        """Return the site, calculation method, date convention and original NASA source receipts."""
        import copy
        return {
            "status": "complete",
            "provenance": self._meta(self._days),
            "source_receipts": copy.deepcopy(self._sources),
            "coverage": {
                "first": str(self._days[0]),
                "last": str(self._days[-1]),
                "valid_days": len(self._days),
            },
            "quality": self._quality_summary(self._days),
            "heat_definition": self._heat_definition(),
            "scope": "Daily POWER regional gridded weather and calculated short-grass reference ET0.",
        }
