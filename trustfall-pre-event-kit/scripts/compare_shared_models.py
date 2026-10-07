"""Compare provider packages in sibling TRUSTFALL kits."""

from __future__ import annotations

import hashlib
from pathlib import Path


def hashes(folder: Path) -> dict[str, str]:
    return {
        path.relative_to(folder).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(folder.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def main() -> int:
    parent = Path(__file__).resolve().parents[2]
    pre = parent / "trustfall-pre-event-kit" / "models"
    challenge = parent / "trustfall-survive-it" / "models"
    if not pre.is_dir() or not challenge.is_dir():
        print("[FAIL] Both sibling models/ directories must be present.")
        return 1
    left, right = hashes(pre), hashes(challenge)
    if left == right:
        print(f"[PASS] Shared models packages are identical ({len(left)} files).")
        return 0
    print("[FAIL] Shared models packages differ.")
    for name in sorted(set(left) | set(right)):
        if left.get(name) != right.get(name):
            print(f"  - {name}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
