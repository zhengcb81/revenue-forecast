"""Append a labelled revision to an oracle, append-only, with a hash proof.

Convention copied from SRC oracle.md §9 and its r2/r3/r4 proofs:
  new_bytes = old_bytes + b"\\n" + revision_bytes   (revision has NO trailing
  newline, so the marker sits at exactly pre_bytes + 1)

Usage:
  python append_revision.py <oracle.md> <revision.md> <proof.json out> \
      <expected pre bytes> <expected pre sha256>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# Prefix hashes frozen by SRC (reviewer_report.md §1.2) + the pre-r5 state
# pinned by B1-PREREQ freeze.json. Re-checked after EVERY append.
KNOWN_PREFIXES = {
    27697: "81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281",
    31081: "60ecbca7a008d60b8634bfed1cec56b801a86e6486f639c54e19cd257867f1d4",
    35840: "231e79768bd71ce95730ed10539d1e5865caa659c0dccf942bf7f2b99d8e3523",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    target = Path(sys.argv[1])
    rev_path = Path(sys.argv[2])
    proof_path = Path(sys.argv[3])
    pre_bytes = int(sys.argv[4])
    pre_sha = sys.argv[5]

    data = target.read_bytes()
    if len(data) != pre_bytes:
        raise SystemExit(f"PRE-BYTES MISMATCH: {len(data)} != {pre_bytes}")
    if sha256(data) != pre_sha:
        raise SystemExit(f"PRE-SHA MISMATCH: {sha256(data)} != {pre_sha}")

    rev = rev_path.read_bytes()
    if rev.endswith(b"\n") or rev.endswith(b"\r"):
        raise SystemExit("revision file must not end with a newline")
    marker = rev.split(b"\n", 1)[0]
    if not marker.startswith(b"## Revision r"):
        raise SystemExit(f"revision must start with '## Revision rN': {marker!r}")
    if marker in data:
        raise SystemExit(f"marker already present in target: {marker!r}")

    out = data + b"\n" + rev
    marker_offset = len(data) + 1
    structural_ok = (
        out[len(data) : len(data) + 1] == b"\n"
        and out[marker_offset : marker_offset + len(marker)] == marker
        and marker not in data
    )

    prefix_checks = {}
    for n, expected in {**KNOWN_PREFIXES, pre_bytes: pre_sha}.items():
        measured = sha256(out[:n])
        prefix_checks[str(n)] = {
            "expected": expected,
            "measured": measured,
            "match": measured == expected,
        }
    frozen_prefix_untouched = all(v["match"] for v in prefix_checks.values())
    proof = {
        "tool": "B1-PREREQ scratch/append_revision.py",
        "target": str(target),
        "revision_file": str(rev_path),
        "revision_heading": marker.decode("utf-8"),
        "pre_bytes": pre_bytes,
        "pre_sha256": pre_sha,
        "append_marker_offset": marker_offset,
        "marker_at_pre_plus_1": marker_offset == pre_bytes + 1,
        "structural_ok": structural_ok,
        "post_bytes": len(out),
        "post_sha256": sha256(out),
        "revision_bytes": len(rev),
        "revision_sha256": sha256(rev),
        "prefix_checks": prefix_checks,
        "frozen_prefix_untouched": frozen_prefix_untouched,
        "method": "pure suffix append: new = old + b'\\n' + revision (revision has no trailing newline)",
    }
    if not (structural_ok and frozen_prefix_untouched and marker_offset == pre_bytes + 1):
        # fail BEFORE touching the file
        raise SystemExit(f"PROOF WOULD FAIL, not appending: {json.dumps(proof)}")

    target.write_bytes(out)
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(json.dumps(proof, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
