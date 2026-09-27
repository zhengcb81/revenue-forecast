"""I-11-A: archive the terminal state in one canonical log file.

The per-step stdout of the R2 re-run lives in:
  * `evidence/I-11-A/commands_run.log` (the R2 sequence that produced the current artifacts)
  * `evidence/I-11-A/extract/*.stdout.txt` / `*.stderr.txt` (per-command streams)
  * `commands.json` (argv, expected and observed return codes, output sha256)
This script writes ONE canonical index so the reviewer does not have to reconcile
several partial logs, and it records the sha256 of every log it points at.

Usage: python -X utf8 -B tools/archive_run_log.py <attempt_root>
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    attempt = sys.argv[1]
    ev = os.path.join(attempt, "evidence", "I-11-A")
    extract = os.path.join(ev, "extract")

    logs = []
    for base, dirs, files in os.walk(attempt):
        if os.sep + "iso" + os.sep in base + os.sep and "venv" in base:
            dirs[:] = []
            continue
        if os.path.basename(base) == "__pycache__":
            dirs[:] = []
            continue
        for f in sorted(files):
            if f.endswith((".log", ".txt")) and ("log" in f or "stdout" in f or "stderr" in f):
                p = os.path.join(base, f)
                logs.append({
                    "path": os.path.relpath(p, attempt).replace("\\", "/"),
                    "byte_size": os.path.getsize(p),
                    "sha256": sha256(p),
                })
    logs.sort(key=lambda e: e["path"])

    commands = json.load(open(os.path.join(attempt, "commands.json"), encoding="utf-8"))
    checks = []
    for c in commands:
        checks.append({"id": c["id"], "expected_returncode": c["expected_returncode"],
                       "observed_returncode": c.get("observed_returncode"),
                       "matches": c["expected_returncode"] == c.get("observed_returncode")})

    selfcheck = json.load(open(os.path.join(ev, "final_selfcheck.json"), encoding="utf-8"))
    validation = json.load(open(os.path.join(ev, "validation_report.json"), encoding="utf-8"))
    arithmetic = json.load(open(os.path.join(extract, "arithmetic_oracle.json"), encoding="utf-8"))

    archive = {
        "attempt_id": "a20260919-01",
        "card_id": "I-11-A",
        "archived_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "tools/archive_run_log.py",
        "purpose": ("single index of the archived run logs and of the terminal state, so that the several "
                    "partial logs in this attempt do not have to be reconciled by hand; the logs themselves "
                    "are NOT re-run or rewritten here"),
        "logs": logs,
        "log_count": len(logs),
        "commands": checks,
        "commands_all_match": all(c["matches"] for c in checks),
        "terminal_results": {
            "final_selfcheck_verdict": selfcheck.get("verdict"),
            "final_selfcheck_problems": selfcheck.get("problems"),
            "validation_positive_case": validation["positive_case"]["verdict"],
            "validation_counterexamples": validation["counterexample_summary"],
            "validation_counts": validation["counts"],
            "arithmetic_summary": arithmetic["summary"],
        },
        "note": ("This file is written AFTER tools/hash_attempt.py by design (it hashes the logs, so it "
                 "cannot be inside the manifest it summarizes without going stale). Its own hash is "
                 "therefore reported in handoff.json under current_source_hashes.run_log_archive."),
    }
    out = os.path.join(ev, "run_log_archive.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(archive, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("logs indexed:", len(logs))
    print("commands all match:", archive["commands_all_match"])
    print("selfcheck:", archive["terminal_results"]["final_selfcheck_verdict"],
          archive["terminal_results"]["final_selfcheck_problems"])
    print("wrote", out, "sha256", sha256(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
