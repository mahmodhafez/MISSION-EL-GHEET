"""Calendar-conditioned quantiles for Sakha daily Tmax and reference ET0."""

from __future__ import annotations

import csv
import math
import struct
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

TARGETS = ("tmax_c", "et0_mm_day")
QUANTILES = (("q10", 0.10), ("q50", 0.50), ("q90", 0.90))
TRAIN_START = date(2001, 1, 1)
TRAIN_END = date(2018, 12, 31)
VALID_START = date(2019, 1, 1)
VALID_END = date(2021, 12, 31)
HISTORICAL_START = date(2001, 1, 1)
HISTORICAL_END = date(2025, 12, 31)
RESEARCH_METHOD = "seasonal_climatology/train_2001_2018/linear_quantiles_pm15_f32/v1"
DESCRIPTIVE_METHOD = "seasonal_climatology/descriptive/linear_quantiles_pm15_f64/v1"
ONE_DAY = timedelta(days=1)


def iso_date(value: date | str) -> date:
    """Accept a civil ISO date YYYY-MM-DD or a date object for an LST day."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise ValueError("Expected a date or YYYY-MM-DD string")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO date: {value!r}") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"Use YYYY-MM-DD: {value!r}")
    return parsed


def float32(value: float) -> float:
    """Reproduce the archived float32 model input while keeping exports unchanged."""
    return struct.unpack("!f", struct.pack("!f", value))[0]


def phase(day: date) -> int:
    """Zero-based leap-calendar slot: Feb 29 = 59; Mar 1 = 60 in every year."""
    return (date(2000, day.month, day.day) - date(2000, 1, 1)).days


def calendar_window(day: date | str) -> tuple[int, ...]:
    """The 31 phase indices at most 15 calendar slots from the target."""
    center = phase(iso_date(day))
    return tuple((center + offset) % 366 for offset in range(-15, 16))


def linear_quantile(sorted_values: Sequence[float], probability: float) -> float:
    """Type-7 empirical quantile, matching numpy.quantile linear interpolation."""
    if not sorted_values or not 0 <= probability <= 1:
        raise ValueError("Quantile requires nonempty sorted values and 0 <= p <= 1")
    rank = (len(sorted_values) - 1) * probability
    left = math.floor(rank)
    weight = rank - left
    if weight == 0:
        return sorted_values[left]
    return sorted_values[left] + weight * (sorted_values[left + 1] - sorted_values[left])


@dataclass(frozen=True)
class DailyTarget:
    day: date
    tmax_c: float
    et0_mm_day: float


def parse_series(records: Iterable[Mapping[str, object]], start: date, end: date) -> list[DailyTarget]:
    """Validate an ordered contiguous daily series with exact inclusive bounds."""
    if start > end:
        raise ValueError("Reference start follows its end")
    result = []
    for index, row in enumerate(records):
        try:
            day = iso_date(row["date"])
            values = []
            for key in TARGETS:
                raw = row[key]
                if isinstance(raw, bool):
                    raise ValueError(f"Boolean {key}")
                value = float(raw)
                if not math.isfinite(value) or value == -999.0:
                    raise ValueError(f"Nonfinite or fill {key}")
                values.append(value)
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"Invalid target row {index + 1}: {exc}") from exc
        expected = start + timedelta(days=index)
        if day != expected or day > end:
            raise ValueError(f"Expected a unique ordered day {expected} in {start}..{end}, got {day}")
        if values[0] <= -273.15 or values[1] < 0:
            raise ValueError(f"Target outside the validated Sakha release domain on {day}")
        result.append(DailyTarget(day, *values))
    if len(result) != (end - start).days + 1:
        raise ValueError(f"Incomplete target interval {start}..{end}")
    return result


def load_targets(path: Path | str, start: date, end: date) -> list[DailyTarget]:
    """Read exact date/tmax_c/et0_mm_day CSV schema and enforce split boundaries."""
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        if reader.fieldnames != ["date", *TARGETS]:
            raise ValueError(f"Unexpected target columns: {reader.fieldnames}")

        def checked_rows():
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f"Wrong CSV field count at line {reader.line_num}")
                yield row

        return parse_series(checked_rows(), start, end)


class SeasonalClimatology:
    """A reference computed once for 366 month/day slots, including leap day."""

    def __init__(self, rows: Sequence[DailyTarget], start: date, end: date, *, research: bool):
        if len(rows) != (end - start).days + 1 or start > end:
            raise ValueError("The reference needs a complete daily interval")
        if research and (start, end) != (TRAIN_START, TRAIN_END):
            raise ValueError("The research reference must use exactly 2001–2018")
        self.reference_start = start.isoformat()
        self.reference_end = end.isoformat()
        self.method = RESEARCH_METHOD if research else DESCRIPTIVE_METHOD
        buckets = [[] for _ in range(366)]
        for index, row in enumerate(rows):
            if row.day != start + timedelta(days=index):
                raise ValueError("Reference days missing, duplicated, unordered or outside interval")
            values = (row.tmax_c, row.et0_mm_day)
            if not all(math.isfinite(value) and value != -999 for value in values):
                raise ValueError("Reference contains a nonfinite or fill target")
            buckets[phase(row.day)].append(tuple(map(float32, values)) if research else values)
        self._reference = []
        for slot in range(366):
            support = [entry for delta in range(-15, 16)
                       for entry in buckets[(slot + delta) % 366]]
            if not support:
                raise ValueError(f"Reference interval supplies no observations around calendar slot {slot}")
            ordered = [sorted(channel) for channel in zip(*support)]
            quantiles = tuple(tuple(linear_quantile(channel, p) for _, p in QUANTILES)
                              for channel in ordered)
            self._reference.append((len(support), quantiles))

    @classmethod
    def from_csv(cls, path: Path | str) -> SeasonalClimatology:
        """Build only the archived research baseline; rejects all extra or missing days."""
        return cls(load_targets(path, TRAIN_START, TRAIN_END), TRAIN_START, TRAIN_END, research=True)

    @classmethod
    def from_records(cls, records: Iterable[Mapping[str, object]], start: date | str,
                     end: date | str) -> SeasonalClimatology:
        """Build a separately labeled descriptive reference from a caller-selected interval."""
        first, last = iso_date(start), iso_date(end)
        return cls(parse_series(records, first, last), first, last, research=False)

    def for_date(self, day: date | str) -> dict:
        """Return historical q10/q50/q90 for the supplied target month/day and both channels."""
        target_date = iso_date(day)
        count, channels = self._reference[phase(target_date)]
        result = {"target_date": target_date.isoformat(), "reference_start": self.reference_start,
                  "reference_end": self.reference_end, "method": self.method, "support_days": count}
        for name, values in zip(TARGETS, channels):
            result[name] = {key: value for (key, _), value in zip(QUANTILES, values)}
        return result
