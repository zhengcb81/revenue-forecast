"""One simulated filing-fetch participant (a real OS process).

The payload arrives in the FILING_FETCH_SIM_PAYLOAD environment variable as
base64(JSON), so no company/path text ever rides on a shell command line.

Envelope protocol: every phase prints exactly one line ``ENVELOPE <json>`` on
stdout when it completes cleanly.  A crash injection (os._exit in the kernel)
prints nothing, which is how the scheduler distinguishes "crashed" from
"returned".

Usage:  <python> sim/participant.py [--two-scopes] [--enter-only]
"""

from __future__ import annotations

import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import kernel  # noqa: E402


def emit(kind, payload):
    print(f"ENVELOPE {json.dumps({'kind': kind, **payload}, sort_keys=True)}")
    sys.stdout.flush()


def run_enter(payload, mode):
    """Dispatch the acquire path for the requested mode (r2)."""
    if mode == "protocol_stale_v1":
        return kernel.run_protocol_stale_v1(payload)
    if mode == "protocol":
        return kernel.run_protocol(payload)
    return kernel.run_legacy(payload)


def run_release(payload, mode):
    if mode in {"protocol", "protocol_stale_v1"}:
        return kernel.run_protocol_exit(payload)
    return kernel.run_legacy_exit(payload)


def lease_variants(base):
    return [f"{base}-1", f"{base}-2"]


def run_two_scopes(payload, mode):
    scopes = []
    base = payload["lease_id"]
    variants = lease_variants(base)
    enters = []
    for index, lease_id in enumerate(variants, start=1):
        scoped = dict(payload)
        scoped["lease_id"] = lease_id
        scoped["invocations"] = index
        scoped["phase"] = "enter"
        scoped["mode"] = mode
        enters.append(run_enter(scoped, mode))
    if payload.get("stop_after_enter"):
        emit("two-scopes", {"enters": enters, "exits": []})
        return 0
    exits = []
    for index, lease_id in enumerate(variants, start=1):
        scoped = dict(payload)
        scoped["lease_id"] = lease_id
        scoped["invocations"] = index
        scoped["phase"] = "exit"
        scoped["mode"] = mode
        exits.append(run_release(scoped, mode))
        if payload.get("stop_after_first_exit"):
            break
    scopes.append({"lease_ids": variants})
    emit("two-scopes", {"enters": enters, "exits": exits, "scopes": scopes})
    return 0


def publish_alive(payload, alive):
    """Publish this invocation's liveness for the injected probe model.

    The file is keyed by pid + holder (the lease) + tag and is REMOVED on a clean
    return, so a crashed invocation (os._exit) leaves it behind.  The holder is
    alive while any of its invocations is still running -- which is how the test
    models "the lease stays valid until the scheduler runs the release step".
    """
    base = payload["base"]
    holder = payload.get("holder") or payload["lease_id"]
    path = os.path.join(base, f"alive.{os.getpid()}.{holder}.{payload['tag']}.json")
    if alive:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"pid": os.getpid(), "holder": holder, "tag": payload["tag"],
                       "alive": True}, handle)
        return
    try:
        os.unlink(path)
    except OSError:
        pass


def run_lifetime(payload, mode):
    """One participant = ONE process: enter, hold at the `lifetime_hold` gate,
    then run its own release.  This is the shape the production call site has
    (the scope wraps the download inside a single invocation), and it makes the
    injected liveness model exact: the alive file exists exactly while the
    participant is in its scope.
    """
    entered = run_enter(payload, mode)
    kernel.gate(payload, "lifetime_hold")
    kernel.maybe_exit_at(payload, "lifetime_crash")
    exit_payload = dict(payload)
    exit_payload["phase"] = "exit"
    released = run_release(exit_payload, mode)
    emit("lifetime", {"result": entered, "exit": released, "lease_id": payload["lease_id"]})
    return 0


def main(argv):
    raw = os.environ.get("FILING_FETCH_SIM_PAYLOAD")
    if not raw:
        print("missing FILING_FETCH_SIM_PAYLOAD", file=sys.stderr)
        return 2
    payload = json.loads(base64.b64decode(raw).decode("utf-8"))
    mode = payload.get("mode", "protocol")
    os.makedirs(payload["base"], exist_ok=True)
    publish_alive(payload, True)
    try:
        if payload.get("lifetime"):
            return run_lifetime(payload, mode)
        if "--two-scopes" in argv:
            return run_two_scopes(payload, mode)
        phase = payload.get("phase", "enter")
        if phase == "enter":
            result = run_enter(payload, mode)
        else:
            result = run_release(payload, mode)
        emit(phase, {"result": result, "lease_id": payload["lease_id"]})
        return 0
    finally:
        publish_alive(payload, False)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
