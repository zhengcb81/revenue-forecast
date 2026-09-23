"""Compare two manifest FILES (before/after) WITHOUT rewriting either, re-walk the
live scope for a third opinion, and write the verification doc.

Usage: verify_docs.py <runs_dir> <manifest_before.json> <manifest_after.json> <verification_out.json>

Guarantees:
  * neither manifest file is ever modified;
  * PASS iff before.files == after.files == live re-hash (zero added/removed/changed);
  * reports whether the two manifest documents are byte-identical as files.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

CARDS = ("M01", "M02", "M03", "M04")
ATTEMPT = "a20260919-01"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(runs_dir):
    out = {}
    for card in CARDS:
        root = os.path.join(runs_dir, card, ATTEMPT)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames.sort()
            for name in sorted(filenames):
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, runs_dir).replace(os.sep, "/")
                out[rel] = {"sha256": sha256_file(full), "bytes": os.path.getsize(full)}
    return out


def main():
    runs_dir, before_path, after_path, out_path = sys.argv[1:5]
    before = json.load(open(before_path, encoding="utf-8"))["files"]
    after = json.load(open(after_path, encoding="utf-8"))["files"]
    live = walk(runs_dir)

    added = sorted(set(before) - set(live))
    removed = sorted(set(live) - set(before))
    changed = sorted(rel for rel in set(before) & set(live)
                     if before[rel]["sha256"] != live[rel]["sha256"])
    live_matches_after = live == after
    ok = not (added or removed or changed) and live_matches_after
    doc = {
        "result": "PASS" if ok else "FAIL",
        "method": "before-manifest vs after-manifest document compare PLUS an "
                  "independent live re-hash of the same scope; neither manifest "
                  "document is modified by this verifier",
        "files_checked": len(live),
        "files_identical": len(live) - len(changed),
        "added_files": added,
        "removed_files": removed,
        "changed_files": [{"path": p, "before": before[p]["sha256"],
                           "after": live[p]["sha256"]} for p in changed],
        "zero_byte_drift": ok,
        "historical_rc_and_evidence_untouched": ok,
        "live_rehash_matches_before": live == before,
        "live_rehash_matches_after": live_matches_after,
        "manifest_before_sha256": sha256_file(before_path),
        "manifest_after_sha256": sha256_file(after_path),
        "manifest_docs_byte_identical": sha256_file(before_path) == sha256_file(after_path),
    }
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("verification=%s checked=%d added=%d removed=%d changed=%d "
          "docs_byte_identical=%s"
          % (doc["result"], doc["files_checked"], len(added), len(removed),
             len(changed), doc["manifest_docs_byte_identical"]))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
