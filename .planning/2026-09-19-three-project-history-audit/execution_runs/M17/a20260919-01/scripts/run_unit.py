"""Capture one command's raw stdout / stderr / exit code into real files.

Used as a module by run_pipeline.py (so every unit of the card is captured the same
way) and usable from the command line to replay a single unit:

  python -X utf8 -B run_unit.py --label <id> --stdout <p> --stderr <p> --rc-json <p> -- <argv...>

PowerShell 5.1 redirection writes UTF-16, which makes evidence files unreadable as
text; this stdlib-only helper writes UTF-8 bytes and records the child's RAW return
code in JSON.  It never rewrites or interprets the business result.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def capture(argv, stdout_path, stderr_path, rc_path, label, cwd=None, extra=None):
    for path in (stdout_path, stderr_path, rc_path):
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)
    started = datetime.datetime.now(datetime.timezone.utc)
    with open(stdout_path, "wb") as out, open(stderr_path, "wb") as err:
        completed = subprocess.run(list(argv), stdout=out, stderr=err, cwd=cwd)
    finished = datetime.datetime.now(datetime.timezone.utc)
    record = {
        "label": label,
        "argv": list(argv),
        "cwd": cwd or os.getcwd(),
        "raw_returncode": completed.returncode,
        "started_utc": started.isoformat(),
        "finished_utc": finished.isoformat(),
        "stdout_path": os.path.abspath(stdout_path),
        "stderr_path": os.path.abspath(stderr_path),
        "stdout_sha256": sha256(stdout_path),
        "stderr_sha256": sha256(stderr_path),
        "capture_rule": ("the recorded rc is the child process's raw return code; stdout/stderr "
                         "are stored as raw UTF-8 bytes and never rewritten"),
    }
    if extra:
        record.update(extra)
    with open(rc_path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=1)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--stdout", required=True)
    parser.add_argument("--stderr", required=True)
    parser.add_argument("--rc-json", required=True)
    parser.add_argument("--cwd", default=None)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("HARNESS ERROR: no command given after --", file=sys.stderr)
        return 1
    code = capture(command, args.stdout, args.stderr, args.rc_json, args.label, cwd=args.cwd)
    print("run_unit label=%s raw_returncode=%s -> %s" % (args.label, code, args.stdout))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
