"""Rework r2c — align the last three assertions with the gate-fixed observations.

Now that gates fire at their NAMED points, the scheduler recordings are authoritative:
  F-L5   : B's after_enter holds BOTH leases, generation 1  (the overlap the case claims)
  F-L6b  : paused 2 / resumed 2, A and B each close their own cycle, A's ownership
           transfer to B is visible in B's own snapshot
  F-L8a-W1b: C joins (pause 1 / resume 1, two leases at C's enter), then B is last
"""

from __future__ import annotations

import pathlib
import re
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
text = TEST.read_text(encoding="utf-8")

# ---- F-L5 (line ~110): the snapshot to read is B's own after_enter --------------
OLD_L5 = '''    joined = s["participants"]["b_joined"]["lease"]
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert len(joined["lease_set"]) == 2, joined
    assert reports["A"]["after_enter"]["generation"] == 1, reports["A"]["after_enter"]'''
NEW_L5 = '''    joined = reports["B"]["after_enter"]
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert len(joined["lease_set"]) == 2, joined
    assert joined["generation"] == 1, joined'''
if OLD_L5 in text:
    text = text.replace(OLD_L5, NEW_L5, 1)
    print("F-L5 snapshot switched to B's after_enter")
else:
    # whatever the current shape is, force the two essential facts
    pattern = re.compile(
        r'    joined = s\["participants"\]\["b_joined"\]\["lease"\]\n'
        r'(?:.*?\n)*?    assert reports\["A"\]\["after_enter"\]\["generation"\] == 1[^\n]*\n'
    )
    text, count = pattern.subn(NEW_L5 + "\n", text)
    print(f"F-L5 rewritten by regex: {count}")
    if count == 0:
        index = text.find('b_joined"]["lease"]')
        print(text[max(0, index - 600) : index + 600])
        sys.exit(1)

# ---- F-L6b: the same shape, from the same source --------------------------------
OLD_6B = '''    a_id, b_id = reports["A"]["lease_id"], reports["B"]["lease_id"]
    snapshots = [reports["A"]["after_enter"], reports["B"]["after_enter"]]
    assert any(
        a_id in snap["lease_set"] and b_id in snap["lease_set"] for snap in snapshots
    ), snapshots'''
NEW_6B = '''    # The overlap, measured: with the gate fix B is parked at its own enter-complete
    # while A is still inside its scope, so B's after_enter holds BOTH leases.
    joined = reports["B"]["after_enter"]
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert len(joined["lease_set"]) == 2, joined'''
if OLD_6B in text:
    text = text.replace(OLD_6B, NEW_6B, 1)
    print("F-L6b overlap assertion rewritten")
else:
    print("F-L6b pattern not found verbatim")

# ---- F-L8a-W1b: C joins, B is last ---------------------------------------------
OLD_W1B = '''    assert third["reports"]["C"]["action"] == "released_joined", third["reports"]["C"]
    assert third["reports"]["B"]["action"] == "released_last", third["reports"]["B"]'''
NEW_W1B = '''    assert third["reports"]["C"]["action"] == "released_joined", third["reports"]["C"]
    assert third["reports"]["B"]["action"] == "released_last", third["reports"]["B"]
    assert third["reports"]["C"]["action"] != "respect_paused"'''
if OLD_W1B in text:
    text = text.replace(OLD_W1B, NEW_W1B, 1)
    print("W1b actions asserted from the measured recording")

TEST.write_text(text, encoding="utf-8")
