"""I-07-A r2 (post-review corrections): re-observe the two facts the reviewer challenged.

F-I07A-01: the roots table must be shown as SQL output, not as a program structure.
F-I07A-02: the multi-root census must be reported untruncated (the first pass used LIMIT 20).

READ-ONLY: mode=ro URI + PRAGMA query_only=ON, SELECT only, no writes.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CATALOG = Path(r"C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3")

ROOTS_SQL = "SELECT root_id, path, kind, priority, last_scanned_at FROM roots ORDER BY priority"
CENSUS_COUNT_SQL = (
    "SELECT COUNT(*) FROM (SELECT s.content_sha256 FROM sources s "
    "JOIN locations l ON l.source_id = s.source_id "
    "GROUP BY s.content_sha256 HAVING COUNT(DISTINCT l.root_id) >= 2)"
)
CENSUS_TOP_SQL = (
    "SELECT s.content_sha256, COUNT(DISTINCT l.root_id) AS root_count, "
    "GROUP_CONCAT(DISTINCT l.root_id) AS roots, COUNT(*) AS loc_count "
    "FROM sources s JOIN locations l ON l.source_id = s.source_id "
    "GROUP BY s.content_sha256 HAVING COUNT(DISTINCT l.root_id) >= 2 "
    "ORDER BY root_count DESC, loc_count DESC LIMIT 5"
)
DOCS_MULTI_ROOT_COUNT_SQL = (
    "SELECT COUNT(*) FROM (SELECT document_id FROM locations WHERE document_id IS NOT NULL "
    "GROUP BY document_id HAVING COUNT(DISTINCT root_id) >= 2)"
)
ROOT_LOCATION_COUNTS_SQL = (
    "SELECT r.root_id, r.path, r.kind, COUNT(l.location_id) AS locations "
    "FROM roots r LEFT JOIN locations l ON l.root_id = r.root_id "
    "GROUP BY r.root_id ORDER BY r.priority"
)
CN_LOCATIONS_SQL = (
    "SELECT root_id, role, location_status, observed_size, relative_path "
    "FROM locations WHERE document_id = ? ORDER BY root_id, role"
)


def catalog_identity() -> dict:
    item = CATALOG.stat()
    wal = CATALOG.parent / (CATALOG.name + "-wal")
    return {"bytes": item.st_size,
            "mtime_iso": datetime.fromtimestamp(item.st_mtime).isoformat(),
            "wal_bytes": wal.stat().st_size if wal.exists() else None}


def main() -> int:
    out_path = Path(sys.argv[1])
    cn_sha = sys.argv[2]
    cn_doc = "urn:company-wiki:document:sha256:" + cn_sha

    before = catalog_identity()
    con = sqlite3.connect(CATALOG.resolve().as_uri() + "?mode=ro", uri=True, timeout=60)
    con.execute("PRAGMA query_only=ON")

    def q(sql: str, params: tuple = ()) -> dict:
        t0 = time.perf_counter()
        cur = con.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        return {"sql": sql, "params": list(params), "row_count": len(rows),
                "rows": rows, "elapsed_seconds": round(time.perf_counter() - t0, 6)}

    started = datetime.now(timezone.utc).isoformat()
    try:
        observations = {
            "roots_table": q(ROOTS_SQL),
            "root_location_counts": q(ROOT_LOCATION_COUNTS_SQL),
            "cn_sample_locations": q(CN_LOCATIONS_SQL, (cn_doc,)),
            "multi_root_same_bytes_total": q(CENSUS_COUNT_SQL),
            "multi_root_same_bytes_top5": q(CENSUS_TOP_SQL),
            "multi_root_same_document_total": q(DOCS_MULTI_ROOT_COUNT_SQL),
        }
    finally:
        con.close()
    after = catalog_identity()

    payload = {
        "captured_at_utc": started,
        "read_only": {"uri": CATALOG.resolve().as_uri() + "?mode=ro",
                      "pragma": "query_only=ON", "writes_issued": 0},
        "catalog_before": before,
        "catalog_after": after,
        "catalog_identity_unchanged": before == after,
        "corrections": {
            "F-I07A-01": "the roots table shown as SQL output; future_lake present with zero locations",
            "F-I07A-02": "the census reported untruncated (total) plus an explicitly labelled top-5",
        },
        "observations": observations,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({
        "catalog_identity_unchanged": payload["catalog_identity_unchanged"],
        "roots_rows": observations["roots_table"]["row_count"],
        "root_ids": [r["root_id"] for r in observations["roots_table"]["rows"]],
        "root_location_counts": observations["root_location_counts"]["rows"],
        "multi_root_same_bytes_total": observations["multi_root_same_bytes_total"]["rows"],
        "multi_root_same_document_total": observations["multi_root_same_document_total"]["rows"],
        "elapsed": {k: v["elapsed_seconds"] for k, v in observations.items()},
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
