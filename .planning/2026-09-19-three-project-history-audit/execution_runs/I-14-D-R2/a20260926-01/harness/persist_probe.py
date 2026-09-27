"""I-14-D-R2: the persistence ("落盘") probe for the dispatched defect.

    python persist_probe.py --src <tree>/src --label <label> --log <events.jsonl> --out <json>

It reproduces, byte for byte, the write path the review exercised end-to-end:

    worker.py:1060  message = str(exc) or repr(exc)
    worker.py:1066  message_redacted=redact_and_truncate(message)
    worker.py:1072  payload = {"event", "pid", "timestamp", "catalog_dir", **extra}
    worker.py:1079  appended to worker_process_events.jsonl

The only difference is the destination file: this probe appends into this
attempt's own evidence directory, never into the product repository (a product
write is out of scope for this round and would be a `blocked` stop).

The dispatched input is reviewer_report.md L28-L31:
    "Authorization: Bearer\\n<SECRET>\\ndoc=17"

Pass = the JSON line read back from disk carries NO secret and DOES carry the
redaction plus the surviving diagnostic.  Exit 0 = pass, 3 = secret persisted.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SECRET = "ghp_ZQ7ReviewerFakeCredential0123456789"
MARKER = "SYNTHETIC_AUDIT_TOKEN"
RAW = "Authorization: Bearer\n" + SECRET + "\ndoc=17"


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--log", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--raw", default=None,
                   help="override the raw exception message (default: the dispatched D1)")
    args = p.parse_args(argv)

    sys.path.insert(0, str(Path(args.src).resolve()))
    try:
        from company_wiki.source_catalog.observability import redact_and_truncate
    except ImportError as exc:
        report = {"label": args.label, "helper_present": False,
                  "verdict": "cannot_adjudicate",
                  "import_error": f"{type(exc).__name__}: {exc}"}
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                                  encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True))
        return 2

    raw = args.raw or RAW
    message_redacted = redact_and_truncate(raw)          # worker.py:1066
    payload = {                                          # worker.py:1072-1078
        "event": "unhandled_exception",
        "pid": os.getpid(),
        "timestamp": datetime.now().isoformat(),
        "catalog_dir": str(Path(args.log).resolve().parent),
        "exception_type": "RuntimeError",
        "message_redacted": message_redacted,
        "cause_types": ["RuntimeError"],
    }
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:     # append-only, worker.py:1079
        fh.write(json.dumps(payload, ensure_ascii=True) + "\n")

    # read back the last line, as a consumer of the log would
    last = log_path.read_text(encoding="utf-8").strip().splitlines()[-1]
    persisted = json.loads(last)["message_redacted"]

    checks = {
        "secret_absent": SECRET not in persisted,
        "marker_absent": MARKER not in persisted,
        "has_redacted": "<redacted>" in persisted,
        "doc17_kept": "doc=17" in persisted,
        "le_200": len(persisted) <= 200,
    }
    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "log": str(log_path),
        "raw_message": raw,
        "message_redacted_written": message_redacted,
        "message_redacted_read_back": persisted,
        "checks": checks,
        "secret_persistence_fixed": all(checks.values()),
        "verdict": "PERSISTED_CLEAN" if all(checks.values()) else "SECRET_PERSISTED",
    }
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                              encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if all(checks.values()) else 3


if __name__ == "__main__":
    sys.exit(main())
