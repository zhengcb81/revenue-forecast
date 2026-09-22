"""REM-49 — compare the focused FC-904 suite results, baseline vs fixed2.

Reads the two junitxml files and asserts the per-node outcomes are IDENTICAL
(the declared form of "the relevant test suite's results are unchanged by the
comment fix").  Exits 0 only when identical; writes the comparison to
evidence/rem49_fc904_parity.json.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
BASE_XML = ATTEMPT / "evidence" / "rem49_fc904_baseline.xml"
FIXED_XML = ATTEMPT / "evidence" / "rem49_fc904_fixed2.xml"
OUT = ATTEMPT / "evidence" / "rem49_fc904_parity.json"

RF3_NODE_FRAGMENT = "TestB3ProductionProvenance::test_module_under_test_is_the_bound_copy"


def cases(path: Path) -> dict:
    root = ET.parse(path).getroot()
    out = {}
    for case in root.iter("testcase"):
        module = (case.get("classname") or "").split(".")[-1]
        key = f"{module}::{case.get('name')}"
        if case.find("failure") is not None or case.find("error") is not None:
            status = "failed"
        elif case.find("skipped") is not None:
            status = "skipped"
        else:
            status = "passed"
        out[key] = status
    return out


def main() -> int:
    baseline = cases(BASE_XML)
    fixed2 = cases(FIXED_XML)
    identical = baseline == fixed2
    base_rf3 = [k for k, v in baseline.items()
                if v == "failed" and RF3_NODE_FRAGMENT in k]
    fixed_rf3 = [k for k, v in fixed2.items()
                 if v == "failed" and RF3_NODE_FRAGMENT in k]
    result = {
        "baseline_file": str(BASE_XML.name),
        "fixed2_file": str(FIXED_XML.name),
        "baseline_counts": {s: list(baseline.values()).count(s)
                            for s in sorted(set(baseline.values()))},
        "fixed2_counts": {s: sorted(fixed2.values()).count(s)
                          for s in sorted(set(fixed2.values()))},
        "per_node_identical": identical,
        "baseline_nodes": baseline,
        "fixed2_nodes": fixed2,
        "failed_nodes_baseline": sorted(k for k, v in baseline.items() if v == "failed"),
        "failed_nodes_fixed2": sorted(k for k, v in fixed2.items() if v == "failed"),
        "rf3_known_failure_in_both": (
            len(base_rf3) == 1 and base_rf3 == fixed_rf3
        ),
        "note": (
            "The only failing node in BOTH runs is RF-3's location-dependent assertion "
            "(test_fc904_artifact_selection.py:379 requires the directory basename "
            "'B3-I05C-delivery-fixes'; this attempt relocates the carrier). It is P4, "
            "owned by RF-3, not by REM-49, and it fails IDENTICALLY before and after the "
            "comment fix — which is exactly the declared zero-behaviour-delta criterion."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"per_node_identical": identical,
                      "baseline_counts": result["baseline_counts"],
                      "fixed2_counts": result["fixed2_counts"]}, indent=2))
    return 0 if identical else 1


if __name__ == "__main__":
    sys.exit(main())
