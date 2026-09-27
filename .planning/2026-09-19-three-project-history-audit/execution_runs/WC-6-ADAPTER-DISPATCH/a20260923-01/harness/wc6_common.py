"""WC-6 shared helpers (nine-step steps 2/3/5). READ-ONLY against live CW.

Everything this card writes lives under <attempt>/evidence, <attempt>/iso or
%TEMP%\\wc6\\cells\\probes.  The product code under test is imported via
PYTHONPATH=<attempt>/iso/cw/src (byte-identical to live CW until step 6).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
ISO_CW = ATT / "iso" / "cw"
ISO_SRC = ISO_CW / "src"
INPUTS = ATT / "inputs"
EVID = ATT / "evidence"
CASES = Path(os.environ.get("TEMP", r"C:\Temp")) / "wc6" / "cells"

AS_OF_DEFAULT = "2026-09-23"

#: oracle §4: time/id-derived keys stripped before byte-comparison (declared, not hidden)
VOLATILE_MARKERS = (
    "_at", "_time", "run_id", "started", "completed", "mtime",
    "retrieved", "last_seen", "first_seen", "scan_time", "now",
)

#: oracle §4 outcome allowlists (explicit columns, in this order)
LOCATION_OUTCOME = (
    "root_id", "relative_path", "absolute_path", "source_id", "document_id",
    "role", "location_status", "observed_size", "metadata_json",
)
SOURCE_OUTCOME = ("source_id", "content_sha256", "byte_size", "mime_type")
DOCUMENT_OUTCOME = (
    "document_id", "document_kind", "source_status", "title",
    "primary_source_id", "published_date", "metadata_priority", "metadata_json",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=False),
        encoding="utf-8",
    )


def q(path: Path) -> str:
    """Single-quoted YAML scalar: backslashes stay literal."""
    return "'" + str(path).replace("'", "''") + "'"


def load_fixture() -> dict:
    return read_json(INPUTS / "probe_fixture.json")


def iso_schema(cwroot: Path) -> dict:
    """Create the isolated catalog with the PRODUCT's own initializer."""
    cat_dir = cwroot / ".source_catalog"
    cat_dir.mkdir(parents=True, exist_ok=True)
    from company_wiki.source_catalog.store import CatalogStore

    store = CatalogStore(cat_dir / "catalog.sqlite3")
    store._initialize()
    con = sqlite3.connect(cat_dir / "catalog.sqlite3")
    tabs = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    con.close()
    return {"catalog": str(cat_dir / "catalog.sqlite3"),
            "table_count": len(tabs), "tables": tabs,
            "created_by": "company_wiki.source_catalog.store.CatalogStore._initialize"}


def strip_volatile(obj):
    """Drop time/id-derived keys (oracle §4 declared exclusions)."""
    if isinstance(obj, dict):
        return {
            k: strip_volatile(v) for k, v in obj.items()
            if not any(marker in k for marker in VOLATILE_MARKERS)
        }
    if isinstance(obj, list):
        return [strip_volatile(v) for v in obj]
    return obj


def dump_catalog(cwroot: Path) -> dict:
    """Read-only dump of the ISOLATED catalog (never production)."""
    cat = cwroot / ".source_catalog" / "catalog.sqlite3"
    if not cat.is_file():
        return {"catalog": str(cat), "exists": False}
    con = sqlite3.connect(f"file:{cat}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    con.row_factory = sqlite3.Row
    out: dict = {"catalog": str(cat), "exists": True}
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    out["table_count"] = len(tables)
    out["counts"] = {
        t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        for t in tables
    }
    out["roots"] = [dict(r) for r in con.execute(
        "SELECT root_id,path,kind,priority FROM roots ORDER BY priority")]
    out["sources"] = [dict(r) for r in con.execute(
        "SELECT source_id,content_sha256,byte_size,mime_type FROM sources "
        "ORDER BY source_id")]
    out["documents"] = [dict(r) for r in con.execute(
        "SELECT document_id,document_kind,source_status,title,primary_source_id,"
        " published_date,metadata_priority,metadata_json,source_type FROM documents"
        " ORDER BY document_id")]
    out["locations"] = [dict(r) for r in con.execute(
        "SELECT location_id,root_id,relative_path,absolute_path,source_id,"
        "document_id,role,location_status,observed_size,observed_mtime_ns,"
        "last_seen_run,manifest_json,metadata_json,error FROM locations"
        " ORDER BY root_id,relative_path")]
    out["entities"] = [dict(r) for r in con.execute(
        "SELECT entity_id,name,entity_kind FROM entities ORDER BY entity_id")]
    out["document_entities"] = [dict(r) for r in con.execute(
        "SELECT document_id,entity_id,confidence,method FROM document_entities"
        " ORDER BY document_id,entity_id")]
    out["scan_runs"] = [dict(r) for r in con.execute(
        "SELECT run_id,status,report_json FROM scan_runs ORDER BY rowid")]
    con.close()
    return out


def _norm_json_column(value):
    """Normalize a `<name>_json` TEXT column: parse, strip volatile keys,
    re-dump canonically.  Measured need: documents.metadata_json embeds
    r4_provenance entries carrying `observed_at` wall-clock stamps, so two runs
    of byte-identical code differ in that string otherwise.  Unparseable or
    non-object payloads pass through untouched (a difference there stays a
    difference)."""
    if not isinstance(value, str) or not value:
        return value
    try:
        parsed = json.loads(value)
    except ValueError:
        return value
    if not isinstance(parsed, dict):
        return value
    return json.dumps(strip_volatile(parsed), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def _normalize_json_columns(obj):
    if isinstance(obj, dict):
        return {
            k: (_norm_json_column(v) if k.endswith("_json") and isinstance(v, str)
                else _normalize_json_columns(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_normalize_json_columns(v) for v in obj]
    return obj


def normalized(dump: dict) -> dict:
    """Split a dump into (a) byte-comparable OUTCOME per oracle §4 and
    (b) the DIAGNOSTIC payload under test (`locations.error`)."""
    diagnostic = {
        row["relative_path"]: row.get("error") for row in dump.get("locations", [])
    }
    outcome = {
        "counts": dump.get("counts"),
        "table_count": dump.get("table_count"),
        "roots": dump.get("roots"),
        "sources": [
            {k: row.get(k) for k in SOURCE_OUTCOME} for row in dump.get("sources", [])
        ],
        "documents": [
            {k: row.get(k) for k in DOCUMENT_OUTCOME} for row in dump.get("documents", [])
        ],
        "locations": [
            {k: row.get(k) for k in LOCATION_OUTCOME} for row in dump.get("locations", [])
        ],
        "entities": dump.get("entities"),
        "document_entities": dump.get("document_entities"),
        "scan_reports": [
            strip_volatile(json.loads(run.get("report_json") or "{}"))
            for run in dump.get("scan_runs", [])
        ],
        "scan_run_statuses": [run.get("status") for run in dump.get("scan_runs", [])],
    }
    return {"outcome": _normalize_json_columns(outcome), "diagnostic": diagnostic}


def tree_manifest(root: Path) -> dict:
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            out[path.relative_to(root).as_posix()] = {
                "sha256": sha256_file(path), "bytes": path.stat().st_size}
    return out


#: same bounded scope as pin_sources (src/ + tests/ + config pins) for diffing
SUBTREES = ("src", "tests")
EXTRA_FILES = (
    "config/source_catalog.yaml",
    "config/source_acquisition.yaml",
    "config/source_catalog_worker.yaml",
)


def manifest_paths(root: Path) -> dict:
    out: dict[str, dict] = {}
    for sub in SUBTREES:
        base = root / sub
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            rel = path.relative_to(root).as_posix()
            out[rel] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    for rel in EXTRA_FILES:
        path = root / rel
        if path.is_file():
            out[rel] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    return out


def copy_support_files(cwroot: Path) -> dict:
    """Read-only copies of product config + security master into the cell."""
    cfg = cwroot / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    copied = {}
    for name in ("source_acquisition.yaml", "source_catalog_worker.yaml"):
        src = CW / "config" / name
        if src.is_file():
            shutil.copy2(src, cfg / name)
            copied[name] = sha256_file(cfg / name)
    sm_src = CW / ".source_catalog" / "security_master"
    sm_dst = cwroot / ".source_catalog" / "security_master"
    sm_files = []
    if sm_src.is_dir():
        shutil.copytree(sm_src, sm_dst, dirs_exist_ok=True)
        sm_files = sorted(p.name for p in sm_dst.glob("*.json"))
    return {"configs": copied, "security_master_files": sm_files}
