"""FIX-W06-GAPS P1 scenario runner (red/green against ONE store module copy).

Faithful adaptation of OPEN5-DOUBT-PROBE scripts/p1_additive_migration.py
(step names kept so evidence maps 1:1 to 01_additive_migration.txt) plus
S6 (error-contract wrap, migration-neutralized) and S7 (fresh-DB full path).

Usage:
  python -X utf8 -B s_p1_migration.py --module <processing_demand_store.py> --out <evidence.txt>

Scenarios (oracle.md P1-a..P1-f):
  S1  fresh migrate                (01: [P1-a ...])
  S2  idempotent re-migrate        (01: [P1-b ...])
  S3  N-1 additive migrate         (01: [P1-b2 ...])  + rows/defaults preserved
  S4  register() on upgraded DB    (01: [P1-c register...])
  S5  claim()   on upgraded DB     (01: [P1-c claim...])
  S6  error contract: missing-column-class failures surface as store-owned
      types (migrator bypassed so the wrap is proven independently)
  S7  fresh-DB full path no-regression (register/claim/list_active/CLI shapes)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import sys
import traceback
from pathlib import Path

LOG: list[str] = []
RESULTS: dict[str, dict] = {}


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


def step(name: str, fn):
    try:
        value = fn()
        log(f"[{name}] rc=0 -> {value!r}" if value is not None else f"[{name}] rc=0")
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
NEW_COLS = {"attempts", "lease_owner", "lease_until",
            "request_sha256", "request_json", "candidate_marker",
            "key_version"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    TMP = Path(os.environ["TEMP"]) / "fix-w06-gaps" / "p1"
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    cand_copy = TMP / "processing_demand_store.py"
    shutil.copy2(args.module, cand_copy)
    log(f"target module : {args.module}")
    log(f"module sha256 : {hashlib.sha256(args.module.read_bytes()).hexdigest()}")
    log(f"temp copy     : {cand_copy}")
    log()

    spec = importlib.util.spec_from_file_location("pds_p1", cand_copy)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    Store = mod.DurableDemandStore

    # ---------- S1 / 01 [P1-a first _initialize on fresh DB] ----------
    db_a = TMP / "a_fresh.sqlite3"
    before_a = dump_schema("S1 before", db_a) if db_a.exists() else []
    rc_a, _ = step("S1 first _initialize on fresh DB", lambda: Store(db_a)._initialize())
    after_a = dump_schema("S1 after", db_a)
    has_table = any(r[1] == "processing_demands" for r in after_a)
    has_idx = any(r[1] == "idx_processing_demands_key" for r in after_a)
    RESULTS["S1_fresh_migrate"] = {
        "maps_01": "[P1-a first _initialize on fresh DB]",
        "rc": rc_a, "table_created": has_table, "index_created": has_idx,
        "schema_before": [list(r) for r in before_a],
        "schema_after": [list(r) for r in after_a],
        "ok": rc_a == 0 and has_table and has_idx,
    }
    log()

    # ---------- S2 / 01 [P1-b re-run _initialize] ----------
    def _reg_one():
        demand, created = Store(db_a).register(
            kind="review", source_id="src-p1", source_sha256="a" * 64,
            review_policy="policy-p1", role_set="normalized,sections",
            gaps=[{"gap": "review_required"}], request={"as_of_date": "2026-09-22"})
        return {"demand_id": demand["demand_id"], "created": created}

    rc_reg, reg_val = step("S2 seed one row via register()", _reg_one)
    con = sqlite3.connect(str(db_a))
    rows_before = con.execute("SELECT COUNT(*) FROM processing_demands").fetchone()[0]
    con.close()
    rc_b1, _ = step("S2 re-run _initialize (2nd)", lambda: Store(db_a)._initialize())
    rc_b2, _ = step("S2 re-run _initialize (3rd)", lambda: Store(db_a)._initialize())
    after_b = dump_schema("S2 after 3 migrations", db_a)
    con = sqlite3.connect(str(db_a))
    rows_after = con.execute("SELECT COUNT(*) FROM processing_demands").fetchone()[0]
    con.close()
    RESULTS["S2_idempotent_re_migrate"] = {
        "maps_01": "[P1-b seed one row via register()] + re-run _initialize (2nd/3rd)",
        "register_rc": rc_reg, "register_value": reg_val if isinstance(reg_val, str) else "OK",
        "rows_before_re_migrate": rows_before,
        "second_migrate_rc": rc_b1, "third_migrate_rc": rc_b2,
        "rows_after_re_migrate": rows_after, "schema_stable": after_b == after_a,
        "ok": rc_reg == 0 and rc_b1 == 0 and rc_b2 == 0
        and rows_before == rows_after == 1 and after_b == after_a,
    }
    log()

    # ---------- S3 / 01 [P1-b2 build N-1 DB ... migrate 1st/2nd] ----------
    db_n1 = TMP / "c_nminus1.sqlite3"

    def _make_n1():
        con = sqlite3.connect(str(db_n1))
        con.execute(N1_DDL)
        con.execute(
            "INSERT INTO processing_demands VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ("demand-n1-1", "k1", "review", "pending", "s1", "b" * 64,
             "p1", "normalized,sections", "[]", 1.0, 1.0))
        con.execute(
            "INSERT INTO processing_demands VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ("demand-n1-2", "k2", "review", "pending", "s2", "c" * 64,
             "p1", "normalized,sections", "[]", 2.0, 2.0))
        con.commit()
        con.close()

    step("S3 build N-1 DB with 2 existing rows", _make_n1)
    before_n1 = dump_schema("S3 N-1 before migrate", db_n1)
    rc_m1, _ = step("S3 migrate N-1 (1st _initialize)", lambda: Store(db_n1)._initialize())
    rc_m2, _ = step("S3 migrate N-1 (2nd _initialize, idempotency)",
                    lambda: Store(db_n1)._initialize())
    after_n1 = dump_schema("S3 N-1 after migrate", db_n1)
    con = sqlite3.connect(str(db_n1))
    physical = {row[1] for row in con.execute("PRAGMA table_info(processing_demands)")}
    con.row_factory = sqlite3.Row
    kept = [dict(r) for r in con.execute(
        "SELECT * FROM processing_demands ORDER BY demand_id").fetchall()]
    con.close()
    log(f"--- rows after migrate ({len(kept)}) ---")
    for r in kept:
        log(f"    {json.dumps(r, ensure_ascii=False, sort_keys=True)}")
    added = NEW_COLS & physical
    missing = NEW_COLS - physical
    old_rows_preserved = {r["demand_id"] for r in kept} >= {"demand-n1-1", "demand-n1-2"}
    defaults_ok = all(
        (r.get("attempts") in (0, None))
        and (r.get("lease_owner") is None)
        and (r.get("lease_until") is None)
        for r in kept if r["demand_id"].startswith("demand-n1-"))
    RESULTS["S3_n1_additive_migrate"] = {
        "maps_01": "[P1-b2 build N-1 DB with 2 existing rows] + migrate 1st/2nd + rows after migrate",
        "migrate_1st_rc": rc_m1, "migrate_2nd_rc": rc_m2,
        "schema_before": [list(r) for r in before_n1],
        "schema_after": [list(r) for r in after_n1],
        "physical_columns_after": sorted(physical),
        "new_columns_added": sorted(added),
        "new_columns_missing": sorted(missing),
        "old_rows_preserved": old_rows_preserved,
        "old_rows_defaults_ok": defaults_ok,
        "ok": rc_m1 == 0 and rc_m2 == 0 and not missing
        and old_rows_preserved and defaults_ok,
    }
    log()

    # ---------- S4/S5 / 01 [P1-c register()/claim() against migrated N-1 DB] ----------
    rc_reg_n1, reg_n1_val = step(
        "S4 register() against migrated N-1 DB",
        lambda: Store(db_n1).register(
            kind="review", source_id="src-n1", source_sha256="d" * 64,
            review_policy="p1", role_set="normalized,sections", gaps=[],
            request={"as_of_date": "2026-09-22"}))
    rc_claim_n1, claim_n1_val = step(
        "S5 claim() against migrated N-1 DB (uses new columns)",
        lambda: Store(db_n1).claim(owner="w1", lease_seconds=300.0))
    con = sqlite3.connect(str(db_n1))
    con.row_factory = sqlite3.Row
    kept2 = [dict(r) for r in con.execute(
        "SELECT demand_id,status FROM processing_demands ORDER BY demand_id").fetchall()]
    con.close()
    log(f"--- rows after register+claim ({len(kept2)}) ---")
    for r in kept2:
        log(f"    {json.dumps(r, ensure_ascii=False, sort_keys=True)}")
    RESULTS["S4_register_on_upgraded"] = {
        "maps_01": "[P1-c register() against migrated N-1 DB]",
        "register_rc": rc_reg_n1,
        "register_result": reg_n1_val if isinstance(reg_n1_val, str) else "OK",
        "ok": rc_reg_n1 == 0,
    }
    RESULTS["S5_claim_on_upgraded"] = {
        "maps_01": "[P1-c claim() against migrated N-1 DB (uses new columns)]",
        "claim_rc": rc_claim_n1,
        "claim_result": claim_n1_val if isinstance(claim_n1_val, str) else "OK",
        "ok": rc_claim_n1 == 0,
    }
    log()

    # ---------- S6 error contract (migrator bypassed on an N-1 DB) ----------
    db_e = TMP / "d_errcontract.sqlite3"

    def _make_err():
        con = sqlite3.connect(str(db_e))
        con.execute(N1_DDL)
        con.execute(
            "INSERT INTO processing_demands VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ("demand-e1", "ke", "review", "pending", "se", "e" * 64,
             "pe", "normalized,sections", "[]", 1.0, 1.0))
        con.commit()
        con.close()

    step("S6 build N-1 DB (no rows) for error-contract", _make_err)

    class NoMigrateStore(Store):
        def _initialize(self) -> None:  # bypass the fix so schema gaps surface
            return None

    def _call(fn):
        def run():
            try:
                fn()
                return "OK"
            except BaseException as exc:  # noqa: BLE001
                owned = isinstance(exc, getattr(mod, "DemandStoreError", ()))
                return f"{type(exc).__name__}: {exc} [store_owned={owned}]"
        return run

    rc_e1, v_e1 = step(
        "S6 register() missing-column-class failure (migrator bypassed)",
        _call(lambda: NoMigrateStore(db_e).register(
            kind="review", source_id="s", source_sha256="e" * 64,
            review_policy="p", role_set="normalized,sections", gaps=[],
            request={})))
    rc_e2, v_e2 = step(
        "S6 claim() missing-column-class failure (migrator bypassed)",
        _call(lambda: NoMigrateStore(db_e).claim(owner="w1")))
    rc_e3, v_e3 = step(
        "S6 list_active() on degraded store (migrator bypassed)",
        _call(lambda: NoMigrateStore(db_e).list_active()))
    owned = lambda v: "[store_owned=True]" in str(v)  # noqa: E731
    RESULTS["S6_error_contract_wrap"] = {
        "maps_01": "P1-c claim rc=1 EXC=OperationalError: no such column: lease_until (bare throw) + card P1 item 2/3",
        "register_result": v_e1, "claim_result": v_e2, "list_active_result": v_e3,
        "expected": "all failures surface as store-owned types "
                    "(DemandStoreUnavailable/DemandStoreError) with the store's own message contract; "
                    "no bare sqlite3.* escapes",
        "ok": bool(owned(v_e1) and owned(v_e2) and owned(v_e3)),
    }
    log()

    # ---------- S7 fresh-DB full path (no regression) ----------
    db_f = TMP / "e_fresh_full.sqlite3"

    def _fresh_path():
        store = Store(db_f)
        demand, created = store.register(
            kind="review", source_id="src-f", source_sha256="f" * 64,
            review_policy="pf", role_set="normalized,sections",
            gaps=[{"gap": "review_required"}], request={"as_of_date": "2026-09-22"})
        again, created2 = store.register(
            kind="review", source_id="src-f", source_sha256="f" * 64,
            review_policy="pf", role_set="normalized,sections",
            gaps=[{"gap": "review_required"}], request={"as_of_date": "2026-09-22"})
        active = store.list_active()
        claimed = store.claim(owner="w1", lease_seconds=300.0)
        return {
            "created": created, "dedupe_created": created2,
            "dedupe_same_id": demand["demand_id"] == again["demand_id"],
            "active_rows": len(active), "claimed_id": claimed["demand_id"],
            "claimed_status": claimed["status"],
        }

    rc_f, v_f = step("S7 fresh-DB register/dedupe/list/claim", _fresh_path)
    RESULTS["S7_fresh_db_no_regression"] = {
        "maps_01": "P1-a/P1-b PASS kept + P1-c old rows preserved PASS kept (fresh-DB path unchanged-green)",
        "rc": rc_f, "value": v_f if isinstance(v_f, str) else v_f,
        "ok": rc_f == 0 and isinstance(v_f, dict)
        and v_f["created"] and not v_f["dedupe_created"] and v_f["dedupe_same_id"]
        and v_f["active_rows"] == 1 and v_f["claimed_status"] == "running",
    }
    log()

    log("=== SUMMARY ===")
    log(json.dumps(RESULTS, ensure_ascii=False, indent=2, default=str))
    overall = all(v.get("ok") for v in RESULTS.values())
    log(f"P1 SCENARIOS (S1..S7): {'PASS' if overall else 'FAIL'}")
    for name, res in RESULTS.items():
        log(f"    {name}: {'PASS' if res.get('ok') else 'FAIL'}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\n[evidence written] {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
