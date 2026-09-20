"""Round-2 close-out: point handoff.json at the transcribed verdict and re-verify.

Runs AFTER seal_attempt.py and AFTER transcribe_verdicts.py, because the transcript must be
the last writer of review.md.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/close_round2.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    ev = os.path.join(attempt, "evidence", card)
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")

    trans_path = os.path.join(attempt, "recovery", "verdict_transcription_check.json")
    trans = json.load(open(trans_path, encoding="utf-8"))
    review_path = os.path.join(attempt, "review.md")
    review_text = open(review_path, encoding="utf-8").read()
    begin_line = None
    end_line = None
    for i, line in enumerate(review_text.splitlines(), start=1):
        if line.startswith("<!-- BEGIN independent-review verdict"):
            begin_line = i
        if line.startswith("<!-- END independent-review verdict") and begin_line:
            end_line = i
            break

    handoff_path = os.path.join(attempt, "handoff.json")
    handoff = json.load(open(handoff_path, encoding="utf-8"))
    handoff["reviewer_status"] = (
        "round 1: M21 accepted_scoped; M22/M23/M24 changes_required. "
        "round 2 (point review of revision r2): M21 accepted_scoped (maintained); "
        "M22 accepted_scoped (promoted); M23 accepted_scoped (promoted); "
        "M24 changes_required (blocker downgraded, one item still open). "
        "The round-2 verdict is transcribed VERBATIM into this attempt's review.md at lines "
        "%s-%s; the byte-equality proof is evidence/%s/verdict_transcription_check.txt. "
        "The implementer never writes 'accepted'." % (begin_line, end_line, card))
    handoff["review_verdict_transcription"] = {
        "review_md_begin_marker_line": begin_line,
        "review_md_end_marker_line": end_line,
        "review_md_sha256": sha(review_path),
        "check_file": "evidence/%s/verdict_transcription_check.txt" % card,
        "source_block_sha256": trans["source_block_sha256"],
        "written_block_sha256": trans["written_block_sha256"],
        "byte_identical": trans["byte_identical"],
        "reviewer_report_sha256": trans["report_sha256"],
        "reviewer_report_sha256_quoted_by_the_parent_agent":
            trans["report_sha256_as_quoted_by_the_parent_agent"],
        "reviewer_report_sha256_matches_the_parent_quotation":
            trans["report_sha256_matches_the_parent_quotation"],
        "note": "the verdict is appended, not rewritten; nothing in it was reworded, and the "
                "four values / the scope / the remaining items are exactly as written",
    }
    handoff["revision"] = (
        "r2 + round-2 close-out (independent review round 2: M21 accepted_scoped maintained, "
        "M22/M23 promoted to accepted_scoped, M24 still changes_required). Round-2 items "
        "implemented: required_message_ids gate + R4/R5 probes, metadata correction, "
        "append-only wording. The M24 cross-year item could NOT be implemented as literally "
        "specified (see revision_r2.json review_items_r2_round2 and the appended oracle.md "
        "section 8); it is disclosed and needs an owner ruling.")
    with open(handoff_path, "w", encoding="utf-8") as fh:
        json.dump(handoff, fh, ensure_ascii=False, indent=1)
    print("handoff reviewer_status -> lines", begin_line, end_line)

    # commands.json gets the two new probe units recorded
    proc = subprocess.run([py, "-X", "utf8", "-B",
                           os.path.join(attempt, "scripts", "build_commands.py"),
                           "--card", card, "--attempt", attempt],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("build_commands rc", proc.returncode)
    # then re-point the handoff at the rebuilt commands.json
    handoff = json.load(open(handoff_path, encoding="utf-8"))
    handoff["commands_executed"] = [u["unit_id"] for u in
                                    json.load(open(os.path.join(attempt, "commands.json"),
                                                   encoding="utf-8"))["units"]]
    with open(handoff_path, "w", encoding="utf-8") as fh:
        json.dump(handoff, fh, ensure_ascii=False, indent=1)

    with open(os.path.join(attempt, "recovery", "final_verify.txt"), "wb") as fh:
        proc = subprocess.run([py, "-X", "utf8", "-B",
                               os.path.join(attempt, "scripts", "final_verify.py"),
                               "--card", card, "--attempt", attempt],
                              stdout=fh, stderr=subprocess.STDOUT)
    print("final_verify rc", proc.returncode)
    return 0


if __name__ == "__main__":
    sys.exit(main())
