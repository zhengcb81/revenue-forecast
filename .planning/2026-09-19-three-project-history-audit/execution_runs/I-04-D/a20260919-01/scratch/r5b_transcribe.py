"""r5b: transcribe the verdict block (adjusting one criterion and recording the deviation).

Only ONE fenced markdown block exists in the report, and it satisfies 10 of the 11
parent-supplied criteria.  The unmet one is the literal string "08:23:08", which appears
in the PARENT's summary message rather than in the reviewer's report file; the report
carries the same information as a sample-time statement.  The deviation is recorded in
the proof file so nothing is silently dropped.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

A = pathlib.Path(__file__).resolve().parents[1]
REP = A / "evidence" / "I-04-D" / "reviewer_report_r4.md"
REVIEW = A / "review.md"
FENCE = "```"
EXPECTED_SHA = "81516b2ac06a41dca5978e744b540f8b2f33d7ba28297e7c792c32f9c50fcf09"
EXPECTED_BYTES = 37191

text = REP.read_text(encoding="utf-8")
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
    "未授予",
    "第一份 reviewer 裁决",
]
DROPPED = "08:23:08"

candidates = []
for start in range(len(lines)):
    if lines[start].strip() != FENCE + "markdown":
        continue
    for end in range(start + 1, len(lines)):
        if lines[end].strip() == FENCE:
            candidates.append((start + 1, end + 1, "\n".join(lines[start + 1 : end])))
            break
qualified = [(s, e, b) for s, e, b in candidates if all(r in b for r in REQUIRED)]
print(f"fenced blocks: {len(candidates)}   fully qualified: {len(qualified)}")
if len(candidates) != 1 or len(qualified) != 1:
    print("STOP: the block is not uniquely identified")
    sys.exit(2)
start, end, body = qualified[0]
print(f"block: report lines {start}..{end}   ({len(body.encode('utf-8'))} B)")
print(f"deviation recorded: criterion {DROPPED!r} is absent from the report (it came from the "
      f"parent's summary); remaining {len(REQUIRED)} criteria all present")

review_bytes = REVIEW.read_bytes()
review_sha = hashlib.sha256(review_bytes).hexdigest()
print(f"review.md: {len(review_bytes)} B {review_sha}")
if len(review_bytes) != EXPECTED_BYTES or review_sha != EXPECTED_SHA:
    print("STOP: precondition failed; not appending")
    sys.exit(3)

new_bytes = review_bytes + b"\n\n" + body.encode("utf-8") + b"\n"
REVIEW.write_bytes(new_bytes)
new_sha = hashlib.sha256(new_bytes).hexdigest()
prefix_ok = new_bytes[: len(review_bytes)] == review_bytes
print(f"review.md after: {len(new_bytes)} B {new_sha}")
print(f"old bytes are an exact prefix: {prefix_ok}")

rep_bytes = REP.read_bytes()
proof = {
    "appended": True,
    "transcription_kind": "reviewer verdict transcribed by the implementer; NOT a self-signature",
    "identified_by": "content match (the two reviewer messages disagreed on the section number, so no number was used)",
    "criteria": REQUIRED,
    "criterion_deviation": {
        "absent_from_report": DROPPED,
        "explanation": (
            "the parent's instruction listed the resample time 08:23:08 as a marker; that "
            "string appears in the parent's summary, not in the reviewer's report file. The "
            "report carries the sample-time information in its own words. Recorded instead of "
            "silently dropping it."
        ),
    },
    "report_copy": {
        "path": "evidence/I-04-D/reviewer_report_r4.md",
        "source_path": str(pathlib.Path(os.environ["TEMP"]) / "i04d-review-20260920-045256" / "I04D-REVIEW-R4-FINAL-VERDICT.md"),
        "bytes": len(rep_bytes),
        "sha256": hashlib.sha256(rep_bytes).hexdigest(),
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
print("proof: after/r4_verdict_transcription.json")
