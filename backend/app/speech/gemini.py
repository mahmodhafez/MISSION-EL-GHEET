"""Gemini provider for strict extraction. Called by the backend only; the key never reaches the browser.
The transcript is sent to Google and not stored or logged here."""
from __future__ import annotations

import httpx

from .extraction import SYSTEM_INSTRUCTION, response_schema

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiExtractor:
    def __init__(self, api_key: str, model: str, timeout: float = 8.0, client: httpx.Client | None = None):
        self._key, self._model, self._timeout = api_key, model, timeout
        self._client = client or httpx.Client(timeout=timeout)

    def extract(self, transcript: str, question_id: str, locale: str, season_order: int, crop_ids: list[str]) -> str | None:
        """Raw JSON text from the model, or None on any provider error (treated as no_match)."""
        prompt = (f"question_id: {question_id}\nlocale: {locale}\ncurrent season order: {season_order}\n"
                  f"allowed crops: {', '.join(crop_ids)}\ntranscript: {transcript}")
        body = {
            "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json", "responseSchema": response_schema(crop_ids)},
        }
        try:
            r = self._client.post(API.format(model=self._model), json=body, headers={"x-goog-api-key": self._key})
            if r.status_code != 200:
                return None
            parts = r.json()["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts)
        except (httpx.HTTPError, KeyError, IndexError, ValueError):
            return None
