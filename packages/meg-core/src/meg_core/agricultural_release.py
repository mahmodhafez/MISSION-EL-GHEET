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


def load_reviewed_release(directory: str | Path = RELEASE_DIR) -> ReviewedRelease:
    """Load this exact reviewed package. A missing/altered document raises KBError."""
    directory = Path(directory)
    manifest = _read_pinned(directory, "manifest.json", MANIFEST_SHA256)
    hashes = manifest["sha256"]
    agricultural = AgriculturalKB(_read_pinned(directory, "agricultural_kb.json", hashes["agricultural_kb.json"]))
    catalogue = load_catalogue(_read_pinned(directory, "catalogue.json", hashes["catalogue.json"]))
    _read_pinned(directory, "review.json", hashes["review.json"])
    return ReviewedRelease(agricultural, catalogue, manifest["release"], manifest["site_id"])
