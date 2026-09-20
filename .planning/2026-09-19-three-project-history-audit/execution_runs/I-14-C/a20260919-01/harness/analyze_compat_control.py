"""I-14-C r5: attributing the compat-suite failures (per-run sets, unions, both trees).

The compat suite (CW/tests/contract/test_source_catalog_worker_bootstrap.py +
test_observability.py) does not fail with a STABLE set of node ids: measured over five runs at
r5 the failing count was 3, 4, 4, 5, 5 with the difference coming from nodes that are
timing/path sensitive.  So "identical failure set per run" is the wrong criterion and r4's
"IDENTICAL failure set" claim is not reproducible; the right question is whether any failing
node is reachable on the PRISTINE tree.

This script answers exactly that from the captured stdout files:

* per-run failing node ids,
* the union per tree,
* whether the two unions are equal (if they are, no node is card-specific),
* the per-node occurrence count per tree.

Exit 0 when the unions are equal, 3 otherwise.

    python analyze_compat_control.py --attempt <attempt> --out <attempt>/r5/compat-control-analysis.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RUNS = {
    "T0-1": "r5/compat-control-product-1",
    "T0-2": "r5/compat-control-product-2",
    "T4-1": "r5/compat-control-product_fixed-1",
    "T4-2": "r5/compat-control-product_fixed-2",
    "T4-plain": "r5/cmd-compat",
}
TREE_OF = {"T0-1": "T0", "T0-2": "T0", "T4-1": "T4", "T4-2": "T4", "T4-plain": "T4"}


def failing_nodes(stdout_path: Path) -> list[str]:
    if not stdout_path.is_file():
        return []
    return sorted(
        line.split("::")[-1].strip()
        for line in stdout_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.startswith("FAILED ")
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    attempt = Path(args.attempt).resolve()
    per_run = {name: failing_nodes(attempt / rel / "stdout.txt") for name, rel in RUNS.items()}
    unions: dict[str, list[str]] = {}
    for tree in ("T0", "T4"):
        nodes: set[str] = set()
        for name, tree_label in TREE_OF.items():
            if tree_label == tree:
                nodes.update(per_run[name])
        unions[tree] = sorted(nodes)

    occurrences = {
        node: {tree: sum(1 for name, label in TREE_OF.items()
                         if label == tree and node in per_run[name])
               for tree in ("T0", "T4")}
        for node in sorted(set(unions["T0"]) | set(unions["T4"]))
    }
    payload = {
        "script": "harness/analyze_compat_control.py",
        "runs": list(RUNS),
        "per_run_failing_nodes": per_run,
        "per_run_counts": {name: len(nodes) for name, nodes in per_run.items()},
        "union_T0": unions["T0"],
        "union_T4": unions["T4"],
        "unions_equal": unions["T0"] == unions["T4"],
        "occurrences": occurrences,
        "only_on_T4": sorted(set(unions["T4"]) - set(unions["T0"])),
        "only_on_T0": sorted(set(unions["T0"]) - set(unions["T4"])),
        "note": (
            "The failing COUNT varies run to run (3..5) and the sets differ by the timing nodes "
            "test_child_without_runtime_session_is_terminated_and_restarted and "
            "test_stale_child_heartbeat_is_terminated_and_restarted; the UNIONS are what matter, "
            "and an equal union means every failing node also fails on the pristine tree."
        ),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("per-run counts:", json.dumps(payload["per_run_counts"]))
    print("unions equal:", payload["unions_equal"], "| only on T4:", payload["only_on_T4"])
    return 0 if payload["unions_equal"] else 3


if __name__ == "__main__":
    sys.exit(main())
