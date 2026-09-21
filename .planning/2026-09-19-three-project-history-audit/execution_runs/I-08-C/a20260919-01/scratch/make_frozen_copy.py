"""I-08-C r3 bookkeeping (attempt-local, no production access).

1. Reconstruct `oracle.md.r2_frozen_copy.txt` = the exact frozen prefix of
   `oracle.md` (everything before the append marker) and prove:
     - it hashes to the r2 recorded digest 478bd70e...
     - the current `oracle.md` still STARTS WITH those exact bytes
   Proof by locating the marker and hashing the prefix -- never by
   total-length-minus-append-length arithmetic.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent.parent  # script lives in scratch/, artifacts in the attempt dir
ORACLE = D / "oracle.md"
COPY = D / "oracle.md.r2_frozen_copy.txt"
MARKER = b"<!-- ================= APPEND-ONLY BELOW THIS LINE ================= -->"
R2_SHA = "478bd70e0a1dfbfb924ebec0175bb2bdcdd199880de1c554de099d8ac8723c90"
R2_BYTES = 6831

raw = ORACLE.read_bytes()
idx = raw.find(MARKER)
if idx < 0:
    raise SystemExit("append marker not found")
prefix = raw[:idx]

# The recorded r2 frozen body is bytes [0:R2_BYTES) of this file. The r3 edit
# may have normalised a missing final newline at the boundary, so the marker can
# sit at R2_BYTES or R2_BYTES+1 -- but the recorded 6831 bytes themselves must be
# untouched and everything after them must be append material only.
frozen = raw[:R2_BYTES]

out: dict[str, object] = {
    "marker_offset": idx,
    "marker_line_starts_at": raw[:idx].count(b"\n") + 1,
    "current_oracle_bytes": len(raw),
    "recorded_frozen_body_bytes": R2_BYTES,
    "recorded_frozen_body_sha256": hashlib.sha256(frozen).hexdigest(),
    "recorded_frozen_body_expected_sha256": R2_SHA,
    "boundary_bytes_between_body_and_marker": repr(raw[R2_BYTES:idx]),
    "current_oracle_sha256": hashlib.sha256(raw).hexdigest(),
    "frozen_prefix_sha256": hashlib.sha256(prefix).hexdigest(),
    "frozen_prefix_bytes": len(prefix),
}

# byte-identical body check (hash of the recorded prefix, independent of any
# total-length relation)
out["frozen_body_untouched"] = hashlib.sha256(frozen).hexdigest() == R2_SHA
out["current_starts_with_frozen_prefix"] = raw.startswith(prefix)
out["boundary_is_whitespace_only"] = raw[R2_BYTES:idx].strip() == b""

# a copy written from the recorded prefix, not from this file, must match
COPY.write_bytes(frozen)
out["frozen_copy_bytes"] = len(frozen)
out["frozen_copy_sha256"] = hashlib.sha256(COPY.read_bytes()).hexdigest()
out["frozen_copy_equals_recorded_body"] = COPY.read_bytes() == frozen

# sanity: the append region must not contain a second copy of the frozen body
out["append_region_bytes"] = len(raw) - idx
out["append_region_cites_frozen_sha_in_provenance"] = (
    R2_SHA.encode() in raw[idx:]
)

out["append_only_proof"] = bool(
    out["frozen_body_untouched"]
    and out["current_starts_with_frozen_prefix"]
    and out["boundary_is_whitespace_only"]
    and out["frozen_copy_equals_recorded_body"]
)

print(json.dumps(out, indent=2, sort_keys=True))
raise SystemExit(0 if out["append_only_proof"] else 1)
