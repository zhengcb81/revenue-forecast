#!/usr/bin/env python3
"""Parse a pytest junit-xml into a flat {testcase_id: status} map.

status ∈ {passed, failed, error, skipped} (xfailed/xfail are reported as their
underlying outcome by pytest's junit writer; this script only classifies the
four ``<testcase>`` shapes).  Used by diff_family.py for before==after proof.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET


def parse(path: str) -> dict[str, str]:
    root = ET.parse(path).getroot()
    out: dict[str, str] = {}
    for case in root.iter("testcase"):
        cid = f"{case.get('classname', '')}::{case.get('name', '')}"
        if case.find("skipped") is not None:
            out[cid] = "skipped"
        elif case.find("error") is not None:
            out[cid] = "error"
        elif case.find("failure") is not None:
            out[cid] = "failed"
        else:
            out[cid] = "passed"
    return out


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: parse_junit.py <junit.xml> <out.json>")
        return 1
    data = parse(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    counts: dict[str, int] = {}
    for status in data.values():
        counts[status] = counts.get(status, 0) + 1
    print(json.dumps(counts, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
