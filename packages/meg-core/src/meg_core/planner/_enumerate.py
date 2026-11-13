"""Restartable lazy products. Never cache a date range or a slot Cartesian product."""

from datetime import date
from heapq import merge
from itertools import combinations

from ._types import DateRangeChoice

FIELDS = ("crop_id", "profile_id", "sowing_date")


def values(choice):
    if isinstance(choice, DateRangeChoice):
        return (date.fromordinal(day).isoformat() for day in
                range(choice.start.toordinal(), choice.end.toordinal() + 1, choice.step_days))
    return iter(choice.allowed_values)


def contains(choice, value):
    if isinstance(choice, DateRangeChoice):
        day = date.fromisoformat(value)
        return choice.start <= day <= choice.end and (day - choice.start).days % choice.step_days == 0
    return value in choice.allowed_values


def field_options(season, name, choices):
    original = getattr(season, name).value
    baseline = original.isoformat() if isinstance(original, date) else original
    yield baseline, ()
    relevant = tuple(c for c in choices if c.season_id == season.season_id and c.field == name)
    previous = None
    for value in merge(*(values(c) for c in relevant)):
        if value == previous:
            continue
        previous = value
        if value != baseline:
            yield value, tuple(sorted(c.choice_id for c in relevant if contains(c, value)))


def slot_edits(season, choices, index=0, edits=()):
    if index == len(FIELDS):
        if edits:
            yield edits
        return
    name = FIELDS[index]
    for value, ids in field_options(season, name, choices):
        yield from slot_edits(season, choices, index + 1, edits + ((name, value, ids),) if ids else edits)


def combinations_for_slots(plan, choices, slots, index=0, edits=()):
    if index == len(slots):
        yield edits
        return
    slot = slots[index]
    for edit in slot_edits(plan[slot], choices):
        yield from combinations_for_slots(plan, choices, slots, index + 1, edits + ((slot, edit),))


def raw_combinations(plan, choices):
    editable = tuple(i for i, season in enumerate(plan) if any(c.season_id == season.season_id for c in choices))
    for count in range(1, len(editable) + 1):
        for slots in combinations(editable, count):
            yield from combinations_for_slots(plan, choices, slots)
