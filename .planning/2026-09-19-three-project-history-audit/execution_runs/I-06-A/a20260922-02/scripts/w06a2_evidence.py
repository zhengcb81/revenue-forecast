#!/usr/bin/env python3
"""Collect the card-required evidence artifacts for I-06-A / a20260922-02:

  evidence/demand.cross-process.json      (cross-process registration/query)
  evidence/request-to-demand-binding.json (request identity -> demand binding,
                                           incl. the c8/c9/c10 counterexample)
  evidence/paused-before-after.json       (N3: nothing auto-resumes/starts)
  evidence/prod-unchanged.json            (production repos: ZERO writes)
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
CASES = Path(__file__).resolve().parent / "w06a2_cases.py"
EVID = ATTEMPT / "evidence"
TARGET = ATTEMPT / "iso"
CW_REAL = Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog")

sys.path.insert(0, str(CASES.parent))
import w06a2_cases as suite  # noqa: E402


def run_child(*args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(CASES), "--target", str(TARGET), "--child", *args],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[-800:]
    return json.loads(proc.stdout)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    EVID.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="w06a2-evid-"))
    db = tmp / "catalog.sqlite3"

    threads_before = sorted(th.name for th in threading.enumerate())

    # ---- cross-process scenario: four REAL processes over one catalog -------
    reg_a = suite.sample_registration(as_of_date="2026-09-19")
    reg_repeat = suite.sample_registration(as_of_date="2026-09-19")
    reg_asof = suite.sample_registration(as_of_date="2027-03-31")
    reg_c89 = suite.sample_registration(as_of_date="2026-09-19", target="Zijin Mining H")
    specs = {}
    for name, reg in (("a", reg_a), ("repeat", reg_repeat),
                      ("asof", reg_asof), ("c89", reg_c89)):
        p = tmp / f"spec-{name}.json"
        p.write_text(json.dumps(reg), encoding="utf-8")
        specs[name] = p

    p1 = run_child("register", "--db", str(db), "--spec", str(specs["a"]))       # process 1
    q2 = run_child("query", "--db", str(db))                                      # process 2
    p3 = run_child("register", "--db", str(db), "--spec", str(specs["repeat"]))   # process 3
    q4 = run_child("query", "--db", str(db))                                      # process 4
    p5 = run_child("register", "--db", str(db), "--spec", str(specs["asof"]))     # process 5
    p6 = run_child("register", "--db", str(db), "--spec", str(specs["c89"]))      # process 6
    q7 = run_child("query", "--db", str(db))                                      # process 7

    # Self-evidence (review finding 3): each child reports its own pid and
    # literal argv in its output envelope.
    children = [
        {"step": step, "pid": out.get("pid"), "argv": out.get("argv")}
        for step, out in (("p1_register", p1), ("p2_query", q2),
                          ("p3_resubmit", p3), ("p4_query", q4),
                          ("p5_asof_register", p5), ("p6_entity_register", p6),
                          ("p7_query", q7))
    ]

    cross = {
        "scenario": [
            "p1 register request A (not_reviewed block)",
            "p2 independent process queries",
            "p3 independent process resubmits the IDENTICAL request A",
            "p4 independent process queries",
            "p5 register request B (ONLY as_of_date differs)",
            "p6 register request C (entity differs)",
            "p7 independent process queries",
        ],
        "p1_register": p1,
        "p2_query": q2,
        "p3_resubmit": p3,
        "p4_query": q4,
        "p5_asof_register": p5,
        "p6_entity_register": p6,
        "p7_query": q7,
        "children": children,
        "assertions": {
            "p2_sees_exactly_one": q2["count"] == 1,
            "resubmit_reuses_same_id": p3["demand_id"] == p1["demand_id"],
            "p4_still_one_todo": q4["count"] == 1,
            "asof_divergent_is_second_demand": p5["demand_id"] != p1["demand_id"],
            "entity_divergent_is_third_demand": p6["demand_id"] != p1["demand_id"],
            "p7_sees_three_rows": q7["count"] == 3,
            "durable_ids_not_per_process_pd0": all(
                row["demand_id"].startswith("demand-") for row in q7["demands"]
            ),
            "seven_distinct_child_pids": len({c["pid"] for c in children}) == 7,
            "children_self_report_argv": all(c["argv"] for c in children),
        },
        "database_exists": db.exists(),
    }
    assert all(cross["assertions"].values()), cross["assertions"]
    (EVID / "demand.cross-process.json").write_text(
        json.dumps(cross, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ---- request-to-demand binding (c8/c9/c10 counterexample now passes) -----
    t = suite.load_tree(TARGET)
    dstore = t["pd"].CatalogDemandStore(db)
    rows = {r.demand_id: r for r in dstore.list()}
    binding = {
        "rule": "demand_key = sha256(canonical_json({source_sha256, review_policy,"
                " role_set, request_identity})) (OPEN-2 option A / OPEN-5 ruling 4.5.1)",
        "bindings": [
            {
                "label": label,
                "request_sha256": suite.request_sha256_of_text(reg["request_json"]),
                "request_identity": reg["request_identity"],
                "demand_id": demand_id,
                "row_request_sha256": rows[demand_id].request_sha256,
                "row_matches_request":
                    rows[demand_id].request_sha256 == suite.request_sha256_of_text(reg["request_json"]),
            }
            for label, reg, demand_id in (
                ("c1_first_request", reg_a, p1["demand_id"]),
                ("c3_identical_resubmission", reg_repeat, p3["demand_id"]),
                ("c10_asof_only_changed", reg_asof, p5["demand_id"]),
                ("c8_c9_entity_changed", reg_c89, p6["demand_id"]),
            )
        ],
        "assertions": {
            "each_row_binds_its_own_request": all(
                rows[demand_id].request_sha256 == suite.request_sha256_of_text(reg["request_json"])
                for reg, demand_id in ((reg_a, p1["demand_id"]), (reg_repeat, p3["demand_id"]),
                                       (reg_asof, p5["demand_id"]), (reg_c89, p6["demand_id"]))
            ),
            "no_silent_absorption": len({p1["demand_id"], p5["demand_id"], p6["demand_id"]}) == 3,
            "c8_c9_c10_counterexample_resolved":
                rows[p5["demand_id"]].request_sha256 != rows[p1["demand_id"]].request_sha256,
        },
    }
    assert all(binding["assertions"].values()), binding["assertions"]
    (EVID / "request-to-demand-binding.json").write_text(
        json.dumps(binding, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ---- paused-before-after (N3: nothing auto-resumes / starts) ------------
    threads_after = sorted(th.name for th in threading.enumerate())
    statuses = {r.demand_id: (r.status, r.lease_owner) for r in dstore.list()}
    paused = {
        "note": "registration + cross-process queries ran with the worker side"
                " untouched: no scheduler/worker/thread was started and no demand"
                " was auto-claimed or auto-advanced (OPEN-3).",
        "threads_before": threads_before,
        "threads_after": threads_after,
        "threads_unchanged": threads_before == threads_after,
        "demand_states_after_all_registrations": {
            k: {"status": v[0], "lease_owner": v[1]} for k, v in statuses.items()
        },
        "no_auto_claim": all(v[0] == "pending" and v[1] is None for v in statuses.values()),
        "worker_control_touched": False,
    }
    assert paused["threads_unchanged"] and paused["no_auto_claim"], paused
    (EVID / "paused-before-after.json").write_text(
        json.dumps(paused, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ---- production repos: ZERO writes (copy fidelity + anchor hashes) ------
    implemented = ("store.py", "processing_demand.py",
                   "prompt_injection.py", "prompt_injection_guard.py")
    prod = {"production_writes": "ZERO", "files": {}}
    for name in implemented:
        real = CW_REAL / name
        before = ATTEMPT / "before" / "cw" / "src" / "company_wiki" / "source_catalog" / name
        prod["files"][name] = {
            "real_repo_sha256": sha256_file(real),
            "before_copy_sha256": sha256_file(before),
            "copy_fidelity": sha256_file(real) == sha256_file(before),
        }
    prod["dependency_copies_match_real"] = True
    for rel in ("admission.py", "lock.py", "llm_failure_policy.py", "models.py"):
        real = CW_REAL / rel
        before = ATTEMPT / "before" / "cw" / "src" / "company_wiki" / "source_catalog" / rel
        same = sha256_file(real) == sha256_file(before)
        prod["files"][rel] = {"copy_fidelity": same}
        prod["dependency_copies_match_real"] = prod["dependency_copies_match_real"] and same
    assert all(v.get("copy_fidelity") for v in prod["files"].values()), prod
    (EVID / "prod-unchanged.json").write_text(
        json.dumps(prod, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("evidence collected:", sorted(p.name for p in EVID.glob("*.json")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
