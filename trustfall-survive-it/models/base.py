"""Shared interfaces and small HTTP helpers for model adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelResult:
    """Normalized result returned by every provider."""

    text: str
    provider: str
    model: str
    usage: dict[str, Any] | None = None


class ModelError(RuntimeError):
    """Base class for safe, provider-neutral model errors."""


class ModelConfigurationError(ModelError):
    """Configuration is missing or invalid."""


class ModelAuthenticationError(ModelError):
    """The provider rejected the configured credential."""


class ModelRateLimitError(ModelError):
    """The provider rate limit was reached."""


class ModelUnavailableError(ModelError):
    """The provider could not be reached or is unavailable."""


class ModelResponseError(ModelError):
    """The provider returned a malformed response."""


class BaseModelAdapter(ABC):
    """Provider-neutral synchronous generation interface."""

    provider: str
    model: str

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> ModelResult:
        """Generate text without making any authorization decisions."""


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: float = 20.0,
) -> dict[str, Any]:
    """Send an HTTP request and translate failures without leaking secrets."""

    try:
        import httpx
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise ModelConfigurationError(
            "httpx is required for live providers; install requirements.txt"
        ) from exc

    try:
        response = httpx.request(
            method, url, headers=headers, json=payload, timeout=timeout
        )
    except httpx.TimeoutException as exc:
        raise ModelUnavailableError("The model provider timed out") from exc
    except httpx.RequestError as exc:
        raise ModelUnavailableError("The model provider is unavailable") from exc

    if response.status_code in {401, 403}:
        raise ModelAuthenticationError("The model provider rejected the credential")
    if response.status_code == 429:
        raise ModelRateLimitError("The model provider rate limit was reached")
    if response.status_code >= 500:
        raise ModelUnavailableError(
            f"The model provider returned HTTP {response.status_code}"
        )
    if response.status_code >= 400:
        raise ModelResponseError(
            f"The model request failed with HTTP {response.status_code}"
        )
    try:
        data = response.json()
    except ValueError as exc:
        raise ModelResponseError("The model provider returned invalid JSON") from exc
    if not isinstance(data, dict):
        raise ModelResponseError("The model provider returned an unexpected response")
    return data


class OpenAICompatibleAdapter(BaseModelAdapter):
    """Reusable adapter for OpenAI-compatible chat-completions APIs."""

    def __init__(
        self,
        *,
        provider: str,
        model: str,
        api_key: str,
        base_url: str,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        if not api_key:
            raise ModelConfigurationError(f"{provider} API key is not configured")
        if not model:
            raise ModelConfigurationError(f"{provider} model is not configured")
        if not base_url:
            raise ModelConfigurationError(f"{provider} base URL is not configured")
        self.provider = provider
        self.model = model
        self.api_key = api_key
        normalized = base_url.rstrip("/")
        self.url = (
            normalized
            if normalized.endswith("/chat/completions")
            else f"{normalized}/chat/completions"
        )
        self.extra_headers = extra_headers or {}

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
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }
        data = request_json("POST", self.url, headers=headers, payload=payload)
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelResponseError(
                "The model provider response did not contain generated text"
            ) from exc
        if not isinstance(text, str):
            raise ModelResponseError("The generated model content was not text")
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else None
        return ModelResult(text=text, provider=self.provider, model=self.model, usage=usage)
