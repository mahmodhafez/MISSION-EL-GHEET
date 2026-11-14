# Agricultural KB contract for Yahya

Contract `agricultural-kb/1`, research release `crop-research-20261111-v1`. The machine schema is `agricultural_kb/schema.json`. The offline loader uses the Python standard library and has no climate, solver or ML dependency. Its validated snapshot returns detached dictionaries/lists containing only JSON types; serialize with `json.dumps(value, allow_nan=False)`. `KBError.to_dict()` returns `{"error":{"code":string,"path":string,"message":string}}`. Do not treat a load failure or zero enforceable rules as evidence that a crop plan is feasible.

## Current evidence and provenance

The original `MISSION_EL_GHEET_Research_Package` was recovered from Downloads and crosschecked against its ZIP. Eight original CSV/Markdown files remain byte-identical under `sources/agriculture/`, with file and archive SHA256 in `MANIFEST.json`. The entire evidence register has 71 entries. The KB imports exactly the 27 crop entries E036–E062, mapped by explicit crop-rule tags C01–C27, not by row position or a new scientific assessment. Fifteen source/version records preserve URLs, titles, dates and locators. Private ChatGPT Library references remain locators to team documents; their accessibility is not inferred from a URL. Underlying journal PDFs are not bundled and were not fetched during this implementation. `source_opened` and `review_date` report the original research review, not a new source visit.

The crop IDs are `wheat`, `berseem`, `grain_maize`, `grain_sorghum`. Keep rule IDs C01–C27 and evidence IDs E036–E062 stable. C25–C27 reference all four crops. The loader never derives species, planting cutoffs or soil restrictions from a crop name. `research_context` preserves cultivar, geographic and seasonal context verbatim. The `parameters.source_text` and `parameters.units` preserve each proposed value verbatim, including trial ranges and unknowns. They are research parameters, not executable constraints; do not parse prose into planner bounds at request time.

## Public Python calls

| Call | Result |
|---|---|
| `load_kb(path=None)` | Validated `AgriculturalKB`; default JSON resolves relative to the package, not cwd. An explicit path is a file, not a directory. |
| `AgriculturalKB(document)` | Validate an in-memory JSON-compatible snapshot; primarily useful for reviewed release tooling/tests. |
| `kb.get_crops()` / `kb.get_crop(crop_id)` | Crop profiles with stable IDs, intended purpose and linked rule IDs. |
| `kb.get_rules(crop_id=None, locality=None, conditions=None, view="all")` | Rules with original evidence/approval fields plus computed `enforceability`. All arguments are keywords. |
| `kb.get_rules(view="supported", ...)` | Rule and linked evidence all VERIFIED. This is **scientific support only**. |
| `kb.get_rules(view="unverified", ...)` | Complement of supported, including conditional, derived, blocked and not-applicable evidence. |
| `kb.get_approved_rules(...)` | Explicit local sign-offs; a signed rule may still be disabled or inapplicable. |
| `kb.get_enforceable_rules(locality="sakha", conditions={...}, crop_id=...)` | The only view suitable for selecting planner constraints; returns `[]` in the delivered release. |
| `kb.get_pending_rules(...)` | All rules not enforceable for the query, including rejected/revoked/inapplicable rules with reasons. |
| `kb.get_evidence(evidence_id=None)` / `kb.get_sources(source_id=None)` | One referenced record or all records when omitted. |
| `kb.get_status(locality="sakha", conditions={...})` | Schema/version, scientific counts, local sign-off/enforceable counts and per-rule review blockers. |
| `approval_scope_sha256(rule, evidence, sources)` | Digest of rule content except approval plus linked evidence/sources; used by a reviewed approval workflow. |

See the runnable Python block in `START_HERE.md` and `python -m examples.backend_p0`. The example combines pending rules, evidence, historical weather, ET0, descriptive climatology and climate QC/provenance. `python -m agricultural_kb --kb knowledge_base/agricultural_kb.json --locality sakha` prints status. Invalid KB input produces a JSON error and exit code 2. Error codes include `KB_UNAVAILABLE`, `INVALID_JSON`, `INVALID_KB`, `DUPLICATE_ID`, `BROKEN_REFERENCE`, `INCOMPLETE_APPROVAL`, `INCOMPLETE_APPLICABILITY`, `STALE_APPROVAL`, `UNKNOWN_ID`, `INVALID_QUERY`.

## Four independent decisions

1. `scientific_status`: `VERIFIED`, `CONDITIONAL`, `DERIVED`, `UNVERIFIED`, `NOT APPLICABLE`, `BLOCKED`. The first 27 records preserve the ledger exactly: 18/4/1/3/1/0 respectively.
2. `local_applicability.status`: `PENDING`, `APPLICABLE`, `NOT_APPLICABLE`. `locality_ids` identifies **review scope**, not proof of applicability. All records are scoped for Sakha review; C22 is explicitly not applicable to grain because its source concerns forage. Even a Sakha trial does not approve a general rule. `APPLICABLE` requires a named reviewer and reference.
3. `approval.status`: `PENDING`, `APPROVED`, `REJECTED`, `REVOKED`. An approved record requires `reviewer`, real ISO `approved_on`, `reference` and `scope_sha256`. The digest binds the exact rule, conditions, parameters and linked evidence/source metadata. Editing them invalidates the sign-off; never regenerate the digest as a substitute for review.
4. `enforcement.status`: explicit `DISABLED` or `ENABLED`, separate from computed `enforceability.status` (`BLOCKED` or `ENFORCEABLE`). Caller-supplied `enforceable` fields are rejected. Computation requires all scientific evidence VERIFIED, linked sources/evidence, local applicability APPLICABLE, APPROVED sign-off, exact locality/condition match, no unresolved requirements, ENABLED activation and a structured constraint. There is no fallback from missing approval to evidence status.

The shipped result is `NO_LOCAL_SIGN_OFF`. Other status values are `NO_APPLICABLE_APPROVED_RULES` and `HAS_ENFORCEABLE_RULES`. These statuses describe the returned rule set, not whole-plan feasibility. Missing critical commitments or field-release information must remain unresolved even when other future rules become enforceable.

## Filtering and constraint semantics for approval

The only current locality ID is lowercase `sakha`; unknown IDs produce a structured error. There is no implicit locality inheritance, nearest-site mapping or transfer from Upper Egypt. With no locality query, records remain available for research but none is enforceable. `conditions` maps explicit case-sensitive string keys to observed string values. In a rule, each key maps to a nonempty list of allowed strings. All required keys must match (AND between keys, OR within a list). Supplied conflicting values filter the rule out. Missing values keep the rule visible but blocked with `missing_condition:<key>`. A query may have extra context keys. Crop filtering uses exact crop IDs and includes shared rules.

The contract supports three structured constraint forms for **future signed releases**. None is populated in the delivered KB:

| Kind | Fields and proposed meaning |
|---|---|
| `numeric_range` | `field,lower,upper,units`: finite inclusive bounds, lower ≤ upper; booleans are rejected as numbers. |
| `calendar_window` | `field,start_month_day,end_month_day`: valid MM-DD bounds, inclusive, cross-year window when start > end; Feb 29 must use the planner's explicit year/leap policy. |
| `category_set` | `field,allowed`: nonempty distinct allowed strings, exact match. |

The loader selects constraints; it does not execute them, construct plans or infer field availability. **Yahya must approve** field names, units, date/leap and occupancy semantics, conditional requirements, the trusted reviewer workflow, response/error handling and the rule versions used by the planner. The existing climate contract uses `[sow_date,crop_end_exclusive)` and does not equate maturity, final cut or crop end with first free field day. These distinctions need a local decision before a scheduling rule can be activated.

## Review and publication workflow

Create a new KB version after agronomic review; preserve this research release. Record cultivar/purpose, locality, applicability conditions, source sections, and the chosen parameter interpretation. Resolve each documented requirement with evidence, review the structured constraint with Yahya, obtain named dated agronomic sign-off, then explicitly enable the constraint and calculate the scope digest of that reviewed content. Reject/revoke decisions leave the rule visible but blocked. Approval entries are repository records, **not cryptographic identity authentication**: protect write access and review releases. Do not accept a farmer-supplied JSON document as an approval authority.

To reproduce the initial research-only JSON, run `python -m agricultural_kb.build --output outputs/rebuilt_kb.json`. This command checks source hashes, crosslinks and original Pending sign-offs, refuses overwriting its destination, and never promotes rules. It will not import later approval decisions automatically. Tests use clearly marked synthetic approvals only; they do not change the delivered data.

The original research reports contain proposed acquisition coordinates and earlier proposed heat/occupancy conventions. They remain historical evidence. The frozen climate runtime contract remains authoritative for its 31.10/30.95 point, 4.96 m grid elevation, threshold comparison and release methodology. No proposed research instruction changes the verified climate release.
