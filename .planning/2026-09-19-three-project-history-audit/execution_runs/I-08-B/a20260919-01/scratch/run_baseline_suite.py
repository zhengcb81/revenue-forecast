"""Baseline census with the same ignore list, for a like-for-like comparison."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

attempt = Path(sys.argv[1])
tree = attempt / "before" / "baseline_tree" / "rf"
python = attempt / "iso" / "venv" / "Scripts" / "python.exe"
ignore = [
    line.strip()
    for line in (attempt / "scratch" / "c8_ignore.txt").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
argv = [
    str(python), "-X", "utf8", "-B", "-m", "pytest", "tests",
    "-p", "no:cacheprovider", "-q", "--tb=no", "-rf",
    f"--basetemp={attempt / 'scratch' / 'c8-baseline-pytest'}",
]
for module in ignore:
    argv.append(f"--ignore={module}")
print("TREE:", tree, flush=True)
completed = subprocess.run(argv, cwd=str(tree))
print("RAW_RETURNCODE:", completed.returncode)
raise SystemExit(0)
