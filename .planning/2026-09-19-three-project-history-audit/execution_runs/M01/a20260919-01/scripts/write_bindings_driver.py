"""Driver: read card_specs.json and run write_binding.py for every card.

Avoids all shell quoting problems by keeping the spec on disk.

ASCII-only stdout.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    specs_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "scripts", "card_specs.json")
    specs_path = os.path.abspath(os.path.join(here, "card_specs.json"))
    with open(specs_path, "r", encoding="utf-8") as handle:
        specs = json.load(handle)["cards"]

    plan = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))
    print("plan root:", plan)
    failures = []
    for spec in specs:
        attempt = os.path.join(plan, "execution_runs", spec["card"], "a20260919-01")
        py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
        script = os.path.join(attempt, "scripts", "write_binding.py")
        if not os.path.exists(py):
            failures.append((spec["card"], "missing interpreter"))
            print(spec["card"], "SKIP missing interpreter", py)
            continue
        argv = [py, "-X", "utf8", "-B", script,
                "--card", spec["card"], "--model", spec["model"], "--formula", spec["formula"],
                "--required", spec["required"], "--optional", spec["optional"],
                "--defaults", json.dumps(spec["defaults"]),
                "--driver-bounds", spec["driver_bounds"],
                "--probe-keys", json.dumps(spec["probe_keys"]),
                "--probe-note", spec["probe_note"]]
        proc = subprocess.run(argv, cwd=attempt, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Node-free, plain Popen-free subprocess is fine here; capture and report.
        out = proc.stdout.decode("utf-8", "replace").strip().splitlines()
        err = proc.stderr.decode("utf-8", "replace").strip()
        print(spec["card"], "raw_rc=", proc.returncode, "|", out[-1] if out else "", "|", err[:200])
        if proc.returncode != 0:
            failures.append((spec["card"], err[:200]))
    print("failures:", failures)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
