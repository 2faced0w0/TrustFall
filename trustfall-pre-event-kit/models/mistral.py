"""Mistral AI adapter."""

from __future__ import annotations

import os

from .base import OpenAICompatibleAdapter


class MistralAdapter(OpenAICompatibleAdapter):
    @classmethod
    def from_environment(cls, *, model: str) -> "MistralAdapter":
        return cls(
            provider="mistral",
            model=model,
            api_key=os.getenv("MISTRAL_API_KEY", ""),
            base_url="https://api.mistral.ai/v1",
        )


Adapter = MistralAdapter
