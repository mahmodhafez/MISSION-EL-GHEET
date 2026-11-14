"""Milestone 1: pure deterministic Promise Test, with private contract views.

evaluate(plan: tuple[SeasonInput, ...], snapshot: ScenarioSnapshot,
         kb: KnowledgeBase) -> PlanEvaluation

The signature and result field names follow the target boundary. These names
currently refer to private dataclasses, NOT approved meg_core.contracts exports.
Yahya must bind the shared models and server plan reference during integration.
The caller supplies an already-loaded KB; no files, clocks, network or forecasts
are accessed. Invalid structures raise InputValidationError before evaluation.
"""

from ._checks import reduce_status, scalar
from ._evidence import evaluate_evidence
from ._temporal import commitments, occupancy, preparation
from ._types import Explanation, KnowledgeBase, PlanEvaluation, ScenarioSnapshot, SeasonInput
from ._validation import FACT_FIELDS, validate


def evaluate(plan: tuple[SeasonInput, ...], snapshot: ScenarioSnapshot,
             kb: KnowledgeBase) -> PlanEvaluation:
    validate(plan, snapshot, kb)
    lock_checks, preserved = commitments(plan, snapshot)
    evidence_checks, minima = evaluate_evidence(plan, snapshot, kb)
    checks = lock_checks + occupancy(plan, snapshot) + preparation(plan, snapshot, minima) + evidence_checks
    order = {season.season_id: season.order for season in plan}

    def sort_key(check):
        protected = check.explanation.code == "sowing_before_protected_cut"
        severity = 0 if check.outcome == "fail" and check.effect == "hard" else (
            1 if check.outcome == "unknown" and check.required_for == "planning" else 2)
        return (not protected, severity, tuple(order[s] for s in check.season_ids), check.rule_id,
                check.commitment_ids, check.explanation.code)

    checks.sort(key=sort_key)
    assumptions = tuple(
        Explanation("declared_fact_assumption", {"input_path": f"plan.{season.season_id}.{name}",
                    "value": scalar(fact.value), "origin": fact.origin}, fact.source_refs)
        for season in plan for name in FACT_FIELDS
        if (fact := getattr(season, name)).value is not None and fact.evidence_status != "verified")
    return PlanEvaluation(reduce_status(checks), tuple(checks), preserved, assumptions)
