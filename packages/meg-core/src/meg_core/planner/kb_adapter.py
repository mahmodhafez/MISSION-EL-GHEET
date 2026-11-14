"""Map Refaat's agricultural KB (`agricultural-kb/1`) onto the private planner views.

PROPOSED boundary: Yahya must approve field names, units and the date/leap convention
(see Refaat's AGRICULTURAL_KB_CONTRACT.md). Pure: takes the JSON-compatible dicts that
Refaat's loader already returned; never imports it, reads files or promotes evidence.

Only rules the loader marks enforceable become planner rules. Every other rule is listed
in `unmapped` with a reason, so missing planning topics keep a plan `needs_review`.
"""

from dataclasses import dataclass
from datetime import date
import re

from ._types import Condition, FactRule, KnowledgeBase, Profile, SourceRef, SowingWindowRule
from ._validation import require, slot, text

# Winter-YYYY starts in YYYY: July-December resolve to YYYY, January-June to YYYY+1.
SLOT_YEAR_POLICY = "winter-start-year-v1-proposed"
# rule_type -> planner topic. Extend only by Refaat + Yahya agreement.
DEFAULT_TOPICS = {"sowing_window": "sowing_support"}
_KEY = re.compile(r"[a-z][a-z0-9_]*")
_MONTH_DAY = re.compile(r"(\d{2})-(\d{2})")


@dataclass(frozen=True)
class Unmapped:
    rule_id: str
    reason: str


@dataclass(frozen=True)
class AdaptedKB:
    kb: KnowledgeBase
    unmapped: tuple[Unmapped, ...]
    kb_version: str
    slot_year_policy: str = SLOT_YEAR_POLICY


def _resolve(month_day, label):
    match = _MONTH_DAY.fullmatch(month_day) if type(month_day) is str else None
    require(match is not None, "invalid_month_day", "constraint")
    month, day = int(match[1]), int(match[2])
    kind, year = label.split("-")
    year = int(year) + (kind == "winter" and month < 7)
    return date(year, month, day)  # ValueError for 02-29 in a non-leap year


def _window(rule_id, constraint, label):
    try:
        start, end = _resolve(constraint["start_month_day"], label), _resolve(constraint["end_month_day"], label)
    except ValueError:
        return None, "leap_day_unresolved"
    if start > end:
        return None, "window_crosses_slot_year"
    return (start, end), None


def adapt(*, crops, enforceable_rules, kb_version, data_release, site_id, season_labels,
          topics=DEFAULT_TOPICS) -> AdaptedKB:
    """Build a planner KnowledgeBase from loader output. Never infers a missing value."""
    for name, value in (("kb_version", kb_version), ("data_release", data_release), ("site_id", site_id)):
        text(value, name)
    require(type(crops) is list and type(enforceable_rules) is list, "list_required", "crops/enforceable_rules")
    require(type(season_labels) is tuple and bool(season_labels), "tuple_required", "season_labels")
    for label in season_labels:
        slot(label, "season_labels")
    profiles = []
    for crop in crops:
        require(type(crop) is dict, "crop_required", "crops")
        text(crop.get("crop_id"), "crops.crop_id")
        text(crop.get("purpose"), "crops.purpose")
        profiles.append(Profile(crop["crop_id"], crop["crop_id"], crop["purpose"]))
    known = {p.profile_id for p in profiles}
    rules, unmapped = [], []
    for rule in enforceable_rules:
        require(type(rule) is dict, "rule_required", "enforceable_rules")
        rid = rule.get("rule_id")
        text(rid, "enforceable_rules.rule_id")
        reason = None
        if (rule.get("enforceability") or {}).get("enforceable") is not True:
            reason = "not_enforceable"
        elif rule.get("rule_type") not in topics:
            reason = "topic_mapping_required"
        elif not rule.get("source_ids"):
            reason = "source_refs_missing"
        constraint = (rule.get("enforcement") or {}).get("constraint") or {}
        conditions = rule.get("conditions") or {}
        if reason is None and any(type(v) is not list or len(v) != 1 for v in conditions.values()):
            reason = "multi_value_condition"
        if reason is None and any(_KEY.fullmatch(k) is None for k in conditions):
            reason = "condition_key_unsupported"
        if reason is None and any(c not in known for c in rule.get("crop_ids") or ()):
            reason = "unknown_crop"
        if reason:
            unmapped.append(Unmapped(rid, reason))
            continue
        refs = tuple(SourceRef(s, f"{kb_version} rule {rid}") for s in sorted(set(rule["source_ids"])))
        base = dict(rule_version=kb_version, topic=topics[rule["rule_type"]], source_refs=refs,
                    evidence_status="verified", effect="hard", required_for="planning")
        where = (Condition("site_id", site_id),) + tuple(
            Condition("field." + k, v[0]) for k, v in sorted(conditions.items()))
        kind, field = constraint.get("kind"), constraint.get("field")
        made = []
        for crop in rule["crop_ids"]:
            if kind == "calendar_window" and field == "sowing_date":
                for label in season_labels:
                    window, why = _window(rid, constraint, label)
                    if why:
                        unmapped.append(Unmapped(f"{rid}:{crop}:{label}", why))
                        continue
                    made.append(SowingWindowRule(**base, rule_id=f"{rid}:{crop}:{label}", profile_id=crop,
                                                 applicability=where + (Condition("season_label", label),),
                                                 start=window[0], end=window[1]))
            elif kind == "numeric_range" and type(field) is str and _KEY.fullmatch(field):
                for op, bound in (("ge", constraint.get("lower")), ("le", constraint.get("upper"))):
                    made.append(FactRule(**base, rule_id=f"{rid}:{crop}:{op}", profile_id=crop,
                                         applicability=where, path="field." + field, expected=bound,
                                         operator=op, unit=constraint.get("units")))
            elif kind == "category_set" and type(field) is str and _KEY.fullmatch(field) and \
                    len(constraint.get("allowed") or ()) == 1:
                made.append(FactRule(**base, rule_id=f"{rid}:{crop}:eq", profile_id=crop, applicability=where,
                                     path="field." + field, expected=constraint["allowed"][0]))
            else:
                unmapped.append(Unmapped(f"{rid}:{crop}", "unsupported_constraint"))
        rules.extend(made)
    kb = KnowledgeBase(data_release=data_release, profiles=tuple(profiles), rules=tuple(rules))
    return AdaptedKB(kb, tuple(sorted(unmapped, key=lambda u: (u.rule_id, u.reason))), kb_version)
