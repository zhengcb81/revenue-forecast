"""Inspect a completed or partial FF weekly T3 receipt and write an RF report."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import mkdtemp
from uuid import uuid4

if __package__:
    from .weekly_t3_assurance import add_owner_options, read_weekly_t3
else:
    from weekly_t3_assurance import add_owner_options, read_weekly_t3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = PROJECT_ROOT / "assurance" / "runs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", type=Path, default=REPORT_ROOT)
    parser.add_argument("--run-id", help="local RF report identifier")
    parser.add_argument("--force", action="store_true",
                        help="legacy flag retained for callers. Only reads existing owner evidence.")
    add_owner_options(parser, run_id_option="--owner-run-id")
    args = parser.parse_args(argv)

    run_id = args.run_id
    if run_id is None:
        run_id = f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex}"
    if not run_id or run_id in {".", ".."} or any(char in run_id for char in "/\\:"):
        parser.error("--run-id must be one local report name")

    result = read_weekly_t3(
        args.filing_fetch_root, receipts_dir=args.receipts_dir, owner_run_id=args.owner_run_id,
    )
    status = {"ok": "passed", "not-ok": "failed", "blocked": "blocked"}[result.status]
    args.report_root.mkdir(parents=True, exist_ok=True)
    out = args.report_root / run_id
    try:
        out.mkdir()
    except FileExistsError:
        # An explicit name may already represent a historical observation.
        out = Path(mkdtemp(prefix=f"{run_id}-", dir=args.report_root))
    run_id = out.name
    report = result.report(run_id)
    report.update(status=status, force=args.force, returncode=result.exit_code, reason=result.detail)
    (out / "t3_report.json").write_text(
        json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8",
    )
    if status == "blocked":
        print(f"BLOCKED: {result.detail} report_id={run_id}", file=sys.stderr)
    else:
        print(f"T3 status: {status} report_id={run_id}")
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
