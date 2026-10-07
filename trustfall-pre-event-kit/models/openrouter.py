"""OpenRouter adapter."""

from __future__ import annotations

import os

from .base import OpenAICompatibleAdapter


class OpenRouterAdapter(OpenAICompatibleAdapter):
    @classmethod
    def from_environment(cls, *, model: str) -> "OpenRouterAdapter":
        return cls(
            provider="openrouter",
            model=model,
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            base_url="https://openrouter.ai/api/v1",
            extra_headers={"X-Title": "TRUSTFALL Workshop"},
        )


Adapter = OpenRouterAdapter
