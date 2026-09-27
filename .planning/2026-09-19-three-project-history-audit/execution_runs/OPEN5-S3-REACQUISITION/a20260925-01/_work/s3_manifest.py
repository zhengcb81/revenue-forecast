"""S3 manifest: sha256-level before/after snapshot of read-only reference dirs.

Usage: python s3_manifest.py --out <manifest.json> --label before|after
Read-only: opens files for reading only.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys

REF_DIRS = [
    ".planning/2026-09-19-three-project-history-audit/execution_runs/I-11-A/a20260919-01",
    ".planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01",
    ".planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-PEND5B-OCR-CAPABILITY/a20260924-01",
]


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(root: str):
    # Windows MAX_PATH guard: use the \\?\ extended-length prefix (read-only access)
    if os.name == "nt" and not root.startswith("\\\\?\\"):
        root = "\\\\?\\" + os.path.abspath(root)
    entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            fp = os.path.join(dirpath, name)
            rel = os.path.relpath(fp, root).replace("\\", "/")
            st = os.stat(fp)
            entries.append(
                {
                    "rel": rel,
                    "bytes": st.st_size,
                    "mtime_ns": st.st_mtime_ns,
                    "sha256": sha256_file(fp),
                }
            )
    return entries


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    args = ap.parse_args()

    out = {
        "label": args.label,
        "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "read_only_hash_snapshot",
        "dirs": [],
    }
    for d in REF_DIRS:
        entries = walk(d)
        agg = hashlib.sha256()
        for e in entries:
            agg.update(f"{e['rel']}|{e['bytes']}|{e['sha256']}\n".encode("utf-8"))
        out["dirs"].append(
            {
                "dir": d,
                "files": len(entries),
                "bytes": sum(e["bytes"] for e in entries),
                "aggregate_sha256": agg.hexdigest(),
                "entries": entries,
            }
        )
        print(f"{d}: files={len(entries)} agg={agg.hexdigest()[:16]}", flush=True)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", mode=0o777, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(args.out, "r", encoding="utf-8") as f:
        json.load(f)
    print("wrote", args.out, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
