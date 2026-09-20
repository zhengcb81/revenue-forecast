"""Hold the LEASE lock from an external process, for the r3 timeout cases.

Usage:
  <python> sim/hold_lock.py <base64-json-payload> <hold_seconds>

The payload keys are `base` (the case directory) and `name` (the lock file name).
The helper writes `<base>/_external_holder.ready` once it holds the lock, so the
scheduler can synchronise deterministically instead of sleeping.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from kernel import FileLock  # noqa: E402


def main(argv):
    payload = json.loads(base64.b64decode(argv[1]).decode("utf-8"))
    hold = float(argv[2])
    path = os.path.join(payload["base"], payload.get("name", "filing_fetch_pause.lock"))
    lock = FileLock(path, 30.0)
    lock.acquire()
    with open(os.path.join(payload["base"], "_external_holder.ready"), "w",
              encoding="utf-8") as handle:
        handle.write(str(os.getpid()))
    time.sleep(hold)
    lock.release()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
