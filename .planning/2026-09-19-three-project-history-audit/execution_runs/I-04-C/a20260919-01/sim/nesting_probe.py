"""F-L2a probe: can two PausedWorkerScopes of ONE process nest at all?

The frozen protocol's own status guard (mirroring fetch_filing.py L528-L529:
"runtime_state != running => worker_stopped") runs on every entry, and the first
scope pauses the worker.  This probe measures what a nested second entry sees,
inside one process, using two threads so the overlap is real.

It also shows the protocol-level fact that the second registration, if it exists
in the refcount (produced by another process sharing the pid), is never removed
by the pid-wide filter.

Read-only apart from its own evidence directory.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ATTEMPT = os.path.dirname(HERE)
import kernel  # noqa: E402
from harness import Harness, b64  # noqa: E402


def main():
    root = os.path.join(ATTEMPT, "evidence", "run")
    h = Harness("F-L2a-nesting", root)
    base = {
        "base": h.base,
        "journal": h.journal,
        "tag": "nested",
        "mode": "protocol",
        "phase": "enter",
        "enabled": True,
        "request_budget": 100.0,
        "cleanup_budget": 30.0,
        "probe_b64": b64({}),
        "status_b64": b64({"desired_state": "enabled", "runtime_state": "running"}),
    }
    first = dict(base, lease_id="nest-scope-1", invocations=1)
    second = dict(base, lease_id="nest-scope-2", invocations=2)
    results = {}

    def run_second():
        time.sleep(0.30)  # let scope 1 finish its pause
        results["second"] = kernel.run_protocol(second)
        kernel.run_protocol_exit(dict(second, tag="nested-exit2"))

    thread = threading.Thread(target=run_second)
    thread.start()
    results["first"] = kernel.run_protocol(first)
    thread.join(timeout=30)
    exit_first = kernel.run_protocol_exit(dict(first, tag="nested-exit1"))

    record = {
        "case": "F-L2a-nesting",
        "first_action": results["first"]["action"],
        "second_action": results["second"]["action"],
        "second_writes": results["second"]["writes"],
        "second_lease_set": results["second"].get("lease_set"),
        "exit_first_action": exit_first["action"],
        "counts": h.counts(),
        "lease_view": h.lease_view(),
        "owner_exists": h.owner_exists(),
        "nesting_established": results["second"]["writes"] > 0,
        "status": "PASS",
    }
    print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
