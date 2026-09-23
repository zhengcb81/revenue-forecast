"""I-07-C shared helpers. ASCII-only source by contract: clause 5 requires that
NO company identifier is hardcoded in this card's construction code. Every
company/asset name is derived at runtime from sample_manifest.json, the sidecars
this harness copies, or inputs/fifth_root_company.json (data file, disclosed).
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
FF = Path(r"C:\Users\郑曾波\Projects\filing-fetch")
PLAN = RF / ".planning" / "2026-09-19-three-project-history-audit"
MANIFEST = PLAN / "execution_v2" / "sample_manifest.json"
INPUTS = ATT / "inputs"
EVID = ATT / "evidence"
CASES = Path(os.environ.get("TEMP", r"C:\Temp")) / "i07c" / "cells"

AS_OF = "2026-09-23"          # bound as_of_date for every resolve in this card
PROD_CATALOG = CW / ".source_catalog" / "catalog.sqlite3"
PROD_CONFIG = CW / "config" / "source_catalog.yaml"

CELLS = [
    "X04-multiroot",
    "X05-fifthroot",
    "UNK-adapter",
    "UNK-sidecar",
    "UNK-kind",
    "X01-companies-only",
    "X02-dayu-only",
]
# X03-external-only deliberately has NO cell: blocked for lack of a sample.


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def samples() -> list[dict]:
    """Manifest samples with derived entity dir + kind dir (no literals here)."""
    out = []
    for s in load_manifest()["samples"]:
        raw = Path(s["path"])
        parts = raw.parts
        try:
            ci = [i for i, p in enumerate(parts) if p == "companies"][0]
            entity_dir = parts[ci + 1]
        except IndexError as exc:  # pragma: no cover - manifest shape drift
            raise SystemExit(f"cannot derive entity dir from {raw}") from exc
        out.append(
            {
                "id": s["id"],
                "market": s["market"],
                "raw": raw,
                "sidecar": Path(s["sidecar"]),
                "raw_sha256": s["sha256"],
                "byte_size": s["byte_size"],
                "entity_dir": entity_dir,
                "kind_dir": raw.parts[-2],
                "file_name": raw.name,
            }
        )
    return out


def sample_smallest() -> dict:
    return min(samples(), key=lambda s: s["byte_size"])


def sample_by_market(market: str) -> dict:
    hits = [s for s in samples() if s["market"] == market]
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one sample for market {market!r}, got {len(hits)}")
    return hits[0]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")


def copy_checked(src: Path, dst: Path) -> dict:
    import shutil

    dst.parent.mkdir(parents=True, exist_ok=True)
    before = sha256_file(src)
    shutil.copy2(src, dst)
    after = sha256_file(dst)
    return {"src": str(src), "dst": str(dst), "src_sha256": before,
            "dst_sha256": after, "match": before == after, "bytes": dst.stat().st_size}


def iso_schema(cwroot: Path) -> dict:
    """Create the isolated catalog with the PRODUCT's own initializer (18 tables)."""
    cat_dir = cwroot / ".source_catalog"
    cat_dir.mkdir(parents=True, exist_ok=True)
    from company_wiki.source_catalog.store import CatalogStore

    store = CatalogStore(cat_dir / "catalog.sqlite3")
    store._initialize()
    con = sqlite3.connect(cat_dir / "catalog.sqlite3")
    tabs = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    con.close()
    return {"catalog": str(cat_dir / "catalog.sqlite3"), "tables": tabs,
            "table_count": len(tabs),
            "created_by": "company_wiki.source_catalog.store.CatalogStore._initialize (product code)"}


def copy_support_files(cwroot: Path) -> dict:
    """Security-master snapshots + acquisition/worker configs (read-only copies)."""
    import shutil

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
    out["counts"] = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
                     for t in tables}
    out["roots"] = [dict(r) for r in con.execute(
        "SELECT root_id,path,kind,priority,last_scanned_at FROM roots ORDER BY priority")]
    out["sources"] = [dict(r) for r in con.execute(
        "SELECT source_id,content_sha256,byte_size,mime_type FROM sources ORDER BY source_id")]
    out["documents"] = [dict(r) for r in con.execute(
        "SELECT document_id,document_kind,source_status,title,primary_source_id,"
        " published_date,metadata_priority,metadata_json FROM documents ORDER BY document_id")]
    out["document_metadata"] = [
        {"document_id": r["document_id"],
         "metadata_json": r["metadata_json"]}
        for r in out["documents"]]
    out["locations"] = [dict(r) for r in con.execute(
        "SELECT location_id,root_id,relative_path,absolute_path,source_id,document_id,"
        " role,location_status,observed_size,error,metadata_json FROM locations ORDER BY root_id,relative_path")]
    out["entities"] = [dict(r) for r in con.execute(
        "SELECT entity_id,name,entity_kind FROM entities ORDER BY entity_id")]
    out["document_entities"] = [dict(r) for r in con.execute(
        "SELECT document_id,entity_id,confidence,method FROM document_entities"
        " ORDER BY document_id,entity_id")]
    out["scan_runs"] = [dict(r) for r in con.execute(
        "SELECT run_id,status,report_json FROM scan_runs ORDER BY started_at")]
    con.close()
    return out


def resolve_entity_from_sidecar(sidecar_path: Path, fallback: str) -> str:
    """Data-driven identity for the resolve request: sidecar company_name /
    display_name first, else the derived directory name. No literal anywhere."""
    try:
        payload = read_json(sidecar_path)
    except (OSError, ValueError):
        return fallback
    for key in ("company_name", "display_name", "entity"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback
