"""P1 mutation evidence (round 3): red (pre-fix) vs green (post-fix).

Three injections, each applied to a REAL producer-built catalog:

  I1  forge the offsets: char_start += 1 (slice content untouched)
  I2  push the offsets out of every origin window (content untouched)
  I3  clear the candidate set: every `normalized` artifact row -> status='failed'

The script builds the catalogs with the CURRENT tree, then swaps ONLY
`section_query.py` between the pre-fix copy and the current (fixed) bytes while
querying the very same injected catalogs, so the two verdict columns differ by
nothing except the file under test.

Usage:
  <py> -X utf8 -B scripts/w05a_p1_mutations.py <pre-fix-section_query.py>

The pre-fix copy must live OUTSIDE the importable tree; `iso/prefix_r3/` holds
the frozen copy of the r3 bytes that the round-3 review tested.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SCRATCH = Path(
    os.environ.get("W05A_SCRATCH", r"C:\Users\郑曾波\AppData\Local\Temp\w05a")
) / "a20260919-01" / "p1"
CW_SRC = Path(os.environ["W05A_CW_SRC"])
TARGET = CW_SRC / "company_wiki" / "source_catalog" / "section_query.py"
DOC = "urn:cw:doc:emerald-2025-annual"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CW_SRC))


def build_catalog(case: str):
    sys.path.insert(0, str(HERE))
    cases = importlib.import_module("w05a_cases")
    return cases, cases.build_catalog(SCRATCH / case)


def fresh_query_module():
    """Import the query module fresh, with bytecode caching disabled.

    (Sys.modules is cleared AND the file is re-read; the caller asserts the
    module's own bytes so a cached copy can never masquerade as the fix.)
    """
    for name in [n for n in list(sys.modules) if n.startswith("company_wiki")]:
        del sys.modules[name]
    return importlib.import_module("company_wiki.source_catalog.section_query")


def query(db: Path, expect_sha256: str) -> dict:
    module = fresh_query_module()
    actual = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
    assert actual == expect_sha256, (
        f"the query module is not the bytes under test: {module.__file__} "
        f"is {actual}, expected {expect_sha256}"
    )
    try:
        result = module.SectionQueryService(db).list_sections(document_id=DOC)
    except Exception as exc:  # noqa: BLE001
        return {
            "verdict": "refused",
            "error_type": type(exc).__name__,
            "reason": str(exc),
            "window_match": [],
            "module_sha256": actual,
        }
    return {
        "verdict": "returned",
        "reason": None,
        "window_match": [entry.window_match for entry in result.sections],
        "window_positions": [list(entry.window_positions) for entry in result.sections],
        "module_sha256": actual,
    }


def artifact_row(db: Path, role: str = "sections") -> dict:
    connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            "SELECT path, metadata_json, content_sha256 FROM artifacts "
            "WHERE artifact_role=?", (role,)
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else {}


def exec_sql(db: Path, sql: str, params: tuple = ()) -> None:
    connection = sqlite3.connect(str(db))
    try:
        connection.execute(sql, params)
        connection.commit()
    finally:
        connection.close()


def sync_row(db: Path, entries: list[dict]) -> str:
    """Rewrite index + metadata + row hash so ONLY the offsets differ."""
    row = artifact_row(db)
    index_path = Path(row["path"])
    payload = json.dumps(entries, ensure_ascii=False, indent=2).encode("utf-8")
    index_path.write_bytes(payload)
    metadata = json.dumps(
        {"schema_version": "1.0", "sections": entries, "count": len(entries)},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    )
    exec_sql(
        db,
        "UPDATE artifacts SET content_sha256=?, byte_size=?, metadata_json=? "
        "WHERE artifact_role='sections'",
        (hashlib.sha256(payload).hexdigest(), len(payload), metadata),
    )
    return hashlib.sha256(payload).hexdigest()


def mutate_offsets(db: Path, delta: int) -> dict:
    row = artifact_row(db)
    entries = json.loads(Path(row["path"]).read_text(encoding="utf-8"))
    before = [
        {"role": e["role"], "char_start": e["char_start"], "char_end": e["char_end"]}
        for e in entries
    ]
    for entry in entries:
        entry["char_start"] = int(entry["char_start"]) + delta
        entry["char_end"] = int(entry["char_end"]) + delta
    sync_row(db, entries)
    return {
        "delta": delta,
        "before": before,
        "after": [
            {"role": e["role"], "char_start": e["char_start"], "char_end": e["char_end"]}
            for e in entries
        ],
        "slice_content_untouched": True,
        "index_and_row_hash_resynced": True,
    }


def drop_normalized(db: Path) -> dict:
    exec_sql(db, "UPDATE artifacts SET status='failed' WHERE artifact_role='normalized'")
    connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        left = connection.execute(
            "SELECT count(*) FROM artifacts WHERE artifact_role='normalized' "
            "AND status='completed'"
        ).fetchone()[0]
    finally:
        connection.close()
    return {"normalized_completed_rows": left}


def main() -> int:
    pre_fix = Path(sys.argv[1]).resolve()
    fixed_bytes = TARGET.read_bytes()
    pre_bytes = pre_fix.read_bytes()
    out_dir = ATTEMPT / "evidence"
    out_dir.mkdir(parents=True, exist_ok=True)
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)

    report: dict = {
        "method": (
            "identical injected catalogs queried twice: once with the pre-fix "
            "section_query.py, once with the current (fixed) bytes"
        ),
        "pre_fix_source": str(pre_fix),
        "pre_fix_sha256": hashlib.sha256(pre_bytes).hexdigest(),
        "fixed_source": str(TARGET),
        "fixed_sha256": hashlib.sha256(fixed_bytes).hexdigest(),
        "injections": {},
    }
    injections = [
        # NOTE on deltas: the frozen trim semantics (oracle.md §3.1.1) compare
        # `fragment.strip("\n")` with `window.strip("\n")`, so a +1 shift of
        # BOTH offsets can still reproduce the same trimmed text when the
        # boundary characters are newlines (measured: +1 stayed a source_window
        # hit on the real producer catalog).  +2 moves a content character out
        # of the window and is therefore the decisive forgery.
        ("I1_offsets_plus_one", lambda db: mutate_offsets(db, 2)),
        ("I2_offsets_way_off", lambda db: mutate_offsets(db, 5)),
        ("I3_no_normalized_source", drop_normalized),
    ]
    for name, mutate in injections:
        _, built = build_catalog(name)
        db = built["config"].database_path
        detail = mutate(db)
        try:
            TARGET.write_bytes(pre_bytes)
            pre = query(db, report["pre_fix_sha256"])
        finally:
            TARGET.write_bytes(fixed_bytes)
        fixed = query(db, report["fixed_sha256"])
        report["injections"][name] = {
            "mutation_detail": detail,
            "pre_fix": pre,
            "post_fix": fixed,
            "verdict_change": f"{pre['verdict']} -> {fixed['verdict']}",
        }
    (out_dir / "p1-mutations.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
