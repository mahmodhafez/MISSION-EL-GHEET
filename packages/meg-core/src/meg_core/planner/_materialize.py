"""Apply authorized edits and evidence dependencies, without deciding feasibility."""

from dataclasses import replace
from datetime import date

from ._catalogue import active_rules, profile_season, sowing_supported, template_dates
from ._checks import sources
from ._types import CalendarRule, Explanation, Fact, PreparationRule, ScopeIssue
from ._validation import DATE_FIELDS, InputValidationError, validate


def proposed(value, refs=(), *, evidence="proposed", reason="endpoint_mapping_missing", unit=None):
    return Fact(value=value, unknown_reason=reason if value is None else None, unit=unit,
                origin="unknown" if value is None else "derived",
                evidence_status="open" if value is None else evidence,
                confirmation_status="unconfirmed", source_refs=refs)


def dependency(plan, index, name):
    if name.startswith("next."):
        index += 1
        name = name[5:]
    return getattr(plan[index], name).value if index < len(plan) else None


def independent(snapshot, plan, index, name):
    original = snapshot.input.seasons
    return any(item.season_id == original[index].season_id and item.field == name and
               all(dependency(original, index, dep) == dependency(plan, index, dep) for dep in item.depends_on)
               for item in snapshot.input.independent_facts)


def materialize(raw, snapshot, kb):
    original = snapshot.input.seasons
    result = list(original)
    template_ids, explanations = set(), []
    all_choices = tuple(sorted({cid for _, edits in raw for _, _, ids in edits for cid in ids}))
    profiles = {p.profile_id: p for p in kb.profiles}

    def issue(code, index, *, blocked=True, paths=()):
        local_choices = tuple(sorted({cid for i, edits in raw if i == index for _, _, ids in edits for cid in ids}))
        return ScopeIssue(code, local_choices or all_choices, (original[index].season_id,), tuple(paths),
                          kind="blocked" if blocked else "excluded")

    for index, edits in raw:
        old = original[index]
        edit = {name: value for name, value, _ in edits}
        crop = edit.get("crop_id", old.crop_id.value)
        sow = date.fromisoformat(edit["sowing_date"]) if "sowing_date" in edit else old.sowing_date.value
        for lock in snapshot.input.commitments:
            if lock.season_id == old.season_id and lock.kind == "crop" and crop != lock.protected_value.value:
                return issue("protected_commitment_mismatch", index, blocked=False)
        pid = edit.get("profile_id", old.profile_id.value)
        if crop != old.crop_id.value and "profile_id" not in edit:
            options = []
            for profile in kb.profiles:
                if profile.crop_id == crop and profile.purpose == old.purpose.value:
                    candidate = replace(profile_season(old, profile), sowing_date=proposed(sow))
                    if sowing_supported(kb, candidate, snapshot):
                        options.append(profile)
            if len(options) != 1:
                return issue("profile_binding_unavailable" if not options else "profile_binding_ambiguous", index,
                             paths=(f"kb.profiles.{crop}",))
            pid = options[0].profile_id
        profile = profiles.get(pid)
        if profile is None:
            return issue("crop_profile_missing", index, paths=(f"kb.profiles.{pid}",))
        if profile.crop_id != crop or (old.purpose.value is not None and profile.purpose != old.purpose.value):
            return issue("incompatible_profile", index, blocked=False)
        if old.purpose.value is None:
            return issue("purpose_unknown", index, paths=(f"plan.{old.season_id}.purpose",))
        season = replace(old,
            crop_id=old.crop_id if crop == old.crop_id.value else proposed(crop, profile.source_refs, evidence=profile.evidence_status),
            profile_id=old.profile_id if pid == old.profile_id.value else proposed(pid, profile.source_refs, evidence=profile.evidence_status),
            sowing_date=old.sowing_date if sow == old.sowing_date.value else proposed(sow))
        if (crop != old.crop_id.value or pid != old.profile_id.value) and not sowing_supported(kb, season, snapshot):
            return issue("sowing_basis_missing", index, paths=(f"kb.profiles.{pid}.sowing_support",))
        result[index] = season

    # Recompute only changed timelines. Never slide a later farmer intention.
    for index, _ in raw:
        season = result[index]
        calendars = tuple(r for r in active_rules(kb, season, snapshot, CalendarRule)
                          if r.sowing_date == season.sowing_date.value)
        mappings = [(tuple(getattr(r, field) for field in DATE_FIELDS), r.source_refs, "verified") for r in calendars]
        for rule in calendars:
            explanations.append(Explanation("calendar_recomputed", {"season_id": season.season_id,
                "rule_id": rule.rule_id, "rule_version": rule.rule_version}, rule.source_refs))
        if not mappings:
            for template in sorted(kb.templates, key=lambda t: t.template_id):
                if template.profile_id != season.profile_id.value:
                    continue
                dates, basis = template_dates(template, season, snapshot)
                if dates and dates[0] == season.sowing_date.value:
                    template_ids.add(template.template_id)
                    mappings.append((dates, template.source_refs, "verified" if basis == "verified" else "proposed"))
                    explanations.append(Explanation("template_calendar_basis", {"template_id": template.template_id,
                        "template_version": template.template_version, "basis": basis,
                        "source_sowing_date": template.sowing_date.isoformat(),
                        "target_sowing_date": dates[0].isoformat()}, template.source_refs))
        fields = {}
        for offset, name in enumerate(DATE_FIELDS[1:], 1):
            locked = name == "harvest_or_cut_date" and any(c.season_id == season.season_id and c.kind == name
                                                          for c in snapshot.input.commitments)
            if locked or independent(snapshot, result, index, name):
                fields[name] = getattr(original[index], name)
                continue
            values = {m[0][offset] for m in mappings}
            value = next(iter(values)) if len(values) == 1 and None not in values else None
            evidence = "verified" if mappings and all(m[2] == "verified" for m in mappings) else "proposed"
            fields[name] = proposed(value, sources(*(m[1] for m in mappings)), evidence=evidence)
            if value is None:
                explanations.append(Explanation("endpoint_invalidated", {"season_id": season.season_id, "field": name}, ()))
        result[index] = replace(season, **fields)

    for index, season in enumerate(result[:-1]):
        # Preparation depends on both sides, including a changed endpoint.
        affected = result[index] != original[index] or result[index + 1] != original[index + 1]
        if not affected or independent(snapshot, result, index, "preparation_days_after_release"):
            continue
        rules = tuple(r for r in active_rules(kb, season, snapshot, PreparationRule)
                      if r.effect == "hard" and r.next_profile_id == result[index + 1].profile_id.value)
        days = max((r.days for r in rules), default=None)
        result[index] = replace(season, preparation_days_after_release=proposed(
            days, sources(*(r.source_refs for r in rules)), evidence="verified",
            reason="transition_preparation_mapping_missing", unit="day"))
    plan = tuple(result)
    try:
        validate(plan, snapshot, kb)
    except InputValidationError as error:
        if error.code not in ("invalid_season_interval", "date_out_of_range", "incompatible_profile"):
            raise
        return ScopeIssue("derived_" + error.code, all_choices, tuple(original[i].season_id for i, _ in raw),
                          error.field_paths, kind="excluded")
    refs = sources(*(getattr(s, name).source_refs for s in plan for name in
                     ("crop_id", "profile_id") + DATE_FIELDS + ("preparation_days_after_release",)))
    return plan, tuple(sorted(template_ids)), refs, tuple(explanations)
