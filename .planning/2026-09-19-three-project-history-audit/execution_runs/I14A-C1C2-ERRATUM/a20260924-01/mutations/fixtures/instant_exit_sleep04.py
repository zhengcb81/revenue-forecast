"""I14A-C1C2-ERRATUM mutation fixture M3/M4: F4 with its lifetime extended.

Byte-identical to ``iso/fixtures/instant_exit_no_sample.py`` except for the
``time.sleep(0.4)`` added after the envelope is printed, which pushes the call's
measured lifetime (0.4 s+) past the identity-scope threshold (0.1504 s = 2x the
effective sampling cadence).  Used only to prove that the scoped
``fixture_pid_is_in_samples`` assertion re-engages for a long-lived F4 call
(oracle.md §6, arms M3/M4).  Not a card fixture; lives under ``mutations/``.
"""

from __future__ import annotations

import json
import os
import sys
import time

print(json.dumps({
    "status": "ok",
    "fixture": "F4-instant-exit-no-sample",
    "pid": os.getpid(),
}, ensure_ascii=False))
sys.stdout.flush()
time.sleep(0.4)          # MUTATION: extend lifetime beyond 2x the cadence
sys.exit(0)
