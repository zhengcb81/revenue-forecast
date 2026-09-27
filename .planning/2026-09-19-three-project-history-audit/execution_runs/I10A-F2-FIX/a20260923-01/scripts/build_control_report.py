#!/usr/bin/env python
"""Turn the control subset run into family_diff_control.json.

Control = the SAME 5 flipped testcases, executed in this session under the SAME
conditions (dir-mode shim + short temp root) but in `iso_ctl/rf`, a pristine copy:
product = production bytes, fixtures = production bytes. A testcase that also fails
in the control is an ENVIRONMENT flip; one that passes in the control is attributable
to this card's change.

Usage: python scripts/build_control_report.py <pytest_rc>
"""
from __future__ import annotations

import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EV = ATT / "evidence"
JUNIT = EV / "family_ctl_subset_junit.xml"


def main() -> int:
    raw_rc = int(sys.argv[1])
    root = ET.parse(JUNIT).getroot()
    statuses: dict[str, str] = {}
    messages: dict[str, str] = {}
    for case in root.iter("testcase"):
        cid = f"{case.get('classname', '')}::{case.get('name', '')}"
        node = case.find("error")
        kind = "error"
        if node is None:
            node = case.find("failure")
            kind = "failed"
        if node is None:
            statuses[cid] = "skipped" if case.find("skipped") is not None else "passed"
        else:
            statuses[cid] = kind
            messages[cid] = (node.get("message") or "")[:300]

    after = json.loads((EV / "family_diff.json").read_text(encoding="utf-8"))
    before = json.loads((EV / "family_before.json").read_text(encoding="utf-8"))
    flipped = [r["id"] for r in after["regressed"]]

    missing = [i for i in flipped if i not in statuses]
    regressed, controlled_ok = [], []
    for cid in flipped:
        st = statuses.get(cid)
        row = {"id": cid, "before": before.get(cid), "control": st,
               "control_message": messages.get(cid)}
        if st in ("failed", "error"):
            regressed.append(row)
        else:
            controlled_ok.append(row)

    report = {
        "artifact": "family_diff_control",
        "generated_at_local": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "control_tree": "iso_ctl/rf (pristine product + pristine fixtures)",
        "control_conditions": "same session, same dir-mode shim, same short temp root",
        "pytest_raw_rc": raw_rc,
        "flipped_in_after": flipped,
        "regressed_in_control": regressed,
        "passed_in_control": controlled_ok,
        "ids_not_run_in_control": missing,
        "identical": False,
    }
    (EV / "family_diff_control.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (EV / "family_ctl_subset.json").write_text(
        json.dumps({"artifact": "family_ctl_subset", "raw_rc": raw_rc,
                    "statuses": statuses,
                    "generated_at_local": report["generated_at_local"]},
                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "raw_rc": raw_rc,
        "regressed_in_control": [r["id"] for r in regressed],
        "passed_in_control": [r["id"] for r in controlled_ok],
        "missing": missing,
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
