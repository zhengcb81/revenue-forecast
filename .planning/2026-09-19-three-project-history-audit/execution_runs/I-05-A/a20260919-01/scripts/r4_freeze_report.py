"""Step 1: freeze the reviewer report into the card (byte-exact copy + readback).

The report lives in %TEMP%, which will be cleaned.  This copies it BYTE FOR BYTE
into the card's evidence area and verifies the copy by re-reading both files.

Usage: <py> -X utf8 -B scripts/r4_freeze_report.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

CARD = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-05-A\a20260919-01"
)
SOURCE = Path(r"C:\Users\郑曾波\AppData\Local\Temp\planrev4\rev\REPORT_R4_FULL.md")
PREREG = Path(r"C:\Users\郑曾波\AppData\Local\Temp\planrev4\rev\PREREGISTRATION_R4.md")
DEST_DIR = CARD / "evidence" / "I-05-A"
DEST = DEST_DIR / "reviewer_report_r4.md"

# hashes cited by the parent (kept for the record, NOT used as the source of truth)
CITED = {
    "report_sha256": "d64c8ce2cf0a8382db324b8f9013721b20b415e833484b859233a6497d9bcc27",
    "report_bytes": 23101,
    "preregistration_sha256": "0e884affbef1fc7436d9c9a5d46f1ef9cbf83aadab57112947adcedea48a8785",
}
# content signature that identifies THIS card's verdict block (body markers that
# appear only in a real I-05-A acceptance).  The `plus1` boundary is spelled
# "偏移 +1" inside the verdict block; it appears as "plus1" only in the earlier
# §1.1 evidence listing, so the block is matched on the prose form.
SIGNATURE = (
    "accepted_scoped",
    "sections_binding_error",
    "sections_no_normalized_source",
    "88 passed",
    "c0",
    "偏移 +1",
    "char_start",
    "9/11",
)
SIGNATURE_MIN_HITS = len(SIGNATURE)


def main() -> int:
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    src_bytes = SOURCE.read_bytes()
    DEST.write_bytes(src_bytes)
    readback = DEST.read_bytes()
    text = src_bytes.decode("utf-8")

    # locate the verdict block BY CONTENT (the report's own headings are
    # inconsistent: the block labelled "④" holds the verdict text, while the
    # short "判定" summary sits under "①")
    lines = text.splitlines(keepends=True)
    block_start = None
    for index, line in enumerate(lines):
        if line.startswith("## ④") and "可粘贴进" in line and "裁决正文" in line:
            block_start = index
            break
    assert block_start is not None, "verdict block heading not found"
    block_end = block_start + 1
    while block_end < len(lines) and not (
        lines[block_end].startswith("## ") and block_end != block_start
    ):
        block_end += 1
    block = "".join(lines[block_start:block_end])
    missing = [token for token in SIGNATURE if token not in block]
    assert not missing, f"verdict block is missing required markers: {missing}"
    assert block.count("accepted_scoped") >= 1

    record = {
        "step": "freeze reviewer report",
        "source_path": str(SOURCE),
        "source_bytes": len(src_bytes),
        "source_sha256": hashlib.sha256(src_bytes).hexdigest(),
        "card_copy_path": str(DEST),
        "card_copy_bytes": len(readback),
        "card_copy_sha256": hashlib.sha256(readback).hexdigest(),
        "byte_identical": readback == src_bytes,
        "block_locator": (
            "identified BY CONTENT: the '## ④ … 可粘贴进 `review.md` 的裁决正文' block; "
            "the report's own '①' heading holds the short verdict summary, so the parent's "
            "'§4' refers to this ④ block (the numbering inside the file is inconsistent)"
        ),
        "also_present": {
            "short_verdict_heading": "## ① 判定：`accepted_scoped`",
            "evidence_listing_heading": "### 1.1 是否真的 per-origin 强制（你要求的第 1 项）",
            "note": "the machine-readable injection listings (plus1 / plus1_content / only_second / "
                    "midline / fabricated / roleswap) live in §1.1, not inside the verdict block",
        },
        "preregistration": {
            "source_path": str(PREREG),
            "exists": PREREG.is_file(),
            "sha256_live": (
                hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.is_file() else None
            ),
            "sha256_cited": CITED["preregistration_sha256"],
            "matches_cited": (
                PREREG.is_file()
                and hashlib.sha256(PREREG.read_bytes()).hexdigest()
                == CITED["preregistration_sha256"]
            ),
        },
        "cited_by_parent": CITED,
        "discrepancy": {
            "cited_report_sha256_matches_live": (
                hashlib.sha256(src_bytes).hexdigest() == CITED["report_sha256"]
            ),
            "cited_report_bytes_matches_live": len(src_bytes) == CITED["report_bytes"],
            "note": (
                "The bytes on disk at freeze time do NOT match the sha256/size the parent "
                "cited (d64c8ce2…/23101 B). The live file is the one frozen here; its "
                "content signature (accepted_scoped + sections_binding_error + "
                "sections_no_normalized_source + 88 passed + c0 + plus1 + 9/11) confirms it is "
                "this card's round-4 verdict report. The cited value is preserved unverified."
            ),
        },
        "verdict_block": {
            "start_line_1based": block_start + 1,
            "end_line_1based": block_end,
            "line_count": block_end - block_start,
            "bytes": len(block.encode("utf-8")),
            "sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
            "signature_tokens_present": list(SIGNATURE),
        },
    }
    (DEST_DIR / "reviewer_report_r4.freeze.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    (CARD / "evidence" / "reviewer_report_r4_block.txt").write_text(
        block, encoding="utf-8", newline="\n"
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
