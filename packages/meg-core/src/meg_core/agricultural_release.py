"""Offline composition boundary for the dated Sakha review and the pure planner."""
from dataclasses import dataclass
import hashlib
from pathlib import Path

from agricultural_kb import AgriculturalKB, KBError
from agricultural_kb.validation import strict_json
from .planner.crop_catalogue import Catalogue, CatalogueKB, build_planner_kb, load_catalogue


RELEASE_ID = "sakha-agricultural-review-2026-11-14.1"
RELEASE_DIR = Path(__file__).resolve().parents[1] / "knowledge_base" / RELEASE_ID
MANIFEST_SHA256 = "5897174ee5fb2a3a43da0ee63be8280f19c2dc11ba702083f0cae3ae27df2457"


def _read_pinned(directory, name, expected_hash):
    try:
        content = (directory / name).read_bytes()
    except OSError as exc:
        raise KBError("KB_UNAVAILABLE", name, str(exc)) from exc
    if hashlib.sha256(content).hexdigest() != expected_hash:
        raise KBError("SOURCE_INTEGRITY", name, "Reviewed release bytes differ from the pinned version")
    try:
        return strict_json(content)
    except ValueError as exc:
        raise KBError("INVALID_KB", name, str(exc)) from exc


@dataclass(frozen=True)
class ReviewedRelease:
    agricultural: AgriculturalKB
    catalogue: Catalogue
    version: str
    site_id: str

    def for_planner(self, *, site_id: str, season_labels: tuple[str, ...],
                    conditions: dict[str, str] | None = None) -> CatalogueKB:
        """Build one site-scoped planner input. Pass only server-confirmed matching facts."""
        if site_id != self.site_id:
            raise KBError("OUTSIDE_RELEASE_SCOPE", "site_id", "This review covers Sakha only")
        eligible = self.agricultural.get_enforceable_rules(locality=site_id, conditions=conditions)
        return build_planner_kb(self.catalogue, refaat_crops=self.agricultural.get_crops(),
                                enforceable_rules=eligible, kb_version=self.version,
                                data_release=self.version, site_id=site_id, season_labels=season_labels)


def bind_profiles(seasons, kb):
    """Resolve each season's planner profile by its exact (crop_id, purpose).

    A season whose crop and purpose match no profile, or more than one, raises
    InputValidationError("profile_binding_unresolved"). Purposes are never broadened:
    forage never binds a seed or 'forage_or_seed_requires_review' profile.
    """
    from dataclasses import replace
    from .planner._validation import InputValidationError
    bound = []
    for season in seasons:
        key = (season.crop_id.value, season.purpose.value)
        matches = [p.profile_id for p in kb.profiles if (p.crop_id, p.purpose) == key]
        if len(matches) != 1:
            raise InputValidationError("profile_binding_unresolved",
                                       f"plan.{season.season_id}.profile_id")
        bound.append(replace(season, profile_id=replace(season.profile_id, value=matches[0])))
    return tuple(bound)


_LEVELS = ("research_record", "runtime_profile", "review_candidate", "feasibility_eligible")


def catalogue_view(release: "ReviewedRelease", built: CatalogueKB) -> list[dict]:
    """Per-crop UI view that keeps four ideas apart: visible, offerable, enforced, feasible.

    `offerable_purposes` lists purposes a farmer may explore (results stay review-only
    without enforceable rules). Research records are visible but never offerable.
    """
    rules = release.agricultural.get_rules()
    enforced = {p.profile_id for p in built.kb.profiles if any(r.profile_id == p.profile_id for r in built.kb.rules)}
    view = []
    for record in release.catalogue.records:
        profiles = sorted((p.profile_id, p.purpose) for p in built.kb.profiles if p.crop_id == record.crop_id)
        offerable = sorted({purpose for pid, purpose in profiles
                            if _LEVELS.index(record.level) >= 2 or pid in {x.profile_id for x in release.catalogue.proposals}})
        view.append({
            "crop_id": record.crop_id, "scientific_name": record.scientific_name,
            "names": {"ar-EG": record.name_ar, "en": record.name_en}, "level": record.level,
            "approval": record.approval, "research_only": record.level == "research_record",
            "planner_profiles": [{"profile_id": pid, "purpose": purpose} for pid, purpose in profiles],
            "offerable_purposes": offerable,
            "kb_rules": sum(record.crop_id in r["crop_ids"] for r in rules),
            "enforced_profiles": sorted(pid for pid, _ in profiles if pid in enforced),
            "conflicts": sorted(c.conflict_id for c in release.catalogue.conflicts if c.crop_id == record.crop_id),
            "blockers": list(record.blockers),
            "feasibility_eligible": record.level == "feasibility_eligible",
        })
    return view


def load_reviewed_release(directory: str | Path = RELEASE_DIR) -> ReviewedRelease:
    """Load this exact reviewed package. A missing/altered document raises KBError."""
    directory = Path(directory)
    manifest = _read_pinned(directory, "manifest.json", MANIFEST_SHA256)
    hashes = manifest["sha256"]
    agricultural = AgriculturalKB(_read_pinned(directory, "agricultural_kb.json", hashes["agricultural_kb.json"]))
    catalogue = load_catalogue(_read_pinned(directory, "catalogue.json", hashes["catalogue.json"]))
    _read_pinned(directory, "review.json", hashes["review.json"])
    return ReviewedRelease(agricultural, catalogue, manifest["release"], manifest["site_id"])
