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

__all__ = ["InputValidationError", "Release", "load_release", "run_promise_test", "decode_input"]

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


def load_release(path: Path) -> Release:
    """Load a KB. Today the only one is the UH-001 planner fixture: NOT a runtime agronomy release (Refaat owns that)."""
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
    draft = replace(snapshot, input=replace(snapshot.input, journey="explore")) if (choices or catalogue) else snapshot
    preview = prepare_scope(ScopeRequest(snapshot=draft, choices=choices, catalogue_choices=catalogue), release.kb)
    bound = draft
    if preview.choices or preview.issues:
        extra = {"scope_hash": preview.scope_hash, "exploration_confirmed": True} if confirm else {}
        bound = replace(draft, input=replace(draft.input, exploration=preview.choices, pending_scope_issues=preview.issues, **extra))
    result = plan_service(bound, release.kb, SearchPolicy())
    return {"synthetic": release.synthetic, "exploration_confirmed": confirm, "preview": encode(preview), "result": encode(result)}
