"""Twelve-crop catalogue: evidence gating, purpose filtering and UH-001 regressions.

Signed/enforceable rules below are SYNTHETIC stand-ins; the delivered Refaat release has none.
Set MEG_AGRI_KB to Refaat's knowledge_base/agricultural_kb.json for the real-release checks.
"""

from dataclasses import replace
from datetime import date
import json
import os
from pathlib import Path
import unittest

from test_constraints import uh001
from test_generation import authorized, date_choice
from meg_core.planner import constraints
from meg_core.planner.crop_catalogue import build_planner_kb, crop_ids, exploration_crop_ids, load_catalogue
from meg_core.planner.generate import generate
from meg_core.planner.scope import prepare_scope
from meg_core.planner.service import plan as plan_service
from meg_core.planner._types import CatalogueChoice, ExplorationChoice, ScopeRequest, SearchPolicy
from meg_core.planner._validation import InputValidationError

CATALOGUE = Path(__file__).resolve().parents[3] / "docs" / "planner" / "crop-catalogue.v0.1-proposed.json"
# The crop list from Refaat's delivered KB (checked against the real file when MEG_AGRI_KB is set).
REFAAT_CROPS = [{"crop_id": "wheat", "purpose": "grain"},
                {"crop_id": "berseem", "purpose": "forage_or_seed_requires_review"},
                {"crop_id": "grain_maize", "purpose": "grain"},
                {"crop_id": "grain_sorghum", "purpose": "grain"}]
RELEASE = "catalogue-test-release"
ORIGINAL_FOUR = {"wheat", "berseem", "grain_maize", "grain_sorghum"}
ADDED_EIGHT = {"rice", "sugar_beet", "watermelon", "strawberry", "egyptian_cotton", "faba_bean", "cantaloupe", "harankash"}


def catalogue_doc():
    return json.loads(CATALOGUE.read_text(encoding="utf-8"))


def signed(rule_id, crop, start, end):
    """SYNTHETIC signed sowing window, as Refaat's get_enforceable_rules() would return it."""
    return {"rule_id": rule_id, "crop_ids": [crop], "rule_type": "sowing_window", "source_ids": ["SYNTHETIC-ONLY"],
            "conditions": {}, "enforceability": {"enforceable": True, "blockers": []},
            "enforcement": {"status": "ENABLED", "constraint": {"kind": "calendar_window", "field": "sowing_date",
                                                                  "start_month_day": start, "end_month_day": end}}}


def uh001_on_catalogue(enforceable_rules=()):
    """UH-001 bound to catalogue profiles: S1 forage berseem uses the proposed forage profile."""
    plan, snapshot, _ = uh001()
    profile = {"berseem": "berseem-forage-proposed"}
    plan = tuple(replace(s, profile_id=replace(s.profile_id, value=profile.get(s.crop_id.value, s.crop_id.value)))
                 for s in plan)
    snapshot = replace(snapshot, data_release=RELEASE, input=replace(snapshot.input, seasons=plan))
    built = build_planner_kb(load_catalogue(catalogue_doc()), refaat_crops=REFAAT_CROPS,
                             enforceable_rules=list(enforceable_rules), kb_version="crop-research-20261111-v1",
                             data_release=RELEASE, site_id="sakha", season_labels=tuple(s.season_label for s in plan))
    return plan, snapshot, built


class CatalogueRecords(unittest.TestCase):
    def setUp(self):
        self.catalogue = load_catalogue(catalogue_doc())

    def test_all_twelve_records_preserved_with_levels(self):
        self.assertEqual(set(crop_ids(self.catalogue)), ORIGINAL_FOUR | ADDED_EIGHT)
        levels = {r.crop_id: r.level for r in self.catalogue.records}
        self.assertEqual({c for c, lvl in levels.items() if lvl == "research_record"},
                         {"watermelon", "strawberry", "cantaloupe", "harankash"})
        self.assertNotIn("feasibility_eligible", levels.values())
        self.assertTrue(all(r.approval == "pending" for r in self.catalogue.records))
        for crop in ("cantaloupe", "harankash"):
            record = next(r for r in self.catalogue.records if r.crop_id == crop)
            self.assertTrue(any(b.startswith("not_representable:") for b in record.blockers))

    def test_purpose_filtering_is_exact(self):
        self.assertEqual(exploration_crop_ids(self.catalogue, "grain"),
                         ("faba_bean", "grain_maize", "grain_sorghum", "rice", "wheat"))
        self.assertEqual(exploration_crop_ids(self.catalogue, "forage"), ("berseem",))  # via proposal only
        self.assertEqual(exploration_crop_ids(self.catalogue, "seed"), ())
        self.assertEqual(exploration_crop_ids(self.catalogue, "fresh_fruit"), ())
        self.assertEqual(crop_ids(self.catalogue, purpose="fresh_fruit"),
                         ("cantaloupe", "harankash", "strawberry", "watermelon"))

    def test_overclaiming_catalogues_are_refused(self):
        bad = []
        doc = catalogue_doc(); doc["crops"][4]["level"] = "feasibility_eligible"; bad.append(doc)
        doc = catalogue_doc(); doc["crops"][0]["level"] = "approved_for_everything"; bad.append(doc)
        doc = catalogue_doc(); doc["crops"].append(dict(doc["crops"][0])); bad.append(doc)
        doc = catalogue_doc(); doc["status"] = "runtime_release"; bad.append(doc)
        doc = catalogue_doc(); doc["profile_proposals"][0]["evidence_refs"] = []; bad.append(doc)
        for doc in bad:
            with self.subTest(), self.assertRaises(InputValidationError):
                load_catalogue(doc)


class EvidenceGating(unittest.TestCase):
    def test_refaat_four_load_and_research_only_crops_are_not_profiles(self):
        _, _, built = uh001_on_catalogue()
        crops = {p.crop_id for p in built.kb.profiles}
        self.assertTrue(ORIGINAL_FOUR <= crops)
        self.assertEqual(crops & {"watermelon", "strawberry", "cantaloupe", "harankash"}, set())
        self.assertEqual(built.kb.rules, ())
        proposed = {p.profile_id: p.evidence_status for p in built.kb.profiles}
        self.assertEqual(proposed["rice"], "proposed")
        self.assertEqual(proposed["berseem"], "open")  # Refaat's record, unchanged

    def test_unapproved_or_conflicted_rules_never_become_enforceable(self):
        unsigned = dict(signed("C14", "grain_maize", "05-01", "05-31"), enforceability={"enforceable": False})
        _, _, built = uh001_on_catalogue([unsigned, signed("C01", "wheat", "11-10", "11-30")])
        self.assertEqual(built.kb.rules, ())
        reasons = {(u.rule_id, u.reason) for u in built.unmapped}
        self.assertIn(("C01", "unresolved_evidence_conflict"), reasons)
        self.assertIn(("C14", "not_enforceable"), reasons)
        # A signed rule outside any conflict does map: the gate is specific, not a blanket drop.
        _, _, ok = uh001_on_catalogue([signed("C14", "grain_maize", "05-01", "05-31")])
        self.assertTrue(ok.kb.rules)

    def test_wheat_window_conflict_keeps_both_claims_verbatim(self):
        (conflict,) = load_catalogue(catalogue_doc()).conflicts
        texts = {origin: text for origin, text, _ in conflict.claims}
        self.assertEqual(texts["refaat_kb"], "10 Nov to 30 Nov")
        self.assertTrue(texts["ledger"].startswith("15-30 Nov"))
        self.assertEqual(conflict.status, "unresolved_pending_signoff")

    def test_berseem_purpose_needs_explicit_forage_profile(self):
        plan, snapshot, built = uh001_on_catalogue()
        raw = tuple(replace(s, profile_id=replace(s.profile_id, value="berseem")) if s.season_id == "s1" else s
                    for s in plan)
        with self.assertRaises(InputValidationError):  # Refaat's unresolved purpose cannot bind a forage season
            constraints.evaluate(raw, replace(snapshot, input=replace(snapshot.input, seasons=raw)), built.kb)
        self.assertEqual(sorted(p.purpose for p in built.kb.profiles if p.crop_id == "berseem"),
                         ["forage", "forage_or_seed_requires_review"])

    def test_research_only_crop_cannot_be_offered(self):
        plan, snapshot, built = uh001_on_catalogue()
        draft = replace(snapshot, input=replace(snapshot.input, journey="explore"))
        preview = prepare_scope(ScopeRequest(snapshot=draft, choices=(
            ExplorationChoice("fruit", "s4", "crop_id", ("watermelon",)),),
            catalogue_choices=(CatalogueChoice("cat", "s4", "crop_id", ("strawberry",)),)), built.kb)
        self.assertNotIn("watermelon", preview.available_crop_ids)
        self.assertEqual({i.code for i in preview.issues}, {"catalogue_value_unavailable", "catalogue_choices_unavailable"})
        self.assertTrue(all(i.kind == "blocked" for i in preview.issues))


class Uh001OnCatalogue(unittest.TestCase):
    def test_uh001_results_unchanged(self):
        plan, snapshot, built = uh001_on_catalogue()
        choices = (date_choice("2027-05-28", "2027-06-01"),
                   ExplorationChoice("grain-crops", "s2", "crop_id", tuple(c for c in exploration_crop_ids(
                       built.catalogue, "grain") if c != "grain_maize")))
        result = plan_service(authorized(snapshot, built.kb, choices), built.kb, SearchPolicy())
        self.assertEqual(result.current.status, "rejected")
        self.assertEqual(result.current.checks[0].explanation.code, "sowing_before_protected_cut")
        self.assertEqual(result.feasible_alternatives, ())
        self.assertEqual({c.plan[1].sowing_date.value for c in result.review_investigations},
                         {date(2027, 5, 28), date(2027, 6, 1)})
        for candidate in result.review_investigations:
            self.assertEqual(candidate.plan[0].harvest_or_cut_date, plan[0].harvest_or_cut_date)  # 20 May kept
            self.assertIsNone(candidate.plan[1].release_date.value)  # unknown stays unknown
        # Maize is a protected crop in S2, so every crop swap there is excluded, never relaxed.
        self.assertTrue(any(e.code == "choice_conflicts_with_protected_commitment" for e in result.exclusions))

    def test_crop_swap_without_evidence_is_blocked_not_dated(self):
        plan, snapshot, built = uh001_on_catalogue()
        snapshot = replace(snapshot, input=replace(snapshot.input, commitments=tuple(
            c for c in snapshot.input.commitments if c.season_id != "s3")))
        result = generate(authorized(snapshot, built.kb, (ExplorationChoice("rice", "s3", "crop_id", ("rice",)),)),
                          built.kb, SearchPolicy())
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.search.status, "incomplete")
        self.assertEqual(result.search.uninstantiated_choice_ids, ("rice",))


@unittest.skipUnless(os.environ.get("MEG_AGRI_KB"), "set MEG_AGRI_KB to Refaat's agricultural_kb.json")
class RealRefaatRelease(unittest.TestCase):
    def test_fixture_matches_delivered_release_and_nothing_is_signed(self):
        doc = json.loads(Path(os.environ["MEG_AGRI_KB"]).read_text(encoding="utf-8"))
        self.assertEqual([{"crop_id": c["crop_id"], "purpose": c["purpose"]} for c in doc["crops"]], REFAAT_CROPS)
        self.assertEqual(sum(r["approval"]["status"] == "APPROVED" for r in doc["rules"]), 0)
        c01 = next(r for r in doc["rules"] if r["rule_id"] == "C01")
        self.assertEqual(c01["parameters"]["source_text"], "10 Nov to 30 Nov")
        built = build_planner_kb(load_catalogue(catalogue_doc()), refaat_crops=doc["crops"], enforceable_rules=[],
                                 kb_version=doc["kb_version"], data_release=RELEASE, site_id="sakha",
                                 season_labels=("winter-2026", "summer-2027", "winter-2027", "summer-2028"))
        self.assertEqual(built.kb.rules, ())


if __name__ == "__main__":
    unittest.main()
