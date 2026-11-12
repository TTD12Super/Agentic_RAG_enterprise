"""Small server-side Gemini streaming adapter.

The API key is accepted only from process settings and is sent in the
provider header. Provider response bodies are intentionally not exposed.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class GeminiProviderError(RuntimeError):
    """Safe provider failure that contains no provider response body."""

    def __init__(self, code: str = "PROVIDER_ERROR") -> None:
        super().__init__(code)
        self.code = code


class GeminiStreamProvider:
    """Call Gemini's ``streamGenerateContent`` endpoint without an SDK."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        opener=urlopen,
        timeout_seconds: float = 45.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key is required")
        if not model.strip():
            raise ValueError("model is required")
        self._api_key = api_key
        self._model = model
        self._opener = opener
        self._timeout_seconds = timeout_seconds

    def stream(self, messages: Sequence[Mapping[str, str]]) -> Iterator[str]:
        system_messages = [
            message["content"] for message in messages if message.get("role") == "system"
        ]
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": message["content"]}]}
                for message in messages
                if message.get("role") != "system"
            ],
        }
        if system_messages:
            payload["systemInstruction"] = {
                "parts": [{"text": "\n\n".join(system_messages)}]
            }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{quote(self._model, safe='')}:streamGenerateContent?alt=sse"
        )
        request = Request(
            url,
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self._api_key,
            },
            method="POST",
        )

        try:
            response = self._opener(request, timeout=self._timeout_seconds)
            try:
                for raw_line in response:
                    line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else str(raw_line)
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if not data or data == "[DONE]":
                        continue
                    try:
                        parsed = json.loads(data)
                    except json.JSONDecodeError as error:
                        raise GeminiProviderError("PROVIDER_INVALID_RESPONSE") from error
                    yield from _text_parts(parsed)
            finally:
                close = getattr(response, "close", None)
                if callable(close):
                    close()
        except GeminiProviderError:
            raise
        except HTTPError as error:
            raise GeminiProviderError(_http_error_code(error.code)) from error
        except (URLError, TimeoutError, OSError) as error:
            raise GeminiProviderError("PROVIDER_UNAVAILABLE") from error


def _text_parts(payload: object) -> Iterator[str]:
    if not isinstance(payload, Mapping):
        raise GeminiProviderError("PROVIDER_INVALID_RESPONSE")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        content = candidate.get("content")
        if not isinstance(content, Mapping):
            continue
        parts = content.get("parts")
        if not isinstance(parts, list):
            continue
        for part in parts:
            if isinstance(part, Mapping) and isinstance(part.get("text"), str):
                yield part["text"]


def _http_error_code(status: int) -> str:
    if status in {401, 403}:
        return "PROVIDER_AUTH_FAILED"
    if status == 429:
        return "PROVIDER_RATE_LIMITED"
    return "PROVIDER_ERROR"


__all__ = ["GeminiProviderError", "GeminiStreamProvider"]
