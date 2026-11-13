"""Download only the approved public checkpoint into the task workspace."""
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "checkpoint"
REVISION = "29ec3766d36d6f73f0696f85560a422f50e8498c"
MODEL = "amazon/chronos-2"
EXPECTED_SHA256 = "ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42"


def download(filename: str) -> dict:
    url = f"https://huggingface.co/{MODEL}/resolve/{REVISION}/{filename}"
    target = DEST / filename
    partial = target.with_suffix(target.suffix + ".partial")
    started = time.perf_counter()
    digest = hashlib.sha256()
    size = 0
    request = urllib.request.Request(url, headers={"User-Agent": "MISSION-EL-GHEET-validation/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response, partial.open("wb") as stream:
        status = response.status
        while chunk := response.read(1024 * 1024):
            stream.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    actual_hash = digest.hexdigest()
    if filename == "model.safetensors" and actual_hash != EXPECTED_SHA256:
        raise RuntimeError(f"Checkpoint hash mismatch: {actual_hash}")
    if filename == "config.json":
        config = json.loads(partial.read_text(encoding="utf-8"))
        if config["architectures"] != ["Chronos2Model"]:
            raise RuntimeError("Unexpected model architecture")
    partial.replace(target)
    return {"filename": filename, "url": url, "http_status": status, "bytes": size,
            "sha256": actual_hash, "seconds": time.perf_counter() - started}


if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    results = []
    for filename in ["config.json", "model.safetensors"]:
        print(f"Downloading {filename} at pinned revision {REVISION}", flush=True)
        result = download(filename)
        results.append(result)
        print(json.dumps(result), flush=True)
    provenance = {"model_id": MODEL, "revision": REVISION,
                  "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
                  "published_weight_sha256": EXPECTED_SHA256,
                  "files": results}
    (ROOT / "checkpoint_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
