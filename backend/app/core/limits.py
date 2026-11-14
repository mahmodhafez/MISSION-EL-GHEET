"""Abuse limits for the public, password-free deployment (backend design §10a).

One ASGI middleware, no extra packages:
- request body caps (413): JSON 64 KB, speech 256 KB;
- per-client sliding-window limits per route group (429 + Retry-After);
- a global daily ceiling on paid calls (Gemini), persisted in SQLite so a restart doesn't reset it.

Sized so one judge (or several behind one venue Wi-Fi) never hits a limit: a full journey is about
10–30 voice turns and under 100 API calls. Counters are in memory: run one worker (Render free does).
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from .errors import envelope

KB = 1024


@dataclass(frozen=True)
class Rule:
    per_minute: int
    per_day: int | None = None


@dataclass(frozen=True)
class Limits:
    enabled: bool = True
    proxy_hops: int = 0          # 0 = socket address; N = Nth address from the right of X-Forwarded-For
    speech: Rule = Rule(20, 300)
    tts: Rule = Rule(60)
    write: Rule = Rule(30, 500)
    read: Rule = Rule(120)
    speech_daily_ceiling: int = 3000
    max_json_bytes: int = 64 * KB
    max_speech_bytes: int = 256 * KB


_WRITE = re.compile(r"^/api/v1/scenarios(/from-answers|/[^/]+/(revisions|promise-test|evidence-cards|replay))?$")


def group_of(method: str, path: str) -> str | None:
    """Route group for limiting, or None for paths that are never limited (health check for the uptime pinger)."""
    if path in ("/api/v1/health", "/health"):
        return None
    if path == "/api/v1/speech/interpret":
        return "speech"
    if path == "/api/v1/speech/tts":
        return "tts"
    if method == "POST" and _WRITE.match(path):
        return "write"
    return "read"


class Counter:
    """Sliding windows per (client, group): timestamps of the last minute and the last day."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._minute: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._day: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def hit(self, key: tuple[str, str], rule: Rule, now: float) -> int:
        """Record a request; return 0 if allowed, else seconds to wait."""
        with self._lock:
            m = self._minute[key]
            while m and m[0] <= now - 60:
                m.popleft()
            if len(m) >= rule.per_minute:
                return max(1, int(m[0] + 60 - now) + 1)
            if rule.per_day is not None:
                d = self._day[key]
                while d and d[0] <= now - 86400:
                    d.popleft()
                if len(d) >= rule.per_day:
                    return max(1, int(d[0] + 86400 - now) + 1)
                d.append(now)
            m.append(now)
            if len(self._minute) > 50_000:  # bound memory against address spraying
                self._sweep(now)
            return 0

    def _sweep(self, now: float) -> None:
        for store, span in ((self._minute, 60), (self._day, 86400)):
            for k in [k for k, q in store.items() if not q or q[-1] <= now - span]:
                del store[k]


def resolved_ip(scope: dict, hops: int) -> str:
    """Client address. Proxies append to X-Forwarded-For, so counting `hops` from the right can't be
    spoofed by a header the client sends itself. hops=0 uses the socket address."""
    ip = (scope.get("client") or ("unknown", 0))[0]
    if hops > 0:
        for name, value in scope.get("headers", []):
            if name == b"x-forwarded-for":
                parts = [p.strip() for p in value.decode("latin-1").split(",") if p.strip()]
                if len(parts) >= hops:
                    ip = parts[-hops]
                break
    return ip


def client_key(scope: dict, hops: int) -> str:
    """Hashed client address: never logged or stored in clear."""
    return hashlib.sha256(resolved_ip(scope, hops).encode()).hexdigest()[:16]


async def _reply(send, status: int, code: str, message: str, retry_after: int | None = None) -> None:
    body = json.dumps(envelope(code, message)).encode()
    headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]
    if retry_after:
        headers.append((b"retry-after", str(retry_after).encode()))
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})


class LimitMiddleware:
    def __init__(self, app, limits: Limits, store=None, clock=time.time):
        self.app, self.limits, self.store, self.clock = app, limits, store, clock
        self.counter = Counter()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not self.limits.enabled or scope["method"] == "OPTIONS":
            return await self.app(scope, receive, send)
        path, method = scope["path"], scope["method"]
        group = group_of(method, path)
        if group is None:
            return await self.app(scope, receive, send)

        cap = self.limits.max_speech_bytes if group == "speech" else self.limits.max_json_bytes
        for name, value in scope.get("headers", []):
            if name == b"content-length" and value.isdigit() and int(value) > cap:
                return await _reply(send, 413, "payload_too_large", f"Request body over {cap // KB} KB.")

        rule = getattr(self.limits, group)
        wait = self.counter.hit((client_key(scope, self.limits.proxy_hops), group), rule, self.clock())
        if wait:
            return await _reply(send, 429, "rate_limited", "Too many requests. Please wait and try again.", wait)
        if group == "speech" and self.store is not None and not self.store.take_daily("speech", self.limits.speech_daily_ceiling):
            return await _reply(send, 429, "daily_budget_reached", "Voice is resting for today; the pictures still work.", 3600)

        # Read the body up front (bounded), so a chunked upload without Content-Length is capped too.
        chunks, size = [], 0
        while True:
            msg = await receive()
            if msg["type"] != "http.request":
                return  # client disconnected
            size += len(msg.get("body", b""))
            if size > cap:
                return await _reply(send, 413, "payload_too_large", f"Request body over {cap // KB} KB.")
            chunks.append(msg.get("body", b""))
            if not msg.get("more_body"):
                break
        body, sent = b"".join(chunks), False

        async def replay():
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        return await self.app(scope, replay, send)
