"""Audit-only catalog read. Opens SQLite in mode=ro, never invokes product writers."""
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path.home() / "Projects" / "company-wiki"
db = root / ".source_catalog" / "catalog.sqlite3"
with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as conn:
    conn.execute("PRAGMA query_only=ON")
    conn.row_factory = sqlite3.Row
    def rows(sql, args=()):
        return [dict(r) for r in conn.execute(sql, args)]
    result = {"audit_time_utc": datetime.now(timezone.utc).isoformat(), "mode": "ro+query_only", "db": str(db)}
    result["roots"] = rows("SELECT * FROM roots")
    result["root_counts"] = rows("SELECT root_id,location_status,role,count(*) AS n FROM locations GROUP BY root_id,location_status,role")
    result["companies"] = {}
    for company, patterns in {"Zijin": ["%紫金%", "%601899%", "%Zijin%"], "Xiaomi": ["%小米%", "%Xiaomi%"], "Microsoft": ["%微软%", "%Microsoft%", "%MSFT%"]}.items():
        preds = " OR ".join("(e.name LIKE ? OR d.title LIKE ?)" for _ in patterns)
        args = tuple(p for p in patterns for _ in range(2))
        docs = rows(f"SELECT DISTINCT d.* FROM documents d LEFT JOIN document_entities de ON de.document_id=d.document_id LEFT JOIN entities e ON e.entity_id=de.entity_id WHERE {preds}", args)
        entries = []
        for doc in docs:
            doc_id = doc["document_id"]
            entries.append({"document": doc, "entities": rows("SELECT e.* FROM document_entities de JOIN entities e ON e.entity_id=de.entity_id WHERE de.document_id=?", (doc_id,)), "locations": rows("SELECT * FROM locations WHERE document_id=?", (doc_id,)), "artifacts": rows("SELECT * FROM artifacts WHERE document_id=?", (doc_id,)), "assertions": rows("SELECT * FROM source_metadata_assertions WHERE document_id=?", (doc_id,))})
        result["companies"][company] = entries
    target = Path(__file__).with_name(sys.argv[1] if len(sys.argv) > 1 else "catalog_baseline.json")
    if target.exists():
        raise SystemExit("baseline exists; immutable audit snapshot retained")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"saved": str(target), "roots": result["roots"], "root_counts": result["root_counts"], "companies": {k: len(v) for k,v in result["companies"].items()}},ensure_ascii=False,indent=2))
