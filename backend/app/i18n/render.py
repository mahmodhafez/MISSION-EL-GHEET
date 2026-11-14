"""Render planner codes + params into bilingual text and speech (design D4). Stored results keep codes only;
wording is produced per request, so a language switch never re-runs the planner."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .formatting import date_speech, date_text, days, digits, words

CATALOGUE = json.loads((Path(__file__).parent / "messages.json").read_text(encoding="utf-8"))
MESSAGES, CROPS = CATALOGUE["messages"], CATALOGUE["crop"]
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
REASON_ORDER = ["endpoint_mapping_missing", "irrigation_availability_unknown", "soil_suitability_unknown",
                "cultivar_availability_unknown", "forage_quantity_unknown", "sowing_support_unverified", "preparation_requirement_unverified"]


def crop_name(crop_id: str | None, locale: str) -> str:
    return CROPS.get(crop_id or "_unknown", CROPS["_unknown"])[locale]


def bare(name: str, locale: str) -> str:
    return name.removeprefix("the ") if locale == "en" else name


def render(code: str, params: dict, locale: str) -> dict | None:
    """{code, version, text, speech}, or None when no template exists (the screen falls back to the code)."""
    m = MESSAGES.get(code)
    if m is None:
        return None
    text, speech = {}, {}
    for k, v in params.items():
        if isinstance(v, str) and DATE.fullmatch(v):
            text[k], speech[k] = date_text(v, locale, year=False), date_speech(v, locale, year=False)
        elif k == "preparation_days" and isinstance(v, int):
            text[k], speech[k] = days(v, locale, False), days(v, locale, True)
        elif isinstance(v, int) and not isinstance(v, bool):
            text[k], speech[k] = digits(v, locale), words(v, locale)
        else:
            text[k] = speech[k] = "" if v is None else str(v)
    try:
        return {"code": code, "version": m["version"], "text": m[locale].format(**text), "speech": m[locale].format(**speech)}
    except KeyError:
        return None


def _crops_by_season(plan_input: dict) -> dict[str, str | None]:
    return {s["season_id"]: s["crop_id"]["value"] for s in plan_input["seasons"]}


def render_result(result: dict, plan_input: dict, locale: str) -> dict:
    """Everything a result screen says, in one locale: headline, conflict, why, options, coverage, takeaway."""
    crops = _crops_by_season(plan_input)
    order = {s["season_id"]: s["order"] for s in plan_input["seasons"]}
    cur = result["current"]

    def names(cid: str | None, prefix: str = "") -> dict:
        n = crop_name(cid, locale)
        return {f"{prefix}crop": n, f"{prefix}crop_bare": bare(n, locale), f"{prefix}crop_cap": bare(n, locale).capitalize()}

    out: dict = {"locale": locale, "headline": render(f"status.{cur['status']}", {}, locale), "conflicts": [], "why": None,
                 "options": [], "coverage": [], "review_reasons": [], "takeaway": None}
    pair = None
    for c in cur["checks"]:
        if c["outcome"] != "fail":
            continue
        p = dict(c["explanation"]["params"])
        code = c["explanation"]["code"]
        sid = p.get("season_id") or p.get("next_season_id")
        cut_sid = next((s for s in c["season_ids"] if s != sid), None)
        extra = {**names(crops.get(sid)), **names(crops.get(cut_sid), "cut_")}
        r = render(code, {**p, **extra}, locale)
        if code == "preparation_shortfall":
            out["why"] = r
        elif r:
            out["conflicts"].append(r)
        if code == "sowing_before_protected_cut":
            pair = {**p, **extra}
    for c in result["review_investigations"] + result["feasible_alternatives"]:
        ch = next((x for x in c["changes"] if x["direct"]), None)
        if ch and ch["field"] == "sowing_date" and ch["after"]["value"]:
            r = render("investigation", {"new_date": ch["after"]["value"], **names(crops.get(ch["season_id"]))}, locale)
            out["options"].append({"candidate_id": c["candidate_id"], **(r or {})})
    seen = set()
    for x in result["exclusions"]:
        key = (x["code"], tuple(x["season_ids"]))
        if x["kind"] != "blocked" or key in seen:
            continue
        seen.add(key)
        sid = x["season_ids"][0] if x["season_ids"] else None
        cid = next((p.split(".")[-1] for p in x["missing_input_paths"] if p.startswith("kb.profiles.")), None)
        r = render(x["code"], {"season_number": order.get(sid, 0), **names(cid)}, locale)
        if r:
            out["coverage"].append(r)
    if result["search"]["status"] == "incomplete" and result["review_investigations"] + result["feasible_alternatives"]:
        out["coverage"].append(render("search_incomplete", {}, locale))
    codes = {c["explanation"]["code"] for cand in result["review_investigations"] for c in cand["evaluation"]["checks"] if c["outcome"] == "unknown"}
    out["review_reasons"] = [r for r in (render(f"reason.{k}", {}, locale) for k in REASON_ORDER if k in codes) if r][:4]
    if pair:
        alts = render("no_feasible_alternative", {}, locale) if not result["feasible_alternatives"] else None
        out["takeaway"] = render("takeaway.conflict", {**pair, "alternatives": alts["text"] if alts else ""}, locale)
        if out["takeaway"] and alts:  # speech variant needs the spoken sub-sentence too
            out["takeaway"]["speech"] = render("takeaway.conflict", {**pair, "alternatives": alts["speech"]}, locale)["speech"]
    return out
