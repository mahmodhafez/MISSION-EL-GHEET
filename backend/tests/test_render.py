"""Backend-owned bilingual wording (D4): text uses digits, speech spells numbers; both from planner codes."""
from test_answers import UH001_ANSWERS


def result(client, locale):
    sc = client.post("/api/v1/scenarios/from-answers", json=UH001_ANSWERS).json()
    return sc, client.post(f"/api/v1/scenarios/{sc['id']}/promise-test", params={"locale": locale}).json()


def test_arabic_conflict_text_and_speech(client):
    _, out = result(client, "ar-EG")
    r = out["rendered"]
    assert r["headline"]["text"] == "الخطة فيها تعارض."
    c = r["conflicts"][0]
    assert c["code"] == "sowing_before_protected_cut"
    assert "١٥ مايو" in c["text"] and "٢٠ مايو" in c["text"] and "الذرة الشامية" in c["text"] and "البرسيم" in c["text"]
    assert "خمستاشر مايو" in c["speech"] and "عشرين مايو" in c["speech"]
    assert not any(ch.isdigit() for ch in c["speech"])
    assert [o["text"] for o in r["options"]][0].startswith("لو الذرة الشامية ٢٨ مايو")
    assert any("الموسم ٤" in x["text"] for x in r["coverage"])
    assert [x["text"] for x in r["review_reasons"]] == ["ميعاد الحصاد", "المية", "التربة", "الصنف"]
    assert "مفيش بديل أكيد" in r["takeaway"]["text"]


def test_english_and_relocalise_without_rerun(client):
    sc, out = result(client, "en")
    assert out["rendered"]["conflicts"][0]["text"] == "Sowing the maize on 15 May comes before the berseem cut you kept on 20 May. The cut stays."
    again = client.get(f"/api/v1/results/{out['result_id']}", params={"locale": "ar-EG"}).json()
    assert again["rendered"]["locale"] == "ar-EG" and again["payload"]["result"] == out["result"]


def test_why_absent_when_preparation_unknown(client):
    """The app does not ask preparation days yet, so the planner cannot compute the earliest date: no invented 'why'."""
    _, out = result(client, "en")
    assert out["rendered"]["why"] is None


def test_why_rendered_when_planner_has_preparation_days(client, uh001):
    sc = client.post("/api/v1/scenarios", json=uh001).json()
    out = client.post(f"/api/v1/scenarios/{sc['id']}/promise-test", params={"locale": "ar-EG"}).json()
    why = out["rendered"]["why"]
    assert why["code"] == "preparation_shortfall"
    assert "٢١ مايو" in why["text"] and "٧ أيام" in why["text"] and "٢٨ مايو" in why["text"]
    assert "سبع أيام" in why["speech"] and "تمانية وعشرين مايو" in why["speech"]
