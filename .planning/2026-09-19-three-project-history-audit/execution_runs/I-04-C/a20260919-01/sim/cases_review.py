"""r2 cases demanded by the independent review (each maps to one finding).

  V4-a   F-I04C-01: the owner dies INSIDE the obligation-writing critical section
         (entries empty, resume.required=True, owner=dead).  The last releaser must
         not leave a permanently paused worker.
  V4-e   F-I04C-02: the refcount's owner is a THIRD PARTY (not us, no pid to
         prove it dead).  Releasing must fail closed: no ownership claim, no
         resume, owner evidence untouched.
  V4-f   F-I04C-02: downstream of V4-e, a new participant must NOT resume that
         foreign pause (`owner_evidence_foreign`).
  F-W7   ADR-5 W7/T10: the owner evidence changes while we are inside the release
         critical section (scope-time user intervention).
  F-L2c-dead   F-I04C-06: a dead lease with NO owner marker and non-empty entries
         is TOOL evidence, not a user pause.
  F-L2e-stale / F-L2e-fixed   F-I04C-07: the ADR-11 pair.  The stale variant reads
         the status before the lock (v1 shape); under the SAME schedule it pauses
         twice, while the fixed path joins once.
  F-GEN  F-I04C-03: the generation counter is per-file and restarts at 1; this
         records the documented behaviour instead of claiming monotonicity.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from harness import Harness, b64  # noqa: E402

SCHEMA = "filing-fetch.pause-refcount/2"


def write_state(harness, payload):
    with open(harness.refcount_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)


def _clean(root, case):
    shutil.rmtree(os.path.join(root, case), ignore_errors=True)


def case_v4a(root, verbose=False):
    """F-I04C-01: the owner dies INSIDE the obligation-writing critical section.

    A is the ONLY participant of its cycle (so its release really is the last one
    and the obligation write is reached), then it dies at exactly that point.  The
    next participant must take the orphaned obligation over and close it, and its
    own cycle must resolve normally.  Nobody may be left with a paused worker.
    """
    _clean(root, "V4-a")
    h = Harness("V4-a", root, verbose=verbose)
    checks = []
    a = h.payload("A", request_budget=100.0, lifetime=True,
                  exit_at="wm-release-before-resume",
                  wait_for=h.gate_wait("lifetime_hold", tag="A"))
    proc_a = h.spawn(a)
    h.wait_reached("enter_registered", timeout=60, tag="A")
    view_a = h.lease_view()
    checks.append(h.check("A opened the cycle alone (generation 1)",
                          view_a["entries"] == [a["lease_id"]]
                          and view_a["generation"] == 1, json.dumps(view_a)))

    h.open_fence("lifetime_hold", tag="A")
    res_a = h.collect(proc_a, timeout=60)
    checks.append(h.check("A died in the obligation window (exit 90)",
                          res_a["returncode"] == 90, str(res_a["returncode"])))
    h.kill_declared("A")
    mid = h.lease_view()
    checks.append(h.check("obligation held by the dead owner A (the V4-a state)",
                          mid["entries"] == [] and mid["resume_required"] is True
                          and mid["owner_lease"] == a["lease_id"], json.dumps(mid)))
    checks.append(h.check("worker paused and nobody resumed yet (O-1 window)",
                          h.counts()["resume_calls"] == 0
                          and h.counts()["desired_state"] == "paused",
                          json.dumps(h.counts())))

    # The next participant inherits the obligation (ADR-10b) and opens its cycle.
    b = h.payload("B", request_budget=100.0)
    res_b = h.run(b)
    result_b = res_b["envelope"]["result"]
    checks.append(h.check("B closes the orphaned obligation on arrival",
                          "takeover_resumed" in result_b.get("actions", []),
                          json.dumps(result_b)))
    checks.append(h.check("B then owns a fresh paused cycle",
                          result_b["action"] == "paused_by_us"
                          and result_b["owner_lease"] == b["lease_id"], json.dumps(result_b)))
    checks.append(h.check("the pause was actually resumed (worker not left paused)",
                          h.counts()["resume_calls"] == 1
                          and h.counts()["desired_state"] == "paused", json.dumps(h.counts())))
    res_exit_b = h.run(h.payload("B-exit", phase="exit", lease_id=b["lease_id"]))
    checks.append(h.check("B's own cycle closes with the second resume",
                          h.counts()["resume_calls"] == 2, json.dumps(h.counts())))
    checks.append(h.check("state cleaned up", not h.lease_view()["exists"]
                          and not h.owner_exists(), json.dumps(h.lease_view())))
    return h.finish(checks, {"mid_state": mid})


def case_v4e(root, verbose=False):
    """Foreign owner: releasing must not claim it, nor resume it."""
    _clean(root, "V4-e")
    h = Harness("V4-e", root, verbose=verbose,
                worker_initial={"desired_state": "paused", "runtime_state": "stopped"})
    checks = []
    third = "third-party-owner-0001"
    mine = h.payload("M", request_budget=100.0)
    write_state(h, {
        "schema": SCHEMA, "generation": 1,
        "entries": [{"pid": os.getpid(), "boot_uuid": "x", "os_start_time": "",
                     "lease_id": mine["lease_id"], "invocations": 1}],
        "resume": {"required": False},
        "owner": {"lease_id": third, "generation": 1},
    })
    with open(h.owner_path, "w", encoding="utf-8") as handle:
        handle.write("filing-fetch")
    res = h.run(h.payload("M-exit", phase="exit", lease_id=mine["lease_id"]))
    result = res["envelope"]["result"]
    checks.append(h.check("release fails closed on foreign owner evidence",
                          result["action"] == "released_owner_changed", json.dumps(result)))
    checks.append(h.check("no resume was attempted for the foreign pause",
                          h.counts()["resume_calls"] == 0, json.dumps(h.counts())))
    checks.append(h.check("the foreign owner record was NOT rewritten",
                          h.lease_view()["owner_lease"] == third, json.dumps(h.lease_view())))
    checks.append(h.check("no obligation was invented for the foreign pause",
                          h.lease_view()["resume_required"] is False,
                          json.dumps(h.lease_view())))
    checks.append(h.check("worker still paused (we did not touch it)",
                          h.counts()["desired_state"] == "paused", json.dumps(h.counts())))
    return h.finish(checks)


def case_v4f(root, verbose=False):
    """Downstream of a foreign owner: a new participant must not resume it."""
    _clean(root, "V4-f")
    h = Harness("V4-f", root, verbose=verbose,
                worker_initial={"desired_state": "paused", "runtime_state": "stopped"})
    checks = []
    third = "third-party-owner-0001"
    write_state(h, {
        "schema": SCHEMA, "generation": 1, "entries": [],
        "resume": {"required": False},
        "owner": {"lease_id": third, "generation": 1},
    })
    with open(h.owner_path, "w", encoding="utf-8") as handle:
        handle.write("filing-fetch")
    before = open(h.refcount_path, encoding="utf-8").read()
    res = h.run(h.payload("N", request_budget=50.0,
                          status={"desired_state": "paused", "runtime_state": "stopped"}))
    result = res["envelope"]["result"]
    checks.append(h.check("the new participant fails closed on the foreign pause",
                          result["action"] == "owner_evidence_foreign", json.dumps(result)))
    checks.append(h.check("no resume of the foreign pause",
                          h.counts()["resume_calls"] == 0, json.dumps(h.counts())))
    checks.append(h.check("no pause either (we never took the cycle over)",
                          h.counts()["pause_calls"] == 0, json.dumps(h.counts())))
    checks.append(h.check("no write: the state file is byte-identical",
                          open(h.refcount_path, encoding="utf-8").read() == before,
                          "sha-compare in the journal below"))
    checks.append(h.check("owner marker untouched", h.owner_exists()))
    return h.finish(checks)


def case_w7(root, verbose=False):
    """ADR-5 W7/T10: the owner evidence changes while WE are the last releaser.

    Schedule: A and B both run as LIFETIME participants (so both leases are alive
    while the schedule says so).  A releases first (B still holds a lease, so A is
    not the last one and must not resume).  B is then the last releaser; while B
    sits inside its release critical section an external actor rewrites the owner
    record, so B must fail closed: no resume, no ownership claim, evidence intact.
    """
    _clean(root, "F-W7")
    h = Harness("F-W7", root, verbose=verbose)
    checks = []
    a = h.payload("A", request_budget=100.0, lifetime=True,
                  wait_for=h.gate_wait("lifetime_hold", tag="A"))
    proc_a = h.spawn(a)
    h.wait_reached("enter_registered", timeout=60, tag="A")
    b = h.payload("B", request_budget=100.0, lifetime=True,
                  wait_for={**h.gate_wait("lifetime_hold", tag="B"),
                            **h.gate_wait("release_before_decision", tag="B")})
    proc_b = h.spawn(b)
    h.wait_reached("enter_registered", timeout=60, tag="B")
    view = h.lease_view()
    checks.append(h.check("both leases alive, A owns the cycle",
                          sorted(view["entries"]) == sorted([a["lease_id"], b["lease_id"]])
                          and view["owner_lease"] == a["lease_id"], json.dumps(view)))

    h.open_fence("lifetime_hold", tag="A")
    res_a = h.collect(proc_a, timeout=60)
    checks.append(h.check("A's release only removes A's lease (B still active)",
                          res_a["envelope"]["exit"]["action"] == "released_joined",
                          json.dumps(res_a["envelope"]["exit"])))
    checks.append(h.check("no resume while another lease is still held",
                          h.counts()["resume_calls"] == 0, json.dumps(h.counts())))

    h.open_fence("lifetime_hold", tag="B")
    h.wait_reached("release_before_decision", timeout=60, tag="B")
    state = json.loads(open(h.refcount_path, encoding="utf-8").read())
    state["owner"] = {"lease_id": "external-owner-0007", "generation": state["generation"]}
    write_state(h, state)
    h.open_fence("release_before_decision", tag="B")
    res_b = h.collect(proc_b, timeout=60)
    result = res_b["envelope"]["exit"]
    checks.append(h.check("the changed owner is detected",
                          result["action"] == "released_owner_changed", json.dumps(result)))
    checks.append(h.check("no resume on changed ownership",
                          h.counts()["resume_calls"] == 0, json.dumps(h.counts())))
    checks.append(h.check("owner evidence preserved",
                          h.lease_view()["owner_lease"] == "external-owner-0007",
                          json.dumps(h.lease_view())))
    checks.append(h.check("no obligation was invented for the foreign owner",
                          h.lease_view()["resume_required"] is False,
                          json.dumps(h.lease_view())))
    checks.append(h.check("worker only touched by the cycles we own",
                          h.counts()["desired_state"] == "paused", json.dumps(h.counts())))
    return h.finish(checks)


def case_l2c_dead(root, verbose=False):
    """Dead lease + no marker + non-empty entries is TOOL evidence (F-I04C-06)."""
    _clean(root, "F-L2c-dead")
    h = Harness("F-L2c-dead", root, verbose=verbose,
                worker_initial={"desired_state": "paused", "runtime_state": "running"})
    checks = []
    write_state(h, {
        "schema": SCHEMA, "generation": 1,
        "entries": [{"pid": 9102, "boot_uuid": "x", "os_start_time": "",
                     "lease_id": "dead-lease-0002", "invocations": 1}],
        "resume": {"required": False},
        "owner": {"lease_id": "dead-lease-0002", "generation": 1},
    })
    res = h.run(h.payload("B", request_budget=100.0,
                          probe={"9102": {"alive": False}},
                          status={"desired_state": "paused", "runtime_state": "running"}))
    result = res["envelope"]["result"]
    checks.append(h.check("a provably dead lease is NOT read as a user pause",
                          result["action"] != "respect_paused", json.dumps(result)))
    checks.append(h.check("the dead cycle is closed and re-opened by us",
                          result["action"] == "paused_by_us"
                          and "takeover_resumed" in result.get("actions", []),
                          json.dumps(result)))
    checks.append(h.check("its dangling pause was resumed exactly once",
                          h.counts()["resume_calls"] == 1, json.dumps(h.counts())))
    checks.append(h.check("we now own the cycle",
                          h.lease_view()["owner_lease"] == res["envelope"]["lease_id"],
                          json.dumps(h.lease_view())))
    checks.append(h.check("the dead lease is gone from the refcount",
                          "dead-lease-0002" not in h.lease_view()["entries"],
                          json.dumps(h.lease_view())))
    return h.finish(checks)


def _l2e(root, mode, tag, stale):
    """Shared schedule: B is held at the pre-lock point while A completes its pause."""
    h = Harness(tag, root)
    checks = []
    b = h.payload("B", request_budget=100.0, mode=mode)
    if stale:
        # the stale variant waits right after its pre-lock status read
        b["wait_for"] = h.gate_wait("stale_prelock_read", tag="B")
    proc_b = h.spawn(b)
    if stale:
        h.wait_reached("stale_prelock_read", timeout=30, tag="B")
    # Now A really pauses the worker while B is parked before/at the lock.
    a = h.payload("A", request_budget=100.0)
    h.run(a)
    if stale:
        h.open_fence("stale_prelock_read", tag="B")
    res_b = h.collect(proc_b, timeout=60)
    return h, checks, a, b, res_b


def case_l2e_stale(root, verbose=False):
    """F-I04C-07 RED: the v1 shape (status read before the lock) pauses twice."""
    _clean(root, "F-L2e-stale")
    h, checks, a, b, res_b = _l2e(root, "protocol_stale_v1", "F-L2e-stale", stale=True)
    result = res_b["envelope"]["result"]
    counts = h.counts()
    checks.append(h.check("the stale snapshot says enabled/running at the pre-lock read",
                          result.get("prelock_status", {}).get("desired_state") == "enabled",
                          json.dumps(result)))
    checks.append(h.check("RED: acting on the stale snapshot pauses the worker AGAIN",
                          counts["pause_calls"] == 2, json.dumps(counts)))
    checks.append(h.check("RED: the second participant does not join the live cycle",
                          result["action"] == "paused_by_us", json.dumps(result)))
    return h.finish(checks, {"stale_result": result})


def case_l2e_fixed(root, verbose=False):
    """F-I04C-07 GREEN: the same schedule under the frozen single-critical-section
    path reads the status inside the lock and joins (exactly one pause)."""
    _clean(root, "F-L2e-fixed")
    h = Harness("F-L2e-fixed", root)
    checks = []
    # Same interleaving as the RED case: A pauses and then parks INSIDE its scope
    # (holding the lock is not needed -- what matters is that the pause already
    # happened when B reads the status).  B is started afterwards.
    a = h.payload("A", request_budget=100.0, lifetime=True,
                  wait_for=h.gate_wait("lifetime_hold", tag="A"))
    proc_a = h.spawn(a)
    h.wait_reached("enter_registered", timeout=60, tag="A")
    b = h.payload("B", request_budget=100.0, lifetime=True,
                  wait_for=h.gate_wait("lifetime_hold", tag="B"))
    proc_b = h.spawn(b)
    h.wait_reached("enter_registered", timeout=60, tag="B")
    view = h.lease_view()
    checks.append(h.check("B joined the live cycle instead of pausing again",
                          sorted(view["entries"]) == sorted([a["lease_id"], b["lease_id"]]),
                          json.dumps(view)))
    checks.append(h.check("exactly one pause for the whole schedule",
                          h.counts()["pause_calls"] == 1, json.dumps(h.counts())))
    h.open_fence("lifetime_hold", tag="B")
    h.open_fence("lifetime_hold", tag="A")
    res_a = h.collect(proc_a, timeout=60)
    res_b = h.collect(proc_b, timeout=60)
    checks.append(h.check("B read the status INSIDE the lock (paused, not enabled)",
                          res_b["envelope"]["result"]["lock_status"]["desired_state"]
                          == "paused",
                          json.dumps(res_b["envelope"]["result"].get("lock_status"))))
    checks.append(h.check("both participants returned cleanly",
                          res_a["returncode"] == 0 and res_b["returncode"] == 0,
                          json.dumps([res_a["returncode"], res_b["returncode"]])))
    checks.append(h.check("exactly one resume, state cleaned",
                          h.counts()["resume_calls"] == 1 and not h.lease_view()["exists"],
                          json.dumps(h.counts())))
    checks.append(h.check("no gate timeouts",
                          not h.journal_events("gate_timeout"),
                          json.dumps(h.journal_events("gate_timeout"))))
    return h.finish(checks)


def case_generation(root, verbose=False):
    """F-I04C-03: the generation is per-file, not global (documented, tested)."""
    _clean(root, "F-GEN")
    h = Harness("F-GEN", root, verbose=verbose)
    checks = []
    a = h.payload("A", phase="enter", request_budget=100.0)
    h.run(a)
    first = h.lease_view()
    checks.append(h.check("first cycle is generation 1", first["generation"] == 1,
                          json.dumps(first)))
    h.run(h.payload("A-exit", phase="exit", lease_id=a["lease_id"]))
    checks.append(h.check("cycle closed: the refcount file is gone",
                          not h.lease_view()["exists"], json.dumps(h.lease_view())))
    b = h.payload("B", phase="enter", request_budget=100.0)
    h.run(b)
    second = h.lease_view()
    checks.append(h.check("a NEW file restarts at generation 1 (NOT monotonic across files)",
                          second["generation"] == 1, json.dumps(second)))
    h.run(h.payload("B-exit", phase="exit", lease_id=b["lease_id"]))
    checks.append(h.check("state cleaned again", not h.lease_view()["exists"],
                          json.dumps(h.lease_view())))
    return h.finish(checks, {"documented_rule": "decision.md ADR-12"})


CASES = {
    "V4-a": case_v4a,
    "V4-e": case_v4e,
    "V4-f": case_v4f,
    "F-W7": case_w7,
    "F-L2c-dead": case_l2c_dead,
    "F-L2e-stale": case_l2e_stale,
    "F-L2e-fixed": case_l2e_fixed,
    "F-GEN": case_generation,
}
