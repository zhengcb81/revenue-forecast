"""I-07-D isolation builder: per-case company-wiki root + product-isomorphic
catalog + asset copies. Writes ONLY under <attempt>/iso/.

Usage:
  python build_iso.py base            # build iso/base template (config, catalog schema, entities)
  python build_iso.py case <case_id>  # clone template into iso/cases/<case_id>/ with per-state assets/rows

States (per scenario_matrix S-1..S-3):
  state1 : raw+sidecar present AND registered rows present (copied from production
           observation for the sample that has them; never hand-authored green)
  state2 : raw+sidecar present, NO document/location/artifact rows (unregistered)
  state3 : raw+sidecar ABSENT from the isolated root (provider must be simulated)

Isolation-state construction is recorded (what was copied from production vs
absent), never invented: every row in an isolated catalog is either (a) created
by the product's own schema initializer, or (b) copied verbatim from a read-only
production observation with only path relocations into the isolated root.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
import os

ATT = Path(__file__).resolve().parents[1]
BASE = ATT / "iso" / "base"
# Per-case trees live under %TEMP% because the attempt path plus the US sample's
# long file names exceed the Windows 260-char path limit and the PRODUCT (not
# just this harness) opens those paths with plain (non-\\?\) APIs.
CASES = Path(os.environ.get("TEMP", r"C:\Temp")) / "i07d" / "cases"

SRC = {
    "CN-ZIJIN-2025": {
        "entity_dir": "紫金矿业",
        "raw": "2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf",
        "kind": "annual",
        "raw_sha256": "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d",
        "sidecar_sha256": "7f7570fe6565698f1962a9301b5e47dbe76fb3a5e8dfa5663a48fc3793bf20b5",
        "market": "CN",
        "has_production_rows": True,
        "derived": [
            ".source_catalog/derived/01/01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d/normalized.md",
            ".source_catalog/derived/01/01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d/summary.md",
        ],
    },
    "HK-XIAOMI-2025": {
        "entity_dir": "小米集團－Ｗ",
        "raw": "2026-04-28_hkexnews_12127452_2025年度報告.pdf",
        "kind": "annual",
        "raw_sha256": "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c",
        "sidecar_sha256": "8228741d299164380bde36a83df1267b59e9b46721bea7d8efee857aeeb8da71",
        "market": "HK",
        "has_production_rows": False,
        "derived": [],
    },
    "US-MSFT-2026": {
        "entity_dir": "MICROSOFT CORP",
        "raw": "2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm",
        "kind": "annual",
        "raw_sha256": "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff",
        "sidecar_sha256": "1cbfb1a2ed055fa199806a5d01b96f325396506c472ebfabb80474ec712abb6a",
        "market": "US",
        "has_production_rows": False,
        "derived": [],
    },
}

PROD_CATALOG = CW / ".source_catalog" / "catalog.sqlite3"
ISO_CONFIG = """schema_version: "1.0"
catalog_dir: '{root}\\.source_catalog'
reusable_root_kinds: [company_raw]
roots:
  - root_id: company_raw
    kind: company_raw
    path: '{root}\\companies'
    priority: 10
    privacy_class: public
"""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def prod_conn() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{PROD_CATALOG}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    con.row_factory = sqlite3.Row
    return con


def iso_schema(cwroot: Path) -> dict:
    """Create the isolated catalog with the PRODUCT's own initializer."""
    cat_dir = cwroot / ".source_catalog"
    cat_dir.mkdir(parents=True, exist_ok=True)
    from company_wiki.source_catalog.store import CatalogStore

    store = CatalogStore(cat_dir / "catalog.sqlite3")
    store._initialize()  # product schema creation (isomorphic by construction)
    con = sqlite3.connect(cat_dir / "catalog.sqlite3")
    tabs = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    con.close()
    return {"catalog": str(cat_dir / "catalog.sqlite3"), "tables": tabs,
            "table_count": len(tabs),
            "created_by": "company_wiki.source_catalog.store.CatalogStore._initialize (product code)"}


def write_config(cwroot: Path) -> dict:
    (cwroot / "config").mkdir(parents=True, exist_ok=True)
    cfg = cwroot / "config" / "source_catalog.yaml"
    before = None
    prod_cfg = CW / "config" / "source_catalog.yaml"
    cfg.write_text(ISO_CONFIG.format(root=str(cwroot)), encoding="utf-8")
    acq_src = CW / "config" / "source_acquisition.yaml"
    acq_dst = cwroot / "config" / "source_acquisition.yaml"
    if acq_src.is_file():
        shutil.copy2(acq_src, acq_dst)
    # worker config is required (strict resolve) by the ensure write flow
    wcfg_src = CW / "config" / "source_catalog_worker.yaml"
    wcfg_dst = cwroot / "config" / "source_catalog_worker.yaml"
    if wcfg_src.is_file():
        shutil.copy2(wcfg_src, wcfg_dst)
    # security-master snapshots (real production identity data, copied read-only):
    # identify reads <catalog_dir>/security_master/{cn,hk,us}.json
    sm_src = CW / ".source_catalog" / "security_master"
    sm_dst = cwroot / ".source_catalog" / "security_master"
    sm_files = []
    if sm_src.is_dir():
        shutil.copytree(sm_src, sm_dst, dirs_exist_ok=True)
        sm_files = sorted(p.name for p in sm_dst.glob("*.json"))
    return {
        "config": str(cfg),
        "config_sha256": sha256_file(cfg),
        "production_config_sha256": sha256_file(prod_cfg),
        "rebound": "catalog_dir + single company_raw root -> isolated cwroot (absolute paths)",
        "source_acquisition_copied": acq_dst.is_file(),
        "worker_config_copied": wcfg_dst.is_file(),
        "security_master_copied": sm_files,
        "before": before,
    }


def copy_asset(sample: str, cwroot: Path, *, with_raw: bool) -> dict:
    meta = SRC[sample]
    rel_dir = Path("companies") / meta["entity_dir"] / "raw" / "financial_reports" / meta["kind"]
    dst_dir = cwroot / rel_dir
    dst_dir.mkdir(parents=True, exist_ok=True)
    src_raw = CW / "companies" / meta["entity_dir"] / "raw" / "financial_reports" / meta["kind"] / meta["raw"]
    rec: dict = {"sample": sample, "with_raw": with_raw}
    if with_raw:
        for src in (src_raw, Path(str(src_raw) + ".source.json")):
            if not src.is_file():
                raise FileNotFoundError(f"production sample asset missing: {src}")
            dst = dst_dir / src.name
            shutil.copy2(src, dst)
            rec[src.name] = {
                "src": str(src), "dst": str(dst),
                "src_sha256": sha256_file(src), "dst_sha256": sha256_file(dst),
                "bytes": dst.stat().st_size,
            }
        rec["raw_match"] = (rec[src_raw.name]["src_sha256"] == meta["raw_sha256"]
                            == rec[src_raw.name]["dst_sha256"])
        rec["sidecar_match"] = rec[src_raw.name + ".source.json"]["src_sha256"] == meta["sidecar_sha256"]
    else:
        rec["raw_absent"] = str(dst_dir / meta["raw"])
        rec["raw_absent_exists"] = (dst_dir / meta["raw"]).exists()
    return rec


def copy_production_rows(sample: str, cwroot: Path) -> dict:
    """Copy the production observation rows for this sample into the isolated
    catalog, relocating only absolute paths that point into production."""
    meta = SRC[sample]
    doc_id = f"urn:company-wiki:document:sha256:{meta['raw_sha256']}"
    cat = cwroot / ".source_catalog" / "catalog.sqlite3"
    con = prod_conn()
    rows = {}
    for t in ("documents", "locations", "artifacts", "document_entities",
              "source_metadata_assertions", "document_fingerprint_state"):
        rows[t] = [dict(r) for r in con.execute(
            f'SELECT * FROM "{t}" WHERE document_id=?', (doc_id,))]
    rows["sources"] = []
    # sources are keyed by primary_source_id, not document_id
    if rows["documents"]:
        src_id = rows["documents"][0]["primary_source_id"]
        rows["sources"] = [dict(r) for r in con.execute(
            "SELECT * FROM sources WHERE source_id=?", (src_id,))]
        rows["locations"] = [dict(r) for r in con.execute(
            "SELECT * FROM locations WHERE document_id=? OR source_id=?",
            (doc_id, src_id))]
        rows["artifacts"] = [dict(r) for r in con.execute(
            "SELECT * FROM artifacts WHERE document_id=? OR source_id=?",
            (doc_id, src_id))]
    # entities: copy the whole real registry (271 rows) — real identity data
    rows["entities"] = [dict(r) for r in con.execute("SELECT * FROM entities")]
    rows["roots"] = [dict(r) for r in con.execute("SELECT * FROM roots")]
    rows["catalog_meta"] = [dict(r) for r in con.execute("SELECT * FROM catalog_meta")]
    con.close()

    # keep only locations under the isolated company_raw root; drop the
    # production dropbox_stock location (that root is NOT part of the isolated
    # config) — recorded, never silently.
    dropped_locations = [
        {"location_id": r["location_id"], "root_id": r["root_id"],
         "absolute_path": r["absolute_path"],
         "reason": "root not present in isolated config (only company_raw); "
                   "keeping it would reference production bytes outside the isolation"}
        for r in rows["locations"] if r.get("root_id") != "company_raw"
    ]
    rows["locations"] = [r for r in rows["locations"] if r.get("root_id") == "company_raw"]

    # relocate absolute paths into the isolated root
    relocated = {"locations": 0, "artifacts": 0, "roots": 0}
    prod_root = str(CW)
    iso_root = str(cwroot)
    for r in rows["locations"]:
        if r.get("absolute_path", "").startswith(prod_root):
            r["absolute_path"] = iso_root + r["absolute_path"][len(prod_root):]
            relocated["locations"] += 1
    for r in rows["artifacts"]:
        if r.get("path", "").startswith(prod_root):
            r["path"] = iso_root + r["path"][len(prod_root):]
            relocated["artifacts"] += 1
    for r in rows["roots"]:
        if r.get("path", "").startswith(prod_root):
            r["path"] = iso_root + r["path"][len(prod_root):]
            relocated["roots"] += 1
    # roots table: keep ONLY the isolated-config roots
    rows["roots"] = [r for r in rows["roots"] if r.get("root_id") == "company_raw"]

    con = sqlite3.connect(cat)
    cur = con.cursor()
    inserted = {}
    order = ["entities", "catalog_meta", "roots", "sources", "documents",
             "locations", "artifacts", "document_entities",
             "source_metadata_assertions", "document_fingerprint_state"]
    for t in order:
        data = rows.get(t) or []
        inserted[t] = 0
        if not data:
            continue
        cols = list(data[0].keys())
        sql = f'INSERT OR IGNORE INTO "{t}" ({",".join(cols)}) VALUES ({",".join("?" * len(cols))})'
        for row in data:
            cur.execute(sql, tuple(row[c] for c in cols))
            inserted[t] += cur.rowcount
    con.commit()
    con.close()

    # derived artifact files (real production bytes) into the isolated root
    derived = []
    for rel in meta["derived"]:
        src = CW / rel
        dst = cwroot / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        derived.append({"rel": rel, "src_sha256": sha256_file(src),
                        "dst_sha256": sha256_file(dst), "bytes": dst.stat().st_size,
                        "match": sha256_file(src) == sha256_file(dst)})

    return {"document_id": doc_id, "inserted": inserted,
            "relocated": relocated, "dropped_locations": dropped_locations,
            "derived": derived,
            "provenance": "rows copied read-only from production observation; "
                          "only absolute paths relocated into the isolated root",
            "metadata_prompt_injection_review_present": bool(
                rows["documents"] and
                '"prompt_injection_review"' in (rows["documents"][0].get("metadata_json") or ""))}


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "base"
    manifest: dict = {"mode": mode, "built_at_utc": datetime.now(timezone.utc).isoformat()}

    if mode == "base":
        if BASE.exists():
            shutil.rmtree(BASE)
        (BASE / "cwroot").mkdir(parents=True)
        manifest["schema"] = iso_schema(BASE / "cwroot")
        manifest["config"] = write_config(BASE / "cwroot")

    elif mode == "case":
        case_id = sys.argv[2]
        sample = sys.argv[3]
        state = sys.argv[4]  # state1 | state2 | state3
        case_dir = CASES / case_id
        if case_dir.exists():
            shutil.rmtree(case_dir)
        cwroot = case_dir / "cwroot"
        shutil.copytree(BASE / "cwroot", cwroot,
                        ignore=shutil.ignore_patterns("companies", "derived"))
        manifest["case_id"] = case_id
        manifest["sample"] = sample
        manifest["state"] = state
        # rewrite config with this case's absolute root
        manifest["config"] = write_config(cwroot)
        with_raw = state in ("state1", "state2")
        manifest["asset"] = copy_asset(sample, cwroot, with_raw=with_raw)
        if state == "state1":
            manifest["rows"] = copy_production_rows(sample, cwroot)
        elif state == "state2":
            # identity registry only (real rows), NO document/location/artifact rows
            meta = SRC[sample]
            con = prod_conn()
            ents = [dict(r) for r in con.execute("SELECT * FROM entities")]
            cmeta = [dict(r) for r in con.execute("SELECT * FROM catalog_meta")]
            con.close()
            cat = cwroot / ".source_catalog" / "catalog.sqlite3"
            c = sqlite3.connect(cat)
            cur = c.cursor()
            for row in ents:
                cur.execute("INSERT OR IGNORE INTO entities VALUES (?,?,?)",
                            tuple(row[k] for k in ("entity_id", "name", "entity_kind")))
            for row in cmeta:
                cur.execute("INSERT OR IGNORE INTO catalog_meta VALUES (?,?)",
                            (row["key"], row["value"]))
            c.commit()
            c.close()
            manifest["rows"] = {"entities": len(ents), "catalog_meta": len(cmeta),
                                "document_rows": 0, "state": "unregistered by construction",
                                "document_id_absent": f"urn:company-wiki:document:sha256:{meta['raw_sha256']}"}
        elif state == "state3":
            manifest["rows"] = {"document_rows": 0,
                                "raw_absent": True,
                                "note": "isolation simulated missing file (C level); "
                                        "NOT a live genuinely-missing sample"}
        # worker control state (freeze point)
        ctrl = cwroot / ".source_catalog" / "worker_control.json"
        manifest["worker_control"] = {"path": str(ctrl), "exists": ctrl.exists(),
                                      "state": "absent (no worker running; frozen)"}
        manifest["case_tree"] = {"root": str(case_dir),
                                 "location": "%TEMP%\\i07d\\cases (MAX_PATH isolation root)"}
        # per-case iso snapshot
        snap = []
        for p in sorted(case_dir.rglob("*")):
            if p.is_file():
                snap.append({"rel": str(p.relative_to(case_dir)),
                             "bytes": p.stat().st_size,
                             "sha256": sha256_file(p)})
        manifest["iso_snapshot"] = snap
        out = ATT / "evidence" / "cases" / case_id / "initial_state.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({"written": str(out), "case_id": case_id,
                          "tables": manifest.get("schema", {}).get("table_count")},
                         ensure_ascii=False))
        return 0

    out = ATT / "evidence" / f"iso_{mode}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"written": str(out), "tables": manifest["schema"]["table_count"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
