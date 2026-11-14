"""Export the fixed KB v1 contract. Run from root: python -m scripts.export_kb_schema."""
import json
from pathlib import Path


def object_schema(**properties):
    return {"type": "object", "additionalProperties": False,
            "required": list(properties), "properties": properties}


def array(items, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum, "uniqueItems": True}


def enum(*values):
    return {"type": "string", "enum": list(values)}


def schema():
    text = {"type": "string", "minLength": 1}
    nullable = {"type": ["string", "null"], "minLength": 1}
    identifier = {"type": "string", "pattern": "^[a-zA-Z0-9_][a-zA-Z0-9_.-]*$"}
    status = enum("VERIFIED", "CONDITIONAL", "DERIVED", "NOT APPLICABLE", "UNVERIFIED", "BLOCKED")
    constraint = {"oneOf": [
        {"type": "null"},
        object_schema(kind=enum("numeric_range"), field=identifier,
                      lower={"type": "number"}, upper={"type": "number"}, units=text),
        object_schema(kind=enum("calendar_window"), field=identifier,
                      start_month_day={"type": "string", "pattern": "^[0-9]{2}-[0-9]{2}$"},
                      end_month_day={"type": "string", "pattern": "^[0-9]{2}-[0-9]{2}$"}),
        object_schema(kind=enum("category_set"), field=identifier, allowed=array(text, 1)),
    ]}
    rule = object_schema(
        rule_id=identifier, crop_ids=array(identifier, 1), rule_type=identifier,
        rule_label=text, parameters=object_schema(source_text=text, units=text),
        research_context=object_schema(locality=text, cultivar=text, season=text),
        source_ids=array(identifier), evidence_ids=array(identifier), scientific_status=status,
        local_applicability=object_schema(status=enum("PENDING", "APPLICABLE", "NOT_APPLICABLE"),
                                         locality_ids=array(identifier, 1), reviewer=nullable, reference=nullable),
        approval=object_schema(status=enum("PENDING", "APPROVED", "REJECTED", "REVOKED"),
                               reviewer=nullable, approved_on=nullable, reference=nullable,
                               scope_sha256={"type": ["string", "null"], "pattern": "^[a-f0-9]{64}$"}),
        enforcement=object_schema(status=enum("DISABLED", "ENABLED"), constraint=constraint),
        conditions={"type": "object", "additionalProperties": array(text, 1)},
        unresolved_requirements=array(text), source_activation_note=text,
        source_review_requirement=text, source_sign_off=text)
    result = object_schema(
        schema_version=enum("agricultural-kb/1"), kb_version=text,
        provenance=object_schema(ledger=text, evidence_register=text, source_manifest=text),
        localities=array(object_schema(locality_id=identifier, name=text, climate_site_id=text), 1),
        crops=array(object_schema(crop_id=identifier, display_name=text, purpose=text, rule_ids=array(identifier)), 1),
        sources=array(object_schema(source_id=identifier, title=text,
                                    url={"type": "string", "pattern": "^https?://"}, version=text)),
        evidence=array(object_schema(evidence_id=identifier, source_ids=array(identifier, 1),
                                     scientific_status=status, claim=text, locality=text, crop_context=text,
                                     units=text, locator=text, limitations=text, review_required=text,
                                     notes=text, source_opened=text, review_date=text)),
        rules=array(rule))
    return {"$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "MISSION EL GHEET agricultural KB v1", **result}


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "agricultural_kb/schema.json"
    target.write_text(json.dumps(schema(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
