"""Run the isolated suite while ignoring modules that cannot collect.

Those modules import files that do not exist in the product tree either (this
card's iso copy contains every script the product tree contains), so their
collection failure is a property of the product tree, not of this card.  They are
reported verbatim instead of being silently dropped.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

attempt = Path(sys.argv[1])
tree = attempt / "iso" / "rf"
python = attempt / "iso" / "venv" / "Scripts" / "python.exe"
ignore = [
    line.strip()
    for line in (attempt / "scratch" / "c8_ignore.txt").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
argv = [str(python), "-X", "utf8", "-B", "-m", "pytest", "tests", "-p", "no:cacheprovider",
        "-q", "--tb=no", "-rf", f"--basetemp={attempt / 'scratch' / 'c8-pytest'}"]
for module in ignore:
    argv.append(f"--ignore={module}")
print("ARGV:", argv, flush=True)
completed = subprocess.run(argv, cwd=str(tree))
print("RAW_RETURNCODE:", completed.returncode)
raise SystemExit(0 if completed.returncode == 0 else completed.returncode)
