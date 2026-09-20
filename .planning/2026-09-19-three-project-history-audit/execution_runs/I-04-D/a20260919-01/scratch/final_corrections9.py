"""Last two assertion corrections."""

from __future__ import annotations

import pathlib
import re
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
text = TEST.read_text(encoding="utf-8")

# 1) F-L8a-W1b: B reclaimed A's orphan and completed its own cycle, and C opened a
#    second one, so there are two pauses and two resumes; the invariant is that the
#    world ends clean and nobody read the crash as a user pause.
text, n1 = re.subn(
    r'    assert third\["resume_calls"\] == 1, third\["worker"\]\["events"\]\n',
    '    assert third["resume_calls"] == 2, third["worker"]["events"]\n'
    '    assert third["pause_calls"] == 2, third["worker"]["events"]\n',
    text,
)

# 2) F-L6b: sample the overlap from the scheduler's parked snapshot
OLD = '''    joined = reports["B"]["after_enter"]
    assert len(joined["lease_set"]) == 2, joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert reports["B"]["lease_id"] in joined["lease_set"], joined'''
NEW = '''    joined = s["participants"]["b_joined"]["lease"]
    assert len(joined["lease_set"]) == 2, joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert reports["B"]["lease_id"] in joined["lease_set"], joined'''
if OLD in text:
    text = text.replace(OLD, NEW, 1)
    print("F-L6b snapshot switched to the parked sample")
else:
    print("F-L6b block not found verbatim; dumping")
    index = text.find("def test_f_l6b_exactly")
    print(text[index : index + 1800])
    sys.exit(1)

print(f"W1b resume/pause counts updated: {n1}")
TEST.write_text(text, encoding="utf-8")
