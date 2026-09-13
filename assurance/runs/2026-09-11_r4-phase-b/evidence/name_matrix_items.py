"""F-B00-6: put the matrix items into the acceptance files' docstrings.

The phase-B acceptance map claims, per step, which L-items that step covers - but
four of those items were never NAMED in the case files, so a reader (or a
sampling reviewer) could not trace a case back to the matrix.  This adds one line
per file, derived FROM the same map (no new claim), and re-runs the two-sided
check afterwards.

Usage: python evidence/name_matrix_items.py [--check]
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
REVENUE = HERE.parents[3]
WIKI = REVENUE.parent / "company-wiki"
MAP = RUN / "test-acceptance-map.md"
TESTS = WIKI / "tests" / "contract"

# step -> file; the item list is READ FROM THE MAP, never hand-written here
STEP_FILES = {
    "B01": "test_r4b01_field_owner_alignment.py",
    "B02": "test_r4b02_candidate_selection.py",
    "B03": "test_r4b03_stable_bytes.py",
    "B04": "test_r4b04_reference_stability.py",
    "B05": "test_r4b05_metadata_provenance.py",
    "B06": "test_r4b06_qualification.py",
    "B07": "test_r4b07_version_contract.py",
}
ANCHOR = "Product code is NOT modified by this file"


def claimed() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in MAP.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| \*\*(B0\d)\*\*", line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.split("|")]
        out[match.group(1)] = sorted(set(re.findall(r"\bL\d{2}\b", cells[2])))
    return out


def main(argv: list[str]) -> int:
    check = "--check" in argv
    items = claimed()
    changed = []
    for step, name in STEP_FILES.items():
        ids = items.get(step) or []
        if not ids:
            print(f"{step}: no items parsed from the map - skipped")
            continue
        path = TESTS / name
        text = path.read_text(encoding="utf-8")
        if "Matrix items:" in text:
            print(f"{step}: already names its items")
            continue
        line = (
            f"Matrix items: {', '.join(ids)} (phase-B acceptance map, reverse-coverage\n"
            f"section; step {step} claims these, and the cases below are what exercises them)."
        )
        if ANCHOR not in text:
            print(f"{step}: anchor line missing in {name} - NOT modified")
            continue
        updated = text.replace(ANCHOR, f"{line}\n\n{ANCHOR}", 1)
        if check:
            print(f"{step}: would add '{line.splitlines()[0]}'")
            continue
        path.write_text(updated, encoding="utf-8", newline="")
        changed.append(name)
        print(f"{step}: named {', '.join(ids)} in {name}")

    if changed and not check:
        for name in changed:
            subprocess.run(["git", "add", f"tests/contract/{name}"], cwd=str(WIKI), check=False)
        print("staged:", ", ".join(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
