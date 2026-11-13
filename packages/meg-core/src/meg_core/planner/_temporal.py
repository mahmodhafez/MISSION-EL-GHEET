"""Locks and one-field calendar arithmetic. No agronomic duration inference."""

from datetime import date

from ._checks import check, path, sources


def commitments(plan, snapshot):
    checks, preserved = [], []
    by_id = {s.season_id: s for s in plan}
    for lock in sorted(snapshot.input.commitments, key=lambda c: c.commitment_id):
        season = by_id[lock.season_id]
        value, missing, failed, retained = lock.protected_value.value, [], False, False
        if lock.kind in ("crop", "purpose"):
            name = "crop_id" if lock.kind == "crop" else "purpose"
            actual = getattr(season, name).value
            if actual is None:
                missing.append(path(season, name))
            else:
                retained = actual == value
                failed = not retained
        else:
            day = date.fromisoformat(value)
            name = "harvest_or_cut_date" if lock.kind == "harvest_or_cut_date" else "release_date"
            actual = getattr(season, name).value
            endpoint = "crop_end_exclusive" if lock.kind == "harvest_or_cut_date" else "release_date"
            if actual is None:
                missing.append(path(season, name))
            else:
                retained = actual == day if lock.kind == "harvest_or_cut_date" else actual > day
                failed = not retained
            for field, predicate in (("sowing_date", lambda d: d <= day), (endpoint, lambda d: d > day)):
                fact = getattr(season, field)
                if fact.value is None:
                    missing.append(path(season, field))
                elif not predicate(fact.value):
                    failed = True
            retained = retained and not failed
        if retained:
            preserved.append(lock.commitment_id)
        outcome = "fail" if failed else "unknown" if missing else "pass"
        code = {"fail": "protected_commitment_mismatch", "unknown": "protected_commitment_unverified",
                "pass": "protected_commitment_preserved"}[outcome]
        checks.append(check("commitment_preserved", outcome, code, (season.season_id,),
                            params={"commitment_id": lock.commitment_id, "season_id": season.season_id,
                                    "kind": lock.kind, "protected_value": value, "actual_value": actual},
                            paths=missing, refs=lock.protected_value.source_refs,
                            commitments=(lock.commitment_id,)))
    return checks, tuple(sorted(preserved))


def release_bound(season, locks):
    """Known intentions/locks bound release without filling the unknown Fact."""
    bounds = []
    for name, increment in (("release_date", 0), ("crop_end_exclusive", 0), ("harvest_or_cut_date", 1)):
        f = getattr(season, name)
        if f.value is not None:
            bounds.append((f.value.toordinal() + increment, name, f.source_refs))
    for lock in locks:
        if lock.season_id == season.season_id and lock.kind in ("occupation_through", "harvest_or_cut_date"):
            bounds.append((date.fromisoformat(lock.protected_value.value).toordinal() + 1,
                           lock.kind, lock.protected_value.source_refs))
    return max(bounds, key=lambda b: (b[0], b[1])) if bounds else (None, "unknown", ())


def civil(ordinal):
    return date.fromordinal(ordinal).isoformat() if ordinal is not None and ordinal <= date.max.toordinal() else None


def occupancy(plan, snapshot):
    checks = []
    locks = snapshot.input.commitments
    for i, prior in enumerate(plan):
        bound, basis, bound_refs = release_bound(prior, locks)
        for later in plan[i + 1:]:
            sow = later.sowing_date.value
            ids = (prior.season_id, later.season_id)
            protected = [c for c in locks if c.season_id == prior.season_id and
                         c.kind in ("occupation_through", "harvest_or_cut_date") and sow is not None and
                         sow <= date.fromisoformat(c.protected_value.value)]
            cut_locks = [c for c in protected if c.kind == "harvest_or_cut_date"]
            if cut_locks:
                cut = max(cut_locks, key=lambda c: (c.protected_value.value, c.commitment_id))
                checks.append(check("single_field_occupancy", "fail", "sowing_before_protected_cut", ids,
                                    params={"season_id": later.season_id, "sowing_date": sow,
                                            "protected_cut_date": cut.protected_value.value},
                                    refs=sources(*(c.protected_value.source_refs for c in protected)),
                                    commitments=tuple(c.commitment_id for c in protected)))
                continue
            if sow is not None and prior.sowing_date.value is not None and sow < prior.sowing_date.value:
                checks.append(check("single_field_occupancy", "fail", "season_order_conflict", ids,
                                    params={"prior_season_id": prior.season_id, "next_season_id": later.season_id,
                                            "prior_sowing_date": prior.sowing_date.value, "sowing_date": sow}))
                continue
            params = {"prior_season_id": prior.season_id, "next_season_id": later.season_id,
                      "sowing_date": sow, "occupancy_bound_exclusive": civil(bound), "basis": basis}
            if sow is not None and bound is not None and sow.toordinal() < bound:
                checks.append(check("single_field_occupancy", "fail", "field_occupied", ids,
                                    params=params, refs=bound_refs,
                                    commitments=tuple(c.commitment_id for c in protected)))
            else:
                missing = [path(s, name) for s, name in ((prior, "release_date"), (later, "sowing_date"))
                           if getattr(s, name).value is None]
                checks.append(check("single_field_occupancy", "unknown" if missing else "pass",
                                    "occupancy_timing_unknown" if missing else "field_available", ids,
                                    params=params, paths=missing, refs=bound_refs))
    return checks


def preparation(plan, snapshot, supported_minima):
    checks = []
    for i, prior in enumerate(plan[:-1]):
        later = plan[i + 1]
        sow, declared = later.sowing_date.value, prior.preparation_days_after_release.value
        minimum, rule_refs = supported_minima.get(prior.season_id, (None, ()))
        days = max(v for v in (minimum, declared) if v is not None) if minimum is not None or declared is not None else None
        bound, basis, bound_refs = release_bound(prior, snapshot.input.commitments)
        earliest = bound + days if bound is not None and days is not None else None
        missing = [path(s, name) for s, name in ((prior, "release_date"),
                    (prior, "preparation_days_after_release"), (later, "sowing_date")) if getattr(s, name).value is None]
        failure = sow is not None and earliest is not None and sow.toordinal() < earliest
        code = "preparation_shortfall" if failure else "transition_timing_unknown" if missing else "preparation_satisfied"
        checks.append(check("transition_preparation", "fail" if failure else "unknown" if missing else "pass", code,
                            (prior.season_id, later.season_id),
                            params={"prior_season_id": prior.season_id, "next_season_id": later.season_id,
                                    "sowing_date": sow, "release_date": prior.release_date.value,
                                    "release_lower_bound": civil(bound), "preparation_days": days,
                                    "earliest_sowing_date": civil(earliest), "basis": basis},
                            paths=missing, refs=sources(bound_refs, rule_refs, prior.preparation_days_after_release.source_refs)))
    return checks
