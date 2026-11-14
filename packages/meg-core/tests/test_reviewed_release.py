"""Regression tests at the real, packaged agricultural-loader to planner boundary."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

CORE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE / "src"))
sys.path.insert(0, str(CORE / "tools"))
from agricultural_kb import KBError, load_kb
from meg_core.agricultural_release import RELEASE_DIR, RELEASE_ID, load_reviewed_release
from meg_core.planner.crop_catalogue import crop_ids, exploration_crop_ids
from reviewed_uh001 import run

LABELS = ("winter-2026", "summer-2027", "winter-2027", "summer-2028")


class ReviewAssembly(unittest.TestCase):
    def test_versioned_raw_file_works_with_original_loader_and_legacy_default(self):
        current = load_kb(RELEASE_DIR / "agricultural_kb.json")
        self.assertEqual(load_kb().get_status()["kb_version"], "crop-research-20261111-v1")
        self.assertEqual(current.get_status()["kb_version"], RELEASE_ID)
        self.assertEqual([r["rule_id"] for r in current.get_rules()], [f"C{i:02d}" for i in range(1,28)])
        self.assertEqual(len(current.get_rules(view="supported")), 18)
        self.assertEqual(current.get_approved_rules(), [])
        self.assertEqual(len(current.get_pending_rules(locality="sakha")), 27)

    def test_scope_and_no_enforcement_for_confirmed_field_facts(self):
        release = load_reviewed_release()
        built = release.for_planner(site_id="sakha", season_labels=LABELS,
                                    conditions={"purpose":"grain","cultivar":"Sakha 95"})
        self.assertEqual((built.kb.rules, built.kb.templates), ((), ()))
        self.assertEqual(built.kb.data_release, release.version)
        with self.assertRaises(KBError) as err:
            release.for_planner(site_id="unreviewed-site", season_labels=LABELS)
        self.assertEqual(err.exception.code, "OUTSIDE_RELEASE_SCOPE")

    def test_profile_boundary_and_purpose_offers(self):
        release = load_reviewed_release()
        built = release.for_planner(site_id="sakha", season_labels=LABELS)
        self.assertEqual(len(crop_ids(release.catalogue)), 12)
        self.assertEqual(len(built.kb.profiles), 9)
        self.assertEqual(crop_ids(release.catalogue, minimum_level="feasibility_eligible"), ())
        self.assertEqual(exploration_crop_ids(release.catalogue, "forage"), ("berseem",))
        self.assertEqual(exploration_crop_ids(release.catalogue, "seed"), ())
        fruits = {"watermelon","strawberry","cantaloupe","harankash"}
        self.assertTrue(fruits.isdisjoint(p.crop_id for p in built.kb.profiles))

    def test_scientific_history_and_claim_crosswalk(self):
        dossier = json.loads((RELEASE_DIR / "review.json").read_bytes())
        reviews = dossier["original_rule_reviews"] + dossier["expansion_records"]
        source_ids = {s["source_id"] for s in dossier["source_register"]}
        for row in reviews:
            self.assertTrue(row["source_ids"])
            self.assertTrue(set(row["source_ids"]) <= source_ids)
            self.assertFalse(row["runtime_enforceable"])
            self.assertIsNone(row["signoff_ref"])
        self.assertEqual(len(reviews), len({r["record_id"] for r in reviews}))
        ids = {r["record_id"] for r in dossier["expansion_records"]}
        self.assertTrue(all(set(x) <= ids for x in dossier["team_assertion_crosswalk"].values()))
        original = load_kb()
        current = load_reviewed_release().agricultural
        self.assertEqual(original.get_evidence(), current.get_evidence())
        self.assertEqual(original.get_sources(), current.get_sources())
        for before, after in zip(original.get_rules(), current.get_rules(), strict=True):
            for key in before.keys() - {"unresolved_requirements"}:
                self.assertEqual(before[key], after[key])
            self.assertEqual(after["unresolved_requirements"][:len(before["unresolved_requirements"])],
                             before["unresolved_requirements"])

    def test_altered_or_missing_packaged_bytes_refused(self):
        for name in ("manifest.json","review.json","catalogue.json","agricultural_kb.json"):
            with self.subTest(name=name), tempfile.TemporaryDirectory(dir=CORE) as temp:
                root=Path(temp)
                for f in RELEASE_DIR.iterdir():
                    shutil.copyfile(f,root/f.name)
                p=root/name
                p.write_bytes(p.read_bytes()+b" ")
                with self.assertRaises(KBError) as err:
                    load_reviewed_release(root)
                self.assertEqual(err.exception.code,"SOURCE_INTEGRITY")
                p.unlink()
                with self.assertRaises(KBError) as err:
                    load_reviewed_release(root)
                self.assertEqual(err.exception.code,"KB_UNAVAILABLE")

    def test_uh001_through_loader_promise_generator_and_service(self):
        result = run()
        self.assertEqual(result["current"], "rejected")
        self.assertEqual(result["service_current"], result["current"])
        self.assertEqual(result["first_reason"], "sowing_before_protected_cut")
        self.assertEqual(result["service_feasible"], 0)
        self.assertEqual(result["generator_status_counts"], {"needs_review":2})
        self.assertEqual(result["generator_search"], result["service_search"])
        reviews=result["review_investigations"]
        self.assertEqual({i["s2_sowing"] for i in reviews},{"2027-05-28","2027-06-01"})
        for i in reviews:
            self.assertEqual((i["s1_cut"],i["status"]), ("2027-05-20","needs_review"))
            for key in ("s2_harvest","s2_end_exclusive","s2_release"):
                self.assertIsNone(i[key])
            # UH-001 explicitly makes the seven-day preparation independent of sowing date.
            self.assertEqual(i["s2_preparation_days"], 7)


if __name__ == "__main__":
    unittest.main()
