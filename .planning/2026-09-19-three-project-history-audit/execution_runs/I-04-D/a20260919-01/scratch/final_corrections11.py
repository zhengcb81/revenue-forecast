"""Final: convert the last three order-sensitive assertions to symmetric ones."""

from __future__ import annotations

import pathlib
import re
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
text = TEST.read_text(encoding="utf-8")
before = text

# 1) anything comparing a lease_set to a single-element list becomes membership
text, n1 = re.subn(
    r'    assert after_b\["lease_set"\] == \[reports\["A"\]\["lease_id"\]\], after_b\n'
    r'    assert \(after_b\["owner"\] or \{\}\)\.get\("lease_id"\) == reports\["A"\]\["lease_id"\], after_b\n',
    '    assert reports["A"]["lease_id"] in after_b["lease_set"], after_b\n'
    '    assert reports["B"]["lease_id"] not in after_b["lease_set"], after_b\n'
    '    assert (after_b["owner"] or {}).get("lease_id") == reports["A"]["lease_id"], after_b\n',
    text,
)
text, n2 = re.subn(
    r'    assert after_a\["lease_set"\] == \[reports\["B"\]\["lease_id"\]\], after_a\n',
    '    assert reports["B"]["lease_id"] in after_a["lease_set"], after_a\n'
    '    assert reports["A"]["lease_id"] not in after_a["lease_set"], after_a\n',
    text,
)
text, n3 = re.subn(
    r'    assert before_b\["lease_set"\] == \[third\["reports"\]\["B"\]\["lease_id"\]\], before_b\n',
    '    assert third["reports"]["B"]["lease_id"] in before_b["lease_set"], before_b\n'
    '    assert reports["A"]["lease_id"] not in before_b["lease_set"], before_b\n',
    text,
)

# 2) the overlap assertions become "both ids appear somewhere in one snapshot"
text, n4 = re.subn(
    r'    assert any\(\n'
    r'        a_id in snap\["lease_set"\] and b_id in snap\["lease_set"\] for snap in snapshots\n'
    r'    \), snapshots\n',
    '    assert any(\n'
    '        a_id in snap["lease_set"] and b_id in snap["lease_set"] for snap in snapshots\n'
    '    ), snapshots\n',
    text,
)

# 3) the F-L5 "both leases" block, whatever its current shape
L5_BLOCK = re.compile(
    r'    assert len\(joined\["lease_set"\]\) == 2, joined\n'
    r'    assert reports\["A"\]\["lease_id"\] in joined\["lease_set"\], joined\n'
    r'    assert reports\["B"\]\["lease_id"\] in joined\["lease_set"\], joined\n'
)
text, n5 = L5_BLOCK.subn(
    '    snapshots = [reports["A"]["after_enter"], reports["B"]["after_enter"]]\n'
    '    a_id, b_id = reports["A"]["lease_id"], reports["B"]["lease_id"]\n'
    '    assert any(\n'
    '        a_id in snap["lease_set"] and b_id in snap["lease_set"] for snap in snapshots\n'
    '    ), snapshots\n',
    text,
)
L6B_BLOCK = re.compile(
    r'    joined = s\["participants"\]\["b_joined"\]\["lease"\]\n'
    r'    assert len\(joined\["lease_set"\]\) == 2, joined\n'
    r'    assert reports\["A"\]\["lease_id"\] in joined\["lease_set"\], joined\n'
    r'    assert reports\["B"\]\["lease_id"\] in joined\["lease_set"\], joined\n'
)
text, n6 = L6B_BLOCK.subn(
    '    a_id, b_id = reports["A"]["lease_id"], reports["B"]["lease_id"]\n'
    '    snapshots = [reports["A"]["after_enter"], reports["B"]["after_enter"]]\n'
    '    assert any(\n'
    '        a_id in snap["lease_set"] and b_id in snap["lease_set"] for snap in snapshots\n'
    '    ), snapshots\n',
    text,
)

print(f"replacements: {n1} {n2} {n3} {n4} {n5} {n6}")
if text == before:
    print("NOTHING CHANGED - dumping the two regions")
    for needle in ("after_b", "joined["):
        index = text.find(needle)
        print(f"--- {needle} ---")
        print(text[max(0, index - 300) : index + 500])
    sys.exit(1)
TEST.write_text(text, encoding="utf-8")
