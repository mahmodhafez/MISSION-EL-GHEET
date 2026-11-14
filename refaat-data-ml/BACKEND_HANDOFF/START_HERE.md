# Start here • Backend Developer
**Yahya: P0 now includes the Agricultural KB.** Read [AGRICULTURAL_KB_CONTRACT.md](AGRICULTURAL_KB_CONTRACT.md) alongside the existing climate contract. The KB exposes 27 researched rules for wheat, berseem, grain maize and grain sorghum. Eighteen are scientifically verified; every local sign-off is pending. The planner currently receives an empty enforceable-rule list with `NO_LOCAL_SIGN_OFF`, which must remain visible as an unresolved planning dependency.

The proposed schema `agricultural_kb/schema.json` and approval/filter semantics need your approval. This handoff tests Python consumers only; it does not claim integration into your actual backend or planning engine.
**Use one local `ClimateStore` per worker.** It opens the frozen Sakha CSVs, verifies their identity and serves daily history, climatology and plan comparisons in Python. No network, GPU, HTTP service, database or third-party package is required. This is a reference consumer integration; the actual application repository was not supplied.

Extract the ZIP into a writable folder. From that folder, with Python 3.11 or later:

```console
python verify_package.py
python -m climate_data.backend_example --data data --out my_example.json
python -m agricultural_kb
python -m examples.backend_p0
python -m unittest discover -s tests -v
```

Open `my_example.json`: `request` holds two complete four-season candidate plans; the remaining keys are actual responses from all seven public methods. Compare it with `example_response.json`. Choose a fresh output filename on each run. In the complete project, commands run at the project root; the delivered copy of this example and its contract are under `BACKEND_HANDOFF/`.

```python
import json
from pathlib import Path
from climate_data.backend import ClimateStore, ClimateInputError, ClimateDataError
from agricultural_kb import load_kb, KBError

kb = load_kb()  # path relative to package, or pass a configured KB JSON path
print(json.dumps(kb.get_status(locality="sakha"), allow_nan=False))
print(kb.get_crop("grain_maize"))
approved = kb.get_approved_rules(locality="sakha")  # signed, still inspect applicability
constraints = kb.get_enforceable_rules(locality="sakha")  # only this view feeds constraints
pending = kb.get_pending_rules(crop_id="wheat", locality="sakha")
evidence = kb.get_evidence(pending[0]["evidence_ids"][0])
print(approved, constraints, evidence, kb.get_sources(evidence["source_ids"][0]))

store = ClimateStore(Path("data"), site_id="sakha_31.10_30.95")
print(store.get_data_provenance()["coverage"])
print(store.get_daily_weather("2020-02-28", "2020-03-01")["coverage"])
print(store.calculate_et0_summary("2020-02-28", "2020-03-01")["metrics"])
print(store.calculate_heat_exposure("2014-06-03", "2014-06-05")["hot_days"])
print(store.get_climatology("2028-02-29")["quantiles"]["tmax_c"])

fixture = Path("example_response.json")
if not fixture.is_file():  # directory layout of the complete project
    fixture = Path("BACKEND_HANDOFF/example_response.json")
request = json.loads(fixture.read_text(encoding="utf-8"))["request"]
replay = store.get_historical_replay(request["plans"][0], [2015], template_anchor_year=2026)
comparison = store.compare_historical_plans(request["plans"], request["anchor_years"],
                                             template_anchor_year=request["template_anchor_year"])
print(replay["status"], comparison["eligible_anchors"], comparison["exclusions"])
```

The example accepts 2015 and 2016. Anchor 2024 would extend the connected sequence into incomplete 2026 and is excluded for **both** plans. The two eligible sequences overlap in calendar time; show descriptive spread, not a confidence level or probability of success.

**Integrating:** Put this ZIP's `climate_data/` on your application's Python import path (for instance as a package under your existing source root). Keep its `data/` as a versioned, read-only runtime directory and pass its absolute path at startup. The standard library is enough. Handle `ClimateDataError` during startup as unavailable/corrupt cache. For queries, validate the site and dates, catch `ClimateInputError` for invalid requests, and branch on result `status` before displaying values. A partial historical interval has available daily rows but no total; present a gap instead of filling it with zero. Flagged observations stay in totals when coverage is complete.

**Next files:** `CONTRACT.md` defines methods, schemas, indicators, blocked states and update procedure. `SHARED_DATA_DICTIONARY.md` defines the input columns and flags. The version and source metadata are in `data/release.json` and `data/source_manifest.json`; `sources/power_provenance*.json` are the two original receipts. Use the full project's `rebuild.py` only when creating or auditing a release, never on the request path. For the UI, use “historical reference ET₀” and “days reaching the historical heat threshold.” Crop demand, irrigation volume and heat damage cannot be inferred from these outputs.

