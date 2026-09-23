"""FIX-W06-GAPS P2-B scenario runner: claim() defined refusals (red/green).

Adapted from OPEN5-DOUBT-PROBE scripts/p2_concurrent_claim.py (cross-process
race kept) + direct refusal-contract probes.  Assertion set (oracle P2-B):
  A  exactly one winner per race round            (01 assert A — stays green)
  B  EVERY loser receives a DEFINED refusal       (02 assert B — red on before/)
     = store-owned exception class + non-empty verbatim text from M-D1,
       never a bare None return value.
  C  single-process refusals: empty queue / unknown id / live-lease id all
     raise M-D1 texts (never silent None).

Usage: python -X utf8 -B s_p2_claim_refusal.py --module <store.py> --out <evidence.txt>
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import traceback
from pathlib import Path

LOG: list[str] = []
RESULTS: dict = {}
PY = sys.executable

M_D1 = {
    "no demand": 'f"no demand {demand_id!r}"',
    "not claimable": 'f"demand {demand_id!r} is not claimable"',
    "no ready": '"no ready demand to claim"',
    "lease expired": '"lease expired"',
}


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


CHILD = r'''
import importlib.util, json, os, sys, time
from pathlib import Path
tmp = Path(os.environ["GAPS_P2_TMP"])
spec = importlib.util.spec_from_file_location("pds", tmp / "processing_demand_store.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
owner = sys.argv[1]
go = tmp / "go.flag"
(tmp / f"ready.{owner}").write_text("1", encoding="utf-8")
while not go.exists():
    time.sleep(0.001)
out = {"owner": owner}
try:
    store = mod.DurableDemandStore(tmp / "claim.sqlite3")
    claimed = store.claim(owner=owner, lease_seconds=60.0)
    out["result"] = claimed
    out["refusal"] = None if claimed is not None else {
        "shape": "None return value", "code": None, "text": None}
except BaseException as exc:
    out["result"] = None
    out["refusal"] = {
        "shape": "exception",
        "code": type(exc).__name__,
        "text": str(exc),
        "store_owned": isinstance(exc, getattr(mod, "DemandStoreError", ())),
    }
print(json.dumps(out, ensure_ascii=False))
'''


def run_round(TMP: Path, round_no: int, owners: list[str]) -> dict:
    db = TMP / "claim.sqlite3"
    if db.exists():
        db.unlink()
    for p in TMP.glob("ready.*"):
        p.unlink()
    go = TMP / "go.flag"
    if go.exists():
        go.unlink()
    spec = importlib.util.spec_from_file_location("pds_p2", TMP / "processing_demand_store.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    demand, created = mod.DurableDemandStore(db).register(
        kind="review", source_id=f"src-r{round_no}", source_sha256="e" * 64,
        review_policy="p", role_set="normalized,sections", gaps=[],
        request={"as_of_date": "2026-09-22"})
    env = dict(os.environ, GAPS_P2_TMP=str(TMP))
    procs = [
        subprocess.Popen([PY, "-X", "utf8", "-B", "-c", CHILD, owner],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        for owner in owners
    ]
    deadline = time.time() + 10
    while time.time() < deadline and not all(
            (TMP / f"ready.{o}").exists() for o in owners):
        time.sleep(0.001)
    time.sleep(0.05)
    go.write_text("go", encoding="utf-8")
    outs = []
    for p in procs:
        stdout, stderr = p.communicate(timeout=30)
        outs.append({"rc": p.returncode,
                     "stdout": stdout.decode("utf-8", "replace").strip(),
                     "stderr": stderr.decode("utf-8", "replace").strip()})
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT demand_id,status,lease_owner,lease_until FROM processing_demands")]
    con.close()
    parsed = []
    for o in outs:
        try:
            parsed.append(json.loads(o["stdout"].splitlines()[-1]))
        except Exception:
            parsed.append({"raw": o})
    winners = [p for p in parsed if p.get("result")]
    losers = [p for p in parsed if not p.get("result")]
    log(f"--- round {round_no} (demand_id={demand['demand_id']}) ---")
    for p, o in zip(parsed, outs):
        log(f"    proc rc={o['rc']} -> {json.dumps(p, ensure_ascii=False)}")
    log(f"    db rows after: {json.dumps(rows, ensure_ascii=False)}")
    log(f"    winners={len(winners)} losers={len(losers)}")
    return {"round": round_no, "demand_id": demand["demand_id"],
            "processes": parsed, "raw": outs, "db_rows_after": rows,
            "winner_count": len(winners), "loser_count": len(losers)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    TMP = Path(os.environ["TEMP"]) / "fix-w06-gaps" / "p2"
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    shutil.copy2(args.module, TMP / "processing_demand_store.py")
    log(f"target module : {args.module}")
    log(f"module sha256 : {hashlib.sha256(args.module.read_bytes()).hexdigest()}")
    log(f"expected refusal contract (oracle M-D1): {json.dumps(M_D1)}")
    log()

    rounds = [run_round(TMP, i, ["wA", "wB"]) for i in range(5)]
    winners_ok = all(r["winner_count"] == 1 for r in rounds)
    loser_refusals = [l.get("refusal") for r in rounds for l in r["processes"]
                      if not l.get("result") and "refusal" in l]
    defined_refusal = bool(loser_refusals) and all(
        isinstance(ref, dict) and ref.get("shape") == "exception"
        and ref.get("code") and ref.get("text") and ref.get("store_owned")
        for ref in loser_refusals)
    RESULTS["P2B_cross_process_race"] = {
        "maps_02": "P2 assert A (exactly one winner) / P2 assert B (defined loser refusal)",
        "rounds": rounds,
        "assert_A_exactly_one_winner": winners_ok,
        "assert_B_defined_refusal_for_loser": defined_refusal,
        "loser_refusal_shapes": loser_refusals,
        "ok": winners_ok and defined_refusal,
    }
    log()
    log(f"P2 assert A (exactly one winner): {'PASS' if winners_ok else 'FAIL'}")
    log(f"P2 assert B (defined loser refusal): {'PASS' if defined_refusal else 'FAIL (bare None / undefined refusal)'}")
    log()

    # ---------- C: single-process refusal contract ----------
    spec = importlib.util.spec_from_file_location("pds_p2c", TMP / "processing_demand_store.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    Store = mod.DurableDemandStore
    db_c = TMP / "single.sqlite3"
    if db_c.exists():
        db_c.unlink()

    def refusal_of(fn):
        try:
            value = fn()
            return {"shape": "None return value" if value is None else "returned",
                    "code": None, "text": None, "value_type": type(value).__name__}
        except BaseException as exc:  # noqa: BLE001
            return {"shape": "exception", "code": type(exc).__name__,
                    "text": str(exc),
                    "store_owned": isinstance(exc, getattr(mod, "DemandStoreError", ()))}

    empty = refusal_of(lambda: Store(db_c).claim(owner="w1"))
    log(f"[S-C1 claim on empty store] -> {json.dumps(empty, ensure_ascii=False)}")
    store = Store(db_c)
    demand, _ = store.register(
        kind="review", source_id="s", source_sha256="a" * 64, review_policy="p",
        role_set="normalized,sections", gaps=[], request={})
    store.claim(owner="wA", lease_seconds=60.0)  # now running under live lease
    unknown = refusal_of(lambda: store.claim(owner="w1", demand_id="demand-nope"))
    log(f"[S-C2 claim unknown demand_id] -> {json.dumps(unknown, ensure_ascii=False)}")
    live = refusal_of(lambda: store.claim(owner="wB", demand_id=demand["demand_id"]))
    log(f"[S-C3 claim live-lease demand_id] -> {json.dumps(live, ensure_ascii=False)}")
    exhausted = refusal_of(lambda: Store(db_c).claim(owner="wB"))
    log(f"[S-C4 claim with only live-lease running rows] -> {json.dumps(exhausted, ensure_ascii=False)}")

    def defined(ref, want_text):
        return (ref.get("shape") == "exception" and ref.get("store_owned")
                and ref.get("text") == want_text)

    RESULTS["P2B_single_process_refusals"] = {
        "maps_02": "P2 assert B (defined refusal, single-process shapes)",
        "empty_queue": empty, "unknown_id": unknown,
        "live_lease_id": live, "exhausted_pool": exhausted,
        "expect_empty": '"no ready demand to claim"',
        "expect_unknown": 'f"no demand {demand_id!r}" -> "no demand \'demand-nope\'"',
        "expect_live_lease": 'f"demand {demand_id!r} is not claimable"',
        "expect_exhausted": '"no ready demand to claim"',
        "ok": defined(empty, "no ready demand to claim")
        and defined(unknown, "no demand 'demand-nope'")
        and defined(live, f"demand {demand['demand_id']!r} is not claimable")
        and defined(exhausted, "no ready demand to claim"),
    }
    log()
    log("=== SUMMARY ===")
    log(json.dumps(RESULTS, ensure_ascii=False, indent=2, default=str))
    overall = all(v.get("ok") for v in RESULTS.values())
    log(f"P2B SCENARIOS: {'PASS' if overall else 'FAIL'}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\n[evidence written] {args.out}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        args_out = None
        sys.exit(1)
