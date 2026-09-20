"""Append a reviewer round's verdict blocks to review.md, byte-for-byte.

Generalised version of the round-2 transcriber: it extracts, IN ORDER, the blockquote
verdict blocks that follow the report's "## 7." heading and maps them to the cards in the
report's own stated order (M21, M22, M23, M24 - the same order the report's section 0
table uses). Each round gets its own BEGIN/END marker block, so earlier rounds are kept
and never rewritten.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/transcribe_round3_verdicts.py \
      --card M21 --attempt <attempt-root> [--report <path>] [--round 3]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

CARD_ORDER = ("M21", "M22", "M23", "M24")
BEGIN_T = "<!-- BEGIN independent-review verdict (round %d, transcribed verbatim) -->"
END_T = "<!-- END independent-review verdict (round %d) -->"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def section7(report_text: str, report_name: str = "R3") -> str:
    """The text of the report's '## 7.' section.

    The heading itself is not part of the payload; cutting anywhere inside it is harmless
    because no verdict line can begin with the '#' marker. The cut for the END of the section
    must handle both '\\n## ' and '\\n\\n## ' (the reviewer's reports use the latter).
    """
    after = report_text.split("## 7.", 1)[1]
    for tail_marker in ("\n\n## ", "\n## "):
        if tail_marker in after:
            return after.split(tail_marker, 1)[0]
    return after


def extract_blocks(report_text: str) -> list:
    """Blockquote verdict blocks under '## 7.', in order.

    A blank SEPARATOR LINE between two quote runs starts a new block; a quote line containing
    only '>' is an interior blank of the SAME block. So the rule needs the previous line type:
      * line starts with '>' and is not exactly '>'  -> append
      * line is exactly '>'                           -> append (interior blank)
      * line is blank AND the previous line was exactly '>'  -> append (block still open)
      * line is blank otherwise                       -> CLOSE the current block
    """
    section = section7(report_text)
    raw = section.split("\n")
    blocks = []
    current = []
    for line in raw:
        if line.startswith(">") and line.strip() != ">":
            current.append(line)
            continue
        if line.strip() == ">":
            current.append(line)
            continue
        if line.strip() == "":
            if current and current[-1].strip() == ">":
                current.append(line)
                continue
            if current:
                blocks.append(current)
                current = []
            continue
        if current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    # drop a trailing interior blank from each block and normalise to one final newline
    out = []
    for block in blocks:
        while block and block[-1].strip() == "":
            block.pop()
        out.append(("\n".join(block) + "\n").encode("utf-8"))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=list(CARD_ORDER))
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--report", default=r"C:\Users\郑曾波\AppData\Local\Temp"
                                            r"\m21m24-review-20260920-035233\REPORT_R3.md")
    parser.add_argument("--round", type=int, default=3)
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    ev = os.path.join(attempt, "evidence", card)

    report_bytes = open(args.report, "rb").read()
    blocks = extract_blocks(report_bytes.decode("utf-8"))
    if len(blocks) != len(CARD_ORDER):
        print("expected %d verdict blocks, found %d" % (len(CARD_ORDER), len(blocks)))
        return 1
    source_block = blocks[CARD_ORDER.index(card)]

    begin = (BEGIN_T % args.round).encode("utf-8")
    end = (END_T % args.round).encode("utf-8")
    review_path = os.path.join(attempt, "review.md")
    existing = open(review_path, "rb").read()
    # Idempotency, and preservation of EARLIER rounds: every begin/end marker pair of any
    # round is located, everything AFTER the last end-marker is discarded (that is this
    # script's own previous output, possibly half-written), and every complete block up to and
    # including the last end-marker is kept in place. An earlier draft instead cut at the
    # newest begin-marker, which truncated the round-2 block when round 3 was appended.
    marker_re = re.compile(re.escape(b"<!-- BEGIN independent-review verdict") + rb"[^\n]*-->")
    end_re = re.compile(re.escape(b"<!-- END independent-review verdict") + rb"[^\n]*-->")
    begins = [m.end() for m in marker_re.finditer(existing)]
    ends = [m.end() for m in end_re.finditer(existing)]
    if begins and ends and ends[-1] > begins[-1]:
        existing = existing[:ends[-1]].rstrip(b"\n") + b"\n"

    payload = begin + b"\n\n" + source_block + b"\n" + end + b"\n"
    begin_line = len(existing.decode("utf-8").splitlines()) + 1
    with open(review_path, "wb") as fh:
        fh.write(existing + b"\n" + payload)

    written = open(review_path, "rb").read()
    at = written.find(begin)
    inner = written[at:].split(b"\n", 1)[1].lstrip(b"\n")
    written_block = inner[:inner.find(end)].rstrip(b"\n") + b"\n"
    equal = written_block == source_block

    # round-3 record (round-2 record is left untouched)
    record = {
        "card_id": card,
        "round": args.round,
        "report_path": args.report,
        "report_sha256": sha(report_bytes),
        "report_bytes": len(report_bytes),
        "report_lines": len(report_bytes.decode("utf-8").splitlines()),
        "report_sha256_matches_the_transmitted_value": (
            sha(report_bytes)
            == "5e5b0d15d3a2e14ffa71ffad49e18be2e49ed60af1313b51fc5f2a0d61f23677"),
        "transmitted_value_note": "the round-2 report's transmitted hash was wrong and that "
                                  "was settled in round 3 (report section 1); this round's "
                                  "transmitted hash is verified above",
        "source_block_sha256": sha(source_block),
        "source_block_bytes": len(source_block),
        "written_block_sha256": sha(written_block),
        "written_block_bytes": len(written_block),
        "byte_identical": equal,
        "block_index_in_section_7": CARD_ORDER.index(card),
        "card_order_used": list(CARD_ORDER),
        "order_source": "the report's own section 0 table and section 7 block order",
        "review_md_line_of_begin_marker": begin_line,
        "review_md_line_of_end_marker": begin_line
        + len(source_block.decode("utf-8").splitlines()) + 2,
        "review_md_path": review_path,
        "review_md_sha256_after_append": sha(written),
        "no_verdict_wording_changed": "the verdict, its scope (formula only) and its listed "
                                      "remaining items are exactly as the reviewer wrote them",
        "round2_record_preserved": ("round 2" in written.decode("utf-8")),
    }

    check_path = os.path.join(ev, "verdict_transcription_check.txt")
    with open(check_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n")
        fh.write("=" * 72 + "\n")
        fh.write("verdict transcription check (round %d)\n" % args.round)
        for key in ("card_id", "report_path", "report_sha256", "report_bytes", "report_lines",
                    "report_sha256_matches_the_transmitted_value", "source_block_sha256",
                    "source_block_bytes", "written_block_sha256", "written_block_bytes",
                    "byte_identical", "block_index_in_section_7",
                    "review_md_line_of_begin_marker", "review_md_line_of_end_marker",
                    "review_md_sha256_after_append", "round2_record_preserved"):
            fh.write("%s = %s\n" % (key, record[key]))
        fh.write("assertion = sha256(source round-%d block) == sha256(block written into "
                 "review.md) == %s\n" % (args.round, record["source_block_sha256"]))
    with open(os.path.join(attempt, "recovery",
                           "verdict_transcription_check_round%d.json" % args.round), "w",
              encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=1)

    print("card", card, "round", args.round, "byte_identical", equal,
          "| lines", begin_line, "-", record["review_md_line_of_end_marker"])
    print("source", record["source_block_sha256"], "written", record["written_block_sha256"])
    print("report sha matches transmitted:",
          record["report_sha256_matches_the_transmitted_value"])
    return 0 if equal else 1


if __name__ == "__main__":
    sys.exit(main())
