"""Apply the three remaining corrections with tolerant matching."""

from __future__ import annotations

import pathlib
import re
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
text = TEST.read_text(encoding="utf-8")

# 1) F-L6b: the both-leases sample
text, n1 = re.subn(
    r'    joined = s\["participants"\]\["b_joined"\]\["lease"\]\n'
    r'    assert len\(joined\["lease_set"\]\) == 2, joined\n',
    '    joined = s["participants"]["b_joined"]["lease"]\n'
    '    assert reports["B"]["lease_id"] in joined["lease_set"], joined\n'
    '    assert reports["A"]["lease_id"] in joined["lease_set"], joined\n'
    '    assert len(joined["lease_set"]) == 2, joined\n',
    text,
)

# 2) F-L8a-W1b: neither participant may adopt the crashed cycle as a user pause
text, n2 = re.subn(
    r'    assert third\["reports"\]\["C"\]\["action"\] == "released_last"[^\n]*\n'
    r'    assert third\["reports"\]\["B"\]\["action"\] == "released_last"[^\n]*\n'
    r'    assert third\["reports"\]\["C"\]\["action"\] != "respect_paused"\n',
    '    for tag in ("B", "C"):\n'
    '        assert third["reports"][tag]["action"] != "respect_paused", (\n'
    '            tag,\n'
    '            third["reports"][tag]["action"],\n'
    '        )\n'
    '    assert third["reports"]["B"]["action"] == "released_last", third["reports"]["B"]["action"]\n'
    '    assert third["resume_calls"] == 1, third["worker"]["events"]\n'
    '    assert third["final_lease"]["refcount_exists"] is False\n',
    text,
)

# 3) F-L8b-W2: A's crash lands before its pause, so only B's exit resumes
text, n3 = re.subn(
    r'(    assert s\["reports"\]\["B"\]\["action"\] != "respect_paused"\n)'
    r'    assert s\["pause_calls"\] == 2 and s\["resume_calls"\] == 2, s\["worker"\]\["events"\]\n',
    r'\1    assert s["pause_calls"] == 2, s["worker"]["events"]\n'
    r'    assert s["resume_calls"] == 1, s["worker"]["events"]\n',
    text,
)

print(f"applied: both-leases={n1} w1b={n2} w2={n3}")
TEST.write_text(text, encoding="utf-8")
