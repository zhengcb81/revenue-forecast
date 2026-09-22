"""DW15-REPAIR fixtures: synthetic scratch catalogs + variant-aware call helpers.

All fixtures are SYNTHETIC and live under pytest's tmp_path (%TEMP%); nothing
here ever opens a product repo path or a `.source_catalog` directory.

Fixture construction is adapted from I-15-A's attempt-owned harness
(`execution_runs/I-15-A/a20260919-01/harness/archive_verifier.py`, read-only),
which itself builds the card's fixed sample:

  phase PRE   doc-A retired {a1,a2}; doc-C retired {c1}   -> archive here
  phase POST  + doc-B retired {b1}; + a3; doc-C active     -> prune here

EXPECTED_DELETE / EXPECTED_RETAIN are PRE-LISTED here (and in oracle.md); they
are never derived from the scripts' own reports.
"""
from __future__ import annotations

import gzip
import hashlib
import inspect
import json
import sqlite3
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
ATTEMPT = HARNESS.parent
if str(ATTEMPT) not in sys.path:
    sys.path.insert(0, str(ATTEMPT))

NOW_ARCHIVE = datetime(2026, 5, 1, tzinfo=timezone.utc)
NOW_PRUNE = datetime(2026, 9, 19, tzinfo=timezone.utc)
NOW_FRESH = datetime(2026, 9, 18, tzinfo=timezone.utc)   # 1 day before NOW_PRUNE
RETENTION_DAYS = 90

SAMPLE_DOCUMENTS = {
    "doc-A": ("retired", ["a1", "a2", "a3"]),
    "doc-B": ("retired", ["b1"]),
    "doc-C": ("active", ["c1"]),
}
PRE_ARCHIVE_DOCUMENTS = {
    "doc-A": ("retired", ["a1", "a2"]),
    "doc-C": ("retired", ["c1"]),
}
ARCHIVED_AT_TAKE = ["a1", "a2", "c1"]
EXPECTED_DELETE = ["a1", "a2"]
EXPECTED_RETAIN = ["a3", "b1", "c1"]
ALL_SPANS = ["a1", "a2", "a3", "b1", "c1"]
# retired spans a snapshot taken over the POST-state catalog must contain:
RETIRED_AT_TAKE = ["a1", "a2", "a3", "b1"]

SPAN_ROWS = {
    "a1": ("doc-A", "doc-A#p1", 1, 0, None, "A first span text", "completed"),
    "a2": ("doc-A", "doc-A#p2", 2, 0, None, "A second span text", "completed"),
    "a3": ("doc-A", "doc-A#p3", 3, 0, None, "A span added AFTER the archive", "completed"),
    "b1": ("doc-B", "doc-B#p1", 1, 0, None, "B never archived", "completed"),
    "c1": ("doc-C", "doc-C#p1", 1, 0, None, "C active again", "completed"),
}
PARSER_NAME = "txt"
PARSER_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# binding guard: temp dirs + this attempt only, never a product path
# ---------------------------------------------------------------------------

def guard_scratch(path: Path) -> Path:
    resolved = Path(path).resolve()
    parts = [p.lower() for p in resolved.parts]
    if ".source_catalog" in parts:
        raise SystemExit(f"BINDING-REFUSED (production catalog path): {resolved}")
    temp_root = Path(tempfile.gettempdir()).resolve()
    under_temp = resolved == temp_root or temp_root in resolved.parents
    under_attempt = resolved == ATTEMPT.resolve() or ATTEMPT.resolve() in resolved.parents
    if not (under_temp or under_attempt):
        raise SystemExit(
            f"BINDING-REFUSED (not under %TEMP% or this attempt): {resolved}")
    if not under_attempt and "execution_runs" in parts:
        raise SystemExit(f"BINDING-REFUSED (foreign attempt dir): {resolved}")
    return resolved


# ---------------------------------------------------------------------------
# scratch catalog builders (product DDL via CatalogStore, data synthetic)
# ---------------------------------------------------------------------------

def _span_json(span_id: str) -> str:
    return json.dumps({"span_id": span_id, "kind": "paragraph"}, sort_keys=True)


def _source_id(document_id: str) -> str:
    return f"src-{document_id[-1]}"


def build_scratch_catalog(db_path: Path, documents: dict | None = None) -> Path:
    documents = SAMPLE_DOCUMENTS if documents is None else documents
    db_path = guard_scratch(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    from company_wiki.source_catalog.store import CatalogStore

    CatalogStore(db_path)                      # product DDL/migrations

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        for index, source_id in enumerate(("src-A", "src-B", "src-C"), start=1):
            conn.execute(
                "INSERT INTO sources(source_id, content_sha256, byte_size, "
                "mime_type, first_seen_at) VALUES(?,?,?,?,?)",
                (source_id, hashlib.sha256(source_id.encode()).hexdigest(),
                 1024 * index, "text/plain", "2026-01-01T00:00:00Z"))
        for document_id, (status, _spans) in documents.items():
            conn.execute(
                "INSERT INTO documents(document_id, primary_source_id, title, "
                "source_type, document_kind, published_date, source_status, "
                "metadata_priority, metadata_json, text_fingerprint, "
                "first_seen_at, last_seen_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (document_id, _source_id(document_id), f"scratch {document_id}",
                 "filing", "annual_report", "2026-04-01", status, 1, "{}",
                 f"fp-{document_id}", "2026-01-01T00:00:00Z",
                 "2026-01-01T00:00:00Z"))
        for spans in documents.values():
            _insert_spans(conn, spans[1])
        conn.commit()
    finally:
        conn.close()
    return db_path


def _insert_spans(conn, span_ids) -> None:
    for span_id in span_ids:
        (document_id, locator, page, paragraph, table,
         raw_text, parse_status) = SPAN_ROWS[span_id]
        conn.execute(
            "INSERT INTO evidence_spans(span_id, document_id, source_id, locator, "
            "page_number, paragraph_index, table_index, raw_text, span_json, "
            "parser_name, parser_version, parse_status) "
            "VALUES(:span_id,:document_id,:source_id,:locator,:page_number,"
            ":paragraph_index,:table_index,:raw_text,:span_json,:parser_name,"
            ":parser_version,:parse_status)",
            {"span_id": span_id, "document_id": document_id,
             "source_id": _source_id(document_id), "locator": locator,
             "page_number": page, "paragraph_index": paragraph,
             "table_index": table, "raw_text": raw_text,
             "span_json": _span_json(span_id), "parser_name": PARSER_NAME,
             "parser_version": PARSER_VERSION, "parse_status": parse_status})


def advance_to_post_archive_state(db_path: Path) -> None:
    """PRE -> POST: +doc-B/b1, +a3, doc-C back to active."""
    db_path = guard_scratch(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute(
            "INSERT INTO documents(document_id, primary_source_id, title, "
            "source_type, document_kind, published_date, source_status, "
            "metadata_priority, metadata_json, text_fingerprint, "
            "first_seen_at, last_seen_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            ("doc-B", "src-B", "scratch doc-B", "filing", "annual_report",
             "2026-04-01", "retired", 1, "{}", "fp-doc-B",
             "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"))
        _insert_spans(conn, ["b1", "a3"])
        conn.execute("UPDATE documents SET source_status='active' "
                     "WHERE document_id='doc-C'")
        conn.execute("UPDATE locations SET location_status='active' "
                     "WHERE document_id='doc-C'")
        conn.commit()
    finally:
        conn.close()


def live_span_ids(db_path: Path) -> list[str]:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return [r[0] for r in conn.execute(
            "SELECT span_id FROM evidence_spans ORDER BY span_id")]
    finally:
        conn.close()


def live_row(db_path: Path, span_id: str) -> dict:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT * FROM evidence_spans WHERE span_id=?",
                           (span_id,)).fetchone()
    finally:
        conn.close()
    if row is None:
        raise KeyError(span_id)
    return dict(row)


def row_digest(row: dict) -> str:
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def make_config(db_path: Path):
    db_path = guard_scratch(db_path)
    from company_wiki.source_catalog.models import CatalogConfig, RootSpec
    scratch_root = db_path.parent / "roots"
    scratch_root.mkdir(parents=True, exist_ok=True)
    return CatalogConfig(
        project_root=db_path.parent.parent,
        catalog_dir=db_path.parent,
        roots=(RootSpec("scratch", scratch_root, "directory"),),
    )


def receipts_for(config) -> list[Path]:
    gates = config.catalog_dir / "artifacts" / "gates"
    if not gates.is_dir():
        return []
    # deliberately no '-' after 'retired': the instrument must observe BOTH the
    # repaired unique names (prune-retired-<token>.json) and the reverted fixed
    # name (prune-retired.json); '.partial-*' residue never ends in '.json'.
    return sorted(gates.glob("prune-retired*.json"))


# ---------------------------------------------------------------------------
# hand-built verified manifest trees (attempt writes them; digests of REAL
# scratch rows, so they verify exactly like product-written manifests)
# ---------------------------------------------------------------------------

def write_manifest_tree(db_path: Path, archive_root: Path, day: str,
                        span_ids: list[str], verified_completed_at: str) -> Path:
    day_dir = guard_scratch(archive_root / "archive" / day)
    day_dir.mkdir(parents=True, exist_ok=True)
    rows = [live_row(db_path, span_id) for span_id in span_ids]
    body = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    gz_bytes = gzip.compress(body.encode("utf-8"))
    snapshot = day_dir / f"retired-evidence-manual{uuid.uuid4().hex[:8]}.jsonl.gz"
    snapshot.write_bytes(gz_bytes)
    digests = {row["span_id"]: row_digest(row) for row in rows}
    manifest = {
        "schema_version": "archive-verified-manifest-1.0",
        "catalog_identity": f"{Path(db_path).name}:synthetic",
        "archive_path": str(snapshot.resolve()),
        "archive_sha256": hashlib.sha256(gz_bytes).hexdigest(),
        "archive_bytes": len(gz_bytes),
        "rows_in_archive": len(rows),
        "verified_completed_at": verified_completed_at,
        "span_ids": sorted(digests),
        "row_digests": {k: digests[k] for k in sorted(digests)},
        "verifier": "attempt fixture (synthetic tree under %TEMP%)",
        "problems": [],
        "ok": True,
    }
    manifest_path = snapshot.with_name(snapshot.name + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                             encoding="utf-8")
    return manifest_path


# ---------------------------------------------------------------------------
# variant-aware call helpers: fall back to the original signature so the
# ORIGINAL code runs its real behaviour (behavioural RED, not a TypeError)
# ---------------------------------------------------------------------------

def _accepts(func, name: str) -> bool:
    try:
        return name in inspect.signature(func).parameters
    except (TypeError, ValueError):
        return False


def call_archive(db_path: Path, archive_root: Path, *, now: datetime,
                 progress=None):
    from company_wiki.source_catalog import archive_retired_evidence as module
    kwargs = {}
    if _accepts(module.archive_retired_evidence, "now"):
        kwargs["now"] = now
    if progress is not None and _accepts(module.archive_retired_evidence,
                                         "progress"):
        kwargs["progress"] = progress
    return module.archive_retired_evidence(db_path, archive_root, **kwargs)


def call_prune(config, archive_root, *, now: datetime, apply: bool = False,
               retention_days: int = RETENTION_DAYS, plan=None):
    from company_wiki.source_catalog import prune_retired_evidence as module
    kwargs = {"apply": apply, "retention_days": retention_days}
    if _accepts(module.prune_retired_evidence, "now"):
        kwargs["now"] = now
    if plan is not None and _accepts(module.prune_retired_evidence, "plan"):
        kwargs["plan"] = plan
    return module.prune_retired_evidence(config, archive_root, **kwargs)


def prune_module():
    from company_wiki.source_catalog import prune_retired_evidence as module
    return module


def pre_to_post_case(tmp_path: Path) -> dict:
    """PRE state -> real product archive at NOW_ARCHIVE -> POST state.

    Adds an empty decoy directory dated 2026-05-01 so the ORIGINAL code (which
    authorises by directory age) reaches its delete path: its RED then comes
    from *what* it deletes / that it deletes at all, not from a clock accident.
    The repaired code ignores directory names entirely.
    """
    db = build_scratch_catalog(tmp_path / "catalog" / "catalog.sqlite3",
                               PRE_ARCHIVE_DOCUMENTS)
    archive_root = tmp_path / "manifests"
    report = call_archive(db, archive_root, now=NOW_ARCHIVE)
    advance_to_post_archive_state(db)
    (archive_root / "archive" / "2026-05-01").mkdir(parents=True, exist_ok=True)
    return {
        "db": db,
        "archive_root": archive_root,
        "config": make_config(db),
        "archive_report": report,
        "archive_path": Path(report.archive_path)
        if hasattr(report, "archive_path") else None,
    }
