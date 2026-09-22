"""DW15-REPAIR conftest: bind this pytest run to ONE variant tree.

DW15_VARIANT points at a directory that CONTAINS the `company_wiki` package:
  iso/baseline   -> pristine original scripts (RED run)
  iso/fixed      -> repaired scripts (GREEN run)
  mutants/mN     -> one defect-fix reverted (mutation run)

Nothing else may be on sys.path ahead of the variant; the product repos are
never imported from their checkouts.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

VARIANT = os.environ.get("DW15_VARIANT")
if not VARIANT:
    raise SystemExit(
        "DW15_VARIANT not set: expected iso/baseline | iso/fixed | mutants/mN")
variant_path = Path(VARIANT).resolve()
if not (variant_path / "company_wiki").is_dir():
    raise SystemExit(f"DW15_VARIANT has no company_wiki package: {variant_path}")

# variant tree first; harness second (fixtures).
sys.path.insert(0, str(variant_path))
harness = Path(__file__).resolve().parent.parent / "harness"
if str(harness) not in sys.path:
    sys.path.insert(1, str(harness))
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
