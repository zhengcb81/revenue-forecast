"""I-14-C harness conftest: make the harness package importable, nothing else."""

from __future__ import annotations

import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))
