# Agricultural KB: final review of Refaat's release

**Read this if…** you need to know whether Refaat's reviewed KB is safe to integrate and what it does not prove.

Status: Review report · 2026-11-14 · Reviewer: Amr + Astra (software and evidence gating; **not** agronomic sign-off) · Base `review/refaat-agricultural-kb` @ `cae1703` · Fix branch `review/agronomy-kb-final`.

---

## Verdict: CONDITIONAL PASS

The release loads, is hash-pinned and keeps every rule non-enforceable. UH-001 is unchanged, and 118 planner tests
pass. The scientific limitations below are non-blocking because nothing is enforced. **No rule has agronomic
approval**, so the KB must not be described as agriculturally certified.

## What Refaat delivered (`cae1703`, built directly on `planner/twelve-crop-catalogue` `5644125`)

- **Release `sakha-agricultural-review-2026-11-14.1`:** `agricultural_kb.json`, `catalogue.json`, `review.json`
  and a `manifest.json` pinned by SHA-256.
- **Loader:** `meg_core.agricultural_release.load_reviewed_release()`, plus his `agricultural_kb` package and schema.
- **Review docs:** `docs/planner/scientific-review/sakha-agricultural-review-2026-11-14.1/`, with an Arabic
  scientific review, conflicts, sources and a 102-record approval matrix.
- **Tests:** 6 new release tests; his claim of 110 planner tests passing was **verified**.

## Independent verification

| Claim / risk | Checked | Result |
|---|---|---|
| C01–C27 preserved | Diffed against `crop-research-20261111-v1` | Same 27 IDs. Only `unresolved_requirements` changed (added scope notes). |
| No silent activation | Counted states | 27/27 approval PENDING, enforcement DISABLED, no structured constraint; `get_enforceable_rules("sakha") == []`. |
| No fabricated sign-off | 102 matrix rows | `qualified_reviewer` and `signoff_reference` = "NONE RECORDED" on all 102. |
| Crop levels | Diffed against `crop-catalogue.v0.1-proposed.json` | Unchanged for all 12. |
| Wheat conflict | Read C01 and the conflict record | **Kept open** and explained: a modelling calendar (C01) vs an old-land advisory (W1); the 5-day gap has no shown cause. C01 is held. |
| Berseem purpose | Catalogue | **Stricter:** a new conflict `berseem-production-purpose` holds C07–C13. The forage profile stays `proposed`. |
| Sources exist | Fetched all 15 URLs | 7 open (200), 7 EKB rate-limited (429), 1 timeout. **2 are private ChatGPT-library team documents.** |
| C01 text | Fetched the GYGA page | JavaScript-rendered, so the "10–30 Nov" value can't be machine-checked. The conflict gate remains appropriate. |
| UH-001 | Real loader → Promise Test → generator → service | rejected (`sowing_before_protected_cut`); 28 May and 1 Jun `needs_review`; cut 2027-05-20 kept; maize harvest/release unknown; **0 feasible**. |

## Findings

| # | Severity | Finding | Action |
|---|---|---|---|
| F1 | P1 (integration) | Profile binding by crop + purpose existed only inside a demo tool. Yahya's backend still loads the UH-001 *planner fixture*, not this release. | Added `bind_profiles()` (refuses absent or ambiguous bindings; never broadens purpose) plus tests. Backend patch in the [handoff](../agronomy/yahya-kb-integration-handoff.md). |
| F2 | P1 (integration) | The frontend lists every planner profile `crop_id` as a choice. Nothing told it which crops are only review candidates and which are research records. | Added `catalogue_view()`, which keeps visible / offerable / enforced / feasible separate. Tests prove research crops have no profile and no offerable purpose. |
| F3 | P1 (science provenance) | C12, C25, C26 and C27 cite **only private team documents**. C12 and C27 are labelled scientific `CONDITIONAL`. | Not changed (Refaat's hash-pinned data). Flagged in the [matrix](agronomy-rule-matrix.md) for reclassification. Safe now because nothing is enforced. |
| F4 | P2 | `agricultural_kb.load_kb()` with no argument still loads the older `crop-research-20261111-v1`. | Documented. Integrators must call `load_reviewed_release()`. |
| F5 | Info | Berseem rules map to profile `berseem`, while a forage season binds `berseem-forage-proposed`. Even after future sign-off, forage berseem gets no rules until mapped. | Conservative, documented for Refaat and Yahya. |

**No P0 defect was found.** There's no false feasibility, no wrong enforcement, no broken loader and no invented
dates. The fixes are additive (F1, F2). No KB data, rule, approval or planner engine code was changed.

## Twelve crops

| Crop | Level | Offerable for | Notes |
|---|---|---|---|
| Wheat, grain maize, grain sorghum | review candidate | grain | Rules pending. Wheat's C01 is held by a conflict. |
| Berseem | runtime profile + proposal | forage (proposal only) | Refaat's purpose `forage_or_seed_requires_review`. C07–C13 held. Seed unsupported. |
| Rice, faba bean | review candidate | grain | Rice also needs a legal-permission field fact. Faba has no harvest date. |
| Sugar beet | review candidate | sugar | Release depends on factory delivery (unknown). |
| Egyptian cotton | review candidate | fibre | Picking count and stalk clearing unknown. Not the first harvest. |
| Watermelon, strawberry | research record | — | National evidence only or poor local fit. Never a profile. |
| Cantaloupe, harankash | research record | — | Cultivar group or species unresolved. Never a profile. |

## Winter-year and date logic

- **Convention.** The planner orders `summer-Y` before `winter-Y`, and `winter-Y` starts in Y. The adapter maps
  July–December to Y and January–June to Y+1 (`winter-start-year-v1-proposed`).
- **Edge cases.** Leap-day and cross-slot windows are reported, never guessed. A rule built for different season
  labels is `not_applicable` (test `test_wrong_season_year_never_applies_a_rule`).
- **Protected cut.** The 20 May cut is preserved, and a protected cut never sets a release date.

## Must not claim

- That any rule or crop is agronomically approved, certified or validated.
- That any plan is `feasible` for UH-001.
- That berseem forage, rice legality, beet delivery, cotton clearing, faba harvest or field release are known.
- That climate results change feasibility.
