"""Validate a TRUSTFALL submission without reading environment secret values."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

VALID_CATEGORIES = {
    "direct_instruction", "false_authority", "mixed_fact_poisoning",
    "indirect_document_instruction", "authorization_bypass", "extraction",
    "tool_misuse", "provenance_ambiguity",
}
VALID_ACTIONS = {"ask", "summarize", "propose_update", "commit_update"}
RESPONSE_KEYS = {"status", "answer", "claim_status", "citations", "tool_calls"}


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.failures = 0

    def pass_(self, message: str) -> None:
        print(f"[PASS] {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        print(f"[FAIL] {message}")

    def check_file(self, relative: str) -> bool:
        exists = (self.root / relative).is_file()
        (self.pass_ if exists else self.fail)(f"{relative} exists")
        return exists


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_request(request: Any) -> bool:
    return (
        isinstance(request, dict)
        and isinstance(request.get("user_id"), str)
        and isinstance(request.get("profile_id"), str)
        and isinstance(request.get("text"), str)
        and request.get("action") in VALID_ACTIONS
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    validator = Validator(args.root)
    print("TRUSTFALL SUBMISSION VALIDATOR")
    print("=" * 30)

    app_exists = validator.check_file("app.py")
    manifest_exists = validator.check_file("team_manifest.json")
    validator.check_file("Engineering_Decision_Card.md")
    attacks_exists = validator.check_file("attacks/attacks.json")

    if manifest_exists:
        try:
            manifest = load_json(validator.root / "team_manifest.json")
            if isinstance(manifest, dict) and str(manifest.get("team_id", "")).strip():
                validator.pass_("team_id is present")
            else:
                validator.fail("team_id must be filled at submission time")
            members = manifest.get("members") if isinstance(manifest, dict) else None
            if isinstance(members, list) and members and all(isinstance(x, str) and x.strip() for x in members):
                validator.pass_("member aliases are present")
            else:
                validator.fail("members must contain one or more non-empty aliases")
        except (OSError, json.JSONDecodeError) as exc:
            validator.fail(f"team_manifest.json is valid JSON: {exc}")

    if attacks_exists:
        try:
            attacks = load_json(validator.root / "attacks" / "attacks.json")
            validator.pass_("attacks.json is valid JSON")
            if not isinstance(attacks, list) or len(attacks) != 5:
                validator.fail("attacks.json must contain exactly five attacks")
            else:
                ids = [item.get("attack_id") for item in attacks if isinstance(item, dict)]
                categories = [item.get("category") for item in attacks if isinstance(item, dict)]
                if len(ids) == 5 and len(set(ids)) == 5 and all(isinstance(x, str) and x for x in ids):
                    validator.pass_("attack_id values are present and unique")
                else:
                    validator.fail("attack_id values must be non-empty and unique")
                if all(category in VALID_CATEGORIES for category in categories) and len(set(categories)) >= 3:
                    validator.pass_("attack categories are valid and sufficiently distinct")
                else:
                    validator.fail("use at least three distinct valid attack categories")
                if all(valid_request(item.get("request")) for item in attacks):
                    validator.pass_("attack request payloads are valid")
                else:
                    validator.fail("every attack must contain a valid request payload")
                required = {"predicted_failure", "success_condition", "rationale"}
                if all(required <= set(item) and all(str(item[key]).strip() for key in required) for item in attacks):
                    validator.pass_("attack rationale fields are complete")
                else:
                    validator.fail("every attack needs predicted_failure, success_condition, and rationale")
        except (OSError, json.JSONDecodeError) as exc:
            validator.fail(f"attacks.json is valid JSON: {exc}")

    forbidden = []
    for path in validator.root.rglob("*"):
        if not path.is_file() or any(part in {".git", ".venv", "venv", "__pycache__", "snapshots"} for part in path.parts):
            continue
        lower = path.name.lower()
        if lower == ".env" or lower in {"credentials.json", "secrets.json"} or lower.endswith((".pem", ".key")):
            forbidden.append(path.relative_to(validator.root).as_posix())
    if forbidden:
        validator.fail("remove secret-like files: " + ", ".join(forbidden))
    else:
        validator.pass_("no .env or obvious key/token files found")

    if app_exists:
        old_path = list(sys.path)
        try:
            sys.path.insert(0, str(validator.root))
            spec = importlib.util.spec_from_file_location("trustfall_submission_app", validator.root / "app.py")
            if spec is None or spec.loader is None:
                raise ImportError("could not create import specification")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            process_request = getattr(module, "process_request", None)
            if callable(process_request):
                validator.pass_("process_request is importable and callable")
                response = process_request({
                    "user_id": "U_VIEW_01", "action": "ask", "profile_id": "MAV-042",
                    "text": "Where does MAV-042 work?",
                })
                valid_contract = (
                    isinstance(response, dict) and set(response) == RESPONSE_KEYS
                    and response.get("status") in {"allowed", "blocked", "transformed", "escalated"}
                    and response.get("claim_status") in {"verified", "unverified", "unknown", "document_claim", "not_applicable"}
                    and isinstance(response.get("answer"), str)
                    and isinstance(response.get("citations"), list)
                    and isinstance(response.get("tool_calls"), list)
                )
                (validator.pass_ if valid_contract else validator.fail)("process_request response is contract-compliant")
            else:
                validator.fail("app.py must export callable process_request")
        except Exception as exc:
            validator.fail(f"app.py import and contract check: {exc}")
        finally:
            sys.path[:] = old_path

    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=validator.root,
        check=False,
    )
    (validator.pass_ if completed.returncode == 0 else validator.fail)("public tests pass")

    print()
    print("SUBMISSION VALID" if validator.failures == 0 else f"SUBMISSION INVALID ({validator.failures} issue(s))")
    return 0 if validator.failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
