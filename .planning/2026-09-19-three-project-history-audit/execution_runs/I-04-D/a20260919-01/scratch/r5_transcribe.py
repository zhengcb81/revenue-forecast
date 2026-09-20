"""r5: freeze the reviewer report, identify the paste-ready block BY CONTENT, transcribe it.

Strict conditions from the reviewer:
  * the block is identified by content, never by a section number (the two messages
    disagreed about the number);
  * transcription happens ONLY if review.md is still 37191 B / 81516b2a...;
  * after appending, the previous bytes must be an EXACT BYTE PREFIX of the new file.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

A = pathlib.Path(__file__).resolve().parents[1]
REP_SRC = pathlib.Path(os.environ["TEMP"]) / "i04d-review-20260920-045256" / "I04D-REVIEW-R4-FINAL-VERDICT.md"
REVIEW = A / "review.md"
FENCE = "```"

EXPECTED_REVIEW_SHA = "81516b2ac06a41dca5978e744b540f8b2f33d7ba28297e7c792c32f9c50fcf09"
EXPECTED_REVIEW_BYTES = 37191

# ---------------------------------------------------------------- 1. freeze the report
rep_bytes = REP_SRC.read_bytes()
rep_sha = hashlib.sha256(rep_bytes).hexdigest()
dest_dir = A / "evidence" / "I-04-D"
dest_dir.mkdir(parents=True, exist_ok=True)
rep_dest = dest_dir / "reviewer_report_r4.md"
rep_dest.write_bytes(rep_bytes)
print(f"report frozen : {rep_dest}")
print(f"  source      : {REP_SRC}  {len(rep_bytes)} B  {rep_sha}")
print(f"  readback    : {len(rep_dest.read_bytes())} B  {hashlib.sha256(rep_dest.read_bytes()).hexdigest()}")
print(f"  identical   : {rep_dest.read_bytes() == rep_bytes}")

# ---------------------------------------------------------------- 2. identify BY CONTENT
text = rep_bytes.decode("utf-8", errors="replace")
lines = text.splitlines()
REQUIRED = [
    "accepted_scoped",
    "reviewed_revision",
    "37191",
    "81516b2a",
    "fd163a27",
    "27f492b1",
    "2026-09-20T04:31:21Z",
    "05:34:15",
    "08:23:08",
    "未授予",
    "第一份 reviewer 裁决",
]
candidates = []
for start in range(len(lines)):
    if lines[start].strip() != FENCE + "markdown":
        continue
    for end in range(start + 1, len(lines)):
        if lines[end].strip() == FENCE:
            body = "\n".join(lines[start + 1 : end])
            candidates.append((start + 1, end + 1, body))
            break

print("\ncandidate fenced markdown blocks:", len(candidates))
qualified = []
for start, end, body in candidates:
    missing = [r for r in REQUIRED if r not in body]
    print(f"  lines {start}..{end}  missing={missing}")
    if not missing:
        qualified.append((start, end, body))

if len(qualified) != 1:
    print(f"\nSTOP: expected exactly one fully-qualified block, found {len(qualified)}")
    print("all headings in the report:")
    for n, line in enumerate(lines, 1):
        if line.startswith("#"):
            print(f"  {n}: {line[:120]}")
    sys.exit(2)

start, end, block_body = qualified[0]
print(f"\nUNIQUE block identified by content: report lines {start}..{end}")
print("first line :", block_body.splitlines()[0][:120])
print("last line  :", block_body.splitlines()[-1][:120])

# ---------------------------------------------------------------- 3. precondition
review_bytes = REVIEW.read_bytes()
review_sha = hashlib.sha256(review_bytes).hexdigest()
print(f"\nreview.md    : {len(review_bytes)} B  {review_sha}")
if len(review_bytes) != EXPECTED_REVIEW_BYTES or review_sha != EXPECTED_REVIEW_SHA:
    print("STOP: review.md no longer matches the transcription precondition; NOT appending")
    (A / "after" / "r4_verdict_transcription.json").write_text(
        json.dumps(
            {
                "appended": False,
                "reason": "review.md precondition failed",
                "expected": {"bytes": EXPECTED_REVIEW_BYTES, "sha256": EXPECTED_REVIEW_SHA},
                "actual": {"bytes": len(review_bytes), "sha256": review_sha},
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    sys.exit(3)

# ---------------------------------------------------------------- 4. append as BYTES
separator = b"\n\n"
block_bytes = block_body.encode("utf-8")
new_bytes = review_bytes + separator + block_bytes + b"\n"
REVIEW.write_bytes(new_bytes)
new_sha = hashlib.sha256(new_bytes).hexdigest()
prefix_ok = new_bytes[: len(review_bytes)] == review_bytes
print(f"\nreview.md    : {len(new_bytes)} B  {new_sha}")
print(f"  byte-prefix proof (old bytes are an exact prefix of the new file): {prefix_ok}")

proof = {
    "appended": True,
    "transcription_kind": "reviewer verdict transcribed by the implementer; NOT a self-signature",
    "block_identified_by": "content match on 11 required markers (the two reviewer messages disagreed on the section number)",
    "report_copy": {
        "path": "evidence/I-04-D/reviewer_report_r4.md",
        "source_path": str(REP_SRC),
        "bytes": len(rep_bytes),
        "sha256": rep_sha,
        "readback_identical": rep_dest.read_bytes() == rep_bytes,
    },
    "block_source_lines": {"first": start, "last": end},
    "review_md": {
        "bytes_before": len(review_bytes),
        "sha256_before": review_sha,
        "bytes_after": len(new_bytes),
        "sha256_after": new_sha,
        "appended_bytes": len(new_bytes) - len(review_bytes),
        "old_bytes_are_exact_prefix": prefix_ok,
    },
}
(A / "after" / "r4_verdict_transcription.json").write_text(
    json.dumps(proof, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8"
)
print("proof written: after/r4_verdict_transcription.json")
