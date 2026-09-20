"""Normalise review.md to exactly one verdict block per round, in round order.

Recovery step after two append bugs in this round (both now fixed in
transcribe_round3_verdicts.py): a duplicate round-3 block and a transposed layout. This
script re-derives the file deterministically:

  1. take the part of review.md BEFORE the first verdict marker (the original r1 body);
  2. re-append the round-2 block from its recorded bytes;
  3. re-append the round-3 block from its recorded bytes;
  4. assert the written blocks equal the recorded blocks byte-for-byte.

It never rewrites a verdict's wording: the blocks come from
recovery/verdict_transcription_check_round{2,3}.json, which in turn came from the reports.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/normalise_review_md.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

BEGIN_T = "<!-- BEGIN independent-review verdict (round %d, transcribed verbatim) -->"
END_T = "<!-- END independent-review verdict (round %d) -->"
ANY_MARKER = re.compile(re.escape(b"<!-- BEGIN independent-review verdict") + rb"[^\n]*-->")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    ev = os.path.join(attempt, "evidence", card)
    review_path = os.path.join(attempt, "review.md")

    raw = open(review_path, "rb").read()
    m = ANY_MARKER.search(raw)
    head = raw[:m.start()].rstrip(b"\n") + b"\n" if m else raw.rstrip(b"\n") + b"\n"

    blocks = {}
    for rnd in (2, 3):
        path = os.path.join(attempt, "recovery",
                            "verdict_transcription_check_round%d.json" % rnd)
        with open(path, "rb") as fh:
            rec = json.loads(fh.read().decode("utf-8"))
        report = open(rec["report_path"], "rb").read()
        blocks[rnd] = {"record": rec, "report": report}

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "t3", os.path.join(attempt, "scripts", "transcribe_round3_verdicts.py"))
    t3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t3)

    out = head
    positions = {}
    for rnd in (2, 3):
        rec = blocks[rnd]["record"]
        report_text = blocks[rnd]["report"].decode("utf-8")
        extracted = t3.extract_blocks(report_text)
        idx = rec["block_index_in_section_7"]
        source_block = extracted[idx]
        begin = (BEGIN_T % rnd).encode("utf-8")
        end = (END_T % rnd).encode("utf-8")
        positions[rnd] = {
            "begin_line": len(out.decode("utf-8").splitlines()) + 1,
            "block_sha256": sha(source_block),
            "matches_recorded": sha(source_block) == rec["source_block_sha256"],
        }
        out = out + b"\n" + begin + b"\n\n" + source_block + b"\n" + end + b"\n"
        positions[rnd]["end_line"] = len(out.decode("utf-8").splitlines())
    with open(review_path, "wb") as fh:
        fh.write(out)

    # verify from the written file
    written = open(review_path, "rb").read()
    ok = True
    for rnd in (2, 3):
        begin = (BEGIN_T % rnd).encode("utf-8")
        end = (END_T % rnd).encode("utf-8")
        at = written.find(begin)
        inner = written[at:].split(b"\n", 1)[1].lstrip(b"\n")
        block = inner[:inner.find(end)].rstrip(b"\n") + b"\n"
        positions[rnd]["written_sha256"] = sha(block)
        positions[rnd]["byte_identical"] = (sha(block) == positions[rnd]["block_sha256"])
        ok = ok and positions[rnd]["byte_identical"]
    counts = {rnd: written.count((BEGIN_T % rnd).encode("utf-8")) for rnd in (2, 3)}

    record = {
        "card_id": card,
        "review_md_path": review_path,
        "review_md_sha256": sha(written),
        "review_md_lines": len(written.decode("utf-8").splitlines()),
        "blocks": positions,
        "block_occurrences": counts,
        "all_blocks_byte_identical": ok,
        "exactly_one_block_per_round": all(v == 1 for v in counts.values()),
        "reason": "normalisation after two append bugs in round 3: a duplicated round-3 block "
                  "and a transposed layout. The verdict WORDING is untouched - each block is "
                  "re-extracted from the reviewer's own report with the recorded index and "
                  "compared byte-for-byte with the recorded digest.",
    }
    with open(os.path.join(attempt, "recovery", "review_md_round_blocks.json"), "w",
              encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=1)
    print(json.dumps(record, ensure_ascii=False, indent=1))
    return 0 if (ok and record["exactly_one_block_per_round"]) else 1


if __name__ == "__main__":
    sys.exit(main())
