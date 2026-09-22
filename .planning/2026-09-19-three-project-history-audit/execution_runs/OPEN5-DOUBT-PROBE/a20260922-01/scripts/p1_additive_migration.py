"""P1 — additive migration probe against the I-06-A UNRATIFIED candidate.

Target: execution_runs/I-06-A/a20260919-01/iso/candidate/processing_demand_store.py
        real migration entry = DurableDemandStore._initialize() + DEMAND_SCHEMA
        (OPEN-1 option-A shape names the CW production mechanism
         _apply_additive_migrations at CW store.py:1072; the candidate re-expresses
         it as CREATE TABLE IF NOT EXISTS + BEGIN IMMEDIATE).

Runs ONLY against throwaway sqlite files under %TEMP%. Reads the candidate
byte-for-byte (copy into %TEMP% first, then import the copy).
Writes raw evidence to evidence/01_additive_migration.txt.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import sys
import traceback
from pathlib import Path

CAND_SRC = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-06-A\a20260919-01\iso\candidate\processing_demand_store.py"
)
OUT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\OPEN5-DOUBT-PROBE\a20260922-01\evidence\01_additive_migration.txt"
)
TMP = Path(os.environ["TEMP"]) / "open5-doubt-probe" / "p1"

LOG: list[str] = []


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


def step(name: str, fn):
    """Run one step, capture rc + exception text, never abort the probe."""
    try:
        value = fn()
        log(f"[{name}] rc=0")
        return 0, value
    except Exception as exc:  # noqa: BLE001 — raw capture is the point
        detail = f"{type(exc).__name__}: {exc}"
        log(f"[{name}] rc=1 EXC={detail}")
        log(traceback.format_exc())
        return 1, detail


def schema_dump(db: Path) -> list[tuple]:
    con = sqlite3.connect(str(db))
    try:
        return con.execute(
            "SELECT type,name,sql FROM sqlite_master ORDER BY type,name"
        ).fetchall()
    finally:
        con.close()


def dump_schema(tag: str, db: Path) -> list[tuple]:
    rows = schema_dump(db)
    log(f"--- schema dump [{tag}] ({db.name}) ---")
    for r in rows:
        log(f"    {r[0]} {r[1]} :: {r[2]}")
    return rows


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    cand_copy = TMP / "processing_demand_store.py"
    shutil.copy2(CAND_SRC, cand_copy)
    sha = hashlib.sha256(CAND_SRC.read_bytes()).hexdigest()
    log(f"candidate src : {CAND_SRC}")
    log(f"candidate sha256: {sha}")
    log(f"temp copy     : {cand_copy}")
    log()

    spec = importlib.util.spec_from_file_location("pds_p1", cand_copy)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    Store = mod.DurableDemandStore

    results: dict[str, dict] = {}

    # ---------- P1-a: fresh DB, first migrate ----------
    db_a = TMP / "a_fresh.sqlite3"
    before_a = dump_schema("P1-a before", db_a) if db_a.exists() else []
    rc_a, _ = step("P1-a first _initialize on fresh DB", lambda: Store(db_a)._initialize())
    after_a = dump_schema("P1-a after", db_a)
    has_table = any(r[1] == "processing_demands" for r in after_a)
    has_idx = any(r[1] == "idx_processing_demands_key" for r in after_a)
    results["P1-a"] = {
        "rc": rc_a,
        "schema_before": [list(r) for r in before_a],
        "schema_after": [list(r) for r in after_a],
        "table_created": has_table,
        "index_created": has_idx,
        "verdict_expect": "rc=0 + table + index",
        "ok": rc_a == 0 and has_table and has_idx,
    }
    log()

    # ---------- P1-b: migrate the SAME fresh DB twice more (idempotency) ----------
    def _reg_one():
        return Store(db_a).register(
            kind="review",
            source_id="src-p1",
            source_sha256="a" * 64,
            review_policy="policy-p1",
            role_set="normalized,sections",
            gaps=[{"gap": "review_required"}],
            request={"as_of_date": "2026-09-22"},
        )

    rc_reg, reg_val = step("P1-b seed one row via register()", _reg_one)
    con = sqlite3.connect(str(db_a))
    rows_before = con.execute("SELECT COUNT(*) FROM processing_demands").fetchone()[0]
    con.close()
    rc_b1, _ = step("P1-b re-run _initialize (2nd)", lambda: Store(db_a)._initialize())
    rc_b2, _ = step("P1-b re-run _initialize (3rd)", lambda: Store(db_a)._initialize())
    after_b = dump_schema("P1-b after 3 migrations", db_a)
    con = sqlite3.connect(str(db_a))
    rows_after = con.execute("SELECT COUNT(*) FROM processing_demands").fetchone()[0]
    con.close()
    results["P1-b"] = {
        "register_rc": rc_reg,
        "rows_before_re_migrate": rows_before,
        "second_migrate_rc": rc_b1,
        "third_migrate_rc": rc_b2,
        "rows_after_re_migrate": rows_after,
        "schema_stable": after_b == after_a,
        "verdict_expect": "re-migrate rc=0, no duplicate rows, schema unchanged",
        "ok": rc_reg == 0 and rc_b1 == 0 and rc_b2 == 0
        and rows_before == rows_after == 1 and after_b == after_a,
    }
    log()

    # ---------- P1-b2 / P1-c: DB at schema version N-1 (older columns), with rows ----------
    # N-1 = the same table MINUS the columns the current schema adds on top of the
    # original FC-era shape (attempts / lease_owner / lease_until / request_sha256 /
    # request_json / candidate_marker). This is the pre-claim/pre-binding version.
    db_n1 = TMP / "c_nminus1.sqlite3"
    N1_DDL = (
        "CREATE TABLE processing_demands ("
        "demand_id TEXT PRIMARY KEY,"
        "demand_key TEXT NOT NULL,"
        "kind TEXT NOT NULL,"
        "status TEXT NOT NULL,"
        "source_id TEXT NOT NULL,"
        "source_sha256 TEXT NOT NULL,"
        "review_policy TEXT NOT NULL,"
        "role_set TEXT NOT NULL,"
        "gaps_json TEXT NOT NULL,"
        "created_at REAL NOT NULL,"
        "updated_at REAL NOT NULL)"
    )

    def _make_n1():
        con = sqlite3.connect(str(db_n1))
        con.execute(N1_DDL)
        con.execute(
            "INSERT INTO processing_demands VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ("demand-n1-1", "k1", "review", "pending", "s1", "b" * 64,
             "p1", "normalized,sections", "[]", 1.0, 1.0),
        )
        con.execute(
            "INSERT INTO processing_demands VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ("demand-n1-2", "k2", "review", "pending", "s2", "c" * 64,
             "p1", "normalized,sections", "[]", 2.0, 2.0),
        )
        con.commit()
        con.close()

    rc_make, _ = step("P1-b2 build N-1 DB with 2 existing rows", _make_n1)
    before_n1 = dump_schema("P1-b2 N-1 before migrate", db_n1)
    rc_m1, _ = step("P1-b2 migrate N-1 (1st _initialize)", lambda: Store(db_n1)._initialize())
    rc_m2, _ = step("P1-b2 migrate N-1 (2nd _initialize, idempotency)",
                    lambda: Store(db_n1)._initialize())
    after_n1 = dump_schema("P1-b2 N-1 after migrate", db_n1)

    cols_before = {r[2] for r in before_n1 if r[1] == "processing_demands"}
    cols_after = {r[2] for r in after_n1 if r[1] == "processing_demands"}
    con = sqlite3.connect(str(db_n1))
    con.row_factory = sqlite3.Row
    kept = [dict(r) for r in con.execute(
        "SELECT * FROM processing_demands ORDER BY demand_id").fetchall()]
    con.close()
    log(f"--- rows after migrate ({len(kept)}) ---")
    for r in kept:
        log(f"    {json.dumps(r, ensure_ascii=False, sort_keys=True)}")

    schema_changed_additively = cols_before != cols_after
    # new columns present on the physical table?
    flat_cols = set()
    for r in after_n1:
        if r[1] == "processing_demands" and r[2]:
            flat_cols = set()
    con = sqlite3.connect(str(db_n1))
    physical = {row[1] for row in con.execute("PRAGMA table_info(processing_demands)")}
    con.close()
    new_cols = {"attempts", "lease_owner", "lease_until",
                "request_sha256", "request_json", "candidate_marker"}
    added = new_cols & physical
    missing = new_cols - physical

    # Does the CURRENT code path work against the migrated N-1 DB?
    rc_reg_n1, reg_n1_val = step(
        "P1-c register() against migrated N-1 DB",
        lambda: Store(db_n1).register(
            kind="review",
            source_id="src-n1",
            source_sha256="d" * 64,
            review_policy="p1",
            role_set="normalized,sections",
            gaps=[],
            request={"as_of_date": "2026-09-22"},
        ),
    )
    rc_claim_n1, claim_n1_val = step(
        "P1-c claim() against migrated N-1 DB (uses new columns)",
        lambda: Store(db_n1).claim(owner="w1", lease_seconds=300.0),
    )
    con = sqlite3.connect(str(db_n1))
    con.row_factory = sqlite3.Row
    kept2 = [dict(r) for r in con.execute(
        "SELECT * FROM processing_demands ORDER BY demand_id").fetchall()]
    con.close()
    log(f"--- rows after register+claim ({len(kept2)}) ---")
    for r in kept2:
        log(f"    {json.dumps(r, ensure_ascii=False, sort_keys=True)}")

    old_rows_preserved = {r["demand_id"] for r in kept2} >= {"demand-n1-1", "demand-n1-2"}
    defaults_ok = all(
        (r.get("attempts") in (0, None))
        and (r.get("lease_owner") is None)
        and (r.get("lease_until") is None)
        for r in kept2 if r["demand_id"].startswith("demand-n1-")
    )
    results["P1-b2"] = {
        "build_n1_rc": rc_make,
        "migrate_1st_rc": rc_m1,
        "migrate_2nd_rc": rc_m2,
        "schema_before": [list(r) for r in before_n1],
        "schema_after": [list(r) for r in after_n1],
        "physical_columns_after": sorted(physical),
        "new_columns_added": sorted(added),
        "new_columns_missing": sorted(missing),
        "verdict_expect": "migration adds the new columns additively (or fails loudly)",
        "ok": rc_m1 == 0 and rc_m2 == 0 and not missing,
        "schema_changed_additively": schema_changed_additively,
    }
    results["P1-c"] = {
        "rows_after_migrate": kept,
        "register_rc": rc_reg_n1,
        "register_result": reg_n1_val if isinstance(reg_n1_val, str) else "OK",
        "claim_rc": rc_claim_n1,
        "claim_result": claim_n1_val if isinstance(claim_n1_val, str) else "OK",
        "rows_after_register_claim": kept2,
        "old_rows_preserved": old_rows_preserved,
        "old_rows_defaults_ok": defaults_ok,
        "verdict_expect": "old rows preserved + new columns default sensibly + current code works",
        "ok": old_rows_preserved and defaults_ok and rc_reg_n1 == 0,
    }
    log()
    log("=== SUMMARY ===")
    log(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    overall = all(v.get("ok") for v in results.values())
    log(f"P1 OVERALL (fresh/idempotent/N-1-additive/preserve): {'PASS' if overall else 'FAIL'}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\n[evidence written] {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
