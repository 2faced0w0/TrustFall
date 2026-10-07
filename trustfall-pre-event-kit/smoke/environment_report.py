"""Non-sensitive environment report helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_report(path: Path, report: dict[str, Any]) -> None:
    """Write only the explicitly supplied readiness fields."""

    allowed = {
        key: report[key]
        for key in ("status", "python", "mock_model", "filesystem", "tests", "live_provider")
        if key in report
    }
    path.write_text(json.dumps(allowed, indent=2) + "\n", encoding="utf-8")
