"""I-14-E: concurrent-activity sampler (oracle-addendum-B B2).

Samples the machine's process inventory while the measurement arms run and writes one JSON
object per sample to ``after/concurrent-activity.jsonl``:

  * every python / pytest / powershell / node / chrome-headless-shell process, with pid,
    parent pid, creation time and command line;
  * which of them belong to this attempt (matched by the attempt path in the command line)
    versus to another session -- the parent's CF-I14F-X1 asks for exactly this distinction,
    because "load" has to be attributed to something concrete, not asserted;
  * a CPU-delta ranking over the sample interval (only positive deltas above a threshold).

Cheap by construction: one CIM query per interval, no child processes.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
OUT = ATTEMPT / "after" / "concurrent-activity.jsonl"

QUERY = (
    "Get-CimInstance Win32_Process | "
    "Where-Object { $_.Name -match 'python|pytest|powershell|node|chrome-headless-shell' } | "
    "Select-Object ProcessId,ParentProcessId,Name,CreationDate,CommandLine | "
    "ConvertTo-Json -Compress -Depth 3"
)

CPU_QUERY = (
    "Get-Process | Select-Object Id,ProcessName,CPU | ConvertTo-Json -Compress -Depth 2"
)


def run_ps(query: str) -> object:
    proc = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                           query], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          text=True, encoding="utf-8", errors="replace")
    text = (proc.stdout or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=2400.0)
    parser.add_argument("--interval", type=float, default=20.0)
    parser.add_argument("--label", default="campaign")
    args = parser.parse_args(argv)

    attempt_text = str(ATTEMPT)
    previous: dict[int, float] = {}
    deadline = time.time() + args.seconds
    with OUT.open("a", encoding="utf-8") as handle:
        while time.time() < deadline:
            stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
            procs = run_ps(QUERY)
            if procs is None:
                procs = []
            elif isinstance(procs, dict):
                procs = [procs]
            cpu_now = run_ps(CPU_QUERY) or []
            if isinstance(cpu_now, dict):
                cpu_now = [cpu_now]
            deltas = []
            current: dict[int, float] = {}
            for item in cpu_now:
                pid = item.get("Id")
                cpu = item.get("CPU")
                if pid is None or cpu is None:
                    continue
                current[pid] = float(cpu)
                if pid in previous:
                    delta = float(cpu) - previous[pid]
                    if delta > 0.2:
                        deltas.append({"pid": pid, "name": item.get("ProcessName"),
                                       "cpu_delta": round(delta, 2)})
            previous = current
            mine, others = [], []
            for item in procs:
                line = item.get("CommandLine") or ""
                record = {"pid": item.get("ProcessId"),
                          "ppid": item.get("ParentProcessId"),
                          "name": item.get("Name"),
                          "created": item.get("CreationDate"),
                          "cmd": line[:220]}
                (mine if attempt_text in line else others).append(record)
            handle.write(json.dumps({
                "label": args.label, "sampled_at": stamp,
                "attempt_processes": mine, "other_processes": others,
                "cpu_deltas_top": sorted(deltas, key=lambda d: -d["cpu_delta"])[:10],
                "other_python_or_pytest": [r for r in others
                                           if "python" in (r["name"] or "").lower()
                                           or "pytest" in (r["cmd"] or "").lower()],
            }, ensure_ascii=False) + "\n")
            handle.flush()
            time.sleep(args.interval)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
