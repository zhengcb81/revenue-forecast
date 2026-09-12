"""Does the acceptance map's L-mapping survive contact with the code?

The phase-B acceptance map claims, per step, which matrix items (L01-L12) that
step covers.  Now that all seven steps are implemented, this script checks the
claim against the repository instead of trusting the table:

  * the map's step rows are parsed for their L-IDs (B01..B07);
  * the B-side acceptance files are scanned for L-ID mentions, BOTH in the step's
    own file and across all of them;
  * a claimed L-ID with no mention ANYWHERE is a gap (the map would be
    overstating coverage); a step whose own file never names its items is a
    weaker, recorded observation rather than a failure.

Usage: python evidence/l_coverage_check.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path(__file__).resolve().parents[4]
WIKI_TESTS = REVENUE.parent / "company-wiki" / "tests" / "contract"
MAP = RUN / "test-acceptance-map.md"

# The B-side acceptance files, per step (the files this phase created).
STEP_FILES = {
    "B01": "test_r4b01_field_owner_alignment.py",
    "B02": "test_r4b02_candidate_selection.py",
    "B03": "test_r4b03_stable_bytes.py",
    "B04": "test_r4b04_reference_stability.py",
    "B05": "test_r4b05_metadata_provenance.py",
    "B06": "test_r4b06_qualification.py",
    "B07": "test_r4b07_version_contract.py",
}

L_IDS = [f"L{index:02d}" for index in range(1, 13)]


def claimed_from_map() -> dict[str, list[str]]:
    """Parse the step rows of the map: `| **B0x** | **L0y**、L0z | ...`."""
    claimed: dict[str, list[str]] = {}
    text = MAP.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.startswith("| **B0"):
            continue
        step_match = re.search(r"\*\*(B0\d)\*\*", line)
        if not step_match:
            continue
        step = step_match.group(1)
        # only the second cell (the matrix column) is the claim
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) < 3:
            continue
        claimed[step] = sorted(set(re.findall(r"\bL\d{2}\b", cells[2])))
    return claimed


def mentions() -> dict[str, list[str]]:
    """Which acceptance files name which L-IDs (in docstrings or comments)."""
    found: dict[str, list[str]] = {lid: [] for lid in L_IDS}
    for path in sorted(WIKI_TESTS.glob("test_r4b0*.py")):
        text = path.read_text(encoding="utf-8")
        for lid in L_IDS:
            if re.search(rf"\b{lid}\b", text):
                found[lid].append(path.name)
    return found


def main() -> int:
    claimed = claimed_from_map()
    found = mentions()
    report = {"claimed_per_step": claimed, "mentions": found, "gaps": [], "step_without_own_mentions": []}
    for step, ids in sorted(claimed.items()):
        own = STEP_FILES.get(step)
        for lid in ids:
            if not found[lid]:
                report["gaps"].append({"step": step, "item": lid})
            elif own and own not in found[lid]:
                report["step_without_own_mentions"].append(
                    {"step": step, "item": lid, "mentioned_in": found[lid]}
                )
    uncovered = [lid for lid in L_IDS if not found[lid]]
    report["items_with_no_mention_anywhere"] = uncovered

    out = RUN / "evidence" / "l-item-coverage.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("claimed per step:")
    for step, ids in sorted(claimed.items()):
        print(f"  {step}: {', '.join(ids) or '(none parsed)'}")
    print("\nL-IDs with no mention in any B-side acceptance file:", uncovered or "none")
    print("claimed items with no mention anywhere:", report["gaps"] or "none")
    print("steps whose own file does not name the item:", report["step_without_own_mentions"] or "none")
    print("wrote", out.relative_to(REVENUE).as_posix())
    return 1 if report["gaps"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
