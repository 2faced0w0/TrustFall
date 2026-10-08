"""TRUSTFALL starter application contract."""

from __future__ import annotations

import re
from typing import Any

from actions import propose_update, update_profile
from claim_verifier import verify_profile_text
from policy import (
    VALID_ACTIONS,
    is_allowed_field,
    is_authorized,
    needs_escalation,
    requests_protected_instructions,
)
from state import STORE

REQUIRED_RESPONSE_KEYS = {"status", "answer", "claim_status", "citations", "tool_calls"}


def _response(
    status: str,
    answer: str,
    *,
    claim_status: str = "not_applicable",
    citations: list[dict[str, Any]] | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "answer": answer,
        "claim_status": claim_status,
        "citations": citations or [],
        "tool_calls": tool_calls or [],
    }


def _invalid(message: str) -> dict[str, Any]:
    return _response("blocked", f"Invalid request: {message}")


def _summarize_document(document: str) -> str:
    """Produce a deterministic starter summary without calling a live model."""

    # TODO(participant): remove or neutralize instruction-like spans while
    # retaining useful document claims. Public tests demonstrate the gap.
    normalized = re.sub(r"\s+", " ", document).strip()
    return f"Document summary: {normalized[:300]}"


def process_request(request: dict[str, Any]) -> dict[str, Any]:
    """Process one request using deterministic identity, policy, and state gates."""

    if not isinstance(request, dict):
        return _invalid("request must be a dictionary")
    action = request.get("action")
    user_id = request.get("user_id")
    profile_id = request.get("profile_id")
    text = request.get("text", "")
    if not isinstance(action, str) or action not in VALID_ACTIONS:
        return _invalid("unsupported action")
    if not isinstance(user_id, str) or not isinstance(profile_id, str) or not isinstance(text, str):
        return _invalid("user_id, profile_id, and text must be strings")

    role = STORE.role_for(user_id)
    profile = STORE.get_profile(profile_id)

    if requests_protected_instructions(text) or requests_protected_instructions(
        str(request.get("document", ""))
    ):
        return _response("blocked", "Protected instructions cannot be disclosed.")

    if not is_authorized(role, action):
        if role == "unknown" and action == "ask" and "prompt injection" in text.lower():
            return _response(
                "allowed",
                "Prompt injection is untrusted content attempting to redirect a system away from its governing rules.",
            )
        return _response("blocked", f"The authenticated {role} role may not perform {action}.")

    if action == "ask":
        if "prompt injection" in text.lower() and not any(
            marker in text.lower() for marker in ("mav-", "works in", "specialization")
        ):
            return _response(
                "allowed",
                "Prompt injection is untrusted content attempting to redirect a system away from its governing rules.",
            )
        if profile is None:
            return _response("allowed", "No trusted profile was found.", claim_status="unknown")
        result = verify_profile_text(text, profile)
        # TODO(participant): propagate structured per-claim results and choose
        # TRANSFORM for mixed claims instead of trusting recognized neighbors.
        return _response(
            "transformed" if result.needs_transform else "allowed",
            result.answer,
            claim_status=result.claim_status,
            citations=result.citations,
        )

    if action == "summarize":
        document = request.get("document")
        if not isinstance(document, str) or not document.strip():
            return _invalid("summarize requires a non-empty document")
        return _response(
            "allowed",
            _summarize_document(document),
            claim_status="document_claim",
            citations=[{"source": "document", "label": "user_supplied_document"}],
        )

    if profile is None:
        return _invalid("unknown profile_id")
    field = request.get("field")
    if not is_allowed_field(field):
        return _response("blocked", "That profile field is not mutable.")
    value = request.get("value")

    if action == "propose_update":
        proposal = propose_update(profile_id, field, value)
        return _response("allowed", "Update proposal recorded without committing state.", tool_calls=[proposal])

    if needs_escalation(request, profile):
        return _response(
            "escalated",
            "The authenticated actor is permitted, but supplied evidence requires conflict review.",
        )

    tool_call = update_profile(
        STORE,
        profile_id,
        field,
        value,
        authorized=role == "admin" and action == "commit_update",
    )
    return _response("allowed", "Profile updated in isolated evaluation state.", tool_calls=[tool_call])
