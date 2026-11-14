# Season Replay: test report

**Read this if…** you want the exact commands, counts and real outputs behind the [audit](season-replay-final-audit.md).

Status: Executed 2026-11-14 · Windows 11, CPython 3.13.14, pytest 9.2.0 (Yahya's pinned version) · Branch `climate/season-replay-hardening` (base `2a4e4bc`).

---

## Commands and counts

Run from the repository root:

```powershell
$env:MEG_CLIMATE_DATA_DIR = "<path>\refaat-data-ml\data"          # release sakha-power-lst-20261110-et0-v1
$env:MEG_REFAAT_DIR = "<path>\refaat-data-ml"                      # optional: cross-check cited metrics
python -m pytest backend/tests -q -p no:cacheprovider -rs
```

| Suite | Tests | Result |
|---|---|---|
| Mahmoud's original suite at `2a4e4bc` (before changes) | 22 | 22 passed (and wrote 7 files into the repo, see audit D3) |
| `backend/tests` after fixes | **46 + 13 subtests** | **46 passed, 0 failed, 0 skipped** (with `MEG_REFAAT_DIR`; without it, 1 skip) |
| · `test_windows.py` (SYNTHETIC data, hand-computed) | 12 | passed |
| · `test_climate_real.py` (REAL NASA release) | 6 | passed |
| · `test_uncle_hussein.py` (real data + real Promise Test) | 6 | passed |
| · `test_replay.py`, `test_climatology.py`, `test_evidence_card.py`, `test_replay_cli.py` | 22 | passed |
| Planner regression `packages/meg-core` (`python -I -S -m unittest discover -s tests`) | 84 | passed, unchanged |

Blocked: none. Not run: Python 3.12 interpreter (not installed), a clean-environment install, and a Vercel
deployment.

## Independent checks

- **Synthetic math** (`test_windows.py`): known Tmax ramp/constant ET0. Covers exact window means and totals, n−1
  versus population SD, paired difference and year counts, Feb 29 exclusion, Dec→Jan rollover, cross-year offsets,
  missing-day pairing, quarantine exclusion, invalid inputs (13 subcases), and deterministic JSON with `allow_nan=False`.
- **Real NASA arithmetic:** a separate script (plain `csv` + `statistics`, no shared code) recomputed UH-001 from
  `sakha_daily.csv`. All 10 compared figures matched within **7.1e-15**. `test_climate_real.py` repeats this for
  every year and window.
- **Climatology:** Layer B q50 for 28 May was recomputed independently from `fit_targets.csv` (float32, ±15
  leap-calendar slots, type-7 quantile); support days and value match. Mahmoud's climatology matches Refaat's
  module on 366/366 slots.
- **Cited metrics:** equal to `ML_HANDOFF/reference/metrics.json` (test runs when `MEG_REFAAT_DIR` is set).

## Real UH-001 output

Input: protected cut **2027-05-20**; original sowing 2027-05-15; investigated sowings **2027-05-28** (W1, reference)
and **2027-06-01** (W2); 14-day windows. Release `sakha-power-lst-20261110-et0-v1`, historical snapshot SHA-256
`212bf82f…`.

Promise Test (real planner, `uh001.json`): original **rejected**, 28 May **needs_review**, 1 Jun **needs_review**,
0 feasible. Climate output echoes these unchanged.

**Layer A — historical, 25 years (2001–2025), 0 excluded, same years for both windows:**

| Metric | 28 May–10 Jun | 1–14 Jun | Paired difference (W2−W1) |
|---|---|---|---|
| Mean daily Tmax, degC | 36.59 (SD 1.33; 33.99–39.14) | 36.90 (SD 1.51; 34.75–41.59) | **+0.30** (SD 0.93), hotter in 14/25 years |
| Hottest day in window, degC | 42.38 | 42.48 | +0.10, higher 4 / lower 4 / equal 17 |
| Mean daily ET0, mm/day | 8.50 | 8.54 | +0.04 |
| Total ET0 over 14 days, mm | 119.01 (107.6–129.7) | 119.58 (108.2–136.4) | **+0.56** (SD 3.40), higher in 13/25 years |

**Layer B — climatology (evaluated 2001–2018 baseline), typical conditions for the 2027 dates:**

| Metric | 28 May–10 Jun | 1–14 Jun | Difference |
|---|---|---|---|
| Tmax q50 (window mean), degC | 36.00 (q10–q90 32.46–40.78) | 36.46 (32.93–41.05) | +0.47 |
| ET0 q50 (window mean), mm/day | 8.29 | 8.41 | +0.12 |
| Sum of daily ET0 q50, mm | 116.10 | 117.71 | +1.61 |

**Interpretation.** The later window was slightly warmer on average. The difference is smaller than the normal
year-to-year spread and reverses in 11 of 25 years. ET0 differences are negligible relative to their spread.
Neither layer says which date is agriculturally better, and neither changes the `needs_review` statuses.

## Performance (real data, this laptop)

Store load **0.21 s**, one UH-001 comparison **1.3 ms**, JSON payload **29 KB**. Standard library only, CPU only,
no network at runtime. Release directory on disk is about 2.5 MB.
