"""App answers → planner snapshot → real Promise Test."""

UH001_ANSWERS = {
    "first_winter_year": 2026, "journey": "explore", "confirm_exploration": True,
    "seasons": [
        {"season_id": "s1", "crop_id": "berseem", "purpose": "forage", "sowing_date": "unknown", "last_cut_date": "2027-05-20"},
        {"season_id": "s2", "crop_id": "grain_maize", "purpose": "grain", "sowing_date": "2027-05-15"},
        {"season_id": "s3", "crop_id": "wheat", "purpose": "grain", "sowing_date": "2027-11-20"},
        {"season_id": "s4", "crop_id": "grain_sorghum", "purpose": "grain", "sowing_date": "2028-06-01"},
    ],
    "locks": {"s1": True, "s2": True, "s3": True},
    "permissions": [
        {"season_id": "s2", "field": "sowing_date", "allowed_values": ["2027-05-28", "2027-06-01"]},
        {"season_id": "s4", "field": "crop_id", "allowed_values": ["grain_maize"]},
    ],
}


def run(client, answers):
    sc = client.post("/api/v1/scenarios/from-answers", json=answers)
    assert sc.status_code == 201, sc.text
    return sc.json(), client.post(f"/api/v1/scenarios/{sc.json()['id']}/promise-test").json()


def test_uh001_answers_give_the_reference_outcome(client):
    sc, out = run(client, UH001_ANSWERS)
    res = out["result"]
    assert res["current"]["status"] == "rejected"
    assert [c["explanation"]["code"] for c in res["current"]["checks"] if c["outcome"] == "fail"] == ["sowing_before_protected_cut"]
    assert res["feasible_alternatives"] == []
    assert [[ch["after"]["value"] for ch in c["changes"] if ch["direct"]] for c in res["review_investigations"]] == [["2027-05-28"], ["2027-06-01"]]
    assert res["search"]["status"] == "incomplete"


def test_unknowns_are_explicit_never_assumed(client):
    sc, _ = run(client, UH001_ANSWERS)
    s2 = sc["input"]["snapshot"]["input"]["seasons"][1]
    assert s2["harvest_or_cut_date"] == {**s2["harvest_or_cut_date"], "value": None, "unknown_reason": "not_collected", "confirmation_status": "confirmed_unknown"}
    assert s2["preparation_days_after_release"]["value"] is None and s2["preparation_days_after_release"]["unit"] == "day"
    s1 = sc["input"]["snapshot"]["input"]["seasons"][0]
    assert s1["sowing_date"]["unknown_reason"] == "farmer_unknown"
    assert s1["crop_id"]["origin"] == "farmer_report"


def test_check_journey_has_no_search(client):
    _, out = run(client, {**UH001_ANSWERS, "journey": "check", "permissions": []})
    assert out["result"]["review_investigations"] == [] and out["result"]["current"]["status"] == "rejected"


def test_answers_are_strict(client):
    bad = client.post("/api/v1/scenarios/from-answers", json={**UH001_ANSWERS, "seasons": UH001_ANSWERS["seasons"][:3]})
    assert bad.status_code == 422 and bad.json()["error"]["code"] == "invalid_request"
