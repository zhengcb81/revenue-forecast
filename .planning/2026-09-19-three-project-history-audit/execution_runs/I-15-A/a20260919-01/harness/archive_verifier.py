"""I-15-A: scratch catalog + real archive construction and independent verification.

Everything here is synthetic and lives under the attempt directory.  The production
catalog (49.7 GB, `.source_catalog/catalog.sqlite3`) is never opened; `guard_scratch`
refuses any path that resolves into a product repo.

The archive is produced by the REAL product writer
(`company_wiki.source_catalog.archive_retired_evidence`), so the evidence is about the
product's actual output shape - but the *verification* of that output is done by
`verify_archive` below, which shares no code with the product writer.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sqlite3
import sys
import zlib
from pathlib import Path

EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
FORBIDDEN_PATH_PARTS = ("company-wiki", "revenue-forecast", "filing-fetch")


# ---------------------------------------------------------------------------
# binding guard
# ---------------------------------------------------------------------------


def guard_scratch(path: Path, product_repos: tuple[str, ...] = FORBIDDEN_PATH_PARTS) -> Path:
    """Refuse a scratch path that resolves into a product repo checkout.

    The attempt dir itself lives under `revenue-forecast/.planning/...`, so the guard
    checks for a *product* subtree marker rather than the repo name alone: the path must
    contain 'execution_runs' and must NOT contain '.source_catalog' or 'src\\company_wiki'.
    """
    resolved = Path(path).resolve()
    parts = [p.lower() for p in resolved.parts]
    if "execution_runs" not in parts:
        raise SystemExit(f"BINDING-REFUSED (not under execution_runs): {resolved}")
    tail = "/".join(parts[parts.index("execution_runs"):])
    if ".source_catalog" in parts or "src/company_wiki" in tail.replace("\\", "/"):
        raise SystemExit(f"BINDING-REFUSED (looks like a product path): {resolved}")
    return resolved


# ---------------------------------------------------------------------------
# the card's fixed sample
# ---------------------------------------------------------------------------
#
# Timeline the fixed sample implies (the card says "apply 前 A 仍 retired、C 已 active",
# so c1 must already have been archived while C was retired and C was reactivated after):
#
#   phase PRE  (at archive time)  doc-A retired {a1,a2} ; doc-C retired {c1}
#   ---- real archive_retired_evidence() runs here -> gzip contains a1,a2,c1 ----
#   phase POST (at prune time)    doc-A retired {a1,a2} + a3 added later
#                                 doc-B retired {b1}, never archived
#                                 doc-C active  {c1}, archived but no longer retired
#
# Total spans at prune time = 5.  The archive is a REAL product-written gzip.

NOW = "2026-09-19T00:00:00Z"
RETENTION_DAYS = 90
VERIFIED_COMPLETED_AT = "2026-05-01T00:00:00Z"

SAMPLE_DOCUMENTS = {
    "doc-A": ("retired", ["a1", "a2", "a3"]),
    "doc-B": ("retired", ["b1"]),
    "doc-C": ("active", ["c1"]),
}
PRE_ARCHIVE_DOCUMENTS = {
    "doc-A": ("retired", ["a1", "a2"]),
    "doc-C": ("retired", ["c1"]),
}
ARCHIVED_AT_TAKE = ["a1", "a2", "c1"]          # what the real archive contains
ADDED_AFTER_ARCHIVE = ["a3"]                    # retired document, span created later
NEVER_ARCHIVED = ["b1"]                         # retired document, no archive proof
EXPECTED_DELETE = ["a1", "a2"]
EXPECTED_RETAIN = ["a3", "b1", "c1"]

SPAN_ROWS = {
    # span_id: (document_id, locator, page, paragraph, table, raw_text, parse_status)
    "a1": ("doc-A", "doc-A#p1", 1, 0, None, "A first span text", "completed"),
    "a2": ("doc-A", "doc-A#p2", 2, 0, None, "A second span text", "completed"),
    "a3": ("doc-A", "doc-A#p3", 3, 0, None, "A span added AFTER the archive", "completed"),
    "b1": ("doc-B", "doc-B#p1", 1, 0, None, "B never archived", "completed"),
    "c1": ("doc-C", "doc-C#p1", 1, 0, None, "C active again", "completed"),
}
PARSER_NAME = "txt"
PARSER_VERSION = "1.0.0"


def span_json(span_id: str) -> str:
    return json.dumps({"span_id": span_id, "kind": "paragraph"}, sort_keys=True)


def _source_id(document_id: str) -> str:
    return f"src-{document_id[-1]}"


def _insert_documents(conn, documents: dict) -> None:
    for document_id, (status, _spans) in documents.items():
        conn.execute(
            """INSERT INTO documents(document_id, primary_source_id, title,
                   source_type, document_kind, published_date, source_status,
                   metadata_priority, metadata_json, text_fingerprint,
                   first_seen_at, last_seen_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (document_id, _source_id(document_id), f"scratch {document_id}",
             "filing", "annual_report", "2026-04-01", status, 1, "{}",
             f"fp-{document_id}", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
        )


def _insert_spans(conn, span_ids: list[str]) -> None:
    for span_id in span_ids:
        (document_id, locator, page, paragraph, table,
         raw_text, parse_status) = SPAN_ROWS[span_id]
        conn.execute(
            """INSERT INTO evidence_spans(span_id, document_id, source_id, locator,
                   page_number, paragraph_index, table_index, raw_text, span_json,
                   parser_name, parser_version, parse_status)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (span_id, document_id, _source_id(document_id), locator, page, paragraph,
             table, raw_text, span_json(span_id), PARSER_NAME, PARSER_VERSION,
             parse_status),
        )


def build_scratch_catalog(db_path: Path, documents: dict | None = None) -> Path:
    """Create a real scratch catalog with the product schema and the given documents."""
    documents = SAMPLE_DOCUMENTS if documents is None else documents
    db_path = guard_scratch(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    from company_wiki.source_catalog.store import CatalogStore

    CatalogStore(db_path)  # runs the product's own DDL/migrations

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        for index, source_id in enumerate(("src-A", "src-B", "src-C"), start=1):
            conn.execute(
                """INSERT INTO sources(source_id, content_sha256, byte_size, mime_type,
                       first_seen_at) VALUES(?,?,?,?,?)""",
                (source_id, hashlib.sha256(source_id.encode()).hexdigest(),
                 1024 * index, "text/plain", "2026-01-01T00:00:00Z"),
            )
        _insert_documents(conn, documents)
        for spans in documents.values():
            _insert_spans(conn, spans[1])
        conn.commit()
    finally:
        conn.close()
    return db_path


def advance_to_post_archive_state(db_path: Path) -> None:
    """Move the scratch catalog from archive time to prune time.

    Adds doc-B/b1 (retired, never archived), adds a3 to doc-A, and reactivates doc-C.
    """
    db_path = guard_scratch(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        _insert_documents(conn, {"doc-B": SAMPLE_DOCUMENTS["doc-B"]})
        _insert_spans(conn, ["b1", "a3"])
        conn.execute("UPDATE documents SET source_status='active' WHERE document_id='doc-C'")
        conn.execute("UPDATE locations SET location_status='active' WHERE document_id='doc-C'")
        conn.commit()
    finally:
        conn.close()


def live_span_ids(db_path: Path) -> list[str]:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT span_id FROM evidence_spans ORDER BY span_id").fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows]


def retired_span_ids(db_path: Path) -> list[str]:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            """SELECT span_id FROM evidence_spans WHERE document_id IN
               (SELECT document_id FROM documents WHERE source_status='retired')
               ORDER BY span_id""").fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows]


def row_digest(row: dict) -> str:
    """Independent row digest: canonical JSON, sorted keys, compact separators."""
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def live_row(db_path: Path, span_id: str) -> dict:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM evidence_spans WHERE span_id=?", (span_id,)).fetchone()
    finally:
        conn.close()
    return dict(row) if row is not None else {}


# ---------------------------------------------------------------------------
# real archive writer (product) + independent verifier (attempt-owned)
# ---------------------------------------------------------------------------


def write_real_archive(db_path: Path, archive_root: Path):
    db_path = guard_scratch(db_path)
    archive_root = guard_scratch(archive_root)
    from company_wiki.source_catalog.archive_retired_evidence import (
        archive_retired_evidence,
    )

    return archive_retired_evidence(db_path, archive_root)


def read_archive_rows(gz_path: Path) -> list[dict]:
    rows = []
    with gzip.open(gz_path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def verify_archive(
    gz_path: Path,
    *,
    expected_ids: list[str],
    expected_completed_at: str,
    write_manifest_to: Path | None = None,
) -> dict:
    """Independent verification of an archive file.  Shares no code with the writer.

    Returns a verdict dict; `ok` is False if any proof is missing.  This is the only
    thing allowed to authorise a deletion set in this attempt.
    """
    report: dict = {
        "archive_path": str(gz_path),
        "verifier": "harness/archive_verifier.py (attempt-owned, independent)",
        "problems": [],
    }
    if not gz_path.is_file():
        report["problems"].append("archive file missing")
        report["ok"] = False
        return report
    body = gz_path.read_bytes()
    report["archive_sha256"] = hashlib.sha256(body).hexdigest()
    report["archive_bytes"] = len(body)
    try:
        rows = read_archive_rows(gz_path)
    except (OSError, EOFError, zlib.error, json.JSONDecodeError) as exc:
        report["problems"].append(f"archive unreadable: {type(exc).__name__}: {exc}")
        report["ok"] = False
        return report
    report["rows_in_archive"] = len(rows)
    ids = [r.get("span_id") for r in rows]
    report["duplicate_span_ids"] = sorted({i for i in ids if ids.count(i) > 1})
    if report["duplicate_span_ids"]:
        report["problems"].append("duplicate span ids in archive")
    digests = {r["span_id"]: row_digest(r) for r in rows}
    missing = sorted(set(expected_ids) - set(digests))
    if missing:
        report["problems"].append(f"expected ids absent from archive: {missing}")
    report["row_digests"] = digests
    report["expected_ids"] = sorted(expected_ids)
    report["verified_completed_at"] = expected_completed_at
    report["schema_version"] = "archive-verified-manifest-1.0"
    report["catalog_identity"] = "scratch-catalog-i15a"
    report["ok"] = not report["problems"]
    if write_manifest_to is not None:
        write_manifest_to = guard_scratch(write_manifest_to)
        manifest = {
            "schema_version": report["schema_version"],
            "catalog_identity": report["catalog_identity"],
            "archive_path": report["archive_path"],
            "archive_sha256": report["archive_sha256"],
            "archive_bytes": report["archive_bytes"],
            "rows_in_archive": report["rows_in_archive"],
            "verified_completed_at": expected_completed_at,
            "span_ids": sorted(digests),
            "row_digests": digests,
            "verifier": report["verifier"],
            "problems": report["problems"],
            "ok": report["ok"],
        }
        write_manifest_to.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        report["manifest_path"] = str(write_manifest_to)
    return report


def plan_hash(span_ids: list[str], archive_sha256: str, verified_completed_at: str,
              retention_days: int) -> str:
    """Attempt-owned exact-set plan hash (W15-R4).  Never produced by the product."""
    payload = json.dumps({
        "schema_version": "exact-prune-plan-1.0",
        "archive_sha256": archive_sha256,
        "verified_completed_at": verified_completed_at,
        "retention_days": retention_days,
        "span_ids": sorted(span_ids),
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def select_prunable_ids(db_path: Path, verified_row_digests: dict) -> dict:
    """Apply W15-R2 independently: archived AND still present AND still retired.

    `in_archive_not_retired` is the important output: those ids are inside the verified
    archive but must NOT be deleted, because the archive is evidence, not a licence.
    """
    db_path = guard_scratch(db_path)
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        current = {r["span_id"]: (r["document_id"], r["source_status"])
                   for r in conn.execute(
                       """SELECT e.span_id, e.document_id, d.source_status
                          FROM evidence_spans e
                          JOIN documents d ON d.document_id = e.document_id""")}
    finally:
        conn.close()
    in_archive = set(verified_row_digests)
    present_and_retired = {sid for sid, (_doc, status) in current.items()
                           if status == "retired"}
    return {
        "in_archive": sorted(in_archive),
        "in_archive_and_retired": sorted(in_archive & present_and_retired),
        "in_archive_not_retired": sorted(in_archive - present_and_retired),
        "retired_not_in_archive": sorted(present_and_retired - in_archive),
        "prunable": sorted(in_archive & present_and_retired),
    }


def add_product_src(src: str) -> None:
    if src not in sys.path:
        sys.path.insert(0, src)
