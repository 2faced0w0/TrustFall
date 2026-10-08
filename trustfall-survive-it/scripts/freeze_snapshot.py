"""Create an immutable-style source snapshot plus SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "snapshots"}
EXCLUDED_FILES = {".env", "readiness_report.json"}


def should_include(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return not any(part in EXCLUDED_DIRS for part in relative.parts) and path.name not in EXCLUDED_FILES and not path.name.endswith((".pyc", ".tmp", "~"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, help="Snapshot label, such as pre-patch or final")
    args = parser.parse_args()
    label = re.sub(r"[^a-zA-Z0-9_-]+", "-", args.label).strip("-")
    if not label:
        parser.error("label must contain letters or numbers")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = ROOT / "snapshots" / f"{stamp}-{label}"
    destination.mkdir(parents=True, exist_ok=False)
    manifest: dict[str, str] = {}
    for source in sorted(ROOT.rglob("*")):
        if not source.is_file() or not should_include(source):
            continue
        relative = source.relative_to(ROOT)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest[relative.as_posix()] = hashlib.sha256(target.read_bytes()).hexdigest()
    (destination / "SHA256_MANIFEST.json").write_text(
        json.dumps({"label": label, "created_utc": stamp, "files": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Snapshot: {destination}")
    print(f"Files hashed: {len(manifest)}")
    print("[PASS] Source project was copied; working files were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
