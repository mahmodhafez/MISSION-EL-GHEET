"""Sourced research notes for the crops a farmer entered (rendered.research, 14 Nov 2026).

Reads the reviewed Sakha agricultural KB. These rules have no local sign-off, so the planner cannot enforce them. They
can still be shown, labelled, next to the farmer's dates. Nothing here changes a plan's status, and nothing is invented:
* only rules whose `source_text` matches an exact date/day pattern become structured notes (fail closed);
* everything else goes to `other` with its English source text;
* the only arithmetic is placing calendar dates in the farmer's season year, counting days between the farmer's date
  and a sourced window, and adding the source's own day counts to the farmer's sowing date (first berseem cut).
"""
from __future__ import annotations

import re
from datetime import date, timedelta

from ..i18n.formatting import date_speech, date_text, days, digits, words
from ..i18n.render import MESSAGES, bare, crop_name

MON = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}
DM = r"(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
WINDOW = re.compile(rf"^{DM} to {DM}$")
SOW_AND_HARVEST = re.compile(rf"^{DM} to {DM} sowing and (\d{{1,2}})–(\d{{1,2}}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) harvest$")
DATE_LIST = re.compile(rf"^({DM}(?:(?:, | and ){DM})*)(.*)$")
MATURITY_PAIR = re.compile(rf"{DM} sowing yielded ([\d.]+) and ([\d.]+) days")
FIRST_CUT = re.compile(r"^First (\d+)–(\d+) days after sowing, then (\d+)–(\d+) between cuts$")

# Exact source remainders after a trial-date list, translated (not paraphrased into new claims). Unknown → dropped.
TRIAL_EXTRA = {
    ". Highest-yield treatments differed by genotype.": {"en": " The best date differed by variety.", "ar-EG": " وأحسن ميعاد اختلف حسب الصنف."},
    " tested during 2023–24. SC168 performed best at 15 May within trial.": {
        "en": " Hybrid SC168 did best on 15 May in that trial.", "ar-EG": " والهجين SC168 كان أحسن في ١٥ مايو في التجربة دي."},
    "": {"en": "", "ar-EG": ""},
}
# Research localities (place names; Arabic is a DRAFT for native review). Unknown → the English name.
WHERE_AR = {
    "Nile Delta": "الدلتا", "Sakha": "سخا", "Sakha, Kafr El-Sheikh": "سخا، كفر الشيخ",
    "Tag Al-Ezz, Dakahlia, Nile Delta": "تاج العز، الدقهلية", "Upper Egypt": "الصعيد",
    "Giza, Cairo University": "الجيزة (جامعة القاهرة)", "Egyptian guidance": "إرشادات مصرية", "Egypt": "مصر",
    "Sakha Research Station": "محطة بحوث سخا",
}
KIND_ORDER = ["sowing_window", "trial_dates", "first_cut", "maturity_window", "harvest_window", "maturity_days"]
TITLE = {"sowing_window": "sowing", "trial_dates": "trial", "first_cut": "first_cut", "maturity_window": "harvest",
         "harvest_window": "harvest", "maturity_days": "maturity_days"}
SEASON_START = {"winter": (10, 1), "summer": (4, 1)}


def _where(name: str, locale: str) -> str:
    return WHERE_AR.get(name, name) if locale == "ar-EG" else name


def _near(month: int, day: int, anchor: date) -> date:
    """The occurrence of day/month closest to the anchor (within half a year)."""
    best = None
    for y in (anchor.year - 1, anchor.year, anchor.year + 1):
        try:
            d = date(y, month, day)
        except ValueError:
            continue
        if best is None or abs((d - anchor).days) < abs((best - anchor).days):
            best = d
    return best


def _after(month: int, day: int, anchor: date) -> date:
    """The first occurrence of day/month on or after the anchor."""
    d = date(anchor.year, month, day)
    return d if d >= anchor else date(anchor.year + 1, month, day)


def _window(m1, d1, m2, d2, anchor, following=False):
    start = _after(m1, d1, anchor) if following else _near(m1, d1, anchor)
    end = date(start.year, m2, d2)
    return start, end if end >= start else date(start.year + 1, m2, d2)


def _range(a: float, b: float, locale: str) -> str:
    lo, hi = sorted((round(a), round(b)))
    return digits(lo, locale) if lo == hi else f"{digits(lo, locale)}–{digits(hi, locale)}"


def _dates_list(ds: list[date], locale: str, spoken: bool) -> str:
    f = date_speech if spoken else date_text
    parts = [f(d.isoformat(), locale, year=False) for d in ds]
    if len(parts) == 1:
        return parts[0]
    return (("، ".join(parts[:-1]) + " و" + parts[-1]) if locale == "ar-EG" else (", ".join(parts[:-1]) + " and " + parts[-1]))


def _say(code: str, params: dict, locale: str) -> dict | None:
    """Like i18n.render, plus *_days ints and prebuilt (text, speech) tuples."""
    m = MESSAGES.get(code)
    if m is None:
        return None
    text, speech = {}, {}
    for k, v in params.items():
        if isinstance(v, tuple):
            text[k], speech[k] = v
        elif isinstance(v, date):
            text[k], speech[k] = date_text(v.isoformat(), locale, year=False), date_speech(v.isoformat(), locale, year=False)
        elif k.endswith("_days") and isinstance(v, int):
            text[k], speech[k] = days(v, locale, False), days(v, locale, True)
        elif isinstance(v, int) and not isinstance(v, bool):
            text[k], speech[k] = digits(v, locale), words(v, locale)
        else:
            text[k] = speech[k] = "" if v is None else str(v)
    try:
        return {"code": code, "version": m["version"], "text": m[locale].format(**text), "speech": m[locale].format(**speech)}
    except KeyError:
        return None


def _source(kb, rule: dict) -> dict:
    sid = rule["source_ids"][0] if rule["source_ids"] else None
    src = kb.get_sources(sid) if sid else {}
    ev = kb.get_evidence(rule["evidence_ids"][0]) if rule["evidence_ids"] else {}
    return {"source_id": sid, "title": src.get("title"), "url": src.get("url"), "version": src.get("version"), "locator": ev.get("locator")}


def _notes_for_rule(rule: dict, sow: date | None, anchor: date, cn: dict, locale: str) -> list[dict] | None:
    """Structured notes for one rule, or None when its text is not an exact known pattern."""
    t, kind = rule["parameters"]["source_text"].strip(), rule["rule_type"]
    where_en = rule["research_context"]["locality"]
    where = _where(where_en, locale)
    base = {**cn, "where": where}
    out = []

    def note(k, code, params, window=None, farmer=None, ds=()):
        placement = gap = None
        if window and farmer:
            s, e = window
            placement = "before" if farmer < s else "after" if farmer > e else "inside"
            gap = (s - farmer).days if placement == "before" else (farmer - e).days if placement == "after" else None
            code = f"{code}.{placement}"
            params = {**params, "farmer_date": farmer, **({"gap_days": gap} if gap else {})}
        r = _say(code, {**base, **params}, locale)
        title = _say(f"research.title.{TITLE[k]}", {}, locale)
        if r is None or title is None:
            return
        out.append({"rule_id": rule["rule_id"], "kind": k, "title": title["text"], "text": r["text"], "speech": r["speech"],
                    "window": {"start": window[0].isoformat(), "end": window[1].isoformat()} if window else None,
                    "farmer_date": farmer.isoformat() if farmer else None, "placement": placement, "days_outside": gap,
                    "dates": [d.isoformat() for d in ds], "where": where})

    if kind in ("sowing_window", "physiological_maturity_window") and (m := WINDOW.match(t)):
        d1, m1, d2, m2 = int(m[1]), MON[m[2]], int(m[3]), MON[m[4]]
        if kind == "sowing_window":
            w = _window(m1, d1, m2, d2, sow or anchor)
            note("sowing_window", "research.sowing_window" if sow else "research.sowing_window.none", {"start": w[0], "end": w[1]}, w if sow else None, sow)
        else:
            w = _window(m1, d1, m2, d2, sow or anchor, following=True)
            note("maturity_window", "research.maturity_window", {"start": w[0], "end": w[1]}, w)
    elif kind == "nonlocal_sowing_harvest_evidence" and (m := SOW_AND_HARVEST.match(t)):
        w = _window(MON[m[2]], int(m[1]), MON[m[4]], int(m[3]), sow or anchor)
        note("sowing_window", "research.sowing_window" if sow else "research.sowing_window.none", {"start": w[0], "end": w[1]}, w if sow else None, sow)
        h = _window(MON[m[7]], int(m[5]), MON[m[7]], int(m[6]), w[0], following=True)
        note("harvest_window", "research.harvest_window", {"start": h[0], "end": h[1]}, h)
    elif kind in ("trial_sowing_dates", "sowing_date_comparison", "experimental_planting_dates") and (m := DATE_LIST.match(t)):
        # Unknown qualifier after the dates: drop it rather than guess a translation.
        extra = TRIAL_EXTRA.get(m.groups()[-1], {"en": "", "ar-EG": ""})
        ds = sorted(_near(MON[mo], int(d), sow or anchor) for d, mo in re.findall(DM, m[1]))
        note("trial_dates", "research.trial_dates", {"dates": (_dates_list(ds, locale, False), _dates_list(ds, locale, True)),
             "extra": extra[locale]}, ds=ds)
        if out and sow:
            out[-1]["farmer_date"] = sow.isoformat()
    elif kind == "time_to_physiological_maturity" and (pairs := MATURITY_PAIR.findall(t)):
        parts_t, parts_s = [], []
        unit = "يوم" if locale == "ar-EG" else "days"
        for d, mo, a, b in pairs:
            sd = date(2000, MON[mo], int(d)).isoformat()
            rng = f"{_range(float(a), float(b), locale)} {unit}"
            p = _say("research.maturity_pair", {"range": rng, "sown": (date_text(sd, locale, year=False), date_speech(sd, locale, year=False))}, locale)
            if p is None:
                return None
            parts_t.append(p["text"]); parts_s.append(p["speech"])
        sep = "، و" if locale == "ar-EG" else ", and "
        note("maturity_days", "research.maturity_days", {"pairs": (sep.join(parts_t), sep.join(parts_s)),
             "cultivar": rule["research_context"]["cultivar"]})
    elif kind == "first_cut_and_interval_guidance" and (m := FIRST_CUT.match(t)):
        a, b, c, d = (int(x) for x in m.groups())
        params = {"first": (f"{_range(a, b, locale)} {'يوم' if locale == 'ar-EG' else 'days'}",) * 2,
                  "interval": (f"{_range(c, d, locale)} {'يوم' if locale == 'ar-EG' else 'days'}",) * 2}
        if sow:
            w = (sow + timedelta(days=a), sow + timedelta(days=b))
            note("first_cut", "research.first_cut.dated", {**params, "start": w[0], "end": w[1], "sow": sow}, None)
            if out:
                out[-1]["window"] = {"start": w[0].isoformat(), "end": w[1].isoformat()}
        else:
            note("first_cut", "research.first_cut", params)
    else:
        return None
    return out


def _anchor(season: dict) -> date:
    kind, _, year = season["season_label"].partition("-")
    m, d = SEASON_START.get(kind, (1, 1))
    return date(int(year), m, d)


def research_block(release, plan_input: dict, locale: str) -> dict | None:
    """rendered.research for the reviewed release; None for fixture releases (no source KB)."""
    kb = getattr(getattr(release, "release", None), "agricultural", None)
    if kb is None:
        return None
    covered = {c["crop_id"] for c in kb.get_crops()}
    seasons, empty = [], []
    for s in sorted(plan_input["seasons"], key=lambda x: x["order"]):
        cid = s["crop_id"]["value"]
        if cid is None:
            empty.append(s["season_id"])
            continue
        if cid not in covered:
            continue
        sow = s["sowing_date"]["value"]
        sow = date.fromisoformat(sow) if sow else None
        name = crop_name(cid, locale)
        cn = {"crop": name, "crop_bare": bare(name, locale)}
        notes, other = [], []
        for rule in kb.get_rules(crop_id=cid):
            if len(rule["crop_ids"]) > 1:  # pilot-field placeholders shared by all crops ("currently unknown")
                continue
            parsed = _notes_for_rule(rule, sow, _anchor(s), cn, locale)
            src = _source(kb, rule)
            if parsed:
                notes += [{**n, "source": src} for n in parsed]
            elif rule["scientific_status"] != "NOT APPLICABLE":
                other.append({"rule_id": rule["rule_id"], "label": rule["rule_label"], "source_text": rule["parameters"]["source_text"],
                              "where": _where(rule["research_context"]["locality"], locale), "source": src})
        notes.sort(key=lambda n: KIND_ORDER.index(n["kind"]))
        seasons.append({"season_id": s["season_id"], "crop_id": cid, "crop": name, "notes": notes, "other": other})
    if not seasons and not empty:
        return None
    return {"caveat": _say("research.caveat", {}, locale), "seasons": seasons, "empty_seasons": empty,
            "empty_hint": _say("research.empty_seasons", {}, locale) if empty and seasons else None}
