"""Repair the r2 boundary of oracle.md: drop the separating newline so the boundary is exact.

Why this exists (recorded, not hidden): the first r2 append inserted one separating "\\n" before
the boundary marker, which made the marker line start at ``len(frozen body) + 1`` while the
recorded frozen-body hash was taken over the frozen body alone. That is an off-by-one in the
BOUNDARY BOOKKEEPING, not a change of the frozen text: removing that one byte makes
``sha256(oracle.md bytes before the marker)`` equal the single recorded pre-append hash again.

The script
  1  asserts the bytes before the separator still hash to the recorded frozen-body value,
  2  removes exactly that one separator byte (nothing else),
  3  re-asserts the prefix hash and rewrites the boundary metadata in revision_r2.json,
  4  adds an R2-06 item documenting the repair.

No expectation, tolerance, case or refusal condition is touched; the frozen body is byte-equal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

MARKER = "<!-- R2-APPEND-BOUNDARY: everything above this line is the frozen oracle body (v1) -->"
R2_HEADING = "## 修订 r2"


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt)
    evidence = os.path.join(attempt, "evidence", args.card)
    oracle_md = os.path.join(attempt, "oracle.md")
    v1 = json.load(open(os.path.join(attempt, "before", "oracle_md_v1.json"), "r",
                        encoding="utf-8"))
    payload = open(oracle_md, "rb").read()
    marker_pos = payload.find(MARKER.encode("utf-8"))
    if marker_pos < 0:
        print("no boundary marker found: nothing to repair")
        return 12
    separator_pos = marker_pos - 1
    prefix = payload[:separator_pos]
    if sha256_bytes(prefix) != v1["sha256"]:
        print("bytes before the separator do NOT hash to the recorded frozen body: refusing to "
              "rewrite anything")
        return 13
    if payload[separator_pos:separator_pos + 1] != b"\n":
        print("the byte before the marker is not the expected separator newline: refusing")
        return 14

    repaired = payload[:separator_pos] + payload[marker_pos:]
    new_offset = repaired.find(MARKER.encode("utf-8"))
    if sha256_bytes(repaired[:new_offset]) != v1["sha256"]:
        print("repair would not reproduce the frozen body hash: refusing to write")
        return 15
    with open(oracle_md, "wb") as handle:
        handle.write(repaired)
    os.makedirs(os.path.join(attempt, "recovery"), exist_ok=True)
    open(os.path.join(attempt, "recovery", "oracle_md_before_boundary_repair.bin"),
         "wb").write(payload)

    text = repaired.decode("utf-8")
    revision_path = os.path.join(evidence, "revision_r2.json")
    revision = json.load(open(revision_path, "r", encoding="utf-8"))
    revision["boundary"]["byte_offset"] = new_offset
    revision["boundary"]["sha256_of_bytes_before_the_marker"] = sha256_bytes(repaired[:new_offset])
    revision["boundary"]["reproduces_the_recorded_frozen_body_hash"] = True
    revision["boundary"]["marker_occurrences_in_oracle_md"] = text.count(MARKER)
    revision["boundary"]["r2_heading_occurrences_in_oracle_md"] = text.count(R2_HEADING)
    revision["boundary"]["oracle_md_sha256_after_append"] = sha256_bytes(repaired)
    revision["boundary"]["oracle_md_bytes_after_append"] = len(repaired)
    revision["items"]["R2-06"] = (
        "boundary bookkeeping repaired: the first append inserted one separating newline before "
        "the marker, so the marker line started one byte after the frozen body boundary. That "
        "single byte was removed (scripts/repair_r2_boundary.py); the frozen body is byte-equal "
        "(prefix sha256 re-verified against before/oracle_md_v1.json before and after the "
        "repair). No expectation, tolerance, case or refusal condition changed.")
    with open(revision_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(revision, handle, ensure_ascii=False, indent=1)
        handle.write("\n")

    print("separator byte removed at offset %d; new boundary offset %d" % (separator_pos, new_offset))
    print("prefix sha256 = %s (recorded = %s)" % (sha256_bytes(repaired[:new_offset]), v1["sha256"]))
    print("marker occurrences=%d r2 heading occurrences=%d" % (text.count(MARKER),
                                                               text.count(R2_HEADING)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
