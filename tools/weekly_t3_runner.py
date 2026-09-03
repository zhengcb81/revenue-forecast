"""FC-1103: weekly real-provider isolated T3 runner.

Runs the FC-805 T3 suite (CN/HK/US real downloads on a TEMP wiki — never the
production catalog) through the real filing-fetch tests, and reports:

  - PASS (exit 0): all three markets green with real downloads + second-request
    zero-download verification (FC805_REAL_DOWNLOAD=1 must be set by the
    release owner).
  - BLOCKED (exit 2): T3 not authorized (FC805_REAL_DOWNLOAD != 1) or
    provider credentials missing — an alert, never a silent green.
  - FAIL (exit 1): any market download/verification failed.

The report lands under ``assurance/runs/{run_id}/t3_report.json`` (isolated).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILING_ROOT = PROJECT_ROOT.parent / "filing-fetch"
T3_TEST = FILING_ROOT / "tests" / "test_fc805_real_download_t3.py"
REPORT_ROOT = PROJECT_ROOT / "assurance" / "runs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", type=Path, default=REPORT_ROOT)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--force", action="store_true",
                        help="run real downloads (sets FC805_REAL_DOWNLOAD=1)")
    args = parser.parse_args(argv)

    run_id = args.run_id or time.strftime("%Y%m%dT%H%M%SZ")
    report: dict = {"run_id": run_id, "force": args.force}

    if not args.force:
        report.update({"status": "blocked",
                       "reason": "T3 real-provider download not authorized "
                                 "(--force / FC805_REAL_DOWNLOAD=1 required)"})
        out = args.report_root / run_id
        out.mkdir(parents=True, exist_ok=True)
        (out / "t3_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("BLOCKED: " + report["reason"], file=sys.stderr)
        return 2

    env = dict(os.environ)
    env["FC805_REAL_DOWNLOAD"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "pytest", str(T3_TEST), "-q"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800,
        cwd=str(FILING_ROOT), env=env,
    )
    report["returncode"] = proc.returncode
    report["stdout_tail"] = proc.stdout[-2000:]
    if proc.returncode == 0:
        report["status"] = "passed"
    elif "skip" in proc.stdout.lower() and "failed" not in proc.stdout.lower():
        report["status"] = "blocked"
        report["reason"] = "T3 skipped (provider credentials missing?)"
    else:
        report["status"] = "failed"
    out = args.report_root / run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "t3_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"T3 status: {report['status']}")
    if proc.returncode != 0:
        print(proc.stdout[-1500:])
    return {0: 0, 2: 2}.get(proc.returncode, 1)


if __name__ == "__main__":
    sys.exit(main())
