"""Round-5 handoff registration: E1 erratum, E2 strengthening, the CMD-I04C-08
raw-log gap, and the pointer to the reviewer's verdict in review.md section 5.

Append-only in meaning: existing strings keep their text and only gain a trailing
clause; new keys carry the new record; the three parallel arrays
(commands_executed / expected_exit_codes / raw_exit_codes) gain the same number of
entries each.  Idempotent (stops when `closeout_corrections` is present).

Run:  & $PY -B sim/patch_r5_handoff.py
"""

from __future__ import annotations

import io
import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ATTEMPT, "handoff.json")

E1_SUFFIX = (" [ERRATUM E1, round 5: evidence/phase-wall.txt records F-L2d "
             "max_lock_wait_seconds=9.782719 and phase_wall_seconds=13.386, i.e. 9.78 s / 13.4 s; the "
             "9.87/13.2 figures transcribed here were a digit transposition. The magnitude conclusion "
             "(8-way wait close to 10 s, phase wall about 13 s, queueing consumes the download budget) "
             "and ADR-2 are unchanged. Corrected in place in decision.md section 14, oracle.md R3-2 and "
             "review.md section 6.]")

REVIEWER_STATUS_SUFFIX = (" The closeout review verdict is now in review.md section 5: the reviewer's "
                          "verbatim text was pasted there by sim/patch_r5_docs.py (52 lines read out of "
                          "evidence/r5-reviewer-closeout-report.md, sha256 9dafd6cf566418cf...); the "
                          "implementer wrote no verdict and claims none. status stays review_pending: "
                          "sign-off is not the implementer's call.")

CLOSEOUT = {
    "source_report": ("reviewer closeout report, copied byte-for-byte to "
                      "evidence/r5-reviewer-closeout-report.md (sha256 "
                      "9dafd6cf566418cf4b5e1e9c21cb9147902fbe83dccd47147a5d66c20ef678d0); the paste block was "
                      "extracted from it by sim/patch_r5_docs.py, never retyped"),
    "verdict": "accepted_scoped (limited to this attempt's design text and simulation results)",
    "E1_phase_wall_numbers": {
        "status": "corrected (append-only, 3 sites + handoff)",
        "defect": ("review.md section 6 quoted 'max lock wait 9.87 s, phase wall 13.2 s' for F-L2d while "
                   "evidence/phase-wall.txt records max_lock_wait_seconds=9.782719, phase_wall_seconds=13.386"),
        "correction": "9.78 s / 13.4 s",
        "sites": ["review.md section 6 (correction block after the table)",
                  "decision.md section 14 F-I04C-12 (correction block after the bullet)",
                  "oracle.md R3-2 (correction note inside the appended section)",
                  "handoff.json.results.queue_cost (in-place erratum annotation)"],
        "unchanged": "no design conclusion, no assertion strength, no frozen oracle expectation",
    },
    "E2_assertion_strengthening": {
        "status": "strengthened + mutation evidence",
        "defect": ("sim/cases_timeout.py F-T4: the sub-clause `not any(lease in successful_ids is False ...)` "
                   "is a CHAINED COMPARISON, i.e. `(lease in successful_ids) and (successful_ids is False)` = "
                   "constant False, so `not any(...)` was vacuously True and could never fail; the "
                   "'queue wait is reported' check was called with a literal True (a recorder, not an assertion); "
                   "the winners/joiners clause compared lengths only"),
        "fix": ["replaced by explicit quantifiers: all(lease in successful_ids ...) AND "
                "all(lease not in timed_out_ids ...) AND view['entries'] != []",
                "the queue-wait check now asserts that every successful participant reported lock_wait and that "
                "0.0 <= wait <= budget + 0.001 (1 ms = reporting resolution)",
                "the winners/joiners clause is now set equality plus disjointness, not a length compare"],
        "checks_unchanged": "F-T4 still reports 8 checks with the same names; no expectation changed",
        "mutation_evidence": ("evidence/r5-assertion-mutation.txt (sim/verify_r5_assertions.py, 16/16 expectations): "
                              "the historical sub-clause returns True in 4/4 hostile views, the historical whole "
                              "clause stays green when a timed-out lease is in the refcount while succeeded/timed_out "
                              "overlap, and every injected defect (stray lease, missing lock_wait, wait over budget, "
                              "miscounted actions) turns the shipped clause red"),
        "recheck_run": ("evidence/r5-timeout-suite-recheck.txt: F-T1/T2/T3/T4 = 7/3/6/8 checks all PASS, exit 0, run "
                        "into evidence/recheck/run (the frozen evidence/run/F-T4/ was NOT overwritten); that run's "
                        "outcome was P0,P2,P3,P4 timed out and P1,P5 succeeded with waits 0.0 s / 0.676 s"),
        "raw_log_gap_closed": "the strengthened suite now has a raw log (the CMD-I04C-08 gap below)",
    },
    "CMD_I04C_08_raw_log_gap": {
        "status": "recorded, not re-run as an implementer command",
        "claim": ("commands.json and handoff.json claim 'pytest -k pause or resume' => 8 passed / 109 deselected "
                  "on the byte-identical iso source"),
        "gap": ("no raw log exists in this attempt: searching the whole attempt (excluding iso/) for 'deselected' "
                "matches ONLY commands.json and handoff.json, i.e. the two files that make the claim"),
        "resolution": ("the closeout reviewer re-ran it from a %TEMP% copy of the iso tree and got "
                       "'8 passed, 109 deselected in 0.32s' (exit 0) => the claim is TRUE but was undocumented"),
        "standing_rule": "from round 5 on, any command whose result is claimed must leave its raw log in evidence/",
    },
    "append_only_chain": ("evidence/r5-appendonly-proof.txt (sim/verify_r5_appendonly.py): unwinding the round-5 "
                          "blocks restores the round-4 state byte-for-byte and unwinding the round-4 blocks then "
                          "restores the originally reviewed bytes (decision.md bb9bb0f4..., review.md 8cc116bc..., "
                          "oracle.md 3594f4d6...)"),
    "reviewer_report_copy": "evidence/r5-reviewer-closeout-report.md (hashed in evidence/hashes.txt)",
}

NEW_COMMANDS = [
    ("I04C-10-timeout-suite-recheck", 0, 0),
    ("I04C-11-assertion-mutation", 0, 0),
    ("I04C-12-appendonly-chain", 0, 0),
]


def main():
    with io.open(PATH, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if "closeout_corrections" in data:
        print("SKIP already applied (closeout_corrections present)")
        return 0

    before = {
        "revision": data["revision"],
        "next_action": data["next_action"],
        "reviewer_status": data["reviewer_status"],
        "queue_cost": data["results"]["queue_cost"],
    }

    data["closeout_corrections"] = CLOSEOUT
    data["results"]["queue_cost"] = before["queue_cost"] + E1_SUFFIX
    data["reviewer_status"] = before["reviewer_status"] + REVIEWER_STATUS_SUFFIX
    for name, expected, raw in NEW_COMMANDS:
        data["commands_executed"] = list(data["commands_executed"]) + [name]
        data["expected_exit_codes"] = list(data["expected_exit_codes"]) + [expected]
        data["raw_exit_codes"] = list(data["raw_exit_codes"]) + [raw]
    data["evidence_paths"] = list(data["evidence_paths"]) + [
        "execution_runs/I-04-C/a20260919-01/evidence/r5-reviewer-closeout-report.md",
        "execution_runs/I-04-C/a20260919-01/evidence/r5-assertion-mutation.txt",
        "execution_runs/I-04-C/a20260919-01/evidence/r5-timeout-suite-recheck.txt",
        "execution_runs/I-04-C/a20260919-01/evidence/r5-appendonly-proof.txt",
    ]

    with io.open(PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=1, sort_keys=True)

    with io.open(PATH, "r", encoding="utf-8") as handle:
        check = json.load(handle)
    print("wrote handoff.json")
    print("  keys=%d  commands/expected/raw=%d/%d/%d"
          % (len(check), len(check["commands_executed"]), len(check["expected_exit_codes"]),
             len(check["raw_exit_codes"])))
    print("  E1 in review.md section 5 pointer: %s"
          % ("review.md section 5" in check["reviewer_status"]))
    print("  prefix preservation:")
    for name, old in sorted(before.items()):
        new = check["revision"] if name == "revision" else (
            check["next_action"] if name == "next_action" else (
                check["reviewer_status"] if name == "reviewer_status" else check["results"]["queue_cost"]))
        print("    %-16s startswith(old)=%s  suffix_added=%s"
              % (name, new.startswith(old), len(new) > len(old)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
