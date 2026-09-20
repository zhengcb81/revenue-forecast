"""Cross-process lock stress + the two RED counterexamples for the lock ADR.

Modes:
  counter        N processes x M read-modify-write increments under the real OS lock
  counter-nolock same, without the lock (control: proves updates are lost)
  holder-crash   a child dies while holding the lock; the parent must get it back
  resume-race    two participants reach the release decision without a lock
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from harness import PARTICIPANT, PYTHON, Harness, b64  # noqa: E402,F401
from kernel import FileLock  # noqa: E402


def worker_counter(payload_path):
    payload = json.loads(open(payload_path, encoding="utf-8").read())
    base = payload["base"]
    counter = os.path.join(base, "counter.txt")
    lock_path = os.path.join(base, "counter.lock")
    journal = os.path.join(base, "counter.journal.jsonl")
    rounds = int(payload["rounds"])
    use_lock = bool(payload.get("use_lock", True))
    acq = 0
    for _ in range(rounds):
        if use_lock:
            lock = FileLock(lock_path, 30.0)
            lock.acquire()
            acq += 1
        try:
            try:
                with open(counter, "r", encoding="utf-8") as handle:
                    value = int(handle.read().strip() or "0")
            except FileNotFoundError:
                value = 0
            value += 1
            with open(counter, "w", encoding="utf-8") as handle:
                handle.write(str(value))
        finally:
            if use_lock:
                lock.release()
    with open(journal, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"tag": payload["tag"], "pid": os.getpid(),
                                 "rounds": rounds, "lock_acquisitions": acq}) + "\n")
    return 0


def stress_counter(root, processes=8, rounds=25, use_lock=True, timeout=180.0):
    h = Harness("F-LK1" if use_lock else "F-LK2", root)
    payload_path = os.path.join(h.base, "payload.json")
    counter = os.path.join(h.base, "counter.txt")
    with open(counter, "w", encoding="utf-8") as handle:
        handle.write("0")
    procs = []
    for index in range(processes):
        body = {"base": h.base, "tag": f"C{index}", "rounds": rounds, "use_lock": use_lock}
        path = os.path.join(h.base, f"payload.{index}.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(body, handle)
        out = open(os.path.join(h.base, f"stdout.C{index}.txt"), "w", encoding="utf-8")
        err = open(os.path.join(h.base, f"stderr.C{index}.txt"), "w", encoding="utf-8")
        procs.append(subprocess.Popen(
            [PYTHON, "-B", os.path.abspath(__file__), "worker-counter", path],
            cwd=h.base, stdout=out, stderr=err, stdin=subprocess.DEVNULL))
    codes = []
    for proc in procs:
        try:
            codes.append(proc.wait(timeout=timeout))
        except subprocess.TimeoutExpired:
            proc.kill()
            codes.append("TIMEOUT")
    with open(counter, encoding="utf-8") as handle:
        final = int(handle.read().strip() or "0")
    expected = processes * rounds
    rows = []
    with open(os.path.join(h.base, "counter.journal.jsonl"), encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    record = {
        "case": h.case_id,
        "processes": processes,
        "rounds": rounds,
        "expected": expected,
        "final": final,
        "lost_updates": expected - final,
        "returncodes": codes,
        "lock_acquisitions": sum(r["lock_acquisitions"] for r in rows),
        "status": "PASS" if (final == expected if use_lock else final < expected) else "FAIL",
    }
    print(json.dumps(record, sort_keys=True))
    return 0 if record["status"] == "PASS" else 1


class Holder:
    """Child that takes the lock, sleeps, then dies without unlocking."""

    def __init__(self, path, hold_seconds):
        self.path = path
        self.hold = hold_seconds

    def __call__(self):
        lock = FileLock(self.path, 30.0)
        lock.acquire()
        with open(self.path + ".held", "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        time.sleep(self.hold)
        os._exit(90)


def holder_crash(root):
    h = Harness("F-LK3", root)
    lock_path = os.path.join(h.base, "crash.lock")
    ready = lock_path + ".held"
    proc = subprocess.Popen(
        [PYTHON, "-B", os.path.abspath(__file__), "holder", lock_path, "1.5"],
        cwd=h.base, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL)
    deadline = time.monotonic() + 20
    while not os.path.exists(ready):
        if time.monotonic() > deadline:
            proc.kill()
            print(json.dumps({"case": h.case_id, "status": "FAIL",
                              "detail": "holder never acquired"}, sort_keys=True))
            return 1
        time.sleep(0.01)
    code = proc.wait(timeout=30)
    lock = FileLock(lock_path, 20.0)
    start = time.monotonic()
    lock.acquire()
    waited = time.monotonic() - start
    lock.release()
    ok = waited <= 0.5 and code == 90
    record = {"case": h.case_id, "holder_exit_code": code,
              "parent_wait_seconds": round(waited, 4),
              "lock_file_exists": os.path.exists(lock_path),
              "cleanup_action_required": False,
              "status": "PASS" if ok else "FAIL"}
    print(json.dumps(record, sort_keys=True))
    return 0 if ok else 1


def resume_race(root):
    """No-lock legacy decision: both participants reach the release decision."""
    h = Harness("F-L1-nolock-guard", root)
    a = h.payload("A", mode="legacy", request_budget=100.0,
                  wait_for=h.gate_wait("release_lock_held"))
    h.run(a)
    b = h.payload("B", mode="legacy", request_budget=100.0)
    h.run(b)
    exit_a = h.payload("A-exit", mode="legacy", phase="exit", lease_id=a["lease_id"],
                       wait_for=h.gate_wait("before_resume"))
    proc_a = h.spawn(exit_a, argv=[])
    h.wait_reached("before_resume")
    view_before = h.lease_view()
    exit_b = h.payload("B-exit", mode="legacy", phase="exit", lease_id=b["lease_id"],
                       probe={str(os.getpid()): {"alive": True}})
    res_b = h.run(exit_b, timeout=30)
    h.open_fence("before_resume")
    res_a = h.collect(proc_a)
    counts = h.counts()
    record = {
        "case": h.case_id,
        "state_after_A_release": view_before,
        "A": res_a["envelope"]["result"],
        "B": res_b["envelope"]["result"],
        "counts": counts,
        "status": "RED-CONFIRMED" if counts["resume_calls"] == 2 else "UNEXPECTED",
    }
    print(json.dumps(record, sort_keys=True))
    return 0


def main(argv):
    mode = argv[1]
    if mode == "worker-counter":
        return worker_counter(argv[2])
    if mode == "holder":
        return Holder(argv[2], float(argv[3]))()
    root = argv[2]
    if mode == "counter":
        return stress_counter(root, use_lock=True)
    if mode == "counter-nolock":
        return stress_counter(root, use_lock=False)
    if mode == "holder-crash":
        return holder_crash(root)
    if mode == "resume-race":
        return resume_race(root)
    print(f"unknown mode {mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
