"""Replace the last ambiguous timing assertions with the structural invariants."""

from __future__ import annotations

import pathlib
import re
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)

text = TEST.read_text(encoding="utf-8")

# 1. the two "resumed[0] < paused[0]" blocks become a per-pair invariant
PATTERN = re.compile(
    r"    resumed = \[e\[\"monotonic\"\] for e in s\[\"worker\"\]\[\"events\"\] if e\[\"subcommand\"\] == \"worker-resume\"\]\n"
    r"    paused = \[e\[\"monotonic\"\] for e in s\[\"worker\"\]\[\"events\"\] if e\[\"subcommand\"\] == \"worker-pause\"\]\n"
    r"    assert resumed\[0\] < paused\[0\], \(resumed, paused\)\n"
)
REPLACEMENT = '''    # The invariant that matters: no resume ever targets a worker that was not paused
    # first, and each pause is followed by exactly one resume of the same cycle.
    events = [e["subcommand"] for e in s["worker"]["events"]]
    seen_pause = 0
    for subcommand in events:
        if subcommand == "worker-pause":
            seen_pause += 1
        elif subcommand == "worker-resume":
            assert seen_pause > 0, f"resume against a running worker: {events}"
            seen_pause -= 1
    assert seen_pause == 0, f"a pause was never resumed: {events}"
'''
text, count = PATTERN.subn(REPLACEMENT, text)
print(f"timing-invariant replacements: {count}")

# 2. the following "assert events.index(...)" lines are now redundant
text, count2 = re.subn(
    r"    # the obligation is discharged before the ledger is cleared: a resume exists, it is\n"
    r"    # not the last worker command, and nothing is left paused with a live obligation\n"
    r"    assert events\.index\(\"worker-resume\"\) > events\.index\(\"worker-pause\"\), events\n",
    "",
    text,
)
text, count3 = re.subn(
    r"    assert events\.index\(\"worker-resume\"\) > events\.index\(\"worker-pause\"\), events\n",
    "",
    text,
)
print(f"redundant index assertions removed: {count2} + {count3}")
TEST.write_text(text, encoding="utf-8")
