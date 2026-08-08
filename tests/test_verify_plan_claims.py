"""verify_plan_claims (R5) — completed claims must be machine-evidenced."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from verify_plan_claims import parse_plan, verify  # noqa: E402


COMPLETED_WITH_EVIDENCE = """\
## Phase 1（测试）— 状态：completed
- [x] done
- [x] done too

## Phase 2（伪完成）— 状态：completed
- [x] one
- [ ] unchecked without waiver
"""

PROGRESS_WITH_EVIDENCE = """\
## 2026-08-08
- Phase 1: python -m pytest tests -q -> 5 passed
"""

PROGRESS_WITHOUT_EVIDENCE = """\
## 2026-08-08
- Phase 1 完成了
"""


class VerifyPlanClaimsTests(unittest.TestCase):
    def test_unchecked_items_in_completed_phase_need_waiver(self) -> None:
        problems, _ = verify(COMPLETED_WITH_EVIDENCE, PROGRESS_WITH_EVIDENCE)
        self.assertTrue(
            any("unchecked" in problem and "Phase 2" in problem for problem in problems)
        )

    def test_completed_claim_requires_evidence(self) -> None:
        problems, _ = verify(COMPLETED_WITH_EVIDENCE, PROGRESS_WITHOUT_EVIDENCE)
        self.assertTrue(
            any("no machine evidence" in problem for problem in problems)
        )

    def test_waiver_suppresses_unchecked_complaint(self) -> None:
        plan = COMPLETED_WITH_EVIDENCE.replace(
            "- [ ] unchecked without waiver",
            "- [ ] unchecked with waiver（豁免：环境性残余）",
        )
        problems, report = verify(plan, PROGRESS_WITH_EVIDENCE)
        self.assertFalse(any("unchecked" in problem for problem in problems))

    def test_fully_backed_plan_passes(self) -> None:
        plan = """\
## Phase 1（全部完成）— 状态：completed
- [x] everything checked
"""
        problems, _ = verify(plan, PROGRESS_WITH_EVIDENCE)
        self.assertEqual(problems, [])

    def test_parse_plan_counts_checkboxes(self) -> None:
        phases = parse_plan(COMPLETED_WITH_EVIDENCE)
        self.assertEqual(phases[0]["unchecked"], 0)
        self.assertEqual(phases[1]["unchecked"], 1)


if __name__ == "__main__":
    unittest.main()
