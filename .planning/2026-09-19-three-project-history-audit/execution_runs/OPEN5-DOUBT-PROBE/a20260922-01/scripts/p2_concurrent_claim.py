"""P2 — concurrent claim probe (exactly-one-winner + defined refusal).

Targets:
  PRIMARY  I-06-A iso/candidate/processing_demand_store.py :: DurableDemandStore.claim
           (SQLite, cross-process) — claim(owner, lease_seconds).
  SECONDARY in-memory DemandQueue.claim(demand_id=...) (I-06-B iso/cw copy and the
           RF product byte-copy) — two threads race for the same demand_id.

Freeze (oracle-lite): A = exactly one winner; B = loser receives a DEFINED
refusal (code/text). All state under %TEMP%; raw output ->
evidence/02_concurrent_claim.txt.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

BASE = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs"
)
CAND_SRC = BASE / r"I-06-A\a20260919-01\iso\candidate\processing_demand_store.py"
MEM_CW = BASE / r"I-06-B\a20260919-01\iso\cw\src\company_wiki\source_catalog\processing_demand.py"
MEM_RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\scripts\processing_demand.py")
OUT = BASE / r"OPEN5-DOUBT-PROBE\a20260922-01\evidence\02_concurrent_claim.txt"
TMP = Path(os.environ["TEMP"]) / "open5-doubt-probe" / "p2"
PY = sys.executable

LOG: list[str] = []
results: dict = {}


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


CHILD = r'''
import importlib.util, json, os, sys, time
from pathlib import Path
tmp = Path(os.environ["OPEN5_P2_TMP"])
spec = importlib.util.spec_from_file_location("pds", tmp / "processing_demand_store.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
owner = sys.argv[1]
go = tmp / "go.flag"
ready = tmp / f"ready.{owner}"
ready.write_text("1", encoding="utf-8")
while not go.exists():
    time.sleep(0.001)
out = {"owner": owner}
try:
    store = mod.DurableDemandStore(tmp / "claim.sqlite3")
    claimed = store.claim(owner=owner, lease_seconds=60.0)
    out["result"] = claimed
    out["refusal"] = None if claimed is not None else {
        "shape": "None return value",
        "code": None,
        "text": None,
    }
except BaseException as exc:
    out["exception"] = f"{type(exc).__name__}: {exc}"
print(json.dumps(out, ensure_ascii=False))
'''


def run_round(round_no: int, owners: list[str]) -> dict:
    db = TMP / "claim.sqlite3"
    if db.exists():
        db.unlink()
    for p in TMP.glob("ready.*"):
        p.unlink()
    go = TMP / "go.flag"
    if go.exists():
        go.unlink()
    # one pending demand only
    spec = importlib.util.spec_from_file_location("pds_p2", TMP / "processing_demand_store.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    demand, created = mod.DurableDemandStore(db).register(
        kind="review",
        source_id=f"src-r{round_no}",
        source_sha256="e" * 64,
        review_policy="p",
        role_set="normalized,sections",
        gaps=[],
        request={"as_of_date": "2026-09-22"},
    )
    env = dict(os.environ, OPEN5_P2_TMP=str(TMP))
    procs = [
        subprocess.Popen(
            [PY, "-X", "utf8", "-B", "-c", CHILD, owner],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        )
        for owner in owners
    ]
    deadline = time.time() + 10
    while time.time() < deadline and not all(
        (TMP / f"ready.{o}").exists() for o in owners
    ):
        time.sleep(0.001)
    time.sleep(0.05)  # let every child reach the spin-wait
    go.write_text("go", encoding="utf-8")
    outs = []
    for p in procs:
        stdout, stderr = p.communicate(timeout=30)
        outs.append({
            "rc": p.returncode,
            "stdout": stdout.decode("utf-8", "replace").strip(),
            "stderr": stderr.decode("utf-8", "replace").strip(),
        })
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
    return {
        "round": round_no,
        "demand_id": demand["demand_id"],
        "processes": parsed,
        "raw": outs,
        "db_rows_after": rows,
        "winner_count": len(winners),
        "loser_count": len(losers),
    }


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    cand_copy = TMP / "processing_demand_store.py"
    shutil.copy2(CAND_SRC, cand_copy)
    log(f"PRIMARY candidate : {CAND_SRC}")
    log(f"  sha256={hashlib.sha256(CAND_SRC.read_bytes()).hexdigest()}")
    log()

    # ---------- cross-process race: 2 processes, 5 rounds ----------
    rounds = [run_round(i, ["wA", "wB"]) for i in range(5)]
    winners_ok = all(r["winner_count"] == 1 for r in rounds)
    loser_refusals = [
        l.get("refusal") for r in rounds for l in r["processes"]
        if not l.get("result") and "refusal" in l
    ]
    defined_refusal = all(
        isinstance(ref, dict) and (ref.get("code") or ref.get("text"))
        for ref in loser_refusals
    ) and bool(loser_refusals)
    results["P2-cross-process"] = {
        "rounds": rounds,
        "assert_A_exactly_one_winner": winners_ok,
        "assert_B_defined_refusal_for_loser": defined_refusal,
        "loser_refusal_shapes": loser_refusals,
        "note": "candidate claim() has NO demand_id parameter; with exactly one "
                "pending demand the race is for that single demand_id",
        "ok": winners_ok and defined_refusal,
    }
    log()
    log(f"P2 assert A (exactly one winner): {'PASS' if winners_ok else 'FAIL'}")
    log(f"P2 assert B (defined loser refusal): {'PASS' if defined_refusal else 'FAIL (refusal shape: bare None return, no code/text)'}")
    log()

    # ---------- in-memory DemandQueue: two threads, same demand_id ----------
    def mem_race(mod_path: Path, tag: str) -> dict:
        spec = importlib.util.spec_from_file_location(f"mem_{tag}", mod_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"mem_{tag}"] = mod  # dataclass needs the module registered
        spec.loader.exec_module(mod)
        q = mod.DemandQueue(lease_seconds=60.0)
        d = q.enqueue(key="k-race", kind="review", now=0.0)
        barrier = threading.Barrier(2)
        outcomes = []

        def worker(owner: str) -> None:
            barrier.wait()
            try:
                claimed = q.claim(owner=owner, now=1.0, demand_id=d.demand_id)
                outcomes.append({"owner": owner, "won": True,
                                 "status": claimed.status,
                                 "lease_owner": claimed.lease_owner})
            except Exception as exc:  # noqa: BLE001
                outcomes.append({"owner": owner, "won": False,
                                 "exception_type": type(exc).__name__,
                                 "refusal_text": str(exc)})

        ts = [threading.Thread(target=worker, args=(o,)) for o in ("tA", "tB")]
        for t in ts:
            t.start()
        for t in ts:
            t.join(timeout=10)
        winners = [o for o in outcomes if o["won"]]
        losers = [o for o in outcomes if not o["won"]]
        log(f"--- in-memory race [{tag}] {mod_path} ---")
        for o in outcomes:
            log(f"    {json.dumps(o, ensure_ascii=False)}")
        return {
            "module": str(mod_path),
            "module_sha256": hashlib.sha256(mod_path.read_bytes()).hexdigest(),
            "outcomes": outcomes,
            "winner_count": len(winners),
            "loser_count": len(losers),
            "loser_refusal": losers[0] if losers else None,
        }

    mem_cw = mem_race(MEM_CW, "cw-iso-zr507")
    mem_rf = mem_race(MEM_RF, "rf-product-zr701")
    mem_ok = (
        mem_cw["winner_count"] == 1 and mem_rf["winner_count"] == 1
        and mem_cw["loser_refusal"] is not None and mem_rf["loser_refusal"] is not None
    )
    results["P2-in-memory-threads"] = {
        "cw_iso": mem_cw,
        "rf_product": mem_rf,
        "assert_A_exactly_one_winner":
            mem_cw["winner_count"] == 1 and mem_rf["winner_count"] == 1,
        "assert_B_defined_refusal_for_loser":
            all(x["loser_refusal"] and x["loser_refusal"].get("refusal_text")
                for x in (mem_cw, mem_rf)),
        "ok": mem_ok,
    }
    log()
    log("=== SUMMARY ===")
    log(json.dumps(results, ensure_ascii=False, indent=2, default=str))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\n[evidence written] {OUT}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(LOG) + "\n" + traceback.format_exc(), encoding="utf-8")
        sys.exit(1)
