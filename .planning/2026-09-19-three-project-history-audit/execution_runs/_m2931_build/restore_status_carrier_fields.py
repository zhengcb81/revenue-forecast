import argparse
import hashlib
import json
import os
import re

CARDS = ("M29", "M30", "M31")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=CARDS)
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    handoff_path = os.path.join(attempt, "handoff.json")
    before = sha256(handoff_path)
    with open(handoff_path, "r", encoding="utf-8") as handle:
        handoff = json.load(handle)

    # the verdict line range is re-derived from the transcription proof (the authoritative source),
    # not copied from prose
    proof = os.path.join(attempt, "evidence", card, "verdict_transcription_check.txt")
    fields = {}
    with open(proof, "r", encoding="utf-8") as handle:
        for line in handle:
            if ": " in line:
                key, value = line.split(": ", 1)
                fields[key.strip()] = value.strip()
    first = int(fields["appended_block_first_line_1based"])
    last = int(fields["appended_block_last_line_1based"])

    status = handoff["reviewer_status"]
    restored = {
        "verdict_transcribed_verbatim_into": "review.md",
        "verdict_block_first_line": first,
        "verdict_block_last_line": last,
        "verdict_block_sha256": fields["appended_block_sha256"],
        "transcription_proof": "evidence/%s/verdict_transcription_check.txt" % card,
        "reviewer_report": status.get("reviewer_report"),
        "state": "accepted_scoped (formula qualification only), per the independent reviewer",
        "implementer_signed": False,
        "implementer_never_signs_acceptance": True,
    }
    status["verdict_line_range"] = restored
    status["carrier_fields_restored_utc_note"] = (
        "the line-range fields are re-derived from evidence/%s/verdict_transcription_check.txt by "
        "scripts/restore_status_carrier_fields.py so the audit link survives every later edit of this "
        "object" % card)
    handoff["reviewer_status"] = status
    with open(handoff_path, "w", encoding="utf-8") as handle:
        json.dump(handoff, handle, ensure_ascii=False, indent=1)
    print("%s reviewer_status.verdict_line_range = %d-%d (sha %s)"
          % (card, first, last, restored["verdict_block_sha256"][:16]))
    print("   handoff.json sha256 %s -> %s" % (before[:16], sha256(handoff_path)[:16]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
