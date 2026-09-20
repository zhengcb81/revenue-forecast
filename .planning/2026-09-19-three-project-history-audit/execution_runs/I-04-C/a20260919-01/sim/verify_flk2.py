"""Independent recompute of the F-LK2 truth (round-4 carry condition C1).

Why this file exists
--------------------
The round-2 review carried a condition (C1): two documents still quoted a STALE
F-LK2 group (`finals [12, 19, 7, 26, 43] => lost_updates [197, 185, 191, 198, 14]`)
while the final evidence round recorded a different group.  Before correcting any
text, the truth must be recomputed from the evidence instead of copied from prose.

Two independent sources are used here:

  SOURCE A (raw run artifacts, not written by hand):
    evidence/run/F-LK2-r{1..5}/counter.txt              -> the final counter value
    evidence/run/F-LK2-r{1..5}/payload.{0..7}.json      -> processes, rounds, use_lock
    evidence/run/F-LK2-r{1..5}/counter.journal.jsonl    -> per-process lock_acquisitions
  SOURCE B (the frozen evidence record):
    evidence/lock-and-legacy.txt, the `--- F-LK2 ---` record

The expected total is processes * rounds and `lost_updates = expected - final`
(sim/stress.py::stress_counter computes exactly that).  This script recomputes
every field of SOURCE B from SOURCE A and additionally checks the arithmetic
inside SOURCE B, and shows why the stale group cannot come from any 200-target
evidence line.

Usage (Windows PowerShell, ASCII stdout):
  & $PY -B sim/verify_flk2.py                # writes evidence/flk2-recompute.txt
  & $PY -B sim/verify_flk2.py --print        # stdout only

Exit code 0 = the evidence record is exactly reproducible from the raw runs.
"""

from __future__ import annotations

import io
import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ATTEMPT, "evidence")
RECORD_FILE = os.path.join(EVIDENCE, "lock-and-legacy.txt")
RUN_DIR = os.path.join(EVIDENCE, "run")
ROUNDS = 5
STALE_FINALS = [12, 19, 7, 26, 43]
STALE_LOST = [197, 185, 191, 198, 14]

out_lines = []


def say(text=""):
    out_lines.append(text)


def load_record():
    """SOURCE B: find and parse the F-LK2 record line."""
    lines = io.open(RECORD_FILE, encoding="utf-8").read().splitlines()
    for index, line in enumerate(lines, 1):
        if line.startswith('{"case": "F-LK2"'):
            return index, json.loads(line)
    raise SystemExit("F-LK2 record not found in " + RECORD_FILE)


def load_raw(round_index):
    """SOURCE A: recompute one round from the raw run directory."""
    base = os.path.join(RUN_DIR, "F-LK2-r%d" % round_index)
    if not os.path.isdir(base):
        raise SystemExit("missing run dir " + base)
    with io.open(os.path.join(base, "counter.txt"), encoding="utf-8") as handle:
        final = int(handle.read().strip() or "0")
    payloads = []
    for name in sorted(os.listdir(base)):
        if name.startswith("payload.") and name.endswith(".json"):
            with io.open(os.path.join(base, name), encoding="utf-8") as handle:
                payloads.append(json.load(handle))
    rounds = sorted({int(p["rounds"]) for p in payloads})
    use_lock = sorted({bool(p.get("use_lock", True)) for p in payloads})
    acquisitions = []
    with io.open(os.path.join(base, "counter.journal.jsonl"), encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                acquisitions.append(json.loads(line))
    expected = len(payloads) * (rounds[0] if len(rounds) == 1 else -1)
    return {
        "case": "F-LK2-r%d" % round_index,
        "final": final,
        "processes": len(payloads),
        "rounds": rounds,
        "use_lock": use_lock,
        "participants_with_rounds": len(acquisitions),
        "rounds_reported": sorted({int(a["rounds"]) for a in acquisitions}),
        "lock_acquisitions_total": sum(int(a["lock_acquisitions"]) for a in acquisitions),
        "expected": expected,
        "lost_updates": expected - final,
    }


def main():
    say("F-LK2 RECOMPUTE (round-4 carry condition C1) - independent of prose")
    say("generated_by: sim/verify_flk2.py")
    say("command: & $PY -B sim/verify_flk2.py   (run from the attempt root)")
    say("source_A: evidence/run/F-LK2-r{1..5}/ (counter.txt, payload.*.json, counter.journal.jsonl)")
    say("source_B: evidence/lock-and-legacy.txt")
    say("")

    record_line, record = load_record()
    say("SOURCE B: evidence/lock-and-legacy.txt line %d is the F-LK2 record" % record_line)
    say("  case=%s expected=%s processes=%s rounds=%s status=%s"
        % (record["case"], record["expected"], record["processes"], record["rounds"],
           record["status"]))
    say("  record finals            = %s" % json.dumps(record["finals"]))
    say("  record lost_updates      = %s" % json.dumps(record["lost_updates"]))
    say("  record lost_updates_range= %s" % json.dumps(record["lost_updates_range"]))
    say("  record determinism       = %s" % record["determinism"])
    say("")

    raw = [load_raw(i) for i in range(1, ROUNDS + 1)]
    say("SOURCE A: recomputed from the raw run directories")
    say("  %-10s %6s %4s %6s %6s %6s %6s %6s %6s"
        % ("round", "final", "proc", "rounds", "useLk", "parts", "acq", "expect", "lost"))
    for item in raw:
        say("  %-10s %6d %4d %6s %6s %6d %6d %6d %6d"
            % (item["case"], item["final"], item["processes"],
               ",".join(str(r) for r in item["rounds"]),
               ",".join(str(v).lower() for v in item["use_lock"]),
               item["participants_with_rounds"], item["lock_acquisitions_total"],
               item["expected"], item["lost_updates"]))
    say("")

    checks = []

    raw_finals = [item["final"] for item in raw]
    raw_lost = [item["lost_updates"] for item in raw]
    raw_range = [min(raw_lost), max(raw_lost)]
    raw_expected = sorted({item["expected"] for item in raw})

    checks.append(("A1 raw finals match the recorded `runs[].final`",
                   raw_finals == [run["final"] for run in record["runs"]],
                   "raw=%s record_runs=%s" % (json.dumps(raw_finals),
                                              json.dumps([r["final"] for r in record["runs"]]))))
    checks.append(("A2 raw finals match the recorded top-level `finals`",
                   raw_finals == record["finals"], json.dumps(raw_finals)))
    checks.append(("A3 raw lost_updates match the recorded `lost_updates`",
                   raw_lost == record["lost_updates"], json.dumps(raw_lost)))
    checks.append(("A4 raw lost range matches the recorded `lost_updates_range`",
                   raw_range == record["lost_updates_range"], json.dumps(raw_range)))
    checks.append(("A5 expected total is one value and equals processes*rounds",
                   len(raw_expected) == 1 and raw_expected[0] == record["expected"],
                   "raw_expected=%s record_expected=%s" % (json.dumps(raw_expected),
                                                           record["expected"])))
    checks.append(("A6 every raw round is the no-lock control (use_lock=false)",
                   all(item["use_lock"] == [False] for item in raw),
                   json.dumps([item["use_lock"] for item in raw])))
    checks.append(("A7 no lock was taken in any round (control holds)",
                   all(item["lock_acquisitions_total"] == 0 for item in raw),
                   json.dumps([item["lock_acquisitions_total"] for item in raw])))
    checks.append(("A8 each round has processes participants all reporting rounds",
                   all(item["processes"] == record["processes"]
                       and item["participants_with_rounds"] == record["processes"]
                       and item["rounds_reported"] == [record["rounds"]]
                       for item in raw),
                   json.dumps([[item["processes"], item["participants_with_rounds"],
                                item["rounds_reported"]] for item in raw])))
    checks.append(("B1 record arithmetic: lost_updates == expected - finals (elementwise)",
                   record["lost_updates"] == [record["expected"] - f for f in record["finals"]],
                   json.dumps(record["lost_updates"])))
    checks.append(("B2 record arithmetic: lost_updates_range == [min, max] of lost_updates",
                   record["lost_updates_range"] == [min(record["lost_updates"]),
                                                    max(record["lost_updates"])],
                   json.dumps(record["lost_updates_range"])))
    checks.append(("B3 record determinism field says NOT deterministic (qualitative claim)",
                   record["determinism"].startswith("NOT deterministic"),
                   record["determinism"][:60]))
    checks.append(("B4 every recorded run has lock_acquisitions == 0",
                   all(run["lock_acquisitions"] == 0 for run in record["runs"]),
                   json.dumps([run["lock_acquisitions"] for run in record["runs"]])))

    stale_lost_from_finals = [record["expected"] - f for f in STALE_FINALS]
    checks.append(("C1 the STALE group printed in decision.md 13.5 / review.md P3-4 is NOT "
                   "reproducible: 200 - [12,19,7,26,43] != [197,185,191,198,14]",
                   stale_lost_from_finals != STALE_LOST
                   and STALE_FINALS != record["finals"],
                   "200-stale_finals=%s stale_lost=%s" % (json.dumps(stale_lost_from_finals),
                                                          json.dumps(STALE_LOST))))

    say("RECOMPUTE CHECKS")
    failed = 0
    for name, ok, detail in checks:
        if not ok:
            failed += 1
        say("  [%s] %s" % ("PASS" if ok else "FAIL", name))
        say("         detail: %s" % detail)
    say("")

    say("STALE VS EVIDENCE")
    say("  stale (still printed in decision.md 13.5 and review.md 1/P3-4):")
    say("    finals       = %s" % json.dumps(STALE_FINALS))
    say("    lost_updates = %s" % json.dumps(STALE_LOST))
    say("    => 200 - finals = %s  (equals the printed lost_updates? %s)"
        % (json.dumps(stale_lost_from_finals), stale_lost_from_finals == STALE_LOST))
    say("  evidence truth (SOURCE A == SOURCE B):")
    say("    finals       = %s" % json.dumps(raw_finals))
    say("    lost_updates = %s" % json.dumps(raw_lost))
    say("    lost_updates_range = %s" % json.dumps(raw_range))
    say("    => 200 - finals = %s  (equals lost_updates? %s)"
        % (json.dumps([200 - f for f in raw_finals]), [200 - f for f in raw_finals] == raw_lost))
    say("  same group? %s" % (raw_finals == STALE_FINALS))
    say("")

    verdict = (failed == 0)
    say("VERDICT: %s  (%d/%d checks passed)"
        % ("RECORD REPRODUCED FROM RAW EVIDENCE" if verdict else "MISMATCH - DO NOT CORRECT TEXT",
           len(checks) - failed, len(checks)))
    say("TRUTH: finals %s => lost_updates %s (range %s), expected %d, %d processes x %d rounds"
        % (json.dumps(raw_finals), json.dumps(raw_lost), json.dumps(raw_range),
           record["expected"], record["processes"], record["rounds"]))
    say("CONFLICT WITH THE BRIEF: none (the brief's group %s equals the recomputed group)"
        % json.dumps([16, 35, 10, 56, 18]) if raw_finals == [16, 35, 10, 56, 18]
        else "CONFLICT WITH THE BRIEF: recomputed %s != brief [16, 35, 10, 56, 18]"
             % json.dumps(raw_finals))

    text = "\n".join(out_lines) + "\n"
    target = os.path.join(EVIDENCE, "flk2-recompute.txt")
    with io.open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    if "--print" in sys.argv:
        sys.stdout.write(text.encode("ascii", "backslashreplace").decode("ascii"))
    else:
        sys.stdout.write("wrote %s\n" % os.path.relpath(target, ATTEMPT))
        sys.stdout.write(("VERDICT: %s\n" % ("OK" if verdict else "MISMATCH")))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
