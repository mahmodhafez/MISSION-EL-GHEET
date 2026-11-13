"""Download one public NASA POWER point for scientific readiness checks."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import urllib.parse
import urllib.request

folder = Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument("--start",default="20010101")
parser.add_argument("--end",default="20251231")
parser.add_argument("--suffix",default="2001_2025")
args=parser.parse_args()
parameters = {
    "parameters": "T2M_MAX,T2M_MIN,T2MDEW,RH2M,WS2M,ALLSKY_SFC_SW_DWN,PS,PRECTOTCORR",
    "community": "AG", "longitude": "30.95", "latitude": "31.10",
    "start": args.start, "end": args.end, "format": "JSON", "time-standard": "LST",
}
url = "https://power.larc.nasa.gov/api/temporal/daily/point?" + urllib.parse.urlencode(parameters)
request = urllib.request.Request(url, headers={"User-Agent": "Mission-El-Gheet-Research-Readiness/1.0"})
with urllib.request.urlopen(request, timeout=90) as response:
    raw = response.read()
    status = response.status
    content_type = response.headers.get("Content-Type")
data = json.loads(raw)
assert data.get("type") == "Feature" and "parameter" in data.get("properties", {}), "Not a data response"
path = folder / f"power_sakha_{args.suffix}_LST.json"
path.write_bytes(raw)
provenance = {
    "url": url, "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "http_status": status, "content_type": content_type, "bytes": len(raw),
    "sha256": hashlib.sha256(raw).hexdigest(), "parameters": parameters,
    "coordinate_status": "Provisional research point near Sakha; not a confirmed farmer parcel. Pilot locality remains evidence-dependent.",
    "capture_method": "Original HTTP response bytes downloaded directly from NASA POWER API.",
    "response_header": data["header"], "response_units": data["parameters"],
    "limitation": "Archive downloaded now, not historical issue-time vintages. Gridded products, not field observations.",
}
(folder / ("power_provenance.json" if args.suffix=="2001_2025" else f"power_provenance_{args.suffix}.json")).write_text(json.dumps(provenance, indent=2), encoding="utf-8")
print(json.dumps({"status":status,"bytes":len(raw),"sha256":provenance["sha256"],"header":data["header"],"counts":{k:len(v) for k,v in data["properties"]["parameter"].items()},"units":{k:v["units"] for k,v in data["parameters"].items()}},indent=2))
