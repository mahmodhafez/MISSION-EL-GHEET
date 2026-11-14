"""Dependency-free validator for the explicit JSON Schema subset used by this KB.

This is not a general JSON Schema implementation. Unsupported schema keywords fail
closed. The shipped schema can also be consumed by Draft 2020-12 validators.
"""
import json
import math
import re


class KBError(ValueError):
    """Stable, JSON-serializable data/input error, with a machine-readable code."""

    def __init__(self, code, path, message):
        super().__init__(message)
        self.code, self.path, self.message = code, path, message

    def to_dict(self):
        return {"error": {"code": self.code, "path": self.path, "message": self.message}}


def strict_json(payload):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise KBError("INVALID_JSON", "$", "Duplicate JSON key: " + key)
            result[key] = value
        return result

    def constant(value):
        raise KBError("INVALID_JSON", "$", "Nonfinite JSON number: " + value)

    try:
        return json.loads(payload, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, KBError):
            raise
        raise KBError("INVALID_JSON", "$", str(exc)) from exc


def validate(value, schema, path="$"):
    allowed = {"$schema", "title", "description", "type", "enum", "properties",
               "required", "additionalProperties", "items", "minItems", "uniqueItems",
               "minLength", "pattern", "oneOf"}
    if set(schema) - allowed:
        raise KBError("INVALID_SCHEMA", path, "Unsupported schema keyword")
    if "oneOf" in schema:
        matched = 0
        for alternative in schema["oneOf"]:
            try:
                validate(value, alternative, path)
                matched += 1
            except KBError as exc:
                if exc.code == "INVALID_SCHEMA":
                    raise
        if matched != 1:
            raise KBError("INVALID_KB", path, "Expected exactly one allowed schema")
        return
    kinds = {"object": type(value) is dict, "array": type(value) is list,
             "string": type(value) is str, "null": value is None,
             "boolean": type(value) is bool, "integer": type(value) is int,
             "number": type(value) in (int, float) and math.isfinite(value)}
    types = schema.get("type", list(kinds))
    if isinstance(types, str):
        types = [types]
    if not any(kinds.get(kind, False) for kind in types):
        raise KBError("INVALID_KB", path, "Wrong value type or nonfinite number")
    if "enum" in schema and value not in schema["enum"]:
        raise KBError("INVALID_KB", path, "Unknown enum value")
    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            raise KBError("INVALID_KB", path, "Empty text")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            raise KBError("INVALID_KB", path, "Invalid text format")
    if type(value) is list:
        if len(value) < schema.get("minItems", 0):
            raise KBError("INVALID_KB", path, "Too few entries")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            raise KBError("INVALID_KB", path, "Duplicate entries")
        for index, item in enumerate(value):
            validate(item, schema.get("items", {}), f"{path}[{index}]")
    if type(value) is dict:
        missing = set(schema.get("required", [])) - value.keys()
        if missing:
            raise KBError("INVALID_KB", path, "Missing fields: " + ", ".join(sorted(missing)))
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in properties:
                validate(item, properties[key], path + "." + key)
            elif additional is False:
                raise KBError("INVALID_KB", path + "." + key, "Unknown field")
            elif isinstance(additional, dict):
                validate(item, additional, path + "." + key)
