# Status: ML and data

**Read this if…** you're asking "what data and models exist, and what runs?"

**As of **, last commit `0122e92`. Owners: Amr (ML decisions), Refaat (data), Mahmoud (Ridge). If this is far behind `git log`, trust git.

---

## Next up

From the [ML plan](../ml/plan.md) (13 Nov):

1. Share the assembled release `meg-shared--v1`; every recipient verifies hashes against its manifest.
2. Refaat: 38-feature schema, keyed X/y, origin ledger, no-future-feature tests.
3. Mahmoud: climatology adapter; one Ridge experiment **only** after Amr's go (≤3 h).
4. Amr: accept/reject artifacts; write `forecast_bundle.json` for the backend.

## Built and verified

| Thing | Path | Verified |
|---|---|---|
| NASA POWER / ET0 audit + regeneration scripts | `data/validation/` | 16 tests pass (13 Nov, Linux, Python 3.12.3); **13 skip** without the validation ZIP. With the ZIP: 16/16 pass (Amr, 12–13 Nov, Windows, 3.13.5) |
| Shared-release builder | `ml/tools/prepare_shared_release.py` | 3 tests pass (1 skips without the ZIP), 13 Nov |
| Refaat's climatology + evaluator package | `data/local/shared--v1/refaat/` (also `work/refaat-handoff-/`) | 10 tests + 5 reproduction commands passed on Amr's machine (13 Nov), [record](../ml/refaat-verification.json). Needs the CSVs, which are not in git |
| Chronos-2 + LoRA experiment | Validation ZIP only | Trained and reloaded (11 Nov). **Lost to seasonal climatology.** [Results](../ml/ml-experiment.md) |

## Not in git (must be transferred)

`docs/VALIDATION_ARTIFACTS.zip` (468 MB), `ML_HANDOFF.zip`, the release CSVs. See
[artifact transfer](../archive/handoff-/ARTIFACT_TRANSFER.md).

## Known problems

- Weather data ends , so a live forecast for mid-November can't run from it. The
  default forecast state is `unavailable`/`stale`.
- Jul–Oct 2026 is a consumed test period; it can't be reused as a fresh test.
- Full public reproduction is blocked until the frozen inputs have an approved distribution.
- Mahmoud's and Refaat's hardware are unverified.

## Proposals (not approved)

- [Multi-grid-cell experiment](../ml/multigrid-proposal.md).
