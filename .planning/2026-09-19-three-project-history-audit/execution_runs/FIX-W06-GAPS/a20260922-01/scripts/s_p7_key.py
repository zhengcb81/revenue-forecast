"""FIX-W06-GAPS P7 scenario runner: OPEN-2 option A idempotency key
(c8/c9/c10 counterexample family; oracle APPEND A).

Scenarios (same script drives the BEFORE store = old triple key and the
FIXED store = request-identity key):
  c8  same source/policy/roles, only request as_of_date differs
  c9  same source/policy/roles, only request target differs
  c10 same source/policy/roles (+as_of_date/target), only payload content differs
OLD behavior (before/): each pair silently merges into ONE key and ONE
demand row (created=False on the 2nd call) — the c8/c9/c10 defect.
GREEN expectation: each pair yields TWO keys + TWO demand rows and each row's
request_sha256 == canonical_sha256 of ITS OWN request.
Plus: legacy rows migrated from N-1 keep key_version='triple-v1' and are
never silently merged with v2 registrations (read-time judgment surface).

Usage: python -X utf8 -B s_p7_key.py --module <store.py> --out <evidence.txt>
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
RESULTS: dict = {}


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    TMP = Path(os.environ["TEMP"]) / "fix-w06-gaps" / "p7"
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    shutil.copy2(args.module, TMP / "processing_demand_store.py")
    log(f"target module : {args.module}")
    log(f"module sha256 : {hashlib.sha256(args.module.read_bytes()).hexdigest()}")
    log()
    spec = importlib.util.spec_from_file_location("pds_p7", TMP / "processing_demand_store.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    Store = mod.DurableDemandStore

    base_request = {"as_of_date": "2026-09-22", "target": "acme-annual-report",
                    "note": "payload-v1"}

    def pair_case(tag: str, db_name: str, request_a: dict, request_b: dict):
        db = TMP / db_name
        store = Store(db)
        d1, c1 = store.register(
            kind="review", source_id="src-p7", source_sha256="a1" * 32,
            review_policy="pol-p7", role_set="normalized,sections",
            gaps=[], request=request_a)
        d2, c2 = store.register(
            kind="review", source_id="src-p7", source_sha256="a1" * 32,
            review_policy="pol-p7", role_set="normalized,sections",
            gaps=[], request=request_b)
        rows = store.list_active()
        entry = {
            "request_a": request_a, "request_b": request_b,
            "first": {"created": c1, "demand_id": d1["demand_id"],
                      "demand_key": d1["demand_key"],
                      "request_sha256": d1["request_sha256"],
                      "key_version": d1.get("key_version")},
            "second": {"created": c2, "demand_id": d2["demand_id"],
                       "demand_key": d2["demand_key"],
                       "request_sha256": d2["request_sha256"],
                       "key_version": d2.get("key_version")},
            "distinct_ids": d1["demand_id"] != d2["demand_id"],
            "distinct_keys": d1["demand_key"] != d2["demand_key"],
            "row_count": len(rows),
            "request_sha_a_ok": d1["request_sha256"] == mod.canonical_sha256(request_a),
            "request_sha_b_ok": d2["request_sha256"] == mod.canonical_sha256(request_b),
        }
        entry["ok"] = (
            entry["distinct_ids"] and entry["distinct_keys"]
            and entry["row_count"] == 2
            and entry["request_sha_a_ok"] and entry["request_sha_b_ok"]
            and c1 and c2
        )
        log(f"[{tag}] -> {json.dumps(entry, ensure_ascii=False, sort_keys=True)}")
        return entry

    c8 = pair_case("c8 as_of_date-only difference", "c8.sqlite3",
                   dict(base_request, as_of_date="2026-09-22"),
                   dict(base_request, as_of_date="2026-12-31"))
    c9 = pair_case("c9 target-only difference", "c9.sqlite3",
                   dict(base_request, target="acme-annual-report"),
                   dict(base_request, target="acme-interim-report"))
    c10 = pair_case("c10 payload-only difference", "c10.sqlite3",
                    dict(base_request, note="payload-v1"),
                    dict(base_request, note="payload-v2"))
    RESULTS["P7_key_c8c9c10"] = {
        "maps_p7": "c8/c9/c10 counterexample family (I-06-B use-case (a) axis): same source/policy/roles, "
                   "requests differing in exactly one of as_of_date/target/payload — OLD behavior = same key, "
                   "silent merge-in; expected = two keys + two demand rows + per-row request_sha256",
        "c8_as_of_date": c8, "c9_target": c9, "c10_payload": c10,
        "expect_key": "sha256(canonical_json({source_sha256, review_policy, role_set, "
                      "request_identity{as_of_date, target, payload_digest}}))",
        "ok": c8["ok"] and c9["ok"] and c10["ok"],
    }
    log()

    # legacy-key judgment surface (APPEND A item 2) --------------------------
    db_n1 = TMP / "legacy.sqlite3"
    con = sqlite3.connect(str(db_n1))
    con.execute(
        "CREATE TABLE processing_demands (demand_id TEXT PRIMARY KEY,"
        "demand_key TEXT NOT NULL,kind TEXT NOT NULL,status TEXT NOT NULL,"
        "source_id TEXT NOT NULL,source_sha256 TEXT NOT NULL,"
        "review_policy TEXT NOT NULL,role_set TEXT NOT NULL,"
        "gaps_json TEXT NOT NULL,created_at REAL NOT NULL,updated_at REAL NOT NULL)")
    legacy_key = mod.canonical_sha256({
        "source_sha256": "a1" * 32, "review_policy": "pol-p7",
        "role_set": "normalized,sections"})
    con.execute(
        "INSERT INTO processing_demands VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        ("demand-legacy-1", legacy_key, "review", "pending", "src-p7",
         "a1" * 32, "pol-p7", "normalized,sections", "[]", 1.0, 1.0))
    con.commit()
    con.close()

    def legacy_case():
        store = Store(db_n1)
        rows = store.list_active()
        legacy_rows = [r for r in rows if r["demand_id"] == "demand-legacy-1"]
        legacy_version = legacy_rows[0].get("key_version") if legacy_rows else None
        d3, c3 = store.register(
            kind="review", source_id="src-p7", source_sha256="a1" * 32,
            review_policy="pol-p7", role_set="normalized,sections",
            gaps=[], request=base_request)
        rows_after = store.list_active()
        merged_silently = (not c3) or d3["demand_id"] == "demand-legacy-1"
        return {
            "legacy_key_version": legacy_version,
            "new_register_created": c3,
            "merged_silently": merged_silently,
            "rows_after": len(rows_after),
            "_legacy_rows": len(legacy_rows),
        }

    try:
        legacy = legacy_case()
    except BaseException as exc:  # noqa: BLE001 — on before/ the P1 defect face
        legacy = {"error": f"{type(exc).__name__}: {exc}"}
    log(f"[legacy key_version judgment] -> {json.dumps(legacy, ensure_ascii=False, sort_keys=True)}")
    legacy_ok = (
        legacy.get("_legacy_rows") == 1
        and legacy.get("legacy_key_version") == "triple-v1"
        and legacy.get("new_register_created") is True
        and legacy.get("merged_silently") is False
        and legacy.get("rows_after") == 2
    )
    RESULTS["P7_legacy_key_semantics_preserved"] = {
        "maps_p7": "APPEND A item 2: legacy rows keep historical key semantics (key_version='triple-v1', "
                   "never recomputed); v2 registrations never silently merge across versions "
                   "(OPEN-4-style read-time judgment via key_version)",
        "observed": legacy,
        "ok": legacy_ok,
    }
    log()

    log("=== SUMMARY ===")
    log(json.dumps(RESULTS, ensure_ascii=False, indent=2, default=str))
    for name, res in RESULTS.items():
        log(f"    {name}: {'PASS' if res.get('ok') else 'FAIL'}")
    overall = all(v.get("ok") for v in RESULTS.values())
    log(f"P7 SCENARIOS: {'PASS' if overall else 'FAIL'}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\n[evidence written] {args.out}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
