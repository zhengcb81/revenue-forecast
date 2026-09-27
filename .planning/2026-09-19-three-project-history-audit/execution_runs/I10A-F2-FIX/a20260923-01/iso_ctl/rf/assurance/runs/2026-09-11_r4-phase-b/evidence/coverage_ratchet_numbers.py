"""Print the FC-1204 gate's own numbers from a coverage report (no gate code copied).

The gate (tests/contract/test_fc1204_coverage_ratchet.py) recomputes each module's branch
coverage as round(100 * (covered_lines + covered_branches) / (num_statements + num_branches), 1)
and compares it to its frozen floor.  This prints exactly those values for the modules touched by
the 2026-09-19 increment, so the record carries the number behind the "ratchet passed" claim.

Usage::

    python coverage_ratchet_numbers.py PATH-TO-coverage.json [module ...]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PREFIX = "src/company_wiki/source_catalog/"
DEFAULT_MODULES = ("normalizer.py", "adapters/sidecar.py", "activation.py", "resolver.py",
                   "scanner.py", "assertion_service.py", "remediation.py")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", type=Path)
    parser.add_argument("modules", nargs="*", default=list(DEFAULT_MODULES))
    args = parser.parse_args(argv)

    data = json.loads(args.report.read_text(encoding="utf-8"))
    files = data.get("files", {})
    measured: dict[str, float] = {}
    for path, entry in files.items():
        rel = path.replace("\\", "/")
        if not rel.startswith(PREFIX):
            continue
        summary = entry.get("summary", {})
        num = summary.get("num_statements", 0)
        cov = summary.get("covered_lines", 0)
        total = summary.get("num_branches", 0)
        covb = summary.get("covered_branches", 0)
        if num:
            measured[rel[len(PREFIX):]] = round(100.0 * (cov + covb) / (num + total), 1)
    for module in args.modules:
        print(f"{module}: {measured.get(module, 'NOT MEASURED')}")
    print(f"modules measured: {len(measured)}")
    print("totals: " + json.dumps(data.get("totals", {}).get("percent_covered")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
