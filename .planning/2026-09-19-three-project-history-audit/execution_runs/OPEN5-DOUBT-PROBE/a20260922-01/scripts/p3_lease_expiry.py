"""P3 — lease expiry probe (OPEN-5 ruling C5: resume after lease expiry ⇒ REJECT).

PRIMARY   candidate DurableDemandStore (real 1s lease + real sleep):
          - is there ANY resume API? (expect ABSENT — record exact surface)
          - after expiry: can the same owner / a third party re-claim or resume?
            (record ACTUAL behavior, incl. the stranded running+expired face)
SECONDARY in-memory DemandQueue (injected clock): complete()/heartbeat() past
          lease_until ⇒ must raise DemandStateError("lease expired") = REJECT.

Raw output -> evidence/03_lease_expiry.txt. No numeric spec is asserted
(1s is a test fixture only).
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import os
import re
import shutil
import sys
import time
import traceback
from pathlib import Path

BASE = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs"
)
CAND_SRC = BASE / r"I-06-A\a20260919-01\iso\candidate\processing_demand_store.py"
MEM_CW = BASE / r"I-06-B\a20260919-01\iso\cw\src\company_wiki\source_catalog\processing_demand.py"
OUT = BASE / r"OPEN5-DOUBT-PROBE\a20260922-01\evidence\03_lease_expiry.txt"
TMP = Path(os.environ["TEMP"]) / "open5-doubt-probe" / "p3"

LOG: list[str] = []
results: dict = {}


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


def step(name: str, fn):
    try:
        value = fn()
        log(f"[{name}] rc=0 -> {value!r}")
        return 0, value
    except Exception as exc:  # noqa: BLE001
        detail = f"{type(exc).__name__}: {exc}"
        log(f"[{name}] rc=1 EXC={detail}")
        return 1, detail


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    cand_copy = TMP / "processing_demand_store.py"
    shutil.copy2(CAND_SRC, cand_copy)
    spec = importlib.util.spec_from_file_location("pds_p3", cand_copy)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    Store = mod.DurableDemandStore

    # ---------- P3-0: what resume-like API exists at all? ----------
    src_text = cand_copy.read_text(encoding="utf-8")
    surface = {
        "public_methods_of_DurableDemandStore": sorted(
            n for n, f in inspect.getmembers(Store, inspect.isfunction)
            if not n.startswith("__")
        ),
        "module_level_functions": sorted(
            n for n, f in inspect.getmembers(mod, inspect.isfunction)
            if not n.startswith("__") and f.__module__ == mod.__name__
        ),
        "cli_commands": re.findall(r'choices=\(([^)]*)\)', src_text),
        "occurrences_of_resume_in_source": [
            f"line {i}: {line.rstrip()}"
            for i, line in enumerate(src_text.splitlines(), 1)
            if "resume" in line.lower()
        ],
        "occurrences_of_complete_in_source": [
            f"line {i}: {line.rstrip()}"
            for i, line in enumerate(src_text.splitlines(), 1)
            if re.search(r"\bcomplete\b", line)
        ],
    }
    log("=== P3-0 candidate API surface (resume search) ===")
    log(json.dumps(surface, ensure_ascii=False, indent=2))
    has_resume = any("resume" in m for m in surface["public_methods_of_DurableDemandStore"])
    results["P3-0-resume-api-existence"] = {
        "surface": surface,
        "resume_api_exists": has_resume,
        "verdict": "ABSENT-implement-first" if not has_resume else "present",
        "checked_paths": [
            str(CAND_SRC),
            "I-06-B attempt: scripts/w06b_review_harness.py, after/*, commands.json "
            "(review lifecycle only — no demand resume entry)",
        ],
    }
    log()

    # ---------- P3-a: real 1s lease on the candidate store ----------
    db = TMP / "lease.sqlite3"
    store = Store(db)
    demand, _ = store.register(
        kind="review",
        source_id="src-lease",
        source_sha256="f" * 64,
        review_policy="p",
        role_set="normalized,sections",
        gaps=[],
        request={"as_of_date": "2026-09-22"},
    )
    log(f"registered demand_id={demand['demand_id']}")

    def _claim_w1():
        return store.claim(owner="w1", lease_seconds=1.0)

    rc_c1, claimed = step("P3-a claim(w1, lease_seconds=1.0)", _claim_w1)
    lease_until = claimed.get("lease_until") if isinstance(claimed, dict) else None
    log(f"    lease_until={lease_until} (wall clock now={time.time():.3f})")
    log("[P3-a] sleeping 1.4s past lease expiry ...")
    time.sleep(1.4)
    log(f"    wall clock now={time.time():.3f} (lease expired)")

    def _resume():
        # The C5 surface: resume of the original request after expiry.
        fn = getattr(store, "resume")
        return fn(demand_id=demand["demand_id"], owner="w1")

    rc_resume, resume_val = step("P3-a resume() after expiry (C5 must REJECT)", _resume)

    def _reclaim_same():
        return store.claim(owner="w1", lease_seconds=1.0)

    rc_same, same_val = step("P3-a re-claim by SAME owner after expiry", _reclaim_same)

    def _reclaim_other():
        return store.claim(owner="w2", lease_seconds=1.0)

    rc_other, other_val = step("P3-a re-claim by THIRD party after expiry", _reclaim_other)

    def _complete():
        return getattr(store, "complete")

    rc_comp, comp_val = step("P3-a complete() existence on candidate", _complete)

    import sqlite3
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT demand_id,status,lease_owner,lease_until FROM processing_demands")]
    con.close()
    log(f"    db rows now: {json.dumps(rows, ensure_ascii=False)}")

    stranded = (
        rows and rows[0]["status"] == "running"
        and (isinstance(same_val, type(None)) or same_val is None)
        and (isinstance(other_val, type(None)) or other_val is None)
    )
    results["P3-a-candidate-store"] = {
        "claim_rc": rc_c1,
        "lease_seconds_fixture": 1.0,
        "lease_until": lease_until,
        "resume_rc": rc_resume,
        "resume_result": resume_val,
        "reclaim_same_owner_after_expiry": {"rc": rc_same, "result": same_val},
        "reclaim_third_party_after_expiry": {"rc": rc_other, "result": other_val},
        "complete_exists": rc_comp == 0,
        "db_rows": rows,
        "c5_expected": "resume after expiry ⇒ REJECT",
        "c5_actual": (
            "no resume surface at all (AttributeError) ⇒ C5 untestable on the "
            "candidate" if rc_resume == 1 and "AttributeError" in str(resume_val)
            else f"resume rc={rc_resume} result={resume_val}"
        ),
        "stranded_running_expired_lease": bool(stranded),
        "stranded_note": (
            "claim() only selects status IN ('pending','failed') — a 'running' row "
            "with an expired lease is NEVER selectable again; the demand is stranded"
        ) if stranded else None,
    }
    log()

    # ---------- P3-b: in-memory DemandQueue, injected clock ----------
    spec2 = importlib.util.spec_from_file_location("mem_p3", MEM_CW)
    mem = importlib.util.module_from_spec(spec2)
    sys.modules["mem_p3"] = mem
    spec2.loader.exec_module(mem)
    q = mem.DemandQueue(lease_seconds=1.0)  # 1s fixture lease
    d = q.enqueue(key="k-lease", kind="review", now=0.0)
    claimed2 = q.claim(owner="w1", now=0.0, demand_id=d.demand_id)
    log(f"[P3-b] claimed at now=0.0 lease_until={claimed2.lease_until}")

    def _complete_expired():
        return q.complete(demand_id=d.demand_id, owner="w1", now=2.0)

    rc_ce, ce_val = step("P3-b complete() at now=2.0 (> lease_until=1.0)", _complete_expired)

    def _heartbeat_expired():
        return q.heartbeat(demand_id=d.demand_id, owner="w1", now=2.0)

    rc_he, he_val = step("P3-b heartbeat() at now=2.0", _heartbeat_expired)

    def _wrong_owner():
        return q.complete(demand_id=d.demand_id, owner="w2", now=0.5)

    rc_wo, wo_val = step("P3-b complete() by WRONG owner inside lease", _wrong_owner)

    def _expire():
        return q.expire(now=2.0)

    rc_ex, ex_val = step("P3-b explicit expire(now=2.0)", _expire)
    snap = q.snapshot()
    log(f"    after expire: {[(s.demand_id, s.status, s.lease_owner) for s in snap]}")

    def _reclaim_after_expire():
        return q.claim(owner="w2", now=2.0, demand_id=d.demand_id)

    rc_rc2, rc2_val = step("P3-b explicit re-claim after expire (must be explicit)",
                           _reclaim_after_expire)

    reject_texts = []
    for v in (ce_val, he_val, wo_val):
        if isinstance(v, str) and "EXC=" not in v:
            continue
    for v in (ce_val, he_val, wo_val):
        if isinstance(v, str) and v.startswith("DemandStateError"):
            reject_texts.append(v)
    c5_met_memory = (
        rc_ce == 1 and "lease expired" in str(ce_val)
        and rc_he == 1 and "lease expired" in str(he_val)
    )
    results["P3-b-in-memory-queue"] = {
        "module": str(MEM_CW),
        "lease_seconds_fixture": 1.0,
        "complete_after_expiry": {"rc": rc_ce, "result": ce_val},
        "heartbeat_after_expiry": {"rc": rc_he, "result": he_val},
        "complete_wrong_owner_in_lease": {"rc": rc_wo, "result": wo_val},
        "explicit_expire": {"rc": rc_ex, "result": ex_val},
        "reclaim_after_expire": {"rc": rc_rc2, "result": rc2_val},
        "rejection_texts": reject_texts,
        "c5_expected": "resume-equivalent (complete/heartbeat) after expiry ⇒ REJECT",
        "c5_met": c5_met_memory,
    }
    log()
    log("=== SUMMARY ===")
    log(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    log(f"P3 OVERALL C5 on candidate: {results['P3-a-candidate-store']['c5_actual']}")
    log(f"P3 OVERALL C5 on memory queue: {'PASS (REJECT)' if c5_met_memory else 'FAIL'}")

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
