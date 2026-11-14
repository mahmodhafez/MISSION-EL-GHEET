# Local inputs not stored in git

**Read this if…** `tests/test_pipeline.py` or `rebuild.py` fails with a missing `sources/...` file.

Status: Current · Owner: Refaat · Last reviewed 2026-11-14.

---

Four NASA POWER files are raw or derived data, so `.gitignore` keeps them out of the repository. The pipeline pins each one
by SHA-256 (`climate_data/pipeline.py` and `data/source_manifest.json`) and refuses any other bytes.

| File in `sources/` | SHA-256 |
|---|---|
| `power_sakha_2001_2025_LST.json` | `212bf82f9b2baf09eed440a5a5a6d889891964da2448a7c06a57deb3954f20bf` |
| `power_sakha_2026_Jan_Oct_LST.json` | `6a957d31aff96ab9b6de604f1ed5bd0def3ee364e742458d5f0e4e9aa37b8700` |
| `weather_et0.csv` | `17141df82f6300c051257c21fb9ac3d9f5f1627fd32cbc8c07bc9296c477bde8` |
| `weather_et0_2026_Jan_Oct.csv` | `c4d5929fd0d4d55c416ee45d5ebd21502142994afbc76b00c6f20e1b349ee36e` |

Get them from Refaat or Amr. The matching copies on Amr's machine (2026-11-14) were in the archived audit replay
`work/scientific_validation_2026-11-11/archived_audit_replay/`. Check the hash before use:

```sh
sha256sum sources/power_sakha_2001_2025_LST.json
```

`sources/original/audit_weather.py` is tracked. It is a byte-identical copy of `data/validation/audit_weather.py` on `main`
(SHA-256 `905a700d…`), pinned by the pipeline.

## Missing from the pushed branch: `provenance/legacy_delivery/` (external blocker)

`tests/test_p0.py::test_original_delivery_all_hashes_and_schema_export_preserved` and `scripts/verify_legacy.py` need it,
so the suite is **54/55** until Refaat pushes it. It isn't on Amr's machine. Checked 2026-11-14: every local
`PACKAGE_MANIFEST.json` hashes to `6be436bf…`, not the pinned value. The test must not be skipped or weakened.

Required content, per `scripts/verify_legacy.py`:

- `provenance/legacy_delivery/PACKAGE_MANIFEST.json`, the original 66-file delivery manifest, with SHA-256
  `2947f8bec57c4a4a378893c34305540e5336997fe31856b5e66f654af1952aae`.
- The original bytes of each file changed after delivery, stored at its manifest path under `provenance/legacy_delivery/`.
  The P0 report names them: `README.md`, `BACKEND_HANDOFF/START_HERE.md`, `ML_HANDOFF/START_HERE.md`,
  `make_handoffs.py`, `check_handoff.py`. Every other manifest entry is checked against the current file.

Also note: `outputs/handoffs/BACKEND_HANDOFF.zip` (853,197 B) and `ML_HANDOFF.zip` (389,125 B) are tracked, although the
P0 report says generated ZIPs should be excluded. They were left in place pending Refaat's decision. `make_handoffs.py`
can't rebuild them until the root `PACKAGE_MANIFEST.json` (also absent from the push) is restored.
