"""Replay the supplied UH-001 JSON against the pinned review release. Research fixture only."""
from collections import Counter
from dataclasses import replace
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from planner_cli import encode, load
from meg_core.agricultural_release import load_reviewed_release
from meg_core.planner import constraints
from meg_core.planner._types import ScopeRequest
from meg_core.planner.generate import generate
from meg_core.planner.scope import prepare_scope
from meg_core.planner.service import plan


def run():
    _, snapshot, _, choices, catalogue_choices, policy, confirmed = load(
        Path(__file__).with_name("fixtures") / "uh001.json")
    release = load_reviewed_release()
    inputs = snapshot.input
    built = release.for_planner(site_id=inputs.site_id,
                                season_labels=tuple(s.season_label for s in inputs.seasons))
    # The fixture uses reference-* aliases. Resolve by its unchanged crop AND purpose.
    seasons = []
    for season in inputs.seasons:
        matches = [p for p in built.kb.profiles if (p.crop_id, p.purpose) ==
                   (season.crop_id.value, season.purpose.value)]
        if len(matches) != 1:
            raise ValueError(f"UH-001 profile binding is ambiguous or absent for {season.season_id}")
        seasons.append(replace(season, profile_id=replace(season.profile_id, value=matches[0].profile_id)))
    snapshot = replace(snapshot, data_release=release.version, input=replace(inputs, seasons=tuple(seasons)))
    evaluated = constraints.evaluate(snapshot.input.seasons, snapshot, built.kb)
    draft = replace(snapshot, input=replace(snapshot.input, journey="explore"))
    preview = prepare_scope(ScopeRequest(snapshot=draft, choices=choices, catalogue_choices=catalogue_choices), built.kb)
    if not confirmed:
        raise ValueError("The supplied fixture did not authorize exploration")
    bound = replace(draft, input=replace(draft.input, exploration=preview.choices,
                    pending_scope_issues=preview.issues, scope_hash=preview.scope_hash, exploration_confirmed=confirmed))
    generated = generate(bound, built.kb, policy)
    result = plan(bound, built.kb, policy)
    return {
        "fixture": "UH-001/v1; fictional farmer; source calendar retained",
        "release": result.data_release,
        "catalogue_crop_count": len(release.catalogue.records),
        "planner_profile_ids": [p.profile_id for p in built.kb.profiles],
        "runtime_rule_count": len(built.kb.rules), "template_count": len(built.kb.templates),
        "current": evaluated.status, "service_current": result.current.status,
        "first_reason": evaluated.checks[0].explanation.code,
        "protected_cut": encode(seasons[0].harvest_or_cut_date.value),
        "service_feasible": len(result.feasible_alternatives),
        "generator_status_counts": dict(Counter(c.evaluation.status for c in generated.candidates)),
        "generator_search": encode(generated.search), "service_search": encode(result.search),
        "review_investigations": [{
            "candidate_id": c.candidate_id, "status": c.evaluation.status, "s2_sowing": encode(c.plan[1].sowing_date.value),
            "s1_cut": encode(c.plan[0].harvest_or_cut_date.value), "s2_harvest": encode(c.plan[1].harvest_or_cut_date.value),
            "s2_end_exclusive": encode(c.plan[1].crop_end_exclusive.value), "s2_release": encode(c.plan[1].release_date.value),
            "s2_preparation_days": c.plan[1].preparation_days_after_release.value,
            "review_reasons": sorted({x.explanation.code for x in c.evaluation.checks if x.outcome=="unknown"}),
        } for c in result.review_investigations],
        "exclusions": [encode(e) for e in result.exclusions],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
