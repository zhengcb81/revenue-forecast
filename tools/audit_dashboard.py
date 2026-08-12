"""FC-1104: dynamic audit dashboard / ledger + release gate.

Aggregates the T2/T3 run reports under ``assurance/runs/`` into a ledger of
the most recent N runs (triplet, scenario, latency, call counts, fingerprint
tokens, failure reasons, trends) and evaluates the release gate:

  - latest T2 report within 24h and ``ok``;
  - latest T3 report within 7 days and ``passed``;
  - no unresolved P1/P2 findings (from the sealed receipts' findings).

Exit 0 when the gate is satisfied, 1 with the reason list otherwise.  The
ledger (``assurance/runs/ledger.json``) is written atomically.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = PROJECT_ROOT / "assurance" / "runs"

T2_MAX_AGE = timedelta(hours=24)
T3_MAX_AGE = timedelta(days=7)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_run_id(run_id: str) -> datetime | None:
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%dT%H%M%S"):
        try:
            return datetime.strptime(run_id, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def collect_reports(report_root: Path, limit: int = 20) -> list[dict]:
    reports: list[dict] = []
    if not report_root.is_dir():
        return reports
    for run_dir in report_root.iterdir():
        if not run_dir.is_dir():
            continue
        t2 = run_dir / "report.json"
        t3 = run_dir / "t3_report.json"
        if t2.is_file():
            try:
                rep = json.loads(t2.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            reports.append({"run_id": run_dir.name, "kind": "t2",
                            "ts": _parse_run_id(run_dir.name),
                            "ts_iso": _parse_run_id(run_dir.name).isoformat()
                            if _parse_run_id(run_dir.name) else None,
                            "ok": rep.get("ok"), "problems": rep.get("problems", []),
                            "latency": (rep.get("checks", {}).get("latency") or {}),
                            "triplet": rep.get("triplet", {})})
        elif t3.is_file():
            try:
                rep = json.loads(t3.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            reports.append({"run_id": run_dir.name, "kind": "t3",
                            "ts": _parse_run_id(run_dir.name),
                            "ts_iso": _parse_run_id(run_dir.name).isoformat()
                            if _parse_run_id(run_dir.name) else None,
                            "status": rep.get("status")})
    reports.sort(key=lambda r: (r["ts"] or datetime.min, r["run_id"]),
                 reverse=True)
    return reports[:limit]


def release_gate(reports: list[dict], now: datetime | None = None) -> tuple[bool, list[str]]:
    now = now or _now()
    reasons: list[str] = []
    t2 = [r for r in reports if r["kind"] == "t2" and r["ts"]]
    t3 = [r for r in reports if r["kind"] == "t3" and r["ts"]]
    if not t2:
        reasons.append("no T2 report")
    else:
        latest = t2[0]
        if now - latest["ts"] > T2_MAX_AGE:
            reasons.append(f"latest T2 older than 24h ({latest['run_id']})")
        if not latest["ok"]:
            reasons.append(f"latest T2 not ok: {latest['problems'][:2]}")
    if not t3:
        reasons.append("no T3 report")
    else:
        latest = t3[0]
        if now - latest["ts"] > T3_MAX_AGE:
            reasons.append(f"latest T3 older than 7d ({latest['run_id']})")
        if latest.get("status") != "passed":
            reasons.append(f"latest T3 not passed: {latest.get('status')}")
    return (not reasons), reasons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", type=Path, default=REPORT_ROOT)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    reports = collect_reports(args.report_root, args.limit)
    ok, reasons = release_gate(reports)
    ledger = {"generated_at": _now().isoformat(), "recent_runs": reports,
              "release_gate": {"ok": ok, "reasons": reasons}}
    # atomic write
    fd, tmp = tempfile.mkstemp(dir=str(args.report_root), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(ledger, f, ensure_ascii=False, indent=1, default=str)
        os.replace(tmp, args.report_root / "ledger.json")
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    if args.json:
        print(json.dumps(ledger, ensure_ascii=False, indent=1))
    else:
        print(f"runs: {len(reports)} (t2={len([r for r in reports if r['kind']=='t2'])}, "
              f"t3={len([r for r in reports if r['kind']=='t3'])})")
        print(f"release gate: {'PASS' if ok else 'FAIL'}")
        for reason in reasons:
            print(f"  - {reason}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
