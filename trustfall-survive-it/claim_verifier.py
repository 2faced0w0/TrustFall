"""Starter deterministic claim verification against trusted profile data."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ClaimResult:
    answer: str
    claim_status: str
    citations: list[dict[str, str]]
    needs_transform: bool = False


def _citation(profile_id: str, field: str) -> dict[str, str]:
    return {"source": "profiles.json", "profile_id": profile_id, "field": field}


def verify_profile_text(text: str, profile: dict[str, Any]) -> ClaimResult:
    """Answer basic questions and classify simple assertions.

    TODO(participant): split compound text into independent claims, classify
    every claim, and represent mixed results safely within the fixed response
    contract. The baseline stops after recognized trusted neighbors, which is
    intentionally exposed by public tests.
    """

    lowered = text.lower()
    profile_id = str(profile["profile_id"])
    works_in = str(profile["works_in"])
    specialization = str(profile["specialization"])

    if any(word in lowered for word in ("where", "city")) and any(
        word in lowered for word in ("work", "based", "located")
    ):
        return ClaimResult(
            f"{profile_id} works in {works_in}.",
            "verified",
            [_citation(profile_id, "works_in")],
        )
    if any(word in lowered for word in ("specialization", "speciality", "specialty", "skill")):
        return ClaimResult(
            f"{profile_id} specializes in {specialization}.",
            "verified",
            [_citation(profile_id, "specialization")],
        )

    location_match = re.search(r"(?:works|based|located)\s+in\s+([a-z]+)", lowered)
    if location_match and location_match.group(1) != works_in.lower():
        return ClaimResult(
            f"Trusted data does not support the stated location for {profile_id}.",
            "unverified",
            [_citation(profile_id, "works_in")],
        )

    recognized: list[tuple[str, str]] = []
    if works_in.lower() in lowered:
        recognized.append(("works_in", works_in))
    if specialization.lower() in lowered:
        recognized.append(("specialization", specialization))
    if recognized:
        facts = "; ".join(f"{field}={value}" for field, value in recognized)
        return ClaimResult(
            f"Verified from trusted profile data: {facts}.",
            "verified",
            [_citation(profile_id, field) for field, _ in recognized],
        )
    return ClaimResult(
        f"Trusted profile data cannot settle that claim about {profile_id}.",
        "unknown",
        [],
    )
