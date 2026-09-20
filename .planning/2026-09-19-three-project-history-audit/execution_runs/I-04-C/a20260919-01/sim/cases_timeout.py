"""r3 cases: the LOCK TIMEOUT boundary (reviewer's still-required item 1 and 2).

  F-T1   request-phase real timeout: an external process really holds the lease
         lock; the participant's lock budget is 0.05 s, so it must fail closed with
         code/action `lease_lock_timeout`, zero writes, zero CLI calls, and the
         state file must be byte-identical.
  F-T2   request-phase budget 0: no wait at all is attempted (I-04-A D3: a passed
         deadline gives no budget), same fail-closed outcome.
  F-T3   cleanup-phase real timeout: the participant already owns a paused cycle;
         while it is parked inside its release critical section an external holder
         takes the lock, so the CLEANUP budget also expires and the envelope must
         report `cleanup_status=failed:lease_lock_timeout` while keeping the
         obligation and the owner evidence.
  F-T4   queue crosses the budget: N participants contend with an injected
         critical-section hold time H; the queueing ones (wait ~ (N-1)*H) exceed
         their lock budget and fail closed with `lease_lock_timeout` and zero
         writes, while the winners still register and the terminal state is
         consistent.  The case ALSO reports how much of each participant's request
         budget was consumed by queueing (the ADR-2 cost the reviewer asked for).
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from harness import LOCK, PYTHON, Harness, b64  # noqa: E402

HOLD_LOCK = os.path.join(HERE, "hold_lock.py")


def _clean(root, case):
    shutil.rmtree(os.path.join(root, case), ignore_errors=True)


def _start_holder(harness, seconds):
    payload = {"base": harness.base, "name": LOCK}
    proc = subprocess.Popen(
        [PYTHON, "-B", HOLD_LOCK, b64(payload), str(seconds)],
        cwd=harness.base,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )
    ready = os.path.join(harness.base, "_external_holder.ready")
    deadline = time.monotonic() + 20
    while not os.path.exists(ready):
        if time.monotonic() > deadline:
            proc.kill()
            raise AssertionError("external lock holder never became ready")
        time.sleep(0.01)
    return proc


def case_f_t1(root, verbose=False):
    """Request-phase lock timeout, with the lock really held by another process."""
    _clean(root, "F-T1")
    h = Harness("F-T1", root, verbose=verbose)
    checks = []
    holder = _start_holder(h, 2.5)
    try:
        before = open(h.refcount_path, "rb").read() if os.path.exists(h.refcount_path) else b""
        started = time.monotonic()
        res = h.run(h.payload("A", request_budget=0.05))
        elapsed = round(time.monotonic() - started, 3)
        result = res["envelope"]["result"]
        checks.append(h.check("the documented code appears: lease_lock_timeout",
                              result["code"] == "lease_lock_timeout", json.dumps(result)))
        checks.append(h.check("the request-phase action is the fail-closed timeout",
                              result["action"] == "lease_lock_timeout", json.dumps(result)),
                      )
        checks.append(h.check("zero writes", result["writes"] == 0, json.dumps(result)))
        checks.append(h.check("zero CLI calls (no pause, no resume)",
                              h.counts()["pause_calls"] == 0
                              and h.counts()["resume_calls"] == 0, json.dumps(h.counts())))
        after = open(h.refcount_path, "rb").read() if os.path.exists(h.refcount_path) else b""
        checks.append(h.check("the lease state file is byte-identical",
                              before == after, f"{len(before)} -> {len(after)} bytes"))
        checks.append(h.check("the wait was bounded by the injected budget (0.05 s + slack)",
                              elapsed < 1.0, f"elapsed={elapsed}s"))
        checks.append(h.check("the timeout is journalled with its code",
                              any(e.get("event") == "lock_timeout"
                                  and e.get("code") == "lease_lock_timeout"
                                  for e in h.journal_events()),
                              json.dumps(h.journal_events("lock_timeout"))))
    finally:
        holder.wait(timeout=30)
    return h.finish(checks)


def case_f_t2(root, verbose=False):
    """Budget 0 (deadline already passed): the lock must not even be attempted."""
    _clean(root, "F-T2")
    h = Harness("F-T2", root, verbose=verbose)
    checks = []
    holder = _start_holder(h, 1.5)
    try:
        res = h.run(h.payload("A", request_budget=0.0))
        result = res["envelope"]["result"]
        checks.append(h.check("no budget => fail closed with lease_lock_timeout",
                              result["code"] == "lease_lock_timeout", json.dumps(result)))
        checks.append(h.check("zero writes and zero CLI",
                              result["writes"] == 0 and h.counts()["pause_calls"] == 0
                              and h.counts()["resume_calls"] == 0,
                              json.dumps({"result": result, "counts": h.counts()})))
        checks.append(h.check("no lock was actually taken (no lock_acq journal entry)",
                              not any(e.get("event") == "lock_acq" for e in h.journal_events()),
                              json.dumps(h.journal_events())))
    finally:
        holder.wait(timeout=30)
    return h.finish(checks)


def case_f_t3(root, verbose=False):
    """Cleanup-phase lock timeout while the request itself already succeeded."""
    _clean(root, "F-T3")
    h = Harness("F-T3", root, verbose=verbose)
    checks = []
    a = h.payload("A", request_budget=60.0, cleanup_budget=0.3, lifetime=True,
                  wait_for=h.gate_wait("lifetime_hold", tag="A"))
    proc_a = h.spawn(a)
    h.wait_reached("enter_registered", timeout=60, tag="A")
    checks.append(h.check("A owns a paused cycle before the cleanup problem",
                          h.counts()["pause_calls"] == 1, json.dumps(h.counts())))

    # Deterministic order: the lock is taken EXTERNALLY first, and only then is A
    # released into its cleanup critical section.
    holder = _start_holder(h, 2.5)
    try:
        h.open_fence("lifetime_hold", tag="A")
        res = h.collect(proc_a, timeout=60)
        released = res["envelope"]["exit"]
        checks.append(h.check("the request result is untouched by the cleanup problem",
                              res["envelope"]["result"]["action"] == "paused_by_us",
                              json.dumps(res["envelope"]["result"])))
        checks.append(h.check("cleanup reports the lock timeout with its code",
                              released["cleanup_status"]
                              == "failed:lease_lock_timeout", json.dumps(released)))
        checks.append(h.check("the release action is the fail-closed one",
                              released["action"] == "release_fail_closed", json.dumps(released)))
        checks.append(h.check("the obligation and the owner evidence are preserved "
                              "(no false 'restored')",
                              h.lease_view()["exists"] and h.owner_exists(),
                              json.dumps(h.lease_view())))
        checks.append(h.check("the worker is still paused (we never claimed to resume)",
                              h.counts()["desired_state"] == "paused", json.dumps(h.counts())))
    finally:
        holder.wait(timeout=30)
    return h.finish(checks, {
        "note": "cleanup uses lock_budget_for(cleanup_budget)=min(0.3,60); the timeout is "
                "therefore the cleanup-phase analogue of F-T1",
    })


def case_f_t4(root, verbose=False):
    """The queue crosses the lock budget: late participants fail closed."""
    _clean(root, "F-T4")
    h = Harness("F-T4", root, verbose=verbose)
    checks = []
    # 6 participants, each holding the critical section for H=0.4 s of injected pause
    # cost, with a lock budget of 1.0 s: the queue is ~(N-1)*H = 2.0 s, so the
    # participants beyond the first few cannot acquire in time.
    tags = [f"P{i}" for i in range(6)]
    hold = 0.4
    budget = 1.0
    payloads = {}
    procs = []
    for tag in tags:
        # enter-only: one critical section per participant, no hold gate to wait on
        payload = h.payload(tag, phase="enter", request_budget=budget,
                            pause_hold_seconds=hold)
        payloads[tag] = payload
        procs.append((tag, h.spawn(payload)))
    results = [(tag, h.collect(proc, timeout=120)) for tag, proc in procs]
    envelopes = {tag: res["envelope"]["result"] for tag, res in results}
    timed_out = [tag for tag in tags
                 if envelopes[tag].get("code") == "lease_lock_timeout"]
    succeeded = [tag for tag in tags if tag not in timed_out]
    winners = [tag for tag in succeeded if envelopes[tag]["action"] == "paused_by_us"]
    joiners = [tag for tag in succeeded if envelopes[tag]["action"] == "joined"]
    checks.append(h.check("the queue really crossed the budget: at least one participant "
                          "failed closed with lease_lock_timeout",
                          len(timed_out) >= 1, json.dumps(envelopes)))
    checks.append(h.check("every timed-out participant wrote nothing",
                          all(envelopes[tag]["writes"] == 0 for tag in timed_out),
                          json.dumps({t: envelopes[t]["writes"] for t in timed_out})))
    checks.append(h.check("at least one participant opened or took over the cycle "
                          "(enter-only winners exit, so a later participant may "
                          "legitimately reclaim the dead cycle)",
                          len(winners) >= 1,
                          json.dumps({t: envelopes[t]["action"] for t in tags})))
    checks.append(h.check("the winners plus joiners are exactly the non-timed-out ones",
                          set(winners) | set(joiners) == set(succeeded)
                          and not (set(winners) & set(joiners)),
                          json.dumps({t: envelopes[t]["action"] for t in tags})))
    view = h.lease_view()
    successful_ids = {payloads[tag]["lease_id"] for tag in succeeded}
    timed_out_ids = {payloads[tag]["lease_id"] for tag in timed_out}
    # r5 E2: the two conjuncts below are explicit universal quantifiers over the
    # refcount view.  The previous sub-clause `not any(lease in successful_ids is
    # False ...)` was a CHAINED COMPARISON in Python -- it evaluates as
    # `(lease in successful_ids) and (successful_ids is False)`, never True, so the
    # `not any(...)` was vacuously True and could never fail (the closeout review
    # found it).  A timed-out lease entering the refcount must turn this red.
    checks.append(h.check("no timed-out participant ever appears in the refcount",
                          all(lease in successful_ids for lease in view["entries"])
                          and all(lease not in timed_out_ids for lease in view["entries"])
                          and view["entries"] != [],
                          json.dumps({"view": view, "succeeded": succeeded,
                                      "timed_out": timed_out})))
    wait_seconds = {tag: round(envelopes[tag].get("lock_wait") or 0.0, 3) for tag in succeeded}
    # r5 E2: this used to assert a literal `True` (a recorder, not an assertion).
    # Now it asserts the reporter really emitted `lock_wait` for every successful
    # participant and that the reported wait is a real number inside the lock
    # budget (1 ms allowance = the reporting resolution).  A missing field or an
    # out-of-budget number turns it red.
    checks.append(h.check("the queue wait is reported (the download budget it consumed)",
                          all(envelopes[tag].get("lock_wait") is not None for tag in succeeded)
                          and all(0.0 <= value <= budget + 0.001
                                  for value in wait_seconds.values()),
                          json.dumps({"holds_seconds": hold, "budget": budget,
                                      "waited_seconds": wait_seconds,
                                      "timed_out": timed_out})))
    checks.append(h.check("no gate timeouts",
                          not h.journal_events("gate_timeout"),
                          json.dumps(h.journal_events("gate_timeout"))))
    # release the successful participants (reverse order) so the case ends clean
    for tag in reversed(succeeded):
        h.run(h.payload(f"{tag}-exit", phase="exit", lease_id=payloads[tag]["lease_id"]))
    final = h.lease_view()
    checks.append(h.check("no lease and no obligation is left dangling after the "
                          "successful releases",
                          final.get("entries", []) == []
                          and final.get("resume_required") is False,
                          json.dumps(final)))
    return h.finish(checks, {
        "timed_out": timed_out,
        "queue_and_hold_model": "queue_wait ~ (N-1) * H; with the lock budget capped at "
                                "LOCK_MAX_SECONDS, N*H > cap makes the tail fail closed",
        "budget_consumed_by_queueing": wait_seconds,
    })


CASES = {
    "F-T1": case_f_t1,
    "F-T2": case_f_t2,
    "F-T3": case_f_t3,
    "F-T4": case_f_t4,
}
