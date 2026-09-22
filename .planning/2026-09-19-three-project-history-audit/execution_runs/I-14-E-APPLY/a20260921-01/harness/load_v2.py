"""I-14-E-APPLY campaign v2 load generator (oracle-addendum-C, section C5).

Differences from v1's ``harness/load.py`` (which is left untouched as v1 history):

  * burners are **self-expiring**: each busy loop exits on its own after
    ``expiry_seconds`` (= guard + 60).  If the driver is hard-killed mid-run
    (the v1 campaign died with STATUS_CONTROL_C_EXIT and its ``finally`` never
    ran), at most ``expiry_seconds`` later the orphans disappear by themselves,
    so an interrupted campaign cannot leave the machine loaded for the rest of
    the day.
  * only the two shapes campaign v2 uses: ``quiet`` (no load) and ``cpu``
    (K busy loops, same arithmetic as I-14-E / v1: ``x = (x + 1) % 1000003``).

Nothing here touches the product trees or the iso trees.
"""

from __future__ import annotations

import subprocess
import sys
import time

BURNER_SRC = """
import time
x = 0
end = time.time() + {seconds:.1f}
while time.time() < end:
    x = (x + 1) % 1000003
"""


class Load:
    def __init__(self, kind: str, burners: int, expiry_seconds: float) -> None:
        if kind not in ("quiet", "cpu"):
            raise ValueError(f"unsupported load kind for campaign v2: {kind!r}")
        self.kind = kind
        self.burners = burners if kind == "cpu" else 0
        self.expiry_seconds = float(expiry_seconds)
        self.procs: list[subprocess.Popen] = []

    def start(self) -> None:
        if self.kind == "quiet":
            return
        src = BURNER_SRC.format(seconds=self.expiry_seconds)
        for _ in range(self.burners):
            self.procs.append(subprocess.Popen(
                [sys.executable, "-c", src],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        # let the burners reach steady state before the measured run starts
        time.sleep(1.5)

    def describe(self) -> dict:
        return {"kind": self.kind, "burners": self.burners,
                "burner_expiry_seconds": self.expiry_seconds,
                "warmup_seconds": 1.5 if self.kind == "cpu" else 0.0,
                "self_expiring": True}

    def stop(self) -> None:
        for proc in self.procs:
            if proc.poll() is None:
                proc.kill()
        for proc in self.procs:
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        self.procs = []
