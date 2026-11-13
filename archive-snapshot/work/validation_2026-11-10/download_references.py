from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import urllib.request

folder = Path(__file__).resolve().parents[1] / "agronomy"
folder.mkdir(exist_ok=True)
sources = {
    "sugita_2017.pdf": "https://tsukuba.repo.nii.ac.jp/record/41521/files/HydrologicalSciencesJournal_20170314.pdf",
    "maize_arc.pdf": "https://www.arc.sci.eg/files/2114/Attachment.pdf",
}
def fetch(item):
    name, url = item
    try:
        with urllib.request.urlopen(url, timeout=40) as response:
            raw = response.read()
            status = response.status
        if not raw.startswith(b"%PDF"):
            raise ValueError("Response is not PDF bytes")
        (folder / name).write_bytes(raw)
        return {"file": name, "url": url, "status": status, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    except Exception as exc:
        return {"file":name,"url":url,"error":str(exc)}
with ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(fetch, sources.items()))
(folder / "download_provenance.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
