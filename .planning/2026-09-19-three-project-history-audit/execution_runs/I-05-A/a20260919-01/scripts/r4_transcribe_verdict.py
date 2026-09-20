"""Step 2: transcribe the reviewer verdict block into review.md (byte-exact append).

Guarantees recorded:
  * the pre-append review.md bytes are the EXACT prefix of the post-append file
    (byte comparison, no normalisation);
  * before/after sha256 and byte counts;
  * the appended block is byte-identical to the block extracted from the frozen
    report copy.

Usage: <py> -X utf8 -B scripts/r4_transcribe_verdict.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

CARD = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-05-A\a20260919-01"
)
REPORT = CARD / "evidence" / "I-05-A" / "reviewer_report_r4.md"
REVIEW = CARD / "review.md"
BLOCK_TXT = CARD / "evidence" / "reviewer_report_r4_block.txt"

HEADER = (
    "\n---\n\n"
    "# r5 — 独立复审（第四轮）裁决转录（**载体落定，非实现者自签**）\n\n"
    "以下裁决正文由独立 reviewer 撰写、经父 agent 授权转录；转录方式为**逐字节追加**，\n"
    "不改写本文件既有字节。来源报告卡内副本：`evidence/I-05-A/reviewer_report_r4.md`。\n\n"
    "<!-- BEGIN REVIEWER VERDICT (verbatim, byte-exact) -->\n"
)
FOOTER = "\n<!-- END REVIEWER VERDICT -->\n"


def main() -> int:
    report_bytes = REPORT.read_bytes()
    block = BLOCK_TXT.read_bytes()
    assert block and block in report_bytes, "the block must come from the frozen report"

    before = REVIEW.read_bytes()
    header_bytes = HEADER.encode("utf-8")
    footer_bytes = FOOTER.encode("utf-8")
    after = before + header_bytes + block + footer_bytes
    REVIEW.write_bytes(after)
    readback = REVIEW.read_bytes()

    start = len(before) + len(header_bytes)
    stop = start + len(block)
    record = {
        "step": "transcribe reviewer verdict into review.md",
        "review_md": str(REVIEW),
        "before_bytes": len(before),
        "before_sha256": hashlib.sha256(before).hexdigest(),
        "after_bytes": len(readback),
        "after_sha256": hashlib.sha256(readback).hexdigest(),
        "old_bytes_are_exact_prefix": readback[: len(before)] == before,
        "added_bytes": len(readback) - len(before),
        "block_byte_identical_to_report": readback[start:stop] == block,
        "report_source": str(REPORT),
        "report_bytes": len(report_bytes),
        "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        "block": {
            "source_line_range_in_report_1based": [125, 136],
            "bytes": len(block),
            "sha256": hashlib.sha256(block).hexdigest(),
        },
        "appended_region_in_review_md": {
            "start_byte_offset": start,
            "stop_byte_offset": stop,
            "start_line_1based": before.decode("utf-8").count("\n") + 6,
            "stop_line_1based": readback.decode("utf-8").count("\n") + 1,
            "header_bytes": len(header_bytes),
            "footer_bytes": len(footer_bytes),
            "verification_slice_bytes": len(readback[start:stop]),
        },
        "no_normalisation": "every comparison above is on raw bytes",
    }
    (CARD / "after" / "r4_verdict_transcription.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
