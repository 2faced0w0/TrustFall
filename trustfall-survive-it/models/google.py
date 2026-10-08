"""Google AI Studio Gemini REST adapter."""

from __future__ import annotations

import os
from typing import Any

from .base import (
    BaseModelAdapter,
    ModelConfigurationError,
    ModelResponseError,
    ModelResult,
    request_json,
)


class GoogleAdapter(BaseModelAdapter):
    provider = "google"

    def __init__(self, *, model: str, api_key: str) -> None:
        if not api_key:
            raise ModelConfigurationError("google API key is not configured")
        if not model:
            raise ModelConfigurationError("google model is not configured")
        self.model = model
        self.api_key = api_key

    @classmethod
    def from_environment(cls, *, model: str) -> "GoogleAdapter":
        return cls(model=model, api_key=os.getenv("GOOGLE_API_KEY", ""))

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> ModelResult:
        contents = [
            {
                "role": "model" if item.get("role") == "assistant" else "user",
                "parts": [{"text": str(item.get("content", ""))}],
            }
            for item in messages
        ]
        generation: dict[str, Any] = {"temperature": temperature}
        if max_tokens is not None:
            generation["maxOutputTokens"] = max_tokens
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        data = request_json(
            "POST",
            url,
            headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
            payload={"contents": contents, "generationConfig": generation},
        )
        try:
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(part["text"] for part in parts if "text" in part)
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelResponseError("Google response did not contain generated text") from exc
        if not text:
            raise ModelResponseError("Google response contained empty generated text")
        return ModelResult(text=text, provider=self.provider, model=self.model)


Adapter = GoogleAdapter
