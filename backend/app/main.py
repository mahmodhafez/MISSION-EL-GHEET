"""create_app(): settings → data release → store → routes. Run: backend/.venv/bin/uvicorn app.main:app (from backend/)."""
from __future__ import annotations


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import router
from .core import errors
from .core.config import Settings
from .planner.adapter import load_release
from .speech.gemini import GeminiExtractor
from .store.db import Store


def create_app(settings: Settings | None = None, extractor=None) -> FastAPI:
    settings = settings or Settings.load()
    app = FastAPI(title="MISSION EL GHEET API", version="0.1.0")
    app.state.settings = settings
    app.state.release = load_release(settings.data_release_path)
    app.state.store = Store(settings.db_path)
    app.state.extractor = extractor if extractor is not None else (
        GeminiExtractor(settings.gemini_api_key, settings.gemini_model) if settings.gemini_api_key else None)
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
    errors.install(app)
    app.include_router(router)
    return app


def __getattr__(name: str):  # lazy `app` for uvicorn, so importing the module in tests has no side effects
    if name == "app":
        return create_app()
    raise AttributeError(name)


