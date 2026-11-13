"""Reproduce limited readiness checks; this is not the application ET0 pipeline."""
import datetime as dt
import json
import math
from pathlib import Path

folder = Path(__file__).resolve().parent
data = json.loads((folder / "power_sakha_sample.json").read_text(encoding="utf-8"))
series = data["properties"]["parameter"]
expected_units = {
    "T2M_MAX": "C", "T2M_MIN": "C", "RH2M": "%", "WS2M": "m/s",
    "ALLSKY_SFC_SW_DWN": "MJ/m^2/day", "PS": "kPa", "PRECTOTCORR": "mm/day",
}
start = dt.datetime.strptime(data["header"]["start"], "%Y%m%d").date()
end = dt.datetime.strptime(data["header"]["end"], "%Y%m%d").date()
expected_dates = {(start + dt.timedelta(days=i)).strftime("%Y%m%d")
                  for i in range((end - start).days + 1)}
assert set(series) == set(expected_units), "Unexpected parameter set"
assert all(set(values) == expected_dates for values in series.values()), "Date coverage differs"
assert all(data["parameters"][key]["units"] == unit for key, unit in expected_units.items()), "Unit metadata differs"
values = [value for record in series.values() for value in record.values()]
assert all(isinstance(value, (int, float)) and math.isfinite(value) for value in values), "Non-numeric or non-finite value"
assert all(value != data["header"]["fill_value"] for value in values), "Missing-value flag"
assert all(series["T2M_MIN"][day] <= series["T2M_MAX"][day] for day in expected_dates), "Temperature order"
assert all(0 <= value <= 100 for value in series["RH2M"].values()), "Humidity range"
assert all(value >= 0 for key in ("WS2M", "ALLSKY_SFC_SW_DWN", "PRECTOTCORR") for value in series[key].values()), "Negative input"
assert all(value > 0 for value in series["PS"].values()), "Nonpositive pressure"

# FAO56 Example 18 uses published rounded intermediate values, independently
# of the POWER sample. It checks the equation, not extraction or conversions.
temperature, wind, slope, gamma, vpd, radiation, soil_heat = 16.9, 2.078, .122, .0666, .589, 13.28, 0
et0 = (.408 * slope * (radiation - soil_heat)
       + gamma * (900 / (temperature + 273)) * wind * vpd) / (slope + gamma * (1 + .34 * wind))
assert abs(et0 - 3.88) < .02, "FAO56 Example 18 differs beyond rounding tolerance"
report = {
    "sample_checks": "passed",
    "parameter_count": len(series),
    "consecutive_days": len(expected_dates),
    "numeric_values": len(values),
    "units": expected_units,
    "fao56_reference_check": {
        "source": "https://www.fao.org/4/X0490E/x0490e08.htm",
        "computed_mm_per_day": et0,
        "published_mm_per_day": 3.88,
        "absolute_difference_mm_per_day": abs(et0 - 3.88),
        "tolerance_mm_per_day": .02,
        "passed": True,
    },
    "not_verified": ["POWER-to-ET0 pipeline", "crop ETc", "full historical export", "forecast skill", "farm representativeness", "speech recognition", "farmer usability"],
}
(folder / "readiness_checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
