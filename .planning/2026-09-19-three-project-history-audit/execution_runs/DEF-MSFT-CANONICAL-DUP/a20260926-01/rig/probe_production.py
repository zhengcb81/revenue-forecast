"""Read-only probe of the production company-wiki artifacts for this card.

Writes rig/probe_production.json next to this script.  No writes anywhere
else; opens production files read-only.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


out: dict = {}

ann = CW / "companies" / "MICROSOFT CORP" / "raw" / "financial_reports" / "annual"
out["production_annual"] = [
    {"name": p.name, "size": p.stat().st_size, "sha256": sha(p)}
    for p in sorted(ann.iterdir())
]

stg = CW / ".source_catalog" / "staging"
out["production_staging"] = [
    {"path": str(p.relative_to(stg)), "size": p.stat().st_size, "sha256": sha(p)}
    for p in sorted(stg.rglob("*"))
    if p.is_file()
]

journal = CW / ".source_catalog" / "acquisition_attempts.jsonl"
lines = journal.read_text(encoding="utf-8").splitlines()
out["journal_line_count"] = len(lines)
out["journal_last_3"] = [json.loads(line) for line in lines[-3:]]
out["journal_msft_rows"] = [
    json.loads(line)
    for line in lines
    if "0001193125-26-323660" in line
]

con = sqlite3.connect(
    f"file:{CW / '.source_catalog' / 'catalog.sqlite3'}?mode=ro", uri=True
)
con.row_factory = sqlite3.Row
out["db_rows_for_msft_shas"] = [
    dict(row)
    for row in con.execute(
        "SELECT s.content_sha256, s.byte_size, d.source_status, l.absolute_path, "
        "l.location_status FROM sources s "
        "LEFT JOIN documents d ON d.primary_source_id=s.source_id "
        "LEFT JOIN locations l ON l.source_id=s.source_id "
        "WHERE s.content_sha256 LIKE 'e3de0053%' OR s.content_sha256 LIKE '095935f9%'"
    )
]
out["db_counts"] = {
    "sources": con.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
    "documents": con.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
    "locations": con.execute("SELECT COUNT(*) FROM locations").fetchone()[0],
}
out["db_msft_identity_rows"] = [
    dict(row)
    for row in con.execute(
        "SELECT d.document_id, d.title, d.source_status, l.absolute_path, "
        "l.location_status FROM documents d "
        "LEFT JOIN locations l ON l.document_id=d.document_id "
        "WHERE d.metadata_json LIKE '%0001193125-26-323660%'"
    )
]
out["db_roots"] = [dict(r) for r in con.execute("SELECT * FROM roots")]
out["db_scan_runs"] = [
    dict(r)
    for r in con.execute(
        "SELECT run_id, started_at, completed_at, status, report_json "
        "FROM scan_runs ORDER BY started_at DESC LIMIT 5"
    )
]
con.close()

src = CW / "src" / "company_wiki"
total = 0
count = 0
for root, _dirs, names in os.walk(src):
    for name in names:
        try:
            total += os.path.getsize(os.path.join(root, name))
            count += 1
        except OSError:
            pass
out["company_wiki_src"] = {"files": count, "bytes": total}

out["python"] = sys.version
Path(HERE / "probe_production.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
)
print("wrote probe_production.json")
