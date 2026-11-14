"""rendered.research: sourced, unenforced KB findings next to the farmer's dates (14 Nov 2026). Never changes status."""
from test_answers import UH001_ANSWERS

EMPTY = [{"season_id": f"s{i}", "crop_id": None, "sowing_date": None} for i in (2, 3, 4)]
WHEAT_DEC12 = {"first_winter_year": 2026, "journey": "check", "locks": {"s1": True}, "permissions": [],
               "seasons": [{"season_id": "s1", "crop_id": "wheat", "purpose": "grain", "sowing_date": "2026-12-12"}, *EMPTY]}


def _run(client, answers, locale="en"):
    sc = client.post("/api/v1/scenarios/from-answers", json=answers)
    assert sc.status_code == 201, sc.text
    return client.post(f"/api/v1/scenarios/{sc.json()['id']}/promise-test", params={"locale": locale}).json()


def test_wheat_dec12_gets_sourced_notes(reviewed):
    out = _run(reviewed, WHEAT_DEC12)
    assert out["result"]["current"]["status"] == "needs_review"  # research is advisory only
    r = out["rendered"]["research"]
    assert "Not yet reviewed for Sakha" in r["caveat"]["text"]
    assert r["empty_seasons"] == ["s2", "s3", "s4"] and r["empty_hint"]
    (s1,) = r["seasons"]
    notes = {n["rule_id"]: n for n in s1["notes"]}
    sow = notes["C01"]
    assert sow["window"] == {"start": "2026-11-10", "end": "2026-11-30"}
    assert (sow["placement"], sow["days_outside"], sow["farmer_date"]) == ("after", 12, "2026-12-12")
    assert sow["text"] == "Nile Delta calendar: sow wheat 10 November – 30 November. Your date, 12 December, is 12 days after it."
    assert sow["source"]["locator"] == "Table 1, Nile Delta, Wheat" and sow["source"]["url"].startswith("https://")
    assert notes["C03"]["dates"] == ["2026-11-05", "2026-12-05", "2027-01-05"]
    assert notes["C03"]["text"].endswith("The best date differed by variety.")
    assert notes["C02"]["window"] == {"start": "2027-04-15", "end": "2027-05-10"}
    assert "152–153 days when sown 15 November" in notes["C04"]["text"] and "138–140 days when sown 30 November" in notes["C04"]["text"]
    assert [n["kind"] for n in s1["notes"]] == ["sowing_window", "trial_dates", "maturity_window", "maturity_days"]
    assert {o["rule_id"] for o in s1["other"]} == {"C05", "C06"}  # Kc values: not dates, details only


def test_arabic_wording(reviewed):
    r = _run(reviewed, WHEAT_DEC12, "ar-EG")["rendered"]["research"]
    sow = r["seasons"][0]["notes"][0]
    assert sow["text"].startswith("تقويم الدلتا: زراعة القمح") and "بعدها بـ ١٢ يوم" in sow["text"]
    assert "١٢" not in sow["speech"] and "اتناشر" in sow["speech"]  # audio never reads digits


def test_inside_window_and_no_date(reviewed):
    inside = {**WHEAT_DEC12, "seasons": [{"season_id": "s1", "crop_id": "wheat", "purpose": "grain", "sowing_date": "2026-11-20"}, *EMPTY]}
    sow = _run(reviewed, inside)["rendered"]["research"]["seasons"][0]["notes"][0]
    assert (sow["placement"], sow["days_outside"]) == ("inside", None)
    nodate = {**WHEAT_DEC12, "seasons": [{"season_id": "s1", "crop_id": "wheat", "purpose": "grain", "sowing_date": "unknown"}, *EMPTY]}
    sow = _run(reviewed, nodate)["rendered"]["research"]["seasons"][0]["notes"][0]
    assert sow["placement"] is None and sow["window"] is None and sow["text"].endswith("10 November – 30 November.")


def test_uh001_research_does_not_change_result(reviewed):
    out = _run(reviewed, UH001_ANSWERS)
    assert out["result"]["current"]["status"] == "rejected"
    r = out["rendered"]["research"]
    assert r["empty_seasons"] == [] and r["empty_hint"] is None
    crops = [s["crop_id"] for s in r["seasons"]]
    assert "grain_maize" in crops and "berseem" in crops
    maize = next(s for s in r["seasons"] if s["crop_id"] == "grain_maize")
    sow = next(n for n in maize["notes"] if n["rule_id"] == "C14")
    assert sow["window"] == {"start": "2027-04-15", "end": "2027-05-15"} and sow["placement"] == "inside"
    got = reviewed.get(f"/api/v1/results/{out['result_id']}", params={"locale": "en"}).json()
    assert got["rendered"]["research"]["seasons"] == r["seasons"]
