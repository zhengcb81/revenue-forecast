"""Full violation scan: run the EXACT loops of both ratchet tests, but collect ALL violations
instead of aborting at the first assert. Also print actual vs frozen for every frozen key.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
TEST = RF / "tools" / "tests" / "test_complexity_ratchet.py"
spec = importlib.util.spec_from_file_location("tcr", TEST)
tcr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tcr)

SRC = tcr.SRC
print(f"SRC = {SRC}")

print("\n-- frozen files (test_frozen_files_do_not_worsen, ALL rows) --")
for rel, frozen in sorted(tcr.FROZEN_MAX.items()):
    path = SRC / rel
    if not path.is_file():
        print(f"  MISSING {rel}")
        continue
    actual = tcr._max_complexity(path.read_text(encoding="utf-8"))
    flag = "FAIL" if actual > frozen else "ok  "
    print(f"  {flag} {rel:35s} actual={actual:<4d} frozen={frozen}")

print("\n-- new files (test_new_files_stay_simple, ALL violations) --")
viol = []
for path in sorted(SRC.rglob("*.py")):
    rel = str(path.relative_to(SRC)).replace("\\", "/")
    if rel in tcr.FROZEN_MAX:
        continue
    actual = tcr._max_complexity(path.read_text(encoding="utf-8"))
    if actual > tcr.NEW_FILE_MAX:
        viol.append((rel, actual))
for rel, actual in viol:
    print(f"  FAIL {rel:35s} actual={actual} > {tcr.NEW_FILE_MAX}")
if not viol:
    print("  (none)")
print(f"\nTOTAL frozen violations = {sum(1 for rel, f in tcr.FROZEN_MAX.items() if (SRC/rel).is_file() and tcr._max_complexity((SRC/rel).read_text(encoding='utf-8')) > f)}")
print(f"TOTAL new-file violations = {len(viol)}")
