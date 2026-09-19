"""I-04-A design measurement 1/2: epsilon of THIS host's process scheduling boundary.

The card requires epsilon to come from a measurement of the run environment (action 4), not
from a guess and not to be loosened after a future test fails.  This measures, on this host,
two overshoot sources that any real-process timing oracle in I-04-B/E will face:

  A. interpreter startup: elapsed of `python -c "pass"` around subprocess.run
  B. controlled sleep: elapsed of `python -c "import time;time.sleep(0.25)"` minus 0.25

Both use the attempt's iso venv python, exactly like the future bound commands.
Output: design_measurements/epsilon_raw.json + a p95-based proposal printed to stdout.
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "design_measurements" / "epsilon_raw.json"
PYTHON = sys.executable  # the iso venv python this script is launched with
N = 30


def spawn(code: str) -> float:
    start = time.perf_counter()
    proc = subprocess.run([PYTHON, "-X", "utf8", "-B", "-c", code],
                          capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        raise SystemExit(f"spawn failed rc={proc.returncode}: {proc.stderr[:200]}")
    return elapsed


def summarise(values: list[float]) -> dict:
    return {
        "n": len(values),
        "min": round(min(values), 4),
        "median": round(statistics.median(values), 4),
        "p95": round(sorted(values)[int(0.95 * (len(values) - 1))], 4),
        "max": round(max(values), 4),
    }


def main() -> int:
    startup = [spawn("pass") for _ in range(N)]
    sleep_task = [spawn("import time; time.sleep(0.25)") - 0.25 for _ in range(N)]
    proposal = max(summarise(startup)["p95"], summarise(sleep_task)["p95"])
    epsilon = round(min(2.0, proposal * 2), 2)  # 2x headroom, hard cap 2 s
    record = {
        "artifact": "I-04-A epsilon measurement",
        "host_note": "Windows; subprocess.run wall time around the iso venv python",
        "interpreter": PYTHON,
        "n_per_case": N,
        "startup_overshoot_s": summarise(startup),
        "sleep_overshift_over_0_25s_s": summarise(sleep_task),
        "epsilon_proposal_s": epsilon,
        "epsilon_rule": ("epsilon = 2 x max(p95 startup, p95 sleep overshoot), hard-capped at 2 s; "
                         "once signed it must not be loosened because a later test failed"),
        "ran_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
