"""Re-hash the historical scope and compare against the pre-run manifest.

Usage:
  verify_manifest.py <plan_execution_runs_dir> <manifest_before.json> <manifest_after.json> <verification_out.json>

PASS iff: same file set (zero added, zero removed) and identical sha256 for
every single file. Any drift is reported per file.
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


def walk(runs_dir: str) -> dict:
    out = {}
    for card in CARDS:
        root = os.path.join(runs_dir, card, ATTEMPT)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames.sort()
            for name in sorted(filenames):
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, runs_dir).replace(os.sep, "/")
                out[rel] = {"sha256": sha256_file(full),
                            "bytes": os.path.getsize(full)}
    return out


def main() -> int:
    runs_dir, before_path, after_path, out_path = sys.argv[1:5]
    before = json.load(open(before_path, encoding="utf-8"))["files"]
    live = walk(runs_dir)                      # fresh re-hash, post-run
    with open(after_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"scope": ["execution_runs/%s/%s" % (c, ATTEMPT) for c in CARDS],
                   "policy": "post-run re-hash of the identical scope",
                   "file_count": len(live),
                   "total_bytes": sum(v["bytes"] for v in live.values()),
                   "files": live},
                  fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    removed = sorted(set(before) - set(live))
    added = sorted(set(live) - set(before))
    changed = sorted(rel for rel in set(before) & set(live)
                     if before[rel]["sha256"] != live[rel]["sha256"])
    ok = not (removed or added or changed)
    doc = {
        "result": "PASS" if ok else "FAIL",
        "files_checked": len(live),
        "files_identical": len(live) - len(changed) - len(added),
        "added_files": added,
        "removed_files": removed,
        "changed_files": [{"path": p, "before": before[p]["sha256"],
                           "after": live[p]["sha256"]} for p in changed],
        "zero_byte_drift": ok,
        "historical_rc_and_evidence_untouched": ok,
        "manifest_before_sha256": sha256_file(before_path),
        "manifest_after_sha256": sha256_file(after_path),
    }
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("verification=%s checked=%d added=%d removed=%d changed=%d"
          % (doc["result"], doc["files_checked"], len(added), len(removed), len(changed)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
