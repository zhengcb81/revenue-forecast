"""Backfill one missed row in recovery/bookkeeping_r3/summary.json (one M-card attempt).

The first run of ``transcribe_r3_verdict.py`` proved the review.md append in
``evidence/<CARD>/verdict_transcription_r3.json`` but did not add review.md itself to the summary's
``changes`` before -> after table. This script adds exactly that row, taking every value from the
already-verified proof file (source sha256, pre-append sha256/bytes) and from disk (post-append
sha256/bytes). Nothing else in the summary is touched.

The same fix is applied to ``transcribe_r3_verdict.py`` itself, so a future re-run produces the row
directly and this backfill becomes a no-op.

Exit codes: 0 ok (or nothing to do), 9 the proof file disagrees with disk, 1 harness error.
"""

from __future__ import annotations

import hashlib
import json
import os

SCRIPT = os.path.abspath(__file__)
ATTEMPT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT)))
CARD = os.path.basename(os.path.dirname(ATTEMPT))
SUMMARY = os.path.join(ATTEMPT, "recovery", "bookkeeping_r3", "summary.json")
PROOF = os.path.join(ATTEMPT, "evidence", CARD, "verdict_transcription_r3.json")
REVIEW = os.path.join(ATTEMPT, "review.md")


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    summary = json.load(open(SUMMARY, "r", encoding="utf-8"))
    proof = json.load(open(PROOF, "r", encoding="utf-8"))
    review_now = sha256_file(REVIEW)
    review_bytes = os.path.getsize(REVIEW)
    if review_now != proof["review_md_sha256_after"] or review_bytes != proof["review_md_bytes_after"]:
        print("FAIL proof file disagrees with review.md on disk")
        return 9

    row = {
        "path": "review.md",
        "sha256_before": proof["review_md_sha256_before"],
        "bytes_before": proof["review_md_bytes_before"],
        "sha256_after": review_now,
        "bytes_after": review_bytes,
        "changed": True,
        "note": "verdict block appended byte-exact (review.md is append-only)",
    }
    changes = summary["changes"]
    existing = [i for i, e in enumerate(changes) if e["path"] == "review.md"]
    if existing:
        print("review.md row already present (index %d); nothing to do" % existing[0])
        return 0
    changes.insert(0, row)
    summary["changes_backfill_note"] = (
        "recovery/bookkeeping_r3/finalize_summary_r3.py added the review.md row: the first run of "
        "transcribe_r3_verdict.py proved the append in evidence/%s/verdict_transcription_r3.json "
        "but omitted review.md from this table. The values come from that proof file (before) and "
        "from disk (after); no other row was touched." % CARD)
    with open(SUMMARY, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    print("backfilled review.md row: %s (%d B) -> %s (%d B)"
          % (row["sha256_before"], row["bytes_before"], row["sha256_after"], row["bytes_after"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
