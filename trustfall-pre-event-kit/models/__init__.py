"""Provider-neutral model adapters shared by both TRUSTFALL kits."""

from .base import (
    BaseModelAdapter,
    ModelAuthenticationError,
    ModelConfigurationError,
    ModelRateLimitError,
    ModelResponseError,
    ModelResult,
    ModelUnavailableError,
)
from .factory import SUPPORTED_PROVIDERS, create_model
from .mock import MockAdapter

__all__ = [
    "BaseModelAdapter",
    "ModelAuthenticationError",
    "ModelConfigurationError",
    "ModelRateLimitError",
    "ModelResponseError",
    "ModelResult",
    "ModelUnavailableError",
    "MockAdapter",
    "SUPPORTED_PROVIDERS",
    "create_model",
]
