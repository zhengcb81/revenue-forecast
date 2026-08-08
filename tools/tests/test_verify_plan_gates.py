"""WU-8.3: timed-gate and production-apply conflict checks (RED first)."""
import sys
from pathlib import Path
import tempfile

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from verify_plan_claims import (
    _production_apply_conflict,
    _timed_gate_problems,
    _discover_plans,
)


def test_timed_gate_not_elapsed():
    plan = """## Phase 1（治理）— 状态：completed ✅（2026-08-07 完成；DoD 要求 4 周观察期）
- [x] 治理落地
"""
    progress = "2026-08-08 测试通过 100 passed"
    problems = _timed_gate_problems(plan, progress)
    assert any("observation-gated" in p for p in problems), problems


def test_timed_gate_elapsed_ok():
    plan = """## Phase 1（治理）— 状态：completed ✅（2026-07-01 完成；4 周观察期）
- [x] 治理落地
"""
    progress = "2026-08-08 测试通过 100 passed"
    assert _timed_gate_problems(plan, progress) == []


def test_production_apply_conflict():
    plan = "本方案只做规划，不实施。\nproduction apply 已完成：catalog 已退役。"
    assert _production_apply_conflict(plan)
    assert _production_apply_conflict("只做计划，不实施。") == []


def test_discover_finds_findings():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "task_plan.md").write_text("# plan")
        (d / "progress.md").write_text("# progress")
        (d / "findings.md").write_text("# findings")
        pairs = _discover_plans(d)
        assert len(pairs) == 1
        assert pairs[0][2] is not None
