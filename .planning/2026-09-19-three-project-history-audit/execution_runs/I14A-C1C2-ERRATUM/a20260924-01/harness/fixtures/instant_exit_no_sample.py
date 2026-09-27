"""F4 (I-14-A control): valid success output, no time to be sampled.

The point: the "no sample collected" branch is reachable.  It must report
``peak_rss_gb = null`` with ``peak_rss_source = "uncollected:…"`` and it must not
be treated as a green 0.0.
"""

from __future__ import annotations

import json
import os
import sys

print(json.dumps({
    "status": "ok",
    "fixture": "F4-instant-exit-no-sample",
    "pid": os.getpid(),
}, ensure_ascii=False))
sys.stdout.flush()
sys.exit(0)
