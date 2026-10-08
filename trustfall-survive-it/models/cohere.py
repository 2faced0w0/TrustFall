"""Cohere v2 Chat adapter."""

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


class CohereAdapter(BaseModelAdapter):
    provider = "cohere"

    def __init__(self, *, model: str, api_key: str) -> None:
        if not api_key:
            raise ModelConfigurationError("cohere API key is not configured")
        if not model:
            raise ModelConfigurationError("cohere model is not configured")
        self.model = model
        self.api_key = api_key

    @classmethod
    def from_environment(cls, *, model: str) -> "CohereAdapter":
        return cls(model=model, api_key=os.getenv("COHERE_API_KEY", ""))

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> ModelResult:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        data = request_json(
            "POST",
            "https://api.cohere.com/v2/chat",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            payload=payload,
        )
        try:
            parts = data["message"]["content"]
            text = "".join(part["text"] for part in parts if part.get("type") == "text")
        except (KeyError, TypeError) as exc:
            raise ModelResponseError("Cohere response did not contain generated text") from exc
        if not text:
            raise ModelResponseError("Cohere response contained empty generated text")
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else None
        return ModelResult(text=text, provider=self.provider, model=self.model, usage=usage)


Adapter = CohereAdapter
