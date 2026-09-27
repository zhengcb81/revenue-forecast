"""Derived 3-key diagnostic (F0d): run the REAL ratchet test module's loop/`_max_complexity`
with FROZEN_MAX filtered to this card's three keys, against a given scripts tree.

The ratchet test file itself is NEVER modified; this harness imports it and re-executes
`test_frozen_files_do_not_worsen`'s exact loop over the 3 sorted keys. Labeled DERIVED
in the oracle (§6 F0d) — supplementary to the full-row scan, because the real test aborts
lexicographically at sibling-owned rows first.
Usage: python -B derived_3key.py <scripts_root>
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
TEST = RF / "tools" / "tests" / "test_complexity_ratchet.py"
spec = importlib.util.spec_from_file_location("tcr", TEST)
tcr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tcr)

SRC = Path(sys.argv[1])
MINE = ["model_registry.py", "revenue_core.py", "revenue_publication.py"]

# sanity: the real test file's frozen values for MY keys
for key in MINE:
    assert key in tcr.FROZEN_MAX, key
    print(f"frozen[{key}] = {tcr.FROZEN_MAX[key]}")

print("\n-- real-test loop over MY 3 sorted keys only --")
failures = []
for rel, frozen in sorted((k, v) for k, v in tcr.FROZEN_MAX.items() if k in MINE):
    path = SRC / rel
    assert path.is_file(), f"missing {rel}"
    actual = tcr._max_complexity(path.read_text(encoding="utf-8"))
    ok = actual <= frozen
    if not ok:
        failures.append(rel)
    print(f"  {'ok  ' if ok else 'FAIL'} {rel:30s} actual={actual:<3d} frozen={frozen}")

print(f"\nDERIVED-3KEY: {'PASS' if not failures else 'FAIL ' + str(failures)}")
sys.exit(1 if failures else 0)
