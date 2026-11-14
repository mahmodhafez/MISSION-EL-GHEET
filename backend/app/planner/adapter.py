"""The only bridge between the API and the meg_core planner (packages/meg-core, Amr + Astra).

Requests carry the planner's own JSON shape (snapshot + exploration), decoded into meg_core's frozen
dataclasses and run through the real `prepare_scope` and `service.plan`. The JSON codec is copied from
packages/meg-core/tools/planner_cli.py (encode/decode) so the API and the manual CLI read the same shape.
TODO(contracts): replace with meg_core.contracts mapping once the shared Pydantic contracts exist.
"""
from __future__ import annotations

import json
import sys
import types
import typing
from dataclasses import dataclass, fields, is_dataclass, replace
from datetime import date
from pathlib import Path

CORE_SRC = Path(__file__).resolve().parents[3] / "packages" / "meg-core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from meg_core.planner import _types  # noqa: E402
from meg_core.planner._types import ScopeRequest, SearchPolicy  # noqa: E402
from meg_core.planner._validation import InputValidationError  # noqa: E402
from meg_core.planner.scope import prepare_scope  # noqa: E402
from meg_core.planner.service import plan as plan_service  # noqa: E402
from meg_core.agricultural_release import bind_profiles, catalogue_view, load_reviewed_release  # noqa: E402
from agricultural_kb import KBError  # noqa: E402

__all__ = ["InputValidationError", "KBError", "Release", "ReviewedRelease", "load_release", "run_promise_test", "decode_input"]

TAGGED = (_types.Rule, _types.ExplorationChoice, _types.DateRangeChoice)


def encode(value):
    if is_dataclass(value):
        out = {"type": type(value).__name__} if isinstance(value, TAGGED) else {}
        out.update({f.name: encode(getattr(value, f.name)) for f in fields(value) if f.init})
        return out
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, typing.Mapping):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [encode(v) for v in value]
    return value


def decode(hint, data, path="$", typevars=None):
    typevars = typevars or {}
    if isinstance(hint, typing.TypeVar):
        hint = typevars.get(hint, typing.Any)
    if hint is typing.Any:
        return data
    origin, args = typing.get_origin(hint), typing.get_args(hint)
    if origin in (typing.Union, types.UnionType):
        if data is None:
            return None
        if isinstance(data, dict) and "type" in data:
            return decode(getattr(_types, data["type"]), data, path)
        options = [a for a in args if a is not type(None)]
        resolved = [typevars.get(a, a) if isinstance(a, typing.TypeVar) else a for a in options]
        return decode(resolved[0], data, path, typevars) if len(resolved) == 1 else data
    if origin is typing.Literal:
        return data
    if origin is tuple:
        if isinstance(data, dict):
            data = list(data.items())
        if not isinstance(data, list):
            raise ValueError(f"{path}: expected a list")
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(decode(args[0], v, f"{path}[{i}]", typevars) for i, v in enumerate(data))
        return tuple(decode(a, v, f"{path}[{i}]", typevars) for i, (a, v) in enumerate(zip(args, data)))
    if origin is not None and is_dataclass(origin):
        params = getattr(origin, "__parameters__", ())
        return decode(origin, data, path, dict(zip(params, args)))
    if hint is date:
        return date.fromisoformat(data) if isinstance(data, str) else data
    if isinstance(hint, type) and is_dataclass(hint):
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected an object for {hint.__name__}")
        if "type" in data and not hasattr(_types, str(data["type"])):
            raise ValueError(f"{path}: unknown type {data['type']!r}")
        cls = getattr(_types, data["type"]) if "type" in data else hint
        hints = typing.get_type_hints(cls, vars(_types))
        names = {f.name for f in fields(cls) if f.init}
        unknown = set(data) - names - {"type"}
        if unknown:
            raise ValueError(f"{path}: unknown field(s) {sorted(unknown)} for {cls.__name__}")
        kwargs = {k: decode(hints[k], v, f"{path}.{k}", typevars) for k, v in data.items() if k != "type"}
        try:
            return cls(**kwargs)
        except TypeError as error:
            raise ValueError(f"{path}: {cls.__name__}: {error}") from None
    return data


@dataclass(frozen=True)
class Release:
    data_release: str
    kb: object
    synthetic: bool
    note: str

    def catalogue(self) -> dict:
        profiles = getattr(self.kb, "profiles", ())
        return {
            "data_release": self.data_release,
            "crop_ids": sorted({p.crop_id for p in profiles}),
            "profiles": [{"profile_id": p.profile_id, "crop_id": p.crop_id, "purpose": p.purpose, "evidence_status": p.evidence_status} for p in profiles],
            "runtime": False,
            "note": self.note,
        }


class ReviewedRelease:
    """Refaat's reviewed Sakha KB (sakha-agricultural-review-2026-11-14.1), hash-pinned inside meg_core.
    Built per request for the scenario's season labels (docs/agronomy/yahya-kb-integration-handoff.md).
    0 enforceable rules today, so no plan can be feasible."""
    synthetic = False
    note = "Reviewed Sakha agricultural KB; every rule pending local sign-off, none enforced."

    def __init__(self):
        self.release = load_reviewed_release()
        self.data_release = self.release.version

    def evidenced(self) -> set[str]:
        """crop_ids that have sourced evidence in the reviewed agricultural KB."""
        return {c["crop_id"] for c in self.release.agricultural.get_crops()}

    def built(self, site_id: str, season_labels: tuple[str, ...]):
        return self.release.for_planner(site_id=site_id, season_labels=season_labels)

    def catalogue(self, first_winter_year: int | None = None) -> dict:
        y = first_winter_year or 2026
        built = self.built(self.release.site_id, (f"winter-{y}", f"summer-{y + 1}", f"winter-{y + 1}", f"summer-{y + 2}"))
        view = catalogue_view(self.release, built)
        return {
            "data_release": self.data_release,
            # Offer only crops with sourced evidence in the reviewed KB (Yahya, 14 Nov 2026): wheat, berseem, maize,
            # sorghum. Other catalogue crops (rice, faba bean, sugar beet, cotton) have no reviewed evidence yet.
            "crop_ids": [c["crop_id"] for c in view if c["offerable_purposes"] and c["crop_id"] in self.evidenced()],
            "crops": [{**c, "kb_evidence": c["crop_id"] in self.evidenced()} for c in view],
            "profiles": [{"profile_id": p.profile_id, "crop_id": p.crop_id, "purpose": p.purpose, "evidence_status": p.evidence_status} for p in built.kb.profiles],
            "runtime": True,
            "note": self.note,
        }


def load_release(path: Path | str):
    """`reviewed` → Refaat's reviewed KB (default). A JSON path → that planner fixture KB (tests, golden UH-001)."""
    if str(path) == "reviewed":
        return ReviewedRelease()
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    kb = decode(_types.KnowledgeBase, raw["kb"], "$.kb")
    synthetic = "SYNTHETIC" in json.dumps(raw["kb"])
    note = "Dev data release from the planner fixture; not a runtime agronomy release."
    return Release(data_release=kb.data_release, kb=kb, synthetic=synthetic, note=note)


def decode_input(payload: dict):
    snapshot = decode(_types.ScenarioSnapshot, payload["snapshot"], "$.snapshot")
    exploration = payload.get("exploration") or {}
    choices = decode(tuple[_types.ExplorationChoice | _types.DateRangeChoice, ...], exploration.get("choices", []), "$.exploration.choices")
    catalogue = decode(tuple[_types.CatalogueChoice, ...], exploration.get("catalogue_choices", []), "$.exploration.catalogue_choices")
    return snapshot, choices, catalogue


def run_promise_test(payload: dict, release: Release) -> dict:
    """Scope preview → bind the farmer's explicit confirmation → real planner. Mirrors planner_cli `plan`."""
    snapshot, choices, catalogue = decode_input(payload)
    if snapshot.data_release != release.data_release:
        raise InputValidationError("data_release_mismatch", ("snapshot.data_release",))
    confirm = bool(payload.get("confirm_exploration", False))
    if isinstance(release, ReviewedRelease):
        # Per-request KB for these season labels; bind each known crop to its exact (crop_id, purpose) profile.
        built = release.built(snapshot.input.site_id, tuple(s.season_label for s in snapshot.input.seasons))
        kb = built.kb
        seasons = tuple(bind_profiles((s,), kb)[0] if s.crop_id.value is not None else s for s in snapshot.input.seasons)
        snapshot = replace(snapshot, input=replace(snapshot.input, seasons=seasons))
    else:
        kb = release.kb
    draft = replace(snapshot, input=replace(snapshot.input, journey="explore")) if (choices or catalogue) else snapshot
    preview = prepare_scope(ScopeRequest(snapshot=draft, choices=choices, catalogue_choices=catalogue), kb)
    bound = draft
    if preview.choices or preview.issues:
        extra = {"scope_hash": preview.scope_hash, "exploration_confirmed": True} if confirm else {}
        bound = replace(draft, input=replace(draft.input, exploration=preview.choices, pending_scope_issues=preview.issues, **extra))
    result = plan_service(bound, kb, SearchPolicy())
    return {"synthetic": release.synthetic, "exploration_confirmed": confirm, "preview": encode(preview), "result": encode(result)}
