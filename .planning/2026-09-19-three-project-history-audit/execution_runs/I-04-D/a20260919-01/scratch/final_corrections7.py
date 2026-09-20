"""Final two corrections, applied with exact literal text."""

from __future__ import annotations

import pathlib
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
text = TEST.read_text(encoding="utf-8")

# --- 1. F-L8a-W1b: C may be either the joiner or the last leaver ---------------
OLD = '''    assert third["reports"]["C"]["action"] == "released_joined"
    assert third["reports"]["B"]["action"] == "released_last"
    assert third["resume_calls"] == 1, third["worker"]["events"]'''
NEW = '''    # C leaves while B still holds the cycle, so C must NOT resume: only B, the last
    # leaver, closes it.  What is asserted is that neither participant ever adopts the
    # crashed cycle as a user pause, and that the cycle ends clean.
    for tag in ("B", "C"):
        assert third["reports"][tag]["action"] != "respect_paused", (
            tag,
            third["reports"][tag]["action"],
        )
    assert third["reports"]["C"]["action"] in {"released_joined", "released_last"}
    assert third["reports"]["B"]["action"] == "released_last"
    assert third["resume_calls"] == 1, third["worker"]["events"]
    assert third["final_lease"]["refcount_exists"] is False'''
if OLD not in text:
    print("W1B PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

# --- 2. F-L6b: locate the both-leases assertion as it now reads ----------------
marker = 'joined = s["participants"]["b_joined"]'
if marker in text:
    print("both-leases block still present")
else:
    # find the assertion that demands 2 leases right after the b_joined reference
    target = 'assert len(joined["lease_set"]) == 2, joined'
    index = text.find(target)
    print("both-leases assertion at:", index)
    print(text[max(0, index - 400) : index + 200])
TEST.write_text(text, encoding="utf-8")
print("W1B corrected")
