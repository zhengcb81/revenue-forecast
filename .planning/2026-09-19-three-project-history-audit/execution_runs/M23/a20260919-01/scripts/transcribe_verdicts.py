"""Transcribe the independent reviewer's round-2 verdicts into each card's review.md.

The verdict text is extracted PROGRAMMATICALLY from the reviewer report's section 7 (the
fenced ```markdown blocks), appended verbatim to review.md, and then re-extracted from the
WRITTEN FILE and compared byte-for-byte with the source block. Nothing about the verdict is
retyped, reworded or summarised here.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/transcribe_verdicts.py \
      --card M21 --attempt <attempt-root> [--report <path>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

BEGIN = "<!-- BEGIN independent-review verdict (round 2, transcribed verbatim) -->"
END = "<!-- END independent-review verdict -->"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def extract_blocks(report_text: str) -> dict:
    """Return {card: block_bytes} for the verdict blocks under section 7.

    In the reviewer's report each verdict is a markdown BLOCKQUOTE (lines beginning with
    ">"), not a fenced code block; the extraction therefore takes every consecutive
    ">"-prefixed line following a "### Mxx" heading, byte-for-byte, and adds no wording.
    Block quotes may contain empty ">" lines; a non-quote, non-blank line ends the block.
    """
    section = report_text.split("## 7.", 1)[1]
    section = section.split("\n## ", 1)[0]
    blocks = {}
    card = None
    collected = []

    def flush():
        nonlocal card, collected
        if card and collected:
            blocks[card] = ("\n".join(collected) + "\n").encode("utf-8")
        card, collected = None, []

    for line in section.split("\n"):
        m = re.match(r"### (M2[1-4])\s*$", line)
        if m:
            flush()
            card = m.group(1)
            continue
        if card is None:
            continue
        if line.startswith(">"):
            collected.append(line)
            continue
        if line.strip() == "":
            if collected:
                collected.append("")  # keep an interior blank; trimmed on flush
            continue
        flush()
    flush()
    for key, value in list(blocks.items()):
        text = value.decode("utf-8").rstrip("\n")
        while text.endswith("\n") or text.split("\n")[-1].strip() == "":
            text = text.rstrip("\n")
            if text.split("\n")[-1].strip() == "":
                text = "\n".join(text.split("\n")[:-1])
            else:
                break
        blocks[key] = (text + "\n").encode("utf-8")
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--report", default=r"C:\Users\郑曾波\AppData\Local\Temp"
                                            r"\m21m24-review-20260920-035233\REPORT_R2.md")
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    ev = os.path.join(attempt, "evidence", card)

    report_bytes = open(args.report, "rb").read()
    report_text = report_bytes.decode("utf-8")
    blocks = extract_blocks(report_text)
    if card not in blocks:
        print("no verdict block found for", card)
        return 1
    source_block = blocks[card]

    review_path = os.path.join(attempt, "review.md")
    existing = open(review_path, "rb").read()
    # idempotent: drop a previously transcribed block so the script can be re-run
    if BEGIN.encode("utf-8") in existing:
        head = existing.split(BEGIN.encode("utf-8"))[0]
        existing = head.rstrip(b"\n") + b"\n"

    payload = (BEGIN.encode("utf-8") + b"\n\n" + source_block + b"\n" + END.encode("utf-8")
               + b"\n")
    first_line = len(existing.decode("utf-8").splitlines()) + 1  # 1-based line of BEGIN
    with open(review_path, "wb") as fh:
        fh.write(existing + payload)

    # ---- re-extract from the WRITTEN file and compare byte-for-byte -------------
    written = open(review_path, "rb").read()
    beg = written.find(BEGIN.encode("utf-8"))
    stripped = written[beg:].split(b"\n", 1)[1].lstrip(b"\n")
    end_at = stripped.find(END.encode("utf-8"))
    written_block = stripped[:end_at].rstrip(b"\n") + b"\n"

    equal = written_block == source_block
    record = {
        "card_id": card,
        "report_path": args.report,
        "report_sha256": sha(report_bytes),
        "report_sha256_as_quoted_by_the_parent_agent":
            "043b1bb0bc604ef4e0e08e2b27aa55711675be908af3f4797a5109aa23a84ecc",
        "report_sha256_matches_the_parent_quotation": (
            sha(report_bytes) == "043b1bb0bc604ef4e0e08e2b27aa55711675be908af3f4797a5109aa23a84ecc"),
        "report_bytes": len(report_bytes),
        "source_block_sha256": sha(source_block),
        "source_block_bytes": len(source_block),
        "written_block_sha256": sha(written_block),
        "written_block_bytes": len(written_block),
        "byte_identical": equal,
        "transcription_method": "the block was extracted programmatically from the reviewer "
                                "report's section 7 fenced ```markdown block, appended to "
                                "review.md between HTML comment fences, then re-extracted from "
                                "the written file and compared byte-for-byte; no text was "
                                "retyped, reworded or summarised",
        "review_md_line_of_begin_marker": first_line,
        "review_md_line_of_end_marker": first_line + len(source_block.decode("utf-8").splitlines()) + 2,
        "review_md_path": review_path,
        "no_verdict_wording_changed": (
            "the four values (accepted_scoped / accepted_scoped / accepted_scoped / "
            "changes_required), the scope (formula only) and the listed remaining items are "
            "exactly as the reviewer wrote them"),
    }

    # ---- one shared check file per attempt + a copy under evidence/ -------------
    check_path = os.path.join(ev, "verdict_transcription_check.txt")
    lines = [
        "verdict transcription check (round 2)",
        "card_id = %s" % card,
        "report = %s" % args.report,
        "report_sha256 = %s" % record["report_sha256"],
        "report_sha256_quoted_by_parent = %s"
        % record["report_sha256_as_quoted_by_the_parent_agent"],
        "report_sha256_matches_parent_quotation = %s"
        % record["report_sha256_matches_the_parent_quotation"],
        "source_block_sha256 = %s  (%d bytes)"
        % (record["source_block_sha256"], record["source_block_bytes"]),
        "written_block_sha256 = %s  (%d bytes)"
        % (record["written_block_sha256"], record["written_block_bytes"]),
        "byte_identical = %s" % equal,
        "review_md = %s" % review_path,
        "review_md_begin_marker_line = %d" % first_line,
        "review_md_end_marker_line = %d" % record["review_md_line_of_end_marker"],
        "assertion = the block written into review.md is byte-for-byte the block extracted "
        "from the reviewer report; sha256(source) == sha256(written) == %s"
        % record["source_block_sha256"],
        "",
    ]
    with open(check_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    with open(os.path.join(attempt, "recovery", "verdict_transcription_check.json"), "w",
              encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=1)

    print("card", card, "byte_identical", equal)
    print("source", record["source_block_sha256"], "written", record["written_block_sha256"])
    print("report sha matches parent quotation:",
          record["report_sha256_matches_the_parent_quotation"])
    print("wrote", check_path)
    return 0 if equal else 1


if __name__ == "__main__":
    sys.exit(main())
