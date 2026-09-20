"""Mutation evidence for the round-5 assertion strengthening (closeout erratum E2).

The closeout review found that F-T4's refcount check contained a CHAINED COMPARISON
(`lease in successful_ids is False` => `(lease in successful_ids) and
(successful_ids is False)`, never True), so `not any(...)` was vacuously True and
could never fail; and that the "queue wait is reported" check was called with a
literal `True` (a recorder, not an assertion).

This script does NOT re-state the shipped expressions by hand.  It extracts them
from the CURRENT sim/cases_timeout.py (so the mutation test always evaluates the
shipped source), evaluates the historical (pre-r5) expression as well, and shows
for every affected check: the healthy scenario is green, and an injected wrong
entry / broken reporter turns the CURRENT clause RED while the historical clause
stays GREEN -- that gap is the defect being closed.

Output: evidence/r5-assertion-mutation.txt   Exit 0 = every expectation held.

Run:  & $PY -B sim/verify_r5_assertions.py
"""

from __future__ import annotations

import io
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ATTEMPT, "sim", "cases_timeout.py")
TARGET = os.path.join(ATTEMPT, "evidence", "r5-assertion-mutation.txt")

REFCOUNT_LABEL = "no timed-out participant ever appears in the refcount"
WAIT_LABEL = "the queue wait is reported (the download budget it consumed)"
WINNERS_LABEL = "the winners plus joiners are exactly the non-timed-out ones"

# The pre-r5 expressions, verbatim from the reviewed revision (round-4 bytes).
OLD_REFCOUNT = ('not any(lease in successful_ids is False for lease in view["entries"])\n'
                'and all(lease in successful_ids for lease in view["entries"])\n'
                'and view["entries"] != []')
OLD_REFCOUNT_SUBCLAUSE = 'not any(lease in successful_ids is False for lease in view["entries"])'
OLD_WAIT = "True"
OLD_WINNERS = "len(winners) + len(joiners) == len(succeeded)"

out = []


def say(text=""):
    out.append(text)


def extract_expression(text, label):
    """Return the boolean expression of `h.check("<label>", <expr>, json.dumps(...))`."""
    lines = text.split("\n")
    head = None
    for index, line in enumerate(lines):
        if ('"' + label + '",') in line:
            head = index
            break
    if head is None:
        raise SystemExit("check label not found in sim/cases_timeout.py: " + label)
    remainder = lines[head].split('"' + label + '",', 1)[1]
    body = []
    if remainder.strip():
        body.append(remainder)
    for line in lines[head + 1:]:
        if line.strip().startswith("json.dumps("):
            break
        body.append(line)
    expression = "\n".join(body).strip().rstrip(",").rstrip()
    if not expression:
        raise SystemExit("empty expression extracted for: " + label)
    return expression


def evaluate(expression, namespace):
    # Parenthesise: the shipped expressions use implicit line continuation inside
    # the h.check(...) call, and the extracted text has no surrounding parentheses.
    return bool(eval("(" + expression + ")", dict(namespace)))  # noqa: S307


ENVELOPES = {
    "P0": {"action": "paused_by_us", "lock_wait": 0.0},
    "P2": {"action": "joined", "lock_wait": 0.571},
    "P1": {"action": "lease_fail_closed", "code": "lease_lock_timeout", "writes": 0},
    "P3": {"action": "lease_fail_closed", "code": "lease_lock_timeout", "writes": 0},
    "P4": {"action": "lease_fail_closed", "code": "lease_lock_timeout", "writes": 0},
    "P5": {"action": "lease_fail_closed", "code": "lease_lock_timeout", "writes": 0},
}


def scenario(**overrides):
    base = {
        "tags": ["P0", "P1", "P2", "P3", "P4", "P5"],
        "timed_out": ["P1", "P3", "P4", "P5"],
        "succeeded": ["P0", "P2"],
        "winners": ["P0"],
        "joiners": ["P2"],
        "budget": 1.0,
        "hold": 0.4,
        "successful_ids": {"L0", "L2"},
        "timed_out_ids": {"L1", "L3", "L4", "L5"},
        "view": {"entries": ["L0", "L2"]},
        "envelopes": dict(ENVELOPES),
    }
    base.update(overrides)
    base["wait_seconds"] = {
        tag: round(base["envelopes"][tag].get("lock_wait") or 0.0, 3)
        for tag in base["succeeded"]
    }
    return base


def main():
    source = io.open(SOURCE, encoding="utf-8").read()
    current = {
        "refcount": extract_expression(source, REFCOUNT_LABEL),
        "wait": extract_expression(source, WAIT_LABEL),
        "winners": extract_expression(source, WINNERS_LABEL),
    }

    results = []

    def expect(name, expression, namespace, wanted):
        value = evaluate(expression, namespace)
        results.append((value is wanted, name, wanted, value))
        return value

    say("ROUND-5 ASSERTION MUTATION EVIDENCE (closeout erratum E2)")
    say("generated_by: sim/verify_r5_assertions.py")
    say("the CURRENT expressions below are extracted from sim/cases_timeout.py, not retyped")
    say("")
    say("EXTRACTED FROM THE SHIPPED SOURCE")
    for key in ("winners", "refcount", "wait"):
        say("  [%s]" % key)
        for line in current[key].split("\n"):
            say("      " + line)
    say("")

    say("MUTATION 1a - the historical SUB-CLAUSE asserts nothing (chained comparison)")
    say("  the sub-clause reads like 'no foreign lease in the refcount', but evaluates to a")
    say("  constant: `lease in successful_ids is False` == `(lease in successful_ids) and")
    say("  (successful_ids is False)`, and `successful_ids is False` is never True.")
    vacuous_cases = [
        ("a timed-out lease (L3) is in the refcount",
         scenario(view={"entries": ["L0", "L3"]})),
        ("the refcount is empty", scenario(view={"entries": []})),
        ("a nonsense lease id is in the refcount", scenario(view={"entries": ["GARBAGE"]})),
        ("every participant is in the refcount",
         scenario(view={"entries": ["L0", "L1", "L2", "L3", "L4", "L5"]})),
    ]
    for name, namespace in vacuous_cases:
        expect("sub-clause returns True even when %s (vacuous)" % name,
               OLD_REFCOUNT_SUBCLAUSE, namespace, True)
    say("  -> %d/%d scenarios returned True: the sub-clause can never fail"
        % (len(vacuous_cases), len(vacuous_cases)))
    say("")

    say("MUTATION 1b - the historical WHOLE clause has a blind spot the repaired one closes")
    say("  the old conjunct 2 (`all(lease in successful_ids ...)`) only catches a stray lease")
    say("  while `succeeded` and `timed_out` stay disjoint.  If the classification ever puts a")
    say("  timed-out participant into `succeeded` too, the old clause passes:")
    partition_broken = scenario(succeeded=["P0", "P2", "P3"], timed_out=["P1", "P3", "P4", "P5"],
                                successful_ids={"L0", "L2", "L3"},
                                timed_out_ids={"L1", "L3", "L4", "L5"},
                                view={"entries": ["L0", "L3"]})
    old = expect("historical WHOLE clause stays GREEN although a timed-out lease (L3) is in "
                 "the refcount (blind spot)", OLD_REFCOUNT, partition_broken, True)
    new = expect("repaired explicit quantifier turns RED on the same view",
                 current["refcount"], partition_broken, False)
    say("  historical=%s  repaired=%s" % (old, new))
    say("")
    expect("repaired clause is GREEN on the healthy view",
           current["refcount"], scenario(), True)
    expect("repaired clause turns RED on an empty refcount (entries != [] conjunct)",
           current["refcount"], scenario(view={"entries": []}), False)
    say("")

    say("MUTATION 2 - the queue-wait reporter stops emitting lock_wait")
    broken = scenario(envelopes=dict(ENVELOPES, P2={"action": "joined"}))
    old = expect("historical literal True stays GREEN (a recorder, not an assertion)",
                 OLD_WAIT, broken, True)
    new = expect("repaired clause turns RED when lock_wait is missing",
                 current["wait"], broken, False)
    say("  historical=%s  repaired=%s" % (old, new))
    say("")

    say("MUTATION 3 - the reported wait exceeds the lock budget")
    expect("repaired clause turns RED when the wait exceeds the budget",
           current["wait"],
           scenario(envelopes=dict(ENVELOPES, P2={"action": "joined", "lock_wait": 1.5})),
           False)
    expect("repaired clause is GREEN on the healthy report",
           current["wait"], scenario(), True)
    say("")

    say("MUTATION 4 - action bookkeeping double-counts and hides a third action")
    miscounted = scenario(winners=["P0", "P1"], joiners=["P1"], succeeded=["P0", "P1", "P2"])
    old = expect("historical length-only clause stays GREEN on the miscounted set "
                 "(2+1 == 3, but P2's action is unrecognised)",
                 OLD_WINNERS, miscounted, True)
    new = expect("repaired set clause turns RED on the miscounted set",
                 current["winners"], miscounted, False)
    say("  historical=%s  repaired=%s" % (old, new))
    expect("repaired set clause is GREEN on the healthy set",
           current["winners"], scenario(), True)
    expect("repaired set clause turns RED when a tag is in both winners and joiners",
           current["winners"], scenario(winners=["P0", "P2"], joiners=["P2"]), False)
    say("")

    failed = [row for row in results if not row[0]]
    say("SUMMARY: %d/%d expectations held" % (len(results) - len(failed), len(results)))
    for ok, name, wanted, value in results:
        say("  [%s] %s (expected %s, got %s)" % ("OK" if ok else "WRONG", name, wanted, value))
    verdict = not failed
    say("")
    say("VERDICT: %s"
        % ("ASSERTIONS ARE NOW FALSIFIABLE (every injected defect turns the shipped clause red)"
           if verdict else "UNEXPECTED - inspect the rows marked WRONG"))

    text = "\n".join(out) + "\n"
    with io.open(TARGET, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    sys.stdout.write("wrote %s\n" % os.path.relpath(TARGET, ATTEMPT))
    sys.stdout.write("VERDICT: %s (%d/%d)\n"
                     % ("OK" if verdict else "UNEXPECTED", len(results) - len(failed), len(results)))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
