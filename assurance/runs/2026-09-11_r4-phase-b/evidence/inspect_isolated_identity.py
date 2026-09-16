"""Print the isolated document's identity columns (read-only, ASCII)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

ISOLATED = Path.home() / "AppData/Local/Temp/b08-level2-isolated/.source_catalog/catalog.sqlite3"
con = sqlite3.connect(f"file:{ISOLATED.as_posix()}?mode=ro", uri=True)
con.text_factory = lambda raw: raw.decode("utf-8", "replace")
document_id = con.execute(
    "SELECT document_id FROM documents WHERE document_kind='annual_report' LIMIT 1"
).fetchone()[0]
print("entities for the sample document:")
for row in con.execute(
    "SELECT e.name FROM document_entities de JOIN entities e "
    "ON e.entity_id = de.entity_id WHERE de.document_id = ?", (document_id,)
):
    print("  ", row[0])
print("legacy scan row:")
for row in con.execute(
    "SELECT relative_path, location_status, role FROM locations WHERE document_id = ?",
    (document_id,),
):
    print("  name_len=", len(str(row[0])), row[1], row[2])
con.close()
