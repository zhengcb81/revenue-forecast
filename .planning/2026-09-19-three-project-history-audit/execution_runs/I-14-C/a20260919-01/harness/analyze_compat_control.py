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
* which nodes failed ONLY on the fixed tree in these particular runs,
* and, crucially, whether each such "T4-only" node is independently PROVEN to fail on the
  pristine tree too.  Four compat runs are far too few samples when the flaky nodes drop in and
  out by chance (measured: the T4-only set was empty in one pass and contained the restart node
  in the next), so the script also reads the dedicated interleaved frequency evidence
  (``--frequency``, produced by ``harness/run_flake_frequency.py``) and checks every T4-only node
  against the T0 failure count of the same test.

Exit 0 when no T4-only node is unproven on T0, 3 otherwise.

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
    parser.add_argument(
        "--frequency",
        default="r5/flake-evidence/frequency-child_without_runtime.json",
        help="interleaved frequency evidence used to prove a T4-only node also fails on T0",
    )
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

    # Independent T0 evidence for nodes that appear only on T4 in these few runs.
    frequency_path = attempt / args.frequency
    frequency_evidence: dict[str, object] = {"path": args.frequency, "available": False}
    t0_proven: dict[str, dict] = {}
    if frequency_path.is_file():
        freq = json.loads(frequency_path.read_text(encoding="utf-8"))
        node_name = freq.get("node_name")
        t0_failed = freq.get("frequency", {}).get("T0", {}).get("failed")
        frequency_evidence = {
            "path": args.frequency,
            "available": True,
            "node_name": node_name,
            "interleaved": freq.get("interleaved", False),
            "pooled": freq.get("frequency"),
            "per_pass": freq.get("frequency_per_pass"),
        }
        if node_name:
            t0_proven[node_name] = {
                "t0_failed_runs": t0_failed,
                "t0_runs": freq.get("frequency", {}).get("T0", {}).get("runs"),
                "evidence": args.frequency,
            }

    t4_only = sorted(set(unions["T4"]) - set(unions["T0"]))
    unproven = [node for node in t4_only if node not in t0_proven
                or not t0_proven[node]["t0_failed_runs"]]
    payload = {
        "script": "harness/analyze_compat_control.py",
        "runs": list(RUNS),
        "per_run_failing_nodes": per_run,
        "per_run_counts": {name: len(nodes) for name, nodes in per_run.items()},
        "union_T0": unions["T0"],
        "union_T4": unions["T4"],
        "unions_equal": unions["T0"] == unions["T4"],
        "t4_union_is_subset_of_t0": not t4_only,
        "occurrences": occurrences,
        "only_on_T4": t4_only,
        "only_on_T0": sorted(set(unions["T0"]) - set(unions["T4"])),
        "t0_evidence_for_t4_only_nodes": t0_proven,
        "unproven_t4_only_nodes": unproven,
        "verdict": ("no card-specific compat failure: every T4 failure also occurs on T0"
                    if not unproven else
                    "UNPROVEN T4-only failures: " + ", ".join(unproven)),
        "note": (
            "The failing COUNT varies run to run (3..5) and the sets differ by the timing nodes "
            "test_child_without_runtime_session_is_terminated_and_restarted and "
            "test_stale_child_heartbeat_is_terminated_and_restarted.  Four compat runs are too few "
            "samples for a ~30% flake, so a node that happens to appear only on T4 in these runs "
            "is checked against the dedicated interleaved frequency evidence before being called "
            "card-specific."
        ),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("per-run counts:", json.dumps(payload["per_run_counts"]))
    print("unions equal:", payload["unions_equal"],
          "| T4 subset of T0:", payload["t4_union_is_subset_of_t0"],
          "| only on T4:", t4_only)
    print("t0 evidence for T4-only nodes:", json.dumps(t0_proven))
    print("verdict:", payload["verdict"])
    return 0 if not unproven else 3


if __name__ == "__main__":
    sys.exit(main())
