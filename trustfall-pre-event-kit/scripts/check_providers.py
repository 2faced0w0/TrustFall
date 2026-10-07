"""Safely check optional provider configuration and connectivity."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.base import ModelError
from models.factory import create_model


PROVIDERS = [
    ("Mock", "mock", None),
    ("Google AI Studio", "google", "GOOGLE_API_KEY"),
    ("Mistral AI", "mistral", "MISTRAL_API_KEY"),
    ("DeepSeek", "deepseek", "DEEPSEEK_API_KEY"),
    ("Cohere", "cohere", "COHERE_API_KEY"),
    ("Groq Cloud", "groq", "GROQ_API_KEY"),
    ("OpenRouter", "openrouter", "OPENROUTER_API_KEY"),
    ("FreeLLMAPI", "freellmapi", "FREELLMAPI_API_KEY"),
]


def main() -> int:
    print("TRUSTFALL PROVIDER CHECK")
    print("=" * 28)
    mock_ok = False
    for label, provider, key_name in PROVIDERS:
        if key_name and not os.getenv(key_name, "").strip():
            print(f"{label:<22} NOT CONFIGURED")
            continue
        try:
            result = create_model(provider).generate(
                [{"role": "user", "content": "Reply with exactly: TRUSTFALL_READY"}],
                max_tokens=20,
            )
            passed = result.text.strip() == "TRUSTFALL_READY"
            print(f"{label:<22} {'PASS' if passed else 'FAIL'}")
            mock_ok = passed if provider == "mock" else mock_ok
        except ModelError as exc:
            print(f"{label:<22} FAIL ({exc})")
    print()
    print("EVENT READY" if mock_ok else "MOCK MODEL CHECK FAILED")
    print("Live API failure does not prevent event participation when Mock passes.")
    return 0 if mock_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
