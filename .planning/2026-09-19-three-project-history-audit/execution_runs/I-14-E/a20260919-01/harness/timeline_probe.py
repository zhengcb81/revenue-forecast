"""I-14-E glue: compact timelines from the frozen band's surviving scratch record.

Prints, for a chosen set of runs, the event-by-event timeline (status, attempt,
uptime, timestamp delta) so the failure mechanism can be read off the raw record
rather than inferred from the pytest assertion.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCRATCH = Path(os.environ.get("TEMP", "")) / "i14c-flake-freq"


def ts(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def timeline(tag: str) -> None:
    run_dir = SCRATCH / tag
    events_path = next(run_dir.rglob("worker_launcher_events.jsonl"), None)
    if events_path is None:
        print(f"{tag}: no events")
        return
    events = [json.loads(line) for line in
              events_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    t0 = ts(events[0]["recorded_at"])
    print(f"\n{tag}  ({len(events)} events)")
    for e in events:
        delta = (ts(e["recorded_at"]) - t0).total_seconds()
        extra = []
        if e.get("attempt") is not None:
            extra.append(f"attempt={e['attempt']}")
        if e.get("child_pid") is not None:
            extra.append(f"pid={e['child_pid']}")
        if e.get("uptime_seconds") is not None:
            extra.append(f"uptime={e['uptime_seconds']}")
        if e.get("exit_code") is not None:
            extra.append(f"rc={e['exit_code']}")
        if e.get("restart_delay_seconds") is not None:
            extra.append(f"delay={e['restart_delay_seconds']}")
        print(f"  t+{delta:6.3f}s  {e['status']:<18} {' '.join(extra)}"
              + (f"  msg={e['message']}" if e.get("message") else ""))


if __name__ == "__main__":
    for tag in sys.argv[1:]:
        timeline(tag)
