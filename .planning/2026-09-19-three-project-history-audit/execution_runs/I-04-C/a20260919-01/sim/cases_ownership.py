"""I-04-C ownership / crash-window / fail-closed cases (F-L4*, F-W*)."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from harness import Harness, banner, sha256_file  # noqa: E402

SCHEMA = "filing-fetch.pause-refcount/2"


def write_raw(harness, text):
    with open(harness.refcount_path, "w", encoding="utf-8") as handle:
        handle.write(text)


def write_state(harness, payload):
    write_raw(harness, json.dumps(payload, sort_keys=True))


def cycle(harness, tag_a="A", tag_b="B", a_overrides=None, b_overrides=None,
          wait_a=60.0, wait_b=60.0):
    """One two-participant cycle; returns the raw per-step records."""
    a = harness.payload(tag_a, phase="enter", request_budget=100.0, **(a_overrides or {}))
    res_a = harness.run(a, timeout=wait_a)
    b = harness.payload(tag_b, phase="enter", request_budget=100.0, **(b_overrides or {}))
    res_b = harness.run(b, timeout=wait_b)
    return a, res_a, b, res_b


def exit_of(harness, tag, lease_id, **overrides):
    payload = harness.payload(tag, phase="exit", lease_id=lease_id,
                              holder=lease_id, **overrides)
    return harness.run(payload)


# ---------------------------------------------------------------------------
# F-L4 family
# ---------------------------------------------------------------------------


def case_f_l4a(root, verbose=False):
    """F-L4a: the user pauses the worker DURING our scope.

    The card asks for this window (r2: the v1 case never produced a result because
    its victim payload was missing phase="exit" -- harness defect F-I04C-05).  What
    this case records is the measured, documented limitation: with the current
    company-wiki API the tool CANNOT tell "the user also pressed pause" from "our
    own cycle is still the pauser" (control.py only exposes desired_state), so the
    owner's release resumes and thereby undoes the user's pause.  The case asserts
    that measured behaviour and the recorded dependency; it does NOT claim the
    user's intent is protected.

    The protected variant -- where the pause is NOT attributable to us -- is
    F-W7 / V4-e / V4-f (owner evidence changed => fail closed, never resume).
    """
    h = Harness("F-L4a", root, verbose=verbose)
    checks = []
    a = h.payload("A", phase="enter", request_budget=100.0)
    res_a = h.run(a)
    checks.append(h.check("A opened the pause cycle alone",
                          res_a["envelope"]["result"]["action"] == "paused_by_us",
                          json.dumps(res_a["envelope"]["result"])))

    # the user presses pause while our scope is open (idempotent at the CLI level)
    external = h.worker("worker-pause", "user")
    checks.append(h.check("the external worker-pause succeeded (idempotent)",
                          external["returncode"] == 0, json.dumps(external)))
    checks.append(h.check("the API still reports the same state (no provenance)",
                          h.counts()["desired_state"] == "paused",
                          json.dumps(h.counts())))

    res_exit = h.run(h.payload("A-exit", phase="exit", lease_id=a["lease_id"]))
    result = res_exit["envelope"]["result"]
    checks.append(h.check("A's release resumes (owner_is_me): the user's pause is "
                          "indistinguishable and is undone",
                          result["action"] == "released_last"
                          and result.get("resume_reason") == "owner_is_me",
                          json.dumps(result)))
    checks.append(h.check("worker ends enabled (the documented limitation)",
                          h.counts()["desired_state"] == "enabled", json.dumps(h.counts())))
    checks.append(h.check("state cleaned up by our own cycle",
                          not h.lease_view()["exists"] and not h.owner_exists(),
                          json.dumps(h.lease_view())))
    return h.finish(checks, {
        "LIMITATION": "a user pause issued while a filing-fetch cycle is open is "
                      "resumed by that cycle's close; distinguishing it needs "
                      "pause-origin evidence from company-wiki (registered as O-2 "
                      "and as an I-04-D dependency in handoff.json)",
    })


def case_f_l4a_foreign(root, verbose=False):
    """F-L4a-foreign: the same window, but the owner evidence is a THIRD PARTY.

    Here the pause is demonstrably not ours, so the release must fail closed.
    """
    h = Harness("F-L4a-foreign", root, verbose=verbose)
    checks = []
    a = h.payload("A", phase="enter", request_budget=100.0)
    h.run(a)
    b_payload = h.payload("B", request_budget=100.0)
    h.run(b_payload)
    third = "third-party-owner-0001"
    victim = h.payload("B-exit", phase="exit", lease_id=b_payload["lease_id"],
                       wait_for=h.gate_wait("release_before_decision", tag="B-exit"))
    proc = h.spawn(victim)
    h.wait_reached("release_before_decision", timeout=60, tag="B-exit")
    state = json.loads(open(h.refcount_path, encoding="utf-8").read())
    state["owner"] = {"lease_id": third, "generation": state["generation"]}
    write_state(h, state)
    h.open_fence("release_before_decision", tag="B-exit")
    res = h.collect(proc)
    result = res["envelope"]["result"]
    checks.append(h.check("owner change detected",
                          result["action"] == "released_owner_changed", json.dumps(result)))
    checks.append(h.check("no resume on changed ownership", h.counts()["resume_calls"] == 0,
                          json.dumps(h.counts())))
    checks.append(h.check("cleanup_status records the reason",
                          str(result["cleanup_status"]).startswith(
                              "failed:owner_evidence_changed"),
                          json.dumps(result)))
    after = h.lease_view()
    checks.append(h.check("evidence preserved (state file kept, our lease gone)",
                          after["exists"] and b_payload["lease_id"] not in after["entries"]
                          and third == after["owner_lease"], json.dumps(after)))
    checks.append(h.check("owner marker still present", h.owner_exists()))
    return h.finish(checks)


def case_f_l4b(root, verbose=False):
    """Truncated JSON: fail closed, never treat as an empty list."""
    h = Harness("F-L4b", root, verbose=verbose)
    checks = []
    write_raw(h, '{"schema": "' + SCHEMA + '", "entries": [')
    before = sha256_file(h.refcount_path)
    res = h.run(h.payload("A", request_budget=50.0))
    checks.append(h.check("enter fails closed",
                          res["envelope"]["result"]["action"] == "lease_state_corrupt",
                          json.dumps(res["envelope"]["result"])))
    checks.append(h.check("corrupt bytes untouched", sha256_file(h.refcount_path) == before,
                          before))
    checks.append(h.check("no worker action",
                          h.counts()["pause_calls"] == 0 and h.counts()["resume_calls"] == 0,
                          json.dumps(h.counts())))
    res_exit = exit_of(h, "A-exit", h.payload("A")["lease_id"])
    checks.append(h.check("release also fails closed",
                          res_exit["envelope"]["result"]["action"] == "release_fail_closed",
                          json.dumps(res_exit["envelope"]["result"])))
    checks.append(h.check("no resume from the release path",
                          h.counts()["resume_calls"] == 0, json.dumps(h.counts())))
    return h.finish(checks)


def case_f_l4c(root, verbose=False):
    """Legacy list format: fail closed (no generation/incarnation evidence)."""
    h = Harness("F-L4c", root, verbose=verbose)
    checks = []
    write_state_raw = '[{"pid": 9003, "joined": false}]'
    write_raw(h, write_state_raw)
    res = h.run(h.payload("A", request_budget=50.0))
    checks.append(h.check("legacy format refused",
                          res["envelope"]["result"]["action"] == "lease_state_legacy",
                          json.dumps(res["envelope"]["result"])))
    checks.append(h.check("legacy bytes untouched",
                          open(h.refcount_path, encoding="utf-8").read() == write_state_raw))
    checks.append(h.check("no worker action",
                          h.counts()["pause_calls"] == 0 and h.counts()["resume_calls"] == 0,
                          json.dumps(h.counts())))
    return h.finish(checks)


def case_f_l4d(root, verbose=False):
    """F-L4d: the resume itself fails -> keep the obligation, never claim restored.

    r2 schedule: A is the only participant of its cycle, so its release really does
    reach the resume step; the resume is injected to fail.  A later participant must
    then inherit the obligation and finish the recovery.
    """
    h = Harness("F-L4d", root, verbose=verbose)
    checks = []
    a = h.payload("A", phase="enter", request_budget=100.0)
    res_a = h.run(a)
    checks.append(h.check("A opened the cycle alone",
                          res_a["envelope"]["result"]["action"] == "paused_by_us",
                          json.dumps(res_a["envelope"]["result"])))

    exit_a = h.payload("A-exit", phase="exit", lease_id=a["lease_id"],
                       resume_error={"error": "injected resume failure"})
    res = h.run(exit_a)
    result = res["envelope"]["result"]
    checks.append(h.check("resume failure reported",
                          result["action"] == "released_last_resume_failed",
                          json.dumps(result)))
    checks.append(h.check("cleanup_status names the failure",
                          result["cleanup_status"] == "failed:resume_failed",
                          json.dumps(result)))
    checks.append(h.check("the resume attempt is still recorded",
                          result.get("attempted_resumes") == 1,
                          json.dumps(result)))
    view = h.lease_view()
    checks.append(h.check("resume obligation kept", view["resume_required"] is True,
                          json.dumps(view)))
    checks.append(h.check("owner marker kept (recoverable diagnosis)", h.owner_exists()))
    checks.append(h.check("state file kept", view["exists"], json.dumps(view)))
    checks.append(h.check("worker still paused (not falsely restored)",
                          h.counts()["desired_state"] == "paused", json.dumps(h.counts())))

    # takeover: a later participant owns and actually performs the resume
    c = h.payload("C", request_budget=100.0)
    res_c = h.run(c)
    takeover_c = res_c["envelope"]["result"]
    checks.append(h.check("takeover resumed the orphaned pause",
                          "takeover_resumed" in takeover_c.get("actions", [])
                          or takeover_c["action"] == "takeover_resumed",
                          json.dumps(takeover_c)))
    checks.append(h.check("takeover did the resume", h.counts()["resume_calls"] == 1,
                          json.dumps(h.counts())))
    res_exit_c = exit_of(h, "C-exit", c["lease_id"])
    checks.append(h.check("second resume only from the last releaser",
                          h.counts()["resume_calls"] == 2, json.dumps(h.counts())))
    checks.append(h.check("state cleaned after the successful cycle",
                          not h.lease_view()["exists"] and not h.owner_exists(),
                          json.dumps(h.lease_view())))
    return h.finish(checks, {"intermediate_state": view})


def case_f_l4e(root, verbose=False):
    """Entry-level corruption (missing lease_id) is corruption, not an empty list."""
    h = Harness("F-L4e", root, verbose=verbose)
    checks = []
    write_state(h, {"schema": SCHEMA, "generation": 1, "entries": [{"pid": 1234}],
                    "resume": {"required": False}, "owner": {}})
    res = h.run(h.payload("A", request_budget=50.0))
    checks.append(h.check("entry-level corruption fails closed",
                          res["envelope"]["result"]["action"] == "lease_state_corrupt",
                          json.dumps(res["envelope"]["result"])))
    checks.append(h.check("no worker action",
                          h.counts()["pause_calls"] == 0 and h.counts()["resume_calls"] == 0,
                          json.dumps(h.counts())))
    return h.finish(checks)


# ---------------------------------------------------------------------------
# crash windows
# ---------------------------------------------------------------------------


def case_f_w1(root, verbose=False):
    """W1: the participant dies between the refcount write and the owner marker.

    The crash point is the real injection inside the fresh-cycle critical section
    (``after-refcount-before-owner``), so the surviving state really is "lease
    present, owner marker absent, worker still running".  The next participant must
    NOT read that missing marker as a user pause: it reclaims the dead lease, sees
    the worker is running (nothing to resume), and opens exactly one cycle.
    """
    h = Harness("F-W1", root, verbose=verbose)
    checks = []
    a = h.payload("A", phase="enter", request_budget=100.0,
                  exit_at="after-refcount-before-owner")
    res_a = h.run(a)
    checks.append(h.check("A crashed with the exit code we injected",
                          res_a["returncode"] == 90, str(res_a["returncode"])))
    checks.append(h.check("the crashed invocation's liveness record is dropped",
                          bool(h.kill_declared("A"))))
    view = h.lease_view()
    checks.append(h.check("the W1 window: lease durable, owner marker absent",
                          view["entries"] == [a["lease_id"]] and not h.owner_exists(),
                          json.dumps(view) + f" owner={h.owner_exists()}"))
    checks.append(h.check("worker still running (the pause never happened)",
                          h.counts()["desired_state"] == "enabled", json.dumps(h.counts())))

    b = h.payload("B", phase="enter", request_budget=100.0)
    res_b = h.run(b)
    result = res_b["envelope"]["result"]
    checks.append(h.check("B does NOT mistake the missing owner for a user pause",
                          result["action"] == "paused_by_us", json.dumps(result)))
    checks.append(h.check("B reclaims the dead lease and opens its own cycle",
                          "resume_skipped_worker_running" in result.get("actions", [])
                          or "takeover_resumed" in result.get("actions", []),
                          json.dumps(result)))
    after = h.lease_view()
    checks.append(h.check("A's dead lease is gone, B's is present",
                          b["lease_id"] in after.get("entries", [])
                          and a["lease_id"] not in after.get("entries", []),
                          json.dumps(after)))
    checks.append(h.check("only one pause reached the worker",
                          h.counts()["pause_calls"] == 1, json.dumps(h.counts())))
    checks.append(h.check("no resume was sent to a running worker",
                          h.counts()["resume_calls"] == 0, json.dumps(h.counts())))
    res_exit_b = exit_of(h, "B-exit", b["lease_id"])
    checks.append(h.check("B's release closes the cycle with one resume",
                          h.counts()["resume_calls"] == 1, json.dumps(h.counts())))
    checks.append(h.check("state cleaned", not h.lease_view()["exists"]
                          and not h.owner_exists(), json.dumps(h.lease_view())))
    return h.finish(checks)


def case_f_w2(root, verbose=False):
    """W3: paused and registered, then the only participant dies.

    The next participant sees paused + an owner marker + no surviving lease: it
    must take over and resume, never read that as a user pause.
    """
    h = Harness("F-W2", root, verbose=verbose)
    checks = []
    a = h.payload("A", phase="enter", request_budget=100.0,
                  exit_at="after-pause-confirm",
                  wait_for=h.gate_wait("enter_registered"))
    proc = h.spawn(a)
    h.wait_reached("enter_registered")
    h.open_fence("enter_registered")
    res_a = h.collect(proc)
    checks.append(h.check("A crashed after the pause", res_a["returncode"] == 90,
                          str(res_a["returncode"])))
    h.kill_declared("A")
    counts = h.counts()
    view = h.lease_view()
    checks.append(h.check("worker is paused with our lease still registered",
                          counts["desired_state"] == "paused" and
                          view["entries"] == [a["lease_id"]], json.dumps(counts) + json.dumps(view)))
    checks.append(h.check("owner marker present", h.owner_exists()))

    b = h.payload("B", phase="enter", request_budget=100.0)
    res_b = h.run(b)
    result = res_b["envelope"]["result"]
    checks.append(h.check("next participant takes the orphaned pause over and re-opens it",
                          result["action"] == "paused_by_us"
                          and "takeover_resumed" in result.get("actions", []),
                          json.dumps(result)))
    checks.append(h.check("the orphaned pause was resumed exactly once",
                          h.counts()["resume_calls"] == 1, json.dumps(h.counts())))
    checks.append(h.check("the orphaned cycle was closed and exactly one further "
                          "pause opened B's own cycle",
                          h.counts()["pause_calls"] == 2, json.dumps(h.counts())))
    res_exit_b = exit_of(h, "B-exit", b["lease_id"])
    checks.append(h.check("B's own cycle closes with the second resume",
                          h.counts()["resume_calls"] == 2, json.dumps(h.counts())))
    checks.append(h.check("state cleaned", not h.lease_view()["exists"]
                          and not h.owner_exists(), json.dumps(h.lease_view())))
    return h.finish(checks)


def case_f_w4(root, verbose=False):
    """W4: the LAST participant dies between the persisted obligation and the
    resume command.  The obligation must survive and be taken over later."""
    h = Harness("F-W4", root, verbose=verbose)
    checks = []
    a = h.payload("A", phase="enter", request_budget=100.0)
    h.run(a)
    exit_a = h.payload("A-exit", phase="exit", lease_id=a["lease_id"],
                       exit_at="wm-release-before-resume")
    res_a = h.run(exit_a)
    checks.append(h.check("A crashed before the resume", res_a["returncode"] == 90,
                          str(res_a["returncode"])))
    h.kill_declared("A-exit")
    h.kill_declared("A")
    view = h.lease_view()
    counts = h.counts()
    checks.append(h.check("empty refcount with the obligation persisted",
                          view["entries"] == [] and view["resume_required"] is True,
                          json.dumps(view)))
    checks.append(h.check("worker still paused (no false restore)",
                          counts["desired_state"] == "paused", json.dumps(counts)))
    checks.append(h.check("no resume happened", counts["resume_calls"] == 0, json.dumps(counts)))

    b = h.payload("B", phase="enter", request_budget=100.0)
    res_b = h.run(b)
    result = res_b["envelope"]["result"]
    checks.append(h.check("B takes over the orphaned resume",
                          "takeover_resumed" in result.get("actions", [])
                          or result["action"] == "takeover_resumed",
                          json.dumps(result)))
    checks.append(h.check("the orphaned resume ran once",
                          h.counts()["resume_calls"] == 1, json.dumps(h.counts())))
    exit_b = exit_of(h, "B-exit", b["lease_id"])
    checks.append(h.check("B's own cycle closes with the second resume",
                          h.counts()["resume_calls"] == 2, json.dumps(h.counts())))
    checks.append(h.check("state cleaned", not h.lease_view()["exists"]
                          and not h.owner_exists(), json.dumps(h.lease_view())))
    return h.finish(checks)


def case_f_w4b(root, verbose=False):
    """The handover race (card F-L1's 'last release vs new acquire'): the last
    releaser sits in its critical section with the obligation written and the
    resume still pending, while a new participant waits outside."""
    h = Harness("F-W4b", root, verbose=verbose)
    checks = []
    a = h.payload("A", phase="enter", request_budget=100.0)
    h.run(a)
    exit_a = h.payload("A-exit", phase="exit", lease_id=a["lease_id"],
                       wait_for=h.gate_wait("before_resume"))
    proc_a = h.spawn(exit_a)
    h.wait_reached("before_resume")
    view = h.lease_view()
    checks.append(h.check("the last releaser holds the lock with the obligation written",
                          view["entries"] == [] and view["resume_required"] is True,
                          json.dumps(view)))

    b = h.payload("B", phase="enter", request_budget=100.0)
    proc_b = h.spawn(b)
    time.sleep(0.5)
    checks.append(h.check("B is blocked outside the critical section",
                          h.envelope_of("B")["kind"] == "none",
                          "B envelope=" + h.envelope_of("B")["kind"]))
    h.open_fence("before_resume")
    res_exit_a = h.collect(proc_a)
    res_b = h.collect(proc_b)
    result_b = res_b["envelope"]["result"]
    checks.append(h.check("A resumed exactly once",
                          res_exit_a["envelope"]["result"]["action"] == "released_last",
                          json.dumps(res_exit_a["envelope"]["result"])))
    checks.append(h.check("B saw a clean empty state (no orphaned obligation) and "
                          "opened a NEW cycle instead of resuming again",
                          result_b["action"] == "paused_by_us"
                          and result_b.get("resume_calls") == 0
                          and result_b.get("generation") == 1, json.dumps(result_b)))
    checks.append(h.check("the new cycle starts at generation 1 again (ADR-12: the "
                          "counter is per file, not global)",
                          result_b.get("generation") == 1, json.dumps(result_b)))
    checks.append(h.check("one resume at the handover, one pause by B",
                          h.counts()["resume_calls"] == 1
                          and h.counts()["pause_calls"] == 2, json.dumps(h.counts())))
    exit_b = exit_of(h, "B-exit", b["lease_id"])
    checks.append(h.check("total resumes == pauses (2/2): no double resume",
                          h.counts()["resume_calls"] == 2
                          and h.counts()["pause_calls"] == 2, json.dumps(h.counts())))
    checks.append(h.check("state cleaned", not h.lease_view()["exists"]
                          and not h.owner_exists(), json.dumps(h.lease_view())))
    return h.finish(checks)


def case_f_w5(root, verbose=False):
    """Resume outlives the cleanup budget: request result is not rewritten."""
    h = Harness("F-W5", root, verbose=verbose)
    checks = []
    a = h.payload("A", phase="enter", request_budget=100.0)
    res_a = h.run(a)
    checks.append(h.check("request succeeded before the cleanup problem",
                          res_a["envelope"]["result"]["action"] == "paused_by_us",
                          json.dumps(res_a["envelope"]["result"])))
    exit_a = h.payload("A-exit", phase="exit", lease_id=a["lease_id"],
                       cleanup_budget=0.05, resume_delay=0.3, resume_budget=0.05)
    res = h.run(exit_a)
    result = res["envelope"]["result"]
    checks.append(h.check("resume reported as timed out",
                          result["cleanup_status"] == "failed:resume_timeout",
                          json.dumps(result)))
    checks.append(h.check("action names the failure",
                          result["action"] == "released_last_resume_failed", json.dumps(result)))
    view = h.lease_view()
    checks.append(h.check("obligation preserved for the next participant",
                          view["resume_required"] is True, json.dumps(view)))
    checks.append(h.check("no resume action reached the worker",
                          h.counts()["resume_calls"] == 0, json.dumps(h.counts())))
    checks.append(h.check("worker still paused", h.counts()["desired_state"] == "paused",
                          json.dumps(h.counts())))
    return h.finish(checks)


CASES = {
    "F-L4a": case_f_l4a,
    "F-L4b": case_f_l4b,
    "F-L4c": case_f_l4c,
    "F-L4d": case_f_l4d,
    "F-L4e": case_f_l4e,
    "F-W1": case_f_w1,
    "F-W2": case_f_w2,
    "F-W4": case_f_w4,
    "F-W4b": case_f_w4b,
    "F-W5": case_f_w5,
}
