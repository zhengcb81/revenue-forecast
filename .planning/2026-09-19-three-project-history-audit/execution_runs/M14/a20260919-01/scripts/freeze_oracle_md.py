"""Record the frozen oracle.md body hash BEFORE any product run (standard library only).

Writes ``before/oracle_md_v1.json`` with the sha256 / byte count / line count of oracle.md and
refuses to overwrite an existing record (the frozen body is recorded exactly once; a second
record would create a competing baseline, which is forbidden).

Run this after oracle.md is written and before scripts/oracle_<CARD>.py or any product call.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt)
    oracle_md = os.path.join(attempt, "oracle.md")
    target = os.path.join(attempt, "before", "oracle_md_v1.json")
    if os.path.isfile(target):
        print("refusing to overwrite the single frozen-body record at %s" % target)
        return 9
    with open(oracle_md, "rb") as handle:
        payload = handle.read()
    doc = {
        "path": "oracle.md",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "lines": payload.decode("utf-8").count("\n"),
        "recorded_before_any_product_run": True,
        "recorded_at_unix": time.time(),
        "recorded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rule": "this is the ONLY pre-append baseline for oracle.md; the r2 section is appended "
                "below a boundary marker and the bytes above that marker must still hash to "
                "this value (scripts/verify_r2_boundary.py re-derives it)",
    }
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=True, indent=1)
        handle.write("\n")
    print("frozen body sha256 = %s bytes=%d lines=%d" % (doc["sha256"], doc["bytes"],
                                                         doc["lines"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
