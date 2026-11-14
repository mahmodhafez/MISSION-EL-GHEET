# Status: ML and data

**Read this if…** you're asking "what data and models exist, and what runs?"

**As of 2026-11-13**, inspected base `70891af`. Owner(s): Amr (coordination), Refaat / Ahmed (data, climatology and optional Ridge), Mahmoud (historical evaluator). Implementation pending unless explicitly verified below.

---

## Next up

From the [ML plan](../ml/plan.md) (13 Nov):

1. Share the assembled release `meg-shared-20261113-v1`; every recipient verifies hashes against its manifest.
2. Refaat: 38-feature schema, keyed X/y, origin ledger, no-future-feature tests.
3. Refaat / Ahmed: existing climatology baseline and optional bounded Ridge experiment after Amr's go. Mahmoud owns historical Season Replay; no new ML training.
4. Amr: coordinate acceptance; optional bundle publication only after a scientifically supported artifact and Yahya-approved schema exist. No trained forecast or bundle is required for P0.

## Built and verified

- 2026-11-14, branch `climate/season-replay-hardening` (uncommitted), base Mahmoud's `2a4e4bc`:
  - **Season Replay** gives a planting-window comparison. Layer A is historical NASA POWER 2001–2025 and Layer B is
    Refaat's evaluated 2001–2018 climatology.
  - **Verified on the real release:** UH-001 numbers match an independent CSV recomputation (≤1e-14), and the
    climatology matches Refaat's module on 366/366 slots.
  - **Tests:** 46 backend tests and 84 planner tests pass.
  - **Fixed:** invented crop dates, hardcoded verdicts and a git-writing data loader were removed.
  - **Not yet:** the FastAPI route, data shipping and Vercel. See the [audit](../reviews/season-replay-final-audit.md).

| Thing | Path | Verified |
|---|---|---|
| NASA POWER / ET0 audit + regeneration scripts | `data/validation/` | 16 tests pass (13 Nov, Linux, Python 3.12.3); **13 skip** without the validation ZIP. With the ZIP: 16/16 pass (Amr, 12–13 Nov, Windows, 3.13.5) |
| Shared-release builder | `ml/tools/prepare_shared_release.py` | 3 tests pass (1 skips without the ZIP), 13 Nov |
| Refaat's climatology + evaluator package | `data/local/shared-20261113-v1/refaat/` (also `work/refaat-handoff-/`) | 10 tests + 5 reproduction commands passed on Amr's machine (13 Nov), [record](../ml/refaat-verification.json). Needs the CSVs, which are not in git |
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

Confirmed assignment update, 2026-11-13: [team roster](../team.md) governs current ownership. FastAPI and Fieldlight Hybrid are chosen; shared API approval is pending. No trained forecast is required for P0. Recovered NASA/climatology subset is local and Git-ignored; Phase 3 frontend assets await safe transfer.
