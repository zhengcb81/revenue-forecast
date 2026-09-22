"""Apply mutation M6 to ONE target file (attempt-local scratch only).

M6 (frozen verbatim in this attempt's oracle.md §3.2, matching the reviewer's
M6): after the closed-set/structural checks in ``validate_publication_attestation``,
short-circuit whenever the label is not ``host_signed``, so a present-but-invalid
record becomes ignorable under an ``unattested`` label.

Safety rails:
* asserts the target's PRE-hash equals the pinned fixed-tree hash
  (``bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0``),
  so the patch can only ever be applied to a fresh copy of B1's fixed file;
* asserts the anchor occurs exactly once and that the next statement after the
  insertion point is the ``require(record["payload_sha256"]...)`` check;
* writes a JSON proof (pre-hash, post-hash, mutation-line hash, anchor).

Usage: python apply_m6.py <target revenue_publication.py> <proof.json out>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

PRE_SHA256 = "bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0"
ANCHOR = b"so any change to a bound value breaks the signature."
NEXT_STMT = b'    require(\n        record["payload_sha256"]'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    target = Path(sys.argv[1])
    proof_path = Path(sys.argv[2])
    data = target.read_bytes()
    pre = sha256(data)
    if pre != PRE_SHA256:
        raise SystemExit(f"PRE-HASH MISMATCH: {pre} != {PRE_SHA256} (refusing to patch)")
    if data.count(ANCHOR) != 1:
        raise SystemExit(f"anchor count {data.count(ANCHOR)} != 1 (refusing to patch)")
    nl = b"\r\n" if b"\r\n" in data else b"\n"
    i = data.index(ANCHOR)
    j = data.index(nl, i) + len(nl)
    if NEXT_STMT.replace(b"\n", nl) not in data[j : j + len(NEXT_STMT) + 4]:
        raise SystemExit(f"unexpected statement after anchor: {data[j:j+60]!r}")
    mutation_lines = [
        b"    if not claims_signed:",
        b"        # MUTATION M6: only a labelled claim is held to its record.",
        b"        return",
    ]
    mutation = nl.join(mutation_lines) + nl
    out = data[:j] + mutation + data[j:]
    target.write_bytes(out)
    proof = {
        "mutation": "M6",
        "target": str(target),
        "pre_sha256": pre,
        "pre_expected": PRE_SHA256,
        "pre_match": pre == PRE_SHA256,
        "anchor_ascii": ANCHOR.decode("ascii"),
        "anchor_count": data.count(ANCHOR),
        "inserted_lines": [ln.decode("ascii") for ln in mutation_lines],
        "inserted_bytes_sha256": sha256(mutation),
        "newline_style": "CRLF" if nl == b"\r\n" else "LF",
        "post_sha256": sha256(out),
        "post_bytes": len(out),
        "pre_bytes": len(data),
    }
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(json.dumps(proof, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
