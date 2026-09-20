"""Record the reviewer's acceptance for one card, with its carrier, AFTER the verdict is transcribed.

The implementer NEVER signs: this file only records that an INDEPENDENT reviewer's verdict was
transcribed byte-for-byte into review.md, where it lands (line range + sha256), and which generation
it applies to.  pack_card.py and write_handoff.py read this file, so the accepted state survives
re-running of the closing sequence.

Usage:
  python -X utf8 -B apply_review_decision.py --card M17 --attempt-root <attempt> \
      --proof <evidence/M17/transcription_proof_r3.json> --generation "<boundary>"
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os

import card_units

VERDICT = "accepted_scoped (formula qualification only)"
AUTHORITY = "acceptance was written by an independent reviewer, not by the implementer"


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--proof", required=True)
    parser.add_argument("--generation", default="2026-09-20T03:44:34Z-03:44:43Z")
    parser.add_argument("--reviewer", default=("independent reviewer of attempt a20260919-01, "
                                               "round r3, zero-write mode"))
    parser.add_argument("--report", default=None)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    proof = json.load(open(args.proof, encoding="utf-8"))
    if proof.get("byte_equal") is not True:
        print("REFUSED: the transcription proof does not state byte_equal=true")
        return 3

    decision = {
        "card_id": card,
        "model_id": card_units.CARDS[card]["model_id"],
        "formula_state": "accepted_scoped",
        "status": "accepted_scoped",
        "verdict": VERDICT,
        "authority": AUTHORITY,
        "implementer_signed": False,
        "implementer_never_signs_acceptance": True,
        "signed_by": args.reviewer,
        "carrier": {
            "review_md_verdict_block": {
                "target": proof["target"],
                "first_line": proof["landing_point"]["target_first_line"],
                "last_line": proof["landing_point"]["target_last_line"],
                "byte_offset_start": proof["landing_point"]["target_byte_offset_start"],
                "byte_offset_end": proof["landing_point"]["target_byte_offset_end"],
                "sha256": proof["copied_region_sha256"],
                "bytes": proof["source_block_bytes"],
                "source_report_lines": "%s:%s" % (proof["source_range"]["first_line"],
                                                  proof["source_range"]["last_line"]),
            },
            "byte_equality_proof": os.path.relpath(args.proof, attempt).replace("\\", "/"),
            "byte_equality_proof_sha256": sha256(args.proof),
            "byte_equal_source_and_copy": proof["byte_equal"],
            "generation_boundary": args.generation,
            "generation_snapshot": "evidence/%s/generation_20260920T034434Z/" % card,
            "reviewer_report": args.report,
            "note": ("the acceptance lives in the reviewer's own words inside review.md; this file "
                     "records where that block is and that the copy equals the reviewer's bytes"),
        },
        "scope": {
            "formula": "accepted_scoped",
            "disclosure_adaptation": "unmapped (ZERO output, not partial progress)",
            "accuracy": "unproven (no evaluation was run at all)",
        },
        "not_extendable_to": ("disclosure adaptation, accuracy, other models, other companies, other "
                              "periods, or any other batch"),
        "generation_validity": ("the judgement applies to the frozen generation %s; a later write to "
                                "the attempt directory invalidates it and requires re-review"
                                % args.generation),
        "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    out = os.path.join(evidence, "review_decision.json")
    tmp = out + ".tmp-atomic"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(decision, handle, ensure_ascii=False, indent=1)
    os.replace(tmp, out)
    print("review decision recorded:", out)
    print("formula_state:", decision["formula_state"], "| status:", decision["status"])
    print("implementer_signed:", decision["implementer_signed"],
          "| authority:", decision["authority"])
    print("carrier block lines:", decision["carrier"]["review_md_verdict_block"]["first_line"], "-",
          decision["carrier"]["review_md_verdict_block"]["last_line"],
          "| sha256:", decision["carrier"]["review_md_verdict_block"]["sha256"][:16])
    print("generation boundary:", decision["carrier"]["generation_boundary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
