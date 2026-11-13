"""Pure standalone orchestration; no persistence, server identity, weather or ML."""

from . import constraints
from ._types import KnowledgeBase, PlanningResult, ScenarioSnapshot, SearchPolicy
from .generate import _generate_prepared, authorized_scope


def display_group(candidate):
    # A bare profile alias or nearby date is not a new farming decision.
    preferences = tuple((check.season_ids, check.outcome,
                         check.explanation.params.get("window_start"), check.explanation.params.get("window_end"))
                        for check in candidate.evaluation.checks if check.effect == "preference"
                        and check.outcome in ("pass", "fail"))
    return (tuple((s.crop_id.value, s.purpose.value) for s in candidate.plan), candidate.direct_season_ids, preferences)


def plan(snapshot: ScenarioSnapshot, kb: KnowledgeBase, policy: SearchPolicy) -> PlanningResult:
    scope = authorized_scope(snapshot, kb, policy)
    current = constraints.evaluate(snapshot.input.seasons, snapshot, kb)
    generated = _generate_prepared(snapshot, kb, policy, scope)
    feasible, groups = [], set()
    for candidate in generated.candidates:
        if candidate.evaluation.status == "feasible":
            group = display_group(candidate)
            if group not in groups and len(feasible) < 2:
                feasible.append(candidate)
                groups.add(group)
    return PlanningResult(current, tuple(feasible),
        tuple(c for c in generated.candidates if c.evaluation.status == "needs_review"),
        tuple(c for c in generated.candidates if c.evaluation.status == "rejected"),
        generated.search, generated.exclusions, scope, kb.data_release)
