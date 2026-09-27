"""F2 (I-14-A): exits 0 while the business result is a failure.

The point: rc == 0 is not success.  A meter that only checks the return code
reports this as a fast, successful query.
"""

from __future__ import annotations

import json
import os
import sys
import time

time.sleep(0.05)
print(json.dumps({
    "status": "failed",
    "error": "not_found",
    "detail": "no registered document for this identity",
    "fixture": "F2-exit0-business-failure",
    "pid": os.getpid(),
}, ensure_ascii=False))
sys.stdout.flush()
sys.exit(0)
