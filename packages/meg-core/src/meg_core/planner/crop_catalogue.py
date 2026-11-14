"""Twelve-crop catalogue with explicit capability levels, layered on `kb_adapter.adapt`.

PROPOSED, research-only. Pure: takes the reviewed catalogue document and the dicts
Refaat's loader returned; never reads files, never approves evidence, adds no rules.

Levels (each is a separate approval, never implied by the previous one):
  research_record      informational only; never a planner profile, never offered.
  runtime_profile      a planner Profile exists, so stored plans can bind to it.
  review_candidate     may be offered for explicit exploration; results stay review-only
                       until approved rules exist.
  feasibility_eligible requires recorded approval; refused while approval is pending.
"""

from dataclasses import dataclass, replace

from ._types import KnowledgeBase, Profile, SourceRef
from ._validation import require, text
from .kb_adapter import Unmapped, adapt

LEVELS = ("research_record", "runtime_profile", "review_candidate", "feasibility_eligible")
_RUNTIME = LEVELS[1:]


@dataclass(frozen=True)
class CropRecord:
    crop_id: str
    scientific_name: str
    name_ar: str
    name_en: str
    purpose: str
    level: str
    origin: str
    approval: str
    evidence_refs: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class ProfileProposal:
    profile_id: str
    crop_id: str
    purpose: str
    evidence_refs: tuple[str, ...]
    decision_required: str


@dataclass(frozen=True)
class EvidenceConflict:
    conflict_id: str
    crop_id: str
    topic: str
    status: str
    blocks_rule_ids: tuple[str, ...]
    claims: tuple[tuple[str, str, str], ...]  # (origin, text, scope), verbatim


@dataclass(frozen=True)
class Catalogue:
    catalogue_version: str
    records: tuple[CropRecord, ...]
    proposals: tuple[ProfileProposal, ...]
    conflicts: tuple[EvidenceConflict, ...]


@dataclass(frozen=True)
class CatalogueKB:
    kb: KnowledgeBase
    unmapped: tuple[Unmapped, ...]
    catalogue: Catalogue


def _strings(values, path):
    require(type(values) is list, "list_required", path)
    for value in values:
        text(value, path)
    return tuple(values)


def load_catalogue(doc) -> Catalogue:
    """Validate a catalogue document. Malformed or over-claiming input is refused."""
    require(type(doc) is dict, "catalogue_required", "catalogue")
    require(doc.get("status") == "proposed_not_runtime_release", "catalogue_must_be_proposed", "catalogue.status")
    text(doc.get("catalogue_version"), "catalogue.catalogue_version")
    records, seen = [], set()
    for item in doc.get("crops") or ():
        require(type(item) is dict, "crop_required", "catalogue.crops")
        for key in ("crop_id", "scientific_name", "purpose", "level", "origin", "approval"):
            text(item.get(key), "catalogue.crops." + key)
        cid = item["crop_id"]
        require(cid not in seen, "duplicate_crop_id", cid)
        seen.add(cid)
        require(item["level"] in LEVELS, "unknown_level", cid)
        require(item["level"] != "feasibility_eligible" or item["approval"] == "approved",
                "feasibility_requires_approval", cid)
        names = item.get("names") or {}
        text(names.get("ar-EG"), cid + ".names.ar-EG")
        text(names.get("en"), cid + ".names.en")
        records.append(CropRecord(cid, item["scientific_name"], names["ar-EG"], names["en"], item["purpose"],
                                  item["level"], item["origin"], item["approval"],
                                  _strings(item.get("evidence_refs"), cid + ".evidence_refs"),
                                  _strings(item.get("blockers"), cid + ".blockers")))
    require(bool(records), "catalogue_empty", "catalogue.crops")
    proposals = []
    for item in doc.get("profile_proposals") or ():
        for key in ("profile_id", "crop_id", "purpose", "decision_required"):
            text(item.get(key), "catalogue.profile_proposals." + key)
        require(item["crop_id"] in seen, "unknown_crop", item["profile_id"])
        require(item.get("status") == "proposed", "proposal_must_be_proposed", item["profile_id"])
        refs = _strings(item.get("evidence_refs"), item["profile_id"] + ".evidence_refs")
        require(bool(refs), "proposal_needs_evidence", item["profile_id"])
        proposals.append(ProfileProposal(item["profile_id"], item["crop_id"], item["purpose"], refs,
                                         item["decision_required"]))
    conflicts = []
    for item in doc.get("conflicts") or ():
        for key in ("conflict_id", "crop_id", "topic", "status"):
            text(item.get(key), "catalogue.conflicts." + key)
        claims = item.get("claims") or []
        require(type(claims) is list and len(claims) >= 2, "conflict_needs_two_claims", item["conflict_id"])
        conflicts.append(EvidenceConflict(item["conflict_id"], item["crop_id"], item["topic"], item["status"],
                                          _strings(item.get("blocks_refaat_rule_ids") or [], item["conflict_id"]),
                                          tuple((c["origin"], c["text"], c["scope"]) for c in claims)))
    return Catalogue(doc["catalogue_version"], tuple(records), tuple(proposals), tuple(conflicts))


def crop_ids(catalogue, *, purpose=None, minimum_level="research_record"):
    """Crop IDs at or above a level, optionally for one exact purpose."""
    require(minimum_level in LEVELS, "unknown_level", "minimum_level")
    floor = LEVELS.index(minimum_level)
    found = {r.crop_id for r in catalogue.records
             if LEVELS.index(r.level) >= floor and (purpose is None or r.purpose == purpose)}
    if purpose is not None and LEVELS.index("review_candidate") >= floor:
        found |= {p.crop_id for p in catalogue.proposals if p.purpose == purpose}
    return tuple(sorted(found))


def exploration_crop_ids(catalogue, purpose):
    """Crops that may be OFFERED for explicit farmer-confirmed exploration of one purpose."""
    return crop_ids(catalogue, purpose=purpose, minimum_level="review_candidate")


def build_planner_kb(catalogue, *, refaat_crops, enforceable_rules, kb_version, data_release, site_id,
                     season_labels) -> CatalogueKB:
    """Planner KB = Refaat profiles + proposed runtime profiles; rules only from the adapter."""
    require(isinstance(catalogue, Catalogue), "catalogue_required", "catalogue")
    require(type(enforceable_rules) is list, "list_required", "enforceable_rules")
    refaat_ids = {c.get("crop_id") for c in refaat_crops if type(c) is dict}
    for record in catalogue.records:
        if record.origin == "refaat_kb":
            require(record.crop_id in refaat_ids, "refaat_crop_missing", record.crop_id)
    blocked = {rid for c in catalogue.conflicts if c.status != "resolved" for rid in c.blocks_rule_ids}
    held = [r for r in enforceable_rules if type(r) is dict and r.get("rule_id") in blocked]
    adapted = adapt(crops=refaat_crops, enforceable_rules=[r for r in enforceable_rules if r not in held],
                    kb_version=kb_version, data_release=data_release, site_id=site_id, season_labels=season_labels)
    profiles = list(adapted.kb.profiles)
    present = {p.profile_id for p in profiles}
    for record in catalogue.records:
        if record.level in _RUNTIME and record.crop_id not in present:
            refs = tuple(SourceRef(catalogue.catalogue_version, ref) for ref in record.evidence_refs)
            profiles.append(Profile(record.crop_id, record.crop_id, record.purpose, refs, "proposed"))
            present.add(record.crop_id)
    for proposal in catalogue.proposals:
        require(proposal.profile_id not in present, "duplicate_profile_id", proposal.profile_id)
        refs = tuple(SourceRef(catalogue.catalogue_version, ref) for ref in proposal.evidence_refs)
        profiles.append(Profile(proposal.profile_id, proposal.crop_id, proposal.purpose, refs, "proposed"))
        present.add(proposal.profile_id)
    unmapped = adapted.unmapped + tuple(Unmapped(r["rule_id"], "unresolved_evidence_conflict") for r in held)
    kb = replace(adapted.kb, profiles=tuple(sorted(profiles, key=lambda p: p.profile_id)))
    return CatalogueKB(kb, tuple(sorted(unmapped, key=lambda u: (u.rule_id, u.reason))), catalogue)
