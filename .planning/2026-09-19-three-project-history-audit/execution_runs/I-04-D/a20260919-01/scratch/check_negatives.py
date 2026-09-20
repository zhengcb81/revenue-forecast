"""Cross-check the negative-case claim: which of N1..N13 have full scheduler evidence.

The implementer's interim report said "13 frozen negative cases … all green".  A helper
agent correctly objected that oracle's N numbering does not map one-to-one onto the
scheduler cases, so this script enumerates the actual evidence per negative case.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ATTEMPT = Path(__file__).resolve().parents[1]
RUN = ATTEMPT / "evidence" / "run"

# N-id -> (scheduler case or None, the judgement fields the oracle row demands)
LEDGER = {
    "N1": ("I04D-CASE-F-L8a-W1", ("exit_code", "error_code", "action", "pause_calls", "resume_calls")),
    "N2": ("I04D-CASE-F-L8a-W1b", ("exit_code", "error_code", "action", "pause_calls", "resume_calls")),
    "N3": ("I04D-CASE-F-L8b-W2", ("exit_code", "error_code", "action", "pause_calls", "resume_calls")),
    "N4": ("I04D-CASE-F-L8c-W4", ("exit_code", "error_code", "action", "pause_calls", "resume_calls")),
    "N5": (None, ("error_code", "rc", "sha256_before_after")),
    "N6": (None, ("error_code", "rc", "sha256_before_after")),
    "N7": (None, ("error_code", "rc", "sha256_before_after")),
    "N8": ("I04D-CASE-F-L8g-UNKNOWN", ("error_code", "exit_code", "sha256_before_after", "pause_calls")),
    "N9": ("I04D-CASE-F-L8h-WRITEFAIL", ("error_code", "exit_code", "action", "pause_calls")),
    "N10": ("I04D-CASE-F-LK-TIMEOUT", ("error_code", "exit_code", "pause_calls", "resume_calls")),
    "N11": ("I04D-CASE-F-LK-TIMEOUT-ZERO", ("error_code", "exit_code", "pause_calls", "resume_calls")),
    "N12": ("I04D-CASE-F-LK-HOLDER-CRASH", ("exit_code", "lock_bytes", "reacquire")),
    "N13": ("I04D-CASE-F-LK-NEVER-UNLINK", ("lock_exists", "lock_bytes", "pause_calls", "resume_calls")),
}

PYTEST_ONLY = {
    "N5": "test_read_fail_closed_on_corrupt_legacy_and_element_level (lease_state_corrupt, bytes unchanged)",
    "N6": "same test, legacy row (lease_state_legacy, bytes unchanged)",
    "N7": "same test, element-level row (lease_state_corrupt)",
}

full = partial = none = 0
rows = []
for nid, (case, fields) in LEDGER.items():
    if case is None:
        none += 1
        rows.append((nid, "pytest only", PYTEST_ONLY[nid], "no scheduler case exists"))
        continue
    summary_path = RUN / case / "summary.json"
    if not summary_path.exists():
        none += 1
        rows.append((nid, case, "MISSING summary.json", ""))
        continue
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    # which demanded fields are actually populated with a case-specific value?
    present = []
    missing = []
    reports = summary.get("reports") or {}
    for field in fields:
        if field in {"error_code", "exit_code", "action"}:
            hit = any(
                r.get(field) not in (None, "")
                for r in reports.values()
                if isinstance(r, dict)
            )
        elif field == "pause_calls":
            hit = summary.get("pause_calls") is not None
        elif field == "resume_calls":
            hit = summary.get("resume_calls") is not None
        elif field == "sha256_before_after":
            meta = summary.get("participants") or {}
            hit = any(
                isinstance(v, dict) and any(k.startswith("sha256") for k in v)
                for v in meta.values()
            )
        elif field == "lock_bytes":
            hit = (summary.get("final_lease") or {}).get("lock_bytes") is not None
        elif field == "lock_exists":
            hit = (summary.get("final_lease") or {}).get("lock_exists") is not None
        elif field == "reacquire":
            hit = "reacquire" in (summary.get("participants") or {})
        else:
            hit = False
        (present if hit else missing).append(field)
    if not missing:
        full += 1
        state = "FULL"
    else:
        partial += 1
        state = "PARTIAL"
    rows.append(
        (
            nid,
            case,
            state,
            f"harness_error={summary.get('harness_error')!r} missing={missing}",
        )
    )

print(f"negative cases with FULL scheduler evidence : {full}")
print(f"negative cases with PARTIAL evidence        : {partial}")
print(f"negative cases with NO scheduler evidence   : {none}")
print()
for nid, case, state, note in rows:
    print(f"{nid:4} {state:8} {case or '-':32} {note}")
