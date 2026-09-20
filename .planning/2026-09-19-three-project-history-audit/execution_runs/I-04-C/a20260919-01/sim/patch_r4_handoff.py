"""Round-4 handoff registration: close carry condition C1, register C2 (OPEN-3).

Append-only in meaning:
  * existing values are preserved; `revision`, `next_action` and `reviewer_status`
    only gain a trailing sentence about this round;
  * new keys `review_carry_conditions` and `owner_gates` carry the full record;
  * one entry is appended to `open_questions`, and the parallel arrays
    `commands_executed` / `expected_exit_codes` / `raw_exit_codes` gain one entry
    each so they stay parallel.

Idempotent: a second run detects `review_carry_conditions` and stops.
Run:  & $PY -B sim/patch_r4_handoff.py
"""

from __future__ import annotations

import io
import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ATTEMPT, "handoff.json")

C1 = {
    "condition": ("C1 (must close): decision.md section 13.5 and review.md section 1 / P3-4 still "
                  "printed the STALE F-LK2 group finals [12, 19, 7, 26, 43] => lost_updates "
                  "[197, 185, 191, 198, 14], while the final evidence round recorded a different group."),
    "status": "closed",
    "closed_in": "round 4 (append-only text/evidence correction; no design change)",
    "true_values": ("finals [16, 35, 10, 56, 18] => lost_updates [184, 165, 190, 144, 182]; "
                    "lost_updates_range [144, 190]; expected 200 (8 processes x 25 rounds); "
                    "lock_acquisitions 0 in all five rounds"),
    "stale_group_is_self_inconsistent": ("expected - [12,19,7,26,43] = [188,181,193,174,157], which is "
                                         "NOT the [197,185,191,198,14] printed next to it"),
    "recompute_command": "& $PY -B sim/verify_flk2.py",
    "recompute_output": ("evidence/flk2-recompute.txt (13/13 checks PASS: A1-A8 recompute every round from the "
                         "raw run directories and compare with the record fields, B1-B4 recheck the record's own "
                         "arithmetic, C1 shows the stale group is impossible for expected=200)"),
    "authoritative_evidence": [
        "evidence/lock-and-legacy.txt line 6 (the F-LK2 record: finals / lost_updates / lost_updates_range / determinism)",
        "evidence/run/F-LK2-r{1..5}/counter.txt (raw final counter per round: 16, 35, 10, 56, 18)",
        "evidence/run/F-LK2-r{1..5}/payload.{0..7}.json (8 participants x 25 rounds, use_lock=false)",
        "evidence/run/F-LK2-r{1..5}/counter.journal.jsonl (lock_acquisitions=0 for every participant)",
    ],
    "correction_sites": [
        "decision.md section 13.5 item 5: correction block appended after the stale sentence (the sentence itself is byte-identical)",
        "review.md section 1 P3-4 row: correction block appended after the table (the row itself is byte-identical)",
        "decision.md section 14 F-I04C-13 table: closure note appended (the r3 patch had only reached oracle.md section 7)",
    ],
    "history_preserved": ("the stale group [12,19,7,26,43] stays verbatim in the decision.md section 14 F-I04C-13 row "
                          "and inside both correction quotes; the earlier-round 261/200 torn-write narrative is history "
                          "(it is not part of the final evidence round) and was NOT touched"),
    "append_only_proof": ("sim/verify_r4_appendonly.py: deleting exactly the inserted blocks reproduces the pre-change "
                          "sha256 of decision.md (bb9bb0f401e573409842afd7bfc7a17eb3d5dd52b79e134f41417f1aa0a6f479) and "
                          "review.md (8cc116bced471b721bf28f1a15f9daf3e875e720ad9cb3e7eb0ebd3966289a57)"),
    "scope_limits": ("numbers and registration only: no ADR text, no assertion strength and no frozen oracle expectation "
                     "was changed (there is no implementation item in C1)"),
}

C2 = {
    "condition": ("C2 (register only, no design change): OPEN-3 -- the naming/acceptance of the 60 s waiting cap "
                  "(lock_budget_for(x)=min(x,60)) and whether worker-pause may stay inside the lock."),
    "status": "open_owner_ruling",
    "kind": "OWNER RULING item, not an implementation item",
    "does_not_block": ("this does NOT block the accepted_scoped sign-off; no ADR text changes because of it, and until "
                       "the owner rules the implementation uses 60 as already frozen in the kernel"),
    "items": [
        "confirm the naming and the boundary acceptance of LOCK_MAX_SECONDS=60 as 'the waiting cap constant introduced "
        "by this card' (not a new budget: the request-phase budget is normally 900 s; its real effect is to cap the "
        "cleanup segment C<=85 s and short deadlines; a non-positive budget refuses to wait, proven by F-T2)",
        "decide whether worker-pause may stay inside the lock (this card keeps it inside: otherwise two participants "
        "could both believe they are the first pauser; see decision.md section 14 F-I04C-12)",
    ],
    "registered_locations": [
        "handoff.json.review_carry_conditions.C2_OPEN3_owner_gate",
        "handoff.json.owner_gates[0]",
        "handoff.json.open_questions (the original OPEN-3 entry plus the appended C2 registration entry)",
        "decision.md section 8 O-3 (appended registration block)",
        "decision.md section 12 'ADR-2 lock budget (v1.2) and OPEN-3' (appended cross-reference)",
        "decision.md section 14 'OPEN-3 (review advice)' (round-3 text, unchanged)",
        "review.md section 6 OPEN-3 row (round-3 text, unchanged)",
    ],
}

OWNER_GATE = {
    "gate": "OPEN-3",
    "carry_condition": "C2",
    "registered_in_round": "round 4 (2026-09-20, append-only registration)",
    "owner_action_required": True,
    "blocks_signoff": False,
    "blocks": [],
    "does_not_block": "does not block the accepted_scoped sign-off; it is an owner ruling item, not an implementation item",
    "summary": ("(a) name/accept the waiting cap constant 60 (lock_budget_for(x)=min(x,60)); "
                "(b) decide whether worker-pause may stay inside the lock (this card keeps it inside)"),
    "cross_refs": [
        "decision.md section 8 O-3",
        "decision.md section 12 (ADR-2 lock budget v1.2 and OPEN-3)",
        "decision.md section 14 (OPEN-3 review advice)",
        "review.md section 6 (OPEN-3 row)",
    ],
    "fallback_until_ruled": "the implementation uses 60 (the kernel froze the value and it is recorded in the run logs)",
}

OPEN_QUESTION_ENTRY = ("OPEN-3 (registered in round 4 as the C2 OWNER GATE, see review_carry_conditions."
                       "C2_OPEN3_owner_gate and owner_gates[0]): the record above is unchanged; this entry only makes "
                       "the registration explicit. Two rulings are pending: (a) the naming/boundary acceptance of the "
                       "60 s waiting cap; (b) whether worker-pause may stay inside the lock. THIS DOES NOT BLOCK THE "
                       "accepted_scoped SIGN-OFF: it is an owner ruling item, not an implementation item, and no ADR "
                       "text is changed by registering it (until the ruling the implementation uses 60).")

NEXT_ACTION_SUFFIX = (" ROUND 4 (2026-09-20, append-only correction): C1 is CLOSED -- the stale F-LK2 numbers in "
                      "decision.md section 13.5 and review.md section 1/P3-4 were corrected additively against the "
                      "recomputed truth (finals [16,35,10,56,18] => lost [184,165,190,144,182]; see "
                      "evidence/flk2-recompute.txt). C2 (OPEN-3) is registered as an owner gate (review_carry_conditions."
                      "C2_OPEN3_owner_gate, owner_gates[0], decision.md sections 8 O-3 and 12) and does NOT block the "
                      "accepted_scoped sign-off.")

REVISION_SUFFIX = (" + round 4 append-only correction (C1 closed with a recomputed F-LK2 truth; C2/OPEN-3 registered as "
                   "an owner gate; no design, assertion or oracle change)")

REVIEWER_STATUS_SUFFIX = (" Round 4 is an implementer text/evidence correction round only: it reopens no verdict and "
                          "claims none (review.md section 5 stays empty for the reviewer); C1 is closed and C2 is "
                          "registered as an owner gate.")


def main():
    with io.open(PATH, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if "review_carry_conditions" in data:
        print("SKIP already applied (review_carry_conditions present)")
        return 0

    data["review_carry_conditions"] = {
        "C1_stale_FLK2_numbers": C1,
        "C2_OPEN3_owner_gate": C2,
        "source": ("round-2 review verdict accepted_scoped carried two conditions; round 3 disposed the three "
                   "still-required items but left the C1 residue in decision.md section 13.5 and review.md section 1"),
    }
    data["owner_gates"] = [OWNER_GATE]
    data["open_questions"] = list(data["open_questions"]) + [OPEN_QUESTION_ENTRY]
    data["next_action"] = data["next_action"] + NEXT_ACTION_SUFFIX
    data["revision"] = data["revision"] + REVISION_SUFFIX
    data["reviewer_status"] = data["reviewer_status"] + REVIEWER_STATUS_SUFFIX
    data["changed_paths"] = list(data["changed_paths"]) + [
        "execution_runs/I-04-C/a20260919-01/recovery/**"]
    data["evidence_paths"] = list(data["evidence_paths"]) + [
        "execution_runs/I-04-C/a20260919-01/evidence/flk2-recompute.txt"]
    data["commands_executed"] = list(data["commands_executed"]) + ["I04C-09-flk2-recompute"]
    data["expected_exit_codes"] = list(data["expected_exit_codes"]) + [0]
    data["raw_exit_codes"] = list(data["raw_exit_codes"]) + [0]

    with io.open(PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=1, sort_keys=True)

    # read back: the file must still parse and the parallel arrays must stay parallel
    with io.open(PATH, "r", encoding="utf-8") as handle:
        check = json.load(handle)
    print("wrote handoff.json")
    print("  keys                      : %d" % len(check))
    print("  C1 status                 : %s" % check["review_carry_conditions"]["C1_stale_FLK2_numbers"]["status"])
    print("  C2 status                 : %s" % check["review_carry_conditions"]["C2_OPEN3_owner_gate"]["status"])
    print("  owner_gates               : %d (blocks_signoff=%s)"
          % (len(check["owner_gates"]), check["owner_gates"][0]["blocks_signoff"]))
    print("  commands/expected/raw lens: %d/%d/%d"
          % (len(check["commands_executed"]), len(check["expected_exit_codes"]), len(check["raw_exit_codes"])))
    print("  open_questions            : %d" % len(check["open_questions"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
