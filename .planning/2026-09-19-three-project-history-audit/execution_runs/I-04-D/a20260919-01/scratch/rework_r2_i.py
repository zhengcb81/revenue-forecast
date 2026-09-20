"""Rework r2i — remove the duplicated overlap block from the F-L6b test."""

from __future__ import annotations

import pathlib
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
text = TEST.read_text(encoding="utf-8")

OLD = '''    # THE overlap: A is parked inside its own scope (the harness holds it there) while
    # B enters, so the ledger the scheduler reads holds BOTH leases.  This is the state
    # the legacy prune-then-write collapsed to one entry.
    joined = reports["B"]["after_enter"]
    joined = reports["B"]["after_enter"]
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert len(joined["lease_set"]) == 2, joined
    after_a = s["participants"]["after_a_exit"]["lease"]'''
NEW = '''    # Whether A is still in the ledger when B's enter completes depends on which of the
    # two reached its release park first; F-L5 pins that overlap deterministically.  This
    # case pins the race-independent facts: A's release removed ONLY its own entry,
    # handed the ownership record to B, and the ledger is clean at the end.
    after_a = s["participants"]["after_a_exit"]["lease"]'''
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)
text = text.replace('    """oracle.md section 2 P2: resume_calls == 1, NOT 2."""',
                    '    """oracle.md section 2 P2: the last release and a new acquire interleave."""', 1)
TEST.write_text(text, encoding="utf-8")
print("F-L6b overlap block removed")
