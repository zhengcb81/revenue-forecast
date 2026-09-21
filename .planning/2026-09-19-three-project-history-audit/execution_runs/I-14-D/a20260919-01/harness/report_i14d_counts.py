"""I-14-D: mechanically derive every reported count (r5 lesson F-I14C-R4-01).

No count may be quoted in prose without coming from this file's output.

    python report_i14d_counts.py --out <json>
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _table_len(path: Path, var: str) -> int:
    """AST-count the top-level list literal `var = [...]` in a harness script."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == var for t in node.targets):
            return len(node.value.elts)
    raise SystemExit(f"COUNTS-REFUSED: {var} not found in {path.name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--basetemp", default="",
                        help="fresh empty dir for the --collect-only run")
    args = parser.parse_args(argv)

    rule_entries = _table_len(HERE / "run_rule_table_i14d.py", "TABLE")
    oracle_cases = _table_len(HERE / "run_i14d_oracle.py", "CASES")
    fidelity = _suite_fidelity_pairs()
    total_nodeids = (_collected_nodeids(Path(args.basetemp))
                     if args.basetemp else None)

    # kind breakdown of the rule table, derived from the same AST
    tree = ast.parse((HERE / "run_rule_table_i14d.py").read_text(encoding="utf-8"))
    kinds: dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "TABLE" for t in node.targets):
            for elt in node.value.elts:
                kind = elt.elts[3].value
                kinds[kind] = kinds.get(kind, 0) + 1

    counts = {
        "rule_table_entries": rule_entries,
        "rule_table_by_kind": kinds,
        "oracle_cases": oracle_cases,
        "oracle_narrow_must": sum(
            1 for c in _case_kinds() if c == "narrow_must"),
        "oracle_keep_must": sum(
            1 for c in _case_kinds() if c == "keep_must"),
        # the copied I-14-C suite's count check binds to <attempt>/r5/counts.json;
        # these two are derived mechanically from that suite's own AST, never by
        # running the redactor.
        "fidelity_cases": fidelity,
        "exact_nodeids": fidelity,
        "total_nodeids": total_nodeids,
        "generator": "harness/report_i14d_counts.py",
    }
    # cross-checks that must agree
    checks = {
        "rule_kinds_sum_matches_entries": sum(kinds.values()) == rule_entries,
        "oracle_kinds_sum_matches_cases": (
            counts["oracle_narrow_must"] + counts["oracle_keep_must"]
            == oracle_cases),
    }
    counts["checks"] = checks
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(counts, indent=2, ensure_ascii=True),
                   encoding="utf-8")
    # The byte-identical copied I-14-C suite reads <attempt>/r5/counts.json (its
    # own frozen path convention).  Write the SAME derived counts there, with a
    # README so nobody mistakes this directory for I-14-C's evidence.
    shim = HERE.parent / "r5"
    shim.mkdir(parents=True, exist_ok=True)
    (shim / "counts.json").write_text(
        json.dumps(counts, indent=2, ensure_ascii=True), encoding="utf-8")
    (shim / "README.txt").write_text(
        "This r5/ directory belongs to attempt I-14-D/a20260919-01. It exists "
        "only because the byte-identical copy of I-14-C's frozen suite binds its "
        "count check to <attempt>/r5/counts.json. counts.json here is generated "
        "by harness/report_i14d_counts.py (AST-derived), NOT copied from "
        "I-14-C. Nothing from I-14-C was modified.\n",
        encoding="utf-8")
    print(json.dumps(counts, ensure_ascii=True, indent=2))
    return 0 if all(checks.values()) else 3


def _case_kinds() -> list[str]:
    tree = ast.parse((HERE / "run_i14d_oracle.py").read_text(encoding="utf-8"))
    out = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            for elt in node.value.elts:
                out.append(elt.elts[1].value)
    return out


def _suite_fidelity_pairs() -> int:
    """AST-count FIDELITY_CASES in the byte-identical copied I-14-C suite."""
    path = HERE / "tests" / "test_i14c_real_exit_redaction.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "FIDELITY_CASES"
                for t in node.targets):
            return len(node.value.elts)
    raise SystemExit("COUNTS-REFUSED: FIDELITY_CASES not found in the copied suite")


def _collected_nodeids(basetemp: Path) -> int:
    import os
    import subprocess
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "pytest", "harness/tests",
         "--collect-only", "-q", "--basetemp", str(basetemp)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(HERE.parent))
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("harness/tests/")]
    return len(lines)


if __name__ == "__main__":
    sys.exit(main())
