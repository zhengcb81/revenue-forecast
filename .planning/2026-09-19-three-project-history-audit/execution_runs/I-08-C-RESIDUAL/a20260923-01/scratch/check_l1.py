"""I08CR-c1 — L1/F1 checks E-L1.1 + E-L1.2 against B1's oracle.md (read-only).

Byte-level prefix proofs r1-r4, revision markers r5/r6/r7, corrected 10-field text.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"
PLAN = ATT.parents[2]
ORACLE = PLAN / "execution_runs" / "B1-I08C-product-fixes" / "a20260921-01" / "oracle.md"

PREFIXES = {
    "r1_27697": (27697, "81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281"),
    "r1r2_31081": (31081, "60ecbca7a008d60b8634bfed1cec56b801a86e6486f639c54e19cd257867f1d4"),
    "r1r2r3_35840": (35840, "231e79768bd71ce95730ed10539d1e5865caa659c0dccf942bf7f2b99d8e3523"),
    "r1r2r3r4_39287": (39287, "fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae"),
}
MARKERS = {  # frozen expectations (oracle 3.1 E-L1.1), 0-based byte offsets
    "## Revision r5": 39288,
    "## Revision r6": 43299,
    "## Revision r7": 47539,
}
TOTAL_BYTES = 57911
FULL_SHA_PREFIX = "6e344a20"

TEXT_CHECKS = {  # frozen expectation E-L1.2 (text-level presence in the r5+ region)
    "states_10_fields": b"10 fields",
    "sentinel_rule": b"SIGNED_RESULT_SHA256_SENTINEL",
    "result_sha256_not_record_field": b"not** a record field",
    "receipt_sha256_fixpoint": b"receipt_sha256",
    "request_carried": b"request",
}


def main() -> int:
    data = ORACLE.read_bytes()
    out = {
        "target": str(ORACLE),
        "total_bytes": len(data),
        "total_bytes_expected": TOTAL_BYTES,
        "total_bytes_match": len(data) == TOTAL_BYTES,
        "full_sha256": hashlib.sha256(data).hexdigest(),
    }
    out["full_sha256_starts_with_expected"] = out["full_sha256"].startswith(FULL_SHA_PREFIX)
    out["prefixes"] = {}
    for name, (n, want) in PREFIXES.items():
        got = hashlib.sha256(data[:n]).hexdigest()
        out["prefixes"][name] = {"bytes": n, "expected": want, "measured": got, "match": got == want}
    out["markers"] = {}
    for text, want in MARKERS.items():
        b = text.encode()
        first = data.find(b)
        out["markers"][text] = {
            "expected_offset": want,
            "first_offset": first,
            "count": data.count(b),
            "match": first == want and data.count(b) == 1,
        }
    out["extra_markers_report_only"] = {
        t: {"first_offset": data.find(t.encode()), "count": data.count(t.encode())}
        for t in ("## Revision r2", "## Revision r3", "## Revision r4")
    }
    region = data[39288:]
    out["r5_plus_region_bytes"] = len(region)
    out["text_checks"] = {
        k: {"needle": v.decode(), "present": v in region} for k, v in TEXT_CHECKS.items()
    }
    (EVID / "E_L1_r5_region_dump.txt").write_bytes(region)
    (EVID / "E_L1_checks.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    ok = (
        out["total_bytes_match"]
        and out["full_sha256_starts_with_expected"]
        and all(v["match"] for v in out["prefixes"].values())
        and all(v["match"] for v in out["markers"].values())
        and all(v["present"] for v in out["text_checks"].values())
    )
    print(json.dumps(out, indent=1))
    print("L1_E-L1.1_E-L1.2_ALL_OK:", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
