"""WC-6 regression-family selection: mechanical grep over the test tree.

  python select_family.py

Writes <attempt>/evidence/family_files.json + family_grep.txt.
Patterns are fixed here (oracle §6); no hand-picked additions, no removals.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from wc6_common import ISO_CW, EVID, write_json

PATTERNS = [
    r"adapter_dispatch",
    r"scan_root_via_adapter",
    r"_to_scanner_candidate",
    r"_Candidate\b",
    r"_ObservedFile\b",
    r"source_catalog\.scanner",
    r"source_catalog import scanner",
    r"adapters\.sidecar",
    r"SidecarFilingAdapter",
    r"error_details",
    r"\bFROM locations\b",
    r"INSERT INTO locations",
]
#: ratchets that NAMe the touched files (oracle §6)
EXPLICIT = [
    "tests/contract/test_fc1204_complexity_ratchet.py",
    "tests/contract/test_fc1204_coverage_ratchet.py",
    "tests/contract/test_fc1201_root_hardcode_gate.py",
]


def main() -> int:
    root = ISO_CW
    rx = re.compile("|".join(f"(?:{p})" for p in PATTERNS))
    hits: dict[str, list[str]] = {}
    for path in sorted((root / "tests").rglob("test_*.py")):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        matched = sorted({p for p in PATTERNS if re.search(p, text)})
        if matched:
            hits[rel] = matched
    for rel in EXPLICIT:
        hits.setdefault(rel, ["explicit-ratchet"])
    files = sorted(hits)
    write_json(EVID / "family_files.json",
               {"patterns": PATTERNS, "explicit": EXPLICIT,
                "file_count": len(files),
                "files": {f: hits[f] for f in files}})
    lines = [f"{f}\t{', '.join(hits[f])}" for f in files]
    (EVID / "family_grep.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"file_count": len(files), "files": files}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
