"""I-14-E-APPLY: build the MUTANT tree (criterion R4) and the timing-probe tree.

Two independent mutations of the applied fix, each written into its own tree so the
mutant is byte-comparable with the fixed tree:

  mutant_derivation   replace ``hang_timeout_seconds = _derive_...(tmp_path)`` with the
    pre-fix ``0.5`` literal.  Everything else - including the helper definitions and
    the non-vacuity node - stays byte-identical.  Under +8 burners this must go RED
    again, which is the mutation proof that the load response is real.

  mutant_clock        scale the measurement by 0.05 before deriving.  The derivation
    then yields the 2.0 s floor, i.e. a budget that is NOT inflated to the measured
    tail: if node 1 is still green under load with that budget, the green result is
    not evidence about the measurement at all and the whole fix must be reported as
    unproven.  If it is RED, the measurement is load-bearing.

Writes ``after/mutation.diff`` and ``after/timing-mutation.diff`` (unified diffs).
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
SUITE_REL = "tests/contract/test_source_catalog_worker_bootstrap.py"

# Mutating the node itself (not the docstring that quotes the same two lines).
FIXED_ANCHOR = """def test_child_without_runtime_session_is_terminated_and_restarted(tmp_path):"""

MUTANT_DERIVATION = """    # R4 MUTATION: revert to the pre-fix hard-coded constant.
    hang_timeout_seconds = 0.5
    completed = _run_real_worker_launcher(
        project,
        timeout=15,
        worker_hang_timeout_seconds=hang_timeout_seconds,
        child_poll_milliseconds=100,
    )
"""

CLOCK_ANCHOR = """    observed = _measure_child_launch_latency_samples(tmp_path)
    t0 = max(observed) if observed else 0.0
    derived = min(
"""

MUTANT_CLOCK = """    observed = _measure_child_launch_latency_samples(tmp_path)
    # TIMING MUTATION: pretend the measured latency were 20x smaller.  The derived
    # budget then collapses to the 2.0 s floor, which is NOT the measured tail.
    t0 = (max(observed) if observed else 0.0) * 0.05
    derived = min(
"""


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unified(a: str, b: str, name_a: str, name_b: str) -> str:
    return "".join(difflib.unified_diff(
        a.splitlines(keepends=True), b.splitlines(keepends=True),
        fromfile=name_a, tofile=name_b, n=6))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    fixed_dir = ATT / "iso" / "T0"
    fixed = (fixed_dir / SUITE_REL).read_text(encoding="utf-8")
    node_anchor = FIXED_ANCHOR + """
    project = _prepare_fake_launcher_project(
        tmp_path,
        [
            {"sleep_seconds": 5, "exit_code": 0},
            {"exit_code": 0},
        ],
    )

    hang_timeout_seconds = _derive_worker_hang_timeout_seconds(tmp_path)"""
    mutant_node = FIXED_ANCHOR + """
    project = _prepare_fake_launcher_project(
        tmp_path,
        [
            {"sleep_seconds": 5, "exit_code": 0},
            {"exit_code": 0},
        ],
    )

    # R4 MUTATION: revert to the pre-fix hard-coded constant.
    hang_timeout_seconds = 0.5"""
    if fixed.count(node_anchor) != 1 or fixed.count(CLOCK_ANCHOR) != 1:
        print("FIXED-PARENT ANCHOR PROBLEM: "
              f"{fixed.count(node_anchor)}/{fixed.count(CLOCK_ANCHOR)}")
        return 1

    rc = 0
    for name, anchor, replacement, diff_out in (
        ("mutant-derivation-0.5", node_anchor, mutant_node,
         ATT / "after" / "mutation.diff"),
        ("mutant-clock", CLOCK_ANCHOR, MUTANT_CLOCK,
         ATT / "after" / "timing-mutation.diff"),
    ):
        text = fixed.replace(anchor, replacement, 1)
        target_dir = ATT / "iso" / name
        target = target_dir / SUITE_REL
        # both mutants share the fixed tree's launcher scripts
        for rel in ("scripts/source_catalog_worker.ps1",
                    "scripts/source_catalog_worker_at_logon.ps1"):
            (target_dir / rel).parent.mkdir(parents=True, exist_ok=True)
            if not (target_dir / rel).exists():
                (target_dir / rel).write_bytes((fixed_dir / rel).read_bytes())
        target.parent.mkdir(parents=True, exist_ok=True)
        if args.apply:
            target.write_bytes(text.encode("utf-8"))
            diff_out.write_text(
                unified(fixed, text, f"iso/T0/{SUITE_REL}", f"iso/{name}/{SUITE_REL}"),
                encoding="utf-8")
        print(f"{'WROTE' if args.apply else 'DRY'} {target}")
        print(f"  fixed  sha256={sha(fixed_dir / SUITE_REL)}")
        if args.apply:
            print(f"  mutant sha256={sha(target)}")
            print(f"  diff -> {diff_out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
