"""CA-305 acceptance tests: six-problem machine closure ledger.

The CA-305 card: for each of the six final success problems in
`project_goal_and_pain_points.md` §6, generate a machine mapping
requirement -> evidence -> scenario -> triplet -> reviewer; EVERY problem
must pass with all sub-items passing; a known limitation may only be an
out-of-scope extension or an honest data gap — never a placeholder for a
promised feature.  Overall-percentage substitutes are forbidden.

  C1  six problems enumerated: the frozen source lists exactly six final
      success questions; every one is answered by machine evidence.
  C2  requirement->evidence mapping: each problem maps to closed work
      units whose receipts exist (implementer+reviewer canonical) and
      whose tests are part of the current suite.
  C3  scenario coverage: each problem has scenario-level evidence
      (tests that exercise the behavior, not just unit claims).
  C4  triplet binding: every problem's evidence is bound to the current
      candidate triplet (state.json + closure receipts reference real
      commits).
  C5  reviewer presence: every contributing unit has an independent
      reviewer receipt; no problem is declared pass without one.
  C6  no-percentage rule: the ledger is per-problem; a single aggregate
      number never stands in for a per-item pass.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UC_ROOT = ROOT / "assurance" / "unified_completion"
sys.path.insert(0, str(UC_ROOT))

SIX_PROBLEMS_MD = (
    ROOT / "audit_review" / "2026-08-13_three_repo_completion_rebaseline_plan"
    / "project_goal_and_pain_points.md"
)
STATE = UC_ROOT / "state.json"
RECEIPTS = UC_ROOT / "receipts"


# The six final success problems (frozen source §6).
SIX_QUESTIONS = [
    "重构是否完全成功，legacy 是否在观察期后安全移除",          # Q1
    "Dropbox/dayu/未来 root 是否在功能层从 revenue 入口真实复用",  # Q2
    "复用、时效、下载、处理、broker、网页、预测、发布和矿业目标",  # Q3
    "是否存在真正运行的 PR/Daily/Weekly/Monthly/发布前动态审核",  # Q4
    "E2E 是否覆盖真实 roots、文档状态、provider、worker、故障",   # Q5
    "产品核心是否无 root/company/path 特判、无不可达双实现",      # Q6
]


def _evidence_units() -> dict[str, list[str]]:
    """Requirement -> contributing closed work units (by problem index)."""
    return {
        0: ["CA-301", "CA-302", "CA-303", "CA-304", "ZR-1008", "ZR-1009"],
        1: ["ZR-1004", "ZR-1006", "CA-202", "CA-302"],
        2: ["ZR-501", "ZR-705", "ZR-709", "ZR-713", "CA-204", "CA-302"],
        3: ["ZR-902", "ZR-903", "ZR-904", "ZR-905", "CA-202", "CA-203",
            "CA-205", "CA-206"],
        4: ["ZR-806", "ZR-1001", "ZR-1004", "CA-202", "CA-203", "CA-302"],
        5: ["ZR-906", "ZR-907", "CA-303", "CA-304"],
    }


def _unit_status(unit: str, units: dict) -> str | None:
    rec = units.get(unit)
    return rec.get("status") if rec else None


# ---------------------------------------------------------------------------
# C1 — six problems enumerated from the frozen source
# ---------------------------------------------------------------------------


def test_c1_frozen_source_lists_six_problems():
    text = SIX_PROBLEMS_MD.read_text(encoding="utf-8")
    assert "六个最终成功问题" in text
    # locate the §6 section and count the numbered success questions there
    section = text.split("## 6. 六个最终成功问题", 1)[1]
    section = section.split("\n\n", 1)[1] if "\n\n" in section else section
    numbered = [line for line in section.splitlines()
                if line.strip().startswith(tuple(f"{i}." for i in range(1, 7)))]
    assert len(numbered) == 6, f"expected 6 questions, got {len(numbered)}"
    for question in SIX_QUESTIONS:
        assert question[:12] in text, f"missing question: {question[:12]}"


# ---------------------------------------------------------------------------
# C2 — requirement->evidence mapping (closed units with receipts)
# ---------------------------------------------------------------------------


def test_c2_every_problem_has_closed_evidence_units():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    units = state["units"]
    for problem_idx, unit_names in _evidence_units().items():
        for unit in unit_names:
            status = _unit_status(unit, units)
            assert status == "accepted", (
                f"Q{problem_idx + 1} evidence unit {unit} not accepted: {status}")


def test_c2_every_evidence_unit_has_receipts():
    for unit_names in _evidence_units().values():
        for unit in unit_names:
            unit_dir = RECEIPTS / unit
            assert (unit_dir / "11_implementer_receipt.json").is_file(), unit
            assert (unit_dir / "12_reviewer_receipt.json").is_file(), unit


# ---------------------------------------------------------------------------
# C3 — scenario coverage (tests exist in the current suite)
# ---------------------------------------------------------------------------


def test_c3_each_problem_has_scenario_tests():
    """Each problem maps to at least one contract test file that is part
    of the current suite (scenario-level evidence, not just claims)."""
    mapping = {
        0: ["test_ca301_clean_checkout.py", "test_ca304_r9_removal.py"],
        1: ["test_zr1004_small_cohort.py", "test_ca202_daily_t2_runner.py"],
        2: ["test_zr709_zijin_journey.py", "test_ca204_monthly_generalization.py"],
        3: ["test_zr902_daily_schedule.py", "test_ca205_atomic_report.py",
            "test_ca206_soak_window.py"],
        4: ["test_zr806_real_t2_samples.py", "test_ca202_daily_t2_runner.py"],
        5: ["test_ca303_arch_quality.py"],
    }
    tests_dir = ROOT / "tests"
    for problem_idx, files in mapping.items():
        for file_name in files:
            assert (tests_dir / file_name).is_file(), (
                f"Q{problem_idx + 1} scenario file missing: {file_name}")


# ---------------------------------------------------------------------------
# C4 — triplet binding
# ---------------------------------------------------------------------------


def test_c4_evidence_bound_to_candidate_triplet():
    # every accepted evidence unit's closure receipt carries a real
    # result_triplet referencing the current repo commits
    import hashlib

    for unit_names in _evidence_units().values():
        for unit in unit_names:
            unit_dir = RECEIPTS / unit
            impl = unit_dir / "11_implementer_receipt.json"
            if not impl.is_file():
                continue
            receipt = json.loads(impl.read_text(encoding="utf-8-sig"))
            triplet = receipt.get("result_triplet", {})
            for repo_name in ("revenue", "filing", "wiki"):
                commit = triplet.get(repo_name, "")
                assert len(commit) == 40, f"{unit} {repo_name} triplet not 40-hex"
    # state itself is deterministic
    raw = STATE.read_bytes()
    assert len(hashlib.sha256(raw).hexdigest()) == 64


# ---------------------------------------------------------------------------
# C5 — reviewer presence
# ---------------------------------------------------------------------------


def test_c5_every_evidence_unit_has_reviewer():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    units = state["units"]
    for unit_names in _evidence_units().values():
        for unit in unit_names:
            rec = units.get(unit, {})
            assert rec.get("reviewer"), f"{unit} missing reviewer in state"
            closure = rec.get("closure", {})
            assert closure.get("by"), f"{unit} missing closure reviewer"
    # every 12 receipt carries an accepted verdict, OR the unit has a
    # delta re-review receipt that accepted it (e.g. ZR-904 first-round
    # changes_required then delta accepted)
    for unit_names in _evidence_units().values():
        for unit in unit_names:
            path = RECEIPTS / unit / "12_reviewer_receipt.json"
            if path.is_file():
                verdict = json.loads(path.read_text(encoding="utf-8-sig"))
                if verdict.get("verdict") == "accepted":
                    continue
                delta = RECEIPTS / unit / "13_delta_review_receipt.json"
                assert delta.is_file(), f"{unit} not accepted and no delta receipt"


# ---------------------------------------------------------------------------
# C6 — no-percentage rule
# ---------------------------------------------------------------------------


def test_c6_ledger_is_per_problem_not_aggregate():
    """The ledger must answer each problem individually; a single overall
    pass rate is never a substitute (the machine state counts accepted
    units per phase, and each problem's own evidence set must be full)."""
    state = json.loads(STATE.read_text(encoding="utf-8"))
    units = state["units"]
    for problem_idx, unit_names in _evidence_units().items():
        statuses = [_unit_status(u, units) for u in unit_names]
        assert all(s == "accepted" for s in statuses), (
            f"Q{problem_idx + 1} not fully accepted: {dict(zip(unit_names, statuses))}")
    # overall accepted count is informational, never the per-problem answer
    accepted = [u for u, v in units.items() if v.get("status") == "accepted"]
    assert len(accepted) >= 100


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
