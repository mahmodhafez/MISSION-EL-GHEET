# Final agricultural KB publication verification

**Read this if…** you need the actual rerun results for the final reviewed delivery.

Status: Frozen verification record, 2026-11-14 · Owner: Refaat · Last reviewed: 2026-11-14.

The authoritative package is `MISSION-EL-GHEET_Agricultural-KB_2026-11-14.1`, release
`sakha-agricultural-review-2026-11-14.1`. This publication check preserved the completed
scientific review. It did not grant any agronomic approval.

## Provenance and application

- All **42** entries in the supplied `SHA256SUMS.txt` passed.
- The prior review implementation's **39** deliverable files matched the package byte for byte.
- The local review branch starts at `5644125a10f1866fc1d8fac84bd5de689402cc57`, the available
  `planner/twelve-crop-catalogue` tip. The previous checkout and its staged work were preserved.
- The source was a shallow partial clone. An independent sparse checkout was assembled from
  its available Git objects because an offline local clone requested missing unrelated objects.
  Cached branch ancestry is verified; the current GitHub branch state was unavailable.
- `integration.patch` SHA-256:
  `6f6b4edf7105419bae01e69a919ae39609d8e2f11e36983e34905989c10ff13b`.
  The exact `START-HERE.md` order succeeded: `git apply --check`, apply only `.gitattributes`,
  check excluding `.gitattributes`, then apply excluding `.gitattributes` with
  `--whitespace=nowarn`.
- Windows checkout conversion affected 22 unsealed text files. Only CRLF-to-LF normalization
  that reproduced each supplied SHA-256 was permitted. All 39 applied files then matched the
  package byte for byte. Git stores normal text with LF; the attributes preserve sealed data.
- All eight frozen source-manifest files passed verification. Rebuilding the original KB
  reproduced its bytes. The reviewed matrix contains 102 unique dossier records; all remain
  `PENDING`, `DISABLED`, and not runtime-enforceable. C01–C27 and linked evidence are retained.
- The only additions to the reviewed deliverables are this rerun evidence, documentation index
  links and a planner-status link. The supplied scientific reports and data remain intact.

[Integrity results](2026-11-14-agricultural-kb-publication/integrity.json)

The complete staged diff contains 50 intended paths: 39 reviewed deliverables and 11 additional
documentation/evidence files. There are no deletions, unrelated files, unstaged changes or
untracked files in the publication checkout. Every reviewed path was reconciled against the
package; only the planner status gained the separate rerun link. The default `git diff --check`
reports 217 warnings from preserved source bytes, primarily CRLF CSV rows. With `cr-at-eol`,
four historical Markdown trailing-space warnings remain. Those source files were preserved
to retain their original hashes. The new documentation and evidence pass the whitespace check.

## Actual tests

Windows, CPython **3.12.14**. The runs completed on 2026-11-14 at approximately 03:04 UTC.
Counts below come from this execution, not the delivery's historic test logs.

| Run | Passed | Failures | Errors | Skips |
|---|---:|---:|---:|---:|
| Integrated planner suite | 110 | 0 | 0 | 0 |
| Original KB suite, unchanged input copy | 18 | 0 | 0 | 0 |
| Legacy P0 discovery | 0 | 0 | 1 | 0 |
| Legacy backend discovery | 0 | 0 | 1 | 0 |

The planner's 110 passing tests include 27 Promise Test cases, 16 constraint edge cases,
21 generation cases, 18 search-boundary cases, 11 catalogue cases, 9 adapter cases,
2 manual CLI cases and 6 reviewed-release integration cases. These are subdivisions,
not additional tests. The original 18 KB tests exercise approval gates and frozen source fidelity.

The P0 and backend runs executed zero test methods: each discovery registered one failed-import
placeholder. P0 cannot import `scripts.verify_legacy`; backend cannot import `climate_data.backend`.
No substitute modules or synthetic passing results were introduced.

From `packages/meg-core`, with `python` resolving to Python 3.12.14:

```powershell
$env:MEG_AGRI_KB = (Resolve-Path 'src/knowledge_base/sakha-agricultural-review-2026-11-14.1/agricultural_kb.json').Path
python -B -I -S -m unittest discover -s tests -v
python -B -I -S tools/planner_cli.py check tools/fixtures/uh001.json --json
python -B -I -S tools/planner_cli.py plan tools/fixtures/uh001.json --json
python -B -I -S tools/reviewed_uh001.py
```

All four commands exited 0. From a writable byte-preserved copy of the original input tree:

```powershell
python -B -S -m unittest discover -s tests -p test_kb.py -v
python -B -S -m unittest discover -s tests -p test_p0.py -v
python -B -S -m unittest discover -s tests -p test_backend.py -v
```

Their exit codes were 0, 1 and 1 respectively. The original-input test tree is an external
review input, not an additional runtime dependency or a claim that it exists in this repository.

[Machine summary](2026-11-14-agricultural-kb-publication/test-summary.json) ·
[Planner log](2026-11-14-agricultural-kb-publication/planner-tests.txt) ·
[Original KB log](2026-11-14-agricultural-kb-publication/legacy-kb-tests.txt) ·
[P0 error](2026-11-14-agricultural-kb-publication/legacy-p0.txt) ·
[Backend error](2026-11-14-agricultural-kb-publication/legacy-backend.txt)

## UH-001 and limitations

Both stock CLI commands and the reviewed-release replay exited 0. The replay calls the real
Promise Test, candidate generator and planning service. Current plan: `rejected`, first reason
`sowing_before_protected_cut`. The protected cut remains 20 May 2027. The 28 May and 1 June
alternatives remain `needs_review`, with unknown S2 harvest, crop end and field release.
Five raw combinations produced two evaluated and three blocked cases; zero were feasible.
The seven preparation days remain only the independent supplied fixture assumption.

[Stock check](2026-11-14-agricultural-kb-publication/uh001-stock-check.json) ·
[Stock plan](2026-11-14-agricultural-kb-publication/uh001-stock-plan.json) ·
[Reviewed replay](2026-11-14-agricultural-kb-publication/uh001-reviewed.json)

The loader returns 12 catalogue crops, 9 planner profiles and **0 runtime rules**. All qualified
agronomic approvals remain pending. Wheat applicability and advisory-versus-hard-constraint
meaning, berseem forage-versus-seed purpose, cultivar/parcel scope, operational release dates
and transition preparation still require the documented qualified, named and dated sign-off.
Shared HTTP/contracts, deployment and parcel authorization were not verified. No ML branch,
source scientific decision or runtime scientific activation was changed.

GitHub HTTPS was unreachable from this execution environment. This record establishes local
application and verification; it is not evidence of a successful push or an opened PR.
