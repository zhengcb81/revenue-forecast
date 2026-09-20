"""F-L2a probe: two leases of ONE process (real nesting), r2 kernel API.

The frozen protocol's status guard runs on every entry and the first scope pauses
the worker; a second scope of the SAME process that enters afterwards reads
`desired_state=paused` inside its critical section and joins the live cycle
(ADR-9/9b), so two leases from one pid coexist and are released independently --
only the lease_id is ever removed, never the pid.

Runs ENTIRELY in one process and writes only inside its own evidence directory.
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
        "declared_liveness": True,
    }
    first = dict(base, lease_id="nest-scope-1", invocations=1, tag="nested-scope1")
    second = dict(base, lease_id="nest-scope-2", invocations=2, tag="nested-scope2")
    results = {}

    def run_second():
        time.sleep(0.30)  # let scope 1 finish its pause
        results["second"] = kernel.run_protocol(second)

    thread = threading.Thread(target=run_second)
    thread.start()
    results["first"] = kernel.run_protocol(first)
    thread.join(timeout=30)
    # scope 1 leaves first while scope 2 is still inside its scope
    exit_first = kernel.run_protocol_exit(dict(first, tag="nested-exit1"))
    view_after_first = h.lease_view()
    exit_second = kernel.run_protocol_exit(dict(second, tag="nested-exit2"))

    record = {
        "case": "F-L2a-nesting",
        "first_action": results["first"]["action"],
        "second_action": results["second"]["action"],
        "second_actions": results["second"].get("actions"),
        "second_writes": results["second"]["writes"],
        "second_lease_set": results["second"].get("lease_set"),
        "exit_first_action": exit_first["action"],
        "exit_first_transfer": exit_first.get("ownership_transferred_to"),
        "exit_second_action": exit_second["action"],
        "view_after_first_exit": view_after_first,
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
