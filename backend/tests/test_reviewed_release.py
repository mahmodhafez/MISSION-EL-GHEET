"""Backend on Refaat's reviewed KB (sakha-agricultural-review-2026-11-14.1) and the real Season Replay."""
from test_answers import UH001_ANSWERS


def test_catalogue_separates_offerable_from_research(reviewed):
    c = reviewed.get("/api/v1/catalogue").json()
    assert c["data_release"] == "sakha-agricultural-review-2026-11-14.1"
    # Only crops with reviewed-KB evidence are offered (14 Nov 2026).
    assert set(c["crop_ids"]) == {"wheat", "grain_maize", "grain_sorghum", "berseem"}
    no_evidence = {x["crop_id"] for x in c["crops"] if not x["kb_evidence"]}
    assert {"rice", "faba_bean", "sugar_beet", "egyptian_cotton"} <= no_evidence
    research = {x["crop_id"] for x in c["crops"] if x["research_only"]}
    assert {"watermelon", "strawberry", "cantaloupe", "harankash"} <= research
    assert not research & set(c["crop_ids"])
    assert all(not x["feasibility_eligible"] and x["approval"] == "pending" for x in c["crops"])
    berseem = next(x for x in c["crops"] if x["crop_id"] == "berseem")
    assert berseem["offerable_purposes"] == ["forage"]


def test_uh001_answers_on_reviewed_kb(reviewed):
    sc = reviewed.post("/api/v1/scenarios/from-answers", json=UH001_ANSWERS)
    assert sc.status_code == 201, sc.text
    out = reviewed.post(f"/api/v1/scenarios/{sc.json()['id']}/promise-test", params={"locale": "en"}).json()
    res = out["result"]
    assert out["data_release"] == "sakha-agricultural-review-2026-11-14.1"
    assert res["current"]["status"] == "rejected"
    assert [c["explanation"]["code"] for c in res["current"]["checks"] if c["outcome"] == "fail"][0] == "sowing_before_protected_cut"
    assert res["feasible_alternatives"] == []
    assert [c["evaluation"]["status"] for c in res["review_investigations"]] == ["needs_review", "needs_review"]
    assert out["rendered"]["conflicts"][0]["text"].startswith("Sowing the maize on 15 May")


def test_unknown_crop_is_not_bound(reviewed):
    answers = {**UH001_ANSWERS, "journey": "check", "permissions": [],
               "seasons": [*UH001_ANSWERS["seasons"][:3], {"season_id": "s4", "crop_id": "unknown", "purpose": None, "sowing_date": None}]}
    sc = reviewed.post("/api/v1/scenarios/from-answers", json=answers).json()
    out = reviewed.post(f"/api/v1/scenarios/{sc['id']}/promise-test").json()
    assert out["result"]["current"]["status"] == "rejected"


def test_replay_echoes_planner_statuses(reviewed):
    sc = reviewed.post("/api/v1/scenarios/from-answers", json=UH001_ANSWERS).json()
    res = reviewed.post(f"/api/v1/scenarios/{sc['id']}/promise-test").json()
    r = reviewed.post(f"/api/v1/scenarios/{sc['id']}/replay",
                      json={"sow_dates": ["2027-05-15", "2027-05-28", "2027-06-01"], "result_id": res["result_id"]}).json()
    if r["status"] == "unavailable":  # climate data not present on this machine
        assert r["reason"] == "climate_data_unavailable"
        return
    rep = r["replay"]
    assert [w["planner_status"] for w in rep["windows"]] == ["rejected", "needs_review", "needs_review"]
    assert rep["feasibility"]["climate_changes_planner_status"] is False
    assert rep["label"]["ar"] and rep["label"]["en"]
    bad = reviewed.post(f"/api/v1/scenarios/{sc['id']}/replay", json={"sow_dates": ["2027-05-15"], "window_days": 500})
    assert bad.status_code == 422
