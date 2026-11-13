# Planner research integration — Karim and Yahya

**Read this if…** you want to know how the planner research fits the approved specs and what's still unresolved.

Status: Current,  · Owner: Karim / Yahya. Last reviewed .

. Documentation integration only. Read [PLANNER_SPEC.md](planner-spec.md) and [AGRONOMY_EVIDENCE.md](agronomy-evidence.md) alongside this review. Research completion does not approve new modelling conventions, authorize implementation or establish application correctness.

## Provenance and authority

Both source documents were copied without content changes from:

`C:\Users\Amr Hany\Documents\Codex\\mission-el-gheet-four-season-planner-3\outputs\docs`

| File | Source and repository SHA256 at integration |
| --- | --- |
| PLANNER_SPEC.md | `2e85a42e1165ee8801e15cebb456db007d40d89eeb35316146a167011a7b0c4e` |
| AGRONOMY_EVIDENCE.md | `7e732ea45fedba65972b73444842e6233df5c98776b3033b6fbd617b36838dce` |

Source locators, evidence labels, URLs and audit dates remain intact. The ledger's source-verification claims are inherited from that research pass; this integration did not retrieve its papers, independently audit those claims, extract the validation archive or reproduce the NASA/ML results. A versioned source manifest with retrieval metadata, hashes where available and terms status is still a delivery task.

The approved contracts remain authoritative and unchanged. This review also preserves the pre-existing README, frontend brief and status edits. No application files, dependencies, commits or Git history were changed.

## Compatibility review

| Approved document | Comparison and disposition |
| --- | --- |
| [SCIENCE.md](../science/science.md), §§1–6 | Same half-open occupation, preparation inequality, hard/unknown precedence, scope checks, independent replay/ML and optional ETc gates. New local sorghum observations extend the older evidence record; they do not resolve local eligibility. The older statement about the Nubaria trial remains historical evidence, not a statement that no Sakha research exists. Earlier pending-locality wording is already superseded by HANDOFF. |
| [ARCHITECTURE.md](../backend/architecture.md) | Pure bounded planner, trusted catalogue, immutable inputs, separate replay and five-endpoint first slice agree. No new service, database or dependency is needed by the handoff. Proposed search details need review below. |
| [API_CONTRACTS.md](../backend/api-contracts.md), §§1–6 | Existing Fact, Candidate, RuleEvaluation, statuses and search fields can represent the handoff. P0 conflict is HTTP 200 with rejected status, not 422. Unsupported candidate endpoints are present null Facts; proposed facts remain unconfirmed until explicit confirmation. Confirmed snapshot nulls require confirmed_unknown. No incompatible field or enum addition was identified. Proposed explanation codes/parameters still need registration and bilingual templates. |
| [REFERENCE_SCENARIO.md](../product/reference-scenario.md), §§1–6 | Exact dates, protected commitments, R1/R2 review, zero feasible alternatives, S4 uninstantiated choice, inapplicable forecast and rejected review-draft saving agree. Applying seven days to all three transitions and setting crop end equal to assumed release are explicit fixture interpretations, not new agricultural facts. |
| [project status](../status/README.md) | Research handoff is now available; backend and scientific acceptance remain unimplemented/unrun. Existing coding/start gates remain in force. No second evidence-backed feasible scenario has been delivered. |

No blocking contradiction requires changing an approved specification to retain these research documents. The following unresolved decisions block promoting the corresponding proposals to approved implementation semantics; they do not block copying or reviewing the research.

## Review gates and ambiguities

1. **Fixture date mapping — Karim/Yahya with Refaat.** Explicitly encode `p1=p2=p3=7`, `p4=null` with a reason that no successor exists, and `e=h+1=r` only for unchanged UH-001 fixture calendars. The original fixture states a same-field seven-day assumption without separate transition rows. Real intake must establish each transition's scope; neither the cut itself nor a maturity range proves release. R1/R2 invalidate S2 harvest, crop end and release; do not infer them from the protected requirement or retain the September endpoints.
2. **Season labels — Yahya/Karim with Amr.** The API requires consecutive labels but does not prescribe their grammar. Agree a canonical label/site-calendar mapping before implementing parsing; translated display text must not determine identity. Winter 2026/27 precedes summer 2027. No new wire field is approved here.
3. **Search policy — Karim with Amr/Refaat.** The 256 raw-tuple budget, lexicographic edit counts, meaningful display grouping, canonical ID derivation and limit-reason precedence are research proposals. Benchmark and version them before adoption. Four composite choices per slot mean 255 alternatives; four crop IDs do not bound the crop/profile/date product to 255. Count blocked/duplicate tuples against the raw budget, while evaluated_count counts unique evaluated materialized alternatives only. Exactly reaching the budget is not by itself incomplete: determine whether another raw tuple remains. Evidence-blocked branches remain incomplete even after raw enumeration is exhausted.
4. **Search metadata — Karim/Yahya.** The existing API can carry the proposed meanings without structural changes, but their precise semantics need coordinated review. With full research enumeration UH-001 evaluates two alternatives and reports the S4 choice uninstantiated. With enumeration deferred, use incomplete/enumeration_deferred; do not claim that R1/R2 were evaluated. Stable ordering is required for explanations and review/rejected lists as well as feasible cards.
5. **Replay — Yahya/Refaat, later milestone.** The research chooses exclusive shared_blocks.end_date, full common ET0/Tmax coverage and fixed whole-year horizons; the API leaves those details to versioned policies. Review them before emitting numerical comparisons. Leap-day exclusion must be symmetric. SCIENCE's midpoint Kc discretization is still proposed and explicitly awaits approval; the planner's wording about an approved curve does not grant that approval. No crop-specific ETc is enabled by this integration.
6. **Evidence release — Refaat with Karim.** Verify applicability and resolve any source-scope differences before registering hard agricultural exclusions or endpoint mappings. Source metadata is incomplete until packaged. W1's conditional December extension, B1's qualitative sowing endpoints, maturity versus harvest, and trial-period versus first-free-day conventions must remain distinct. No precise date or salinity threshold may be invented to fill those gaps.

## Evidence classes to preserve

| Class | Examples | Permitted use |
| --- | --- | --- |
| Scientific observations | W3 historical wheat/maize calendars; B2 trial cut offsets; M3 June SC10 grain; M4 local cropping periods; S1 hybrid-888 trial | Scoped catalogue observations. No transfer to new years, fields, cultivars, cut promises or release dates without support. |
| Advisory guidance | W1 wheat preference, M1 May maize preference, M2 maturity metadata, S2 cultivar description | Explain preferences and prompt applicability review. June is not a hard maize prohibition; missing Giza 168 from a dated map is not a ban. |
| Verified mathematical/contract rules | One-field non-overlap, full preparation interval, exact protected commitments, structural date ordering and hard-failure precedence | Enforce calendar/commitment consistency using known facts or proven bounds. This is not field agronomic validation. No universal crop succession prohibition or numeric preparation default was established. |
| Fixture assumptions | Fictional UH-001, intended future dates, seven days, next-day release, clayey report and unknown field measurements | Conditional demonstrations only; farmer confirmation does not upgrade illustrative origin or scientific evidence. Synthetic positive fixtures remain separate from the Sakha release. |

## Verification performed in this integration

PowerShell independently evaluated 18 arithmetic assertions: exclusive-cut and preparation boundaries including zero/equality cases; P0 conflict; R1/R2 day shifts; the two later P0 transitions; the two S1 sorghum elapsed-day figures (97/102); the synthetic replay sum/difference; mm-hectare conversion; edge/pair counts; product count; leap-day inclusion; and the two synthetic downstream collision/equality cases. All passed.

| UH-001 quantity | Independently checked result |
| --- | --- |
| S1 release + preparation | 21 May + 7 days = 28 May 2027; preparation occupies 21–27 May inclusive |
| R1 / R2 | 13 / 17 days after baseline sowing; 0 / 4 days after the conditional boundary |
| P0 S2→S3 | Ready 28 September 2027, before 20 November sowing |
| P0 S3→S4 | Ready 3 May 2028, before 1 June sowing |
| Changed S2 endpoints | Unknown; later transition cannot be declared passing or conflicting from stale endpoints |

A separate finite enumeration model produced 255 unique alternatives for four composite values per slot, unchanged by permuted/duplicate allowed values. A five-value case produced 624 alternatives: 256 visited and 368 remaining under the proposed cap. For UH-001's discrete permissions, the product yields five raw alternatives: two S2-only investigations and three evidence-blocked S4-maize combinations. Thus the research expectation of evaluated_count=2, zero feasible alternatives and incomplete/uninstantiated_choices is consistent with that scope. The four-case hard-failure/required-unknown status truth table was evaluated separately. Neither model calls a repository planner.

Local-link scan covered 24 Markdown documents: all 98 Markdown-file link occurrences and the new cross-document evidence-gates anchor resolved. Fourteen existing unresolved non-Markdown occurrences point to ten unique local evidence paths documented in [EVIDENCE_ACCESS.md](../science/evidence-access.md); no provenance links were rewritten or archive contents extracted. Touched-document fences, table column counts, trailing whitespace and UTF-8 replacement-character checks passed; `git diff --check` passed. Cosmetic unmatched inline backticks in the source ledger were retained to preserve source bytes.

These are document, arithmetic and independent specification-model checks. They are **not application unit, API, integration, browser, agronomic or usability tests**. No runnable backend or test framework currently exists in the placeholder directories. Ranking/group selection, endpoint invalidation, actual rule coverage, generated schemas and stable application output remain untested. Historical ET0 and ML assertions were not rerun.

## Exact backend implementation sequence after authorization

1. **Yahya + Karim:** resolve the relevant review gates above with Amr and Refaat; retain existing implementation/start authorization gates. Establish executable v1 Pydantic models, trusted catalogue/source manifest, typed explanation registry and matching Arabic/English parameters. Generate OpenAPI and frontend types from those models. Preserve all four crops and explicit evidence gaps. Do not change approved interfaces without review.
2. **Karim, Yahya supports fixture validation:** author the first regression below against the real pure evaluator in `backend/app/planner/`, then implement only the evaluator, status reduction and required review checks to make it pass. Add structural/interval/lock/unknown boundary cases, including known conflicts across an unknown middle slot. No weather/ML/network dependency belongs in this evaluator.
3. **Yahya:** wire `GET /api/v1/catalogue`, `POST /api/v1/scenarios`, `GET /api/v1/scenarios/{id}`, `POST /api/v1/scenarios/{id}/confirmations`, then `POST /api/v1/promise-tests`. Persist immutable snapshots/results in SQLite; check versions, expected revisions and idempotency atomically. Exercise actual UH-001 HTTP 200 rejection and identical bilingual parameters, plus 422 structural inputs, 409 stale/lock writes and failed-save behavior. Connect the reviewed frontend to this real slice.
4. **Karim:** implement canonical permitted-choice enumeration, dependent-endpoint invalidation, four-season rechecking, deduplication and reviewed ranking/grouping policy. Extend UH-001 regression to R1/R2 needs_review with null S2 endpoints, evaluated_count=2 and the uninstantiated S4 choice. Test deterministic input permutations, budget boundaries, no-permission requests and isolated synthetic positive/cascade fixtures. **Yahya:** persist candidate references and require a new explicit confirmation/evaluation before selection can become current.
5. **Yahya + Refaat:** add prepared-data replay at the architecture's historical-evidence milestone, after mapping/coverage approval. Verify common blocks, leap/exclusion symmetry, units, optional metric unavailability and candidate-minus-baseline differences; run actual pinned numerical fixtures. No complete feasible scenario means no invented feasible comparison or water saving.
6. **Yahya with Karim/Amr:** integrate Evidence Card/review-draft save, feasible/current-only approval, revocation and version-bound audio at the accessible-completion milestone. Test P0 saving as decision_state=review_draft with plan_status=rejected. Keep optional forecast serving isolated; UH-001's fixed issue date makes the disputed sowings not_applicable. Record real application/browser results separately from this review.

### First runnable UH-001 regression to author

Proposed future target: `backend/tests/test_uh001.py::test_uh001_p0_preserves_cut_and_rejects_overlap`. After backend runtime/test setup is authorized and available, run from repository root:

```powershell
python -m pytest backend/tests/test_uh001.py::test_uh001_p0_preserves_cut_and_rejects_overlap -q
```

The file, evaluator callable and pytest environment do not exist yet; this command was **not run**. It is the first implementation acceptance target, not a claimed runnable deliverable from this documentation task.

Arrange a schema-validated, explicitly illustrative UH-001/v1 snapshot with fixed issue date , exact four seasons from REFERENCE_SCENARIO, all protected commitment IDs and pinned demo catalogue/rules. Use the declared transition mapping above. Exercise the actual evaluator with enumeration explicitly deferred in this first test. Assert:

- P0 status is rejected, with `sowing_before_protected_cut` parameters exactly `season_id=s2`, `sowing_date=2027-05-15`, `protected_cut_date=2027-05-20`; retain source locator and affected commitment/season references.
- Every protected commitment remains in preserved_commitment_ids; the confirmed input and protected 20 May cut are unchanged. Retention describes the obligation, not global calendar feasibility.
- The seven-day ready boundary is 28 May conditionally; no failure is fabricated on S2→S3 or S3→S4. Required soil, water, cultivar, calendar and sorghum unknowns coexist with rejection; stage/Kc/unknown forage quantity explanations do not masquerade as hard conflicts.
- feasible_alternatives is empty. Deferred search reports incomplete, evaluated_count=0 and enumeration_deferred; it does not fabricate reviewed candidates. Test full R1/R2 enumeration separately at step 4.
- Repeated evaluation has the same semantic checks/order/parameters apart from permitted generated IDs/timestamps. Both authored language templates consume the same typed parameters. Forecast and Evidence Card behaviors are later service tests, not assertions that the pure evaluator invokes those services.

Demonstrate the first test failing for the missing evaluator and then passing against real implementation; report exact results. Follow with the five-endpoint integration test and the full R1/R2 regression. A passing synthetic or UH-001 test establishes engineering behavior only, not a real feasible agronomic recommendation.
