"""App answers → planner ScenarioSnapshot JSON (minimal mapping, 14 Nov 2026).

Each fact says where it came from. What the farmer said is `origin: farmer_report`, confirmed. The catalogue
profile binding is `origin: derived` with the KB's evidence status. Anything the app does not collect (harvest dates other than a protected cut,
crop end, release, preparation days) is an explicit confirmed unknown with `unknown_reason: not_collected`, so
the planner reports it instead of anything being assumed. No defaults, no copied fixture values.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

UNKNOWN_CROP = "unknown"


class SeasonAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    season_id: Literal["s1", "s2", "s3", "s4"]
    crop_id: str | None
    purpose: str | None = None
    sowing_date: str | None = None          # ISO date, "unknown", or null (not answered)
    last_cut_date: str | None = None        # protected last cut (berseem), ISO or null


class Permission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    season_id: Literal["s1", "s2", "s3", "s4"]
    field: Literal["sowing_date", "crop_id"]
    allowed_values: list[str] = Field(min_length=1, max_length=32)


class Answers(BaseModel):
    model_config = ConfigDict(extra="forbid")
    first_winter_year: int = Field(ge=2020, le=2100)
    journey: Literal["check", "explore"]
    seasons: list[SeasonAnswer] = Field(min_length=4, max_length=4)
    locks: dict[str, bool] = Field(default_factory=dict)
    permissions: list[Permission] = Field(default_factory=list)
    confirm_exploration: bool = False


def fact(value, *, origin: str, evidence: str = "proposed", unknown_reason: str | None = None, unit: str | None = None) -> dict:
    known = value is not None
    return {"value": value if known else None, "unknown_reason": None if known else (unknown_reason or "not_collected"),
            "origin": origin if known else "unknown", "evidence_status": evidence if known else "open",
            "confirmation_status": "confirmed" if known else "confirmed_unknown", "unit": unit,
            "source_refs": [], "method": None}


def farmer(value, reason: str = "farmer_unknown") -> dict:
    return fact(value, origin="farmer_report", unknown_reason=reason)


def missing(reason: str = "not_collected", unit: str | None = None) -> dict:
    return fact(None, origin="unknown", unknown_reason=reason, unit=unit)


def labels(first_winter_year: int) -> list[str]:
    y = first_winter_year
    return [f"winter-{y}", f"summer-{y + 1}", f"winter-{y + 1}", f"summer-{y + 2}"]


def to_payload(a: Answers, release) -> dict:
    """Build the planner-shaped request ({snapshot, exploration, confirm_exploration})."""
    # Fixture release: look the profile up here. Reviewed release: a placeholder that the adapter replaces with
    # bind_profiles() (exact crop_id + purpose, never broadened).
    profiles = getattr(getattr(release, "kb", None), "profiles", ())
    reviewed = not profiles
    seasons, commitments = [], []
    for order, (s, label) in enumerate(zip(sorted(a.seasons, key=lambda x: x.season_id), labels(a.first_winter_year)), start=1):
        known = s.crop_id not in (None, UNKNOWN_CROP)
        profile = next((p for p in profiles if known and p.crop_id == s.crop_id and (s.purpose is None or p.purpose == s.purpose)), None)
        purpose = s.purpose or (profile.purpose if profile else None)
        sow = None if s.sowing_date in (None, "unknown") else s.sowing_date
        seasons.append({
            "season_id": s.season_id, "order": order, "season_label": label,
            "crop_id": farmer(s.crop_id if known else None),
            "purpose": farmer(purpose if known else None),
            "profile_id": (fact(profile.profile_id, origin="derived", evidence=profile.evidence_status) if profile
                           else fact(s.crop_id, origin="derived") if (reviewed and known) else missing("profile_unavailable")),
            "sowing_date": farmer(sow, "farmer_unknown" if s.sowing_date == "unknown" else "not_collected"),
            "harvest_or_cut_date": farmer(s.last_cut_date) if s.last_cut_date else missing(),
            "crop_end_exclusive": missing(),
            "release_date": missing(),
            "preparation_days_after_release": missing(unit="day"),
        })
        if a.locks.get(s.season_id) and known:
            if s.last_cut_date:
                commitments += [
                    {"commitment_id": f"{s.season_id}-cut", "season_id": s.season_id, "kind": "harvest_or_cut_date", "protected_value": farmer(s.last_cut_date)},
                    {"commitment_id": f"{s.season_id}-occupation", "season_id": s.season_id, "kind": "occupation_through", "protected_value": farmer(s.last_cut_date)},
                ]
            else:
                commitments.append({"commitment_id": f"{s.season_id}-crop", "season_id": s.season_id, "kind": "crop", "protected_value": farmer(s.crop_id)})
                if purpose:
                    commitments.append({"commitment_id": f"{s.season_id}-purpose", "season_id": s.season_id, "kind": "purpose", "protected_value": farmer(purpose)})
    explore = a.journey == "explore" and bool(a.permissions)
    choices = [{"type": "ExplorationChoice", "choice_id": f"{p.season_id}-{p.field}", "season_id": p.season_id, "field": p.field,
                "allowed_values": sorted(set(p.allowed_values))} for p in a.permissions] if explore else []
    snapshot = {"data_release": release.data_release, "input": {
        "seasons": seasons, "site_id": "sakha", "field_id": "one-field", "commitments": commitments,
        "field_facts": [], "production_requirements": [], "journey": "explore" if explore else "check",
        "exploration": [], "exploration_confirmed": False, "scope_hash": None, "priority_order": ["minimize_changes"],
        "independent_facts": [], "authorized_template_ids": [], "hypothetical_template_ids": [], "pending_scope_issues": []}}
    return {"snapshot": snapshot, "exploration": {"choices": choices, "catalogue_choices": []}, "confirm_exploration": explore and a.confirm_exploration}
