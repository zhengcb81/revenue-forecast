"""I-04-C simulation scheduler.

Usage:
  <iso python> sim/scheduler.py list
  <iso python> sim/scheduler.py run <case> [<case> ...] [--root <dir>] [--json <file>]
  <iso python> sim/scheduler.py all [--root <dir>] [--json <file>]

Every case gets its own directory under <root>/<case>/.  Raw per-process stdout
and stderr, the journal, the refcount/owner files and the worker action log stay
on disk as evidence.  Exit code 0 only when every check of every selected case
passed.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPT = os.path.dirname(HERE)
for path in (HERE,):
    if path not in sys.path:
        sys.path.insert(0, path)

import cases_core  # noqa: E402
import cases_legacy  # noqa: E402
import cases_ownership  # noqa: E402
import stress  # noqa: E402

CASES = {}
CASES.update(cases_core.CASES)
CASES.update(cases_ownership.CASES)
CASES.update(cases_legacy.CASES)


def run_stress(name, root):
    if name == "F-LK1":
        return stress.stress_counter(root, use_lock=True)
    if name == "F-LK2":
        return stress.stress_counter(root, use_lock=False)
    if name == "F-LK3":
        return stress.holder_crash(root)
    if name == "F-L1-nolock-guard":
        return stress.resume_race(root)
    raise KeyError(name)


ALL = list(CASES) + ["F-LK1", "F-LK2", "F-LK3", "F-L1-nolock-guard"]


def main(argv):
    if len(argv) >= 2 and argv[1] == "list":
        for name in ALL:
            print(name)
        return 0
    if len(argv) < 2:
        print(__doc__)
        return 2
    action = argv[1]
    rest = argv[2:]
    names = []
    root = os.path.join(ATTEMPT, "evidence", "run")
    out_json = None
    index = 0
    while index < len(rest):
        token = rest[index]
        if token == "--root":
            root = rest[index + 1]
            index += 2
            continue
        if token == "--json":
            out_json = rest[index + 1]
            index += 2
            continue
        names.append(token)
        index += 1
    if action == "all":
        names = ALL
    if not names:
        print("no cases selected", file=sys.stderr)
        return 2
    os.makedirs(root, exist_ok=True)
    summary = []
    started = time.time()
    for name in names:
        print(f"\n--- {name} ---")
        case_started = time.time()
        # Every run starts from a clean case directory: journals are appended, so
        # reusing a directory would mix evidence from two runs (START_HERE: one
        # command-run-id per invocation, raw state saved before the next command).
        shutil.rmtree(os.path.join(root, name), ignore_errors=True)
        try:
            if name in CASES:
                code = CASES[name](root, verbose="--verbose" in argv)
            else:
                code = run_stress(name, root)
        except Exception as exc:  # harness error is a FAIL, never a silent skip
            import traceback

            traceback.print_exc()
            print(json.dumps({"case": name, "status": "HARNESS-ERROR",
                              "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True))
            code = 3
        summary.append({"case": name, "exit": code,
                        "seconds": round(time.time() - case_started, 3)})
    payload = {"cases": summary, "total_seconds": round(time.time() - started, 3),
               "failures": [row["case"] for row in summary if row["exit"] != 0]}
    print("\n=== SUMMARY ===")
    print(json.dumps(payload, sort_keys=True))
    if out_json:
        os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=1, sort_keys=True)
    return 0 if not payload["failures"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
