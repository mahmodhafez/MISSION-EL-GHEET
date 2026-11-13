from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import datetime as dt
import hashlib
import json
import urllib.request
from pypdf import PdfReader

folder=Path(__file__).resolve().parents[1]/"agronomy"
sources={
"aiad_2019.pdf":"https://jenvbs.journals.ekb.eg/article_54170_dd3f51abb5d4b2a15ee54215c93d8298.pdf",
"sugita_2017.pdf":"https://tsukuba.repo.nii.ac.jp/records/41521/files/HydrologicalSciencesJournal_20170314.pdf",
"egyptian_clover_fao.pdf":"https://www.fao.org/4/i3500e/i3500e.pdf",
}
def fetch(item):
    name,url=item
    try:
        with urllib.request.urlopen(url,timeout=35) as response:
            raw=response.read(); status=response.status
        assert raw.startswith(b"%PDF"),"Not PDF"
        path=folder/name; path.write_bytes(raw)
        reader=PdfReader(path)
        path.with_suffix(".txt").write_text("\n".join(f"PDF_PAGE {i+1}\n"+(p.extract_text() or "") for i,p in enumerate(reader.pages)),encoding="utf-8")
        return {"file":name,"url":url,"status":status,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"pages":len(reader.pages)}
    except Exception as exc:return {"file":name,"url":url,"error":str(exc)}
with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,sources.items()))
(folder/"study_downloads_2026-11-11.json").write_text(json.dumps({"retrieved_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"results":results},indent=2),encoding="utf-8")
print(json.dumps(results,indent=2))
