"""Minimal request/response contract check; not challenge logic."""

from __future__ import annotations

from typing import Any


def process_request(request: dict[str, Any]) -> dict[str, Any]:
    """Return a fixed, contract-shaped readiness response."""

    if not isinstance(request, dict):
        raise TypeError("request must be a dictionary")
    return {
        "status": "allowed",
        "answer": "Environment ready.",
        "claim_status": "not_applicable",
        "citations": [],
        "tool_calls": [],
    }
