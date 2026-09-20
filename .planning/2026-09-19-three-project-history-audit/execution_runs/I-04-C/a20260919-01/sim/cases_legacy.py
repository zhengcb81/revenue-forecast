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

import kernel  # noqa: E402
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
    """The CURRENT machinery under a paused worker, measured two ways (r2).

    (1) Through its public entry: the legacy guard checks runtime_state FIRST, so a
        paused worker is reported as `worker_stopped` and the refcount bookkeeping
        never runs at all.  That is the production behaviour and it is the reason
        the frozen design moves the paused branch in front of the guard (ADR-9).
    (2) Its unregister atom, called directly (no guard): it deletes EVERY entry with
        the caller's pid, so a second, still-active lease of the same process is
        removed and the worker is resumed while that scope is still running.
    """
    h = Harness("F-L2a-legacy", root, verbose=verbose,
                worker_initial={"desired_state": "paused", "runtime_state": "stopped"})
    checks = []

    # (1) public entry point: the guard short-circuits
    res = h.run(h.payload("legacy", mode="legacy", request_budget=100.0,
                          status={"desired_state": "paused", "runtime_state": "stopped"}))
    checks.append(h.check("the legacy/public guard reports worker_stopped for a paused "
                          "worker (the refcount path is unreachable in production)",
                          res["envelope"]["result"]["action"] == "worker_stopped",
                          json.dumps(res["envelope"]["result"])))

    # (2) the unregister atom with two same-pid leases in the file
    entries = [{"pid": os.getpid(), "joined": True}, {"pid": os.getpid(), "joined": True}]
    with open(h.refcount_path, "w", encoding="utf-8") as handle:
        json.dump(entries, handle)
    with open(h.owner_path, "w", encoding="utf-8") as handle:
        handle.write("filing-fetch")
    payload = h.payload("legacy-unregister", mode="legacy", request_budget=50.0,
                        probe={str(os.getpid()): {"alive": True}})
    empty = kernel.legacy_unregister(payload)
    checks.append(h.check("legacy _unregister deletes BOTH same-pid leases (pid-wide delete)",
                          empty is True and not os.path.exists(h.refcount_path),
                          json.dumps({"file_exists": os.path.exists(h.refcount_path),
                                      "empty": empty})))
    checks.append(h.check("...and it also unlinks the owner marker, so the pause it "
                          "did not finish is nobody's obligation",
                          not h.owner_exists()))
    return h.finish(checks, {"documented_as": "ADR-1/ADR-4 counterexample (why removal "
                                             "must be by lease_id)"})


def case_f_lgw1(root, verbose=False):
    """The CURRENT prune never persists: a dead lease survives in the file (r2).

    The legacy register atom is called directly (the public entry is blocked by the
    guard, see F-L2a-legacy): it prunes dead pids into a LOCAL list, so the file
    keeps the dead entry and a later process sees a stale participant forever.
    """
    h = Harness("F-Lgw1", root, verbose=verbose,
                worker_initial={"desired_state": "paused", "runtime_state": "stopped"})
    checks = []
    stale = [{"pid": 55555, "joined": True}]
    with open(h.refcount_path, "w", encoding="utf-8") as handle:
        json.dump(stale, handle)
    payload = h.payload("legacy-register", mode="legacy", request_budget=50.0,
                        probe={"55555": {"alive": False}})
    first = kernel.legacy_register(payload)
    checks.append(h.check("a dead-only refcount is read as 'nobody is here' (first=True), "
                          "so the caller pauses an already-paused worker again",
                          first is True, str(first)))
    checks.append(h.check("the dead participant is dropped from the file with no trace",
                          legacy_pids(h) == [os.getpid()],
                          json.dumps({"file_pids": legacy_pids(h), "me": os.getpid()})))
    checks.append(h.check("no diagnosis of the dead participant is kept anywhere",
                          not any(e.get("event") == "pruned" for e in h.journal_events()),
                          json.dumps(h.journal_events())))
    return h.finish(checks, {
        "documented_as": "why the frozen design validates the owner before claiming a "
                         "cycle and journals every reclaim",
        "v1_claim_corrected": "the v1 text claimed 'the prune is never persisted'; that is "
                              "FALSE for the register path (it writes prune()+self). The "
                              "measured defect is the silent drop plus the extra pause.",
    })


CASES = {
    "F-L1-nolock": case_f_l1_nolock,
    "F-L2a-legacy": case_f_l2a_legacy,
    "F-Lgw1": case_f_lgw1,
}
