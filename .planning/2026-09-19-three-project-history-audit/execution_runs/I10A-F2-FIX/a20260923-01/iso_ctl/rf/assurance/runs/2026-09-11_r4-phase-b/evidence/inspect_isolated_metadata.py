"""Inspect one isolated-catalog document's metadata shape (read-only, ASCII output)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ISOLATED = Path.home() / "AppData/Local/Temp/b08-level2-isolated/.source_catalog/catalog.sqlite3"
con = sqlite3.connect(f"file:{ISOLATED.as_posix()}?mode=ro", uri=True)
con.text_factory = lambda raw: raw.decode("utf-8", "replace")


def shape(value, depth: int = 0):
    if isinstance(value, dict):
        if depth >= 2:
            return "dict"
        return {key: shape(item, depth + 1) for key, item in list(value.items())[:14]}
    if isinstance(value, list):
        return ["list"] if not value else [shape(value[0], depth + 1)]
    return type(value).__name__


row = con.execute(
    "SELECT document_id, metadata_json FROM documents WHERE document_kind='annual_report' LIMIT 1"
).fetchone()
metadata = json.loads(row[1] or "{}")
print("metadata shape:")
print(json.dumps(shape(metadata), ensure_ascii=False, indent=2))
for key in ("acquisition", "dayu_meta"):
    block = metadata.get(key)
    if isinstance(block, dict):
        print(f"{key} keys: {sorted(block.keys())}")
con.close()
