"""Offline KB loading, validation, evidence retrieval and approval gates."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path

from .validation import KBError, strict_json, validate

DEFAULT_KB = Path(__file__).resolve().parents[1] / "knowledge_base/agricultural_kb.json"
SCHEMA = Path(__file__).with_name("schema.json")


def approval_scope_sha256(rule: dict, evidence: list[dict], sources: list[dict]) -> str:
    """Bind a sign-off to all rule fields except approval, plus linked evidence/sources.

    A digest records scope, not reviewer authentication. Only reviewed repository
    releases may be trusted as approval inputs; never accept user-supplied KBs.
    """
    body = {key: value for key, value in rule.items() if key != "approval"}
    eids = set(rule["evidence_ids"])
    linked = sorted((e for e in evidence if e["evidence_id"] in eids), key=lambda e: e["evidence_id"])
    sids = set(rule["source_ids"]) | {sid for e in linked for sid in e["source_ids"]}
    linked_sources = sorted((s for s in sources if s["source_id"] in sids), key=lambda s: s["source_id"])
    raw = json.dumps({"rule": body, "evidence": linked, "sources": linked_sources},
                     ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AgriculturalKB:
    """Validated snapshot. All public return values are detached JSON structures."""

    def __init__(self, document: dict):
        try:
            # Reject non-JSON in-memory values, NaN, and booleans masquerading as numbers.
            payload = json.dumps(document, allow_nan=False)
            self._doc = strict_json(payload)
            validate(self._doc, strict_json(SCHEMA.read_bytes()))
        except (OSError, ValueError, TypeError, RecursionError) as exc:
            if isinstance(exc, KBError):
                raise
            raise KBError("INVALID_KB", "$", str(exc)) from exc
        self._crops = self._index("crops", "crop_id")
        self._localities = self._index("localities", "locality_id")
        self._sources = self._index("sources", "source_id")
        self._evidence = self._index("evidence", "evidence_id")
        self._rules = self._index("rules", "rule_id")
        self._validate_links()

    def _index(self, name, key):
        result = {}
        for item in self._doc[name]:
            if item[key] in result:
                raise KBError("DUPLICATE_ID", name, "Duplicate " + item[key])
            result[item[key]] = item
        return result

    def _refs(self, ids, index, path):
        for identifier in ids:
            if identifier not in index:
                raise KBError("BROKEN_REFERENCE", path, "Unknown reference: " + identifier)

    def _validate_links(self):
        for evidence in self._evidence.values():
            self._refs(evidence["source_ids"], self._sources, evidence["evidence_id"])
            self._date(evidence["review_date"], evidence["evidence_id"])
        for crop in self._crops.values():
            self._refs(crop["rule_ids"], self._rules, crop["crop_id"])
            expected = {r["rule_id"] for r in self._rules.values() if crop["crop_id"] in r["crop_ids"]}
            if expected != set(crop["rule_ids"]):
                raise KBError("BROKEN_REFERENCE", crop["crop_id"], "Crop/rule links are not reciprocal")
        for rule in self._rules.values():
            rid = rule["rule_id"]
            self._refs(rule["crop_ids"], self._crops, rid)
            self._refs(rule["source_ids"], self._sources, rid)
            self._refs(rule["evidence_ids"], self._evidence, rid)
            local = rule["local_applicability"]
            self._refs(local["locality_ids"], self._localities, rid)
            if local["status"] == "APPLICABLE" and not all((local["reviewer"], local["reference"])):
                raise KBError("INCOMPLETE_APPLICABILITY", rid, "Local applicability requires reviewer and record")
            for eid in rule["evidence_ids"]:
                if not set(self._evidence[eid]["source_ids"]).intersection(rule["source_ids"]):
                    raise KBError("BROKEN_REFERENCE", rid, "Evidence does not link the rule's sources")
            constraint = rule["enforcement"]["constraint"]
            if constraint and constraint["kind"] == "numeric_range" and constraint["lower"] > constraint["upper"]:
                raise KBError("INVALID_KB", rid, "Inverted numeric bounds")
            if constraint and constraint["kind"] == "calendar_window":
                for key in ("start_month_day", "end_month_day"):
                    self._date("2000-" + constraint[key], rid)
            approval = rule["approval"]
            if approval["approved_on"] is not None:
                self._date(approval["approved_on"], rid)
            if approval["status"] == "APPROVED":
                if not all(approval[k] for k in ("reviewer", "approved_on", "reference", "scope_sha256")):
                    raise KBError("INCOMPLETE_APPROVAL", rid, "Approved rules require dated, scope-bound sign-off")
                actual = approval_scope_sha256(rule, self._doc["evidence"], self._doc["sources"])
                if approval["scope_sha256"] != actual:
                    raise KBError("STALE_APPROVAL", rid, "Rule/evidence changed after sign-off")

    @staticmethod
    def _date(value, path):
        try:
            if date.fromisoformat(value).isoformat() != value:
                raise ValueError("Noncanonical date")
        except (TypeError, ValueError) as exc:
            raise KBError("INVALID_KB", path, "Expected a real ISO date") from exc

    def _get(self, index, identifier, label):
        if not isinstance(identifier, str) or identifier not in index:
            raise KBError("UNKNOWN_ID", label, "Unknown " + label)
        return index[identifier]

    def get_crop(self, crop_id: str) -> dict:
        return deepcopy(self._get(self._crops, crop_id, "crop_id"))

    def get_crops(self) -> list[dict]:
        return deepcopy(list(self._crops.values()))

    def get_evidence(self, evidence_id: str | None = None) -> dict | list[dict]:
        return deepcopy(list(self._evidence.values()) if evidence_id is None else
                        self._get(self._evidence, evidence_id, "evidence_id"))

    def get_sources(self, source_id: str | None = None) -> dict | list[dict]:
        return deepcopy(list(self._sources.values()) if source_id is None else
                        self._get(self._sources, source_id, "source_id"))

    def _blockers(self, rule, locality, conditions):
        reasons = []
        if rule["scientific_status"] != "VERIFIED":
            reasons.append("scientific_evidence_not_verified")
        if not rule["evidence_ids"]:
            reasons.append("missing_evidence")
        elif any(self._evidence[e]["scientific_status"] != "VERIFIED" for e in rule["evidence_ids"]):
            reasons.append("linked_evidence_not_verified")
        if not rule["source_ids"]:
            reasons.append("missing_source")
        if rule["approval"]["status"] != "APPROVED":
            reasons.append("local_approval_" + rule["approval"]["status"].lower())
        local = rule["local_applicability"]
        if local["status"] != "APPLICABLE":
            reasons.append("local_applicability_" + local["status"].lower())
        if locality is None:
            reasons.append("locality_required")
        elif locality not in local["locality_ids"]:
            reasons.append("outside_locality_scope")
        for key, values in rule["conditions"].items():
            if key not in conditions:
                reasons.append("missing_condition:" + key)
            elif conditions[key] not in values:
                reasons.append("condition_mismatch:" + key)
        if rule["unresolved_requirements"]:
            reasons.append("unresolved_review_requirements")
        if rule["enforcement"]["status"] != "ENABLED":
            reasons.append("planner_activation_disabled")
        if rule["enforcement"]["constraint"] is None:
            reasons.append("missing_structured_constraint")
        return reasons

    def get_rules(self, *, crop_id=None, locality=None, conditions=None, view="all") -> list[dict]:
        """Views: all, supported (VERIFIED), pending (not enforceable), unverified,
        approved (local sign-off), enforceable (all gates and explicit query match).

        Locality filters review scope, not scientific study location. Conditions
        filter conflicting values; missing conditions remain visible but blocked.
        """
        if type(view) is not str or view not in {"all", "supported", "pending", "unverified", "approved", "enforceable"}:
            raise KBError("INVALID_QUERY", "view", "Unknown rule view")
        if crop_id is not None:
            self._get(self._crops, crop_id, "crop_id")
        if locality is not None:
            self._get(self._localities, locality, "locality")
        conditions = {} if conditions is None else conditions
        if type(conditions) is not dict or any(type(k) is not str or not k.strip() or
                                              type(v) is not str or not v.strip() for k, v in conditions.items()):
            raise KBError("INVALID_QUERY", "conditions", "Expected nonempty string keys and values")
        result = []
        for rule in self._rules.values():
            if crop_id is not None and crop_id not in rule["crop_ids"]:
                continue
            if locality is not None and locality not in rule["local_applicability"]["locality_ids"]:
                continue
            if any(k in conditions and conditions[k] not in values for k, values in rule["conditions"].items()):
                continue
            reasons = self._blockers(rule, locality, conditions)
            supported = rule["scientific_status"] == "VERIFIED" and bool(rule["evidence_ids"]) and all(
                self._evidence[e]["scientific_status"] == "VERIFIED" for e in rule["evidence_ids"])
            if ((view == "supported" and not supported) or (view == "unverified" and supported) or
                (view == "pending" and not reasons) or (view == "enforceable" and reasons) or
                (view == "approved" and rule["approval"]["status"] != "APPROVED")):
                continue
            result.append({**deepcopy(rule), "enforceability": {
                "enforceable": not reasons, "status": "ENFORCEABLE" if not reasons else "BLOCKED",
                "blockers": reasons, "locality": locality, "conditions": deepcopy(conditions)}})
        return result

    def get_approved_rules(self, **query):
        """Locally signed rules; still inspect enforceability for the query."""
        return self.get_rules(view="approved", **query)

    def get_enforceable_rules(self, *, locality, **query):
        return self.get_rules(view="enforceable", locality=locality, **query)

    def get_pending_rules(self, **query):
        return self.get_rules(view="pending", **query)

    def get_status(self, *, locality=None, conditions=None) -> dict:
        rules = self.get_rules(locality=locality, conditions=conditions)
        approved = sum(r["approval"]["status"] == "APPROVED" for r in rules)
        enforceable = sum(r["enforceability"]["enforceable"] for r in rules)
        return {"schema_version": self._doc["schema_version"], "kb_version": self._doc["kb_version"],
                "locality": locality, "rules": len(rules), "locally_approved_rules": approved,
                "enforceable_rules": enforceable,
                "status": "NO_LOCAL_SIGN_OFF" if not approved else
                          ("HAS_ENFORCEABLE_RULES" if enforceable else "NO_APPLICABLE_APPROVED_RULES"),
                "scientific_status_counts": dict(Counter(r["scientific_status"] for r in rules)),
                "review": [{"rule_id": r["rule_id"], "blockers": r["enforceability"]["blockers"]}
                           for r in rules if not r["enforceability"]["enforceable"]]}


def load_kb(path: str | Path | None = None) -> AgriculturalKB:
    """Load a JSON file (default resolves relative to this package, never cwd)."""
    try:
        target = DEFAULT_KB if path is None else Path(path)
        document = strict_json(target.read_bytes())
    except (OSError, TypeError, ValueError) as exc:
        if isinstance(exc, KBError):
            raise
        raise KBError("KB_UNAVAILABLE", "kb_file", str(exc)) from exc
    return AgriculturalKB(document)
