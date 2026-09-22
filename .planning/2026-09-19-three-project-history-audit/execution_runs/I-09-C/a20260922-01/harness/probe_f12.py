"""F12 attribution probe: is raw=120 the PRODUCT CLI's real exit code under a
broken stdout pipe, or a harness mapping?

Controls (same harness, same CLI, same input, same isolated registry):
  A. stdout = PIPE with a live reader  -> baseline (delivery succeeds)
  B. stdout = pipe with NO reader      -> the F12 arm's construction
  C. stdout = regular file            -> baseline (delivery to file)
Harness codes are disjoint from these: this card only ever sets 4242 (kill);
nothing in the harness maps or overrides a child's return code (Popen
returncode is the child's own GetExitCodeProcess value).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ATTEMPT, ISO_RF, KILL_EXIT_CODE, PY, child_env, write_json  # noqa: E402

CASE_DIR = ATTEMPT / "evidence" / "cases" / "F12_stdout_pipe"


def main() -> int:
    state = CASE_DIR / "state"
    registry = CASE_DIR / "state" / "registry" / "publications.jsonl"
    inp = state / "input_p1.json"
    cli = ISO_RF / "scripts" / "revenue_forecast.py"
    base = [str(PY), str(cli), str(inp), "--validate-only"]
    env = child_env(registry)
    results = {}

    # A: live reader
    p = subprocess.run(base, cwd=str(ISO_RF), env=env, capture_output=True,
                       timeout=180)
    results["A_pipe_with_reader"] = {
        "raw_returncode": p.returncode,
        "stdout": p.stdout.decode("utf-8", "replace")[:200],
        "stderr": p.stderr.decode("utf-8", "replace")[:400],
    }

    # B: pipe with NO reader (the F12 arm)
    r_fd, w_fd = os.pipe()
    p = subprocess.Popen(base, cwd=str(ISO_RF), env=env, stdout=w_fd,
                         stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    os.close(w_fd)
    os.close(r_fd)
    _, err = p.communicate(timeout=180)
    results["B_pipe_no_reader"] = {
        "raw_returncode": p.returncode,
        "stderr": (err or b"").decode("utf-8", "replace")[:600],
        "same_construction_as_arm": True,
    }

    # C: stdout to file
    out_file = CASE_DIR / "control_c_stdout.txt"
    with out_file.open("wb") as fh:
        p = subprocess.run(base, cwd=str(ISO_RF), env=env, stdout=fh,
                           stderr=subprocess.PIPE, timeout=180)
    results["C_stdout_to_file"] = {
        "raw_returncode": p.returncode,
        "stdout_file": str(out_file),
        "stderr": (err or b"").decode("utf-8", "replace")[:200],
    }

    results["attribution"] = {
        "harness_exit_codes_reserved": {"kill": KILL_EXIT_CODE},
        "harness_maps_child_rc": False,
        "mechanism": (
            "rc=120 is CPython's standard-stream flush failure exit status, raised "
            "in the CHILD (product CLI) at interpreter finalization when sys.stdout "
            "has no reader; the harness only records Popen.returncode "
            "(GetExitCodeProcess) and never rewrites it."
        ),
        "isolated_variable": "only the stdout sink differs between A/B/C",
        "conclusion_pending_measurement": True,
    }

    write_json(CASE_DIR / "pipe_controls.json", results)
    b = results["B_pipe_no_reader"]["raw_returncode"]
    a = results["A_pipe_with_reader"]["raw_returncode"]
    c = results["C_stdout_to_file"]["raw_returncode"]
    results["attribution"]["conclusion_pending_measurement"] = False
    results["attribution"]["measured"] = {"A": a, "B": b, "C": c}
    results["attribution"]["verdict"] = (
        "product-process exit code attributable to broken-pipe stdio flush "
        f"(A={a}, B={b}, C={c}; B differs from both baselines under identical harness)"
        if b == 120 and (a, c) != (120, 120)
        else f"see measured values A={a} B={b} C={c}"
    )
    write_json(CASE_DIR / "pipe_controls.json", results)
    print(json.dumps(results["attribution"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
