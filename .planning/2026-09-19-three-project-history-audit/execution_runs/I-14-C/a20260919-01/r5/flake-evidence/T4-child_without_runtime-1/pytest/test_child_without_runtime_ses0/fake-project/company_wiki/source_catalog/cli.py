from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

project = Path.cwd()
catalog = project / ".source_catalog"
count_path = catalog / "fake_worker_count.txt"
count = int(count_path.read_text(encoding="utf-8")) + 1 if count_path.exists() else 1
count_path.write_text(str(count), encoding="utf-8")
behaviors = json.loads((project / "fake_behaviors.json").read_text(encoding="utf-8"))
behavior = behaviors[min(count - 1, len(behaviors) - 1)]
if "runtime_heartbeat_age_seconds" in behavior:
    now = time.time()
    runtime = {
        "schema_version": "1.0",
        "pid": os.getpid(),
        "heartbeat_at": now - float(behavior["runtime_heartbeat_age_seconds"]),
        "updated_at": now - float(behavior["runtime_heartbeat_age_seconds"]),
        "worker_status": behavior.get("worker_status", "normalizing"),
        "current_path": behavior.get("current_path", "slow.pdf"),
        "current_path_started_at": now
        - float(behavior.get("current_path_elapsed_seconds", 0)),
    }
    (catalog / "worker_runtime.json").write_text(
        json.dumps(runtime) + "\n",
        encoding="utf-8",
    )
if behavior.get("desired_state") or behavior.get("stop_requested_for"):
    control = json.loads(
        (catalog / "worker_control.json").read_text(encoding="utf-8")
    )
    if behavior.get("desired_state"):
        control["desired_state"] = behavior["desired_state"]
    if behavior.get("stop_requested_for"):
        control["stop_requested_for"] = behavior["stop_requested_for"]
    control["updated_at"] = count + 1
    (catalog / "worker_control.json").write_text(
        json.dumps(control) + "\n",
        encoding="utf-8",
    )
if behavior.get("stdout"):
    print(behavior["stdout"], flush=True)
if behavior.get("stderr"):
    print(behavior["stderr"], file=sys.stderr, flush=True)
time.sleep(float(behavior.get("sleep_seconds", 0)))
raise SystemExit(int(behavior.get("exit_code", 0)))
