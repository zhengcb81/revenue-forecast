"""Append-only prefix proof for oracle.md revision r4 (fix round I-08-C-REFREEZE).

Method: hash the FIXED byte prefixes directly (never total-length arithmetic).
  prefix A = bytes[0:22335]  -> must equal the pre-append sha256 recorded in
                                 oracle.md R4-8 BEFORE the r4 text was appended
  prefix B = bytes[0:6831]   -> must equal the r1/r2 frozen-body sha256
                                 (unchanged since r3; re-checked here)

Run:  C:\\Miniconda\\python.exe -B scratch\\fixround\\prefix_proof.py
Exit: 0 iff both prefixes match, 1 otherwise. JSON on stdout.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ORACLE = Path(__file__).resolve().parents[2] / "oracle.md"

PRE_APPEND_BYTES = 22335
PRE_APPEND_SHA256 = "94a853e978e34f522820cc2e03548fffe8ee2e599725d7a0131f872c93add8b3"
R2_BODY_BYTES = 6831
R2_BODY_SHA256 = "478bd70e0a1dfbfb924ebec0175bb2bdcdd199880de1c554de099d8ac8723c90"


def main() -> int:
    data = ORACLE.read_bytes()
    prefix_a = hashlib.sha256(data[:PRE_APPEND_BYTES]).hexdigest()
    prefix_b = hashlib.sha256(data[:R2_BODY_BYTES]).hexdigest()
    result = {
        "method": "sha256 over fixed byte-length prefixes (no length arithmetic)",
        "current_bytes": len(data),
        "current_sha256": hashlib.sha256(data).hexdigest(),
        "pre_append_bytes": PRE_APPEND_BYTES,
        "pre_append_sha256_recorded_before_append": PRE_APPEND_SHA256,
        "pre_append_prefix_sha256_now": prefix_a,
        "pre_append_prefix_match": prefix_a == PRE_APPEND_SHA256,
        "r2_frozen_body_bytes": R2_BODY_BYTES,
        "r2_frozen_body_sha256_recorded": R2_BODY_SHA256,
        "r2_frozen_body_prefix_sha256_now": prefix_b,
        "r2_frozen_body_match": prefix_b == R2_BODY_SHA256,
        "append_region_starts_at_offset": PRE_APPEND_BYTES,
    }
    result["append_only_proof"] = bool(
        result["pre_append_prefix_match"] and result["r2_frozen_body_match"]
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["append_only_proof"] else 1


if __name__ == "__main__":
    sys.exit(main())
