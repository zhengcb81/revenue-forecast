"""I-14-B file manifest: sha256 (and size) of every artifact in this attempt.

Excludes the isolated venv (thousands of third-party files) but records its
interpreter version instead.  Run LAST, after all other writes.

Usage:
  <iso-python> -X utf8 -B harness/file_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"venv", "__pycache__"}
OUT = ATTEMPT / "evidence" / "file_manifest.json"
SELF = Path(__file__).resolve()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    files = []
    for path in sorted(ATTEMPT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path == OUT or path == SELF:
            continue
        files.append({
            "path": path.relative_to(ATTEMPT).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    doc = {
        "card": "I-14-B",
        "attempt_id": "a20260919-01",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "interpreter": sys.executable,
        "interpreter_version": sys.version,
        "excluded": ["iso/venv/** (isolated interpreter, third-party files)",
                     "**/__pycache__/**", "evidence/file_manifest.json (self)",
                     "harness/file_manifest.py (self)"],
        "file_count": len(files),
        "files": files,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"file_count": len(files), "out": str(OUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
