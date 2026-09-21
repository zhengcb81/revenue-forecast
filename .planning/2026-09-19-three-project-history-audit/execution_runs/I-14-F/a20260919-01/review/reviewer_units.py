"""Reviewer tool: read the REAL parametrized case values out of the added unit test
(via pytest collection, not by re-typing the literals) and re-derive the criterion.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
TEST_FILE = ATTEMPT / "iso" / "tree" / "tests" / "contract" / "test_short_basetemp_convention.py"

spec = importlib.util.spec_from_file_location("cw_unit_under_review", TEST_FILE)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules["cw_unit_under_review"] = mod
spec.loader.exec_module(mod)

conftest = mod.conftest
print(f"shipped constants: WIN32_PATH_LIMIT={conftest.WIN32_PATH_LIMIT} "
      f"GENERATION_RESERVE={conftest.GENERATION_RESERVE} "
      f"BASETEMP_MAX_CHARS={conftest.BASETEMP_MAX_CHARS}")
print(f"arithmetic: {conftest.WIN32_PATH_LIMIT} - {conftest.GENERATION_RESERVE} "
      f"= {conftest.WIN32_PATH_LIMIT - conftest.GENERATION_RESERVE}")
print()
marks = getattr(mod.test_criterion_table, "pytestmark", [])
cases = []
for mark in marks:
    if mark.name == "parametrize":
        cases = mark.args[1]
        break
print(f"{'#':>2} {'cwd_len':>7} {'bt_len':>6} {'relocate':>8} {'expected':>8}  {'match':>5}  comment")
bad = 0
for i, (cwd, requested, expected) in enumerate(cases, 1):
    resolved = conftest.resolve_basetemp(cwd, requested)
    got = conftest.needs_short_path_fallback(cwd, requested)
    ok = got is expected
    bad += 0 if ok else 1
    print(f"{i:>2} {len(str(cwd)):>7} {len(str(resolved)):>6} {str(got):>8} {str(expected):>8}  "
          f"{'OK' if ok else 'MISMATCH':>5}")
print(f"\nmismatches: {bad}")
print("boundary sweep around the shipped threshold:")
for n in (84, 85, 86, 87, 88):
    print(f"  basetemp_len={n:3d} -> relocate={conftest.needs_short_path_fallback('C:\\\\x', 'C:\\\\' + 'z' * (n - 3))}"
          f"   (unrouted max generated = child {n + 125}, logon {n + 150})")
