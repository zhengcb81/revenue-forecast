"""Stub company-wiki worker CLI for the I-04-C simulations.

It is NOT the worker: it mutates a JSON state file inside the attempt
directory and appends journal events.  No real worker, provider, wiki root or
network is touched.

Usage:  <python> sim/stub_worker.py <base64-json-payload> <subcommand>

subcommands: worker-status | worker-pause | worker-resume
Payload keys: base, journal, tag, worker (optional state file name).
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time


def journal(payload, event):
    event = dict(event)
    event.setdefault("pid", os.getpid())
    event.setdefault("tag", payload.get("tag"))
    event.setdefault("monotonic", round(time.monotonic(), 6))
    with open(payload["journal"], "a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True, sort_keys=True) + "\n")
        handle.flush()


def state_path(payload):
    return os.path.join(payload["base"], payload.get("worker", "worker.json"))


def load(payload):
    path = state_path(payload)
    if not os.path.exists(path):
        return {"desired_state": "enabled", "runtime_state": "running",
                "actions": [], "blocked_resume": False}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save(payload, state):
    with open(state_path(payload), "w", encoding="utf-8") as handle:
        json.dump(state, handle, sort_keys=True)
        handle.flush()


def main(argv):
    payload = json.loads(base64.b64decode(argv[1]).decode("utf-8"))
    subcommand = argv[2]
    os.makedirs(payload["base"], exist_ok=True)
    if subcommand == "worker-status":
        state = load(payload)
        print(json.dumps({"desired_state": state["desired_state"],
                          "runtime_state": state["runtime_state"]}, sort_keys=True))
        return 0
    if subcommand == "worker-pause":
        state = load(payload)
        state["desired_state"] = "paused"
        state["runtime_state"] = "stopped"
        state["actions"].append("pause")
        save(payload, state)
        journal(payload, {"event": "worker_pause"})
        print(json.dumps({"desired_state": "paused", "runtime_state": "stopped"}, sort_keys=True))
        return 0
    if subcommand == "worker-resume":
        state = load(payload)
        state["actions"].append("resume")
        if state["desired_state"] != "paused":
            save(payload, state)
            journal(payload, {"event": "worker_resume_refused",
                              "desired_state": state["desired_state"]})
            print(json.dumps({"error": "worker is not paused; nothing to resume"}), file=sys.stderr)
            return 1
        state["desired_state"] = "enabled"
        state["runtime_state"] = "running"
        save(payload, state)
        journal(payload, {"event": "worker_resume"})
        print(json.dumps({"desired_state": "enabled", "runtime_state": "running"}, sort_keys=True))
        return 0
    print(f"unknown subcommand {subcommand}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
