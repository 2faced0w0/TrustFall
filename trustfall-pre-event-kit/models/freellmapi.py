"""Configurable OpenAI-compatible FreeLLMAPI adapter."""

from __future__ import annotations

import os

from .base import OpenAICompatibleAdapter


class FreeLLMAPIAdapter(OpenAICompatibleAdapter):
    @classmethod
    def from_environment(cls, *, model: str) -> "FreeLLMAPIAdapter":
        return cls(
            provider="freellmapi",
            model=model,
            api_key=os.getenv("FREELLMAPI_API_KEY", ""),
            base_url=os.getenv("FREELLMAPI_BASE_URL", ""),
        )


Adapter = FreeLLMAPIAdapter
