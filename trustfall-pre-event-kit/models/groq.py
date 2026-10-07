"""Groq Cloud adapter."""

from __future__ import annotations

import os

from .base import OpenAICompatibleAdapter


class GroqAdapter(OpenAICompatibleAdapter):
    @classmethod
    def from_environment(cls, *, model: str) -> "GroqAdapter":
        return cls(
            provider="groq",
            model=model,
            api_key=os.getenv("GROQ_API_KEY", ""),
            base_url="https://api.groq.com/openai/v1",
        )


Adapter = GroqAdapter
