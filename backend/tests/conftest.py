import json
import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND.parent))  # repo root: the package is backend.app
REPO = BACKEND.parent
FIXTURE = REPO / "packages" / "meg-core" / "tools" / "fixtures" / "uh001.json"

from backend.app.core.config import Settings  # noqa: E402
from backend.app.main import create_app  # noqa: E402


class FakeExtractor:
    """Stands in for Gemini; returns whatever raw text the test sets."""
    def __init__(self):
        self.reply = None

    def extract(self, *a, **k):
        return self.reply


@pytest.fixture
def uh001():
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return {"snapshot": raw["snapshot"], "exploration": raw["exploration"], "confirm_exploration": True}


@pytest.fixture
def fake():
    return FakeExtractor()


@pytest.fixture
def client(tmp_path, fake):
    settings = Settings.load(db_path=tmp_path / "t.sqlite3", data_release_path=FIXTURE,
                             forecast_bundle=tmp_path / "none.json", gemini_api_key="")
    return TestClient(create_app(settings, extractor=fake))


@pytest.fixture
def client_no_speech(tmp_path):
    settings = Settings.load(db_path=tmp_path / "t.sqlite3", data_release_path=FIXTURE, gemini_api_key="")
    return TestClient(create_app(settings))


@pytest.fixture
def reviewed(tmp_path, fake):
    """App on Refaat's reviewed Sakha KB (the production default)."""
    settings = Settings.load(db_path=tmp_path / "r.sqlite3", data_release_path="reviewed",
                             forecast_bundle=tmp_path / "none.json", gemini_api_key="")
    return TestClient(create_app(settings, extractor=fake))
