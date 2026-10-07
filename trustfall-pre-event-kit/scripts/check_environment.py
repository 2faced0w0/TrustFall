"""Run the non-sensitive TRUSTFALL pre-event readiness checks."""

from __future__ import annotations

import copy
import importlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_PYTHON = {(3, 11), (3, 12)}
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.factory import create_model
from smoke.environment_report import write_report
from smoke.smoke_app import process_request


def check(label: str, function) -> bool:
    try:
        function()
    except Exception as exc:  # readiness script should explain every failure
        print(f"[FAIL] {label}: {exc}")
        return False
    print(f"[PASS] {label}")
    return True


def require_python() -> None:
    if sys.version_info[:2] not in SUPPORTED_PYTHON:
        raise RuntimeError(
            "Python 3.11 or 3.12 required; "
            f"found {sys.version_info.major}.{sys.version_info.minor}"
        )


def require_packages() -> None:
    importlib.import_module("httpx")
    importlib.import_module("dotenv")


def require_imports() -> None:
    importlib.import_module("models.factory")
    importlib.import_module("smoke.smoke_app")


def require_contract() -> None:
    response = process_request({"text": "check"})
    expected = {"status", "answer", "claim_status", "citations", "tool_calls"}
    if set(response) != expected:
        raise RuntimeError("smoke response contract is invalid")


def require_mock() -> None:
    result = create_model("mock").generate([{"role": "user", "content": "hello"}])
    again = create_model("mock").generate([{"role": "user", "content": "hello"}])
    if result != again:
        raise RuntimeError("mock output is not deterministic")


def require_filesystem() -> None:
    source = {"value": ["original"]}
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "state.json"
        path.write_text(json.dumps(source), encoding="utf-8")
        snapshot = copy.deepcopy(json.loads(path.read_text(encoding="utf-8")))
        snapshot["value"][0] = "changed"
        if json.loads(path.read_text(encoding="utf-8")) != source:
            raise RuntimeError("source changed during snapshot mutation")


def require_tests() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError("unittest suite failed; run python scripts/run_smoke_tests.py")


def main() -> int:
    print("TRUSTFALL PRE-EVENT READINESS CHECK")
    print("=" * 35)
    results = {
        "python": check("Python 3.11 or 3.12", require_python),
        "packages": check("Required packages", require_packages),
        "imports": check("Project imports", require_imports),
        "contract": check("Request/response contract", require_contract),
        "mock": check("Deterministic mock adapter", require_mock),
        "filesystem": check("JSON I/O and temporary snapshot support", require_filesystem),
        "tests": check("unittest runner", require_tests),
    }
    live_configured = any(
        os.getenv(name, "").strip()
        for name in (
            "GOOGLE_API_KEY", "MISTRAL_API_KEY", "DEEPSEEK_API_KEY",
            "COHERE_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY",
            "FREELLMAPI_API_KEY",
        )
    )
    print("[INFO] Live provider configured" if live_configured else "[SKIP] Live provider not configured")
    ready = all(results.values())
    print()
    print(f"CORE ENVIRONMENT: {'READY' if ready else 'NEEDS ATTENTION'}")
    print(f"MOCK MODEL: {'READY' if results['mock'] else 'NOT READY'}")
    print(f"LIVE MODEL ACCESS: {'CONFIGURED' if live_configured else 'NOT CONFIGURED'}")
    print(
        "\nEVENT READY"
        if ready
        else "\nFix:\npython -m pip install -r requirements.txt\nUse Python 3.11 or 3.12, then rerun this check."
    )
    try:
        write_report(
            ROOT / "readiness_report.json",
            {
                "status": "ready" if ready else "needs_attention",
                "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "mock_model": results["mock"],
                "filesystem": results["filesystem"],
                "tests": results["tests"],
                "live_provider": "configured" if live_configured else "not_configured",
            },
        )
    except OSError:
        print("[SKIP] readiness_report.json could not be written; console results remain valid")
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
