"""Structure targets (R5, RC-2 / N-02) — module size limits must be enforced.

N-02: revenue_core.py reached 3922 lines with no one intercepting, and the
Phase 10 "physical split" was declared complete while its checkboxes were
empty.  These assertions are the executable version of that promise.

Status: revenue_core is still over target (R9 will split it).  This test is
INTENTIONALLY RED until then — see IMPLEMENTATION_PLAN.md Stage 11.  Do not
silence it; split the module instead.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class StructureTargetTests(unittest.TestCase):
    def test_revenue_core_has_a_single_responsibility_boundary(self) -> None:
        # R9 target: revenue_core.py must be an orchestration layer, not a
        # 4000-line monolith.  Currently 3922+ lines — over the 2500 target.
        lines = (SCRIPTS / "revenue_core.py").read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(
            len(lines),
            2500,
            "revenue_core.py exceeds the 2500-line target; R9 module split "
            "is required (IMPLEMENTATION_PLAN.md Stage 11).  Do not raise the "
            "limit silently — split instead.",
        )

    def test_no_empty_placeholder_packages(self) -> None:
        # N-02: analysis/ and research/ were empty shells after the fake split.
        for directory in ("analysis", "research"):
            package = SCRIPTS / directory
            if not package.is_dir():
                continue
            modules = [
                path
                for path in package.glob("*.py")
                if path.name != "__init__.py"
            ]
            self.assertGreater(
                len(modules),
                0,
                f"scripts/{directory}/ is an empty placeholder package; "
                "either wire it up or remove it",
            )


if __name__ == "__main__":
    unittest.main()
