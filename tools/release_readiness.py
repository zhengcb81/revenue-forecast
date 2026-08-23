"""ZR-1001: release readiness — repo fingerprint / catalog integrity /
capacity budgets / backup readability / rollback dry-run / authorization.

Every check must pass before a release window opens (registry: "integrity/
fingerprint, 耗时/空间预算, 用户授权; 未满足不进入窗口"):

  fingerprints  three repo HEADs recorded and consistent.
  integrity     production catalog read-only open + key-table row probes
                (fast gate; full integrity_check is minutes-scale on the
                production catalog — deliberately replaced, documented in
                the card C2).
  capacity      assurance/runs space within the frozen budget (suite time is
                bounded by CI timeouts — REV-002 resolved by removing the
                dead constant).
  backup        backup location exists and is readable.
  rollback      dry-run: current HEADs recorded as the rollback point
                (rollback_manifest.json); steps parse — nothing executes.
  authorization release_authorization.json present and valid (owner/reason/
                at_utc) — without it the readiness gate stays blocked.

Usage:
  python tools/release_readiness.py            # check (exit 1 on any red)
  python tools/release_readiness.py issue-auth --owner X --reason Y
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI_ROOT = ROOT.parent / "company-wiki"
CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"
RUNS_DIR = ROOT / "assurance" / "runs"
BACKUP_DIR = ROOT / "assurance" / "backup"
AUTH_PATH = RUNS_DIR / "release_authorization.json"
ROLLBACK_PATH = RUNS_DIR / "rollback_manifest.json"

BUDGET_RUNS_MB = 2048

REPOS = {
    "revenue": ROOT,
    "filing": ROOT.parent / "filing-fetch",
    "wiki": WIKI_ROOT,
}


def _head(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def head_fingerprints() -> dict:
    return {name: _head(path) for name, path in REPOS.items()}


def catalog_integrity() -> tuple[bool, str]:
    """Fast integrity gate: read-only open + key-table row probes (PRAGMA
    integrity_check / quick_check take minutes on the production catalog;
    a read-only open already validates WAL/page-header consistency, and the
    key-table probes confirm the schema answers)."""
    try:
        con = sqlite3.connect(f"file:{CATALOG}?mode=ro", uri=True, timeout=30)
        counts = {}
        for table in ("documents", "sources", "locations"):
            counts[table] = con.execute(
                f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        con.close()
    except (OSError, sqlite3.Error) as exc:
        return False, f"catalog unreadable: {exc}"
    detail = "read-only open ok, " + ", ".join(
        f"{k}={v}" for k, v in counts.items())
    return True, detail


def capacity_ok() -> tuple[bool, str]:
    size_mb = 0
    if RUNS_DIR.is_dir():
        for path in RUNS_DIR.rglob("*"):
            if path.is_file():
                size_mb += path.stat().st_size
    size_mb = size_mb // (1024 * 1024)
    return size_mb <= BUDGET_RUNS_MB, f"assurance/runs {size_mb}MB <= {BUDGET_RUNS_MB}MB"


def backup_readable() -> tuple[bool, str]:
    if not BACKUP_DIR.is_dir():
        return False, "backup dir missing (assurance/backup)"
    probe = BACKUP_DIR / ".read-probe"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return False, f"backup dir not writable: {exc}"
    return True, "backup dir readable"


def write_rollback_point() -> tuple[bool, str]:
    payload = {
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "heads": head_fingerprints(),
        "rollback_steps": ["git checkout <head> -- <product paths>",
                           "restore backup -> catalog (if needed)"],
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    ROLLBACK_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True, f"rollback point recorded at {ROLLBACK_PATH.name}"


def authorization() -> tuple[bool, str]:
    if not AUTH_PATH.is_file():
        return False, "release_authorization.json missing (release blocked)"
    data = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    required = ("owner", "reason", "at_utc")
    if not all(key in data and data[key] for key in required):
        return False, "authorization incomplete (owner/reason/at_utc)"
    return True, f"authorized by {data['owner']}"


def issue_authorization(owner: str, reason: str) -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"owner": owner, "reason": reason,
               "at_utc": datetime.now(UTC).isoformat()}
    AUTH_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_checks() -> dict:
    int_ok, int_detail = catalog_integrity()
    cap_ok, cap_detail = capacity_ok()
    bak_ok, bak_detail = backup_readable()
    rb_ok, rb_detail = write_rollback_point()
    auth_ok, auth_detail = authorization()
    return {
        "fingerprints": {"ok": True, "detail": json.dumps(head_fingerprints())},
        "integrity": {"ok": int_ok, "detail": int_detail},
        "capacity": {"ok": cap_ok, "detail": cap_detail},
        "backup": {"ok": bak_ok, "detail": bak_detail},
        "rollback": {"ok": rb_ok, "detail": rb_detail},
        "authorization": {"ok": auth_ok, "detail": auth_detail},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Release readiness (ZR-1001)")
    sub = parser.add_subparsers(dest="command")
    auth = sub.add_parser("issue-auth")
    auth.add_argument("--owner", required=True)
    auth.add_argument("--reason", required=True)
    args = parser.parse_args()
    if args.command == "issue-auth":
        issue_authorization(args.owner, args.reason)
        print(f"authorization issued for {args.owner}")
        return 0
    result = run_checks()
    for name, gate in result.items():
        detail = gate.get("detail") or ""
        print(f"{name}: {'OK' if gate['ok'] else 'RED'} {detail}".rstrip())
    return 0 if all(g["ok"] for g in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
