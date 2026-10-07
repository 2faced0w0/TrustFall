"""Deterministic offline model adapter."""

from __future__ import annotations

import re

from .base import BaseModelAdapter, ModelResult


class MockAdapter(BaseModelAdapter):
    """A deterministic adapter for tests, workshops, and offline use."""

    provider = "mock"

    def __init__(self, model: str = "trustfall-deterministic-v1") -> None:
        self.model = model

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> ModelResult:
        del temperature, max_tokens
        content = " ".join(
            str(message.get("content", "")) for message in messages
        ).strip()
        if "TRUSTFALL_READY" in content:
            text = "TRUSTFALL_READY"
        elif "summar" in content.lower():
            clean = re.sub(r"\s+", " ", content).strip()
            text = f"Mock summary: {clean[:180]}"
        elif content:
            text = f"Mock response: {content[:180]}"
        else:
            text = "Mock response ready."
        return ModelResult(text=text, provider=self.provider, model=self.model, usage=None)
