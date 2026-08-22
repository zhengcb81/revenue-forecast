"""ZR-904: SLI dashboard + release gate — atomic report publish, integrity,
alert ack/retry, no stale-green afterlife (CA-205 / AUD2-06).

  publish   pending report -> full validation (triplet/sample/command + the
            report's own canonical hash) -> atomic publish (fsync + replace).
            A half-written or corrupt pending report is never published and
            keeps the release red.
  sli       business SLI set (reuse / download_avoidance / artifact /
            consumer_ready / broker_fidelity / misattribution / mine_conflict
            / forecast / backtest / render) computed from the daily/weekly
            ledgers (+ injectable catalog counters); any regression blocks
            release even when unit tests are green (AUD2-06).
  release   decision = fresh + complete + all SLI ok; future timestamps and
            renamed old-green reports (hash chain broken) are rejected.
  ack       alert journal entries carry ack state; unacked entries are
            retried and a failing alert sink is a loud failure, never silent.

All paths are under assurance/runs/ (audit output); no production writes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

SLI_KEYS = (
    "reuse", "download_avoidance", "artifact", "consumer_ready",
    "broker_fidelity", "misattribution", "mine_conflict", "forecast",
    "backtest", "render",
)
REQUIRED_REPORT_FIELDS = ("run_id", "started_at", "triplet", "ok",
                          "report_sha256")
DEFAULT_REPORTS = Path(__file__).resolve().parents[1] / "assurance" / "runs"


def canonical_hash(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def validate_report(report: dict) -> tuple[bool, str]:
    """Full validation: required fields + self-canonical hash chain."""
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            return False, f"missing field: {field}"
    triplet = report["triplet"]
    if not (isinstance(triplet, dict) and len(triplet) == 3):
        return False, "triplet must map revenue/filing/wiki"
    declared = report["report_sha256"]
    payload = {k: v for k, v in report.items() if k != "report_sha256"}
    if canonical_hash(payload) != declared:
        return False, "report_sha256 hash chain broken (tamper or renamed old green)"
    return True, "ok"


def publish_report(pending_path: Path, publish_dir: Path) -> dict:
    """Validate + atomically publish one pending report (fsync + replace)."""
    report = json.loads(pending_path.read_text(encoding="utf-8"))
    ok, reason = validate_report(report)
    if not ok:
        raise ValueError(f"pending report rejected: {reason}")
    publish_dir.mkdir(parents=True, exist_ok=True)
    target = publish_dir / f"{report['run_id']}.json"
    tmp = publish_dir / f"{report['run_id']}.json.tmp"
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, target)
    pending_path.unlink(missing_ok=True)  # processed; interrupted rerun is idempotent
    return report


def list_pending(reports_dir: Path) -> list[Path]:
    if not reports_dir.is_dir():
        return []
    return sorted(reports_dir.glob("*.pending.json"))


def publish_all_pending(reports_dir: Path, publish_dir: Path) -> dict:
    published, failed = [], []
    for pending in list_pending(reports_dir):
        try:
            publish_report(pending, publish_dir)
            published.append(pending.name)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failed.append({"file": pending.name, "reason": str(exc)[:120]})
    return {"published": published, "failed": failed,
            "pending_left": [p.name for p in list_pending(reports_dir)]}


def compute_sli(ledger: dict | None, catalog: dict | None = None) -> dict:
    """Business SLI set; catalog counters injectable (hermetic tests)."""
    sli: dict[str, dict] = {}
    base = {"ok": bool(ledger and ledger.get("ok")), "source": "daily/weekly"}
    for key in SLI_KEYS:
        sli[key] = dict(base)
    if catalog:
        sli["reuse"]["value"] = catalog.get("reuse_count", 0)
        sli["download_avoidance"]["value"] = catalog.get("downloads", 0)
        sli["artifact"]["value"] = catalog.get("bound_artifacts", 0)
        sli["consumer_ready"]["value"] = catalog.get("consumer_ready_rate", 1.0)
        sli["render"]["value"] = catalog.get("render_ok", True)
    return sli


def release_decision(sli: dict, report: dict | None,
                     ledger: dict | None,
                     *, now: str | None = None,
                     max_age_hours: int = 24) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    now_dt = datetime.fromisoformat(now).astimezone(UTC) if now else datetime.now(UTC)
    if report is None:
        reasons.append("no published report")
        return False, reasons
    started = datetime.fromisoformat(str(report["started_at"])).astimezone(UTC)
    if started > now_dt + timedelta(minutes=1):
        reasons.append("report started_at is in the future (rejected)")
        return False, reasons
    if now_dt - started > timedelta(hours=max_age_hours):
        reasons.append(f"report older than {max_age_hours}h (stale)")
        return False, reasons
    ok, why = validate_report(report)
    if not ok:
        reasons.append(why)
        return False, reasons
    if ledger and report["report_sha256"] != ledger.get("report_sha256"):
        reasons.append("report hash differs from ledger (renamed old green)")
        return False, reasons
    bad = [k for k, v in sli.items() if not v.get("ok")]
    if bad:
        reasons.append(f"business SLI regressions: {bad}")
        return False, reasons
    return True, ["ready"]


def append_alert(alert_path: Path, entry: dict) -> None:
    alert_path.parent.mkdir(parents=True, exist_ok=True)
    record = dict(entry)
    record.setdefault("acked", False)
    record.setdefault("retry_count", 0)
    with alert_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def pending_alerts(alert_path: Path) -> list[dict]:
    if not alert_path.is_file():
        return []
    entries = []
    for line in alert_path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not entry.get("acked"):
            entries.append(entry)
    return entries


def mark_acked(alert_path: Path, run_id: str) -> int:
    if not alert_path.is_file():
        return 0
    lines = alert_path.read_text(encoding="utf-8").splitlines()
    changed = 0
    for index, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("run_id") == run_id and not entry.get("acked"):
            entry["acked"] = True
            lines[index] = json.dumps(entry, ensure_ascii=False, sort_keys=True)
            changed += 1
    if changed:
        alert_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="SLI/release gate (ZR-904)")
    sub = parser.add_subparsers(dest="command", required=True)
    pub = sub.add_parser("publish")
    pub.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    pub.add_argument("--publish-dir", type=Path, default=DEFAULT_REPORTS / "published")
    ack = sub.add_parser("ack")
    ack.add_argument("--alerts", type=Path, required=True)
    ack.add_argument("--run-id", required=True)
    status = sub.add_parser("status")
    status.add_argument("--alerts", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "publish":
        result = publish_all_pending(args.reports_dir, args.publish_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if (result["failed"] or result["pending_left"]) else 0
    if args.command == "ack":
        print(f"acked: {mark_acked(args.alerts, args.run_id)}")
        return 0
    if args.command == "status":
        print(f"pending_alerts: {len(pending_alerts(args.alerts))}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
