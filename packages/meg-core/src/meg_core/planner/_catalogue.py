"""Select supplied calendar evidence; never load data or invent endpoints."""

from dataclasses import replace

from ._evidence import applicable
from ._types import CalendarRule, SowingWindowRule


def active_rules(kb, season, snapshot, kind):
    return tuple(r for r in sorted(kb.rules, key=lambda r: r.rule_id)
                 if isinstance(r, kind) and r.profile_id == season.profile_id.value
                 and r.evidence_status == "verified" and r.source_refs
                 and applicable(r, season, snapshot) is None)


def template_dates(template, season, snapshot):
    """Return explicit exact/transferred dates, or a reason for not instantiating."""
    if template.template_id not in snapshot.input.authorized_template_ids:
        return None, "template_not_authorized"
    if template.runtime_status == "disabled" or not template.source_refs:
        return None, "template_not_activated"
    scope = applicable(template, season, snapshot)
    if scope and scope[0] == "not_applicable":
        return None, "template_scope_mismatch"
    if template.season_label.split("-")[0] != season.season_label.split("-")[0]:
        return None, "template_season_mismatch"
    delta = int(season.season_label.split("-")[1]) - int(template.season_label.split("-")[1])
    if delta and template.template_id not in snapshot.input.hypothetical_template_ids:
        return None, "hypothetical_transfer_not_authorized"
    try:
        dates = tuple(getattr(template, name).replace(year=getattr(template, name).year + delta)
                      if getattr(template, name) is not None else None for name in
                      ("sowing_date", "harvest_or_cut_date", "crop_end_exclusive", "release_date"))
    except ValueError:
        return None, "template_date_not_representable"
    verified = not delta and not scope and template.runtime_status == "approved"
    return dates, "verified" if verified else "hypothetical_review"


def sowing_supported(kb, season, snapshot):
    sow = season.sowing_date.value
    if sow is None:
        return False
    if any(r.sowing_date == sow for r in active_rules(kb, season, snapshot, CalendarRule)):
        return True
    if any(r.effect != "preference" and r.start <= sow <= r.end
           for r in active_rules(kb, season, snapshot, SowingWindowRule)):
        return True
    return any(dates is not None and dates[0] == sow
               for t in kb.templates if t.profile_id == season.profile_id.value
               for dates, _ in (template_dates(t, season, snapshot),))


def profile_season(season, profile):
    return replace(season, crop_id=replace(season.crop_id, value=profile.crop_id, unknown_reason=None),
                   purpose=replace(season.purpose, value=profile.purpose, unknown_reason=None),
                   profile_id=replace(season.profile_id, value=profile.profile_id, unknown_reason=None))
