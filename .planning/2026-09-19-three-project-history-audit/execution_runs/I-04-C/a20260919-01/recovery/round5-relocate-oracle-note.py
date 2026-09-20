"""One-off placement fix for the oracle.md E1 note (round 5).

Why: the note was inserted right after the line that CONTAINS the stale numbers,
which is the middle of a three-line bullet in oracle.md R3-2 -- so it split the
bullet.  This script removes that insertion (verifying that oracle.md then equals
the round5-pre snapshot byte-for-byte, i.e. the removal is exact), after which
sim/patch_r5_docs.py (with the corrected anchor, at the end of the bullet) is run
again to re-insert the same correction in the right place.

Idempotent: stops if the note is not present (already relocated).

Run:  & $PY -B recovery/round5-relocate-oracle-note.py
"""

from __future__ import annotations

import hashlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPT = os.path.dirname(HERE)
if os.path.join(ATTEMPT, "sim") not in sys.path:
    sys.path.insert(0, os.path.join(ATTEMPT, "sim"))

import patch_r5_docs as r5  # noqa: E402

ORACLE = os.path.join(ATTEMPT, "oracle.md")
SNAPSHOT = os.path.join(HERE, "round5-pre-hashes.txt")
EXPECTED = "3594f4d6cbf9b9b20b00c317451a8f8ad2cffe5df4d58664c782a840610a4390"


def main():
    with io.open(ORACLE, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    if r5.MARK_O1 not in text:
        print("SKIP: the E1 note is not present (already relocated or never applied)")
        return 0

    lines = text.split(r5.CRLF)
    hits = [i for i, line in enumerate(lines) if r5.MARK_O1 in line]
    if len(hits) != 1:
        print("FAIL: marker found %d times" % len(hits))
        return 1
    index = hits[0]
    window = lines[index - 1:index + len(r5.BLOCK_O1)]
    if window != [""] + r5.BLOCK_O1:
        print("FAIL: the inserted note is not contiguous/verbatim at line %d" % (index + 1))
        return 1
    del lines[index - 1:index + len(r5.BLOCK_O1)]
    restored = r5.CRLF.join(lines)

    digest = hashlib.sha256(restored.encode("utf-8")).hexdigest()
    if digest != EXPECTED:
        print("FAIL: after removal oracle.md hashes to %s, expected %s" % (digest, EXPECTED))
        return 1
    with io.open(ORACLE, "w", encoding="utf-8", newline="") as handle:
        handle.write(restored)
    print("removed the misplaced note at line %d" % (index + 1))
    print("oracle.md is back to the round5-pre / r3 bytes: %s" % digest)
    print("now re-run sim/patch_r5_docs.py to insert the note at the end of the bullet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
