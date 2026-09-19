"""Unified completion control tooling (CA-001 bootstrap).

This package implements the plan-input manifest validator, the single-writer
lock protocol, compare-and-swap file updates, and the minimal machine state
that `audit_review/README.md` requires from CA-001.  It is assurance tooling,
not product code.
"""

from __future__ import annotations

__version__ = "0.1.0"
