"""Structural errors are exceptions, never agricultural needs_review results."""

from datetime import date
from math import isfinite
import re

from ._types import (
    CalendarRule, Commitment, Condition, Fact, FactRule, FIELD_UNKNOWN_CODES, KnowledgeBase, PreparationRule,
    ProductionRequirement, Profile, RotationRule, ScenarioInput, ScenarioSnapshot,
    SeasonInput, SourceRef, SowingWindowRule,
)

DATE_FIELDS = ("sowing_date", "harvest_or_cut_date", "crop_end_exclusive", "release_date")
IDENTITY_FIELDS = ("crop_id", "purpose", "profile_id")
FACT_FIELDS = IDENTITY_FIELDS + DATE_FIELDS + ("preparation_days_after_release",)


class InputValidationError(ValueError):
    def __init__(self, code: str, *field_paths: str):
        self.code = code
        self.field_paths = tuple(field_paths)
        super().__init__(f"{code}: {', '.join(field_paths)}")


def require(condition: bool, code: str, path: str) -> None:
    if not condition:
        raise InputValidationError(code, path)


def text(value, path):
    require(type(value) is str and bool(value.strip()), "nonempty_string_required", path)


def scalar(value, path):
    require(type(value) in (str, int, float, bool), "scalar_required", path)
    if type(value) is float:
        require(isfinite(value), "nonfinite_value", path)
    if type(value) is str:
        text(value, path)


def input_path(value, path):
    text(value, path)
    require(value in FACT_FIELDS + ("site_id", "season_label") or
            re.fullmatch(r"field\.[a-z][a-z0-9_]*", value) is not None,
            "unsupported_input_path", path)


def confirmed(value, path):
    expected = "confirmed_unknown" if value.value is None else "confirmed"
    require(value.confirmation_status == expected, "unconfirmed_snapshot_fact", path)


def refs(values, path):
    require(type(values) is tuple, "tuple_required", path)
    for ref in values:
        require(isinstance(ref, SourceRef), "source_ref_required", path)
        text(ref.source_id, path)
        text(ref.locator, path)


def fact(value, path):
    require(isinstance(value, Fact), "fact_required", path)
    require(value.evidence_status in ("verified", "proposed", "open"), "invalid_evidence_status", path)
    require(value.origin in ("farmer_report", "field_measurement", "published_study", "illustrative", "derived", "unknown"),
            "invalid_origin", path)
    require(value.confirmation_status in ("confirmed", "confirmed_unknown", "unconfirmed"), "invalid_confirmation", path)
    if value.value is None:
        text(value.unknown_reason, path + ".unknown_reason")
        require(value.confirmation_status != "confirmed", "unknown_cannot_be_confirmed_known", path)
    else:
        require(value.unknown_reason is None, "known_value_has_unknown_reason", path)
        require(value.confirmation_status != "confirmed_unknown", "known_cannot_be_confirmed_unknown", path)
        require(type(value.value) in (str, int, float, bool, date), "invalid_fact_type", path)
        if type(value.value) is float:
            require(isfinite(value.value), "nonfinite_value", path)
    if value.unit is not None:
        text(value.unit, path + ".unit")
    if value.method is not None:
        text(value.method, path + ".method")
    refs(value.source_refs, path + ".source_refs")


def slot(label, path):
    require(type(label) is str, "invalid_season_label", path)
    match = re.fullmatch(r"(winter|summer)-(\d{4})", label)
    require(match is not None, "invalid_season_label", path)
    kind, year_text = match.groups()
    year = int(year_text)
    require(1 <= year <= 9999, "invalid_season_year", path)
    # summer Y immediately precedes winter Y.
    return 2 * year + (kind == "winter")


def seasons(plan, path, profiles):
    require(type(plan) is tuple and len(plan) == 4, "four_seasons_required", path)
    ids, slots = [], []
    for order, season in enumerate(plan, 1):
        require(isinstance(season, SeasonInput), "season_required", path)
        p = f"{path}.{season.season_id}"
        text(season.season_id, p)
        ids.append(season.season_id)
        require(type(season.order) is int and season.order == order, "invalid_season_order", p)
        slots.append(slot(season.season_label, p + ".season_label"))
        for name in FACT_FIELDS:
            f = getattr(season, name)
            fact(f, p + "." + name)
            require(f.unit == ("day" if name == "preparation_days_after_release" else None), "invalid_unit", p + "." + name)
            if f.value is None:
                continue
            if name in IDENTITY_FIELDS:
                text(f.value, p + "." + name)
            elif name in DATE_FIELDS:
                require(type(f.value) is date, "civil_date_required", p + "." + name)
            else:
                require(type(f.value) is int and f.value >= 0, "nonnegative_integer_required", p + "." + name)
        values = [getattr(season, name).value for name in DATE_FIELDS]
        for i, left in enumerate(values):
            for j in range(i + 1, 4):
                right = values[j]
                if left is not None and right is not None:
                    strict = i <= 1 and j >= 2
                    require(left < right if strict else left <= right, "invalid_season_interval", p)
        if season.release_date.value is not None and season.preparation_days_after_release.value is not None:
            require(season.release_date.value.toordinal() + season.preparation_days_after_release.value <= date.max.toordinal(),
                    "date_out_of_range", p + ".preparation_days_after_release")
        profile = profiles.get(season.profile_id.value)
        if profile:
            for name in ("crop_id", "purpose"):
                value = getattr(season, name).value
                require(value is None or value == getattr(profile, name), "incompatible_profile", p + "." + name)
    require(len(set(ids)) == 4, "duplicate_season_id", path)
    require(all(b == a + 1 for a, b in zip(slots, slots[1:])), "nonconsecutive_seasons", path)


def validate(plan, snapshot, kb):
    require(isinstance(snapshot, ScenarioSnapshot), "snapshot_required", "snapshot")
    require(isinstance(snapshot.input, ScenarioInput), "scenario_input_required", "snapshot.input")
    require(isinstance(kb, KnowledgeBase), "knowledge_base_required", "kb")
    text(snapshot.data_release, "snapshot.data_release")
    require(snapshot.data_release == kb.data_release, "data_release_mismatch", "kb.data_release")
    for name in ("profiles", "rules", "required_planning_topics"):
        require(type(getattr(kb, name)) is tuple, "tuple_required", "kb." + name)
    for profile in kb.profiles:
        require(isinstance(profile, Profile), "profile_required", "kb.profiles")
        for name in ("profile_id", "crop_id", "purpose"):
            text(getattr(profile, name), "kb.profiles." + name)
    profiles = {p.profile_id: p for p in kb.profiles}
    require(len(profiles) == len(kb.profiles), "duplicate_profile_id", "kb.profiles")
    seasons(plan, "plan", profiles)
    seasons(snapshot.input.seasons, "snapshot.input.seasons", profiles)
    for season in snapshot.input.seasons:
        for name in FACT_FIELDS:
            confirmed(getattr(season, name), f"snapshot.input.seasons.{season.season_id}.{name}")
    require(tuple((s.season_id, s.season_label) for s in plan) ==
            tuple((s.season_id, s.season_label) for s in snapshot.input.seasons),
            "snapshot_slot_mismatch", "plan")
    text(snapshot.input.field_id, "snapshot.input.field_id")
    text(snapshot.input.site_id, "snapshot.input.site_id")
    fields = snapshot.input.field_facts
    require(type(fields) is tuple, "tuple_required", "snapshot.input.field_facts")
    for entry in fields:
        require(type(entry) is tuple and len(entry) == 2, "field_pair_required", "snapshot.input.field_facts")
        key, value = entry
        text(key, "snapshot.input.field_facts")
        fact(value, "snapshot.input." + key)
        confirmed(value, "snapshot.input." + key)
    require(len(dict(fields)) == len(fields), "duplicate_field", "snapshot.input.field_facts")
    ids = {s.season_id for s in plan}
    commitments = snapshot.input.commitments
    require(type(commitments) is tuple, "tuple_required", "snapshot.input.commitments")
    for c in commitments:
        require(isinstance(c, Commitment), "commitment_required", "snapshot.input.commitments")
        text(c.commitment_id, "snapshot.input.commitments")
        text(c.season_id, "snapshot.input.commitments.season_id")
        require(c.season_id in ids, "unknown_season_id", "snapshot.input.commitments")
        require(c.kind in ("crop", "purpose", "occupation_through", "harvest_or_cut_date"), "invalid_commitment_kind", c.commitment_id)
        fact(c.protected_value, "snapshot.input.commitments." + c.commitment_id)
        text(c.protected_value.value, "snapshot.input.commitments." + c.commitment_id)
        require(c.protected_value.unit is None, "invalid_unit", c.commitment_id)
        require(c.protected_value.confirmation_status == "confirmed", "unconfirmed_commitment", c.commitment_id)
        if c.kind in ("occupation_through", "harvest_or_cut_date"):
            try:
                parsed = date.fromisoformat(c.protected_value.value)
            except ValueError:
                raise InputValidationError("invalid_protected_date", c.commitment_id) from None
            require(parsed.isoformat() == c.protected_value.value, "invalid_protected_date", c.commitment_id)
    require(len({c.commitment_id for c in commitments}) == len(commitments), "duplicate_commitment", "snapshot.input.commitments")
    requirements = snapshot.input.production_requirements
    require(type(requirements) is tuple, "tuple_required", "snapshot.input.production_requirements")
    for req in requirements:
        require(isinstance(req, ProductionRequirement), "requirement_record_required", "snapshot.input.production_requirements")
        text(req.requirement_id, "snapshot.input.production_requirements")
        require(type(req.season_ids) is tuple, "tuple_required", req.requirement_id)
        for sid in req.season_ids:
            text(sid, req.requirement_id)
        require(type(req.hard) is bool and bool(req.season_ids) and set(req.season_ids) <= ids and
                len(set(req.season_ids)) == len(req.season_ids), "invalid_requirement", req.requirement_id)
        fact(req.quantity, req.requirement_id + ".quantity")
        confirmed(req.quantity, req.requirement_id + ".quantity")
        text(req.quantity.unit, req.requirement_id + ".quantity.unit")
        require(req.quantity.value is None or (type(req.quantity.value) in (int, float) and req.quantity.value > 0),
                "positive_quantity_required", req.requirement_id)
    require(len({r.requirement_id for r in requirements}) == len(requirements), "duplicate_requirement", "snapshot.input.production_requirements")
    rule_ids = set()
    for rule in kb.rules:
        require(type(rule) in (FactRule, CalendarRule, SowingWindowRule, PreparationRule, RotationRule), "unsupported_rule_type", "kb.rules")
        text(rule.rule_id, "kb.rules.rule_id")
        p = "kb.rules." + rule.rule_id
        for name in ("rule_id", "rule_version", "profile_id", "topic"):
            text(getattr(rule, name), p + "." + name)
        require(rule.rule_id not in rule_ids, "duplicate_rule_id", p)
        rule_ids.add(rule.rule_id)
        require(rule.profile_id in profiles, "unknown_profile_id", p)
        require(rule.effect in ("hard", "review", "preference"), "invalid_rule_effect", p)
        require(rule.required_for in ("planning", "explanation", "etc"), "invalid_required_for", p)
        require(rule.evidence_status in ("verified", "proposed", "open"), "invalid_evidence_status", p)
        refs(rule.source_refs, p)
        require(type(rule.applicability) is tuple, "tuple_required", p + ".applicability")
        for cond in rule.applicability:
            require(isinstance(cond, Condition), "condition_required", p + ".applicability")
            input_path(cond.path, p + ".applicability")
            scalar(cond.expected, p + ".applicability")
            if cond.unit is not None:
                text(cond.unit, p + ".applicability.unit")
            if cond.method is not None:
                text(cond.method, p + ".applicability.method")
        fixed_topic = {SowingWindowRule: "sowing_support", CalendarRule: "harvest_crop_end_release",
                       PreparationRule: "transition_preparation", RotationRule: "rotation"}.get(type(rule))
        if fixed_topic:
            require(rule.topic == fixed_topic, "predicate_topic_mismatch", p + ".topic")
        else:
            require(rule.topic not in ("sowing_support", "harvest_crop_end_release", "transition_preparation", "rotation",
                                       "protected_commitments", "hard_production_requirements_if_present"),
                    "predicate_topic_mismatch", p + ".topic")
        if isinstance(rule, SowingWindowRule):
            require(type(rule.start) is date and type(rule.end) is date and rule.start <= rule.end, "invalid_window", p)
        elif isinstance(rule, CalendarRule):
            dates = [getattr(rule, name) for name in DATE_FIELDS]
            require(all(type(d) is date for d in dates) and dates[0] <= dates[1] < dates[2] <= dates[3], "invalid_rule_calendar", p)
        elif isinstance(rule, PreparationRule):
            require(type(rule.days) is int and 0 <= rule.days <= date.max.toordinal(), "invalid_preparation_rule", p)
            require(rule.next_profile_id in profiles, "unknown_profile_id", p)
        elif isinstance(rule, FactRule):
            require(rule.unknown_code in FIELD_UNKNOWN_CODES, "unsupported_explanation_code", p + ".unknown_code")
            input_path(rule.path, p + ".path")
            scalar(rule.expected, p + ".expected")
            require(rule.operator in ("eq", "le", "ge"), "invalid_operator", p)
            if rule.unit is not None:
                text(rule.unit, p + ".unit")
            if rule.method is not None:
                text(rule.method, p + ".method")
            if rule.operator != "eq":
                require(type(rule.expected) in (int, float) and isfinite(rule.expected), "numeric_threshold_required", p)
        elif isinstance(rule, RotationRule):
            require(type(rule.allowed_predecessors) is tuple and bool(rule.allowed_predecessors), "empty_rotation_scope", p)
            for crop in rule.allowed_predecessors:
                text(crop, p + ".allowed_predecessors")
    for topic in kb.required_planning_topics:
        text(topic, "kb.required_planning_topics")
