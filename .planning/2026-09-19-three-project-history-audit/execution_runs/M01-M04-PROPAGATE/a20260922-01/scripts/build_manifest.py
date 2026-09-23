"""Build a full-tree sha256 manifest of the historical M01..M04 attempt dirs.

Usage:
  build_manifest.py <plan_execution_runs_dir> <out_json>

Scope (frozen in oracle.md §5): the four directories
  M01/a20260919-01, M02/a20260919-01, M03/a20260919-01, M04/a20260919-01
— every file, including venvs, runners, evidence and rc carriers.
READ-ONLY walk: nothing under those directories is ever written by this script.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

CARDS = ("M01", "M02", "M03", "M04")
ATTEMPT = "a20260919-01"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    runs_dir, out_path = sys.argv[1], sys.argv[2]
    files = {}
    total_bytes = 0
    for card in CARDS:
        root = os.path.join(runs_dir, card, ATTEMPT)
        if not os.path.isdir(root):
            print("MISSING historical dir:", root, file=sys.stderr)
            return 2
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames.sort()
            for name in sorted(filenames):
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, runs_dir).replace(os.sep, "/")
                files[rel] = {"sha256": sha256_file(full),
                              "bytes": os.path.getsize(full)}
                total_bytes += files[rel]["bytes"]
    doc = {
        "scope": ["execution_runs/%s/%s" % (c, ATTEMPT) for c in CARDS],
        "policy": "READ-ONLY pin: this manifest is built BEFORE the arm runs and "
                  "re-built AFTER them; every file must hash identically.",
        "file_count": len(files),
        "total_bytes": total_bytes,
        "files": files,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("manifest files=%d bytes=%d -> %s" % (len(files), total_bytes, out_path))
    print("manifest_sha256=%s" % sha256_file(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
