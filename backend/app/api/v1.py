"""/api/v1 routes (backend design §5). Milestone 1 is real: health, catalogue, scenarios with revisions,
Promise Test on the meg_core planner, stored results, review-draft evidence cards. Speech interpretation is
real when a Gemini key is configured. Replay, forecast and TTS report honest statuses until their inputs exist."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Literal

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from ..core.errors import ApiError
from ..planner.adapter import InputValidationError, run_promise_test
from ..planner.answers import Answers, to_payload
from ..i18n.render import render_result
from ..speech.extraction import is_empty, validate

Locale = Literal["ar-EG", "en"]

router = APIRouter(prefix="/api/v1")


class ScenarioInputBody(BaseModel):
    """Planner-shaped input (meg_core JSON). Proposed until the shared contracts are signed off."""
    model_config = ConfigDict(extra="forbid")
    snapshot: dict
    exploration: dict = Field(default_factory=lambda: {"choices": [], "catalogue_choices": []})
    confirm_exploration: bool = False


class RevisionBody(ScenarioInputBody):
    expected_revision: int


class CardBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    result_id: str


class InterpretBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_id: str = Field(max_length=64)
    locale: Literal["ar-EG", "en"]
    transcript: str = Field(min_length=1, max_length=500)
    season_order: int = Field(ge=1, le=4)


class TtsBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    locale: Literal["ar-EG", "en"]
    code: str = Field(max_length=80)
    params: dict = Field(default_factory=dict)


def _app(req: Request):
    return req.app.state


@router.get("/health")
def health(req: Request):
    s = _app(req)
    return {"status": "ok", "data_release": s.release.data_release, "runtime_release": False,
            "forecast_bundle": "present" if s.settings.forecast_bundle.exists() else "missing",
            "speech_interpreter": "configured" if s.settings.gemini_api_key else "not_configured"}


@router.get("/catalogue")
def catalogue(req: Request):
    return _app(req).release.catalogue()


def _scenario_or_404(req: Request, sid: str) -> dict:
    sc = _app(req).store.get_scenario(sid)
    if sc is None:
        raise ApiError(404, "scenario_not_found")
    return sc


def _payload(body: ScenarioInputBody) -> dict:
    return {"snapshot": body.snapshot, "exploration": body.exploration, "confirm_exploration": body.confirm_exploration}


def _check_decodes(req: Request, payload: dict) -> None:
    from ..planner.adapter import decode_input
    try:
        snapshot, _, _ = decode_input(payload)
    except (ValueError, KeyError, TypeError) as e:
        raise ApiError(422, "invalid_snapshot", str(e)[:300]) from None
    if snapshot.data_release != _app(req).release.data_release:
        raise ApiError(409, "data_release_mismatch", "Snapshot was built for another data release.", ["snapshot.data_release"])


@router.post("/scenarios", status_code=201)
def create_scenario(body: ScenarioInputBody, req: Request):
    payload = _payload(body)
    _check_decodes(req, payload)
    return _app(req).store.create_scenario(_app(req).release.data_release, payload)


@router.post("/scenarios/from-answers", status_code=201)
def create_from_answers(body: Answers, req: Request):
    """App answers → planner snapshot (unknowns explicit, nothing assumed) → stored scenario."""
    payload = to_payload(body, _app(req).release)
    _check_decodes(req, payload)
    return _app(req).store.create_scenario(_app(req).release.data_release, payload)


@router.get("/scenarios/{sid}")
def get_scenario(sid: str, req: Request):
    return _scenario_or_404(req, sid)


@router.post("/scenarios/{sid}/revisions")
def revise(sid: str, body: RevisionBody, req: Request):
    _scenario_or_404(req, sid)
    payload = _payload(body)
    _check_decodes(req, payload)
    sc = _app(req).store.revise_scenario(sid, body.expected_revision, payload)
    if sc is None:
        raise ApiError(409, "revision_conflict", "The scenario changed since you loaded it.", ["expected_revision"])
    return sc


@router.post("/scenarios/{sid}/promise-test")
def promise_test(sid: str, req: Request, locale: Locale = "ar-EG"):
    s = _app(req)
    sc = _scenario_or_404(req, sid)
    try:
        out = run_promise_test(sc["input"], s.release)
    except InputValidationError as e:
        raise ApiError(422, e.code, "The planner refused this input.", list(e.field_paths)) from None
    rid = s.store.add_result(sid, sc["revision"], "promise_test", s.release.data_release, out)  # codes + params only
    rendered = render_result(out["result"], sc["input"]["snapshot"]["input"], locale)
    return {"result_id": rid, "scenario_id": sid, "revision": sc["revision"], "data_release": s.release.data_release, **out, "rendered": rendered}


@router.get("/results/{rid}")
def get_result(rid: str, req: Request, locale: Locale = "ar-EG"):
    r = _app(req).store.get_result(rid)
    if r is None:
        raise ApiError(404, "result_not_found")
    sc = _app(req).store.get_scenario(r["scenario_id"])
    rendered = render_result(r["payload"]["result"], sc["input"]["snapshot"]["input"], locale) if sc else None
    return {**r, "current": sc is not None and sc["revision"] == r["revision"], "rendered": rendered}


@router.post("/scenarios/{sid}/evidence-cards", status_code=201)
def save_card(sid: str, body: CardBody, req: Request):
    """Saves a REVIEW DRAFT. Saving is storage, not approval: the plan keeps its status."""
    s = _app(req)
    sc = _scenario_or_404(req, sid)
    r = s.store.get_result(body.result_id)
    if r is None or r["scenario_id"] != sid:
        raise ApiError(404, "result_not_found")
    if r["revision"] != sc["revision"]:
        raise ApiError(409, "result_not_current", "Run the check again for the current revision before saving.")
    payload = {"kind": "review_draft", "plan_status": r["payload"]["result"]["current"]["status"], "data_release": r["data_release"]}
    cid = s.store.add_card(sid, sc["revision"], r["id"], payload)
    return {"card_id": cid, "scenario_id": sid, "revision": sc["revision"], "result_id": r["id"], **payload}


@router.get("/evidence-cards/{cid}")
def get_card(cid: str, req: Request):
    s = _app(req)
    c = s.store.get_card(cid)
    if c is None:
        raise ApiError(404, "card_not_found")
    sc = s.store.get_scenario(c["scenario_id"])
    return {**c, "current": sc is not None and sc["revision"] == c["revision"]}


@router.post("/scenarios/{sid}/replay")
def replay(sid: str, req: Request):
    _scenario_or_404(req, sid)
    # Historical NASA replay is not connected yet (ML/data work in progress). Never a fake value.
    return {"status": "unavailable", "reason": "replay_not_connected"}


@router.get("/forecast")
def forecast(req: Request, action_dates: list[date] = Query(default_factory=list), today: date | None = None):
    """Experimental 7-day outlook status (ML contract §6). It never changes whether a plan holds."""
    s = _app(req)
    t = today or date.today()
    if action_dates and all(d > t + timedelta(days=7) or d < t for d in action_dates):
        return {"status": "not_applicable", "reason": "outside_forecast_window"}
    if not s.settings.forecast_bundle.exists():
        return {"status": "unavailable", "reason": "bundle_missing"}
    return {"status": "unavailable", "reason": "bundle_reader_not_implemented"}


@router.post("/speech/interpret")
def interpret(body: InterpretBody, req: Request):
    s = _app(req)
    if s.extractor is None:
        return {"status": "unavailable", "reason": "interpreter_not_configured"}
    crop_ids = s.release.catalogue()["crop_ids"]
    raw = s.extractor.extract(body.transcript, body.question_id, body.locale, body.season_order, crop_ids)
    clean = validate(raw, crop_ids) if raw is not None else None
    if clean is None or is_empty(clean):
        return {"status": "no_match"}
    return {"status": "ok", "extraction": clean}


@router.post("/speech/tts")
def tts(body: TtsBody, req: Request):
    """Lookup only (D7): audio is pre-generated offline with ElevenLabs. Missing → not_generated."""
    return {"status": "not_generated", "reason": "audio_not_generated", "code": body.code, "locale": body.locale}
