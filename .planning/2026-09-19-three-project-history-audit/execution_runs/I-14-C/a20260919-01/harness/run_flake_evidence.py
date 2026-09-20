"""I-14-C r5: land the flake checks with REAL captured output.

F-I14C-R4-03: the r4 `r4/flake-*` directories contained only pytest fixture artefacts, so the
"3/3 passed on both trees" claim in handoff.json could not be verified by the reviewer.  This
runner writes stdout, the raw return code and a per-node verdict for every run, and produces
`summary.json`.

    python run_flake_evidence.py --attempt <attempt> --python <iso venv python> --repo <CW>
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

NODES = {
    "child_without_runtime": "test_child_without_runtime_session_is_terminated_and_restarted",
    "logon_wrapper_quoted": "test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths",
}
SUITE = "tests/contract/test_source_catalog_worker_bootstrap.py"
TREES = {"T0": "product", "T4": "product_fixed"}
RUNS = (1, 2, 3)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args(argv)

    attempt = Path(args.attempt).resolve()
    repo = Path(args.repo).resolve()
    out_root = attempt / "r5" / "flake-evidence"
    out_root.mkdir(parents=True, exist_ok=True)

    summary: dict = {"nodes": NODES, "trees": TREES, "runs": list(RUNS), "results": []}
    for tree_label, tree in TREES.items():
        src = attempt / "iso" / tree / "src"
        for node_id, node_name in NODES.items():
            for run in RUNS:
                run_dir = out_root / f"{tree_label}-{node_id}-{run}"
                run_dir.mkdir(parents=True, exist_ok=True)
                proc = subprocess.run(
                    [args.python, "-X", "utf8", "-B", "-m", "pytest",
                     "-p", "no:cacheprovider", "--basetemp", str(run_dir / "pytest"),
                     "-q", f"{repo / SUITE}::{node_name}"],
                    cwd=str(run_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
                         "PYTHONPATH": str(src),
                         "PATH": __import__("os").environ.get("PATH", ""),
                         "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", ""),
                         "TEMP": __import__("os").environ.get("TEMP", ""),
                         "TMP": __import__("os").environ.get("TMP", "")},
                )
                text = proc.stdout.decode("utf-8", "replace")
                (run_dir / "stdout.txt").write_text(text, encoding="utf-8")
                (run_dir / "returncode.txt").write_text(str(proc.returncode), encoding="utf-8")
                verdict = ("passed" if " 1 passed" in text or "1 passed" in text
                           else "failed" if "1 failed" in text else "unknown")
                summary["results"].append({
                    "tree": tree_label,
                    "node": node_id,
                    "run": run,
                    "cwd": str(run_dir),
                    "cwd_len": len(str(run_dir)),
                    "returncode": proc.returncode,
                    "verdict": verdict,
                    "tail": text.strip().splitlines()[-1] if text.strip() else "",
                    "evidence": str(run_dir.relative_to(attempt)),
                })
    (out_root / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True),
                                           encoding="utf-8")
    for row in summary["results"]:
        print(f"{row['tree']}/{row['node']} run{row['run']} rc={row['returncode']} "
              f"{row['verdict']} cwd_len={row['cwd_len']}")
    print("summary:", out_root / "summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
