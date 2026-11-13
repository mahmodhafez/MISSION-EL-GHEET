"""Read-only, standard-library audit of the local scientific evidence ZIP.

Recalculates saved-data results, never imports archived code, trains a model,
retrieves new weather, or determines agricultural feasibility.
"""
import argparse
import ast
import calendar
import csv
from dataclasses import dataclass
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import struct
import sys
import urllib.parse
import zipfile

PREFIX = "work/validation_2026-11-10/"
FIELDS = {
    "T2M_MAX": ("tmax_c", "C"), "T2M_MIN": ("tmin_c", "C"),
    "T2MDEW": ("tdew_c", "C"), "RH2M": ("rh_percent", "%"),
    "WS2M": ("wind2_m_s", "m/s"),
    "ALLSKY_SFC_SW_DWN": ("solar_mj_m2_day", "MJ/m^2/day"),
    "PS": ("pressure_kpa", "kPa"), "PRECTOTCORR": ("rain_mm_day", "mm/day"),
}
TARGETS = ("tmax_c", "et0_mm_day")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected, label, tolerance=3e-6):
    require(math.isfinite(actual) and abs(actual - expected) <= tolerance,
            f"{label}: {actual} != {expected}")


def float32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def et0(row, date, latitude, elevation):
    """Independent expression of SCIENCE section 3, using binary64 arithmetic."""
    tx, tn, td = (row[k] for k in ("tmax_c", "tmin_c", "tdew_c"))
    wind, solar, pressure = (row[k] for k in ("wind2_m_s", "solar_mj_m2_day", "pressure_kpa"))
    require(all(math.isfinite(x) for x in (*row.values(), latitude, elevation)), "nonfinite weather")
    require(tn <= tx and wind >= 0 and solar >= 0 and pressure > 0, "invalid weather")
    require(-90 < latitude < 90, "unsupported latitude")
    saturation = lambda t: 0.6108 * math.exp(17.27 * t / (237.3 + t))
    mean = (tx + tn) / 2
    ea = saturation(td)
    es = (saturation(tx) + saturation(tn)) / 2
    slope = 4098 * saturation(mean) / (mean + 237.3) ** 2
    gamma = pressure * 0.000665
    angle = 2 * math.pi * date.timetuple().tm_yday / 365
    declination = 0.409 * math.sin(angle - 1.39)
    phi = math.radians(latitude)
    sunset = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(declination))))
    ra = 1440 / math.pi * 0.0820 * (1 + 0.033 * math.cos(angle)) * (
        sunset * math.sin(phi) * math.sin(declination)
        + math.cos(phi) * math.cos(declination) * math.sin(sunset))
    clear_sky = (0.75 + 0.00002 * elevation) * ra
    require(clear_sky > 0, "unsupported clear-sky radiation")
    ratio = solar / clear_sky
    cloud = 1.35 * max(0.3, min(1, ratio)) - 0.35
    longwave = 4.903e-9 * ((tx + 273.16) ** 4 + (tn + 273.16) ** 4) / 2
    longwave *= (0.34 - 0.14 * math.sqrt(ea)) * cloud
    net = 0.77 * solar - longwave
    demand = (0.408 * slope * net + gamma * 900 / (mean + 273) * wind * (es - ea))
    demand /= slope + gamma * (1 + 0.34 * wind)
    return demand, ratio


@dataclass
class Array:
    shape: tuple
    values: tuple

    def at(self, *indices):
        require(len(indices) == len(self.shape), "array rank mismatch")
        offset = 0
        for index, size in zip(indices, self.shape):
            require(0 <= index < size, "array index out of bounds")
            offset = offset * size + index
        return self.values[offset]


def read_npy(raw):
    """Only numeric C-order float arrays; never pickle/object deserialization."""
    require(raw[:6] == b"\x93NUMPY" and raw[6:8] in (b"\x01\x00", b"\x02\x00"), "unsupported NPY")
    start = 10 if raw[6] == 1 else 12
    length = int.from_bytes(raw[8:start], "little")
    header = ast.literal_eval(raw[start:start + length].decode("latin1"))
    require(header["fortran_order"] is False, "unsupported Fortran array")
    dtype = header["descr"]
    require(dtype in ("<f4", "<f8"), "unsupported NPY dtype")
    shape = header["shape"]
    require(isinstance(shape, tuple) and all(isinstance(n, int) and n > 0 for n in shape), "invalid NPY shape")
    count = math.prod(shape)
    payload = raw[start + length:]
    require(len(payload) == count * int(dtype[-1]), "NPY payload length")
    values = struct.unpack("<" + str(count) + ("f" if dtype == "<f4" else "d"), payload)
    require(all(math.isfinite(v) for v in values), "nonfinite predictions")
    return Array(shape, values)


def quantile(values, q):
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lo, hi = math.floor(index), math.ceil(index)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (index - lo)


def audit(archive):
    with zipfile.ZipFile(archive) as bundle:
        manifest = json.loads(bundle.read("ARTIFACT_MANIFEST.json"))
        entries = {r["path"]: r for r in manifest["entries"]}
        checked = set()

        def read(name):
            path = PREFIX + name
            raw = bundle.read(path)
            require(path in entries, f"manifest missing {path}")
            item = entries[path]
            require(len(raw) == item["bytes"] and hashlib.sha256(raw).hexdigest() == item["sha256"],
                    f"package integrity mismatch: {path}")
            checked.add(path)
            return raw

        def document(name):
            return json.loads(read(name))

        rows = {}
        csv_hashes = {}
        releases = []
        max_et0_difference = 0.0
        floor_days = 0
        for raw_name, csv_name, provenance_name, expected_days in (
            ("power_sakha_2001_2025_LST.json", "weather_et0.csv", "power_provenance.json", 9131),
            ("power_sakha_2026_Jan_Oct_LST.json", "weather_et0_2026_Jan_Oct.csv", "power_provenance_2026_Jan_Oct.json", 304),
        ):
            raw = read(raw_name)
            source = json.loads(raw)
            provenance = document(provenance_name)
            header = source["header"]
            series = source["properties"]["parameter"]
            require(set(series) == set(FIELDS), "POWER variable mismatch")
            require(all(source["parameters"][k]["units"] == unit for k, (_, unit) in FIELDS.items()), "POWER units mismatch")
            request = urllib.parse.urlsplit(provenance["url"])
            expected_request = {
                "parameters": ",".join(FIELDS), "community": "AG", "longitude": "30.95", "latitude": "31.10",
                "start": header["start"], "end": header["end"], "format": "JSON", "time-standard": "LST",
            }
            require(request.scheme == "https" and request.netloc == "power.larc.nasa.gov"
                    and request.path == "/api/temporal/daily/point"
                    and urllib.parse.parse_qs(request.query) == {k: [v] for k, v in expected_request.items()}
                    and provenance["parameters"] == expected_request,
                    "POWER acquisition request mismatch")
            require(provenance["http_status"] == 200 and provenance["bytes"] == len(raw), "POWER HTTP metadata")
            require(hashlib.sha256(raw).hexdigest() == provenance["sha256"], "POWER response checksum mismatch")
            require(header == provenance["response_header"] and source["parameters"] == provenance["response_units"], "POWER provenance mismatch")
            require(header["time_standard"] == "LST", "POWER time standard")
            require(source["geometry"]["coordinates"] == [30.95, 31.1, 4.96], "POWER research geometry")
            first, last = (dt.datetime.strptime(header[k], "%Y%m%d").date() for k in ("start", "end"))
            dates = [first + dt.timedelta(days=i) for i in range((last-first).days + 1)]
            require(len(dates) == expected_days, "POWER coverage")
            keys = {d.strftime("%Y%m%d") for d in dates}
            require(all(set(s) == keys for s in series.values()), "POWER date alignment")
            raw_csv = read(csv_name)
            csv_hashes[csv_name] = hashlib.sha256(raw_csv).hexdigest()
            saved_rows = list(csv.DictReader(io.StringIO(raw_csv.decode("utf-8"))))
            require([r["date"] for r in saved_rows] == [d.isoformat() for d in dates], "CSV date coverage/order")
            for date, saved in zip(dates, saved_rows):
                key = date.strftime("%Y%m%d")
                row = {field: series[var][key] for var, (field, _) in FIELDS.items()}
                require(all(isinstance(v, (int, float)) and math.isfinite(v) and v != header["fill_value"]
                            for v in row.values()), "POWER missing/nonfinite values")
                require(0 <= row["rh_percent"] <= 100 and row["rain_mm_day"] >= 0, "POWER RH/rain range")
                require(all(float(saved[field]) == value for field, value in row.items()), "CSV weather differs from POWER")
                value, ratio = et0(row, date, 31.1, 4.96)
                difference = abs(value - float(saved["et0_mm_day"]))
                close(value, float(saved["et0_mm_day"]), "ET0 all-row reproduction", 1e-10)
                max_et0_difference = max(max_et0_difference, difference)
                floor_days += ratio < 0.3
                require(date not in rows, "duplicate weather date")
                rows[date] = {**row, "et0_mm_day": float(saved["et0_mm_day"])}
            releases.append(provenance)

        # Check the saved transcription, without executing the archived script.
        syntax = ast.parse(read("check_station_table.py"))
        reference = next(ast.literal_eval(n.value) for n in syntax.body
                         if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "reference" for t in n.targets))
        station_report = document("station_table_diagnostic.json")
        station_differences = []
        for month, values in reference.items():
            year, number = map(int, month.split("-"))
            sample = [r for d, r in rows.items() if d.year == year and d.month == number]
            require(len(sample) == calendar.monthrange(year, number)[1], "station month coverage")
            # km/day wind run at the reported 2 m; no 10 m conversion.
            converted = (*values[:3], values[3] / 86.4)
            differences = {k: statistics.mean(r[k] for r in sample) - v
                           for k, v in zip(("tmax_c", "tmin_c", "rh_percent", "wind2_m_s"), converted)}
            expected = next(c for c in station_report["comparisons"] if c["month"] == month)
            require(expected["days"] == len(sample), "station day count")
            for key, difference in differences.items():
                close(difference, expected["differences_power_minus_published"][key], "station diagnostic", 1e-10)
            station_differences.append(differences)
        require(len(reference) == station_report["months"] == 11, "station month count")
        station_means = {k: statistics.mean(d[k] for d in station_differences) for k in station_differences[0]}
        for key, value in station_means.items():
            close(value, station_report["mean_monthly_bias"][key], "station summary", 1e-10)

        report = document("model_test/holdout_results.json")
        require(report["input_hashes"] == csv_hashes, "ML dataset-vintage mismatch")
        runs = {name: document(f"model_test/{name}/results.json") for name in ("smoke20_verified", "adaptation200")}
        selection = {name: run["fine_tuned"]["scores"]["et0_mm_day"]["mae"] for name, run in runs.items()}
        require(report["selection_validation_et0_mae"] == selection, "adapter selection scores")
        require(report["selected_adapter"] == min(selection, key=selection.get), "adapter selection mismatch")
        for name, run in runs.items():
            require(run["input_sha256"] == csv_hashes["weather_et0.csv"], f"training dataset-vintage mismatch: {name}")
            require(run["status"] == "completed" and run["reload"]["within_0_001"], "recorded execution/reload failed")
            require(run["lora"]["adapter_tensors"] == run["lora"]["changed_adapter_tensors"] > 0, "no recorded adapter updates")
        protocol = document("model_test/evaluation_protocol.json")
        checkpoint = document("model_test/checkpoint_provenance.json")
        # These sources are inspected as text/AST only. They are not imported.
        for name in ("run_model_test.py", "evaluate_holdout.py"):
            tree = ast.parse(read("model_test/" + name))
            predictions = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                           and isinstance(n.func, ast.Attribute) and n.func.attr == "predict_quantiles"]
            require(len(predictions) == 1, "forecast-method provenance: prediction call")
            kwargs = {k.arg: ast.literal_eval(k.value) for k in predictions[0].keywords}
            require(all(kwargs.get(k) == v for k, v in {
                "prediction_length": 14, "context_length": 60, "batch_size": 4,
                "cross_learning": False, "quantile_levels": [0.1, 0.5, 0.9],
            }.items()), "forecast-method provenance: horizon/context/cross-learning/quantiles")
            if name == "run_model_test.py":
                fits = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Attribute) and n.func.attr == "fit"]
                require(len(fits) == 1 and any(k.arg == "finetune_mode" and ast.literal_eval(k.value) == "lora"
                                             for k in fits[0].keywords), "forecast-method provenance: LoRA")
        require(protocol["checkpoint_revision"] == checkpoint["revision"], "checkpoint revision mismatch")
        issues = [dt.date.fromisoformat(s) for s in report["issue_dates"]]
        require(len(issues) == len(set(issues)) == 17 and all((b-a).days == 7 for a, b in zip(issues, issues[1:])), "held-out issue spacing")
        require(issues[0] == dt.date(2026, 7, 1) and issues[-1] == dt.date(2026, 10, 21), "held-out issue range")
        require(all(d > dt.date.fromisoformat(report["checkpoint_revision_date"]) for d in issues), "pre-checkpoint assessment")
        with zipfile.ZipFile(io.BytesIO(read("model_test/holdout_predictions.npz"))) as saved:
            arrays = {Path(n).stem: read_npy(saved.read(n)) for n in saved.namelist()}
        for name in ("truth", "persistence"):
            require(arrays[name].shape == (17, 2, 7), "target/persistence shape")
        for name in ("zero_shot", "fine_tuned", "climatology"):
            require(arrays[name].shape == (17, 2, 7, 3), "quantile prediction shape")
        training = [(d, r) for d, r in rows.items() if d <= dt.date(2018, 12, 31)]
        phase = lambda d: dt.date(2000, d.month, d.day).timetuple().tm_yday
        for w, issue in enumerate(issues):
            cutoff = issue - dt.timedelta(days=7)
            for target, field in enumerate(TARGETS):
                for day in range(7):
                    date = issue + dt.timedelta(days=day + 1)
                    require(arrays["truth"].at(w, target, day) == float32(rows[date][field]), "ML target alignment")
                    require(arrays["persistence"].at(w, target, day) == float32(rows[cutoff][field]), "persistence cutoff mismatch")
                    sample = [float32(r[field]) for d, r in training
                              if min(abs(phase(d)-phase(date)), 366-abs(phase(d)-phase(date))) <= 15]
                    for q, level in enumerate((0.1, 0.5, 0.9)):
                        close(arrays["climatology"].at(w, target, day, q), quantile(sample, level), "training-only climatology")

        scores = {}
        for method, name in (("zero_shot", "zero_shot"), ("fine_tuned", "fine_tuned"),
                             ("seasonal_climatology", "climatology"), ("persistence", "persistence")):
            scores[method] = {}
            for target, field in enumerate(TARGETS):
                errors, widths, coverage, losses = [], [], [], []
                for w in range(17):
                    for day in range(7):
                        truth = arrays["truth"].at(w, target, day)
                        if name == "persistence":
                            errors.append(arrays[name].at(w, target, day) - truth)
                            continue
                        lo, median, hi = (arrays[name].at(w, target, day, q) for q in range(3))
                        require(lo <= median <= hi, "unordered quantiles")
                        errors.append(median - truth)
                        widths.append(hi - lo)
                        coverage.append(lo <= truth <= hi)
                        for value, q in zip((lo, median, hi), (0.1, 0.5, 0.9)):
                            residual = truth - value
                            losses.append(max(q * residual, (q - 1) * residual))
                metrics = {"mae": statistics.mean(abs(e) for e in errors)}
                if name != "persistence":
                    metrics.update(rmse=math.sqrt(statistics.mean(e*e for e in errors)),
                                   bias=statistics.mean(errors), interval_80_coverage=statistics.mean(coverage),
                                   mean_interval_width=statistics.mean(widths), mean_pinball_loss=statistics.mean(losses))
                    leads = [statistics.mean(abs(errors[w*7+d]) for w in range(17)) for d in range(7)]
                    for actual, expected in zip(leads, report["scores"][method][field]["mae_by_lead_1_to_7"]):
                        close(actual, expected, "MAE by lead")
                for key, value in metrics.items():
                    close(value, report["scores"][method][field][key], method + " " + field + " " + key)
                if name != "persistence":
                    metrics["covered"] = sum(coverage)
                scores[method][field] = metrics

        return {
            "status": "passed", "checker_version": "1.0", "runtime": sys.version.split()[0],
            "integrity_checked_members": len(checked),
            "weather": {"days": len(rows), "source_values": len(rows) * 8,
                        "max_et0_difference_mm_day": max_et0_difference, "cloud_floor_days": floor_days,
                        "acquisition": releases},
            "station": {"status": "transcription_arithmetic_only", "months": sorted(reference),
                        "equal_month_mean_differences": station_means,
                        "limitation": "Primary table not reverified; station QC, instrumentation and daily observation boundaries unavailable. No correction fitted."},
            "ml": {"days_per_target": 119, "selected_adapter": report["selected_adapter"],
                   "dataset_hashes_match": True, "scores": scores,
                   "method_provenance": "Archived training/evaluator source inspected; saved predictions rescored. No new inference/training or interval calibration."},
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=Path(__file__).resolve().parents[2] / "docs/VALIDATION_ARTIFACTS.zip")
    args = parser.parse_args()
    try:
        result = audit(args.archive)
    except (OSError, ValueError, KeyError, StopIteration, SyntaxError, struct.error, zipfile.BadZipFile) as error:
        print(json.dumps({"status": "failed", "error": str(error)}))
        return 1
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
