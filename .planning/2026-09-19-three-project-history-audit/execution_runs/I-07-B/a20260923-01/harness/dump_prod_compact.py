"""I-07-B: compact read-only summary of production rows for the three samples."""
from __future__ import annotations

import json
import sqlite3
import sys

PROD = r"C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3"
SHAS = {
    "CN-ZIJIN-2025": "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d",
    "HK-XIAOMI-2025": "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c",
    "US-MSFT-2026": "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff",
}


def rows(cur, sql, params=()):
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def main() -> int:
    con = sqlite3.connect(f"file:{PROD}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    cur = con.cursor()
    tabs = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    out: dict = {"tables": tabs, "ddl": {}, "columns": {}, "samples": {},
                 "identity": {}, "small_rowcounts": {}}
    for t in tabs:
        out["ddl"][t] = cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,)
        ).fetchone()[0]
        out["columns"][t] = [r[1] for r in cur.execute(f'PRAGMA table_info("{t}")')]
    # cheap counts only for tables expected small
    for t in ("catalog_meta", "roots", "entities", "activation_journal",
              "producer_events", "remediation_proposals", "document_retire_audit",
              "document_restore_audit", "document_fingerprint_state"):
        if t in tabs:
            out["small_rowcounts"][t] = cur.execute(
                f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    for name, sha in SHAS.items():
        doc_id = f"urn:company-wiki:document:sha256:{sha}"
        s: dict = {"document_id": doc_id}
        s["documents"] = rows(cur, "SELECT * FROM documents WHERE document_id=?", (doc_id,))
        s["locations"] = rows(cur, "SELECT * FROM locations WHERE document_id=?", (doc_id,))
        s["artifacts"] = rows(cur, "SELECT * FROM artifacts WHERE document_id=?", (doc_id,))
        s["assertions_count"] = cur.execute(
            'SELECT COUNT(*) FROM source_metadata_assertions WHERE document_id=?',
            (doc_id,)).fetchone()[0] if "source_metadata_assertions" in tabs else None
        s["evidence_spans_count"] = cur.execute(
            'SELECT COUNT(*) FROM evidence_spans WHERE document_id=?',
            (doc_id,)).fetchone()[0] if "evidence_spans" in tabs else None
        if s["documents"]:
            sid = s["documents"][0].get("source_id")
            s["sources"] = rows(cur, "SELECT * FROM sources WHERE source_id=?", (sid,)) if sid else []
            s["document_entities"] = rows(cur,
                "SELECT * FROM document_entities WHERE document_id=?", (doc_id,))
            if s["sources"] and "root_id" in (out["columns"].get("sources") or []):
                rid = s["sources"][0].get("root_id")
                s["root_row"] = rows(cur, "SELECT * FROM roots WHERE root_id=?", (rid,)) if rid else []
        out["samples"][name] = s
    # identity: rows in entities table containing the queries
    ent_cols = out["columns"].get("entities") or []
    for q in ("601899", "1810", "MSFT", "紫金", "小米", "MICROSOFT"):
        if not ent_cols:
            break
        where = " OR ".join(f'UPPER(CAST("{c}" AS TEXT)) LIKE ?' for c in ent_cols)
        params = tuple(f"%{q.upper()}%" for _ in ent_cols)
        try:
            out["identity"][q] = rows(cur, f"SELECT * FROM entities WHERE {where}", params)[:5]
        except Exception as exc:  # noqa: BLE001
            out["identity"][q] = f"ERR {exc}"
    out["catalog_meta_rows"] = rows(cur, "SELECT * FROM catalog_meta")
    out["roots_rows"] = rows(cur, "SELECT * FROM roots")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
