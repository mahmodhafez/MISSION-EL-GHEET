# Agricultural KB integration tests

**Read this if…** you need the exact commands, counts and outputs behind the [KB review](agronomy-kb-final-review.md).

Status: Executed 2026-11-14 · Windows 11, CPython 3.13.14 · Release `sakha-agricultural-review-2026-11-14.1` · Branch `review/agronomy-kb-final` (base `cae1703`).

---

## Commands and counts

From `packages/meg-core`:

```powershell
python -I -S -m unittest discover -s tests                                    # default
$env:MEG_AGRI_KB = "src\knowledge_base\sakha-agricultural-review-2026-11-14.1\agricultural_kb.json"
python -I -S -m unittest discover -s tests                                    # real reviewed KB
$env:PYTHONPATH = "src"; python tools\reviewed_uh001.py                      # UH-001 through the release
```

| Run | Tests | Result |
|---|---|---|
| Refaat's commit `cae1703`, default | 110 | 110 passed, 3 skipped (real-KB tests need `MEG_AGRI_KB`) |
| `cae1703` with the reviewed KB / original KB | 110 | 110 passed, 0 skipped (both) |
| After this review, with the reviewed KB | **118** | **118 passed, 0 failed, 0 skipped** |
| After this review, default | 118 | 118 passed, 3 skipped |
| New `test_release_integration.py` | 8 | passed. Mutation checks confirmed that removing the berseem conflict lets a signed C07 map, and that an ambiguous forage profile is refused. |

Recorded by Refaat but outside this planner branch: his 18 original KB tests passed. Two legacy science tests error
because they import `climate_data`, which is not in this branch (`verification/backend.txt`, `p0.txt`).

## Acceptance examples (all in tests)

| Case | Where | Result |
|---|---|---|
| UH-001 original | `test_uh001_reviewed_release` | `rejected`, first reason `sowing_before_protected_cut` |
| UH-001 alternatives 28 May / 1 Jun | same | both `needs_review`; cut 2027-05-20 kept; harvest and release null; 0 feasible |
| Synthetic fully evidenced feasible | `test_generation.py::test_supported_mapping_changes_review_to_feasible` (**SYNTHETIC-ONLY** rules) | `feasible` only when every mandatory topic has synthetic verified support |
| Conflicting evidence | `test_conflicted_wheat_and_berseem_rules_stay_held_even_if_signed` | a signed C01 or C07 is held (`unresolved_evidence_conflict`); a signed non-conflicted C14 maps |
| Research-only crop | `test_research_only_and_wrong_purpose_attempts_are_blocked` | watermelon is not in `available_crop_ids`; blocked `catalogue_value_unavailable` |
| Wrong purpose | same + `test_forage_and_seed_are_not_interchangeable` | grain rice in a forage slot is uninstantiated; a seed berseem season is refused |
| Missing field release | `test_uh001_reviewed_release` | candidate release stays null, so the status stays `needs_review` |
| Pending rule enforcement | `test_pending_rules_never_enforced` | 0 enforceable, 0 planner rules |
| Wrong season year | `test_wrong_season_year_never_applies_a_rule` | rule `not_applicable` |
| Outside release scope | `test_outside_release_scope_refused` | `KBError OUTSIDE_RELEASE_SCOPE` |

## UH-001 output (`tools/reviewed_uh001.py`)

```text
release sakha-agricultural-review-2026-11-14.1 · catalogue 12 crops · runtime rules 0
planner profiles: berseem, berseem-forage-proposed, egyptian_cotton, faba_bean, grain_maize,
                  grain_sorghum, rice, sugar_beet, wheat
current: rejected (sowing_before_protected_cut) · protected cut 2027-05-20 · feasible 0
search: incomplete / uninstantiated_choices · raw 5 · evaluated 2 · blocked 3 (s4-maize)
2027-05-28 needs_review · harvest null · release null · 10 review reasons
2027-06-01 needs_review · harvest null · release null · 10 review reasons
```

## Not run

Python 3.12 interpreter (grammar checked only), Yahya's backend with the release (patch not applied), and frontend.
