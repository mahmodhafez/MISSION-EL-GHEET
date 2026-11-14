"""Settings from MEG_* environment variables (and backend/.env if present). No secrets are logged."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .limits import Limits, Rule

REPO = Path(__file__).resolve().parents[3]


def _env_file() -> dict[str, str]:
    path = REPO / "backend" / ".env"
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def _get(name: str, default: str, file: dict[str, str]) -> str:
    return os.environ.get(name, file.get(name, default))


def _path(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else REPO / p


@dataclass(frozen=True)
class Settings:
    db_path: Path
    data_release_path: Path | str  # "reviewed" = Refaat's reviewed KB inside meg_core; else a planner fixture JSON
    cors_origins: tuple[str, ...]
    gemini_api_key: str = field(repr=False)
    gemini_model: str
    audio_dir: Path
    forecast_bundle: Path
    limits: Limits = Limits()
    debug_client_ip: bool = False  # health shows the resolved client address; turn on only to check MEG_PROXY_HOPS

    @classmethod
    def load(cls, **overrides: object) -> "Settings":
        f = _env_file()
        s = cls(
            db_path=_path(_get("MEG_DB_PATH", "backend/var/meg.sqlite3", f)),
            data_release_path=(lambda v: v if v == "reviewed" else _path(v))(_get("MEG_DATA_RELEASE_PATH", "reviewed", f)),
            cors_origins=tuple(o for o in _get("MEG_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173", f).split(",") if o),
            gemini_api_key=_get("MEG_GEMINI_API_KEY", "", f),
            gemini_model=_get("MEG_GEMINI_MODEL", "gemini-3.8-flash", f),
            audio_dir=_path(_get("MEG_AUDIO_DIR", "frontend/public/audio", f)),
            forecast_bundle=_path(_get("MEG_FORECAST_BUNDLE", "data/release/forecast_bundle.json", f)),
            limits=_limits(f),
            debug_client_ip=_get("MEG_DEBUG_CLIENT_IP", "0", f) == "1",
        )
        return cls(**{**s.__dict__, **overrides}) if overrides else s


def _rule(name: str, default: Rule, f: dict[str, str]) -> Rule:
    """MEG_LIMIT_<NAME>="per_minute/per_day" (per_day optional), e.g. MEG_LIMIT_SPEECH=20/300."""
    raw = _get(f"MEG_LIMIT_{name}", "", f)
    if not raw:
        return default
    a, _, b = raw.partition("/")
    return Rule(int(a), int(b) if b else None)


def _limits(f: dict[str, str]) -> Limits:
    d = Limits()
    return Limits(
        enabled=_get("MEG_LIMITS", "on", f) != "off",
        proxy_hops=int(_get("MEG_PROXY_HOPS", "0", f)),
        speech=_rule("SPEECH", d.speech, f), tts=_rule("TTS", d.tts, f),
        write=_rule("WRITE", d.write, f), read=_rule("READ", d.read, f),
        speech_daily_ceiling=int(_get("MEG_SPEECH_DAILY_CEILING", str(d.speech_daily_ceiling), f)),
    )
