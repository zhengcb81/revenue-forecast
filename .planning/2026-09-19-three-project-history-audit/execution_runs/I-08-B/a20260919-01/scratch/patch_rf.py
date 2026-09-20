"""Add -rf to the two suite runners so failures are listed node by node."""

from __future__ import annotations

import sys
from pathlib import Path

attempt = Path(sys.argv[1])
full = attempt / "scratch" / "run_full_suite.py"
base = attempt / "scratch" / "run_baseline_suite.py"

text = full.read_text(encoding="utf-8")
text = text.replace('"-q", "--tb=no",', '"-q", "--tb=no", "-rf",')
full.write_text(text, encoding="utf-8", newline="")

text = base.read_text(encoding="utf-8")
text = text.replace('"-q", "--tb=no",', '"-q", "--tb=no", "-rf",')
base.write_text(text, encoding="utf-8", newline="")
print("patched")
