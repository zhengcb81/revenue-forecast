"""Generate changes.diff from before-copies vs current files (no git)."""
import difflib
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
ATTP = RF / ".planning/2026-09-19-three-project-history-audit/execution_runs/RF-E2E-ADAPT/a20260923-01"
BEFORE = ATTP / "diffs" / "before"
RELATIVE = [
    "tests/e2e_support/isolated_lake.py",
    "tests/test_preparation_e2e_success.py",
    "tests/test_zr709_zijin_journey.py",
    "tests/test_zr803_chaos_recovery.py",
]

out = []
for rel in RELATIVE:
    old = (BEFORE / rel).read_text(encoding="utf-8").splitlines(keepends=True)
    new = (RF / rel).read_text(encoding="utf-8").splitlines(keepends=True)
    diff = difflib.unified_diff(
        old, new,
        fromfile=f"a/{rel} (before, sha-pinned in binding.md)",
        tofile=f"b/{rel}",
    )
    out.extend(diff)
(ATTP / "changes.diff").write_text("".join(out), encoding="utf-8")
print(f"wrote {ATTP / 'changes.diff'} ({sum(1 for _ in open(ATTP / 'changes.diff', encoding='utf-8'))} lines)")
