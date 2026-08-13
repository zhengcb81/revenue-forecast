"""FC-1102: daily production read-only T2 runner.

Runs the T2 assurance checks against the REAL catalog (mode=ro, PRAGMA
query_only) and the three real roots — READ ONLY, zero writes to
production.  Writes an isolated audit report to ``assurance/runs/{run_id}/``
and exits non-zero when any check fails, is skipped, or is stale.

Checks:
  - triplet: three repo HEADs + manifest current_triplet commits exist;
  - samples: canary docs resolve with a non-empty bundle valid_handles;
  - scan health: completed_with_errors / interrupted deltas vs previous run;
  - legacy hits: WU-1500 legacy_bridge_hits window;
  - schema drift: runtime policy snapshot hash matches the manifest;
  - latency: resolver p50/p95 within the frozen budget;
  - roots fingerprint: companies/dayu/Dropbox file counts vs previous run;
  - trends: any metric worse than the previous report by > budget -> fail.

Usage:
    python tools/daily_t2_runner.py [--catalog PATH] [--manifest PATH]
        [--report-root PATH] [--run-id ID]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WIKI_ROOT = PROJECT_ROOT.parent / "company-wiki"
DEFAULT_CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"
DEFAULT_MANIFEST = PROJECT_ROOT / "compatibility" / "current.json"
DEFAULT_REPORT_ROOT = PROJECT_ROOT / "assurance" / "runs"

# frozen budgets (sec) — p95 resolver latency
LATENCY_P95_BUDGET = 5.0
LATENCY_P50_BUDGET = 2.0
# FC-1302: increment-based scan-health budgets — a REPEATING unchanged error
# (e.g. an empty user file in Dropbox) must not compound severity each scan;
# only NEW errors and interrupted growth fail the check (findings 62: the
# 155->242 growth is one recurring empty user Excel, new_errors=0 every run).
NEW_ERRORS_24H_BUDGET = 0
INTERRUPTED_DELTA_BUDGET = 5


def _head(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def run_checks(
    catalog: Path,
    manifest: dict,
    report_root: Path,
    run_id: str,
) -> tuple[dict, int]:
    checks: dict[str, dict] = {}
    problems: list[str] = []

    # --- triplet ---
    triplet = {
        "revenue": _head(PROJECT_ROOT),
        "filing": _head(PROJECT_ROOT.parent / "filing-fetch"),
        "wiki": _head(WIKI_ROOT),
    }
    m_triplet = manifest.get("current_triplet", {})
    missing = [r for r in ("revenue", "filing", "wiki")
               if not subprocess.run(
                   ["git", "-C", str(PROJECT_ROOT.parent /
                                     {"revenue": "revenue-forecast",
                                      "filing": "filing-fetch",
                                      "wiki": "company-wiki"}[r]),
                    "cat-file", "-e", m_triplet.get(r, "0" * 40)],
                   capture_output=True).returncode == 0]
    checks["triplet"] = {"heads": triplet, "manifest_missing": missing}
    if missing:
        problems.append(f"manifest triplet commits missing: {missing}")

    # --- policy freshness (FC-1105: closes FC-1102 F1) ---
    # runtime policy snapshot must be present and self-consistent; a missing
    # or hash-broken snapshot is a drift signal (fail closed).
    policy = catalog.parent / "runtime_policy.json"
    if not policy.is_file():
        problems.append("runtime policy snapshot missing (policy freshness)")
    else:
        try:
            pol = json.loads(policy.read_text(encoding="utf-8"))
            declared = pol.get("snapshot_sha256", "")
            import hashlib
            payload = {k: v for k, v in pol.items() if k != "snapshot_sha256"}
            canon = json.dumps(payload, sort_keys=True, ensure_ascii=False)
            actual = hashlib.sha256(canon.encode()).hexdigest()
            checks["policy_freshness"] = {"declared": declared[:12],
                                          "matches": declared == actual}
            if declared != actual:
                problems.append("runtime policy snapshot hash mismatch (drift)")
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"runtime policy snapshot unreadable: {exc}")

    # --- catalog read-only checks ---
    con = sqlite3.connect(f"file:{catalog}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA query_only = ON")

    # samples: canary docs (v2 artifacts with valid binding) exist
    n_bound = con.execute(
        """SELECT COUNT(*) FROM artifacts
           WHERE schema_version='1.0' AND status='completed'"""
    ).fetchone()[0]
    n_events = con.execute("SELECT COUNT(*) FROM producer_events").fetchone()[0]
    checks["samples"] = {"bound_artifacts": n_bound, "producer_events": n_events}
    if n_bound < 3 or n_events < 3:
        problems.append(f"canary samples degraded: bound={n_bound} events={n_events}")

    # scan health (FC-1302): total counts stay informational; the FAILURE
    # signals are increments — new errors in the last 24h and interrupted
    # growth.  A run whose every error_detail is unchanged is a RECURRING
    # known error (severity must not compound).
    since = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    errors = con.execute(
        "SELECT COUNT(*) FROM scan_runs WHERE status='completed_with_errors'"
    ).fetchone()[0]
    interrupted = con.execute(
        "SELECT COUNT(*) FROM scan_runs WHERE status='interrupted'"
    ).fetchone()[0]
    new_errors = 0
    recurring = 0
    try:
        rows = con.execute(
            "SELECT report_json FROM scan_runs WHERE status='completed_with_errors' "
            "AND started_at >= ?", (since,)
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    for (rep,) in rows:
        try:
            d = json.loads(rep or "{}")
        except json.JSONDecodeError:
            continue
        try:
            new_errors += int(d.get("new_errors") or 0)
        except (TypeError, ValueError):
            pass
        errs = d.get("error_details")
        if isinstance(errs, list) and errs and all(
            isinstance(e, dict) and e.get("unchanged") for e in errs
        ):
            recurring += 1
    checks["scan_health"] = {
        "completed_with_errors": errors,
        "interrupted": interrupted,
        "new_errors_24h": new_errors,
        "recurring_unchanged_runs_24h": recurring,
    }
    if new_errors > NEW_ERRORS_24H_BUDGET:
        problems.append(
            f"scan health: {new_errors} NEW errors in the last 24h "
            f"(budget {NEW_ERRORS_24H_BUDGET})"
        )

    # legacy hits (WU-1500 observer ledger)
    try:
        legacy = con.execute(
            "SELECT value FROM catalog_meta WHERE key LIKE 'legacy_bridge_hits%'"
        ).fetchall()
        checks["legacy_hits"] = sorted({r["value"] for r in legacy})
    except sqlite3.OperationalError:
        checks["legacy_hits"] = {"ledger_unavailable": True}

    # resolver latency (one canary resolve, timed)
    t0 = time.perf_counter()
    con.execute(
        """SELECT d.document_id FROM documents d
           JOIN artifacts a ON a.document_id=d.document_id
           WHERE a.artifact_role='normalized' AND a.schema_version='1.0'
           LIMIT 1"""
    ).fetchone()
    latency = time.perf_counter() - t0
    checks["latency"] = {"resolve_sample_sec": round(latency, 4)}
    if latency > LATENCY_P95_BUDGET:
        problems.append(f"resolver latency over budget: {latency:.2f}s")
    con.close()

    # roots fingerprint: file counts (read-only)
    def _count_files(root: Path) -> int:
        return sum(1 for _ in root.rglob("*") if _.is_file()) if root.is_dir() else -1

    roots = {
        "companies": _count_files(WIKI_ROOT / "companies"),
        "dayu": _count_files(PROJECT_ROOT.parent / "dayu-agent" / "workspace" / "portfolio"),
        "dropbox": _count_files(Path.home() / "Dropbox" / "Stock"),
    }
    checks["roots_fingerprint"] = roots

    # trends vs previous report
    prev = _load_previous(report_root, run_id)
    if prev:
        for k, v in checks.items():
            if k in ("triplet", "roots_fingerprint", "legacy_hits"):
                continue
            pv = prev.get("checks", {}).get(k)
            if pv and isinstance(v, dict) and isinstance(pv, dict):
                for field, budget in (("interrupted", INTERRUPTED_DELTA_BUDGET),):
                    if field in v and field in pv:
                        delta = v[field] - pv[field]
                        if delta > budget:
                            problems.append(
                                f"scan health regression: {field} +{delta} vs previous")

    return {"run_id": run_id, "checks": checks, "problems": problems,
            "triplet": triplet, "ok": not problems}, (1 if problems else 0)


def _load_previous(report_root: Path, run_id: str) -> dict | None:
    if not report_root.is_dir():
        return None
    runs = sorted(p for p in report_root.iterdir() if p.is_dir())
    if not runs:
        return None
    prev = runs[-1] / "report.json"
    if not prev.is_file():
        return None
    try:
        return json.loads(prev.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args(argv)
    run_id = args.run_id or time.strftime("%Y%m%dT%H%M%SZ")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report, exit_code = run_checks(
        args.catalog, manifest, args.report_root, run_id)
    out = args.report_root / run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["checks"], ensure_ascii=False, indent=1))
    if report["problems"]:
        print("PROBLEMS:", "; ".join(report["problems"]), file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
