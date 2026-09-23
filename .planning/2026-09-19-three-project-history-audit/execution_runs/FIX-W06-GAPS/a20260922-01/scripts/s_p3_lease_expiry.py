"""FIX-W06-GAPS P3-A/P3-B scenario runner (red/green against ONE store copy).

Adapted from OPEN5-DOUBT-PROBE scripts/p3_lease_expiry.py candidate side
(03_lease_expiry.txt [P3-a candidate-store]) + the new oracle expectations.
Scenarios:
  S-P3a  claim(w1, lease=1.0) -> running; sleep past expiry;
         re-claim same owner / third party => defined "lease expired"
         (03: both returned bare None => stranded running row)
  S-P3b  claim(demand_id=<running+expired>) => "lease expired";
         claim(demand_id=<running+live>)   => "demand ... is not claimable"
  S-P3c  explicit expire() reclaim (memory-queue expire() shape):
         expire returns count, row -> pending with lease cleared, then
         claim() succeeds again (explicit — never a silent steal)
  S-P3d  structural absence stays: no resume / no complete surface
         (unbuilt interfaces — I-06-B domain; assert ABSENT, never fake it)

Usage: python -X utf8 -B s_p3_lease_expiry.py --module <store.py> --out <evidence.txt>
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import os
import sqlite3
import sys
import time
import traceback
from pathlib import Path

LOG: list[str] = []
RESULTS: dict = {}


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


def outcome(fn):
    try:
        value = fn()
        return {"rc": 0, "shape": "None return value" if value is None else "returned",
                "result": value}
    except BaseException as exc:  # noqa: BLE001
        return {"rc": 1, "shape": "exception", "code": type(exc).__name__, "text": str(exc)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    TMP = Path(os.environ["TEMP"]) / "fix-w06-gaps" / "p3"
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    shutil.copy2(args.module, TMP / "processing_demand_store.py")
    log(f"target module : {args.module}")
    log(f"module sha256 : {hashlib.sha256(args.module.read_bytes()).hexdigest()}")
    log()
    spec = importlib.util.spec_from_file_location("pds_p3", TMP / "processing_demand_store.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    Store = mod.DurableDemandStore

    db = TMP / "lease.sqlite3"
    store = Store(db)
    demand, _ = store.register(
        kind="review", source_id="src-lease", source_sha256="f" * 64,
        review_policy="p", role_set="normalized,sections", gaps=[], request={})
    did = demand["demand_id"]
    log(f"registered demand_id={did}")

    claimed = outcome(lambda: store.claim(owner="w1", lease_seconds=1.0))
    log(f"[S-P3a claim(w1, lease_seconds=1.0)] -> {json.dumps(claimed, ensure_ascii=False, default=str)}")
    log("    sleeping 1.4s past lease expiry ...")
    time.sleep(1.4)

    reclaim_same = outcome(lambda: store.claim(owner="w1"))
    log(f"[S-P3a re-claim by SAME owner after expiry] -> {json.dumps(reclaim_same, ensure_ascii=False, default=str)}")
    reclaim_third = outcome(lambda: store.claim(owner="w2"))
    log(f"[S-P3a re-claim by THIRD party after expiry] -> {json.dumps(reclaim_third, ensure_ascii=False, default=str)}")
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT demand_id,status,lease_owner,lease_until FROM processing_demands")]
    con.close()
    log(f"    db rows now: {json.dumps(rows, ensure_ascii=False)}")
    stranded = any(r["status"] == "running" for r in rows)

    def defined_expired(ref):
        return (ref.get("shape") == "exception"
                and ref.get("code") == "DemandStateError"
                and ref.get("text") == "lease expired")

    RESULTS["P3B_expired_refusals"] = {
        "maps_03": "[P3-a re-claim by SAME owner / THIRD party after expiry] (03: rc=0 -> None, row stranded running)",
        "claim_for_reference": claimed,
        "reclaim_same_owner_after_expiry": reclaim_same,
        "reclaim_third_party_after_expiry": reclaim_third,
        "db_rows": rows,
        "expect": 'DemandStateError("lease expired") — never silent None',
        "ok": defined_expired(reclaim_same) and defined_expired(reclaim_third),
    }
    log()

    # S-P3b: demand_id-shaped refusals around expiry -------------------------
    db2 = TMP / "lease_ids.sqlite3"
    store2 = Store(db2)
    d1, _ = store2.register(
        kind="review", source_id="s1", source_sha256="1" * 64, review_policy="p",
        role_set="normalized,sections", gaps=[], request={})
    c1 = outcome(lambda: store2.claim(owner="w1", demand_id=d1["demand_id"], lease_seconds=1.0))
    log(f"[S-P3b claim(demand_id, lease=1.0)] -> {json.dumps(c1, ensure_ascii=False, default=str)}")
    live_ref = outcome(lambda: store2.claim(owner="w2", demand_id=d1["demand_id"]))
    log(f"[S-P3b claim(demand_id) INSIDE lease] -> {json.dumps(live_ref, ensure_ascii=False, default=str)}")
    time.sleep(1.4)
    expired_ref = outcome(lambda: store2.claim(owner="w2", demand_id=d1["demand_id"]))
    log(f"[S-P3b claim(demand_id) AFTER expiry] -> {json.dumps(expired_ref, ensure_ascii=False, default=str)}")

    def defined_not_claimable(ref):
        return (ref.get("shape") == "exception"
                and ref.get("code") == "DemandStateError"
                and ref.get("text") == f"demand {d1['demand_id']!r} is not claimable")

    RESULTS["P3B_demand_id_refusals"] = {
        "maps_03": "P3-B extension: claim(demand_id) around lease expiry (c5 family)",
        "inside_lease_refusal": live_ref,
        "after_expiry_refusal": expired_ref,
        "expect_inside": 'DemandStateError(f"demand {demand_id!r} is not claimable")',
        "expect_after_expiry": 'DemandStateError("lease expired")',
        "ok": defined_not_claimable(live_ref) and defined_expired(expired_ref),
    }
    log()

    # S-P3c: explicit expire() reclaim --------------------------------------
    expire_out = outcome(lambda: store2.expire())
    log(f"[S-P3c explicit expire()] -> {json.dumps(expire_out, ensure_ascii=False, default=str)}")
    con = sqlite3.connect(str(db2))
    con.row_factory = sqlite3.Row
    after_expire = [dict(r) for r in con.execute(
        "SELECT demand_id,status,lease_owner,lease_until FROM processing_demands")]
    con.close()
    log(f"    after expire: {json.dumps(after_expire, ensure_ascii=False)}")
    reclaim = outcome(lambda: store2.claim(owner="w2", demand_id=d1["demand_id"]))
    log(f"[S-P3c explicit re-claim after expire] -> {json.dumps(reclaim, ensure_ascii=False, default=str)}")

    expire_ok = (
        expire_out["rc"] == 0 and expire_out.get("result") == 1
        and len(after_expire) == 1
        and after_expire[0]["status"] == "pending"
        and after_expire[0]["lease_owner"] is None
        and after_expire[0]["lease_until"] is None
        and reclaim["rc"] == 0 and reclaim["shape"] == "returned"
        and reclaim["result"]["status"] == "running"
        and reclaim["result"]["lease_owner"] == "w2"
    )
    RESULTS["P3A_explicit_expire_reclaim"] = {
        "maps_03": "03 [P3-a ...] stranded_running_expired_lease=true repair: explicit expire/reclaim entry "
                   "(memory queue expire() shape: after expire: [('pd-0','pending',None)])",
        "expire": expire_out, "rows_after_expire": after_expire,
        "reclaim_after_expire": reclaim,
        "expect": "expire() returns 1; row -> pending with lease cleared; explicit re-claim succeeds",
        "ok": expire_ok,
    }
    log()

    # S-P3d: structural absence of resume/complete (never fake it) ----------
    surface = [m for m in dir(store) if not m.startswith("__")]
    has_resume = hasattr(store, "resume")
    has_complete = hasattr(store, "complete")
    log(f"[S-P3d surface] {sorted(surface)} resume={has_resume} complete={has_complete}")
    RESULTS["P3D_interface_absence"] = {
        "maps_03": "03 [P3-0 candidate API surface] resume/complete ABSENT-implement-first — parent ruling: "
                   "unbuilt interfaces (handoff L240 不得假装存在), I-06-B domain, NOT built here",
        "public_surface": sorted(surface),
        "resume_absent": not has_resume,
        "complete_absent": not has_complete,
        "ok": (not has_resume) and (not has_complete),
    }
    log()

    log("=== SUMMARY ===")
    log(json.dumps(RESULTS, ensure_ascii=False, indent=2, default=str))
    overall = all(v.get("ok") for v in RESULTS.values())
    log(f"P3 SCENARIOS: {'PASS' if overall else 'FAIL'}")
    for name, res in RESULTS.items():
        log(f"    {name}: {'PASS' if res.get('ok') else 'FAIL'}")
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
