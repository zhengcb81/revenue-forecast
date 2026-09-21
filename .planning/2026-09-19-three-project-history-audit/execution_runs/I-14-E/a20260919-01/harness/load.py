"""I-14-E: load generators used by the measurement runs.

Two load shapes, because the two candidate resource contentions differ:
  * ``cpu``   - K busy-loop processes (scheduler contention on 12 logical CPUs)
  * ``spawn`` - a few busy loops PLUS a continuous storm of short-lived python
                processes (process-creation / disk contention; this is the shape
                the I-14-F notes blame: "concurrent pytest campaigns")

The generators are plain child processes owned by the measurement driver; they
are terminated in ``Load.stop()``.  Nothing here touches the product trees.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

BURNER_SRC = "x=0\nwhile True:\n    x=(x+1)%1000003\n"

SPAWNER_SRC = """
import subprocess, sys, time
py = sys.executable
end = time.time() + float(sys.argv[1])
n = 0
while time.time() < end:
    batch = [subprocess.Popen([py, "-c", "pass"],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL) for _ in range(4)]
    for p in batch:
        p.wait()
    n += len(batch)
print("spawned", n)
"""


class Load:
    def __init__(self, kind: str, burners: int, seconds: float) -> None:
        self.kind = kind
        self.burners = burners
        self.seconds = seconds
        self.procs: list[subprocess.Popen] = []
        self.spawn_log = None

    def start(self) -> None:
        if self.kind == "quiet":
            return
        env = dict(os.environ)
        for _ in range(self.burners):
            self.procs.append(subprocess.Popen(
                [sys.executable, "-c", BURNER_SRC], env=env,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        if self.kind == "spawn":
            self.spawn_log = open(os.path.join(os.environ.get("TEMP", "."),
                                               "i14e-spawner.log"), "ab")
            self.procs.append(subprocess.Popen(
                [sys.executable, "-c", SPAWNER_SRC, str(self.seconds)], env=env,
                stdout=self.spawn_log, stderr=subprocess.STDOUT))
        # let the burners actually reach steady state before the first run
        time.sleep(1.5)

    def describe(self) -> dict:
        return {"kind": self.kind, "burners": self.burners if self.kind != "quiet" else 0,
                "spawn_storm": self.kind == "spawn", "seconds": self.seconds}

    def stop(self) -> None:
        for proc in self.procs:
            if proc.poll() is None:
                proc.kill()
        for proc in self.procs:
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        if self.spawn_log is not None:
            self.spawn_log.close()
        self.procs = []
