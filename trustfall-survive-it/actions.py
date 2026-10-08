"""Simulated proposal and state-changing actions."""

from __future__ import annotations

from typing import Any

from state import ProfileState


def propose_update(profile_id: str, field: str, value: Any) -> dict[str, Any]:
    """Return a proposal record without mutating state."""

    return {
        "tool": "propose_update",
        "profile_id": profile_id,
        "field": field,
        "value": value,
        "executed": False,
    }


def update_profile(
    store: ProfileState,
    profile_id: str,
    field: str,
    value: Any,
    *,
    authorized: bool,
) -> dict[str, Any]:
    """Mutate only when deterministic application policy explicitly authorizes it."""

    # TODO(participant): replace the boolean with a richer non-forgeable
    # decision/capability object as the policy implementation matures.
    if not authorized:
        raise PermissionError("state mutation was not authorized")
    store.update_profile(profile_id, field, value)
    return {
        "tool": "update_profile",
        "profile_id": profile_id,
        "field": field,
        "executed": True,
    }
