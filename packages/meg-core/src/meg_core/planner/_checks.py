"""Stable structured results shared by the finite constraint predicates."""

from datetime import date

from ._types import Explanation, RuleEvaluation, SourceRef

SPEC = (SourceRef("planner-spec", "sections 3.1-3.3; Promise Test v1"),)


def scalar(value):
    return value.isoformat() if isinstance(value, date) else value


def sources(*groups):
    return tuple(sorted({r for group in groups for r in group}, key=lambda r: (r.source_id, r.locator)))


def check(rule_id, outcome, code, season_ids=(), *, params=None, refs=SPEC,
          paths=(), commitments=(), effect="hard", required_for="planning", version="1"):
    return RuleEvaluation(
        rule_id, version, effect, required_for, outcome, tuple(season_ids), tuple(sorted(commitments)),
        Explanation(code, {k: scalar(v) for k, v in (params or {}).items()}, sources(refs)),
        tuple(sorted(set(paths))))


def path(season, field):
    return f"plan.{season.season_id}.{field}"


def reduce_status(checks):
    if any(c.outcome == "fail" and c.effect == "hard" for c in checks):
        return "rejected"
    if not checks or any(c.required_for == "planning" and
                         (c.outcome == "unknown" or (c.outcome == "fail" and c.effect == "review"))
                         for c in checks):
        return "needs_review"
    return "feasible"
