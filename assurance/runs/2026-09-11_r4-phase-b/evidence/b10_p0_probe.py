"""P0 verification (B-VR-B10R2-01): ONE malformed documents.metadata_json must not abort the run.

The fixture is the reviewer's `p_normalize_abort.py` construction, kept identical so the
before/after readings are comparable: a throwaway catalog under %TEMP% built through the
product's own CatalogStore, seeded with the minimum rows the queue needs, one document whose
`metadata_json` is `not json at all`.  Before the fix this escaped as JSONDecodeError raised
from normalizer.py:1638 with nothing recorded; the reviewer's probe is the "before" reading.

Phase 2 adds a REAL .md file for the location, because after the fix execution gets past the
parse and the interesting question becomes what the produced artifact records - the reviewer's
B-VR-B10R2-03 (P1) was that the degradation was invisible (identity "consistent", no flag).

Read-only w.r.t. production: everything happens under %TEMP%.

    python b10_p0_probe.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

WIKI_SRC = Path(__file__).resolve().parents[4] / "company-wiki" / "src"
sys.path.insert(0, str(WIKI_SRC))

from company_wiki.source_catalog.config import CatalogConfig  # noqa: E402
from company_wiki.source_catalog.models import RootSpec  # noqa: E402
from company_wiki.source_catalog.normalizer import normalize_catalog  # noqa: E402
from company_wiki.source_catalog.store import CatalogStore  # noqa: E402
from company_wiki.source_contract.source_manifest import source_id_for_sha256  # noqa: E402

ROOT = "urn:company-wiki:root:sha256:" + "r" * 64
DOC = "urn:company-wiki:document:sha256:" + "d" * 64
SHA = "c" * 64
SRC = source_id_for_sha256(SHA)
MANIFEST = {
    "schema_version": "1.0.0", "source_id": SRC, "entity_ids": ["test-issuer"],
    "original_path": "reports/x.md", "content_sha256": SHA,
    "source_type": "regulatory_filing", "published_date": "2026-06-18",
    "retrieved_at": "2026-06-18T00:00:00Z", "collector_name": "probe",
    "collector_version": "1.0.0", "mime_type": "text/markdown", "byte_size": 10,
    "immutable_status": "verified",
}


def _insert(connection, table: str, values: dict) -> None:
    have = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    use = {key: value for key, value in values.items() if key in have}
    columns = ",".join(use)
    marks = ",".join("?" * len(use))
    connection.execute(f"INSERT INTO {table} ({columns}) VALUES ({marks})",
                       tuple(use.values()))


def _seed(tmp: Path, *, payload: bytes | None,
          write: bool = True) -> tuple[CatalogConfig, CatalogStore, Path]:
    database = tmp / "catalog.sqlite3"
    if database.exists():
        database.unlink()
    raw = tmp / "raw" / "reports"
    raw.mkdir(parents=True, exist_ok=True)
    target = raw / "x.md"
    if payload is not None and write:
        target.write_bytes(payload)
    # The manifest must agree with the bytes ON DISK or IngestService refuses later with
    # "source byte_size no longer matches manifest" - my first fixture hard-coded 10 bytes and
    # the probe reported that unrelated mismatch as an escape (recorded, because it cost a
    # run to notice).
    body = payload if payload is not None else b""
    import hashlib

    digest = hashlib.sha256(body).hexdigest()
    size = len(body)
    manifest = {**MANIFEST, "content_sha256": digest, "byte_size": size}
    source_id = source_id_for_sha256(digest)
    manifest["source_id"] = source_id
    config = CatalogConfig(
        project_root=tmp, catalog_dir=tmp / "catalog",
        roots=(RootSpec(root_id=ROOT, path=tmp / "raw", kind="company_raw", priority=1),),
    )
    store = CatalogStore(database)
    with store.transaction() as connection:
        _insert(connection, "roots", {"root_id": ROOT, "path": str(tmp / "raw"),
                                      "kind": "company_raw", "priority": 1})
        _insert(connection, "sources", {
            "source_id": source_id, "content_sha256": digest, "byte_size": size,
            "mime_type": "text/markdown", "relative_path": "reports/x.md", "root_id": ROOT,
            "source_type": "regulatory_filing", "source_status": "active",
            "first_seen_at": "2026-01-01T00:00:00Z", "last_seen_at": "2026-01-01T00:00:00Z"})
        _insert(connection, "documents", {
            "document_id": DOC, "primary_source_id": source_id, "title": "Test Filing",
            "source_type": "regulatory_filing", "document_kind": "annual_report",
            "published_date": "2026-06-18", "source_status": "active", "metadata_priority": 1,
            "metadata_json": "not json at all",  # the malformed column under test
            "first_seen_at": "2026-01-01T00:00:00Z", "last_seen_at": "2026-01-01T00:00:00Z"})
        _insert(connection, "locations", {
            "location_id": "loc-1", "root_id": ROOT, "relative_path": "reports/x.md",
            "absolute_path": str(target), "source_id": source_id, "document_id": DOC,
            "role": "original_primary", "location_status": "active", "last_seen_run": "run-1",
            "manifest_json": json.dumps(manifest), "metadata_json": "{}"})
    return config, store, target


def _run(label: str, tmp: Path, payload: bytes | None, *, write: bool = True) -> dict:
    config, store, _ = _seed(tmp, payload=payload, write=write)
    outcome: dict = {"label": label}
    try:
        report = normalize_catalog(config, store, force=True, retry_limit=3)
        outcome["escaped"] = False
        outcome["failure_reasons"] = dict(getattr(report, "failure_reasons", {}) or {})
        outcome["failed"] = getattr(report, "failed", None)
    except BaseException as exc:  # noqa: BLE001 - the probe reports whatever escapes
        outcome["escaped"] = True
        outcome["error"] = f"{type(exc).__name__}: {str(exc)[:120]}"
        for frame in traceback.extract_tb(sys.exc_info()[2]):
            if "normalizer.py" in frame.filename:
                outcome["raised_from"] = f"normalizer.py:{frame.lineno} {frame.line}"
    return outcome


def main() -> int:
    base = Path(tempfile.gettempdir()) / "b10p0probe"
    base.mkdir(parents=True, exist_ok=True)
    body = b"# Test Filing\n\nbody text\n"

    print("=== phase 1: valid manifest, NO file on disk (the reviewer's shape) ===")
    first = _run("phase1", base / "p1", payload=body, write=False)
    print(json.dumps(first, ensure_ascii=True, indent=2))

    print("=== phase 2: the same file written, so normalization runs to completion ===")
    second = _run("phase2", base / "p2", payload=body, write=True)
    print(json.dumps(second, ensure_ascii=True, indent=2))

    produced = sorted((base / "p2" / "catalog").rglob("normalized.md"))
    if produced:
        text = produced[0].read_text(encoding="utf-8")
        print("produced artifact:", produced[0].name)
        print("  has metadata_unreadable flag:", "metadata_unreadable" in text)
        print("  verdict consistent           :", "verdict: consistent" in text)
        print("  verdict unverifiable         :", "verdict: unverifiable" in text)
        second["artifact_flagged"] = "metadata_unreadable" in text
        second["artifact_verdict_downgraded"] = (
            "verdict: unverifiable" in text and "verdict: consistent" not in text)
    else:
        print("no normalized.md produced in phase 2")
        second["artifact_flagged"] = None

    # Phase 1 is informational: a MISSING primary file surfaces in the unsupported-document
    # handler (a separate, pre-existing behaviour, recorded below).  What matters for this P0
    # is that the escape is NOT the metadata parse any more - no JSONDecodeError and no
    # normalizer.py:1638 in the traceback.
    first_escaped_at_parse = (
        first.get("escaped") and ("JSONDecodeError" in str(first.get("error", ""))
                                  or "1638" in str(first.get("raised_from", "")))
    )
    ok = ((not second["escaped"]) and bool(second.get("artifact_flagged"))
          and bool(second.get("artifact_verdict_downgraded")) and not first_escaped_at_parse)
    print("\nphase 1 escape (informational):", first.get("error", "<none>"))
    print("P0 VERDICT:", "FIXED (the parse no longer escapes; degradation is visible)" if ok
          else "STILL BROKEN or undemonstrated - read the readings above")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
