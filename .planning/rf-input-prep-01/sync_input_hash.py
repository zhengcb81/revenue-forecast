"""Sync the delivered input's final LF byte hash across the planning docs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "inputs/mongodb-fy2025-input.json"
NEW_SHA = hashlib.sha256(INPUT.read_bytes()).hexdigest()
NEW_SIZE = str(INPUT.stat().st_size)
OLD_SHAS = ("6687a3b5ca03842c4af74a02efe11004b81aee24e915833b85d0c99540968f8f",)
DOCS = ["task_plan.md", "progress.md", "handoff.md", "handoff.json"]


def main() -> int:
    changed = []
    for name in DOCS:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        original = text
        for old in OLD_SHAS:
            text = text.replace(old, NEW_SHA)
        text = text.replace('"input_byte_size": 149046', f'"input_byte_size": {NEW_SIZE}')
        text = text.replace("149,046 B", f"{int(NEW_SIZE):,} B")
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed.append(name)
    print(json.dumps({"new_sha256": NEW_SHA, "byte_size": NEW_SIZE, "updated": changed}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
