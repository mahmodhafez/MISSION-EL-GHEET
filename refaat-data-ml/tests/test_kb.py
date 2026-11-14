"""Approval safety and source fidelity; synthetic approvals are test fixtures only."""
import copy
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from agricultural_kb import AgriculturalKB, KBError, approval_scope_sha256, load_kb
from agricultural_kb.build import build_document, serialize, verify_sources

ROOT = Path(__file__).resolve().parents[1]
KB_FILE = ROOT / "knowledge_base/agricultural_kb.json"


def synthetic_document():
    """No agricultural assertion: a synthetic scalar tests only approval plumbing."""
    doc = json.loads(KB_FILE.read_bytes())
    rule = doc["rules"][0]
    rule["local_applicability"].update(status="APPLICABLE", reviewer="TEST reviewer",
                                       reference="TEST applicability record")
    rule["enforcement"] = {"status": "ENABLED", "constraint": {
        "kind": "numeric_range", "field": "synthetic_test_value", "lower": 1, "upper": 2, "units": "test_only"}}
    rule["conditions"] = {"cultivar": ["TEST cultivar"], "purpose": ["TEST purpose"]}
    rule["unresolved_requirements"] = []
    rule["approval"].update(status="APPROVED", reviewer="TEST approver", approved_on="2026-11-13",
                             reference="TEST sign-off; not a real agronomic approval")
    resign(doc)
    return doc


def resign(doc):
    doc["rules"][0]["approval"]["scope_sha256"] = approval_scope_sha256(
        doc["rules"][0], doc["evidence"], doc["sources"])


CONTEXT = {"locality": "sakha", "conditions": {"cultivar": "TEST cultivar", "purpose": "TEST purpose"}}


class AgriculturalKBTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(KB_FILE.read_bytes())
        self.kb = load_kb(KB_FILE)

    def test_original_27_rules_18_verified_four_crops_no_approval(self):
        self.assertEqual([c["crop_id"] for c in self.kb.get_crops()],
                         ["wheat", "berseem", "grain_maize", "grain_sorghum"])
        status = self.kb.get_status(locality="sakha")
        self.assertEqual(status["rules"], 27)
        self.assertEqual(status["scientific_status_counts"],
                         {"VERIFIED": 18, "CONDITIONAL": 4, "DERIVED": 1, "NOT APPLICABLE": 1, "UNVERIFIED": 3})
        self.assertEqual(status["status"], "NO_LOCAL_SIGN_OFF")
        self.assertEqual(self.kb.get_approved_rules(), [])
        self.assertEqual(self.kb.get_enforceable_rules(locality="sakha"), [])
        self.assertEqual(len(self.kb.get_pending_rules(locality="sakha")), 27)
        self.assertEqual(len(self.kb.get_rules(view="supported")), 18)
        self.assertEqual(len(self.kb.get_rules(view="unverified")), 9)

    def test_import_is_byte_reproducible_and_preserves_research(self):
        verify_sources(ROOT / "sources/agriculture")
        self.assertEqual(serialize(build_document(ROOT / "sources/agriculture")), KB_FILE.read_bytes())
        with (ROOT / "sources/agriculture/MISSION_EL_GHEET_Crop_Rule_Ledger.csv").open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        for raw, rule in zip(rows, self.kb.get_rules(), strict=True):
            self.assertEqual(rule["rule_id"], raw["Rule ID"])
            self.assertEqual(rule["parameters"], {"source_text": raw["Proposed value or range"], "units": raw["Units"]})
            evidence = self.kb.get_evidence(rule["evidence_ids"][0])
            source = self.kb.get_sources(rule["source_ids"][0])
            self.assertEqual(evidence["scientific_status"], raw["Current verification status"])
            self.assertEqual(source["url"], raw["Source URL"])
            self.assertEqual(source["title"], raw["Scientific source title"])
            self.assertIn(raw["Assumptions and limitations"], rule["unresolved_requirements"])

    def test_source_byte_tampering_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            target = Path(tmp) / "research"
            shutil.copytree(ROOT / "sources/agriculture", target)
            with (target / "MISSION_EL_GHEET_Crop_Rule_Ledger.csv").open("ab") as file:
                file.write(b"\n")
            with self.assertRaises(KBError) as caught:
                build_document(target)
            self.assertEqual(caught.exception.code, "SOURCE_INTEGRITY")

    def test_all_approval_scientific_and_applicability_states(self):
        for approval in ("PENDING", "APPROVED", "REJECTED", "REVOKED"):
            for science in ("VERIFIED", "CONDITIONAL", "DERIVED", "NOT APPLICABLE", "UNVERIFIED", "BLOCKED"):
                for applicable in ("PENDING", "APPLICABLE", "NOT_APPLICABLE"):
                    doc = synthetic_document()
                    rule = doc["rules"][0]
                    rule["approval"]["status"] = approval
                    rule["scientific_status"] = science
                    rule["local_applicability"]["status"] = applicable
                    resign(doc)
                    with self.subTest(approval=approval, science=science, applicable=applicable):
                        result = AgriculturalKB(doc).get_enforceable_rules(**CONTEXT)
                        self.assertEqual(bool(result), (approval, science, applicable) == ("APPROVED", "VERIFIED", "APPLICABLE"))

    def test_linked_evidence_status_is_an_independent_gate(self):
        for status in ("CONDITIONAL", "DERIVED", "NOT APPLICABLE", "UNVERIFIED", "BLOCKED"):
            doc = synthetic_document()
            doc["evidence"][0]["scientific_status"] = status
            resign(doc)
            kb = AgriculturalKB(doc)
            self.assertEqual(kb.get_enforceable_rules(**CONTEXT), [])
            self.assertNotIn("C01", [r["rule_id"] for r in kb.get_rules(view="supported")])

    def test_scientific_verified_alone_and_approved_alone_cannot_activate(self):
        doc = synthetic_document()
        doc["rules"][0]["enforcement"]["status"] = "DISABLED"
        resign(doc)
        kb = AgriculturalKB(doc)
        self.assertEqual(len(kb.get_approved_rules(**CONTEXT)), 1)
        self.assertEqual(kb.get_enforceable_rules(**CONTEXT), [])
        doc["rules"][0]["enforcement"]["status"] = "ENABLED"
        doc["rules"][0]["approval"]["status"] = "PENDING"
        self.assertEqual(AgriculturalKB(doc).get_enforceable_rules(**CONTEXT), [])

    def test_explicit_locality_and_all_conditions_required(self):
        kb = AgriculturalKB(synthetic_document())
        self.assertEqual([r["rule_id"] for r in kb.get_enforceable_rules(**CONTEXT)], ["C01"])
        for query in ({}, {"locality": "sakha"}, {"locality": "sakha", "conditions": {"cultivar": "TEST cultivar"}},
                      {"locality": "sakha", "conditions": {"cultivar": "different", "purpose": "TEST purpose"}}):
            self.assertEqual(kb.get_rules(view="enforceable", **query), [])
        self.assertFalse(kb.get_rules(conditions=CONTEXT["conditions"])[0]["enforceability"]["enforceable"])
        doc = synthetic_document()
        doc["localities"].append({"locality_id": "elsewhere", "name": "TEST", "climate_site_id": "TEST"})
        self.assertEqual(AgriculturalKB(doc).get_enforceable_rules(locality="elsewhere", conditions=CONTEXT["conditions"]), [])

    def test_pending_review_missing_evidence_and_constraint_block(self):
        for key, value in (("evidence_ids", []), ("source_ids", []), ("unresolved_requirements", ["Still unresolved"])):
            doc = synthetic_document()
            doc["rules"][0][key] = value
            if key == "source_ids":
                doc["rules"][0]["evidence_ids"] = []
            resign(doc)
            self.assertEqual(AgriculturalKB(doc).get_enforceable_rules(**CONTEXT), [])
        doc = synthetic_document()
        doc["rules"][0]["enforcement"]["constraint"] = None
        resign(doc)
        self.assertEqual(AgriculturalKB(doc).get_enforceable_rules(**CONTEXT), [])

    def test_dated_named_and_scope_bound_approval_required(self):
        for key in ("reviewer", "approved_on", "reference", "scope_sha256"):
            doc = synthetic_document()
            doc["rules"][0]["approval"][key] = None
            with self.subTest(key=key), self.assertRaises(KBError) as caught:
                AgriculturalKB(doc)
            self.assertEqual(caught.exception.code, "INCOMPLETE_APPROVAL")
        for value in ("2026-02-30", "20261113", "2026-11-13T00:00:00"):
            doc = synthetic_document()
            doc["rules"][0]["approval"]["approved_on"] = value
            with self.assertRaises(KBError):
                AgriculturalKB(doc)

    def test_stale_approval_after_rule_evidence_or_source_change(self):
        for name in ("rules", "evidence", "sources"):
            doc = synthetic_document()
            if name == "rules":
                doc[name][0]["conditions"] = {}
            elif name == "evidence":
                doc[name][0]["claim"] = "Changed claim"
            else:
                sid = doc["rules"][0]["source_ids"][0]
                next(s for s in doc[name] if s["source_id"] == sid)["url"] = "https://example.invalid/changed"
            with self.subTest(name=name), self.assertRaises(KBError) as caught:
                AgriculturalKB(doc)
            self.assertEqual(caught.exception.code, "STALE_APPROVAL")

    def test_missing_local_applicability_review_is_invalid(self):
        for key in ("reviewer", "reference"):
            doc = synthetic_document()
            doc["rules"][0]["local_applicability"][key] = None
            with self.assertRaises(KBError) as caught:
                AgriculturalKB(doc)
            self.assertEqual(caught.exception.code, "INCOMPLETE_APPLICABILITY")

    def test_dangling_duplicate_and_nonreciprocal_links_are_invalid(self):
        for category, key in (("rules", "rule_id"), ("crops", "crop_id"), ("evidence", "evidence_id"), ("sources", "source_id")):
            doc = copy.deepcopy(self.doc)
            doc[category][1][key] = doc[category][0][key]
            with self.assertRaises(KBError):
                AgriculturalKB(doc)
        for key in ("crop_ids", "evidence_ids", "source_ids"):
            doc = copy.deepcopy(self.doc)
            doc["rules"][0][key] = ["UNKNOWN"]
            with self.assertRaises(KBError) as caught:
                AgriculturalKB(doc)
            self.assertEqual(caught.exception.code, "BROKEN_REFERENCE")
        doc = copy.deepcopy(self.doc)
        doc["crops"][0]["rule_ids"] = []
        with self.assertRaises(KBError):
            AgriculturalKB(doc)

    def test_unknown_missing_wrong_types_and_forged_enforceability_rejected(self):
        for mutation in (lambda d: d.update(schema_version="future"),
                         lambda d: d["rules"][0].update(enforceable=True),
                         lambda d: d["rules"][0]["approval"].update(status=True),
                         lambda d: d["rules"][0].pop("approval"),
                         lambda d: d["rules"][0].update(conditions={"cultivar": []}),
                         lambda d: d["rules"][0].update(scientific_status="verified")):
            doc = copy.deepcopy(self.doc)
            mutation(doc)
            with self.assertRaises(KBError):
                AgriculturalKB(doc)

    def test_supported_constraint_shapes_and_invalid_boundaries(self):
        valid = [{"kind": "calendar_window", "field": "synthetic_date", "start_month_day": "11-30", "end_month_day": "02-29"},
                 {"kind": "category_set", "field": "synthetic_category", "allowed": ["TEST"]}]
        for constraint in valid:
            doc = synthetic_document()
            doc["rules"][0]["enforcement"]["constraint"] = constraint
            resign(doc)
            self.assertEqual(len(AgriculturalKB(doc).get_enforceable_rules(**CONTEXT)), 1)
        invalid = [{"kind": "numeric_range", "field": "x", "lower": 3, "upper": 2, "units": "TEST"},
                   {"kind": "numeric_range", "field": "x", "lower": True, "upper": 2, "units": "TEST"},
                   {"kind": "calendar_window", "field": "x", "start_month_day": "02-30", "end_month_day": "03-01"},
                   {"kind": "category_set", "field": "x", "allowed": []},
                   {"kind": "custom_code", "expression": "anything"}]
        for constraint in invalid:
            doc = synthetic_document()
            doc["rules"][0]["enforcement"]["constraint"] = constraint
            resign(doc)
            with self.assertRaises(KBError):
                AgriculturalKB(doc)

    def test_missing_invalid_json_and_structured_errors(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            path = Path(tmp) / "kb.json"
            with self.assertRaises(KBError) as caught:
                load_kb(path)
            self.assertEqual(caught.exception.code, "KB_UNAVAILABLE")
            self.assertIn("error", json.loads(json.dumps(caught.exception.to_dict())))
            for payload in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e999}', b'{', b'\xff', b'[]'):
                path.write_bytes(payload)
                with self.subTest(payload=payload), self.assertRaises(KBError):
                    load_kb(path)

    def test_queries_return_json_copies_and_include_shared_rules(self):
        rules = self.kb.get_rules(crop_id="grain_maize", locality="sakha")
        self.assertEqual([r["rule_id"] for r in rules], [f"C{i:02d}" for i in (*range(14, 19), 25, 26, 27)])
        for value in (rules, self.kb.get_crops(), self.kb.get_evidence(), self.kb.get_sources(), self.kb.get_status(locality="sakha")):
            json.dumps(value, allow_nan=False)
        rules[0]["approval"]["status"] = "APPROVED"
        crop = self.kb.get_crop("wheat")
        crop["rule_ids"].clear()
        self.assertEqual(self.kb.get_approved_rules(), [])
        self.assertTrue(self.kb.get_crop("wheat")["rule_ids"])
        for query in ({"crop_id": "unknown"}, {"locality": "Sakha"}, {"view": "random"}, {"conditions": []}, {"conditions": {"cultivar": None}}):
            with self.assertRaises(KBError):
                self.kb.get_rules(**query)

    def test_nonlocal_and_forage_sources_do_not_gain_sakha_applicability(self):
        rules = {r["rule_id"]: r for r in self.kb.get_rules(crop_id="grain_sorghum", locality="sakha")}
        self.assertEqual(rules["C19"]["research_context"]["locality"], "Upper Egypt")
        self.assertEqual(rules["C22"]["local_applicability"]["status"], "NOT_APPLICABLE")
        self.assertTrue(all(not r["enforceability"]["enforceable"] for r in rules.values()))

    def test_portable_default_load_without_site_packages_or_models(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            base = Path(tmp)
            shutil.copytree(ROOT / "agricultural_kb", base / "agricultural_kb", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(ROOT / "knowledge_base", base / "knowledge_base")
            code = "import json,sys; from agricultural_kb import load_kb; k=load_kb(); print(json.dumps(k.get_status(locality='sakha'))); assert not {'torch','chronos','sklearn','ortools','climate_data'}.intersection(sys.modules)"
            result = subprocess.run([sys.executable, "-B", "-S", "-c", code], cwd=base, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["enforceable_rules"], 0)


if __name__ == "__main__":
    unittest.main()
