"""Pure preview of explicit permissions. Preview never confirms or mutates input."""

from dataclasses import replace
from datetime import date

from ._canonical import canonical, context, digest
from ._catalogue import active_rules, profile_season, template_dates
from ._types import (
    CalendarRule, CatalogueChoice, DateRangeChoice, ExplorationChoice, IndependentFact,
    KnowledgeBase, PlantingTemplate, ScenarioInput, ScenarioSnapshot, ScopeIssue, ScopePreview,
    ScopeRequest, SearchPolicy,
)
from ._validation import DATE_FIELDS, FACT_FIELDS, InputValidationError, input_path, refs, require, scalar, slot, text, validate

EDITABLE = ("crop_id", "profile_id", "sowing_date")
DEPENDENT = DATE_FIELDS[1:] + ("preparation_days_after_release",)


def validate_policy(policy):
    require(isinstance(policy, SearchPolicy), "search_policy_required", "policy")
    for name in ("raw_budget", "max_choice_records", "max_values_per_choice"):
        value = getattr(policy, name)
        require(type(value) is int and value > 0, "positive_integer_required", "policy." + name)
    require(policy.ordering_version == "minimal-edits-v1-proposed", "unsupported_ordering_version", "policy.ordering_version")


def validate_search_context(snapshot, kb):
    i = snapshot.input
    require(i.journey in ("check", "explore"), "invalid_journey", "snapshot.input.journey")
    require(type(i.exploration_confirmed) is bool, "boolean_required", "snapshot.input.exploration_confirmed")
    for name in ("priority_order", "independent_facts", "authorized_template_ids", "hypothetical_template_ids", "pending_scope_issues"):
        require(type(getattr(i, name)) is tuple, "tuple_required", "snapshot.input." + name)
    for priority in i.priority_order:
        require(priority in ("minimize_changes", "understand_demand", "understand_sequence"), "unsupported_priority", "snapshot.input.priority_order")
    require(len(set(i.priority_order)) == len(i.priority_order), "duplicate_priority", "snapshot.input.priority_order")
    ids = {s.season_id for s in i.seasons}
    for item in i.independent_facts:
        require(isinstance(item, IndependentFact), "independence_record_required", "snapshot.input.independent_facts")
        text(item.season_id, "independent_facts.season_id")
        require(item.season_id in ids and item.field in DEPENDENT, "invalid_independent_fact", "snapshot.input.independent_facts")
        require(type(item.depends_on) is tuple, "tuple_required", "independent_facts.depends_on")
        for dep in item.depends_on:
            require(dep in EDITABLE + ("purpose",) + tuple("next." + f for f in EDITABLE + ("purpose",)),
                    "invalid_dependency", "independent_facts.depends_on")
        value = getattr(next(s for s in i.seasons if s.season_id == item.season_id), item.field)
        require(value.confirmation_status == "confirmed" and value.value is not None, "independent_fact_must_be_known_confirmed", item.field)
    require(len({(f.season_id, f.field) for f in i.independent_facts}) == len(i.independent_facts), "duplicate_independent_fact", "snapshot.input.independent_facts")
    for name in ("authorized_template_ids", "hypothetical_template_ids"):
        for template_id in getattr(i, name):
            text(template_id, "snapshot.input." + name)
    require(set(i.hypothetical_template_ids) <= set(i.authorized_template_ids), "hypothetical_template_not_authorized", "snapshot.input.hypothetical_template_ids")
    for issue in i.pending_scope_issues:
        require(isinstance(issue, ScopeIssue) and issue.kind in ("blocked", "excluded"), "scope_issue_required", "snapshot.input.pending_scope_issues")
    require(type(kb.templates) is tuple, "tuple_required", "kb.templates")
    seen = set()
    for t in kb.templates:
        require(isinstance(t, PlantingTemplate), "template_required", "kb.templates")
        text(t.template_id, "kb.templates.template_id")
        require(t.template_id not in seen, "duplicate_template", "kb.templates")
        seen.add(t.template_id)
        require(t.profile_id in {p.profile_id for p in kb.profiles}, "unknown_template_profile", "kb.templates")
        slot(t.season_label, "kb.templates.season_label")
        text(t.template_version, "kb.templates.template_version")
        require(t.runtime_status in ("review", "approved", "disabled"), "invalid_template_status", "kb.templates")
        refs(t.source_refs, "kb.templates.source_refs")
        require(type(t.sowing_date) is date, "civil_date_required", "kb.templates.sowing_date")
        values = tuple(getattr(t, name) for name in DATE_FIELDS)
        for value in values:
            require(value is None or type(value) is date, "civil_date_required", "kb.templates")
        for a in range(4):
            for b in range(a + 1, 4):
                if values[a] is not None and values[b] is not None:
                    require(values[a] < values[b] if a <= 1 and b >= 2 else values[a] <= values[b], "invalid_template_interval", "kb.templates")
        require(type(t.applicability) is tuple, "tuple_required", "kb.templates.applicability")
        for condition in t.applicability:
            input_path(condition.path, "kb.templates.applicability")
            scalar(condition.expected, "kb.templates.applicability")


def normalize_choices(choices, snapshot):
    require(type(choices) is tuple, "tuple_required", "scope.choices")
    result, seen = [], set()
    ids = {s.season_id for s in snapshot.input.seasons}
    for choice in choices:
        require(type(choice) in (ExplorationChoice, DateRangeChoice), "choice_required", "scope.choices")
        text(choice.choice_id, "scope.choices.choice_id")
        text(choice.season_id, "scope.choices.season_id")
        require(choice.season_id in ids and choice.field in EDITABLE, "invalid_choice_target", choice.choice_id)
        require(choice.choice_id not in seen, "duplicate_choice_id", choice.choice_id)
        seen.add(choice.choice_id)
        if isinstance(choice, DateRangeChoice):
            require(type(choice.start) is date and type(choice.end) is date and choice.start <= choice.end,
                    "invalid_date_range", choice.choice_id)
            require(type(choice.step_days) is int and choice.step_days > 0, "positive_integer_required", choice.choice_id)
        else:
            require(type(choice.allowed_values) is tuple and bool(choice.allowed_values), "nonempty_values_required", choice.choice_id)
            for value in choice.allowed_values:
                text(value, choice.choice_id)
                if choice.field == "sowing_date":
                    try:
                        parsed = date.fromisoformat(value)
                    except ValueError:
                        raise InputValidationError("invalid_choice_date", choice.choice_id) from None
                    require(parsed.isoformat() == value, "invalid_choice_date", choice.choice_id)
            choice = replace(choice, allowed_values=tuple(sorted(set(choice.allowed_values))))
        result.append(choice)
    return tuple(sorted(result, key=lambda c: (c.season_id, c.field, c.choice_id)))


def readback_issues(choices, snapshot, kb):
    """Report requested values that touch a protected crop or lack any catalogue profile.

    Choices stay as requested: the generator records the per-combination exclusion or
    blocked branch. These issues let the farmer see the problem before confirming.
    A protected-commitment conflict is a proven exclusion and takes precedence over a
    missing catalogue entry.
    """
    profiles = {p.profile_id: p for p in kb.profiles}
    crops = {p.crop_id for p in kb.profiles}
    issues = []
    for choice in choices:
        if isinstance(choice, DateRangeChoice) or choice.field == "sowing_date":
            continue
        locks = {c.protected_value.value for c in snapshot.input.commitments
                 if c.season_id == choice.season_id and c.kind == "crop"}
        excluded, blocked = [], []
        for value in choice.allowed_values:
            crop = value if choice.field == "crop_id" else getattr(profiles.get(value), "crop_id", None)
            if crop is not None and locks and crop not in locks:
                excluded.append(value)
            elif (crop not in crops) if choice.field == "crop_id" else (value not in profiles):
                blocked.append(value)
        if excluded:
            issues.append(ScopeIssue("choice_conflicts_with_protected_commitment", (choice.choice_id,),
                                     (choice.season_id,), kind="excluded"))
        if blocked:
            issues.append(ScopeIssue("catalogue_value_unavailable", (choice.choice_id,), (choice.season_id,),
                                     tuple(f"kb.catalogue.{choice.season_id}.{choice.field}.{v}" for v in blocked)))
    return issues


def prepare_scope(request: ScopeRequest, kb: KnowledgeBase) -> ScopePreview:
    require(isinstance(request, ScopeRequest), "scope_request_required", "request")
    snapshot = request.snapshot
    require(isinstance(snapshot, ScenarioSnapshot), "snapshot_required", "snapshot")
    require(isinstance(snapshot.input, ScenarioInput), "scenario_input_required", "snapshot.input")
    validate(snapshot.input.seasons, snapshot, kb, check_confirmation=False)
    validate_search_context(snapshot, kb)
    choices = list(normalize_choices(snapshot.input.exploration if request.choices is None else request.choices, snapshot))
    issues = list(snapshot.input.pending_scope_issues)
    require(type(request.catalogue_choices) is tuple, "tuple_required", "scope.catalogue_choices")
    for query in request.catalogue_choices:
        require(isinstance(query, CatalogueChoice), "catalogue_choice_required", "scope.catalogue_choices")
        text(query.choice_id, "scope.catalogue_choices.choice_id")
        require(query.field in EDITABLE, "invalid_choice_target", query.choice_id)
        require(type(query.allowed_crop_ids) is tuple and bool(query.allowed_crop_ids), "explicit_crop_scope_required", query.choice_id)
        for crop in query.allowed_crop_ids:
            text(crop, query.choice_id)
        season = next((s for s in snapshot.input.seasons if s.season_id == query.season_id), None)
        require(season is not None, "unknown_season_id", query.choice_id)
        values = set()
        for profile in kb.profiles:
            if profile.crop_id not in query.allowed_crop_ids or profile.purpose != season.purpose.value:
                continue
            projected = profile_season(season, profile)
            calendars = active_rules(kb, projected, snapshot, CalendarRule)
            dates = {r.sowing_date for r in calendars}
            for template in kb.templates:
                if template.profile_id == profile.profile_id:
                    mapped, _ = template_dates(template, projected, snapshot)
                    if mapped:
                        dates.add(mapped[0])
            if dates:
                values.update(d.isoformat() for d in dates) if query.field == "sowing_date" else values.add(getattr(profile, query.field))
        if values:
            choices.append(ExplorationChoice(query.choice_id, query.season_id, query.field, tuple(sorted(values))))
        else:
            issues.append(ScopeIssue("catalogue_choices_unavailable", (query.choice_id,), (query.season_id,),
                                     (f"kb.catalogue.{query.season_id}.{query.field}",)))
    choices = normalize_choices(tuple(choices), snapshot)
    issues.extend(readback_issues(choices, snapshot, kb))
    # Adapters may echo preview issues back as pending issues; identical records merge.
    issues = tuple(sorted({canonical(i): i for i in issues}.values(), key=canonical))
    missing = {f"plan.{s.season_id}.{name}" for s in snapshot.input.seasons for name in FACT_FIELDS
               if getattr(s, name).value is None or getattr(s, name).confirmation_status == "unconfirmed"}
    missing.update(p for issue in issues for p in issue.missing_input_paths)
    scope_hash = digest((context(snapshot), choices, issues))
    return ScopePreview(kb.data_release, scope_hash, choices, tuple(sorted({p.crop_id for p in kb.profiles})),
                        tuple(sorted(snapshot.input.commitments, key=lambda c: c.commitment_id)), tuple(sorted(missing)), issues)
