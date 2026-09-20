"""RED counterexamples against a faithful port of the CURRENT production
machinery (fetch_filing.py L409-610).  These runs are the reason ADR-1/ADR-3
exist; they are not product behaviour claims beyond the port itself.
"""

from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from harness import Harness, banner  # noqa: E402

SCHEMA = "filing-fetch.pause-refcount/2"


def pid_of(h, tag):
    for row in h.journal_events():
        if row.get("tag") == tag:
            return row.get("pid")
    return None


def legacy_pids(h):
    """The legacy format stores pid only; return the pid list in file order."""
    view = h.lease_view()
    return [e.get("pid") for e in view.get("entries", []) if isinstance(e, dict)]


def case_f_l1_nolock(root, verbose=False):
    """Two processes inside the current non-atomic register => lost update."""
    h = Harness("F-L1-nolock", root, verbose=verbose)
    checks = []
    a = h.payload("A", mode="legacy", request_budget=100.0, use_lock=False,
                  wait_for=h.gate_wait("racestop"))
    proc_a = h.spawn(a)
    h.wait_reached("racestop")
    pid_a = pid_of(h, "A")
    checks.append(h.check("A is parked INSIDE the read-modify-write (racestop)",
                          pid_a is not None, str(pid_a)))

    b = h.payload("B", mode="legacy", request_budget=100.0, use_lock=False)
    res_b = h.run(b, timeout=30)
    checks.append(h.check("B completed its own register + pause",
                          res_b["envelope"]["result"]["action"] == "paused_by_us"
                          and res_b["envelope"]["result"]["pause_calls"] == 1,
                          json.dumps(res_b["envelope"]["result"])))
    view_b = h.lease_view()
    checks.append(h.check("B's lease is on disk before A writes",
                          legacy_pids(h) == [res_b["envelope"]["result"]["pid"]],
                          json.dumps(view_b)))

    h.open_fence("racestop")
    res_a = h.collect(proc_a)
    view_after = h.lease_view()
    checks.append(h.check("A's stale snapshot OVERWROTE B (lost update)",
                          legacy_pids(h) == [pid_a], json.dumps(view_after)))
    checks.append(h.check("both processes believed they were first (double pause)",
                          h.counts()["pause_calls"] == 2, json.dumps(h.counts())))
    checks.append(h.check("B is no longer in the refcount although B is still running",
                          pid_of(h, "B") not in legacy_pids(h),
                          json.dumps({"file_pids": legacy_pids(h), "pid_b": pid_of(h, "B")})))
    return h.finish(checks, {"pid_a": pid_a,
                             "register_events": h.journal_events("legacy_register")})


def case_f_l2a_legacy(root, verbose=False):
    """Current _unregister deletes by pid: nested scopes resume twice."""
    h = Harness("F-L2a-legacy", root, verbose=verbose)
    checks = []
    res = h.run(h.payload("nested", mode="legacy", two_scopes=True), argv=["--two-scopes"])
    env = res["envelope"]
    leases = [e["lease_id"] for e in env["enters"]]
    checks.append(h.check("both scopes registered under one pid",
                          len(leases) == 2 and len(h.lease_view()["entries"]) == 2,
                          json.dumps(h.lease_view())))
    first_exit = env["exits"][0]
    checks.append(h.check("first exit reports 'last' and resumes (WRONG: the second "
                          "scope is still in flight)",
                          first_exit["action"] == "released_last"
                          and first_exit["resume_calls"] == 1, json.dumps(first_exit)))
    checks.append(h.check("second scope's lease was deleted by the pid-wide filter",
                          not h.lease_view()["exists"], json.dumps(h.lease_view())))
    second_exit = env["exits"][1]
    checks.append(h.check("second exit resumes AGAIN (double resume)",
                          second_exit["resume_calls"] == 1
                          and h.counts()["resume_calls"] == 2, json.dumps(h.counts())))
    return h.finish(checks)


def case_f_lgw1(root, verbose=False):
    """Current code never persists the prune: a dead lease keeps the worker paused."""
    h = Harness("F-Lgw1", root, verbose=verbose,
                worker_initial={"desired_state": "paused", "runtime_state": "stopped"})
    checks = []
    stale = [{"pid": 55555, "joined": True}]
    with open(h.refcount_path, "w", encoding="utf-8") as handle:
        json.dump(stale, handle)
    with open(h.owner_path, "w", encoding="utf-8") as handle:
        handle.write("filing-fetch")
    b = h.payload("B", mode="legacy", request_budget=100.0,
                  probe={"55555": {"alive": False, "start_time": None}})
    res = h.run(b)
    result = res["envelope"]["result"]
    checks.append(h.check("B joined but was treated as a fresh pause",
                          result["action"] == "paused_by_us" or result["action"] == "joined",
                          json.dumps(result)))
    checks.append(h.check("another pause was issued on an already paused worker",
                          h.counts()["pause_calls"] == 1, json.dumps(h.counts())))
    checks.append(h.check("the dead lease was silently dropped from the file "
                          "(no diagnosis kept)",
                          legacy_pids(h) == [result["pid"]],
                          json.dumps({"file_pids": legacy_pids(h), "result": result})))
    checks.append(h.check("owner marker still present; no owner change recorded",
                          h.owner_exists()))
    return h.finish(checks)


CASES = {
    "F-L1-nolock": case_f_l1_nolock,
    "F-L2a-legacy": case_f_l2a_legacy,
    "F-Lgw1": case_f_lgw1,
}
