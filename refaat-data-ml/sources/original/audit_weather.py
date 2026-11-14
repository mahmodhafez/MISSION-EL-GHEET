"""Scientific readiness calculations; not a deployed farm recommendation engine."""
import csv
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import statistics as st

ROOT = Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument("--source",default="power_sakha_2001_2025_LST.json")
parser.add_argument("--suffix",default="")
args=parser.parse_args()
EXPECTED = {"T2M_MAX":"C","T2M_MIN":"C","T2MDEW":"C","RH2M":"%",
            "WS2M":"m/s","ALLSKY_SFC_SW_DWN":"MJ/m^2/day","PS":"kPa","PRECTOTCORR":"mm/day"}

def esat(t):
    return .6108 * math.exp(17.27 * t / (t + 237.3))

def radiation_geometry(latitude, day):
    if not -90 < latitude < 90 or not 1 <= day <= 366:
        raise ValueError("Latitude or day of year outside supported range")
    phi = math.radians(latitude)
    dr = 1 + .033 * math.cos(2 * math.pi * day / 365)
    decl = .409 * math.sin(2 * math.pi * day / 365 - 1.39)
    ws = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(decl))))
    ra = 24 * 60 / math.pi * .0820 * dr * (ws * math.sin(phi) * math.sin(decl)
                                         + math.cos(phi) * math.cos(decl) * math.sin(ws))
    return ra, 24 * ws / math.pi

def reference_et0(tmax, tmin, ea, wind2, rs, pressure, latitude, elevation, day, bound_cloudiness=True):
    vals = (tmax,tmin,ea,wind2,rs,pressure,latitude,elevation,day)
    if not all(math.isfinite(v) for v in vals):
        raise ValueError("Non-finite input")
    if tmin > tmax or ea < 0 or wind2 < 0 or rs < 0 or pressure <= 0:
        raise ValueError("Invalid meteorological input")
    mean_t = (tmax + tmin) / 2
    es = (esat(tmax) + esat(tmin)) / 2
    slope = 4098 * esat(mean_t) / (mean_t + 237.3) ** 2
    gamma = .000665 * pressure
    ra, daylight = radiation_geometry(latitude, day)
    rso = (.75 + .00002 * elevation) * ra
    if rso <= 0:
        raise ValueError("Polar-night radiation is outside this audit's supported conditions")
    ratio_raw = rs / rso
    # Explicit ASCE-EWRI 2005 daily radiation safeguard, Eq.18, printed p20.
    # Keep the FAO56 equation/constants; retain raw ratios and sensitivity below.
    ratio = max(.3, min(1.0, ratio_raw)) if bound_cloudiness else min(1.0, ratio_raw)
    rns = .77 * rs
    rnl = 4.903e-9 * ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2
    rnl *= (.34 - .14 * math.sqrt(ea)) * (1.35 * ratio - .35)
    rn = rns - rnl
    result = (.408 * slope * rn + gamma * 900 / (mean_t + 273) * wind2 * (es-ea))
    result /= slope + gamma * (1 + .34 * wind2)
    return {"et0":result,"es":es,"ea":ea,"vpd":es-ea,"ra":ra,"rso":rso,"rs_ratio":ratio_raw,
            "rns":rns,"rnl":rnl,"rn":rn,"slope":slope,"gamma":gamma,"daylight":daylight}

checks = []
def check(name, value, expected, tolerance):
    passed = abs(value - expected) <= tolerance
    checks.append({"name":name,"value":value,"reference":expected,"tolerance":tolerance,"passed":passed})
    if not passed:
        raise AssertionError(f"{name}: {value} versus {expected}")

# Independent published reference values, FAO56 Chapters 3 and 4.
check("FAO Example 3 saturation pressure at 24.5 C",esat(24.5),3.075,.002)
check("FAO Example 3 mean saturation pressure",(esat(24.5)+esat(15))/2,2.39,.002)
ea5 = (esat(18)*.82 + esat(25)*.54)/2
check("FAO Example 5 humidity extrema",ea5,1.70,.005)
ra8, n9 = radiation_geometry(-20,246)
check("FAO Example 8 extraterrestrial radiation",ra8,32.2,.1)
check("FAO Example 9 daylight",n9,11.7,.05)
rnl11 = 4.903e-9*((25.1+273.16)**4+(19.1+273.16)**4)/2*(.34-.14*math.sqrt(2.1))*(1.35*14.5/18.8-.35)
check("FAO Example 11 net longwave radiation",rnl11,3.5,.1)
check("FAO Example 12 net radiation",.77*14.5-rnl11,7.6,.15)
u2 = (10/3.6) * 4.87 / math.log(67.8*10-5.42)
check("FAO Example 18 wind height and unit conversion",u2,2.078,.005)
ra18, n18 = radiation_geometry(50.8,187)
p18 = 101.3 * ((293-.0065*100)/293)**5.26
ea18 = (esat(12.3)*.84+esat(21.5)*.63)/2
rs18 = (.25 + .50*9.25/n18)*ra18
full18 = reference_et0(21.5,12.3,ea18,u2,rs18,p18,50.8,100,187)
check("FAO Example 18 end-to-end reconstruction",full18["et0"],3.88,.04)
# Independent arithmetic invariants; these do not establish agronomic validity.
check("1 mm over 1 hectare is 10 cubic metres",1/1000*10000,10,1e-12)
check("ETc arithmetic at constant ET0=4 and Kc=1.2",sum(4*1.2 for _ in range(10)),48,1e-10)
invalid_rejected = False
try:
    reference_et0(10,20,1,2,10,101,31,5,100)
except ValueError:
    invalid_rejected = True
assert invalid_rejected
checks.append({"name":"Reject Tmin above Tmax","passed":True})

raw = (ROOT / args.source).read_bytes()
data = json.loads(raw)
series = data["properties"]["parameter"]
first = dt.datetime.strptime(data["header"]["start"],"%Y%m%d").date()
last = dt.datetime.strptime(data["header"]["end"],"%Y%m%d").date()
assert data["geometry"]["coordinates"][:2] == [30.95,31.1], "This audit is restricted to its declared research point"
dates = [first+dt.timedelta(days=i) for i in range((last-first).days+1)]
keys = [day.strftime("%Y%m%d") for day in dates]
assert set(series) == set(EXPECTED)
assert data["header"]["time_standard"] == "LST"
assert all(set(values)==set(keys) for values in series.values())
assert all(data["parameters"][name]["units"]==unit for name,unit in EXPECTED.items())
quality = {}
for name, values in series.items():
    numbers = [values[key] for key in keys]
    bad = sum(not isinstance(v,(int,float)) or not math.isfinite(v) or v==data["header"]["fill_value"] for v in numbers)
    quality[name] = {"count":len(numbers),"missing_or_invalid":bad,"minimum":min(numbers),"maximum":max(numbers),"mean":st.mean(numbers),"units":EXPECTED[name]}
    assert bad == 0, f"Missing/invalid {name}"

rows = []
flags = {"rs_above_rso":[],"raw_ratio_below_0_3":[],"negative_unbounded_cloud_factor":[],"negative_vpd":[],"negative_et0":[],"dew_above_tmin":[]}
for date,key in zip(dates,keys):
    v = {name:series[name][key] for name in EXPECTED}
    assert v["T2M_MIN"] <= v["T2M_MAX"]
    assert 0 <= v["RH2M"] <= 100
    assert v["PRECTOTCORR"] >= 0
    result = reference_et0(v["T2M_MAX"],v["T2M_MIN"],esat(v["T2MDEW"]),v["WS2M"],v["ALLSKY_SFC_SW_DWN"],v["PS"],31.10,data["geometry"]["coordinates"][2],date.timetuple().tm_yday)
    rh_result = reference_et0(v["T2M_MAX"],v["T2M_MIN"],result["es"]*v["RH2M"]/100,v["WS2M"],v["ALLSKY_SFC_SW_DWN"],v["PS"],31.10,data["geometry"]["coordinates"][2],date.timetuple().tm_yday)
    unbounded = reference_et0(v["T2M_MAX"],v["T2M_MIN"],esat(v["T2MDEW"]),v["WS2M"],v["ALLSKY_SFC_SW_DWN"],v["PS"],31.10,data["geometry"]["coordinates"][2],date.timetuple().tm_yday,bound_cloudiness=False)
    for name, condition in (("rs_above_rso",result["rs_ratio"]>1),("raw_ratio_below_0_3",result["rs_ratio"]<.3),("negative_unbounded_cloud_factor",result["rs_ratio"]<.35/1.35),("negative_vpd",result["vpd"]<0),("negative_et0",result["et0"]<0),("dew_above_tmin",v["T2MDEW"]>v["T2M_MIN"])):
        if condition: flags[name].append(date.isoformat())
    rows.append({"date":date.isoformat(),"tmax_c":v["T2M_MAX"],"tmin_c":v["T2M_MIN"],"tdew_c":v["T2MDEW"],"rh_percent":v["RH2M"],"wind2_m_s":v["WS2M"],"solar_mj_m2_day":v["ALLSKY_SFC_SW_DWN"],"pressure_kpa":v["PS"],"rain_mm_day":v["PRECTOTCORR"],"et0_mm_day":result["et0"],"et0_rhmean_approx_mm_day":rh_result["et0"],"et0_without_cloud_floor_mm_day":unbounded["et0"]})
with (ROOT / f"weather_et0{args.suffix}.csv").open("w",newline="",encoding="utf-8") as handle:
    writer = csv.DictWriter(handle,fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)

et = [r["et0_mm_day"] for r in rows]
report = {
    "source_sha256":hashlib.sha256(raw).hexdigest(),"days":len(rows),"parameters":len(EXPECTED),"values":len(rows)*len(EXPECTED),
    "coverage":[dates[0].isoformat(),dates[-1].isoformat()],"quality":quality,"reference_checks":checks,
    "full_reference_example":full18,"flags":{k:{"count":len(v),"first_dates":v[:10]} for k,v in flags.items()},
    "et0_summary":{"minimum_mm_day":min(et),"maximum_mm_day":max(et),"mean_mm_day":st.mean(et),"mean_annual_total_mm":sum(et)/(last.year-first.year+1) if (first.month,first.day)==(1,1) and (last.month,last.day)==(12,31) else None},
    "humidity_method_sensitivity":{"mean_abs_difference_mm_day":st.mean(abs(r["et0_mm_day"]-r["et0_rhmean_approx_mm_day"]) for r in rows),"note":"Dewpoint route preferred for this audit. The RH-mean comparison is an approximation, not an independent truth reference."},
    "cloud_bound_sensitivity":{"source":"https://content-hub.uidaho.edu/api/public/content/9d9ea3f325e945158730b61661e8add8?v=cc545c86","equation":"ASCE-EWRI2005 Eq18, printedpage20: 0.3<=Rs/Rso<=1.0","mean_abs_difference_mm_day":st.mean(abs(r["et0_mm_day"]-r["et0_without_cloud_floor_mm_day"]) for r in rows),"maximum_abs_difference_mm_day":max(abs(r["et0_mm_day"]-r["et0_without_cloud_floor_mm_day"]) for r in rows)},
    "limitations":["No independent station or lysimeter ET0 benchmark; printed monthly weather-table diagnostic is separate","Daily aggregated gridded inputs","Native source resolution, not field resolution","Current historical archive, not issue-time vintages","ETc arithmetic check does not validate crop coefficients or management","Published rounded examples entail tolerances; no arbitrary clipping of ET0"]
}
(ROOT / f"weather_audit{args.suffix}.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k not in ("quality",)},indent=2))
