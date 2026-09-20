"""W05A historical section probe - REBOUND copy (never run in place).

Copied from PLAN/reviews/wiki_legacy/section_probe.py.  Two hard-coded
absolute paths in the original are re-bound here:

  * ``source``  -> this attempt's isolated section_query.py
  * the output  -> this attempt's <tag>/legacy-section-probe.json

The temporary SQLite fixture is created inside this attempt's scratch root,
never in reviews/.  The historical reviews/wiki_legacy/section_probe.json is
NOT overwritten.

Usage: <py> -X utf8 -B scripts/w05a_section_probe_bound.py <tag>
"""

import hashlib
import importlib.util
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
TAG = sys.argv[1] if len(sys.argv) > 1 else "before"
SCRATCH = Path(
    os.environ.get("W05A_SCRATCH", r"C:\Users\郑曾波\AppData\Local\Temp\w05a")
) / "a20260919-01" / "legacy_probe" / TAG
SCRATCH.mkdir(parents=True, exist_ok=True)

source = Path(os.environ["W05A_CW_SRC"]) / "company_wiki" / "source_catalog" / "section_query.py"
# Historical probe used spec_from_file_location (the module had no relative
# imports).  The fixed module consumes the shared validator through package
# imports, so the isolated src root goes on sys.path and the module is
# imported normally; the source is still asserted to be the isolated copy.
sys.path.insert(0, str(Path(os.environ["W05A_CW_SRC"])))
from company_wiki.source_catalog import section_query as module  # noqa: E402

assert Path(module.__file__).resolve() == source.resolve(), module.__file__

out = {
    "source": str(source),
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "production_access": False,
    "rebound_from": (
        "reviews/wiki_legacy/section_probe.py "
        "(original source path pointed at the production tree and wrote its "
        "JSON next to itself)"
    ),
    "cases": [],
}
with tempfile.TemporaryDirectory(dir=SCRATCH, prefix="isolated_sections_") as tmp:
    tmp_path = Path(tmp)
    db = tmp_path / "catalog.sqlite3"
    conn = sqlite3.connect(db)
    conn.executescript(
        "CREATE TABLE documents(document_id TEXT,document_kind TEXT,title TEXT);"
        " CREATE TABLE artifacts(document_id TEXT,path TEXT,metadata_json TEXT,"
        "artifact_role TEXT,generator_name TEXT,generator_version TEXT,status TEXT,"
        "source_sha256 TEXT);"
    )
    conn.execute(
        "INSERT INTO documents VALUES(?,?,?)", ("doc", "annual_report", "fixture only")
    )

    def add(version, status, path):
        entry = {
            "role": "mda",
            "title": "fixture",
            "ordinal": "one",
            "char_start": 0,
            "char_end": 5,
            "path": str(path),
            "span_ids": ["nonexistent-span"],
        }
        conn.execute(
            "INSERT INTO artifacts VALUES(?,?,?,?,?,?,?,?)",
            (
                "doc",
                str(path / "index.json"),
                json.dumps({"sections": [entry]}),
                "sections",
                "source_catalog_section_extractor",
                version,
                status,
                "unverified-wrong-source-hash",
            ),
        )
        conn.commit()

    add("old-version", "failed", tmp_path / "does-not-exist-old")
    try:
        result = module.SectionQueryService(db).list_sections(document_id="doc").to_dict()
        first = {"outcome": "returned", "returned": result}
    except Exception as exc:  # noqa: BLE001
        first = {"outcome": "error", "error_type": type(exc).__name__, "message": str(exc)}
    if isinstance(first, dict) and first.get("error_type") == "OperationalError":
        first["outcome"] = "blocked_by_fixture_schema"
        first["note"] = (
            "the historical MINIMAL fixture only carries the columns the old "
            "query read; the qualified reader needs the real catalog schema, "
            "so this probe cannot exercise it.  The positive cases come from "
            "the REAL producer catalog (scripts/w05a_cases.py) instead of "
            "weakening the fixture."
        )
    out["cases"].append(
        {
            "id": "missing_failed_unbound_accepted",
            "result": first,
            "index_exists": Path(
                (first.get("returned") or {}).get("index_path", "missing")
            ).exists(),
            "expectation": (
                "should fail closed or report invalid/stale rather than an "
                "ordinary usable result"
            ),
        }
    )

    add("new-version", "completed", tmp_path / "does-not-exist-new")
    try:
        result2 = module.SectionQueryService(db).list_sections(document_id="doc").to_dict()
        second = {"outcome": "returned", "returned_index": result2["index_path"]}
    except Exception as exc:  # noqa: BLE001
        second = {"outcome": "error", "error_type": type(exc).__name__, "message": str(exc)}
    if isinstance(second, dict) and second.get("error_type") == "OperationalError":
        second["outcome"] = "blocked_by_fixture_schema"
        second["note"] = (
            "see the note on the first case; the real catalog cases are the "
            "positive/negative evidence"
        )
    out["cases"].append(
        {
            "id": "multiple_versions_no_selection_contract",
            "result": second,
            "expectation": (
                "a failed/unusable older row must never be the served row; "
                "selection must be an explicit rule, not SQLite row order"
            ),
        }
    )
    conn.close()

target = ATTEMPT / TAG / "legacy-section-probe.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
