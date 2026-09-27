"""Compare two junit.xml runs: outcomes per test, regressions = green-before -> not-green-after."""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def outcomes(xml: Path) -> dict[str, str]:
    tree = ET.parse(xml)
    out: dict[str, str] = {}
    for tc in tree.iter("testcase"):
        key = f"{tc.get('classname', '')}::{tc.get('name', '')}"
        if tc.find("skipped") is not None:
            out[key] = "skipped"
        elif tc.find("failure") is not None or tc.find("error") is not None:
            out[key] = "failed"
        else:
            out[key] = "passed"
    return out


a_label, a_xml, b_label, b_xml = sys.argv[1:5]
A, B = outcomes(Path(a_xml)), outcomes(Path(b_xml))

only_a = sorted(set(A) - set(B))
only_b = sorted(set(B) - set(A))
regressions = sorted(k for k in A if k in B and A[k] == "passed" and B[k] != "passed")
improvements = sorted(k for k in A if k in B and A[k] != "passed" and B[k] == "passed")
changed = sorted(k for k in A if k in B and A[k] != B[k])

def counts(d):
    c = {"passed": 0, "failed": 0, "skipped": 0}
    for v in d.values():
        c[v] += 1
    return c

report = {
    f"before[{a_label}]": counts(A),
    f"after[{b_label}]": counts(B),
    "only_before": only_a,
    "only_after": only_b,
    "regressions_green_to_notgreen": regressions,
    "improvements_notgreen_to_green": improvements,
    "all_outcome_changes": {k: [A[k], B[k]] for k in changed},
}
print(json.dumps(report, indent=2))
if len(sys.argv) > 5:
    Path(sys.argv[5]).write_text(json.dumps(report, indent=2), encoding="utf-8")
sys.exit(1 if regressions or only_a else 0)
