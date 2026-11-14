"""Offline release builder for the two fixed daily Sakha POWER snapshots."""
import argparse
import csv
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass, fields
from datetime import date, timedelta
from pathlib import Path
from statistics import quantiles
from urllib.parse import parse_qs, urlsplit

from .et0 import METHOD_VERSION, calculate_daily_et0

DATASET_VERSION = "sakha-power-lst-20261110-et0-v1"
SITE_ID = "sakha_31.10_30.95"
COORDINATES = [30.95, 31.10, 4.96]  # POWER returns longitude, latitude, elevation.
ET0_TOLERANCE = 1e-10  # mm/day; accommodates platform-dependent binary64 libm differences.
VARIABLES = {
    "T2M_MAX": ("tmax_c", "C"), "T2M_MIN": ("tmin_c", "C"), "T2MDEW": ("tdew_c", "C"),
    "RH2M": ("rh_percent", "%"), "WS2M": ("wind2_m_s", "m/s"),
    "ALLSKY_SFC_SW_DWN": ("solar_mj_m2_day", "MJ/m^2/day"), "PS": ("pressure_kpa", "kPa"),
    "PRECTOTCORR": ("rain_mm_day", "mm/day"),
}
WEATHER_COLUMNS = [column for column, unit in VARIABLES.values()]
ET0_COLUMNS = ["et0_mm_day", "et0_rhmean_approx_mm_day", "et0_without_cloud_floor_mm_day"]
TARGET_COLUMNS = ["date", "tmax_c", "et0_mm_day"]
FLAG_COLUMNS = ["rs_above_rso", "raw_ratio_below_0_3", "negative_unbounded_cloud_factor",
                "negative_vpd", "negative_et0", "dew_above_tmin"]
ORIGINAL_SCRIPT_SHA = "905a700d542c5a3e2dc7dd136e21acd7a84469d1ff940efa0836bbb63e7ee0e0"


@dataclass(frozen=True)
class Snapshot:
    name: str
    start: date
    end: date
    raw: str
    raw_sha: str
    receipt: str
    receipt_sha: str
    reference: str
    reference_sha: str


SNAPSHOTS = (
    Snapshot("historical", date(2001, 1, 1), date(2025, 12, 31),
             "power_sakha_2001_2025_LST.json", "212bf82f9b2baf09eed440a5a5a6d889891964da2448a7c06a57deb3954f20bf",
             "power_provenance.json", "d90f33792704b02da5c5bd4a5d36dd884ded503132fdd2d18d39df25727cd469",
             "weather_et0.csv", "17141df82f6300c051257c21fb9ac3d9f5f1627fd32cbc8c07bc9296c477bde8"),
    Snapshot("recent", date(2026, 1, 1), date(2026, 10, 31),
             "power_sakha_2026_Jan_Oct_LST.json", "6a957d31aff96ab9b6de604f1ed5bd0def3ee364e742458d5f0e4e9aa37b8700",
             "power_provenance_2026_Jan_Oct.json", "01e22774c32c1ccca2820dc2eac9294f288433cdc0d65a4be920b729d24ec1d8",
             "weather_et0_2026_Jan_Oct.csv", "c4d5929fd0d4d55c416ee45d5ebd21502142994afbc76b00c6f20e1b349ee36e"),
)


class DataError(ValueError):
    """The snapshot, reference or source receipt failed a release gate."""


def require(condition, message):
    if not condition:
        raise DataError(message)


def strict_json(payload: bytes) -> dict:
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key {key!r}")
            result[key] = value
        return result

    def invalid_number(token):
        raise DataError(f"Invalid JSON constant {token}")

    result = json.loads(payload, object_pairs_hook=unique_object, parse_constant=invalid_number)
    require(isinstance(result, dict), "JSON document must be an object")
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_file(path, digest):
    require(sha256(path) == digest, f"SHA256 differs from fixed release: {path.name}")


def dates_in(spec):
    return [spec.start + timedelta(days=i) for i in range((spec.end - spec.start).days + 1)]


def validate_schema(raw, receipt, spec):
    """Validate actual response and query, before consuming observations."""
    try:
        header = raw["header"]
        units = raw["parameters"]
        series = raw["properties"]["parameter"]
        coords = raw["geometry"]["coordinates"]
        query = receipt["parameters"]
        start, end = spec.start.strftime("%Y%m%d"), spec.end.strftime("%Y%m%d")
        expected_query = {"community": "AG", "time-standard": "LST", "format": "JSON",
                          "parameters": ",".join(VARIABLES), "latitude": "31.10", "longitude": "30.95",
                          "start": start, "end": end}
        url = urlsplit(receipt["url"])
        url_query = parse_qs(url.query, strict_parsing=True)
        require(url.scheme == "https" and url.netloc == "power.larc.nasa.gov" and
                url.path == "/api/temporal/daily/point", "Unexpected source endpoint")
        require(query == expected_query and url_query == {k: [v] for k,v in expected_query.items()},
                "Receipt request does not match fixed release")
        require(receipt["response_header"] == header and receipt["response_units"] == units,
                "Receipt does not describe response")
        require(raw["type"] == "Feature" and raw["geometry"]["type"] == "Point" and
                coords == COORDINATES, "Unexpected site, geometry or grid elevation")
        require(header["api"]["version"] == "v2.10.3" and header["time_standard"] == "LST"
                and header["start"] == start and header["end"] == end
                and header["fill_value"] == -999, "Unexpected response header")
        require(set(units) == set(series) == set(VARIABLES), "Unexpected daily weather schema")
        dates = {day.strftime("%Y%m%d") for day in dates_in(spec)}
        for key, (_, unit) in VARIABLES.items():
            require(units[key]["units"] == unit, f"Wrong units for {key}")
            require(isinstance(series[key], dict) and set(series[key]) == dates,
                    f"Missing or extra date for {key}")
    except (KeyError, TypeError, AttributeError) as exc:
        raise DataError(f"Missing or malformed response/receipt field: {exc}") from exc


def weather_day(series, date_key, fill):
    weather = {}
    for key, (column, _) in VARIABLES.items():
        value = series[key][date_key]
        require(type(value) in (int, float) and math.isfinite(value) and value != fill,
                f"Missing or invalid {key} on {date_key}")
        weather[column] = value
    require(weather["tmin_c"] <= weather["tmax_c"] and
            min(weather["tmin_c"], weather["tdew_c"]) > -273.15 and
            0 <= weather["rh_percent"] <= 100 and weather["pressure_kpa"] > 0 and
            min(weather["solar_mj_m2_day"], weather["wind2_m_s"], weather["rain_mm_day"]) >= 0,
            f"Impossible weather on {date_key}")
    return weather


def partition(day):
    if day.year <= 2018:
        return "fit"
    if day.year <= 2021:
        return "diagnostic_validation"
    if day.year <= 2025:
        return "reserve_not_blind"
    return "2026_quarantine"


def read_snapshot(sources, spec):
    raw_path, receipt_path, reference_path = [sources / name for name in (spec.raw, spec.receipt, spec.reference)]
    for path, expected in ((raw_path,spec.raw_sha),(receipt_path,spec.receipt_sha),(reference_path,spec.reference_sha)):
        verify_file(path, expected)
    raw = strict_json(raw_path.read_bytes())
    receipt = strict_json(receipt_path.read_bytes())
    validate_schema(raw, receipt, spec)
    require(receipt["bytes"] == raw_path.stat().st_size and receipt["sha256"] == spec.raw_sha
            and receipt["http_status"] == 200, "Source receipt integrity failure")
    rows, flags = [], []
    maximum_errors = dict.fromkeys(ET0_COLUMNS, 0.0)
    with reference_path.open(encoding="utf-8", newline="") as handle:
        reference = csv.DictReader(handle)
        require(reference.fieldnames == ["date", *WEATHER_COLUMNS, *ET0_COLUMNS], "Audited reference schema differs")
        for day in dates_in(spec):
            observed = next(reference, None)
            require(observed is not None and observed["date"] == day.isoformat(), "Reference date misaligned")
            weather = weather_day(raw["properties"]["parameter"], day.strftime("%Y%m%d"), raw["header"]["fill_value"])
            require(all(float(observed[k]) == v for k,v in weather.items()), f"Raw/CSV mismatch on {day}")
            et0_inputs = {k:v for k,v in weather.items() if k != "rain_mm_day"}
            flux = calculate_daily_et0(day=day, latitude=COORDINATES[1], elevation_m=COORDINATES[2], **et0_inputs)
            for key in ET0_COLUMNS:
                error = abs(getattr(flux, key) - float(observed[key]))
                require(error <= ET0_TOLERANCE, f"ET0 regression failed for {day}, {key}: {error}")
                maximum_errors[key] = max(maximum_errors[key], error)
            # The reference strings preserve the exact published release even across libm variants.
            rows.append(dict(site_id=SITE_ID, snapshot=spec.name, partition=partition(day), **observed))
            flags.append(dict(date=day.isoformat(), snapshot=spec.name, hard_invalid=0,
                              rs_above_rso=int(flux.rs_over_rso > 1), raw_ratio_below_0_3=int(flux.rs_over_rso < .3),
                              negative_unbounded_cloud_factor=int(flux.rs_over_rso < .35 / 1.35),
                              negative_vpd=int(flux.vpd_kpa < 0), negative_et0=int(flux.et0_mm_day < 0),
                              dew_above_tmin=int(weather["tdew_c"] > weather["tmin_c"]),
                              rs_over_rso=flux.rs_over_rso, vpd_kpa=flux.vpd_kpa,
                              mixed_sources_in_response=int(spec.name == "recent")))
        require(next(reference, None) is None, "Unexpected extra CSV row")
    provenance = dict(snapshot=spec.name, raw=spec.raw, raw_sha256=spec.raw_sha, raw_bytes=receipt["bytes"],
                      derived=spec.reference, derived_sha256=spec.reference_sha, derived_bytes=reference_path.stat().st_size,
                      receipt=spec.receipt, receipt_sha256=spec.receipt_sha, retrieval_utc=receipt["retrieved_utc"],
                      url=receipt["url"], header=raw["header"], coordinates=raw["geometry"]["coordinates"],
                      definitions=raw["parameters"], request=receipt["parameters"])
    return rows, flags, provenance, maximum_errors


def screen_outliers(rows, flags):
    """Monthly training-only outer fences, linear-interpolated inclusive quartiles."""
    columns = [*WEATHER_COLUMNS, ET0_COLUMNS[0]]
    groups = {month: [i for i,row in enumerate(rows) if int(row["date"][5:7]) == month] for month in range(1,13)}
    unusual = [[] for row in rows]
    bounds = []
    for month, indices in groups.items():
        training = [rows[i] for i in indices if rows[i]["partition"] == "fit"]
        for column in columns:
            values = [float(row[column]) for row in training]
            q1, _, q3 = quantiles(values, n=4, method="inclusive")
            iqr = q3-q1
            lower, upper = q1-3*iqr, q3+3*iqr
            bounds.append(dict(month=month, column=column, q1=q1, q3=q3, lower=lower, upper=upper, active=int(iqr>0)))
            if iqr:
                for i in indices:
                    if not lower <= float(rows[i][column]) <= upper:
                        unusual[i].append(column)
    for flag, names in zip(flags, unusual):
        flag["seasonal_3iqr_columns"] = "|".join(names)
        flag["qc_disposition"] = "retain_review" if names or any(flag[key] for key in FLAG_COLUMNS) else "retain"
    return bounds


def run_archived_fixtures(sources, scratch):
    """Execute the hash-pinned pre-existing reference suite on disposable local inputs."""
    runner = sources / "original" / "audit_weather.py"
    verify_file(runner, ORIGINAL_SCRIPT_SHA)
    target = scratch / runner.name
    shutil.copyfile(runner, target)
    output = {}
    for spec in SNAPSHOTS:
        shutil.copyfile(sources / spec.raw, scratch / spec.raw)
        subprocess.run([sys.executable, "-I", "-B", str(target), "--source", spec.raw],
                       check=True, capture_output=True, text=True, timeout=90)
        result = strict_json((scratch / "weather_audit.json").read_bytes())
        checks = result["reference_checks"]
        require(len(checks) == 12 and all(check["passed"] is True for check in checks), "Original reference checks failed")
        output[spec.name] = checks
    return output


def write_table(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8", newline="\n")


def build_release(sources: Path, output: Path) -> dict:
    """Build a complete immutable release into a new directory. Publish only after checks."""
    sources, output = Path(sources).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Choose a new output path: {output}")
    if output.is_relative_to(sources):
        raise DataError("Output directory must be outside immutable sources")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        workspace = Path(temporary)
        staging = workspace / "release"
        rows, flags, manifests = [], [], []
        regression = {}
        for spec in SNAPSHOTS:
            records, quality, metadata, errors = read_snapshot(sources, spec)
            rows.extend(records)
            flags.extend(quality)
            manifests.append(metadata)
            regression[spec.name] = errors
        dates = [date.fromisoformat(row["date"]) for row in rows]
        require(len(dates) == 9435 and all((b-a).days == 1 for a,b in zip(dates, dates[1:])),
                "Combined calendar has gaps, repeats or wrong length")
        bounds = screen_outliers(rows, flags)
        write_table(staging / "data/sakha_daily.csv", rows)
        write_table(staging / "data/quality_flags.csv", flags)
        write_table(staging / "reports/seasonal_screen_bounds.csv", bounds)
        for subset in ("fit", "diagnostic_validation"):
            targets = [{k: row[k] for k in TARGET_COLUMNS} for row in rows if row["partition"] == subset]
            write_table(staging / "data" / (subset + "_targets.csv"), targets)
        write_json(staging / "provenance/source_manifest.json", manifests)
        scratch = workspace / "fixtures"
        scratch.mkdir()
        checks = run_archived_fixtures(sources, scratch)
        report = dict(dataset_version=DATASET_VERSION, method_version=METHOD_VERSION,
                      site_id=SITE_ID, days=len(dates), first_date=str(dates[0]), last_date=str(dates[-1]),
                      leap_days=[str(d) for d in dates if (d.month,d.day) == (2,29)],
                      partition_counts=dict(Counter(row["partition"] for row in rows)),
                      raw_weather_values_verified=len(rows)*len(VARIABLES), hard_invalid_days=0,
                      review_days=sum(row["qc_disposition"] == "retain_review" for row in flags),
                      seasonal_outlier_days=sum(bool(row["seasonal_3iqr_columns"]) for row in flags),
                      flag_counts={key: sum(row[key] for row in flags) for key in FLAG_COLUMNS},
                      reference_et0_tolerance_mm_day=ET0_TOLERANCE, max_abs_et0_difference_mm_day=regression,
                      original_fixture_script_sha256=ORIGINAL_SCRIPT_SHA, original_scientific_fixtures=checks,
                      exported_sha256={p.name:sha256(p) for p in sorted((staging/"data").glob("*.csv"))})
        write_json(staging / "reports/pipeline.json", report)
        staging.rename(output)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_release(args.sources, args.output)
    print(f"Built {report['days']} daily records in {args.output}; evidence: reports/pipeline.json")


if __name__ == "__main__":
    main()
