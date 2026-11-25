"""Compatibility command for the retired GP-009 broker artifact audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = PROJECT_ROOT / "assurance" / "runs" / "monthly_manifest.json"
DEFAULT_ALERT = PROJECT_ROOT / "assurance" / "runs" / "monthly_alert.jsonl"


def report_retired() -> int:
    print(
        "Monthly broker audit retired (monthly_broker_audit_retired). "
        "Use monthly_broker_schedule.py verify to inspect the last recorded run.",
        file=sys.stderr,
    )
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # Keep old command lines parseable so callers receive the explicit disposition.
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--alert", type=Path, default=DEFAULT_ALERT)
    parser.add_argument("--run-id")
    parser.add_argument("--entity")
    parser.parse_args(argv)
    return report_retired()


if __name__ == "__main__":
    raise SystemExit(main())
