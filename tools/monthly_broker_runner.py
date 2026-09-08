"""GP-009 / CA-206 C3: monthly broker-cohort audit (read-only).

The monthly soak run re-verifies the frozen real broker corpus in the
production wiki catalog: every ``broker_research`` document of the Zijin
cohort must still carry a ``normalized`` and a ``sections`` artifact.  The
run never writes the catalog; it writes ``assurance/runs/monthly_manifest.json``
and appends an alert when not-ok (fail-closed, never a silent green).

Exit codes: 0 = ok, 1 = not-ok, 2 = blocked (catalog missing/unreadable).
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

from daily_t2_schedule import _head, append_alert, write_ledger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = (
    PROJECT_ROOT.parent / "company-wiki" / ".source_catalog" / "catalog.sqlite3"
)
DEFAULT_LEDGER = PROJECT_ROOT / "assurance" / "runs" / "monthly_manifest.json"
DEFAULT_ALERT = PROJECT_ROOT / "assurance" / "runs" / "monthly_alert.jsonl"
REQUIRED_ROLES = ("normalized", "sections")
DEFAULT_ENTITY = "紫金"


def audit(catalog: Path, *, entity_like: str = DEFAULT_ENTITY) -> dict:
    """Read-only cohort audit; returns {corpus, complete, incomplete, ok}.

    The cohort is every ``broker_research`` document that is entity-linked to
    the company *or* whose title names it.  The title arm matters: the GP-010
    corpus includes 长江证券's 紫金矿业-vs-陕西煤业 comparison, which is not
    entity-linked to 紫金矿业 and would otherwise be silently dropped.
    """
    con = sqlite3.connect(f"file:{catalog.as_posix()}?mode=ro", uri=True)
    try:
        cur = con.cursor()
        rows = cur.execute(
            "SELECT document_id, title FROM documents WHERE document_kind = 'broker_research' "
            "AND (title LIKE ? OR document_id IN ("
            "  SELECT de.document_id FROM document_entities de "
            "  JOIN entities e ON e.entity_id = de.entity_id WHERE e.name LIKE ?)) "
            "ORDER BY document_id",
            (f"%{entity_like}%", f"%{entity_like}%"),
        ).fetchall()
        documents = []
        for document_id, title in rows:
            roles = {
                role
                for (role,) in cur.execute(
                    "SELECT DISTINCT artifact_role FROM artifacts "
                    "WHERE document_id = ?",
                    (document_id,),
                )
            }
            documents.append(
                {
                    "document_id": document_id,
                    "title": (title or "")[:120],
                    "roles": sorted(roles),
                    "missing": [role for role in REQUIRED_ROLES if role not in roles],
                }
            )
    finally:
        con.close()
    incomplete = [doc for doc in documents if doc["missing"]]
    return {
        "corpus": len(documents),
        "complete": len(documents) - len(incomplete),
        "incomplete": incomplete,
        "documents": documents,
        "ok": bool(documents) and not incomplete,
    }


def run(
    catalog: Path,
    ledger_path: Path,
    alert_path: Path,
    *,
    run_id: str | None = None,
    entity_like: str = DEFAULT_ENTITY,
) -> int:
    run_id = run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    started = datetime.now(UTC).isoformat()
    triplet = {
        "revenue": _head(PROJECT_ROOT),
        "filing": _head(PROJECT_ROOT.parent / "filing-fetch"),
        "wiki": _head(PROJECT_ROOT.parent / "company-wiki"),
    }
    if not catalog.is_file():
        detail = f"production catalog missing: {catalog}"
        write_ledger(ledger_path, run_id, started, triplet, False,
                     f"monthly-run-{run_id}")
        append_alert(alert_path, {
            "at_utc": started, "run_id": run_id, "status": "blocked",
            "reason": detail, "exit_code": 2,
        })
        print(f"BLOCKED: {detail}", file=sys.stderr)
        return 2
    result = audit(catalog, entity_like=entity_like)
    write_ledger(ledger_path, run_id, started, triplet, result["ok"],
                 f"monthly-run-{run_id}")
    # Report dir follows the ledger's parent so tests/alternate ledger paths
    # never write into the repo's assurance/runs (2026-09-08: hermetic tests
    # left assurance/runs/<run_id>/monthly_broker_report.json behind).
    report = ledger_path.parent / run_id
    report.mkdir(parents=True, exist_ok=True)
    (report / "monthly_broker_report.json").write_text(
        json.dumps({"run_id": run_id, "started_at": started, **result},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not result["ok"]:
        detail = (
            f"broker cohort incomplete: {result['complete']}/{result['corpus']} "
            f"documents have {list(REQUIRED_ROLES)}"
        )
        append_alert(alert_path, {
            "at_utc": started, "run_id": run_id, "status": "not-ok",
            "reason": detail, "exit_code": 1,
        })
        print(f"NOT-OK: {detail}", file=sys.stderr)
        for doc in result["incomplete"][:10]:
            print(f"  missing {doc['missing']}: {doc['document_id']}", file=sys.stderr)
        return 1
    print(
        f"run_id={run_id} ok=True broker_cohort={result['corpus']} "
        f"complete={result['complete']}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--alert", type=Path, default=DEFAULT_ALERT)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--entity", default=DEFAULT_ENTITY)
    args = parser.parse_args(argv)
    return run(args.catalog, args.ledger, args.alert,
               run_id=args.run_id, entity_like=args.entity)


if __name__ == "__main__":
    raise SystemExit(main())
