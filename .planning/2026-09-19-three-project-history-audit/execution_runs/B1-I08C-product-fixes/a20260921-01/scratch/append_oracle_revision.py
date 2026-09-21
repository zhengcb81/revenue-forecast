"""Append-only oracle revision r2 with a byte-level proof of append-only-ness.

Locates the append marker and hashes the fixed prefix; never uses
total-length-minus-append-length arithmetic.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ORACLE = Path(sys.argv[1]).resolve()
REVISION = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()

before = ORACLE.read_bytes()
pre_sha = hashlib.sha256(before).hexdigest()
had_trailing_newline = before.endswith(b"\n")

appended = REVISION.read_bytes()
if not appended.endswith(b"\n"):
    appended += b"\n"

with ORACLE.open("ab") as handle:
    if not had_trailing_newline:
        handle.write(b"\n")
    handle.write(appended)

after = ORACLE.read_bytes()
marker = appended.split(b"\n", 1)[0]
offset = after.index(marker)
prefix = after[:offset]
suffix = after[offset:]

proof = {
    "method": "locate the append marker and hash the fixed prefix",
    "oracle_bytes_before": len(before),
    "oracle_sha256_before": pre_sha,
    "had_trailing_newline": had_trailing_newline,
    "normalising_bytes_inserted": 0 if had_trailing_newline else 1,
    "append_marker": marker.decode("utf-8"),
    "append_marker_offset": offset,
    "frozen_body_bytes_on_disk_now": len(prefix),
    "frozen_body_sha256_on_disk_now": hashlib.sha256(prefix).hexdigest(),
    "frozen_body_untouched": hashlib.sha256(prefix).hexdigest() == pre_sha,
    "append_region_bytes": len(suffix),
    "append_region_sha256": hashlib.sha256(suffix).hexdigest(),
    "oracle_bytes_after": len(after),
    "oracle_sha256_after": hashlib.sha256(after).hexdigest(),
}
OUT.write_text(json.dumps(proof, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(proof, indent=1, sort_keys=True))
