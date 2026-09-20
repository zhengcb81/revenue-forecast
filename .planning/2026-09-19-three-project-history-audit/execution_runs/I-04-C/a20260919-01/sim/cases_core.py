"""I-04-C protocol cases: F-L1, F-L2a-d, F-L3, F-LK4 (see oracle.md)."""

from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from harness import (  # noqa: E402
    LOCK, REFCOUNT, WORKER, Harness, b64, banner, sha256_file,
)


SCHEMA = "filing-fetch.pause-refcount/2"


def prewrite_refcount(harness, payload):
    with open(harness.refcount_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)


def prewrite_lease(harness, lease_id, pid, start_time="", boot="seedboot", marker=True):
    prewrite_refcount(harness, {
        "schema": SCHEMA, "generation": 1,
        "entries": [{"pid": pid, "boot_uuid": boot, "os_start_time": start_time,
                     "lease_id": lease_id, "invocations": 1}],
        "resume": {"required": False},
        "owner": {"lease_id": lease_id, "generation": 1},
    })
    if marker:
        with open(harness.owner_path, "w", encoding="utf-8") as handle:
            handle.write("filing-fetch")


def case_f_l1(root, verbose=False):
    """Card F-L1: A acquire, B acquire, A release, B release; initial running.

    One process per participant (enter + hold + release inside the participant),
    which is the production shape and makes the declared-liveness model exact:
    a participant is alive exactly while its process runs, so releases can be
    ordered by fences without any participant dying unexpectedly.

    Expectation: leases 1 -> 2 -> 1 -> 0; one pause; A's release does not resume
    (it hands the cycle over, ADR-10); B's release resumes exactly once.
    """
    import shutil as _shutil

    case_dir = os.path.join(root, "F-L1")
    _shutil.rmtree(case_dir, ignore_errors=True)   # no stale evidence from a prior run
    h = Harness("F-L1", root, verbose=verbose)
    checks = []
    t0 = time.monotonic()

    def mark(label):
        print(f"[F-L1] t+{time.monotonic() - t0:7.3f}s {label}")

    a = h.payload("A", request_budget=100.0, lifetime=True,
                  wait_for=h.gate_wait("enter_registered", tag="A"))
    a["wait_for"].update(h.gate_wait("lifetime_hold", tag="A"))
    a["wait_for"].update(h.gate_wait("before_resume", tag="A"))
    proc_a = h.spawn(a)
    mark("A spawned")
    h.wait_reached("enter_registered")
    mark("A reached enter_registered")
    view1 = h.lease_view()
    c1 = h.counts()
    checks.append(h.check("step1 lease_set=={A}", view1["entries"] == [a["lease_id"]],
                          json.dumps(view1)))
    checks.append(h.check("step1 generation==1", view1["generation"] == 1, str(view1["generation"])))
    checks.append(h.check("step1 owner is A", view1["owner_lease"] == a["lease_id"], str(view1)))
    checks.append(h.check("step1 pause_calls==1", c1["pause_calls"] == 1, json.dumps(c1)))
    checks.append(h.check("step1 owner marker exists (pause confirmed)", h.owner_exists()))
    checks.append(h.check("step1 worker desired=paused", c1["desired_state"] == "paused",
                          json.dumps(c1)))

    b = h.payload("B", request_budget=100.0, lifetime=True,
                  wait_for=h.gate_wait("enter_registered", tag="B"))
    b["wait_for"].update(h.gate_wait("lifetime_hold", tag="B"))
    b["wait_for"].update(h.gate_wait("before_resume", tag="B"))
    proc_b = h.spawn(b)
    mark("B spawned")
    time.sleep(0.4)
    checks.append(h.check("step2 B waits while A holds the critical section",
                          h.envelope_of("B")["kind"] == "none",
                          "B envelope=" + h.envelope_of("B")["kind"]))
    checks.append(h.check("step2 no second pause while B waits",
                          h.counts()["pause_calls"] == 1, json.dumps(h.counts())))
    h.open_fence("enter_registered", tag="A")
    h.wait_reached("enter_registered", timeout=30, tag="B")
    mark("B reached enter_registered")
    view2 = h.lease_view()
    c2 = h.counts()
    checks.append(h.check("step2 lease_set=={A,B}",
                          view2["entries"] == sorted([a["lease_id"], b["lease_id"]]),
                          json.dumps(view2)))
    checks.append(h.check("step2 pause_calls still 1", c2["pause_calls"] == 1, json.dumps(c2)))
    checks.append(h.check("step2 B joined (no pause of its own)",
                          h.envelope_of("B")["kind"] == "none",
                          "B still inside its scope"))
    h.open_fence("enter_registered", tag="B")   # B finishes registering, stays in scope
    mark("B registered")

    # A leaves first: it is not the owner, so it hands the cycle over.
    h.open_fence("lifetime_hold", tag="A")
    res_a = h.collect(proc_a)
    mark("A collected")
    entered_a = res_a["envelope"]["result"]
    released_a = res_a["envelope"]["exit"]
    checks.append(h.check("A enter paused_by_us", entered_a["action"] == "paused_by_us",
                          json.dumps(entered_a)))
    view3 = h.lease_view()
    c3 = h.counts()
    checks.append(h.check("step3 A release leaves only B, with B as owner",
                          view3["entries"] == [b["lease_id"]]
                          and view3["owner_lease"] == b["lease_id"], json.dumps(view3)))
    checks.append(h.check("step3 the non-owner last participant does NOT resume; "
                          "it hands the cycle over",
                          released_a["action"] == "released_took_ownership",
                          json.dumps(released_a)))
    checks.append(h.check("step3 resume_calls==0 after A's release",
                          c3["resume_calls"] == 0, json.dumps(c3)))

    h.open_fence("lifetime_hold", tag="B")
    res_b = h.collect(proc_b)
    c4 = h.counts()
    view4 = h.lease_view()
    released_b = res_b["envelope"]["exit"]
    checks.append(h.check("step4 B closes the handed-over cycle by resuming",
                          released_b["action"] == "released_with_pending_resume",
                          json.dumps(released_b)))
    checks.append(h.check("step4 resume_calls==1", c4["resume_calls"] == 1, json.dumps(c4)))
    checks.append(h.check("step4 pause_calls==1", c4["pause_calls"] == 1, json.dumps(c4)))
    checks.append(h.check("step4 refcount removed", not view4["exists"], json.dumps(view4)))
    checks.append(h.check("step4 owner removed", not h.owner_exists()))
    checks.append(h.check("step4 worker desired=enabled", c4["desired_state"] == "enabled",
                          json.dumps(c4)))
    checks.append(h.check("step4 lock file present (never unlinked)",
                          os.path.exists(os.path.join(h.base, LOCK))))
    extra = {"A_lease_id": a["lease_id"], "B_lease_id": b["lease_id"],
             "resume_actions": h.journal_events("worker_resume"),
             "pause_actions": h.journal_events("worker_pause"),
             "lease_timeline": [view1, view2, view3, view4]}
    return h.finish(checks, extra)


def case_f_l2a(root, verbose=False):
    """Same pid: (a) can nesting even happen?  (b) independent release for two
    same-pid leases produced by different processes."""
    h = Harness("F-L2a", root, verbose=verbose)
    checks = []

    # (a) reachability: measured.  A second scope of the SAME process that enters
    # while a first scope is inside its pause window sees desired_state=paused and
    # no owner marker of its own kind, so it JOINS (guard order matters, ADR-9);
    # two leases from one pid then coexist and release independently.
    raw = _run_nesting(root)
    checks.append(h.check("second same-process scope joins the first one's cycle",
                          raw["second_action"] == "joined", json.dumps(raw)))
    checks.append(h.check("...without pausing the worker a second time",
                          raw["second_writes"] == 1 and raw["counts"]["pause_calls"] == 1,
                          json.dumps(raw)))
    checks.append(h.check("nesting is reachable (one process, two leases)",
                          raw["nesting_established"] is True, json.dumps(raw)))
    checks.append(h.check("the nesting cycle resolves with one resume",
                          raw["counts"]["resume_calls"] == 1, json.dumps(raw["counts"])))
    checks.append(h.check("the nesting cycle issues one pause in total",
                          raw["counts"]["pause_calls"] == 1, json.dumps(raw["counts"])))
    checks.append(h.check("one lease outlives the other's release",
                          raw["exit_first_action"] == "released_joined", json.dumps(raw)))
    checks.append(h.check("state is clean after both scopes exit",
                          raw["lease_view"]["exists"] is False
                          and raw["owner_exists"] is False, json.dumps(raw)))

    # (b) two same-pid leases in one refcount, released one at a time by a third
    # process: only the requested lease_id may disappear.  Two physical processes
    # share a pid in the FILE (prewritten), which is the only way this state can
    # exist per (a).
    h2 = Harness("F-L2a-b", root, verbose=verbose,
                 worker_initial={"desired_state": "paused", "runtime_state": "running"})
    prewrite_lease(h2, "pair-lease-a", 8101, "5000")
    with open(h2.refcount_path, encoding="utf-8") as handle:
        seeded = json.load(handle)
    seeded["entries"].append({"pid": 8101, "boot_uuid": "seedboot2",
                              "os_start_time": "5000", "lease_id": "pair-lease-b",
                              "invocations": 1})
    prewrite_refcount(h2, seeded)
    seed_probe = {"8101": {"alive": True, "start_time": "5000"}}
    exit_1 = h2.run(h2.payload("o1", phase="exit", lease_id="pair-lease-a",
                               probe=seed_probe))
    checks.append(h2.check("releasing one lease keeps the other",
                           h2.lease_view()["entries"] == ["pair-lease-b"],
                           json.dumps(h2.lease_view())))
    checks.append(h2.check("first release did not resume",
                           h2.counts()["resume_calls"] == 0, json.dumps(h2.counts())))
    exit_2 = h2.run(h2.payload("o2", phase="exit", lease_id="pair-lease-b",
                               probe=seed_probe))
    checks.append(h2.check("the last non-owner release takes the cycle over "
                           "instead of resuming (ADR-10)",
                           exit_2["envelope"]["result"]["action"] == "released_took_ownership",
                           json.dumps(exit_2["envelope"]["result"])))
    checks.append(h2.check("the obligation is now owned by the surviving releaser",
                           h2.lease_view()["owner_lease"] == "pair-lease-b"
                           and h2.lease_view()["resume_required"] is True,
                           json.dumps(h2.lease_view())))
    exit_3 = h2.run(h2.payload("o3", phase="exit", lease_id="pair-lease-b",
                               probe=seed_probe))
    checks.append(h2.check("the owner's own release resumes exactly once",
                           exit_3["envelope"]["result"]["action"] == "released_last"
                           and h2.counts()["resume_calls"] == 1, json.dumps(h2.counts())))
    checks.append(h2.check("no pid-wide delete: the first release was not enough",
                           exit_1["envelope"]["result"]["action"] == "released_joined",
                           json.dumps(exit_1["envelope"]["result"])))
    checks.append(h2.check("state cleaned up after the cycle closes",
                           not h2.lease_view()["exists"], json.dumps(h2.lease_view())))

    # (c) the join path, reachable with a paused worker that still reports
    # runtime_state=running (decision.md ADR-9)
    h3 = Harness("F-L2a-c", root, verbose=verbose,
                 worker_initial={"desired_state": "paused", "runtime_state": "running"})
    prewrite_lease(h3, "seed-lease-0001", 8102, "", marker=False)
    other = h3.run(h3.payload("other", request_budget=100.0, probe={"8102": {"alive": True}}))
    checks.append(h3.check("a new participant joins the existing pause cycle",
                           other["envelope"]["result"]["action"] == "joined",
                           json.dumps(other["envelope"]["result"])))
    checks.append(h3.check("joining does not pause again",
                           h3.counts()["pause_calls"] == 0, json.dumps(h3.counts())))
    checks.append(h3.check("both leases coexist",
                           sorted(h3.lease_view()["entries"]) ==
                           sorted([other["envelope"]["lease_id"], "seed-lease-0001"]),
                           json.dumps(h3.lease_view())))
    leave = h3.run(h3.payload("other-exit", phase="exit",
                              lease_id=other["envelope"]["lease_id"],
                              probe={"8102": {"alive": True}}))
    checks.append(h3.check("the joiner's release leaves the seed lease",
                           h3.lease_view()["entries"] == ["seed-lease-0001"],
                           json.dumps(h3.lease_view())))
    return h.finish(checks, {"nesting_probe": raw, "second_base": h2.base,
                             "pair_result": [exit_1["envelope"]["result"],
                                             exit_2["envelope"]["result"],
                                             exit_3["envelope"]["result"]],
                             "join_result": other["envelope"]["result"]})


def _run_nesting(root):
    """Run sim/nesting_probe.py in-process and return its record."""
    import subprocess

    from harness import PYTHON

    proc = subprocess.run(
        [PYTHON, "-B", os.path.join(HERE, "nesting_probe.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    for line in (proc.stdout or "").splitlines():
        if line.startswith("{"):
            return json.loads(line)
    return {"error": "nesting probe produced no record", "stdout": proc.stdout,
            "stderr": proc.stderr}


def case_f_l2b(root, verbose=False):
    """PID reuse: same pid, different recorded OS start time => reclaimable."""
    h = Harness("F-L2b", root, verbose=verbose,
                worker_initial={"desired_state": "paused", "runtime_state": "running"})
    checks = []
    stale = {"schema": "filing-fetch.pause-refcount/2", "generation": 1,
             "entries": [{"pid": 9001, "boot_uuid": "oldboot", "os_start_time": "1000",
                          "lease_id": "stale-lease-0001", "invocations": 1}],
             "resume": {"required": True, "generation": 1,
                        "lease_id": "stale-lease-0001", "phase": "resume_pending"},
             "owner": {"lease_id": "stale-lease-0001", "generation": 1}}
    prewrite_refcount(h, stale)
    fresh = h.payload("B", request_budget=100.0,
                      probe={"9001": {"alive": True, "start_time": "2000"}},
                      status={"desired_state": "paused", "runtime_state": "running"})
    res = h.run(fresh)
    view = h.lease_view()
    checks.append(h.check("takeover happened under the lock (then its own pause cycle)",
                          "takeover_resumed" in res["envelope"]["result"].get("actions", [])
                          or res["envelope"]["result"]["action"] == "takeover_resumed",
                          json.dumps(res["envelope"]["result"])))
    checks.append(h.check("stale lease reclaimed, new lease present",
                          view.get("entries") == [fresh["lease_id"]], json.dumps(view)))
    checks.append(h.check("the orphaned resume ran once", h.counts()["resume_calls"] == 1,
                          json.dumps(h.counts())))
    pruned = h.journal_events("pruned")
    checks.append(h.check("pid_reuse recorded as the reclaim reason",
                          bool(pruned) and pruned[0]["items"][0]["reason"] == "pid_reuse",
                          json.dumps(pruned)))
    return h.finish(checks)


def case_f_l2c(root, verbose=False):
    """Same pid but no incarnation evidence => fail closed, nothing written."""
    h = Harness("F-L2c", root, verbose=verbose,
                worker_initial={"desired_state": "paused", "runtime_state": "running"})
    checks = []
    unknown = {"schema": "filing-fetch.pause-refcount/2", "generation": 1,
               "entries": [{"pid": 9002, "boot_uuid": "", "os_start_time": "7777",
                            "lease_id": "unverifiable-0002", "invocations": 1}],
               "resume": {"required": False}, "owner": {"lease_id": "unverifiable-0002",
                                                        "generation": 1}}
    prewrite_refcount(h, unknown)
    before = sha256_file(h.refcount_path)
    res = h.run(h.payload("B", request_budget=100.0,
                          probe={"9002": {"alive": True, "start_time": None}},
                          status={"desired_state": "paused", "runtime_state": "running"}))
    view = h.lease_view()
    checks.append(h.check("fail closed on unknown liveness",
                          res["envelope"]["result"]["action"] == "lease_conflict_unknown",
                          json.dumps(res["envelope"]["result"])))
    checks.append(h.check("state file untouched (same sha256)", sha256_file(h.refcount_path) == before,
                          before + " -> " + sha256_file(h.refcount_path)))
    checks.append(h.check("no lease added", view.get("entries") == ["unverifiable-0002"],
                          json.dumps(view)))
    checks.append(h.check("no pause, no resume",
                          h.counts()["pause_calls"] == 0 and h.counts()["resume_calls"] == 0,
                          json.dumps(h.counts())))

    # control: the same setup with a DEAD holder must be reclaimable, not blocked
    h2 = Harness("F-L2c-dead", root, verbose=verbose,
                 worker_initial={"desired_state": "paused", "runtime_state": "running"})
    dead = {"schema": "filing-fetch.pause-refcount/2", "generation": 1,
            "entries": [{"pid": 9102, "boot_uuid": "x", "os_start_time": "7777",
                         "lease_id": "dead-lease-0002", "invocations": 1}],
            "resume": {"required": False}, "owner": {"lease_id": "dead-lease-0002",
                                                     "generation": 1}}
    prewrite_refcount(h2, dead)
    res2 = h2.run(h2.payload("B", request_budget=100.0,
                             probe={"9102": {"alive": False}},
                             status={"desired_state": "paused", "runtime_state": "running"}))
    checks.append(h2.check("a proven-dead holder is reclaimed (fresh cycle, not a block)",
                           res2["envelope"]["result"]["action"] == "paused_by_us"
                           and h2.counts()["pause_calls"] == 1,
                           json.dumps(res2["envelope"]["result"])))
    checks.append(h2.check("the dead lease is gone, ours remains",
                           h2.lease_view()["entries"] == [res2["envelope"]["lease_id"]],
                           json.dumps(h2.lease_view())))
    return h.finish(checks, {"second_base": h2.base})


def case_f_l2d(root, verbose=False):
    """Lock contention: 8 concurrent participants serialise cleanly.

    NOTE (measured, see decision.md ADR-9): with the frozen guards the join path
    is never taken when participants start together, because the first pause has
    already stopped the worker; the later participants therefore observe
    worker_stopped and write nothing.  The lock is still what keeps the state
    consistent, and exactly one pause/resume pair happens either way.
    """
    h = Harness("F-L2d", root, verbose=verbose)
    checks = []
    tags = [f"P{index}" for index in range(8)]
    procs = []
    payloads = {}
    for tag in tags:
        payload = h.payload(tag, request_budget=60.0, lifetime=True,
                            wait_for=h.gate_wait("lifetime_hold", tag=tag))
        payloads[tag] = payload
        procs.append((tag, h.spawn(payload)))
    # every participant reaches the hold point inside its own scope; they are
    # serialised by the lease lock, so once all eight have announced, all eight
    # leases must be in the refcount.
    import time as _time

    t0 = _time.monotonic()
    for tag, _ in procs:
        h.wait_reached("enter_registered", timeout=60, tag=tag)
        if verbose:
            print(f"[F-L2d] {tag} registered at t+{_time.monotonic() - t0:.3f}s", flush=True)
    view_held = h.lease_view()
    checks.append(h.check("all eight leases are registered while all eight run",
                          sorted(view_held["entries"]) ==
                          sorted(payloads[t]["lease_id"] for t in tags),
                          json.dumps(view_held)))
    for tag in tags:
        h.open_fence("lifetime_hold", tag=tag)
    results = [h.collect(proc, timeout=60) for _, proc in procs]
    enters = [r["envelope"]["result"] for r in results]
    exits = [r["envelope"]["exit"] for r in results]
    enter_actions = [e["action"] for e in enters]
    exit_actions = [e["action"] for e in exits]
    checks.append(h.check("8 clean exits", all(r["returncode"] == 0 for r in results),
                          json.dumps([r["returncode"] for r in results])))
    checks.append(h.check("exactly one participant opens the cycle",
                          enter_actions.count("paused_by_us") == 1
                          and enter_actions.count("joined") == 7, json.dumps(enter_actions)))
    checks.append(h.check("exactly one pause for the whole run",
                          h.counts()["pause_calls"] == 1, json.dumps(h.counts())))
    checks.append(h.check("exactly one resume, from the last releaser",
                          h.counts()["resume_calls"] == 1
                          and exit_actions.count("released_last") == 1,
                          json.dumps({"counts": h.counts(), "exits": exit_actions})))
    checks.append(h.check("the other seven releases are join/transfer only",
                          all(a in {"released_joined", "released_took_ownership",
                                    "released_with_pending_resume"} for a in exit_actions),
                          json.dumps(exit_actions)))
    checks.append(h.check("exactly one release is the resuming one",
                          exit_actions.count("released_last") == 1, json.dumps(exit_actions)))
    checks.append(h.check("no lock timeouts and no gate timeouts",
                          not h.journal_events("lock_timeout")
                          and not h.journal_events("gate_timeout"),
                          json.dumps({"locks": h.journal_events("lock_timeout"),
                                      "gates": h.journal_events("gate_timeout")})))
    checks.append(h.check("state cleaned up", not h.lease_view()["exists"]
                          and not h.owner_exists(), json.dumps(h.lease_view())))
    return h.finish(checks, {"lock_waits": [e.get("lock_wait") for e in enters],
                             "enter_actions": enter_actions,
                             "exit_actions": exit_actions,
                             "held_view": view_held})


def case_f_l3(root, verbose=False):
    """User-paused worker with no tool ownership: zero writes, zero resume.

    F-L3a models the live case (a paused worker the tool must not resume) with
    desired_state=paused + runtime_state=running, i.e. the check the current code
    performs AFTER the runtime_state guard (fetch_filing.py L528-L537).
    F-L3b keeps the plain stopped-worker variant for the same window.
    """
    checks = []

    h = Harness("F-L3a", root, verbose=verbose,
                worker_initial={"desired_state": "paused", "runtime_state": "running"})
    res = h.run(h.payload("U", request_budget=50.0,
                          status={"desired_state": "paused", "runtime_state": "running"}))
    checks.append(h.check("a: respect_paused", res["envelope"]["result"]["action"] == "respect_paused",
                          json.dumps(res["envelope"]["result"])))
    checks.append(h.check("a: zero pause and zero resume",
                          h.counts()["pause_calls"] == 0 and h.counts()["resume_calls"] == 0,
                          json.dumps(h.counts())))
    checks.append(h.check("a: no refcount file was ever created",
                          not os.path.exists(h.refcount_path)))
    checks.append(h.check("a: no owner marker was ever created", not h.owner_exists()))
    checks.append(h.check("a: worker still paused", h.counts()["desired_state"] == "paused",
                          json.dumps(h.counts())))
    lock_only = [e for e in h.journal_events() if e.get("event") not in {"lock_acq", "lock_rel"}]
    checks.append(h.check("a: no side effects beyond taking the lock (no write, no CLI)",
                          lock_only == [], json.dumps(lock_only)))

    hb = Harness("F-L3b", root, verbose=verbose,
                 worker_initial={"desired_state": "paused", "runtime_state": "stopped"})
    resb = hb.run(hb.payload("U", request_budget=50.0,
                             status={"desired_state": "paused", "runtime_state": "stopped"}))
    checks.append(hb.check("b: a paused-but-not-running worker with NO tool evidence "
                           "is still the user's pause (zero writes)",
                           resb["envelope"]["result"]["action"] == "respect_paused",
                           json.dumps(resb["envelope"]["result"])))
    stopped = Harness("F-L3c", root, verbose=verbose,
                      worker_initial={"desired_state": "enabled", "runtime_state": "stopped"})
    res_stopped = stopped.run(stopped.payload(
        "U", request_budget=50.0,
        status={"desired_state": "enabled", "runtime_state": "stopped"}))
    checks.append(stopped.check("c: an enabled but stopped worker is a no-op too",
                                res_stopped["envelope"]["result"]["action"] == "worker_stopped",
                                json.dumps(res_stopped["envelope"]["result"])))
    checks.append(hb.check("b: zero pause and zero resume",
                           hb.counts()["pause_calls"] == 0 and hb.counts()["resume_calls"] == 0,
                           json.dumps(hb.counts())))
    checks.append(hb.check("b: no refcount file", not os.path.exists(hb.refcount_path)))
    checks.append(hb.check("b: no owner marker", not hb.owner_exists()))
    lock_only_b = [e for e in hb.journal_events()
                   if e.get("event") not in {"lock_acq", "lock_rel"}]
    checks.append(hb.check("b: no side effects beyond taking the lock",
                           lock_only_b == [], json.dumps(lock_only_b)))
    return h.finish(checks, {"second_base": hb.base})


CASES = {
    "F-L1": case_f_l1,
    "F-L2a": case_f_l2a,
    "F-L2b": case_f_l2b,
    "F-L2c": case_f_l2c,
    "F-L2d": case_f_l2d,
    "F-L3": case_f_l3,
}
