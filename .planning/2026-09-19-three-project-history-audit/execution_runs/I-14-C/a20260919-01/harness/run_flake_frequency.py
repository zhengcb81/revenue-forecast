"""I-14-C r5: frequency estimate for the one compat node that showed a timing asymmetry.

Why this exists (honesty requirement on F-I14C-R4-03): with the deep attempt-path basetemp the
node fails identically on BOTH trees (path length, ``WinError 206``).  With a short ``%TEMP%``
basetemp the node passes on the pristine tree but failed on the fixed tree in 2 of 3 runs with
``assert 3 == 2`` on ``child_started`` - i.e. an extra supervisor restart.  A 2-of-3 asymmetry
is not enough to attribute anything, so this script measures the frequency on both trees with
the same node, same basetemp root, same environment, run after run.

One node, N runs per tree per pass, INTERLEAVED (one T0 run, one T4 run, repeating) so that a
change in machine load mid-pass cannot masquerade as a tree difference, evidence per run, and a
per-pass plus pooled frequency table.  Exit 0 always (this is an evidence collector, not a
verdict).

Why interleaving matters here: the first version of this script ran all 12 T0 runs and then all
12 T4 runs and produced T0 6/12 vs T4 5/12; the same script re-run minutes later produced
T0 0/12 vs T4 7/12.  Neither ordering-controlled number is safe to report as a tree difference.

    python run_flake_frequency.py --attempt <attempt> --python <iso-python> \
        --repo <company-wiki> --node child_without_runtime --runs 12 --passes 2 \
        --basetemp-root %TEMP%/i14c-flake-freq --out <attempt>/r5/flake-evidence/frequency.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SUITE = "tests/contract/test_source_catalog_worker_bootstrap.py"
NODES = {
    "child_without_runtime": "test_child_without_runtime_session_is_terminated_and_restarted",
    "logon_wrapper_quoted": "test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths",
}
TREES = {"T0": "product", "T4": "product_fixed"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--node", required=True, choices=sorted(NODES))
    parser.add_argument("--runs", type=int, default=12)
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--basetemp-root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    attempt = Path(args.attempt).resolve()
    repo = Path(args.repo).resolve()
    node_name = NODES[args.node]
    base_root = Path(os.path.expandvars(args.basetemp_root))
    if base_root.exists():
        shutil.rmtree(base_root, ignore_errors=True)
    base_root.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    # INTERLEAVED on purpose: running all T0 runs and then all T4 runs would let a change in
    # machine load mid-pass masquerade as a tree difference.  One run of each tree, alternating,
    # per index, and the whole block repeated --passes times.
    for pass_index in range(1, args.passes + 1):
        for run in range(1, args.runs + 1):
            for tree_label, tree in TREES.items():
                src = attempt / "iso" / tree / "src"
                run_dir = base_root / f"p{pass_index}-{tree_label}-{args.node}-{run}"
                run_dir.mkdir(parents=True, exist_ok=True)
                proc = subprocess.run(
                    [args.python, "-X", "utf8", "-B", "-m", "pytest",
                     "-p", "no:cacheprovider", "--basetemp", str(run_dir / "pytest"),
                     "-q", f"{repo / SUITE}::{node_name}"],
                    cwd=str(run_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
                         "PYTHONPATH": str(src),
                         "PATH": os.environ.get("PATH", ""),
                         "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
                         "TEMP": os.environ.get("TEMP", ""),
                         "TMP": os.environ.get("TMP", "")},
                )
                text = proc.stdout.decode("utf-8", "replace")
                verdict = ("passed" if " 1 passed" in text or "1 passed" in text
                           else "failed" if "1 failed" in text else "unknown")
                assertion = ""
                for line in text.splitlines():
                    if line.startswith("E   AssertionError") or line.startswith("E   Failed"):
                        assertion = line.strip()[:200]
                        break
                (run_dir / "stdout.txt").write_text(text, encoding="utf-8")
                results.append({
                    "pass": pass_index,
                    "tree": tree_label,
                    "run": run,
                    "cwd": str(run_dir),
                    "returncode": proc.returncode,
                    "verdict": verdict,
                    "assertion": assertion,
                    "tail": text.strip().splitlines()[-1] if text.strip() else "",
                })
                print(f"pass{pass_index} {tree_label} run{run} rc={proc.returncode} {verdict} "
                      f"{assertion}", flush=True)

    def tally(rows: list[dict]) -> dict:
        return {
            "runs": len(rows),
            "failed": sum(1 for r in rows if r["verdict"] == "failed"),
            "passed": sum(1 for r in rows if r["verdict"] == "passed"),
            "unknown": sum(1 for r in rows if r["verdict"] == "unknown"),
        }

    frequency = {label: tally([r for r in results if r["tree"] == label]) for label in TREES}
    per_pass = {
        f"pass{index}": {
            label: tally([r for r in results if r["tree"] == label and r["pass"] == index])
            for label in TREES
        }
        for index in range(1, args.passes + 1)
    }
    payload = {
        "script": "harness/run_flake_frequency.py",
        "node": args.node,
        "node_name": node_name,
        "basetemp_root": str(base_root),
        "interleaved": True,
        "tree_src": {label: str(attempt / "iso" / tree / "src") for label, tree in TREES.items()},
        "results": results,
        "frequency": frequency,
        "frequency_per_pass": per_pass,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    print("frequency:", json.dumps(frequency))
    print("per pass:", json.dumps(per_pass))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
