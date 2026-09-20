"""Read I-04-D case summaries and print the observables the oracle is judged on."""

from __future__ import annotations

import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
cases = sys.argv[2:] or None
if not root.exists():
    print(f"runs root not found: {root}")
    raise SystemExit(1)

for case_dir in sorted(root.iterdir()):
    if not case_dir.is_dir():
        continue
    if cases and case_dir.name not in cases:
        continue
    summary_path = case_dir / "summary.json"
    if not summary_path.exists():
        print(f"{case_dir.name}: NO summary.json")
        continue
    s = json.loads(summary_path.read_text(encoding="utf-8"))
    print(f"=== {case_dir.name} ===")
    print(
        f"  pause={s['pause_calls']} resume={s['resume_calls']} status={s['status_calls']} "
        f"lock_acq={s['lock_acquisitions']} max_lock_wait={s['max_lock_wait_seconds']} "
        f"wall={s['case_wall_seconds']}"
    )
    if s.get("harness_error"):
        print(f"  HARNESS ERROR: {s['harness_error']}")
    final = s["final_lease"]
    print(
        f"  final: refcount={final['refcount_exists']} lease_set={final['lease_set']} "
        f"gen={final['generation']} owner={(final['owner'] or {}).get('lease_id')} "
        f"resume_required={final['resume_required']} marker={final['owner_marker_exists']} "
        f"lock={final['lock_exists']}/{final['lock_bytes']}"
    )
    print(f"  worker: {s['final_worker_state']}")
    for tag, report in sorted(s["reports"].items()):
        stats = report.get("stats") or {}
        print(
            f"  [{tag}] pid={report.get('pid')} exit={report.get('exit_code')} "
            f"action={report.get('action')} err={report.get('error_code')!r} "
            f"cleanup={stats.get('cleanup_status')!r} wall={report.get('phase_wall_seconds')}"
        )
        if report.get("error_message"):
            print(f"      msg={report['error_message'][:220]}")
        for key in ("after_inner_exit", "after_enter", "after_exit", "after_error"):
            snap = report.get(key)
            if isinstance(snap, dict):
                print(
                    f"      {key}: refcount={snap['refcount_exists']} "
                    f"lease_set={snap['lease_set']} marker={snap['owner_marker_exists']} "
                    f"gen={snap['generation']}"
                )
    for key in ("intermediate", "after_a_exit", "crash_after", "precondition", "after",
                "injected", "b_joined", "lock_holder", "reacquire", "refcount_is_directory",
                "owner_rewrite", "lock_exists_after", "lock_bytes_after"):
        if key in s["participants"]:
            print(f"  meta.{key}: {json.dumps(s['participants'][key], ensure_ascii=False)[:400]}")
    events = [e.get("event") for e in s["protocol_journal"]]
    print(f"  protocol_journal events: {events}")
