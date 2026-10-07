"""Environment-driven model adapter factory."""

from __future__ import annotations

import os

from .base import BaseModelAdapter, ModelConfigurationError

SUPPORTED_PROVIDERS = (
    "mock",
    "google",
    "mistral",
    "deepseek",
    "cohere",
    "groq",
    "openrouter",
    "freellmapi",
)


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _model_name(provider: str) -> str:
    return os.getenv(f"{provider.upper()}_MODEL", "").strip() or os.getenv(
        "TRUSTFALL_MODEL", ""
    ).strip()


def create_model(provider: str | None = None) -> BaseModelAdapter:
    """Create the configured adapter; mock is the safe default."""

    _load_dotenv()
    selected = (provider or os.getenv("TRUSTFALL_PROVIDER", "mock")).strip().lower()
    if selected not in SUPPORTED_PROVIDERS:
        choices = ", ".join(SUPPORTED_PROVIDERS)
        raise ModelConfigurationError(
            f"Unknown provider '{selected}'. Expected one of: {choices}"
        )
    if selected == "mock":
        from .mock import MockAdapter

        return MockAdapter(_model_name("mock") or "trustfall-deterministic-v1")

    module = __import__(f"models.{selected}", fromlist=["Adapter"])
    adapter_class = getattr(module, "Adapter")
    return adapter_class.from_environment(model=_model_name(selected))
