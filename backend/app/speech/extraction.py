"""Gemini strict extraction (backend design §8.3, decided 14 Nov 2026).

Gemini only EXTRACTS what the farmer said into a fixed JSON shape; every field is null unless said.
`validate()` runs on every reply, whatever produced it: wrong shape → None (no_match); values outside the
catalogue or impossible dates are dropped to null. Nothing here confirms; the app reads back and the farmer
confirms separately.
"""
from __future__ import annotations

import json
from datetime import date

PURPOSES = ("forage", "grain")
UNITS = ("feddan", "qirat", "hectare")

SYSTEM_INSTRUCTION = (
    "You extract facts from a farmer's spoken answer for a crop-rotation app in Egypt. "
    "Return ONLY JSON matching the schema. Extract only what the speaker actually said. "
    "Use null for every field that was not said. Never guess a year, unit, crop, purpose or date. "
    "If the speaker says the bare word ذرة (or درة, or 'corn') without saying which, put it in `ambiguous` "
    "with options grain_maize and grain_sorghum and leave crop null. "
    "If the speaker says they don't know or don't remember, set answer.dont_know true. "
    "If the speaker asks for advice or a recommendation, set off_topic true. Never add advice or any other text."
)


def response_schema(crop_ids: list[str]) -> dict:
    """OpenAPI-style schema for Gemini structured output. All fields nullable."""
    date_parts = {"type": "object", "nullable": True, "properties": {
        "day": {"type": "integer", "nullable": True}, "month": {"type": "integer", "nullable": True},
        "year": {"type": "integer", "nullable": True}}, "required": ["day", "month", "year"]}
    season = {"type": "object", "properties": {
        "order": {"type": "integer"},
        "crop": {"type": "string", "nullable": True, "enum": [*crop_ids, "unknown"]},
        "crop_said": {"type": "string", "nullable": True},
        "purpose": {"type": "string", "nullable": True, "enum": list(PURPOSES)},
        "sowing_date": date_parts, "last_cut_date": date_parts,
        "must_stay": {"type": "boolean", "nullable": True}},
        "required": ["order", "crop", "crop_said", "purpose", "sowing_date", "last_cut_date", "must_stay"]}
    return {"type": "object", "properties": {
        "seasons": {"type": "array", "items": season},
        "area": {"type": "object", "nullable": True, "properties": {
            "value": {"type": "number", "nullable": True}, "unit": {"type": "string", "nullable": True, "enum": list(UNITS)}},
            "required": ["value", "unit"]},
        "answer": {"type": "object", "properties": {
            "yes_no": {"type": "string", "nullable": True, "enum": ["yes", "no"]},
            "confirm": {"type": "boolean", "nullable": True}, "dont_know": {"type": "boolean", "nullable": True}},
            "required": ["yes_no", "confirm", "dont_know"]},
        "ambiguous": {"type": "array", "items": {"type": "object", "properties": {
            "path": {"type": "string"}, "said": {"type": "string"}, "options": {"type": "array", "items": {"type": "string"}}},
            "required": ["path", "said", "options"]}},
        "off_topic": {"type": "boolean"}},
        "required": ["seasons", "area", "answer", "ambiguous", "off_topic"]}


TOP = {"seasons", "area", "answer", "ambiguous", "off_topic"}
SEASON_KEYS = {"order", "crop", "crop_said", "purpose", "sowing_date", "last_cut_date", "must_stay"}


def _date(v) -> dict | None:
    if v is None:
        return None
    if not isinstance(v, dict) or set(v) != {"day", "month", "year"}:
        raise ValueError("date shape")
    d, m, y = v["day"], v["month"], v["year"]
    for x in (d, m, y):
        if x is not None and (not isinstance(x, int) or isinstance(x, bool)):
            raise ValueError("date type")
    if m is not None and not 1 <= m <= 12:
        return None
    if d is not None and not 1 <= d <= 31:
        return None
    if y is not None and not 2000 <= y <= 2100:
        y = None
    if d and m and y:
        try:
            date(y, m, d)
        except ValueError:
            return None
    return {"day": d, "month": m, "year": y}


def _bool(v):
    if v is not None and not isinstance(v, bool):
        raise ValueError("bool")
    return v


def validate(raw: object, crop_ids: list[str]) -> dict | None:
    """Strict check of an extraction. Returns a cleaned copy or None if the shape is wrong."""
    try:
        if isinstance(raw, str):
            raw = json.loads(raw)
        if not isinstance(raw, dict) or set(raw) != TOP:
            return None
        seasons = []
        for s in raw["seasons"]:
            if not isinstance(s, dict) or set(s) != SEASON_KEYS or not isinstance(s["order"], int) or not 1 <= s["order"] <= 4:
                return None
            crop = s["crop"] if s["crop"] in (*crop_ids, "unknown") else None
            purpose = s["purpose"] if s["purpose"] in PURPOSES else None
            said = s["crop_said"] if isinstance(s["crop_said"], str) and len(s["crop_said"]) <= 40 else None
            seasons.append({"order": s["order"], "crop": crop, "crop_said": said, "purpose": purpose,
                            "sowing_date": _date(s["sowing_date"]), "last_cut_date": _date(s["last_cut_date"]),
                            "must_stay": _bool(s["must_stay"])})
        area = raw["area"]
        if area is not None:
            if not isinstance(area, dict) or set(area) != {"value", "unit"}:
                return None
            val = area["value"] if isinstance(area["value"], (int, float)) and not isinstance(area["value"], bool) and 0 < area["value"] < 100000 else None
            area = {"value": val, "unit": area["unit"] if area["unit"] in UNITS else None}
        ans = raw["answer"]
        if not isinstance(ans, dict) or set(ans) != {"yes_no", "confirm", "dont_know"}:
            return None
        answer = {"yes_no": ans["yes_no"] if ans["yes_no"] in ("yes", "no") else None, "confirm": _bool(ans["confirm"]), "dont_know": _bool(ans["dont_know"])}
        ambiguous = []
        for a in raw["ambiguous"]:
            if not isinstance(a, dict) or set(a) != {"path", "said", "options"}:
                return None
            opts = [o for o in a["options"] if o in crop_ids] if isinstance(a["options"], list) else []
            if opts and isinstance(a["path"], str) and isinstance(a["said"], str) and len(a["said"]) <= 40:
                ambiguous.append({"path": a["path"][:40], "said": a["said"], "options": opts})
        if not isinstance(raw["off_topic"], bool):
            return None
        return {"seasons": seasons, "area": area, "answer": answer, "ambiguous": ambiguous, "off_topic": raw["off_topic"]}
    except (ValueError, TypeError, KeyError):
        return None


def is_empty(x: dict) -> bool:
    return not (x["seasons"] or x["ambiguous"] or x["off_topic"] or x["area"] or any(v is not None for v in x["answer"].values()))
