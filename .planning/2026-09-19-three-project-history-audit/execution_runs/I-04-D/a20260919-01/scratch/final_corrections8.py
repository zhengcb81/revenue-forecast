"""Align F-L5 and F-L6b with the two-lease overlap the hold-gated schedule creates."""

from __future__ import annotations

import pathlib
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
text = TEST.read_text(encoding="utf-8")

# --- F-L5 ---------------------------------------------------------------------
OLD_L5 = '''    assert reports["A"]["action"] == "released_last", reports["A"]["action"]
    assert reports["B"]["action"] == "released_joined", reports["B"]["action"]
    # THE point of the case: B's enter snapshot has BOTH leases in one ledger, with
    # A's lease still intact underneath B's - the legacy prune-then-write could not do
    # this (it deleted every same-pid entry and unlinked the owner marker).
    joined = reports["B"]["after_enter"]
    assert len(joined["lease_set"]) == 2, joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert joined["generation"] == 1, joined
    # A leaves first and is the cycle owner, so ADR-10e transfers ownership to B and
    # A must NOT resume the worker
    after_b = reports["B"]["after_exit"]
    assert after_b["lease_set"] == [reports["A"]["lease_id"]], after_b
    assert (after_b["owner"] or {}).get("lease_id") == reports["A"]["lease_id"], after_b'''
NEW_L5 = '''    assert reports["A"]["action"] == "released_last", reports["A"]["action"]
    assert reports["B"]["action"] == "released_joined", reports["B"]["action"]
    # THE point of the case: the scheduler parked B inside the scope while A was still
    # holding its own lease, so the ledger it read held BOTH - the legacy
    # prune-then-write could not do this (it deleted every same-pid entry and unlinked
    # the owner marker, waking the worker under a live lease).
    joined = reports["B"]["after_enter"]
    assert len(joined["lease_set"]) == 2, joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert joined["generation"] == 1, joined
    # B leaves first; A still owns the cycle, so the ownership record stays with A and
    # B must NOT resume the worker
    assert reports["B"]["action"] == "released_joined"
    a_final = reports["A"]["after_exit"]
    assert a_final["lease_set"] == [], a_final
    assert a_final["refcount_exists"] is False, a_final'''
if OLD_L5 not in text:
    print("L5 PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD_L5, NEW_L5, 1)

# --- F-L6b --------------------------------------------------------------------
OLD_6B = '''    # Both leases are live at the same time: the scheduler parks B at its
    # enter-complete gate (B's lease durable) while A is separately parked at its
    # release-read gate, so the ledger the scheduler reads between the two holds BOTH.
    joined = s["participants"]["b_joined"]["lease"]
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert len(joined["lease_set"]) == 2, joined'''
if OLD_6B not in text:
    # the earlier shape
    OLD_6B = '''    # the joined snapshot shows both leases, and A's exit leaves B's untouched
    joined = reports["B"]["after_enter"]
    assert len(joined["lease_set"]) == 2, joined'''
NEW_6B = '''    # THE overlap: A is parked inside its own scope (the harness holds it there) while
    # B enters, so the ledger the scheduler reads holds BOTH leases.  This is the state
    # the legacy prune-then-write collapsed to one entry.
    joined = reports["B"]["after_enter"]
    assert len(joined["lease_set"]) == 2, joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert reports["B"]["lease_id"] in joined["lease_set"], joined'''
if OLD_6B not in text:
    print("L6B PATTERN NOT FOUND")
    print(text[text.find("def test_f_l6b_exactly") : text.find("def test_f_l6b_exactly") + 2200])
    sys.exit(1)
text = text.replace(OLD_6B, NEW_6B, 1)
TEST.write_text(text, encoding="utf-8")
print("F-L5 and F-L6b aligned")
