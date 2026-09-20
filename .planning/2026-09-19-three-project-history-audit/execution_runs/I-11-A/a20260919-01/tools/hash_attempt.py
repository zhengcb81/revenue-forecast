"""I-11-A: hash every file this attempt produced (delivery manifest).

Excludes the isolated venv (third-party bytes, not this attempt's work) and states
that exclusion explicitly in the manifest.

Usage: python -X utf8 -B tools/hash_attempt.py <attempt_root>
"""

from __future__ import annotations

import hashlib
import json
import os
import sys


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    attempt = sys.argv[1]
    entries = []
    excluded = []
    for base, dirs, files in os.walk(attempt):
        rel_base = os.path.relpath(base, attempt).replace("\\", "/")
        if rel_base.startswith("iso/venv"):
            excluded.append(rel_base + "/**")
            dirs[:] = []
            continue
        for f in sorted(files):
            p = os.path.join(base, f)
            rel = os.path.relpath(p, attempt).replace("\\", "/")
            entries.append({"path": rel, "byte_size": os.path.getsize(p), "sha256": sha256(p)})
    entries.sort(key=lambda e: e["path"])
    manifest = {
        "card_id": "I-11-A",
        "attempt_id": "a20260919-01",
        "generated_by": "tools/hash_attempt.py",
        "excluded_from_manifest": sorted(set(excluded)) + [
            "iso/venv/** (isolated interpreter + pytest package tree; third-party bytes, not this attempt's work)"
        ],
        "file_count": len(entries),
        "files": entries,
        "deliverable_top_level": sorted(
            e["path"] for e in entries if "/" not in e["path"] and e["path"] != ".gitignore"),
    }
    out = os.path.join(attempt, "evidence", "I-11-A", "attempt_hashes.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("files hashed:", len(entries))
    print("deliverables:", ", ".join(manifest["deliverable_top_level"]))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
