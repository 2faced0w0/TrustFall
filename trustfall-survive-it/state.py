"""Isolated, resettable in-memory profile state."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"


class ProfileState:
    """Deep-copy trusted JSON into memory and never write the source files."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = data_dir
        self._profiles: dict[str, dict[str, Any]] = {}
        self._users: dict[str, dict[str, Any]] = {}
        self.reset()

    def reset(self) -> None:
        profiles = json.loads((self.data_dir / "profiles.json").read_text(encoding="utf-8"))
        users = json.loads((self.data_dir / "users.json").read_text(encoding="utf-8"))
        self._profiles = copy.deepcopy(profiles)
        self._users = copy.deepcopy(users)

    def role_for(self, user_id: str) -> str:
        record = self._users.get(user_id)
        return str(record.get("role", "unknown")) if record else "unknown"

    def get_profile(self, profile_id: str) -> dict[str, Any] | None:
        profile = self._profiles.get(profile_id)
        return copy.deepcopy(profile) if profile else None

    def update_profile(self, profile_id: str, field: str, value: Any) -> None:
        if profile_id not in self._profiles:
            raise KeyError(profile_id)
        self._profiles[profile_id][field] = copy.deepcopy(value)

    def export_snapshot(self) -> dict[str, dict[str, Any]]:
        return copy.deepcopy(self._profiles)


STORE = ProfileState()


def reset_state() -> None:
    """Restore a clean, deterministic in-memory state for a test or evaluation."""

    STORE.reset()


def export_snapshot() -> dict[str, dict[str, Any]]:
    return STORE.export_snapshot()
