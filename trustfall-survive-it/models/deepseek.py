"""DeepSeek adapter."""

from __future__ import annotations

import os

from .base import OpenAICompatibleAdapter


class DeepSeekAdapter(OpenAICompatibleAdapter):
    @classmethod
    def from_environment(cls, *, model: str) -> "DeepSeekAdapter":
        return cls(
            provider="deepseek",
            model=model,
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            base_url="https://api.deepseek.com",
        )


Adapter = DeepSeekAdapter
