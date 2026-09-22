"""Byte-faithful timed capture of one pre-push gate run (GATE-TIMEOUT-1200).

Usage:
    python timed_gate_run.py <repo_root> <out_txt> <times_json>

- Runs EXACTLY:  <python> -u <repo_root>/tools/pre_push_gate.py
  (no gate flags whatsoever; `-u` only makes the gate's stdout line-unbuffered
  so step-banner timestamps are truthful — a capture-fidelity flag, disclosed
  in commands.json).
- Merges stderr into stdout, reads raw bytes (no re-decoding), writes them
  verbatim to <out_txt> -> FULL unfiltered output.
- Records a UTC timestamp every time a line beginning b"=== " (a gate step
  banner) or the final GREEN banner arrives, plus the child exit code, into
  <times_json>.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    repo_root, out_path, times_path = (Path(p) for p in sys.argv[1:4])
    gate = repo_root / "tools" / "pre_push_gate.py"
    argv = [sys.executable, "-u", str(gate)]
    events: list[dict] = []
    t0 = time.monotonic()
    events.append({"event": "run_start", "utc": utc(), "argv": argv,
                   "cwd": str(repo_root)})
    with open(out_path, "wb") as out:
        proc = subprocess.Popen(
            argv,
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        assert proc.stdout is not None
        for raw in proc.stdout:
            out.write(raw)
            out.flush()
            line = raw.rstrip(b"\r\n")
            if line.startswith(b"=== ") or line.startswith(b"pre-push gate GREEN"):
                events.append({
                    "event": "banner",
                    "utc": utc(),
                    "elapsed_s": round(time.monotonic() - t0, 3),
                    "text": line.decode("utf-8", errors="replace"),
                })
        rc = proc.wait()
    events.append({
        "event": "run_end",
        "utc": utc(),
        "elapsed_s": round(time.monotonic() - t0, 3),
        "exit_code": rc,
    })
    # derive per-step wall times: each banner..next-banner interval
    steps = []
    banners = [e for e in events if e["event"] == "banner"]
    for i, b in enumerate(banners):
        end = banners[i + 1]["elapsed_s"] if i + 1 < len(banners) else None
        steps.append({
            "label": b["text"].lstrip("= ").strip(),
            "started_elapsed_s": b["elapsed_s"],
            "to_next_banner_elapsed_s": (None if end is None
                                         else round(end - b["elapsed_s"], 3)),
        })
    Path(times_path).write_text(
        json.dumps({"argv": argv, "events": events, "steps": steps},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"GATE_EXIT_CODE={rc}")
    return 0  # the wrapper always succeeds; the gate's rc is in times_json


if __name__ == "__main__":
    raise SystemExit(main())
