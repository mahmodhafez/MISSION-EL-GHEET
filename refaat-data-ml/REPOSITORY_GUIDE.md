# Repository setup and delivery

Use Python 3.11+ and open the project root in VS Code. No runtime/test packages, API keys, GPU or downloads are required. `requirements.txt` intentionally documents standard-library-only dependencies.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe verify_package.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Select `.venv\Scripts\python.exe` using VS Code's **Python: Select Interpreter**. Activation is optional; using the executable directly avoids PowerShell execution-policy changes. On macOS/Linux use `python3 -m venv .venv` and `.venv/bin/python`. Open an ordinary Python terminal at the project root for module commands. Do not install model libraries for this P0 package.

## Folder ownership

| Path | Contents / consumer |
|---|---|
| `climate_data/` | Unchanged pipeline, FAO-56 ET0, climatology, historical replay and backend API. |
| `data/` | Immutable 9,435-day climate release, QC, ML splits/windows, runtime source metadata and hashes. |
| `sources/` | Original climate responses/receipts/ET0 comparison CSVs; `original/` holds the independent scientific audit. |
| `sources/agriculture/` | Eight unchanged recovered research files and their new integrity manifest. Keep all relative-linked reports together. |
| `agricultural_kb/` | Standard-library loader, schema validator, JSON schema and deterministic research importer. |
| `knowledge_base/` | Source-linked structured crop KB with pending local approvals. |
| `examples/` | Combined Yahya consumer; no modifications to the team's backend. |
| `tests/` | Existing climate tests, KB approval/source tests and portable consumer checks. |
| `BACKEND_HANDOFF/` | Yahya's guides, climate and KB contracts, original climate response example. This folder alone is not a standalone runtime. |
| `ML_HANDOFF/` | Mahmoud's guide and immutable baseline reference files. This folder alone is not a standalone runtime. |
| `provenance/experiment/` | Historical experiment records only; no models or new experiments. |
| `provenance/legacy_delivery/` | Original delivery manifest and five modified files' original bytes. Unmodified scientific files are reused from their original locations. |
| `reports/` | Existing scientific/handoff evidence, initial and final P0 QA, readiness report. |
| `scripts/` | Explicit schema export, legacy verification, repository manifest maintenance and repository audit. |
| `outputs/` | Ignored disposable builds/QA and generated recipient archives. |

Data lineage and methodology remain in `README.md` and `SHARED_DATA_DICTIONARY.md`. Climate coverage is 2001-01-01–2026-10-31 inclusive in NASA POWER local solar days. ET0 uses daily FAO-56 Penman–Monteith, dewpoint humidity, 2 m wind and ASCE [0.3,1] longwave radiation ratio bounds. Sensitivity paths remain separate. ML fits 2001–2018; validation is 2019–2021, 36 diagnostic origins and 252 scored days per target. The app descriptive climatology uses complete 2001–2025 years. Keep 2022–2025 inspected reserve and partial 2026 quarantined; no new test selection or training.

## Verification and export

```console
python verify_package.py
python -m scripts.verify_legacy
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -p test_pipeline.py -v
python -O -m unittest discover -s tests -p test_kb.py -v
python check_handoff.py --output outputs/qa.json
python -m agricultural_kb
python -m examples.backend_p0
python -m agricultural_kb.build --output outputs/rebuilt_kb.json
python -m climate_data.ml_example --data data
python -m climate_data.evaluation --data data --output outputs/baseline
python make_handoffs.py --output outputs/handoffs
python -m scripts.verify_handoffs --handoffs outputs/handoffs --output outputs/recipient_qa.json
```

Choose unused output files/directories each run. `check_handoff.py` performs the climate rebuild in disposable directories and checks byte-identical outputs; it does not rewrite `data/` or references. Both recipient archives include their own manifest and runnable guide. Extract each into a fresh folder and run `python check_handoff.py --output outputs/qa.json` there. No parent checkout or sibling archive is required.

For Yahya deliver `outputs/handoffs/BACKEND_HANDOFF.zip`, including runtime climate data, KB, research evidence, contracts, examples and consumer tests. For Mahmoud deliver `outputs/handoffs/ML_HANDOFF.zip`, including fit/validation targets, windows, QC/provenance, evaluation code, reference outputs and ML tests. `make_handoffs.py` is the exact inventory authority. Alternatively give both the full repository and their respective `START_HERE.md`; do not send just the guide folders.

## GitHub commit scope and byte preservation

No Git repository was initialized and no commit, push or remote change was made. Commit root scripts/docs, `.gitignore`, `.gitattributes`, and the versioned folders above except `outputs/`. `.gitattributes` disables newline conversion because byte-level SHA256 integrity applies to scientific CSV/JSON, Python audit sources and historical evidence alike. New text files use UTF-8/LF; do not run a formatter over frozen evidence.

The root package manifest is a new repository revision; `data/release.json` is still the original climate release. `scripts.verify_legacy` authenticates the original manifest digest and all its 66 entries using preserved originals only where files intentionally changed. After **reviewed** source/docs changes, run `python -m scripts.update_package_manifest --write`, then verify and test. This explicitly refreshes repository delivery hashes and never rewrites climate hashes or original evidence. Do not refresh hashes to conceal scientific-data changes.

There are no required model weights, virtual environments or ZIPs in the commit scope. The largest files are about 1.41 MB (canonical daily CSV), 1.21 MB (raw historical response) and 1.02 MB (archived ET0 comparison). Retain these distinct scientific roles. Small duplicated source manifests and forecast windows are required by existing interfaces/provenance and remain intact. Recipient ZIPs duplicate data deliberately for standalone handoff, live under ignored `outputs/`, and should be attached to a release or shared separately rather than committed. Historical source ZIPs outside this project remain untouched; their hashes and reused-member inventories preserve provenance.

The research includes private team-document reference URLs, not authentication tokens. Keep the team repository private unless the team decides to publish those materials. Source PDF redistribution and upstream availability are separate from this local code/data handoff. The P0 data engineering implementation is usable; agronomic sign-off, the proposed KB schema's team approval and actual backend integration remain outstanding.
