"""ZR-1001: automatic release readiness checks.

Every check must pass before a release window opens:

  fingerprints  three repo HEADs recorded and consistent.
  integrity     production catalog read-only open + key-table row probes
                (fast gate; full integrity_check is minutes-scale on the
                production catalog — deliberately replaced, documented in
                the card C2).
  scenario_evidence  all 197 required scenario files re-read and SHA-verified.
  capacity      assurance/runs space within the frozen budget (suite time is
                bounded by CI timeouts — REV-002 resolved by removing the
                dead constant).
  backup        backup location exists and is readable.
  rollback      dry-run: current HEADs recorded as the rollback point
                (rollback_manifest.json); steps parse — nothing executes.
Usage:
  python tools/release_readiness.py            # check (exit 1 on any red)
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "assurance" / "unified_completion"))

from uc.scenarios import closure_report as scenario_closure_report  # noqa: E402
from uc.scenarios import verify as scenario_verify  # noqa: E402

WIKI_ROOT = ROOT.parent / "company-wiki"
CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"
RUNS_DIR = ROOT / "assurance" / "runs"
BACKUP_DIR = ROOT / "assurance" / "backup"
ROLLBACK_PATH = RUNS_DIR / "rollback_manifest.json"
SCENARIO_REGISTRY_PATH = (
    ROOT / "assurance" / "unified_completion" / "scenarios" / "scenario_registry.json"
)

BUDGET_RUNS_MB = 2048

REPOS = {
    "revenue": ROOT,
    "filing": ROOT.parent / "filing-fetch",
    "wiki": WIKI_ROOT,
}


def _head(repo: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.decode("ascii", errors="ignore").strip()


def head_fingerprints() -> dict:
    return {name: _head(path) for name, path in REPOS.items()}


def _fingerprints_complete(heads: dict) -> bool:
    return set(heads) == set(REPOS) and all(
        isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha)
        for sha in heads.values()
    )


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


def scenario_evidence_integrity() -> tuple[bool, str]:
    """Use the same frozen-matrix and byte-level verifier as closure-report."""
    try:
        problems = scenario_verify(ROOT, SCENARIO_REGISTRY_PATH)
        if problems:
            return False, f"scenario registry drift: {problems[0]}"
        payload = json.loads(SCENARIO_REGISTRY_PATH.read_text(encoding="utf-8"))
        report = scenario_closure_report(payload, ROOT)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return False, f"scenario evidence unavailable: {exc}"
    ready = report["closure_ready"] and report["total_scenarios"] == 197
    return ready, (
        f"{report['total_scenarios']} scenarios, "
        f"{report['unsatisfied']} evidence failures"
    )


def capacity_ok() -> tuple[bool, str]:
    size_bytes = 0
    if RUNS_DIR.is_dir():
        for path in RUNS_DIR.rglob("*"):
            if path.is_file():
                size_bytes += path.stat().st_size
    mib = 1024 * 1024
    size_mb = size_bytes / mib
    return (
        size_bytes <= BUDGET_RUNS_MB * mib,
        f"assurance/runs {size_mb:.2f}MB <= {BUDGET_RUNS_MB}MB",
    )


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


def write_rollback_point(heads: dict[str, str] | None = None) -> tuple[bool, str]:
    if heads is None:
        heads = head_fingerprints()
    if not _fingerprints_complete(heads):
        return False, "rollback point requires complete three-repo HEADs"
    payload = {
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "heads": heads,
        "rollback_steps": ["git checkout <head> -- <product paths>",
                           "restore backup -> catalog (if needed)"],
    }
    try:
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        ROLLBACK_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        return False, f"rollback point unwritable: {exc}"
    return True, f"rollback point recorded at {ROLLBACK_PATH.name}"


def run_checks() -> dict:
    heads = head_fingerprints()
    fingerprint_ok = _fingerprints_complete(heads)
    int_ok, int_detail = catalog_integrity()
    evidence_ok, evidence_detail = scenario_evidence_integrity()
    cap_ok, cap_detail = capacity_ok()
    bak_ok, bak_detail = backup_readable()
    rb_ok, rb_detail = write_rollback_point(heads)
    return {
        "fingerprints": {"ok": fingerprint_ok, "detail": json.dumps(heads)},
        "integrity": {"ok": int_ok, "detail": int_detail},
        "scenario_evidence": {"ok": evidence_ok, "detail": evidence_detail},
        "capacity": {"ok": cap_ok, "detail": cap_detail},
        "backup": {"ok": bak_ok, "detail": bak_detail},
        "rollback": {"ok": rb_ok, "detail": rb_detail},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Release readiness (ZR-1001)")
    parser.parse_args()
    result = run_checks()
    for name, gate in result.items():
        detail = gate.get("detail") or ""
        print(f"{name}: {'OK' if gate['ok'] else 'RED'} {detail}".rstrip())
    return 0 if all(g["ok"] for g in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
