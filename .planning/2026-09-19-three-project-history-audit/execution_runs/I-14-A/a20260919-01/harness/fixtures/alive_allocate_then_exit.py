"""F3 (I-14-A): allocate measurable memory, stay alive, then exit 0.

Emits its own pid so the probe's sampler can be checked against the process it
claims to have measured.  The allocation is *not* an RSS oracle: committed bytes
and working set differ, so the check is order-of-magnitude plus pid identity
(oracle.md M7).
"""

from __future__ import annotations

import json
import os
import sys
import time

ALLOCATE_MB = 256
HOLD_SECONDS = 1.6


def main() -> int:
    blocks = []
    for _ in range(ALLOCATE_MB):
        block = bytearray(1024 * 1024)
        block[0] = 1
        block[-1] = 1
        blocks.append(block)
    print(json.dumps({
        "status": "ok",
        "fixture": "F3-alive-allocate-then-exit",
        "pid": os.getpid(),
        "allocated_mb": ALLOCATE_MB,
        "hold_seconds": HOLD_SECONDS,
    }, ensure_ascii=False))
    sys.stdout.flush()
    time.sleep(HOLD_SECONDS)
    print(json.dumps({"status": "ok", "phase": "done", "pid": os.getpid(),
                      "blocks_held": len(blocks)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
