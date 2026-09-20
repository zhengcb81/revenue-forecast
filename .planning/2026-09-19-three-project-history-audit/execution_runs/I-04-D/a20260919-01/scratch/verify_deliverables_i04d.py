"""Cross-check the three I-04-D deliverable documents against FACTS.md values.

Read-only: it opens handoff.json / review.md / recovery/README.md and compares the
case table with the measured numbers transcribed from scratch/FACTS.md section 4.
"""
import json
import os
import sys

A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (pause_calls, resume_calls, lock_acquisitions, final_ledger, worker) -- FACTS.md section 4
FACTS = {
    "F-L5": (1, 1, 4, "absent", "running"),
    "F-L6": (3, 3, 6, "absent", "running"),
    "F-L6b": (2, 2, 4, "absent", "running"),
    "F-L7": (1, 1, 3, "absent", "running"),
    "F-L7b": (1, 1, 3, "absent", "running"),
    "F-L7c": (1, 1, 3, "absent", "running"),
    "F-L9a": (0, 0, 1, "absent, marker absent", "paused (untouched)"),
    "F-L9c": (1, 0, 2, "entries=[], owner=null", "paused (user's)"),
    "F-L8a-W1": (1, 1, 3, "absent", "running"),
    "F-L8a-W1b": (2, 2, 5, "absent", "running"),
    "F-L8b-W2": (2, 1, 3, "absent", "running"),
    "F-L8c-W4": (2, 2, 4, "absent", "running"),
    "F-L8d": (1, 0, 2, "entries=[], owner=third-party-owner (byte-unchanged)", "paused"),
    "F-L8g-UNKNOWN": (0, 0, 1, "ledger sha256 unchanged", "running"),
    "F-L8h-WRITEFAIL": (0, 0, 0, "refcount path still a directory", "running"),
    "F-LK-TIMEOUT": (0, 0, 0, "absent", "running"),
    "F-LK-TIMEOUT-ZERO": (0, 0, 1, "absent", "running"),
    "F-LK-HOLDER-CRASH": (0, 0, 0, "absent", "running"),
    "F-LK-NEVER-UNLINK": (2, 2, 4, "absent, lock file present 0 bytes", "running"),
}

REQUIRED = ("card_id attempt_id status completed_steps next_step_number next_action "
            "input_hashes current_source_hashes changed_paths commands_executed raw_exit_codes "
            "expected_exit_codes open_questions blocked_by evidence_paths reviewer_status "
            "carries_disposition measured_results not_granted production_read_only_evidence "
            "produces").split()

fails = []
with open(os.path.join(A, "handoff.json"), encoding="utf-8") as fh:
    d = json.load(fh)

for key in REQUIRED:
    if key not in d:
        fails.append("handoff.json missing required key: " + key)

if d.get("status") != "review_pending":
    fails.append("handoff.json status is not review_pending: " + repr(d.get("status")))

if len(d.get("completed_steps", [])) != 9:
    fails.append("completed_steps is not the nine START_HERE steps: %d" % len(d.get("completed_steps", [])))

if len(d.get("carries_disposition", {})) != 9:
    fails.append("carries_disposition does not have 9 entries")

if len(d.get("measured_results", {}).get("cases", [])) != 19:
    fails.append("measured_results.cases is not 19 entries")

for case in d.get("measured_results", {}).get("cases", []):
    name = case["case"]
    got = (case["pause_calls"], case["resume_calls"], case["lock_acquisitions"],
           case["final_ledger"], case["worker"])
    if name not in FACTS:
        fails.append("unknown case in handoff.json: " + name)
    elif FACTS[name] != got:
        fails.append("case %s mismatch: FACTS=%r handoff=%r" % (name, FACTS[name], got))

if len(d.get("raw_exit_codes", [])) != len(d.get("commands_executed", [])):
    fails.append("raw_exit_codes length != commands_executed length")
if len(d.get("expected_exit_codes", [])) != len(d.get("commands_executed", [])):
    fails.append("expected_exit_codes length != commands_executed length")

outside = [p for p in d.get("changed_paths", [])
           if not p.startswith("execution_runs/I-04-D/a20260919-01/")]
if outside:
    fails.append("changed_paths outside the attempt: %r" % outside)

mismatch = [(r, e) for r, e in zip(d["raw_exit_codes"], d["expected_exit_codes"]) if r != e]
if mismatch != [(1, 0)]:
    fails.append("expected exactly one raw/expected mismatch (green run): %r" % (mismatch,))

# the FACTS numbers that must be stated plainly in review.md
review = open(os.path.join(A, "review.md"), encoding="utf-8").read()
for needle in ("18 passed, 3 failed", "17 failed, 2 passed, 2 skipped in 14.59s",
               "变异证明没有跑", "dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c",
               "5ac2a50a847c62a066fe1984aae6c4e30b593ff674b67b3cb618cacc8e66a436",
               "18 passed / 3 failed"):
    if needle not in review:
        fails.append("review.md missing statement: " + needle)
if "verdict:                      (empty" not in review:
    fails.append("review.md verdict field is not empty")

recovery = open(os.path.join(A, "recovery", "README.md"), encoding="utf-8").read()
for needle in ("dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c",
               "patch_i04d.py --apply", "summary.json", "PLAN/reviews",
               "runs<pid>"):
    if needle not in recovery:
        fails.append("recovery/README.md missing: " + needle)

print("checks run against", A)
if fails:
    print("FAIL (%d)" % len(fails))
    for item in fails:
        print("  -", item)
    sys.exit(1)
print("ALL CHECKS PASS")
