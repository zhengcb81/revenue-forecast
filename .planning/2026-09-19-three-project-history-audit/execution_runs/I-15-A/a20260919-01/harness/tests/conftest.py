"""I-15-A harness conftest: make the attempt's own helper modules importable."""

from __future__ import annotations

import os
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

ATTEMPT = HARNESS.parent
os.environ.setdefault("I15A_ATTEMPT", str(ATTEMPT))
