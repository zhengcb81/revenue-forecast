"""Static proof for r2 F-I04C-07 (ADR-11) and F-I04C-03 wording.

Reads sim/kernel.py as text/AST and asserts the structural facts the frozen
protocol text claims.  This is a STATIC check (it proves the shape of the code,
not a runtime property); it is reported next to the runtime F-L2e pair.

Checks:
  S1  run_protocol acquires the lease lock BEFORE its first worker_status call,
      and has exactly ONE worker_status call site.
  S2  protocol_paused_branch and _fresh_cycle_locked/_takeover_cycle take no lock
      (the caller holds it) -- i.e. no lease_lock/FileLock acquisition inside them.
  S3  run_protocol_stale_v1 exists, is never called from the default path, and
      reads the status BEFORE acquiring the lock (the deliberately wrong shape).
  S4  every protocol function name appears exactly once at module level.
"""

from __future__ import annotations

import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KERNEL = os.path.join(HERE, "kernel.py")

LOCK_CALLS = {"lease_lock", "FileLock"}


def call_name(node):
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def find_functions(tree):
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def first_line_with(nodes, names):
    hits = []
    for node in ast.walk(nodes):
        if isinstance(node, ast.Call) and call_name(node) in names:
            hits.append(node.lineno)
    return min(hits) if hits else None


def has_call(nodes, names):
    return first_line_with(nodes, names) is not None


def main():
    with open(KERNEL, "r", encoding="utf-8") as handle:
        source = handle.read()
    tree = ast.parse(source)
    functions = find_functions(tree)
    checks = []

    def check(label, ok, detail=""):
        checks.append({"check": label, "result": "PASS" if ok else "FAIL",
                       "detail": detail})

    # S1
    run = functions.get("run_protocol")
    if run is None:
        check("S1 run_protocol exists", False)
    else:
        lock_line = first_line_with(run, LOCK_CALLS)
        status_lines = [n.lineno for n in ast.walk(run)
                        if isinstance(n, ast.Call) and call_name(n) == "worker_status"]
        check("S1 run_protocol acquires the lease lock before any worker_status call",
              lock_line is not None and status_lines and min(status_lines) > lock_line,
              f"lock_line={lock_line} status_lines={status_lines}")
        check("S1 exactly one worker_status call site in run_protocol",
              len(status_lines) == 1, f"status_lines={status_lines}")

    # S2
    for name in ("protocol_paused_branch", "_takeover_cycle", "_fresh_cycle_locked",
                 "_withdraw_after_failed_pause"):
        node = functions.get(name)
        check(f"S2 {name} takes no lock (caller holds it)",
              node is not None and not has_call(node, LOCK_CALLS),
              "" if node is None else f"lines={node.lineno}-{node.end_lineno}")

    # S3
    stale = functions.get("run_protocol_stale_v1")
    if stale is None:
        check("S3 run_protocol_stale_v1 exists (the deliberately wrong shape)", False)
    else:
        lock_line = first_line_with(stale, LOCK_CALLS)
        status_line = first_line_with(stale, {"worker_status"})
        check("S3 the stale variant reads the status BEFORE taking the lock",
              lock_line is not None and status_line is not None and status_line < lock_line,
              f"status_line={status_line} lock_line={lock_line}")
        default_calls = [n.lineno for n in ast.walk(run)
                         if isinstance(n, ast.Call)
                         and call_name(n) == "run_protocol_stale_v1"] if run else []
        check("S3 the default path never calls the stale variant",
              not default_calls, f"call_lines={default_calls}")

    # S4
    names = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    check("S4 no duplicate module-level function definitions",
          not duplicates, f"duplicates={duplicates}")

    failed = [c for c in checks if c["result"] == "FAIL"]
    import json
    print(json.dumps({"case": "STATIC-ADR11", "checks": checks,
                      "status": "PASS" if not failed else "FAIL",
                      "failed": len(failed)}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
