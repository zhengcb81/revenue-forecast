"""I-14-E-APPLY: execute the frozen arm plan (oracle.md SS4) in order.

  B1  quiet  fixed   T0,T0b  4x2x2 = 16  -> expect 16/16 green (R2)
  B2  cpu8   fixed   T0,T0b  4x2x2 = 16  -> expect 16/16 green (R1)
  B3  cpu8   mutant-derivation-0.5      4x2x2 = 16 -> expect RED (R4)
  B5  cpu8   mutant-clock (2.0 s floor) 2x2x2 = 8  -> RED => the measurement is load-bearing
  B4  quiet + cpu8  non-vacuity node    2x2x2 each -> expect RED (R3)

Pure orchestrator: each arm is one ``run_bench.py`` invocation, logged to its own file.
The non-ASCII user path is handled by passing argv directly (no shell, no .ps1 literal).
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
PY = ATT / "iso" / "venv" / "Scripts" / "python.exe"
SUITE_FIXED = ATT / "iso" / "T0" / "tests" / "contract" / "test_source_catalog_worker_bootstrap.py"
SUITE_MUT = (ATT / "iso" / "mutant-derivation-0.5" / "tests" / "contract"
             / "test_source_catalog_worker_bootstrap.py")
SUITE_CLOCK = (ATT / "iso" / "mutant-clock" / "tests" / "contract"
               / "test_source_catalog_worker_bootstrap.py")
TREES = f"T0={ATT / 'iso' / 'T0'},T0b={ATT / 'iso' / 'T0b'}"

ARMS = [
    ("B1-fixed-quiet", SUITE_FIXED, "child_without_runtime", "quiet", 4, 2),
    ("B2-fixed-cpu8", SUITE_FIXED, "child_without_runtime", "cpu", 4, 2),
    ("B3-mutant0.5-cpu8", SUITE_MUT, "child_without_runtime", "cpu", 4, 2),
    ("B5-clockmut-cpu8", SUITE_CLOCK, "child_without_runtime", "cpu", 2, 2),
    ("B4-nonvacuity-quiet", SUITE_FIXED, "non_vacuity", "quiet", 2, 2),
    ("B4-nonvacuity-cpu8", SUITE_FIXED, "non_vacuity", "cpu", 2, 2),
]


def main() -> int:
    log_path = ATT / "after" / "bench.log"
    arm_logs = ATT / "after" / "arm-logs"
    arm_logs.mkdir(parents=True, exist_ok=True)
    rc_all = 0
    with log_path.open("a", encoding="utf-8") as log:
        def say(msg: str) -> None:
            line = f"[{time.strftime('%H:%M:%S')}] {msg}"
            print(line, flush=True)
            log.write(line + "\n")
            log.flush()

        say("ARMS START  fixed-parent sha256="
            f"{__import__('hashlib').sha256(SUITE_FIXED.read_bytes()).hexdigest()}")
        for name, suite, node, condition, runs, passes in ARMS:
            out = ATT / "after" / f"bench-{name}.json"
            argv = [str(PY), "-X", "utf8", str(ATT / "harness" / "run_bench.py"),
                    "--python", str(PY), "--suite", str(suite), "--node", node,
                    "--condition", condition, "--trees", TREES,
                    "--runs", str(runs), "--passes", str(passes),
                    "--root", str(Path(__import__("os").environ["TEMP"])
                                   / f"i14eapply-{name}"),
                    "--evidence", str(ATT / "after" / f"bench-captures-{name}"),
                    "--out", str(out)]
            say(f"ARM {name} START node={node} cond={condition} runs={runs} passes={passes}")
            with (arm_logs / f"{name}.log").open("w", encoding="utf-8") as fh:
                proc = subprocess.run(argv, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
                text = proc.stdout.decode("utf-8", "replace")
                fh.write(text)
            tail = [ln for ln in text.splitlines() if ln.strip()][-6:]
            for ln in tail:
                say(f"  {name}| {ln}")
            say(f"ARM {name} EXIT={proc.returncode}")
            if proc.returncode != 0:
                rc_all = 1
            if out.exists():
                payload = json.loads(out.read_text(encoding="utf-8"))
                say(f"ARM {name} TALLY {json.dumps(payload['tally_by_condition'])}")
        say(f"ALL ARMS DONE rc={rc_all}")
    return rc_all


if __name__ == "__main__":
    sys.exit(main())
