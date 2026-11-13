"""Content identities, independent of object repr, locale, clocks and hash seeds."""

from dataclasses import fields, is_dataclass
from datetime import date
import hashlib
import json
from typing import Mapping


def normalized(value):
    if is_dataclass(value):
        result = {f.name: normalized(getattr(value, f.name)) for f in fields(value)}
        # Source-ref list order has no scientific meaning; every other provenance field does.
        if isinstance(result.get("source_refs"), list):
            result["source_refs"].sort(key=lambda r: json.dumps(r, sort_keys=True))
        return result
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {k: normalized(v) for k, v in sorted(value.items())}
    if isinstance(value, tuple):
        return [normalized(v) for v in value]
    return value


def canonical(value) -> str:
    return json.dumps(normalized(value), sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _without_confirmation(value):
    # Preview runs on unconfirmed intake (blueprint "planning-scopes" flow). Binding the
    # hash to fact values, not to their later confirmation, lets the confirmed snapshot
    # bind the reviewed scope. generate() still requires every fact to be confirmed.
    if isinstance(value, dict):
        return {k: _without_confirmation(v) for k, v in value.items() if k != "confirmation_status"}
    if isinstance(value, list):
        return [_without_confirmation(v) for v in value]
    return value


def context(snapshot):
    i = snapshot.input
    return _without_confirmation(normalized((snapshot.data_release, i.site_id, i.field_id, i.seasons,
            tuple(sorted(i.commitments, key=lambda c: c.commitment_id)),
            tuple(sorted(i.field_facts)), tuple(sorted(i.production_requirements, key=lambda r: r.requirement_id)),
            i.priority_order, tuple(sorted(i.independent_facts, key=canonical)),
            tuple(sorted(i.authorized_template_ids)), tuple(sorted(i.hypothetical_template_ids)))))


def plan_key(plan) -> str:
    return canonical(plan)
