"""Finite, typed source-backed predicates and mandatory topic coverage.

Rules arrive already loaded and reviewed. A source observation becomes a scoped
runtime rule only through the KB owner's approval, never by importing the draft
JSON here. No numeric agricultural threshold or calendar is embedded in code.
"""

from ._checks import check, path, sources
from ._types import (
    CalendarRule, Fact, FactRule, MANDATORY_TOPICS, PreparationRule,
    RotationRule, SowingWindowRule,
)
from ._validation import DATE_FIELDS, FACT_FIELDS, IDENTITY_FIELDS


def resolve(name, season, snapshot):
    """Return value, evidence sufficiency, unit, method, canonical input path."""
    if name == "site_id":
        return snapshot.input.site_id, True, None, None, "snapshot.input.site_id"
    if name == "season_label":
        return season.season_label, True, None, None, path(season, name)
    if name in FACT_FIELDS:
        fact, location = getattr(season, name), path(season, name)
    else:
        key = name.removeprefix("field.")
        fact, location = dict(snapshot.input.field_facts).get(key), "snapshot.input." + name
    if not isinstance(fact, Fact):
        return None, False, None, None, location
    supported = fact.value is not None and fact.evidence_status == "verified" and bool(fact.source_refs)
    return fact.value, supported, fact.unit, fact.method, location


def applicable(rule, season, snapshot):
    missing, mismatches = [], []
    for condition in rule.applicability:
        value, supported, unit, method, location = resolve(condition.path, season, snapshot)
        if not supported or unit != condition.unit or method != condition.method:
            missing.append(location)
        elif type(value) is not type(condition.expected) or value != condition.expected:
            mismatches.append(location)
    # A known scope mismatch excludes this source even if another scope fact is missing.
    if mismatches:
        return "not_applicable", "rule_scope_mismatch", (), {"condition": mismatches[0]}
    if missing:
        return "unknown", "profile_applicability_unverified", tuple(missing), {}
    return None


def predicate(rule, season, index, plan, snapshot):
    if isinstance(rule, FactRule):
        value, supported, unit, method, location = resolve(rule.path, season, snapshot)
        params = {"condition": rule.path, "actual_value": value, "expected_value": rule.expected,
                  "unit": rule.unit, "method": rule.method}
        if not supported or unit != rule.unit or method != rule.method:
            return "unknown", rule.unknown_code, (location,), params
        if rule.operator != "eq" and type(value) not in (int, float):
            return "unknown", "measurement_type_unverified", (location,), params
        passed = ((type(value) is type(rule.expected) and value == rule.expected) if rule.operator == "eq"
                  else value <= rule.expected if rule.operator == "le" else value >= rule.expected)
        return ("pass", "field_requirement_satisfied", (), params) if passed else (
            "fail", "field_restriction_conflict", (), params)
    if isinstance(rule, SowingWindowRule):
        sow = season.sowing_date.value
        params = {"sowing_date": sow, "window_start": rule.start, "window_end": rule.end}
        if sow is None:
            return "unknown", "sowing_support_unverified", (path(season, "sowing_date"),), params
        passed = rule.start <= sow <= rule.end
        code = "sowing_window_satisfied" if passed else (
            "outside_preferred_sowing_window" if rule.effect == "preference" else "outside_supported_sowing_window")
        return "pass" if passed else "fail", code, (), params
    if isinstance(rule, CalendarRule):
        # A mapping for another sowing is not an exclusion of this sowing.
        if season.sowing_date.value is not None and season.sowing_date.value != rule.sowing_date:
            return "not_applicable", "calendar_mapping_scope_mismatch", (), {"sowing_date": season.sowing_date.value}
        missing = tuple(path(season, name) for name in DATE_FIELDS if
                        getattr(season, name).value is None or getattr(season, name).value != getattr(rule, name))
        return ("unknown", "endpoint_mapping_missing", missing, {}) if missing else (
            "pass", "calendar_supported", (), {"sowing_date": rule.sowing_date})
    if isinstance(rule, PreparationRule):
        if index == len(plan) - 1:
            return "not_applicable", "no_successor_in_horizon", (), {}
        successor = plan[index + 1]
        if successor.profile_id.value is None:
            return "unknown", "profile_applicability_unverified", (path(successor, "profile_id"),), {}
        if successor.profile_id.value != rule.next_profile_id:
            return "not_applicable", "rule_scope_mismatch", (), {"next_profile_id": successor.profile_id.value}
        days = season.preparation_days_after_release.value
        params = {"preparation_days": days, "minimum_preparation_days": rule.days,
                  "next_profile_id": rule.next_profile_id}
        if days is None:
            return "unknown", "preparation_requirement_unverified", (path(season, "preparation_days_after_release"),), params
        return ("pass", "preparation_requirement_supported", (), params) if days >= rule.days else (
            "fail", "preparation_requirement_shortfall", (), params)
    if isinstance(rule, RotationRule):
        if index == 0:
            return "unknown", "predecessor_unknown", ("snapshot.input.previous_crop",), {}
        crop = plan[index - 1].crop_id.value
        params = {"predecessor_crop_id": crop}
        if crop is None:
            return "unknown", "predecessor_unknown", (path(plan[index - 1], "crop_id"),), params
        return ("pass", "rotation_requirement_satisfied", (), params) if crop in rule.allowed_predecessors else (
            "fail", "rotation_restriction_conflict", (), params)
    raise AssertionError("Rule type must have been validated")


def topic_paths(topic, season):
    fields = {
        "identity_purpose": ("crop_id", "purpose", "profile_id"),
        "sowing_support": ("sowing_date",),
        "harvest_crop_end_release": DATE_FIELDS[1:],
        "transition_preparation": ("preparation_days_after_release",),
    }.get(topic)
    return tuple(path(season, field) for field in fields) if fields else (f"kb.coverage.{season.profile_id.value}.{topic}",)


def evaluate_evidence(plan, snapshot, kb):
    checks, minima = [], {}
    topics = sorted(set(MANDATORY_TOPICS) | set(kb.required_planning_topics))
    for index, season in enumerate(plan):
        covered = set()
        for rule in sorted(kb.rules, key=lambda r: r.rule_id):
            if rule.profile_id != season.profile_id.value:
                continue
            if rule.evidence_status != "verified" or not rule.source_refs:
                result = ("unknown", "rule_evidence_unverified", (f"kb.rules.{rule.rule_id}.evidence",), {})
                if isinstance(rule, FactRule):
                    # Preserve the named open review gate and actual missing
                    # field path. A draft predicate never supplies pass/fail.
                    result = ("unknown", rule.unknown_code,
                              (f"kb.rules.{rule.rule_id}.evidence", resolve(rule.path, season, snapshot)[4]),
                              {"condition": rule.path, "evidence_status": rule.evidence_status})
            else:
                result = applicable(rule, season, snapshot)
                if result is None:
                    result = predicate(rule, season, index, plan, snapshot)
                    if (isinstance(rule, PreparationRule) and index < len(plan) - 1 and
                            plan[index + 1].profile_id.value == rule.next_profile_id and rule.effect == "hard"):
                        old, old_refs = minima.get(season.season_id, (0, ()))
                        minima[season.season_id] = (max(old, rule.days), sources(old_refs, rule.source_refs))
            outcome, code, missing, params = result
            # Keep the source's scope visible without inventing narrative text.
            params = {"season_id": season.season_id, "profile_id": rule.profile_id,
                      **{f"scope.{c.path}": c.expected for c in rule.applicability}, **params}
            checks.append(check(rule.rule_id, outcome, code, (season.season_id,), params=params,
                                refs=rule.source_refs, paths=missing, effect=rule.effect,
                                required_for=rule.required_for, version=rule.rule_version))
            if outcome == "pass" and rule.required_for == "planning" and rule.effect != "preference":
                covered.add(rule.topic)
        # Coverage of one identity predicate cannot fill a missing crop, purpose
        # or profile fact. Catalogue compatibility also remains a structural gate.
        if any(getattr(season, name).value is None for name in IDENTITY_FIELDS):
            covered.discard("identity_purpose")
        for topic in topics:
            # These are evaluated independently, including their empty-scope cases.
            if topic in ("protected_commitments", "hard_production_requirements_if_present"):
                continue
            if topic == "transition_preparation" and index == len(plan) - 1:
                checks.append(check("coverage:" + topic, "not_applicable", "no_successor_in_horizon",
                                    (season.season_id,), effect="review"))
            elif topic not in covered:
                code = {"sowing_support": "sowing_support_unverified",
                        "harvest_crop_end_release": "endpoint_mapping_missing",
                        "transition_preparation": "preparation_requirement_unverified",
                        "local_cultivar_field_fit": "profile_applicability_unverified",
                        "irrigation_constraints": "irrigation_availability_unknown"}.get(topic, "mandatory_topic_uncovered")
                checks.append(check("coverage:" + topic, "unknown", code, (season.season_id,),
                                    params={"topic": topic, "profile_id": season.profile_id.value},
                                    paths=topic_paths(topic, season), effect="review"))
    for req in snapshot.input.production_requirements:
        # No supplied release defines a quantified production predicate. Never
        # infer harvest/feed quantity from protected crop presence or field area.
        checks.append(check("production_requirement", "unknown",
                            "production_requirement_unverified" if req.hard else "forage_quantity_unknown",
                            req.season_ids, params={"requirement_id": req.requirement_id,
                            "quantity": req.quantity.value, "unit": req.quantity.unit},
                            refs=req.quantity.source_refs, paths=(f"snapshot.input.production_requirements.{req.requirement_id}.quantity_support",),
                            effect="review", required_for="planning" if req.hard else "explanation"))
    return checks, minima
