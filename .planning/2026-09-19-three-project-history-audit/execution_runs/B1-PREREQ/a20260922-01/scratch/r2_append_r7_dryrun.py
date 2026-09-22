"""Dry-run the SRC oracle r7 append WITHOUT writing: compute the exact proof
(marker offset, prefix checks, structural checks) and print it. The actual
append is performed afterwards by scratch/append_revision.py, which re-runs
the same checks and refuses to write if any fail.

Usage: python r2_append_r7_dryrun.py <oracle.md> <revision.md> <json out>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# Prefixes as re-measured by the independent reviewer (report 4.1) and pinned
# by SRC §1.2 / this card's append proofs. Checked against the POST-append bytes.
KNOWN_PREFIXES = {
    27697: "81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281",
    31081: "60ecbca7a008d60b8634bfed1cec56b801a86e6486f639c54e19cd257867f1d4",
    35840: "231e79768bd71ce95730ed10539d1e5865caa659c0dccf942bf7f2b99d8e3523",
    39287: "fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae",
    43298: "910ca4a8109b28afb739f4a7463dbf26e13fe85c296e115d806768bcb3bd3231",
    47538: "a8f192f10215642d7df2d8ace240d074f3bf50671cd4f51920b35434ebcf972d",
}
PRE_BYTES = 47538
PRE_SHA = "a8f192f10215642d7df2d8ace240d074f3bf50671cd4f51920b35434ebcf972d"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    target, rev_path, out_path = map(Path, sys.argv[1:4])
    data = target.read_bytes()
    rev = rev_path.read_bytes()

    assert len(data) == PRE_BYTES, f"PRE-BYTES MISMATCH: {len(data)} != {PRE_BYTES}"
    assert sha256(data) == PRE_SHA, f"PRE-SHA MISMATCH: {sha256(data)} != {PRE_SHA}"
    assert not rev.endswith((b"\n", b"\r")), "revision must not end with a newline"

    marker = rev.split(b"\n", 1)[0]
    assert marker.startswith(b"## Revision r7"), marker

    # what the bytes WOULD be
    out = data + b"\n" + rev
    marker_offset = len(data) + 1
    structural_ok = (
        out[len(data): len(data) + 1] == b"\n"
        and out[marker_offset: marker_offset + len(marker)] == marker
        and marker not in data
    )
    prefix_checks = {
        str(n): {
            "expected": h,
            "measured": sha256(out[:n]),
            "match": sha256(out[:n]) == h,
        }
        for n, h in KNOWN_PREFIXES.items()
    }
    proof = {
        "tool": "B1-PREREQ scratch/r2_append_r7_dryrun.py (DRY RUN — no write)",
        "target": str(target),
        "revision_file": str(rev_path),
        "revision_heading": marker.decode("utf-8"),
        "revision_bytes": len(rev),
        "revision_sha256": sha256(rev),
        "pre_bytes": len(data),
        "pre_sha256": sha256(data),
        "would_be_post_bytes": len(out),
        "would_be_post_sha256": sha256(out),
        "append_marker_offset": marker_offset,
        "marker_at_pre_plus_1": marker_offset == PRE_BYTES + 1,
        "marker_absent_from_pre_bytes": marker not in data,
        "bare_heading_prefix_count_post_append": (
            data + b"\n" + rev
        ).count(b"## Revision r7"),
        "structural_ok": structural_ok,
        "prefix_checks": prefix_checks,
        "frozen_prefix_untouched": all(v["match"] for v in prefix_checks.values()),
        "file_written": False,
    }
    ok = (
        structural_ok
        and proof["marker_at_pre_plus_1"]
        and proof["frozen_prefix_untouched"]
        and proof["bare_heading_prefix_count_post_append"] == 1
    )
    proof["dry_run_would_pass"] = ok
    out_path.write_text(json.dumps(proof, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
