"""Bounded, generic search. Agricultural statuses come only from Promise Test."""

from dataclasses import replace

from . import constraints
from ._canonical import context, digest, plan_key
from ._enumerate import raw_combinations
from ._materialize import materialize
from ._types import (
    Candidate, Change, DateRangeChoice, GenerationResult, KnowledgeBase, ScopeIssue,
    ScopeRequest, ScenarioSnapshot, SearchPolicy, SearchSummary,
)
from ._validation import FACT_FIELDS, require, validate
from .scope import prepare_scope, validate_policy


def authorized_scope(snapshot, kb, policy):
    validate_policy(policy)
    require(isinstance(snapshot, ScenarioSnapshot), "snapshot_required", "snapshot")
    require(hasattr(snapshot.input, "seasons"), "scenario_input_required", "snapshot.input")
    validate(snapshot.input.seasons, snapshot, kb)
    scope = prepare_scope(ScopeRequest(snapshot=snapshot), kb)
    require(len(scope.choices) + len(scope.issues) <= policy.max_choice_records, "choice_record_limit", "scope.choices")
    for choice in scope.choices:
        if not isinstance(choice, DateRangeChoice):
            require(len(choice.allowed_values) <= policy.max_values_per_choice, "choice_value_limit", choice.choice_id)
    if scope.choices or scope.issues:
        require(snapshot.input.journey == "explore", "exploration_requires_explore_journey", "snapshot.input.journey")
        require(snapshot.input.exploration_confirmed, "exploration_not_confirmed", "snapshot.input.exploration_confirmed")
        require(snapshot.input.scope_hash == scope.scope_hash, "confirmed_scope_mismatch", "snapshot.input.scope_hash")
    return scope


def candidate_order(candidate, snapshot):
    canonical = plan_key(candidate.plan)
    if "minimize_changes" not in snapshot.input.priority_order:
        return (canonical,)
    decisions, unknown_displacements, days = 0, 0, 0
    for old, new in zip(snapshot.input.seasons, candidate.plan):
        if old.season_id not in candidate.direct_season_ids:
            continue
        decisions += int(old.crop_id.value != new.crop_id.value or old.profile_id.value != new.profile_id.value)
        if old.sowing_date.value != new.sowing_date.value:
            decisions += 1
            if old.sowing_date.value is None or new.sowing_date.value is None:
                unknown_displacements += 1
            else:
                days += abs((new.sowing_date.value - old.sowing_date.value).days)
    return (len(candidate.direct_season_ids), decisions, unknown_displacements, days, canonical)


def _generate_prepared(snapshot, kb, policy, scope):
    iterator = iter(raw_combinations(snapshot.input.seasons, scope.choices))
    candidates, exclusions = {}, list(scope.issues)
    blocked_ids = {cid for issue in scope.issues if issue.kind == "blocked" for cid in issue.choice_ids}
    raw_count = duplicate_count = excluded_count = blocked_count = 0
    baseline_key = plan_key(snapshot.input.seasons)
    evidence_key = digest((kb.data_release, tuple(sorted(kb.profiles, key=lambda p: p.profile_id)),
                           tuple(sorted(kb.rules, key=lambda r: r.rule_id)),
                           tuple(sorted(kb.templates, key=lambda t: t.template_id)),
                           tuple(sorted(kb.required_planning_topics))))
    identity_context = digest((context(snapshot), evidence_key, policy.ordering_version))
    for _ in range(policy.raw_budget):
        raw = next(iterator, None)
        if raw is None:
            break
        raw_count += 1
        materialized = materialize(raw, snapshot, kb)
        if isinstance(materialized, ScopeIssue):
            exclusions.append(materialized)
            if materialized.kind == "blocked":
                blocked_count += 1
                blocked_ids.update(materialized.choice_ids)
            else:
                excluded_count += 1
            continue
        plan, template_ids, refs, tradeoffs = materialized
        key = plan_key(plan)
        ids = tuple(sorted({cid for _, edits in raw for _, _, choice_ids in edits for cid in choice_ids}))
        if key in candidates or key == baseline_key:
            duplicate_count += 1
            if key in candidates:
                prior = candidates[key]
                candidates[key] = replace(prior, choice_ids=tuple(sorted(set(prior.choice_ids) | set(ids))))
            continue
        direct = {(snapshot.input.seasons[i].season_id, field) for i, edits in raw for field, _, _ in edits}
        changes = tuple(Change(old.season_id, field, getattr(old, field), getattr(new, field),
                               (old.season_id, field) in direct)
                        for old, new in zip(snapshot.input.seasons, plan) for field in FACT_FIELDS
                        if getattr(old, field) != getattr(new, field))
        identity_change = any(old.crop_id.value != new.crop_id.value or old.profile_id.value != new.profile_id.value
                              for old, new in zip(snapshot.input.seasons, plan))
        timing_change = any(old.sowing_date.value != new.sowing_date.value for old, new in zip(snapshot.input.seasons, plan))
        kind = "combined" if identity_change and timing_change else "crop_change" if identity_change else "timing_variant"
        evaluation = constraints.evaluate(plan, snapshot, kb)
        candidates[key] = Candidate("candidate-" + digest((identity_context, key)), kind, plan, changes,
                                    evaluation, ids, tuple(snapshot.input.seasons[i].season_id for i, _ in raw),
                                    template_ids, refs, tradeoffs)
    # Peek at most one unevaluated tuple; exact exhaustion is complete.
    truncated = raw_count == policy.raw_budget and next(iterator, None) is not None
    ordered = tuple(sorted(candidates.values(), key=lambda c: candidate_order(c, snapshot)))
    statuses = tuple(c.evaluation.status for c in ordered)
    reason = "candidate_budget" if truncated else "uninstantiated_choices" if blocked_ids else None
    search = SearchSummary(
        "incomplete" if reason else "complete", raw_count, len(ordered), len(ordered),
        statuses.count("rejected"), statuses.count("needs_review"), statuses.count("feasible"),
        duplicate_count, excluded_count, blocked_count,
        tuple(sorted({c.choice_id for c in scope.choices} | {cid for issue in scope.issues for cid in issue.choice_ids})),
        tuple(sorted(blocked_ids)), reason, policy.ordering_version)
    return GenerationResult(ordered, search, tuple(exclusions), scope)


def generate(snapshot: ScenarioSnapshot, kb: KnowledgeBase, policy: SearchPolicy) -> GenerationResult:
    scope = authorized_scope(snapshot, kb, policy)
    return _generate_prepared(snapshot, kb, policy, scope)
