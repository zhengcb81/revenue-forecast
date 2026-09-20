"""Round-3 close-out: point handoff.json at both verdict blocks and re-verify.

Runs AFTER seal_attempt.py and AFTER the transcription/normalisation steps, because the
transcript must be the last writer of review.md.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/close_round3.py \
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

    blocks = json.load(open(os.path.join(attempt, "recovery", "review_md_round_blocks.json"),
                            encoding="utf-8"))
    b2 = blocks["blocks"]["2"]
    b3 = blocks["blocks"]["3"]
    review_path = os.path.join(attempt, "review.md")

    handoff_path = os.path.join(attempt, "handoff.json")
    handoff = json.load(open(handoff_path, encoding="utf-8"))
    handoff["reviewer_status"] = (
        "round 1: M21 accepted_scoped; M22/M23/M24 changes_required. "
        "round 2 (point review of revision r2): M21 accepted_scoped; M22/M23 accepted_scoped; "
        "M24 changes_required. "
        "round 3 (bounded final review): ALL FOUR accepted_scoped, formula qualification only; "
        "M24's deviation was independently upheld and the reviewer attributed the round-2 "
        "checklist error to itself. "
        "Both verdicts are transcribed VERBATIM into this attempt's review.md: round 2 at lines "
        "%s-%s, round 3 at lines %s-%s; byte-equality proofs in "
        "evidence/%s/verdict_transcription_check.txt. The implementer never writes 'accepted'."
        % (b2["begin_line"], b2["end_line"], b3["begin_line"], b3["end_line"], card))
    handoff["review_verdict_transcription"] = {
        "round2": {
            "review_md_lines": [b2["begin_line"], b2["end_line"]],
            "block_sha256": b2["block_sha256"],
            "byte_identical": b2["byte_identical"],
        },
        "round3": {
            "review_md_lines": [b3["begin_line"], b3["end_line"]],
            "block_sha256": b3["block_sha256"],
            "byte_identical": b3["byte_identical"],
            "report_sha256": json.load(open(os.path.join(
                attempt, "recovery", "verdict_transcription_check_round3.json"),
                encoding="utf-8"))["report_sha256"],
            "report_sha256_matches_the_transmitted_value": json.load(open(os.path.join(
                attempt, "recovery", "verdict_transcription_check_round3.json"),
                encoding="utf-8"))["report_sha256_matches_the_transmitted_value"],
        },
        "review_md_sha256": sha(review_path),
        "exactly_one_block_per_round": blocks["exactly_one_block_per_round"],
        "check_files": [
            "evidence/%s/verdict_transcription_check.txt" % card,
            "recovery/verdict_transcription_check.json",
            "recovery/verdict_transcription_check_round3.json",
            "recovery/review_md_round_blocks.json",
        ],
        "note": "none of the verdict wording was changed; the round-2 record is preserved "
                "alongside the round-3 one",
    }
    handoff["revision"] = (
        "r2 + round-2 close-out + round-3 close-out (independent review rounds 2 and 3: all four "
        "cards accepted_scoped, formula qualification only). Round-3 items implemented: verdict "
        "transcription with byte-equality proof, required_message_ids cardinality/explanatory "
        "fields, and the registered gap for this attempt's mislabelled round-2 runner snapshot. "
        "Two items are REGISTERED AND NOT FIXED because the round-3 boundary forbids editing "
        "oracle.md sections 0-12: M24's frozen section 5 is stale in three places (see the "
        "appended run section's section 9), and this attempt's round-2 disclosure about the "
        "FY2027 balance guard was too strong (section 10). Both need an owner ruling.")
    handoff["production_drift"] = {
        "detected_at": "2026-09-20 04:38 (local), during round-3 close-out, by "
                       "final_verify.production_hashes_unchanged reading False",
        "window": {
            "from": "2026-09-20 04:35:31",
            "until": "2026-09-20 04:40:53",
            "diverted_hash": "1f2639e1d44df6794a1478e7c3ed3400b5cf9d70cc994d3804e933bd6b020a86",
            "diverted_bytes": 19703,
            "anchored_hash": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "anchored_bytes": 26446,
        },
        "root_cause": "an orchestration-layer commit job: the repository pre-commit gate exported "
                      "the un-staged changes to C:\\Users\\郑曾波\\.cache\\pre-commit"
                      "\\patch1789875331-33652 and then ran `git checkout -- .`, which failed with "
                      "exit 255 on three concurrently-locked scratch files, so the patch was never "
                      "re-applied and the worktree stayed reset to HEAD. NOT caused by this attempt.",
        "resolved": True,
        "resolution": "the parent agent applied the same patch to its non-.planning subset "
                      "(git apply --check and git apply both exit 0); the anchored hash is restored "
                      "and was re-measured by this attempt",
        "rehashed_after_recovery_by_this_attempt": {
            "scripts/model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "scripts/model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        },
        "first_hand_records": [
            "recovery/production_drift.json (captured at detection time, with the behaviour probe)",
            "recovery/production_drift_resolution.json (the other end of the event)",
        ],
        "time_qualification": "the False warning produced inside the window was CORRECT and is not "
                              "a defect; it was never used to change an expectation, tolerance, "
                              "case, rejection condition or frozen artifact, and no re-snapshot was "
                              "taken",
        "honest_note": "the transient False reading is not preserved as its own file, because every "
                       "later rebuild of final_verify.txt and integrity.json happened after the "
                       "restoration and legitimately reads True; the diverted hash survives in "
                       "recovery/production_drift.json",
        "batch_wide": "the same event affected every attempt whose acceptance chain cites the "
                      "production hash 9ec65295...; this attempt reports only its own four cards",
    }
    handoff["lesson_registered"] = (
        "When a card's acceptance chain depends on a PRODUCTION FILE HASH, that hash must be "
        "treated as a quantity an external git operation can change underneath the attempt. On a "
        "mismatch: first record the drift and its time window, then let the orchestration layer "
        "decide whether to restore or re-anchor - NEVER adapt by editing an expectation, a "
        "tolerance, a case or a frozen artifact. This attempt followed that rule: it recorded the "
        "drift, kept running against its own byte-identical isolated snapshot, and changed nothing "
        "frozen.")
    with open(handoff_path, "w", encoding="utf-8") as fh:
        json.dump(handoff, fh, ensure_ascii=False, indent=1)
    print("handoff round2 lines", b2["begin_line"], b2["end_line"],
          "| round3 lines", b3["begin_line"], b3["end_line"])

    proc = subprocess.run([py, "-X", "utf8", "-B",
                           os.path.join(attempt, "scripts", "build_commands.py"),
                           "--card", card, "--attempt", attempt],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("build_commands rc", proc.returncode)
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
