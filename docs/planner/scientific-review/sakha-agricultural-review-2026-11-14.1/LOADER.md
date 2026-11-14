# Loading the scientific review in the planner

The repository import root is `packages/meg-core/src`. The imported loader, schema, frozen KB and research files came from Refaat’s supplied `original/` directory. The new composition module sits outside the pure `meg_core.planner` package. Use Python 3.12 with its standard library.

## Normal entry point

Run this from the **repository root**. An application can install or configure the same import root at startup.

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path("packages/meg-core/src").resolve()))
from meg_core.agricultural_release import load_reviewed_release

release = load_reviewed_release()
status = release.agricultural.get_status(locality="sakha")
print(release.version, status["locally_approved_rules"], status["enforceable_rules"])
print(release.agricultural.get_rules(crop_id="wheat", view="supported")[0]["rule_id"])

built = release.for_planner(
    site_id="sakha",
    season_labels=("winter-2026", "summer-2027", "winter-2027", "summer-2028"),
    conditions={},  # no matching farm qualifiers supplied
)
print(len(built.catalogue.records), len(built.kb.profiles), len(built.kb.rules))
```

For this release the outputs are `sakha-agricultural-review-2026-11-14.1 0 0`, `C01` and `12 9 0`. The wrapper checks the manifest against a pinned SHA-256 and verifies each data document before assembly. The original schema and linked-evidence checks still run. A hash identifies the release contents. A qualified reviewer’s dated record is a separate requirement.

| Interface | Meaning |
|---|---|
| `load_reviewed_release(directory=RELEASE_DIR) -> ReviewedRelease` | Loads this pinned package. The directory can relocate identical files. A missing file raises `KBError("KB_UNAVAILABLE", ...)`. A hash mismatch raises `SOURCE_INTEGRITY`. |
| `release.for_planner(*, site_id, season_labels, conditions=None) -> CatalogueKB` | Maps a query to the real loader and catalogue builder. Only site `sakha` is covered. An unreviewed site raises `OUTSIDE_RELEASE_SCOPE`. Labels are a tuple of normalized season-year strings. Conditions are confirmed string pairs for this single query. |
| `release.agricultural` | Original `AgriculturalKB` API. `get_crops()`, `get_crop(id)`, `get_sources(id=None)`, `get_evidence(id=None)` and rule views return detached JSON-compatible values. The four historical crop profiles remain here. The 12 crop records belong to `release.catalogue.records`. |
| `get_rules(crop_id=None, locality=None, conditions=None, view="all")` | All arguments are keyword-only. Views are `all`, `supported`, `unverified`, `pending`, `approved` and `enforceable`. A known conflicting condition excludes the row. A missing condition remains visible in the all/pending views with a blocker. |
| `get_approved_rules(**query)`, `get_enforceable_rules(*, locality, **query)`, `get_pending_rules(**query)`, `get_status(locality=..., conditions=...)` | `supported` requires verified rule and linked evidence. `approved` means a local sign-off is recorded. `enforceable` also requires locality, conditions, enabled structured constraint and closure of review requirements. See individual `enforceability.blockers`. |
| `built.kb`, `built.unmapped`, `built.catalogue` | `kb` is the real planner `KnowledgeBase`. `unmapped` reports only rejected mappings among rows submitted to the adapter. Here the loader supplies zero rows, so consult `get_pending_rules()` for the original 27 blockers. |

`from agricultural_kb import load_kb` preserves the original interface. `load_kb()` reads frozen `crop-research-20261111-v1` for established callers. `load_kb(RELEASE_DIR / "agricultural_kb.json")` reads the reviewed four-profile document. Use the wrapper above to bind the dated 12-crop catalogue and its digest.

## Planner binding

Use the same `release.version` for the stored snapshot and the planner `data_release`. Resolve a season to one crop/profile/purpose combination. The forage proposal’s exact profile ID is `berseem-forage-proposed`. A generic `berseem` profile has an unresolved end-use field. The four research-only fruits never enter the runtime profile list.

`constraints.evaluate(snapshot.input.seasons, snapshot, built.kb)` runs the Promise Test. For exploration, the actual API is `prepare_scope(ScopeRequest(...), built.kb)`, followed by the farmer’s explicit scope confirmation and the preview’s bound `scope_hash`. Use `generate(confirmed_snapshot, built.kb, SearchPolicy())` or `service.plan(confirmed_snapshot, built.kb, SearchPolicy())`. The included UH-001 command exercises all of these paths against the stored fixture.

The dated review keeps the original `agricultural-kb/1` JSON schema and the catalogue’s `crop-catalogue/0.1-proposed` schema. All 27 source definitions, IDs, evidence rows and historic statuses are retained. Each rule receives a scoped interpretation and a next action in `unresolved_requirements`. The parent research package is preserved for reproducibility. In the versioned data directory, `review.json` holds row-level review decisions, the 14-assertion crosswalk, all eight assessments and a source-access register. Its schema identifier is `sakha-review-dossier/1`. The dossier is an evidence record. No field in it is translated into a planner rule.

## Decisions for the next signed release

1. Refaat and the qualified local reviewer must record the source and year, cultivar, purpose, parcel conditions, applicability reviewer/reference and a separate signed, dated approval. Confirm that a proposed predicate represents an advisory, preference or hard exclusion with the intended strength. The current adapter assigns `effect="hard"` to mapped rules. A general preference must stay out of that path until there is an agreed representation.
2. Yahya and Refaat should bind conditions to the correct season/profile and agree on units, `field.<key>` paths, source references and `winter-start-year-v1-proposed`. A single global cultivar condition is insufficient for a four-crop field plan. Represent separate purpose-specific rules for forage and seed before clearing the berseem conflict.
3. Record actual crop end, first free day and preparation for each transition. Occupation uses half-open intervals. When release and preparation are known, test `next_sowing >= release_date + preparation_days`. Dates supplied by trials or maturity tables cannot fill these operational fields without a reviewed mapping.
4. For approval, update the linked local scope and structured constraint, clear resolved requirements individually and bind the qualified record with `approval_scope_sha256(rule, evidence, sources)`. Ship the decision as a new reviewed release and retest. This hash alone cannot authenticate the reviewer.
5. Amr and Yahya can decide whether to support pre-horizon field history, alternative purposes and separate crop-specific operational inputs in the shared contracts. The four-season engine only evaluates represented facts and approved predicates. The current backend interface and search policy have not been changed.
