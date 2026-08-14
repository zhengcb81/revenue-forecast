"""ZR-001 replay: read-only real-catalog counterexample queries (company-wiki).

Reads the production catalog SQLite file with ``mode=ro`` + ``PRAGMA
query_only=ON`` only.  Never opens it for writes; the catalog data file is
never modified by this script (size + mtime are fingerprinted before/after).

Usage:  python -B assurance/unified_completion/replays/zr001_catalog_sql.py
        [--catalog PATH]

Emits JSON evidence files into ``replays/evidence/``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_CATALOG = (
    r"C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3"
)

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"

FILING_KINDS = (
    "annual_report",
    "semi_annual_report",
    "quarterly_report",
    "regulatory_filing",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect_ro(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=5.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def one(connection: sqlite3.Connection, sql: str, params: tuple = ()) -> object:
    row = connection.execute(sql, params).fetchone()
    return None if row is None else row[0]


def _review_present(metadata_json: str | None) -> bool:
    if not metadata_json:
        return False
    try:
        data = json.loads(metadata_json)
    except json.JSONDecodeError:
        return False
    return bool(data.get("prompt_injection_review"))


def w2_artifact_lineage(connection: sqlite3.Connection) -> dict:
    """Audit §2.6: artifact lineage — how many artifacts carry a
    schema_version + source_sha256 binding."""
    return {
        "normalized_total": one(
            connection,
            "SELECT COUNT(*) FROM artifacts WHERE artifact_role='normalized'",
        ),
        "normalized_with_binding": one(
            connection,
            "SELECT COUNT(*) FROM artifacts WHERE artifact_role='normalized' "
            "AND schema_version IS NOT NULL AND schema_version<>'' "
            "AND source_sha256 IS NOT NULL AND source_sha256<>''",
        ),
        "summary_total": one(
            connection,
            "SELECT COUNT(*) FROM artifacts WHERE artifact_role='summary'",
        ),
        "summary_with_binding": one(
            connection,
            "SELECT COUNT(*) FROM artifacts WHERE artifact_role='summary' "
            "AND schema_version IS NOT NULL AND schema_version<>'' "
            "AND source_sha256 IS NOT NULL AND source_sha256<>''",
        ),
        "normalized_by_status": [
            tuple(row)
            for row in connection.execute(
                "SELECT status, COUNT(*) FROM artifacts "
                "WHERE artifact_role='normalized' GROUP BY status ORDER BY status"
            )
        ],
        "summary_by_status": [
            tuple(row)
            for row in connection.execute(
                "SELECT status, COUNT(*) FROM artifacts "
                "WHERE artifact_role='summary' GROUP BY status ORDER BY status"
            )
        ],
        "queried_at_utc": utc_now(),
    }


def w5_zijin_prompt_review(connection: sqlite3.Connection) -> dict:
    """Zijin exact-reuse consumption failure data fact: the annual reports
    carry no prompt-injection review, so the resolution envelope reports
    ``not_reviewed`` and revenue fails closed at its safety gate."""
    rows = [
        dict(row)
        for row in connection.execute(
            "SELECT document_id, title, source_type, document_kind, "
            "published_date, source_status, metadata_json "
            "FROM documents WHERE title LIKE '%紫金%' OR title LIKE '%Zijin%' "
            "ORDER BY published_date DESC"
        ).fetchall()
    ]
    samples = []
    reviewed = 0
    for row in rows:
        has_review = _review_present(row.get("metadata_json"))
        reviewed += int(has_review)
        locations = [
            tuple(item)
            for item in connection.execute(
                "SELECT root_id, location_status, role FROM locations "
                "WHERE document_id=?",
                (row["document_id"],),
            )
        ]
        samples.append(
            {
                "document_id": row["document_id"],
                "title": row["title"],
                "source_type": row["source_type"],
                "document_kind": row["document_kind"],
                "published_date": row["published_date"],
                "source_status": row["source_status"],
                "prompt_injection_review_present": has_review,
                "locations": locations,
            }
        )
    entity_rows = [
        dict(row)
        for row in connection.execute(
            "SELECT d.document_id, e.name, e.entity_id, de.confidence, de.method "
            "FROM document_entities de JOIN entities e ON e.entity_id=de.entity_id "
            "JOIN documents d ON d.document_id=de.document_id "
            "WHERE e.name LIKE '%紫金%'"
        ).fetchall()
    ]
    return {
        "zijin_docs_total": len(rows),
        "zijin_docs_with_review": reviewed,
        "samples": samples[:20],
        "entity_links": entity_rows[:10],
        "queried_at_utc": utc_now(),
    }


def d1_sidecar_false_positives(connection: sqlite3.Connection) -> dict:
    """Audit finding 018: ``.pdf.source`` sidecar JSON promoted to an
    independent filing document (pollutes identity and processing queue)."""
    total = one(
        connection,
        "SELECT COUNT(*) FROM documents WHERE title LIKE '%.pdf.source%'",
    )
    as_filing_kinds = [
        dict(row)
        for row in connection.execute(
            "SELECT document_id, title, document_kind, published_date "
            "FROM documents WHERE title LIKE '%.pdf.source%' "
            f"AND document_kind IN {FILING_KINDS!r} ORDER BY title"
        ).fetchall()
    ]
    null_date = sum(1 for row in as_filing_kinds if not row.get("published_date"))
    return {
        "sidecar_titled_docs_total": total,
        "sidecar_titled_as_filing_kinds": len(as_filing_kinds),
        "sidecar_filing_kinds_with_null_published_date": null_date,
        "samples": as_filing_kinds[:15],
        "queried_at_utc": utc_now(),
    }


def d2_dayu_only_filings(connection: sqlite3.Connection) -> dict:
    """Audit finding 018: active dayu_portfolio-only filings that the
    companies-only default containment rejects at the filing boundary."""
    statuses = [
        tuple(row)
        for row in connection.execute(
            "SELECT DISTINCT location_status FROM locations ORDER BY location_status"
        )
    ]
    rows = [
        dict(row)
        for row in connection.execute(
            "SELECT d.document_id, d.title, d.document_kind, d.published_date "
            "FROM documents d "
            "JOIN locations l ON l.document_id=d.document_id "
            "  AND l.root_id='dayu_portfolio' AND l.location_status='active' "
            f"WHERE d.document_kind IN {FILING_KINDS!r} "
            "AND NOT EXISTS ("
            "  SELECT 1 FROM locations l2 WHERE l2.document_id=d.document_id "
            "  AND l2.root_id='company_raw' AND l2.location_status='active') "
            "ORDER BY d.document_kind, d.published_date"
        ).fetchall()
    ]
    by_kind: dict[str, int] = {}
    for row in rows:
        by_kind[row["document_kind"]] = by_kind.get(row["document_kind"], 0) + 1
    return {
        "location_statuses": statuses,
        "dayu_only_active_filing_docs": len(rows),
        "by_kind": by_kind,
        "samples": rows[:20],
        "queried_at_utc": utc_now(),
    }


def d3_dropbox_summary_review_gap(connection: sqlite3.Connection) -> dict:
    """Audit P06/finding 022: Dropbox documents with completed LLM summaries
    versus prompt-injection review coverage (P0 privacy gap)."""
    rows = [
        dict(row)
        for row in connection.execute(
            "SELECT d.document_id, d.metadata_json, a.generator_name "
            "FROM documents d "
            "JOIN locations l ON l.document_id=d.document_id "
            "  AND l.root_id='dropbox_stock' AND l.location_status='active' "
            "JOIN artifacts a ON a.document_id=d.document_id "
            "  AND a.artifact_role='summary' AND a.status='completed'"
        ).fetchall()
    ]
    reviewed = sum(1 for row in rows if _review_present(row.get("metadata_json")))
    generators: dict[str, int] = {}
    for row in rows:
        name = row.get("generator_name") or "unknown"
        generators[name] = generators.get(name, 0) + 1
    dropbox_docs_active = one(
        connection,
        "SELECT COUNT(DISTINCT document_id) FROM locations "
        "WHERE root_id='dropbox_stock' AND location_status='active'",
    )
    return {
        "dropbox_active_location_docs": dropbox_docs_active,
        "dropbox_docs_with_completed_summary": len(rows),
        "dropbox_docs_with_prompt_review": reviewed,
        "summary_generators": generators,
        "queried_at_utc": utc_now(),
    }


def catalog_snapshot(connection: sqlite3.Connection) -> dict:
    return {
        "documents": one(connection, "SELECT COUNT(*) FROM documents"),
        "active_documents": one(
            connection,
            "SELECT COUNT(*) FROM documents WHERE source_status='active'",
        ),
        "locations": one(connection, "SELECT COUNT(*) FROM locations"),
        "artifacts": one(connection, "SELECT COUNT(*) FROM artifacts"),
        "producer_events": one(connection, "SELECT COUNT(*) FROM producer_events"),
        "evidence_spans": one(connection, "SELECT COUNT(*) FROM evidence_spans"),
        "schema_version": one(
            connection,
            "SELECT value FROM catalog_meta WHERE key='schema_version'",
        ),
        "queried_at_utc": utc_now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path(DEFAULT_CATALOG))
    args = parser.parse_args()
    if not args.catalog.exists():
        print(f"catalog not found: {args.catalog}", file=sys.stderr)
        return 1
    stat = args.catalog.stat()
    before = (stat.st_size, stat.st_mtime_ns)
    connection = connect_ro(args.catalog)
    try:
        print("connected ro", flush=True)
        outputs = {}
        for name, fn in (
            ("zr001_catalog_snapshot.json", catalog_snapshot),
            ("w2_artifact_lineage.json", w2_artifact_lineage),
            ("w5_zijin_prompt_review.json", w5_zijin_prompt_review),
            ("d1_sidecar_false_positives.json", d1_sidecar_false_positives),
            ("d2_dayu_only_filings.json", d2_dayu_only_filings),
            ("d3_dropbox_summary_review_gap.json", d3_dropbox_summary_review_gap),
        ):
            print(f"query {name}", flush=True)
            outputs[name] = fn(connection)
    finally:
        connection.close()
    stat = args.catalog.stat()
    after = (stat.st_size, stat.st_mtime_ns)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        payload["catalog"] = {
            "path": str(args.catalog.resolve()),
            "size_before": before[0],
            "size_after": after[0],
            "mtime_ns_before": before[1],
            "mtime_ns_after": after[1],
            "unchanged_by_this_script": before == after,
        }
        path = EVIDENCE_DIR / name
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    for name in sorted(outputs):
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
