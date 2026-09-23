"""I-07-D writer process (adapted from the I-09-C writer): runs the REAL
publication code path (``revenue_forecast.main()`` with CLI argv) in a
separate OS process, with the fault harness armed.

Sequence (evidence is written incrementally so an interruption loses at most
one file):
  1. register this PID in the run's new_run manifest: pid_<pid>.json
     (the orchestrator may kill ONLY PIDs registered here)
  2. install hooks (only when --fault is not "none")
  3. run revenue_forecast.main()
  4. on normal exit write writer_exited_<pid>.json {rc}
     -> its ABSENCE after a kill proves the process died for real
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import setup_paths, write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="")
    parser.add_argument("--markdown", default="")
    parser.add_argument("--fault", default="none")
    parser.add_argument("--label", default="")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    pid = os.getpid()

    # 1. PID manifest registration — before ANY publication work
    write_json(
        run_dir / f"pid_{pid}.json",
        {
            "pid": pid,
            "parent_pid": os.getppid(),
            "parent_note": "Windows venv launcher starts a child interpreter: "
                           "os.getpid() is the process running this code; "
                           "getppid() is the launcher Popen.pid. BOTH are "
                           "registered here, so killing either stays inside "
                           "the new_run manifest.",
            "label": args.label,
            "fault": args.fault,
            "input": args.input,
            "output": args.output,
            "markdown": args.markdown,
            "argv_original": sys.argv,
            "argv": sys.argv,
            "cwd": os.getcwd(),
            "registered_at": time.time(),
            "registry_env": os.environ.get("REVENUE_PUBLICATION_REGISTRY"),
        },
    )

    setup_paths()
    import revenue_forecast as RF  # noqa: E402
    import d_hooks  # noqa: E402

    hook_info = {"installed": False, "armed": None}
    if args.fault and args.fault != "none":
        hook_info = d_hooks.install(args.fault, run_dir)

    argv = ["revenue_forecast.py", args.input]
    if args.output:
        argv += ["--output", args.output]
    if args.markdown:
        argv += ["--markdown", args.markdown]
    sys.argv = argv

    write_json(
        run_dir / f"writer_start_{pid}.json",
        {"pid": pid, "argv": argv, "fault": args.fault, "hooks": hook_info, "t": time.time()},
    )

    rc = RF.main()

    write_json(
        run_dir / f"writer_exited_{pid}.json",
        {"pid": pid, "rc": rc, "fault": args.fault, "t": time.time(),
         "note": "normal exit record — must be ABSENT when the process was hard-killed"},
    )
    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())
