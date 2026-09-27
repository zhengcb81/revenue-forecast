"""I-14-E-TESTSIDE: manual supervisor probe (diagnostic, NOT a band arm).

Builds the same fake launcher project the product test builds (by importing the
product test module read-only) and runs the real ``source_catalog_worker.ps1``
the way the product test does, outside pytest, so a failure can be attributed to
(pytest context) vs (sandbox/OS environment).

Usage:
  python manual_supervisor_probe.py --python <venv python> --repo <iso> --runs 1
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SUITE = "tests/contract/test_source_catalog_worker_bootstrap.py"


def build_fixture(repo: Path):
    spec = importlib.util.spec_from_file_location("cw_bootstrap_test", repo / SUITE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    module = build_fixture(repo)
    root = Path(args.root)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    rows = []
    for index in range(1, args.runs + 1):
        project = module._prepare_fake_launcher_project(
            root / f"run{index}",
            [{"sleep_seconds": 5, "exit_code": 0}, {"exit_code": 0}],
        )
        command = module._real_worker_launcher_command(
            project,
            worker_hang_timeout_seconds=0.5,
            child_poll_milliseconds=100,
        )
        t0 = time.perf_counter()
        completed = subprocess.run(
            command, cwd=str(project), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=60, check=False)
        wall = time.perf_counter() - t0
        events = module._launcher_events(project)
        row = {
            "run": index, "returncode": completed.returncode,
            "wall_seconds": round(wall, 3),
            "stderr": (completed.stderr or "")[-800:],
            "stdout": (completed.stdout or "")[-400:],
            "statuses": [e.get("status") for e in events],
            "messages": [f"{e.get('status')}|{e.get('reason')}|{(e.get('message') or '')[:200]}"
                         for e in events],
            "count_file": (project / ".source_catalog" / "fake_worker_count.txt").exists(),
        }
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    out = root / "probe.json"
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print("out:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
