"""Generic append-only revision applier with a byte-level proof.

Appends a revision file to a frozen document and proves that the previously
frozen byte prefix is untouched by hashing exactly those bytes.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

DOC = Path(sys.argv[1]).resolve()
REVISION = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
PRE_SHA = sys.argv[4]
PRE_BYTES = int(sys.argv[5])

before = DOC.read_bytes()
had_trailing_newline = before.endswith(b"\n")
if len(before) != PRE_BYTES:
    raise SystemExit(
        f"frozen length mismatch before append: {len(before)} != {PRE_BYTES}"
    )

appended = REVISION.read_bytes()
if not appended.endswith(b"\n"):
    appended += b"\n"

with DOC.open("ab") as handle:
    if not had_trailing_newline:
        handle.write(b"\n")
    handle.write(appended)

after = DOC.read_bytes()
if not after.startswith(before):
    raise SystemExit("APPEND-ONLY PROOF FAILED: document is not a prefix-extension")

marker = next(line for line in appended.split(b"\n") if line.strip())
offset = after.index(marker)
prefix = after[:PRE_BYTES]

proof = {
    "method": "hash exactly the previously frozen byte prefix; never "
    "total-length-minus-append-length arithmetic",
    "pre_append_bytes": PRE_BYTES,
    "pre_append_sha256_expected": PRE_SHA,
    "document_is_prefix_extension": True,
    "frozen_prefix_bytes_on_disk_now": len(prefix),
    "frozen_prefix_sha256_on_disk_now": hashlib.sha256(prefix).hexdigest(),
    "frozen_prefix_untouched": hashlib.sha256(prefix).hexdigest() == PRE_SHA,
    "append_marker": marker.decode("utf-8"),
    "append_marker_offset": offset,
    "separating_whitespace_bytes": len(after[PRE_BYTES:offset]),
    "append_region_bytes": len(after) - PRE_BYTES,
    "append_region_sha256": hashlib.sha256(after[PRE_BYTES:]).hexdigest(),
    "document_bytes_after": len(after),
    "document_sha256_after": hashlib.sha256(after).hexdigest(),
}
OUT.write_text(json.dumps(proof, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(proof, indent=1, sort_keys=True))
if not proof["frozen_prefix_untouched"]:
    raise SystemExit("APPEND-ONLY PROOF FAILED")
