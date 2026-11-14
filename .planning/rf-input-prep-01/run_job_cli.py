"""Run one rf_job_cli route and persist exact UTF-8 stdout/stderr and exit code.

Usage:
  python run_job_cli.py <label> -- <cli argv ...>

Writes evidence/<label>.stdout.json, evidence/<label>.stderr.txt and
evidence/<label>.exit.txt; prints the exit code.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[1]
EVIDENCE = ROOT / "evidence"


def main(argv: list[str]) -> int:
    if "--" not in argv:
        print("usage: run_job_cli.py <label> -- <cli argv>", file=sys.stderr)
        return 2
    split = argv.index("--")
    label = argv[0]
    cli_argv = argv[split + 1:]
    stdin_bytes = None
    if "--stdin-file" in cli_argv:
        position = cli_argv.index("--stdin-file")
        stdin_path = Path(cli_argv[position + 1])
        stdin_bytes = stdin_path.read_bytes()
        cli_argv = cli_argv[:position] + cli_argv[position + 2:]
    command = [sys.executable, "-B", str(WORKTREE / "scripts" / "rf_job_cli.py"), *cli_argv]
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(command, capture_output=True, cwd=str(WORKTREE), input=stdin_bytes)
    (EVIDENCE / f"{label}.stdout.json").write_bytes(proc.stdout)
    (EVIDENCE / f"{label}.stderr.txt").write_bytes(proc.stderr)
    (EVIDENCE / f"{label}.exit.txt").write_text(f"{proc.returncode}\n", encoding="utf-8")
    (EVIDENCE / f"{label}.command.json").write_text(
        json.dumps({"argv": command, "cwd": str(WORKTREE)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"label": label, "exit_code": proc.returncode,
                      "stdout_bytes": len(proc.stdout), "stderr_bytes": len(proc.stderr)}))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
