"""Abuse limits for the public deployment (backend design §10a)."""
from fastapi.testclient import TestClient

from conftest import FIXTURE
from backend.app.core.config import Settings
from backend.app.core.limits import Counter, Limits, Rule, client_key, group_of, resolved_ip
from backend.app.main import create_app


def make(tmp_path, **limits):
    s = Settings.load(db_path=tmp_path / "t.sqlite3", data_release_path=FIXTURE, forecast_bundle=tmp_path / "none.json",
                      gemini_api_key="", limits=Limits(**limits))
    return TestClient(create_app(s))


def test_groups():
    assert group_of("GET", "/api/v1/health") is None  # the uptime pinger is never limited
    assert group_of("POST", "/api/v1/speech/interpret") == "speech"
    assert group_of("POST", "/api/v1/scenarios/from-answers") == "write"
    assert group_of("POST", "/api/v1/scenarios/scn_1/promise-test") == "write"
    assert group_of("GET", "/api/v1/catalogue") == "read"


def test_per_minute_limit_returns_429_with_retry_after(tmp_path):
    c = make(tmp_path, read=Rule(3))
    assert [c.get("/api/v1/catalogue").status_code for _ in range(3)] == [200, 200, 200]
    r = c.get("/api/v1/catalogue")
    assert r.status_code == 429 and r.json()["error"]["code"] == "rate_limited"
    assert 1 <= int(r.headers["retry-after"]) <= 61
    assert c.get("/api/v1/health").status_code == 200  # still up for the pinger


def test_per_day_limit_and_window_slides():
    t = [1000.0]
    ctr, rule, key = Counter(), Rule(100, 2), ("ip", "speech")
    assert ctr.hit(key, rule, t[0]) == 0 and ctr.hit(key, rule, t[0] + 1) == 0
    assert ctr.hit(key, rule, t[0] + 2) > 3600  # day used up
    assert ctr.hit(key, rule, t[0] + 86401) == 0  # a day later it's free again


def test_global_daily_ceiling_on_speech(tmp_path):
    c = make(tmp_path, speech_daily_ceiling=2)
    body = {"question_id": "s1_crop", "locale": "en", "transcript": "wheat", "season_order": 1}
    assert [c.post("/api/v1/speech/interpret", json=body).status_code for _ in range(2)] == [200, 200]
    r = c.post("/api/v1/speech/interpret", json=body)
    assert r.status_code == 429 and r.json()["error"]["code"] == "daily_budget_reached"


def test_body_caps(tmp_path):
    c = make(tmp_path)
    big = "x" * (70 * 1024)
    r = c.post("/api/v1/scenarios/from-answers", content=big, headers={"content-type": "application/json"})
    assert r.status_code == 413 and r.json()["error"]["code"] == "payload_too_large"

    def chunks():  # no Content-Length: the cap must still hold
        for _ in range(80):
            yield b"x" * 1024
    r = c.post("/api/v1/scenarios/from-answers", content=chunks(), headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_limits_off(tmp_path):
    c = make(tmp_path, enabled=False, read=Rule(1))
    assert [c.get("/api/v1/catalogue").status_code for _ in range(3)] == [200, 200, 200]


def test_429_keeps_cors_headers(tmp_path):
    c = make(tmp_path, read=Rule(1))
    h = {"origin": "http://127.0.0.1:5173"}
    c.get("/api/v1/catalogue", headers=h)
    r = c.get("/api/v1/catalogue", headers=h)
    assert r.status_code == 429 and r.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"


def test_client_address_from_the_right_of_x_forwarded_for():
    scope = {"client": ("10.0.0.1", 1), "headers": [(b"x-forwarded-for", b"6.6.6.6, 203.0.113.7, 10.1.1.1")]}
    assert resolved_ip(scope, 0) == "10.0.0.1"
    assert resolved_ip(scope, 1) == "10.1.1.1"
    assert resolved_ip(scope, 2) == "203.0.113.7"  # a spoofed left-most value is never used
    assert client_key(scope, 2) != "203.0.113.7" and len(client_key(scope, 2)) == 16  # stored hashed only
