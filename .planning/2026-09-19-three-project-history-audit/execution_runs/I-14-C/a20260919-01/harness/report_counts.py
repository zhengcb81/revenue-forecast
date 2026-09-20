"""I-14-C r5: produce every reportable count MECHANICALLY from the artefacts.

F-I14C-R4-01 found the r4 documents claiming "23 exact pairs" for a 24-entry table, in five
places.  This script is the antidote: any number that appears in a report is computed here
from the table/suite itself and written to `r5/counts.json`, so a document can cite the file
instead of a hand-typed figure.

    python report_counts.py --attempt <attempt dir> --python <iso venv python>
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def _import_module(path: Path, name: str):
    sys.path.insert(0, str(path))
    return __import__(name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    attempt = Path(args.attempt).resolve()
    harness = attempt / "harness"
    tests_dir = harness / "tests"

    rule_table = _import_module(harness, "run_rule_table")
    diag_table = _import_module(harness, "run_diagnostic_table")
    tests = _import_module(tests_dir, "test_i14c_real_exit_redaction")

    rule_kinds: dict[str, int] = {}
    for _id, _text, _expected, kind in rule_table.TABLE:
        rule_kinds[kind] = rule_kinds.get(kind, 0) + 1
    diag_kinds: dict[str, int] = {}
    for _id, _text, _expected, kind in diag_table.CORPUS:
        diag_kinds[kind] = diag_kinds.get(kind, 0) + 1

    # the exact-nodeid count comes from pytest itself, not from len(FIDELITY_CASES)
    collect = subprocess.run(
        [args.python, "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
         "--collect-only", "-q", str(tests_dir / "test_i14c_real_exit_redaction.py")],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(attempt),
    )
    collected = collect.stdout.decode("utf-8", "replace")
    exact_nodeids = len(
        [ln for ln in collected.splitlines() if "test_f08_output_fidelity_exact[" in ln])
    total_nodeids = len(
        [ln for ln in collected.splitlines() if re.search(r"::test_\w+", ln)])
    unique_inputs = len({text for text, _expected in tests.FIDELITY_CASES})
    unique_pairs = len(set(tests.FIDELITY_CASES))

    counts = {
        "generated_by": "harness/report_counts.py (mechanical; no hand-typed numbers)",
        "rule_table_entries": len(rule_table.TABLE),
        "rule_table_by_kind": rule_kinds,
        "diagnostic_corpus_entries": len(diag_table.CORPUS),
        "diagnostic_corpus_by_kind": diag_kinds,
        "diagnostic_strict_entries": diag_kinds.get("diagnostic", 0),
        "fidelity_cases": len(tests.FIDELITY_CASES),
        "fidelity_unique_inputs": unique_inputs,
        "fidelity_unique_pairs": unique_pairs,
        "exact_nodeids": exact_nodeids,
        "total_nodeids_collected": total_nodeids,
        "pytest_collect_returncode": collect.returncode,
        "pytest_collect_tail": collected.strip().splitlines()[-1] if collected.strip() else "",
    }
    Path(args.out).write_text(json.dumps(counts, indent=2, ensure_ascii=True),
                              encoding="utf-8")
    print(json.dumps(counts, ensure_ascii=True, indent=2))
    # the nodeid count and the table length must agree; if not, one of them is wrong
    return 0 if exact_nodeids == counts["fidelity_cases"] else 3


if __name__ == "__main__":
    sys.exit(main())
