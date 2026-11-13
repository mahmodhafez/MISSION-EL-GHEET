"""Private immutable evaluator views, NOT shared schemas or loader definitions.

Replace/bind these at the boundary when Yahya publishes meg_core.contracts.
Refaat's loader supplies reviewed, scoped rule data; this module performs no I/O.
Only explicit Python predicates are supported, never expressions from a release.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import Generic, Literal, Mapping, TypeVar

T = TypeVar("T")
Scalar = str | int | float | bool
Outcome = Literal["pass", "fail", "unknown", "not_applicable"]
Effect = Literal["hard", "review", "preference"]
RequiredFor = Literal["planning", "explanation", "etc"]
PlanStatus = Literal["feasible", "rejected", "needs_review"]
FIELD_UNKNOWN_CODES = (
    "profile_applicability_unverified", "cultivar_availability_unknown",
    "soil_suitability_unknown", "irrigation_availability_unknown",
    "sorghum_local_eligibility_open", "crop_stages_unavailable", "kc_unavailable",
)


@dataclass(frozen=True)
class SourceRef:
    source_id: str
    locator: str


@dataclass(frozen=True, kw_only=True)
class Fact(Generic[T]):
    value: T | None
    unknown_reason: str | None
    origin: str
    evidence_status: Literal["verified", "proposed", "open"]
    confirmation_status: Literal["confirmed", "confirmed_unknown", "unconfirmed"]
    unit: str | None = None
    source_refs: tuple[SourceRef, ...] = ()
    method: str | None = None


@dataclass(frozen=True, kw_only=True)
class SeasonInput:
    season_id: str
    order: int
    # Private normalized slot key: winter-YYYY is the winter START year.
    season_label: str
    crop_id: Fact[str]
    purpose: Fact[str]
    profile_id: Fact[str]
    sowing_date: Fact[date]
    harvest_or_cut_date: Fact[date]
    crop_end_exclusive: Fact[date]
    release_date: Fact[date]
    preparation_days_after_release: Fact[int]


@dataclass(frozen=True)
class Commitment:
    commitment_id: str
    season_id: str
    kind: Literal["crop", "purpose", "occupation_through", "harvest_or_cut_date"]
    protected_value: Fact[str]


@dataclass(frozen=True)
class ProductionRequirement:
    requirement_id: str
    season_ids: tuple[str, ...]
    quantity: Fact[float]
    hard: bool


@dataclass(frozen=True, kw_only=True)
class ScenarioInput:
    seasons: tuple[SeasonInput, ...]
    site_id: str
    field_id: str
    commitments: tuple[Commitment, ...] = ()
    # Flattened agricultural context only. An adapter supplies these from soil,
    # irrigation, cultivar and management facts; no forecast slot exists.
    field_facts: tuple[tuple[str, Fact], ...] = ()
    production_requirements: tuple[ProductionRequirement, ...] = ()
    journey: Literal["check", "explore"] = "check"
    exploration: tuple[ExplorationChoice | DateRangeChoice, ...] = ()
    exploration_confirmed: bool = False
    scope_hash: str | None = None
    priority_order: tuple[str, ...] = ("minimize_changes",)
    independent_facts: tuple[IndependentFact, ...] = ()
    authorized_template_ids: tuple[str, ...] = ()
    hypothetical_template_ids: tuple[str, ...] = ()
    pending_scope_issues: tuple[ScopeIssue, ...] = ()


@dataclass(frozen=True, kw_only=True)
class ScenarioSnapshot:
    input: ScenarioInput
    data_release: str


@dataclass(frozen=True)
class Profile:
    profile_id: str
    crop_id: str
    purpose: str
    source_refs: tuple[SourceRef, ...] = ()
    evidence_status: Literal["verified", "proposed", "open"] = "open"


@dataclass(frozen=True)
class Condition:
    path: str
    expected: Scalar
    unit: str | None = None
    method: str | None = None


@dataclass(frozen=True, kw_only=True)
class Rule:
    rule_id: str
    rule_version: str
    profile_id: str
    topic: str
    source_refs: tuple[SourceRef, ...] = ()
    evidence_status: Literal["verified", "proposed", "open"] = "open"
    effect: Effect = "hard"
    required_for: RequiredFor = "planning"
    applicability: tuple[Condition, ...] = ()


@dataclass(frozen=True, kw_only=True)
class FactRule(Rule):
    path: str
    expected: Scalar
    operator: Literal["eq", "le", "ge"] = "eq"
    unit: str | None = None
    method: str | None = None
    unknown_code: str = "profile_applicability_unverified"


@dataclass(frozen=True, kw_only=True)
class SowingWindowRule(Rule):
    """Resolved inclusive dates; preference windows cannot establish eligibility."""
    start: date
    end: date


@dataclass(frozen=True, kw_only=True)
class CalendarRule(Rule):
    """An approved EXACT calendar, never an elapsed-duration extrapolation."""
    sowing_date: date
    harvest_or_cut_date: date
    crop_end_exclusive: date
    release_date: date


@dataclass(frozen=True, kw_only=True)
class PreparationRule(Rule):
    days: int
    next_profile_id: str


@dataclass(frozen=True, kw_only=True)
class RotationRule(Rule):
    allowed_predecessors: tuple[str, ...]


MANDATORY_TOPICS = (
    "identity_purpose", "local_cultivar_field_fit", "sowing_support",
    "harvest_crop_end_release", "transition_preparation", "irrigation_constraints",
    "protected_commitments", "hard_production_requirements_if_present",
)


@dataclass(frozen=True, kw_only=True)
class KnowledgeBase:
    data_release: str
    profiles: tuple[Profile, ...] = ()
    rules: tuple[Rule, ...] = ()
    required_planning_topics: tuple[str, ...] = MANDATORY_TOPICS
    templates: tuple[PlantingTemplate, ...] = ()


@dataclass(frozen=True)
class Explanation:
    code: str
    params: Mapping[str, Scalar | None]
    source_refs: tuple[SourceRef, ...]

    def __post_init__(self):
        object.__setattr__(self, "params", MappingProxyType(dict(self.params)))


@dataclass(frozen=True)
class RuleEvaluation:
    rule_id: str
    rule_version: str
    effect: Effect
    required_for: RequiredFor
    outcome: Outcome
    season_ids: tuple[str, ...]
    commitment_ids: tuple[str, ...]
    explanation: Explanation
    missing_input_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanEvaluation:
    status: PlanStatus
    checks: tuple[RuleEvaluation, ...]
    preserved_commitment_ids: tuple[str, ...]
    assumptions: tuple[Explanation, ...] = ()
    # The server must bind the actual current/candidate ref. Do not attach a
    # baseline's identity to a candidate or fabricate server IDs in pure code.
    plan_ref: None = field(default=None, init=False)


# Milestone 2 private views: no public Pydantic/HTTP contract is defined here.
@dataclass(frozen=True)
class ExplorationChoice:
    choice_id: str
    season_id: str
    field: Literal["crop_id", "profile_id", "sowing_date"]
    allowed_values: tuple[str, ...]


@dataclass(frozen=True)
class DateRangeChoice:
    """Explicit farmer-authorized inclusive range, traversed lazily."""
    choice_id: str
    season_id: str
    start: date
    end: date
    step_days: int = 1
    field: Literal["sowing_date"] = field(default="sowing_date", init=False)


@dataclass(frozen=True)
class IndependentFact:
    season_id: str
    field: str
    # Adapter-confirmed independence within this scope, subject to these inputs
    # remaining unchanged. next.* names refer to the outgoing transition.
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class PlantingTemplate:
    template_id: str
    profile_id: str
    season_label: str
    sowing_date: date
    source_refs: tuple[SourceRef, ...]
    harvest_or_cut_date: date | None = None
    crop_end_exclusive: date | None = None
    release_date: date | None = None
    template_version: str = "1"
    runtime_status: Literal["review", "approved", "disabled"] = "review"
    applicability: tuple[Condition, ...] = ()


@dataclass(frozen=True)
class CatalogueChoice:
    choice_id: str
    season_id: str
    field: Literal["crop_id", "profile_id", "sowing_date"]
    allowed_crop_ids: tuple[str, ...]


@dataclass(frozen=True)
class ScopeIssue:
    code: str
    choice_ids: tuple[str, ...]
    season_ids: tuple[str, ...]
    missing_input_paths: tuple[str, ...] = ()
    source_refs: tuple[SourceRef, ...] = ()
    kind: Literal["blocked", "excluded"] = "blocked"


@dataclass(frozen=True, kw_only=True)
class ScopeRequest:
    snapshot: ScenarioSnapshot
    choices: tuple[ExplorationChoice | DateRangeChoice, ...] | None = None
    catalogue_choices: tuple[CatalogueChoice, ...] = ()


@dataclass(frozen=True)
class ScopePreview:
    data_release: str
    scope_hash: str
    choices: tuple[ExplorationChoice | DateRangeChoice, ...]
    available_crop_ids: tuple[str, ...]
    protected_commitments: tuple[Commitment, ...]
    missing_input_paths: tuple[str, ...]
    issues: tuple[ScopeIssue, ...]


@dataclass(frozen=True, kw_only=True)
class SearchPolicy:
    raw_budget: int = 256
    ordering_version: str = "minimal-edits-v1-proposed"
    max_choice_records: int = 32
    max_values_per_choice: int = 32


@dataclass(frozen=True)
class Change:
    season_id: str
    field: str
    before: Fact
    after: Fact
    direct: bool


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    kind: Literal["timing_variant", "crop_change", "combined"]
    plan: tuple[SeasonInput, ...]
    changes: tuple[Change, ...]
    evaluation: PlanEvaluation
    choice_ids: tuple[str, ...]
    direct_season_ids: tuple[str, ...]
    template_ids: tuple[str, ...]
    source_refs: tuple[SourceRef, ...]
    tradeoffs: tuple[Explanation, ...] = ()


@dataclass(frozen=True)
class SearchSummary:
    status: Literal["complete", "incomplete"]
    raw_count: int
    materialized_count: int
    evaluated_count: int
    rejected_count: int
    needs_review_count: int
    feasible_count: int
    duplicate_count: int
    excluded_count: int
    blocked_count: int
    scope_choice_ids: tuple[str, ...]
    uninstantiated_choice_ids: tuple[str, ...]
    limit_reason: str | None
    policy_version: str
    policy_approval: str = "pending_team_review"


@dataclass(frozen=True)
class GenerationResult:
    candidates: tuple[Candidate, ...]
    search: SearchSummary
    exclusions: tuple[ScopeIssue, ...]
    scope: ScopePreview


@dataclass(frozen=True)
class PlanningResult:
    current: PlanEvaluation
    feasible_alternatives: tuple[Candidate, ...]
    review_investigations: tuple[Candidate, ...]
    rejected_candidates: tuple[Candidate, ...]
    search: SearchSummary
    exclusions: tuple[ScopeIssue, ...]
    scope: ScopePreview
    data_release: str
