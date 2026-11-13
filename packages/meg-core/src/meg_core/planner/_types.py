"""Private immutable evaluator views, NOT shared schemas or loader definitions.

Replace/bind these at the boundary when Yahya publishes meg_core.contracts.
Refaat's loader supplies reviewed, scoped rule data; this module performs no I/O.
Only explicit Python predicates are supported, never expressions from a release.
"""

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


@dataclass(frozen=True, kw_only=True)
class ScenarioSnapshot:
    input: ScenarioInput
    data_release: str


@dataclass(frozen=True)
class Profile:
    profile_id: str
    crop_id: str
    purpose: str


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
