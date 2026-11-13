# Model selection and research comparison

**Read this if…** you're wondering which model to use or whether to train something.

Status: Current,  · Owner: Amr. Last reviewed .

Decision owner: Amr. Protocol authority: [DATASET_MANIFEST](dataset-manifest.md). Deadline selection: Refaat seasonal climatology + persistence comparator; one optional Ridge challenger. No planner duplication or GPU requirement.

## What each research project actually developed

| Dimension | Amr archive | Refaat delivered ML_HANDOFF |
|---|---|---|
| Problem | Daily regional Tmax and derived reference ET0 forecasting, not crop optimization | Reproducible seasonal baseline, clean split inputs and common evaluator for the same problem |
| Data / geography | POWER 31.10 N,30.95 E; 2001–2025 plus Jan–Oct 2026 | Same lineage; shipped targets 2001–2018 and 2019–2021 only; QC extends to 2026 |
| Inputs / preprocessing | Two channels, 60 days, float32 experiment values; frozen ET0 | Same targets; exact split/finite/schema/hash checks; float32 research baseline/truth, source precision retained |
| Horizon | Input cutoff D−7; predict 14 steps; score steps 8–14 = D+1…D+7 | Identical 36 diagnostic issue dates, cutoff/context and scoring |
| Architecture | Chronos-2 base; actual LoRA rank8/alpha16; persistence; seasonal comparator | Standard-library 366-slot ±15-day empirical q10/q50/q90; no trained model |
| Fit | 2001–2018; LoRA 20 and 200 updates, LR 1e−5, batch4, seed | Calendar distribution estimated from 6,574 fit rows; no optimizer/training loop |
| Validation | Monthly 15th, 2019–2021; adapter selected by ET0 MAE | Same 36 origins, 252 days/target; independently reproduced reference matches archived baseline |
| Consumed assessment | 17 weekly origins Jul–Oct2026;119 days/target | Not shipped as a new model evaluation; documented as consumed |
| Reproducibility | Archive source/checkpoints/adapters/NPZ/config; saved metrics previously rescored | 27 checked files,10 tests,5-command verification and byte-identical baseline exports now reproduced |
| Hardware | Archived 4GB RTX3050 run,40.31s/200 updates,~1.27GB reserved; only that configuration measured | CPU standard library; current local verification about seconds, no GPU needed |
| Risks | Unknown foundation pretraining overlap; revised archives, simulated latency; consumed 2026; small correlated assessment | Same vintage/latency limit; target-date QC must not become features; descriptive all-year reference must not fit validation |
| Planner use | Optional near-term context only; losing model does not justify recommendation | Reusable baseline/scoring/data engineering; calendar expectation, not crop feasibility |

No new trained Refaat model, notebooks, independent locations or crop-yield labels were delivered. No missing source/full-project artifact is counted as inspected. Reuse his public loader/evaluator intact. The supplied full-project `release.json` references an absent `sakha_daily.csv`; use the package manifest for delivered-file verification and the assembled outer manifest for integration.

## Fair numerical comparison

The aligned **2019–2021 diagnostic** comparison can be reported: Refaat's newly reproduced seasonal baseline is exactly Amr's archived baseline. Chronos values below are read from archived `adaptation200/results.json`, not newly inferred or independently rescored in this task.

| Aligned diagnostic model | Tmax MAE °C | ET0 MAE mm/day | Evidence |
|---|---:|---:|---|
| Refaat/Amr seasonal climatology | 2.534365 | 0.583124 | Reproduced byte-identical outputs |
| Amr persistence | 3.790159 | 0.887813 | Archived result |
| Amr zero-shot Chronos-2 | 3.301484 | 0.737995 | Archived result |
| Amr LoRA adaptation200 | 3.289063 | 0.729120 | Archived result |

Separately, the **consumed Jul–Oct2026** assessment remains: climatology 1.656/.523, zero-shot2.000/.644, LoRA1.988/.640. Do not compare the diagnostic 2.534/.583 against these different dates as evidence of model gain/loss. For future fair comparisons use identical keyed predictions, source hashes, cutoff, targets, units, float32 scoring and issue set. Refaat requires no target transformation: all 7,670 dates×2 targets match the original frozen CSV exactly. Any external model with a different target/grid/horizon stays separately reported until it can predict these exact keys from allowed context.

## Final classification

| Option | Classification | Exact use / owner | Decision |
|---|---|---|---|
| Seasonal climatology | PRODUCTION CORE; REUSE EXISTING | CPU historical calendar expectation, daily Tmax/ET0; Mahmoud adapter, Refaat data | Adopt Refaat's tested method; a forecast bundle remains experimental and must satisfy time/availability gates |
| Ridge | TRAIN NOW **only at explicit compute gate**; EXPERIMENTAL | 14 direct daily models, D+1…7, two targets; Mahmoud | Only new trained challenger; Amr authorizes bounded CPU fit after P0 is working |
| LightGBM | DEFER | None for deadline | Extra dependency/tuning not justified over one Ridge experiment |
| Chronos-2 zero-shot | REUSE EXISTING | Archived diagnostic/consumed evidence; Amr | No new install/download/inference required; a short replay only if environment already works and P0 is done |
| Existing LoRA | REUSE EXISTING; EXPERIMENTAL | Historical trained-work evidence; Amr | Keep negative result. No deployment/promotion |
| New Chronos experiment / LoRA | DEFER | None before submission | Do not spend GPU/setup time on an already losing model family |
| Refaat models | REUSE EXISTING | SeasonalClimatology and scoring; Mahmoud | Same experiment lineage, not an independent model ensemble |
| Complementary combination | PRODUCTION CORE | Deterministic planning + historical analysis + separate climatology | Combine functions, never average incompatible scores or use weather to override rules |
| C3S seasonal outlook | DEFER | No validated Sakha skill/data | Explicit unavailable; monthly anomaly is not daily Tmax or stage heat risk |
| Duplicated-grid training / invented outcomes | REJECT | None | Scientifically invalid |

“Production core” here means the controlled prototype's reliable software path, not operational agricultural/forecast validation. Current data end ; a history-dependent Nov13 forecast with D−7 context cannot run from that data. Calendar-only expectation can use its fixed historical reference without pretending recent weather exists, but must be labelled and schema-approved. Default application forecast remains unavailable/stale when no valid current bundle exists; historical analysis continues.

Ridge specifications, thresholds and stops appear only in DATASET_MANIFEST. No deep learning framework is required. Framework facts: [Ridge API](https://scikit-learn.org/1.6/modules/generated/sklearn.linear_model.Ridge.html). Pins are bounded reproducibility choices, not a claim of newest versions or locally tested installation.
