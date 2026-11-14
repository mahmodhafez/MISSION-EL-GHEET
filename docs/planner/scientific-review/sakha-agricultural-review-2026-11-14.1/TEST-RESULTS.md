# Integration verification · 14 November 2026

Windows, CPython **3.12.14**. The immutable input was extracted as `work/inputs/{team,original}`. The separate checkout at `work/repository` was based on `5644125a10f1866fc1d8fac84bd5de689402cc57`. Commands below use PowerShell, starting in the review workspace. The Python executable used was:

```powershell
$py = 'C:\Users\NOUR SOFT\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$root = (Get-Location).Path
$original = Join-Path $root 'work/inputs/original'
$repo = Join-Path $root 'work/repository'
$review = 'sakha-agricultural-review-2026-11-14.1'
```

| Suite / input | Ran | Passed | Failures | Errors | Skips |
|---|---:|---:|---:|---:|---:|
| Attached planner, original Refaat KB | 104 | 104 | 0 | 0 | 0 |
| Original KB, approval logic and frozen source fidelity | 18 | 18 | 0 | 0 | 0 |
| Integrated planner, reviewed KB (104 original + 6 new) | 110 | 110 | 0 | 0 | 0 |
| Legacy P0 delivery tests, discovery | 1 import placeholder | 0 | 0 | 1 | 0 |
| Legacy climate backend tests, discovery | 1 import placeholder | 0 | 0 | 1 | 0 |

The first and third runs overlap. The last two rows contain zero executed test methods. They each represent one unittest discovery error. [Baseline](verification/baseline.txt) · [Original KB](verification/legacy.txt) · [Integrated](verification/release.txt) · [P0 error](verification/p0.txt) · [Backend error](verification/backend.txt)

```powershell
Set-Location (Join-Path $root 'work/inputs/team/packages/meg-core')
$env:MEG_AGRI_KB = Join-Path $original 'knowledge_base/agricultural_kb.json'
& $py -B -I -S -m unittest discover -s tests -v

Set-Location $original
& $py -B -S -m unittest discover -s tests -p test_kb.py -v
& $py -B -S -m unittest discover -s tests -p test_p0.py -v
& $py -B -S -m unittest discover -s tests -p test_backend.py -v

Set-Location (Join-Path $repo 'packages/meg-core')
$env:MEG_AGRI_KB = (Resolve-Path "src/knowledge_base/$review/agricultural_kb.json").Path
& $py -B -I -S -m unittest discover -s tests -v
& $py -B -I -S tools/planner_cli.py check tools/fixtures/uh001.json --json
& $py -B -I -S tools/planner_cli.py plan tools/fixtures/uh001.json --json
& $py -B -I -S tools/reviewed_uh001.py
```

All three CLI commands exited 0. The first two preserve the stock fixture and its own KB. The last command reads the same unmodified fixture, loads the packaged release, matches each existing crop/purpose to its profile, binds the new release ID, and uses the existing scope choices and confirmation. All farmer dates and commitments are preserved. It calls the real Promise Test, candidate generator and planning service. No agricultural activation was introduced to obtain these results.

| UH-001 case | Observed result |
|---|---|
| Current plan | `rejected`; first reason `sowing_before_protected_cut`, May 15 conflicts with protected May 20, 2027. |
| May 28 and June 1, 2027 | Both `needs_review`; May 20 cut retained. S2 harvest, exclusive crop end and field release are all null. The seven-day preparation figure is a fixture independent fact for an unchanged crop/profile pair. Its calendar start is unknown for a moved S2. |
| Exploration | 5 raw combinations, 2 evaluated, 3 blocked. Zero feasible; `incomplete / uninstantiated_choices`. S4 maize returned `profile_binding_unavailable` for three combinations. A listed crop alone supplies no supported sowing/profile binding for the proposed change. |

[Reviewed replay result](verification/uh001-reviewed.json) · [Stock replay summary](verification/uh001-stock-summary.json)

The initial integrated run caught a wrong assumption in the **new** regression test about the independent seven-day preparation fact. It also produced four subtest errors when the pinned-files test could not write to the OS temporary directory. The test now checks the declared independent value, and its temporary files use a writable test directory. The supplied fixtures, rule definitions, engine and 104 pre-existing tests were unchanged. The final 110-test run above passed.

## Boundaries

The original P0 suite imports `scripts.verify_legacy`, `scripts.export_kb_schema` and `make_handoffs`. Those modules are absent from the supplied original tree. Its portable combined scenario also requires the original climate/backend consumer and data. The legacy backend suite requires `climate_data.backend` and `climate_data.backend_example`; the package was absent. The supplied team backend is a placeholder, and the base branch has no shared `meg_core.contracts` implementation or HTTP adapter. Public API serialization, deployment and parcel validation were therefore not exercised. Weather/ML experiments were outside this review.
