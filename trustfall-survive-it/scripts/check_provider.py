"""Check only the selected model provider without printing credentials."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.base import ModelError
from models.factory import create_model


def main() -> int:
    provider = os.getenv("TRUSTFALL_PROVIDER", "mock").strip().lower() or "mock"
    print(f"Provider: {provider}")
    try:
        adapter = create_model(provider)
        print(f"Model: {adapter.model if provider == 'mock' else 'configured'}")
        print(f"Credential: {'not required' if provider == 'mock' else 'present'}")
        result = adapter.generate(
            [{"role": "user", "content": "Reply with exactly: TRUSTFALL_READY"}],
            max_tokens=20,
        )
        passed = result.text.strip() == "TRUSTFALL_READY"
        print(f"Connection: {'LOCAL' if provider == 'mock' else ('PASS' if passed else 'FAIL')}")
        print(f"Simple generation: {'PASS' if passed else 'FAIL'}")
        print("\nMODEL READY" if passed else "\nMODEL CHECK FAILED")
        return 0 if passed else 1
    except ModelError as exc:
        print(f"Connection: FAIL ({exc})")
        print("No credential value was printed. Switch to Mock to continue offline.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
