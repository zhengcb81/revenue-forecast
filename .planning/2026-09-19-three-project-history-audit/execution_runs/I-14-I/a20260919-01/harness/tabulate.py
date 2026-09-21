"""READ-ONLY tabulator for evidence JSON produced by this attempt.

Usage:
  <python> -X utf8 -B harness/tabulate.py --probe <probe_stdout.txt>
  <python> -X utf8 -B harness/tabulate.py --gate <cases_report.json>
  <python> -X utf8 -B harness/tabulate.py --pytest <pytest_stdout.txt>

Prints a compact human-readable table.  Writes nothing.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def show_probe(path: str) -> None:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    print(f"SUT_VERSION = {doc['sut_version']}")
    print(f"{'label':<34} {'outcome':<62} keys")
    for row in doc["rows"]:
        if row["raised"]:
            outcome = (f"RAISED {row['exception_type']}: {row['exception_message']}"
                       f" @ line {row['crash_line']} :: {row['crash_source']}")
            keys = ""
        else:
            outcome = f"verdict={row['verdict']} refusals={row['refusals']}"
            keys = (f"basis_type={row['computed.basis_type']} "
                    f"reg={row['computed.basis_registered']} "
                    f"qc_in={row['computed.quick_check_in_observation_intervals']} "
                    f"sum_used={row['computed.sum_used_for_natural_duration']} "
                    f"qc_ovl={row['computed.quick_check_overlap_seconds']} "
                    f"union={row['computed.union_seconds']} "
                    f"json_ok={row['computed_json_serialisable']}")
        print(f"{row['label']:<34} {outcome:<62} {keys}")


def show_gate(path: str) -> None:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("ok", "label", "case_count", "mismatch_count",
                "accepted_ineligible_count", "sut_raw_returncode", "sut_version",
                "sut_sha256", "cases_sha256", "expectations_sha256", "error"):
        if key in doc:
            print(f"{key} = {doc[key]}")
    if doc.get("accepted_ineligible"):
        print(f"accepted_ineligible = {doc['accepted_ineligible']}")
    for mm in doc.get("mismatches", []):
        print(f"  mismatch {mm['case_id']:<5} {mm['field']:<40} "
              f"expected={mm['expected']!r} got={mm['got']!r}")


PYTEST_LINE = re.compile(
    r"^(?P<file>\S+\.py)::(?P<name>.+?)\s+"
    r"(?P<outcome>PASSED|FAILED|XFAIL|XPASS|ERROR|SKIPPED)\b")


def show_pytest(path: str) -> None:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    counts: dict[str, int] = {}
    for line in text.splitlines():
        m = PYTEST_LINE.match(line.strip())
        if m:
            counts[m.group("outcome")] = counts.get(m.group("outcome"), 0) + 1
            print(f"{m.group('outcome'):<8} {m.group('name')}")
    print("--- counts ---")
    for key in sorted(counts):
        print(f"{key} = {counts[key]}")
    tail = [ln for ln in text.splitlines() if re.search(r"=+ .*(passed|failed|error|xfail).* =+$", ln)]
    for ln in tail:
        print(f"summary: {ln.strip()}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe")
    ap.add_argument("--gate")
    ap.add_argument("--pytest")
    args = ap.parse_args()
    if args.probe:
        show_probe(args.probe)
    if args.gate:
        show_gate(args.gate)
    if args.pytest:
        show_pytest(args.pytest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
