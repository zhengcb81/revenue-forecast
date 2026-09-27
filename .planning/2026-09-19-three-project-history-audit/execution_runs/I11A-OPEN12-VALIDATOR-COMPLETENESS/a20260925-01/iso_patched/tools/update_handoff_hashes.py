"""I-11-A: append the R2 close-out hash block to handoff.json.

Keeps handoff.current_source_hashes in sync with the delivered bytes so the reviewer
does not have to recompute them before comparing.

Usage: python -X utf8 -B tools/update_handoff_hashes.py <attempt_root>
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


KEYS = [
    "binding.json", "oracle.md", "decision.md", "commands.json", "review.md", "handoff.json",
    "changes.diff", "evidence/I-11-A/hypotheses.json", "evidence/I-11-A/source_map.json",
    "evidence/I-11-A/mechanism_review.md", "evidence/I-11-A/validation_report.json",
    "evidence/I-11-A/attempt_hashes.json", "evidence/I-11-A/final_selfcheck.json",
    "evidence/I-11-A/run_log_archive.json", "evidence/I-11-A/commands_run.log",
    "evidence/I-11-A/state_before.json", "evidence/I-11-A/state_after.json",
    "evidence/I-11-A/extract/P1_xiaomi_content_probe.json",
]


def main() -> int:
    attempt = sys.argv[1]
    path = os.path.join(attempt, "handoff.json")
    doc = json.load(open(path, encoding="utf-8"))
    block = {}
    for rel in KEYS:
        p = os.path.join(attempt, rel.replace("/", os.sep))
        if os.path.exists(p):
            block[rel] = {"byte_size": os.path.getsize(p), "sha256": sha256(p)}
    doc.setdefault("current_source_hashes", {})["r2_close_out_hashes"] = {
        "note": ("hashes of the delivered bytes at R2 close-out; handoff.json itself and "
                 "attempt_hashes.json/commands_run.log/final_selfcheck.json are by-design stale inside "
                 "attempt_hashes.json (see its stale_at_manifest_time.expected) - the values here are the "
                 "current ones"),
        "files": block,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("hashed", len(block), "files into handoff.current_source_hashes.r2_close_out_hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
