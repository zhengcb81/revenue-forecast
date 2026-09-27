"""F1 (I-14-A): prints a success-shaped envelope on stdout, then exits 7.

The point: rc != 0 while stdout looks like a good resolve.  A meter that trusts
stdout (or ignores rc) reports this as a fast, successful query.
"""

from __future__ import annotations

import json
import os
import sys
import time

time.sleep(0.05)          # a plausible "fast query" duration
print(json.dumps({
    "status": "ok",
    "document_id": "urn:company-wiki:document:sha256:" + "0" * 64,
    "mode": "exact",
    "fixture": "F1-exit7-success-stdout",
    "pid": os.getpid(),
}, ensure_ascii=False))
sys.stdout.flush()
sys.exit(7)
