import json
import subprocess
import sys

from conftest import FIXTURE, REPO


def cli_result():
    out = subprocess.run([sys.executable, "-I", str(REPO / "packages/meg-core/tools/planner_cli.py"), "plan", str(FIXTURE), "--json"],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["result"]


def make(client, body):
    r = client.post("/api/v1/scenarios", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_health_and_catalogue(client):
    h = client.get("/api/v1/health").json()
    assert h["status"] == "ok" and h["runtime_release"] is False and h["speech_interpreter"] == "not_configured"
    c = client.get("/api/v1/catalogue").json()
    assert c["crop_ids"] == ["berseem", "grain_maize", "grain_sorghum", "wheat"]


def test_uh001_golden_matches_planner_cli(client, uh001):
    """Milestone-1 slice: confirmed UH-001 → real Promise Test → rejected, cut preserved, zero feasible."""
    sc = make(client, uh001)
    assert sc["revision"] == 1
    r = client.post(f"/api/v1/scenarios/{sc['id']}/promise-test").json()
    res = r["result"]
    assert res == cli_result()
    assert res["current"]["status"] == "rejected"
    first = next(c for c in res["current"]["checks"] if c["outcome"] == "fail")
    assert first["explanation"]["code"] == "sowing_before_protected_cut"
    assert "cut" in res["current"]["preserved_commitment_ids"]
    assert res["feasible_alternatives"] == []
    assert [c["evaluation"]["status"] for c in res["review_investigations"]] == ["needs_review", "needs_review"]
    assert res["search"]["status"] == "incomplete"
    stored = client.get(f"/api/v1/results/{r['result_id']}").json()
    assert stored["payload"]["result"] == res and stored["current"] is True


def test_revision_conflict_and_staleness(client, uh001):
    sc = make(client, uh001)
    r = client.post(f"/api/v1/scenarios/{sc['id']}/promise-test").json()
    ok = client.post(f"/api/v1/scenarios/{sc['id']}/revisions", json={**uh001, "expected_revision": 1})
    assert ok.status_code == 200 and ok.json()["revision"] == 2
    conflict = client.post(f"/api/v1/scenarios/{sc['id']}/revisions", json={**uh001, "expected_revision": 1})
    assert conflict.status_code == 409 and conflict.json()["error"]["code"] == "revision_conflict"
    assert client.get(f"/api/v1/results/{r['result_id']}").json()["current"] is False
    stale = client.post(f"/api/v1/scenarios/{sc['id']}/evidence-cards", json={"result_id": r["result_id"]})
    assert stale.status_code == 409 and stale.json()["error"]["code"] == "result_not_current"


def test_saved_card_keeps_plan_status(client, uh001):
    sc = make(client, uh001)
    r = client.post(f"/api/v1/scenarios/{sc['id']}/promise-test").json()
    card = client.post(f"/api/v1/scenarios/{sc['id']}/evidence-cards", json={"result_id": r["result_id"]})
    assert card.status_code == 201
    c = card.json()
    assert c["kind"] == "review_draft" and c["plan_status"] == "rejected"
    assert client.get(f"/api/v1/evidence-cards/{c['card_id']}").json()["current"] is True


def test_errors_use_one_envelope(client, uh001):
    bad = client.post("/api/v1/scenarios", json={**uh001, "snapshot": {"nope": 1}})
    assert bad.status_code == 422 and bad.json()["error"]["code"] == "invalid_snapshot"
    other = json.loads(json.dumps(uh001))
    other["snapshot"]["data_release"] = "something-else"
    mism = client.post("/api/v1/scenarios", json=other)
    assert mism.status_code == 409 and mism.json()["error"]["code"] == "data_release_mismatch"
    extra = client.post("/api/v1/scenarios", json={**uh001, "surprise": 1})
    assert extra.status_code == 422 and extra.json()["error"]["code"] == "invalid_request"
    assert client.get("/api/v1/scenarios/scn_missing").json()["error"]["code"] == "scenario_not_found"


def test_side_services_are_honest(client, uh001):
    sc = make(client, uh001)
    far = client.get("/api/v1/forecast", params={"action_dates": ["2027-05-28"], "today": "2026-11-14"}).json()
    assert far["status"] == "not_applicable"
    near = client.get("/api/v1/forecast", params={"action_dates": ["2026-11-16"], "today": "2026-11-14"}).json()
    assert near == {"status": "unavailable", "reason": "bundle_missing"}
    assert client.post("/api/v1/speech/tts", json={"locale": "ar-EG", "code": "conflict", "params": {}}).json()["status"] == "not_generated"


EMPTY = {"seasons": [], "area": None, "answer": {"yes_no": None, "confirm": None, "dont_know": None}, "ambiguous": [], "off_topic": False}
REQ = {"question_id": "s1_crop", "locale": "ar-EG", "transcript": "برسيم", "season_order": 1}


def test_interpret_not_configured(client_no_speech):
    assert client_no_speech.post("/api/v1/speech/interpret", json=REQ).json() == {"status": "unavailable", "reason": "interpreter_not_configured"}


def test_interpret_strict(client, fake):
    season = {"order": 1, "crop": "berseem", "crop_said": None, "purpose": None, "sowing_date": None,
              "last_cut_date": {"day": 20, "month": 5, "year": None}, "must_stay": None}
    fake.reply = json.dumps({**EMPTY, "seasons": [season]})
    ok = client.post("/api/v1/speech/interpret", json=REQ).json()
    assert ok["status"] == "ok" and ok["extraction"]["seasons"][0]["last_cut_date"] == {"day": 20, "month": 5, "year": None}
    fake.reply = json.dumps({**EMPTY, "seasons": [{**season, "crop": "rice"}]})  # not in the catalogue → null
    assert client.post("/api/v1/speech/interpret", json=REQ).json()["extraction"]["seasons"][0]["crop"] is None
    for bad in ("not json", json.dumps({**EMPTY, "advice": "plant rice"}), json.dumps(EMPTY), None):
        fake.reply = bad
        assert client.post("/api/v1/speech/interpret", json=REQ).json() == {"status": "no_match"}
