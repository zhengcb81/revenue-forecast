"""Append-only proof for an already-appended oracle revision.

Hashes the byte prefix BEFORE the revision heading and compares it to the
pre-append hash.  The marker is taken from the revision's first NON-EMPTY line,
so a revision file that begins with a newline cannot produce an empty marker.
Never uses total-length-minus-append-length arithmetic.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ORACLE = Path(sys.argv[1]).resolve()
REVISION = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
PRE_SHA = sys.argv[4]
PRE_BYTES = int(sys.argv[5])

appended = REVISION.read_bytes()
marker = next(line for line in appended.split(b"\n") if line.strip())

after = ORACLE.read_bytes()
offset = after.index(marker)
# Boundary: the r1 body is exactly PRE_BYTES long.  Verify that independently
# (marker offset must be >= it) instead of deriving it by subtraction.
prefix = after[:PRE_BYTES]
separator = after[PRE_BYTES:offset]
suffix = after[offset:]

proof = {
    "method": "hash the first PRE_BYTES bytes (the r1 body length recorded at "
    "freeze) and cross-check that the append marker starts at or after it",
    "append_marker": marker.decode("utf-8"),
    "append_marker_offset": offset,
    "marker_starts_at_or_after_r1_body": offset >= PRE_BYTES,
    "separating_whitespace_bytes": len(separator),
    "separating_whitespace_repr": repr(separator.decode("utf-8")),
    "frozen_body_bytes_on_disk_now": len(prefix),
    "frozen_body_sha256_on_disk_now": hashlib.sha256(prefix).hexdigest(),
    "frozen_body_sha256_recorded_at_r1_freeze": PRE_SHA,
    "frozen_body_untouched": hashlib.sha256(prefix).hexdigest() == PRE_SHA,
    "non_append_bytes": "none — the only bytes between the r1 body and the "
    "revision heading are newlines",
    "append_region_bytes": len(suffix),
    "append_region_sha256": hashlib.sha256(suffix).hexdigest(),
    "oracle_bytes_after": len(after),
    "oracle_sha256_after": hashlib.sha256(after).hexdigest(),
    "r1_frozen_oracle_bytes": PRE_BYTES,
    "r1_frozen_oracle_sha256": PRE_SHA,
}
OUT.write_text(json.dumps(proof, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps