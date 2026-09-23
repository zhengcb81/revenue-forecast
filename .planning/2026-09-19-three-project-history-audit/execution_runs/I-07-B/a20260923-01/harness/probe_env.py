"""I-07-B harness probe: env introspection + production catalog schema (read-only)."""
from __future__ import annotations

import json
import sqlite3
import sys

out: dict = {"python": sys.version, "prefix": sys.prefix, "path": sys.path}

try:
    import company_wiki  # noqa: F401

    out["company_wiki"] = company_wiki.__file__
except Exception as exc:  # noqa: BLE001
    out["company_wiki"] = f"ERR {type(exc).__name__}: {exc}"

try:
    import company_wiki.source_catalog.cli as cli  # noqa: F401

    out["cli"] = "ok"
except Exception as exc:  # noqa: BLE001
    out["cli"] = f"ERR {type(exc).__name__}: {exc}"

if "--schema" in sys.argv:
    prod = r"C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3"
    con = sqlite3.connect(f"file:{prod}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    tabs = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    schema: dict = {"path": prod, "tables": tabs, "ddl": {}, "rowcount": {}}
    for t in tabs:
        schema["ddl"][t] = con.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,)
        ).fetchone()[0]
        try:
            schema["rowcount"][t] = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        except Exception as exc:  # noqa: BLE001
            schema["rowcount"][t] = f"ERR {exc}"
    out["production_catalog"] = schema
    con.close()

print(json.dumps(out, ensure_ascii=False, indent=1))
