"""Shared fixtures: make the ``uc`` package importable from the tests dir."""

import sys
from pathlib import Path

UC_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]

if str(UC_DIR) not in sys.path:
    sys.path.insert(0, str(UC_DIR))
