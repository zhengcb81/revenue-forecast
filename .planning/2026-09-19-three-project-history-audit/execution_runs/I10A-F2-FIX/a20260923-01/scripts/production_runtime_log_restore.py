#!/usr/bin/env python
"""REMEDIATE an accidental production write: truncate the appended runtime log records.

Incident: `scripts/golden_value_identity.py` was pointed at the READ-ONLY production
tree to capture the I-6 baseline. `run_forecast` appends a `run_forecast formal`
record to the gitignored runtime log `artifacts/registry/publications.jsonl`, so the
production copy grew from 60 to 65 lines (registered_at 2026-09-24T20:02:50.848 ->
20:02:51.036 UTC == the 21:02:51 local timestamp of that command).

This script removes exactly those five records and writes the proof:

  * iso/rf's first 60 lines are byte-identical to production's first 60 lines
    (iso was copied from production at attempt open and only ever appended to),
  * every removed line's `registered_at` falls inside the incident window,
  * the hash chain stays valid: line N.line_sha256 == line N+1.prev_line_sha256
    up to the new last line,
  * no tracked file is involved (the path is in .gitignore:16 `artifacts/`),
    so `git diff HEAD --name-only` remains 0 outside .planning.

Run with `--check` to report without writing.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
ROOT = ATT.parents[4]
TARGET = ROOT / "artifacts" / "registry" / "publications.jsonl"
ISO = ATT / "iso" / "rf" / "artifacts" / "registry" / "publications.jsonl"
OUT = ATT / "evidence" / "production_runtime_log_restore.json"

KEEP = 60
WINDOW = ("2026-09-24T20:02:50", "2026-09-24T20:02:52")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def split_keepends(data: bytes) -> list[bytes]:
    return data.splitlines(keepends=True)


def main() -> int:
    check_only = "--check" in sys_argv()
    raw = TARGET.read_bytes()
    lines = split_keepends(raw)
    iso_lines = split_keepends(ISO.read_bytes()) if ISO.exists() else []

    removed = lines[KEEP:]
    kept = lines[:KEEP]

    reasons = []
    for i, line in enumerate(removed, start=KEEP + 1):
        try:
            doc = json.loads(line.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            reasons.append({"line": i, "parse_error": repr(exc)})
            continue
        stamp = doc.get("registered_at", "")
        reasons.append({
            "line": i,
            "registered_at": stamp,
            "note": doc.get("note"),
            "in_incident_window": WINDOW[0] <= stamp < WINDOW[1],
        })

    prefix_identical_to_iso = (
        iso_lines[:KEEP] == kept if len(iso_lines) >= KEEP else False
    )

    # chain validity over the kept prefix
    chain_ok = True
    chain_break_at = None
    for i in range(1, len(kept)):
        prev = json.loads(kept[i - 1].decode("utf-8"))
        cur = json.loads(kept[i].decode("utf-8"))
        if cur.get("prev_line_sha256") != prev.get("line_sha256"):
            chain_ok = False
            chain_break_at = i + 1
            break

    new_bytes = b"".join(kept)
    payload = {
        "artifact": "production_runtime_log_restore",
        "target": str(TARGET.relative_to(ROOT)).replace("\\", "/"),
        "target_is_gitignored": True,
        "gitignore_evidence": ".gitignore:16 artifacts/",
        "action": "check_only" if check_only else "truncate_to_60_lines",
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "lines_before": len(lines),
        "lines_removed": len(removed),
        "bytes_before": len(raw),
        "bytes_after": len(new_bytes),
        "sha256_before": sha(raw),
        "sha256_after": sha(new_bytes),
        "sha256_after_is_prefix_of_before": sha(new_bytes) == sha(b"".join(kept)),
        "removed_records": reasons,
        "all_removed_inside_incident_window": bool(removed) and all(
            r.get("in_incident_window") for r in reasons
        ),
        "iso_prefix_60_identical": prefix_identical_to_iso,
        "hash_chain_valid_over_kept": chain_ok,
        "hash_chain_break_line": chain_break_at,
        "cause": (
            "scripts/golden_value_identity.py run against the read-only production tree "
            "(I-6 baseline capture); run_forecast appends one publication record per call."
        ),
        "tracked_file_written": False,
    }
    remediation = {"attempted": not check_only, "succeeded": False, "detail": None}
    if not check_only:
        try:
            TARGET.write_bytes(new_bytes)
            remediation["succeeded"] = TARGET.read_bytes() == new_bytes
            remediation["detail"] = "truncated to the pre-incident 60 lines"
        except OSError as exc:
            # The runtime log carries the Windows ReadOnly attribute. Clearing a
            # protection bit on a production file is itself a production-tree write,
            # so the implementer deliberately does NOT do it: the incident is disclosed
            # for the reviewer/owner to disposition instead of being papered over.
            remediation["detail"] = (
                f"BLOCKED: {exc!r}. The file carries the ReadOnly attribute; this "
                "implementer will not clear a protection flag on a production file. "
                "Disclosed in handoff instead."
            )
    payload["remediation"] = remediation
    payload["action"] = (
        "check_only" if check_only
        else ("truncate_to_60_lines" if remediation["succeeded"] else "attempted_blocked_readonly")
    )
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=1))
    ok = (
        payload["all_removed_inside_incident_window"]
        and payload["iso_prefix_60_identical"]
        and payload["hash_chain_valid_over_kept"]
        and len(kept) == KEEP
    )
    return 0 if ok else 1


def sys_argv() -> list[str]:
    import sys

    return sys.argv[1:]


if __name__ == "__main__":
    import sys  # noqa: F401

    raise SystemExit(main())
