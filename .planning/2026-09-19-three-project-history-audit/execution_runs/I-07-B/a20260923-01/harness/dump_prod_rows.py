"""I-07-B: read-only dump of the production catalog rows for the three frozen
samples + identity rows (used to construct the ISOLATED catalog state).

Reads production with mode=ro + PRAGMA query_only=ON; issues SELECT only.
"""
from __future__ import annotations

import json
import sqlite3
import sys

PROD = r"C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3"

SAMPLES = {
    "CN-ZIJIN-2025": {
        "sha256": "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d",
        "query": "601899",
    },
    "HK-XIAOMI-2025": {
        "sha256": "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c",
        "query": "1810",
    },
    "US-MSFT-2026": {
        "sha256": "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff",
        "query": "MSFT",
    },
}


def rows(cur, sql, params=()):
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def main() -> int:
    con = sqlite3.connect(f"file:{PROD}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    cur = con.cursor()
    out: dict = {"production": PROD, "access": "SELECT-only, mode=ro, query_only=ON",
                 "tables": [r[0] for r in cur.execute(
                     "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")],
                 "samples": {}, "identity_probe": {}}

    # entities / document_entities columns for identity discovery
    for t in ("entities", "documents", "roots", "sources", "locations", "artifacts",
              "source_metadata_assertions", "evidence_spans", "document_entities",
              "activation_journal", "producer_events", "catalog_meta", "scan_runs"):
        try:
            out.setdefault("columns", {})[t] = [r[1] for r in cur.execute(
                f'PRAGMA table_info("{t}")')]
        except Exception as exc:  # noqa: BLE001
            out.setdefault("columns", {})[t] = f"ERR {exc}"

    for name, meta in SAMPLES.items():
        sha = meta["sha256"]
        doc_id = f"urn:company-wiki:document:sha256:{sha}"
        s = {"document_id": doc_id}
        for t in ("documents", "sources", "locations", "artifacts",
                  "source_metadata_assertions", "evidence_spans",
                  "document_fingerprint_state"):
            cols = out["columns"].get(t) or []
            try:
                if "document_id" in cols:
                    s[t] = rows(cur, f'SELECT * FROM "{t}" WHERE document_id=?', (doc_id,))
                elif t == "sources" and "source_id" in cols:
                    s[t] = []
            except Exception as exc:  # noqa: BLE001
                s[t] = f"ERR {exc}"
        # join sources via documents.source_id and locations via content hash
        try:
            d = rows(cur, "SELECT * FROM documents WHERE document_id=?", (doc_id,))
            if d:
                src_id = d[0].get("source_id")
                s["source_rows"] = rows(cur, "SELECT * FROM sources WHERE source_id=?",
                                        (src_id,)) if src_id else []
                ent = rows(cur, "SELECT * FROM document_entities WHERE document_id=?",
                           (doc_id,))
                s["document_entities"] = ent
        except Exception as exc:  # noqa: BLE001
            s["join_err"] = str(exc)
        out["samples"][name] = s

    # identity probe: find rows matching the three queries anywhere in entities
    for q in ("601899", "1810", "MSFT"):
        hits = {}
        try:
            hits["entities_like"] = rows(
                cur,
                "SELECT * FROM entities WHERE " +
                " OR ".join(f'CAST("{c}" AS TEXT) LIKE ?' for c in out["columns"]["entities"]),
                tuple(f"%{q}%" for _ in out["columns"]["entities"]))[:10]
        except Exception as exc:  # noqa: BLE001
            hits["entities_like"] = f"ERR {exc}"
        out["identity_probe"][q] = hits

    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
