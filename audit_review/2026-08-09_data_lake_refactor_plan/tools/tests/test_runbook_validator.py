"""WU-103 RED/audit tests: runbook completeness + closure mapping gate."""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from runbook_validator import (  # noqa: E402
    extract_wu_ids,
    check_card_fields,
    check_wu_sets_match,
    check_wu_id_duplicates,
    check_no_placeholders,
    check_plan_version_binding,
    check_finding_mapping,
)


def test_extract_wu_ids_from_task_plan():
    plan = "## Phase 1\n### WU-101 标题\n### WU-102 标题\n### WU-103 标题\n"
    assert extract_wu_ids(plan, "### ") == {"WU-101", "WU-102", "WU-103"}


def test_extract_wu_ids_from_runbook():
    runbook = "### WU-101\n### WU-102\n"
    assert extract_wu_ids(runbook, "### ") == {"WU-101", "WU-102"}


def test_wu_sets_match_fails_on_missing_card():
    plan = "### WU-101\n### WU-102\n"
    runbook = "### WU-101\n"
    problems = check_wu_sets_match(plan, runbook)
    assert any("WU-102" in p and "runbook" in p for p in problems)


def test_wu_sets_match_fails_on_extra_card():
    plan = "### WU-101\n"
    runbook = "### WU-101\n### WU-999\n"
    problems = check_wu_sets_match(plan, runbook)
    assert any("WU-999" in p for p in problems)


def test_card_fields_complete_passes():
    card = """### WU-101

- Owner/Targets：x
- Inputs：x
- RED/Focused：x
- Mutation：x
- Audit：x
- Rollback：x
- Accept：x
"""
    assert check_card_fields(card) == []


def test_card_fields_missing_fails():
    card = "### WU-101\n\n- Owner/Targets：x\n- Inputs：x\n"
    problems = check_card_fields(card)
    assert any("RED/Focused" in p for p in problems)


def test_no_placeholders_fails():
    assert check_no_placeholders("待补齐 WU-400~404")
    assert check_no_placeholders("WU-200 TBD")
    assert check_no_placeholders("placeholder for later")
    assert check_no_placeholders("正常文本") == []


def test_plan_version_binding():
    task_plan = "> 计划版本：2.1-full-refactor-execution-cards\n"
    runbook = "> 绑定计划：task_plan.md 2.1-full-refactor-execution-cards\n"
    assert check_plan_version_binding(task_plan, runbook) == []
    runbook_bad = "> 绑定计划：task_plan.md 1.0-old\n"
    assert check_plan_version_binding(task_plan, runbook_bad)


def test_finding_mapping_coverage():
    findings = "F-034 x\nF-051 y\nF-060 z\n"
    plan = "| F-034 | Phase 3 |\n| F-051 | Phase 10 |\n| F-060 | 总门 |\n"
    mapping = {"F-034": "Phase 3", "F-051": "Phase 10"}
    problems = check_finding_mapping(findings, plan, mapping)
    assert any("F-060" in p for p in problems)
    mapping_full = {"F-034": "P3", "F-051": "P10", "F-060": "P15"}
    assert check_finding_mapping(findings, plan, mapping_full) == []


def test_mapping_missing_table_row_fails():
    # F2: a coverage-table row without a mapping entry must fail
    findings = "F-034 x\n"
    plan = "| F-034 | Phase 3 |\n| F-035 | WU-101 |\n"
    problems = check_finding_mapping(findings, plan, {"F-034": "Phase 3"})
    assert any("F-035" in p for p in problems)


def test_duplicate_wu_id_detected():
    plan = "### WU-101 a\n### WU-101 b\n### WU-102\n"
    problems = check_wu_id_duplicates(plan, "### ", "task_plan")
    assert any("WU-101" in p and "2 times" in p for p in problems)
    assert check_wu_id_duplicates("### WU-101\n### WU-102\n", "### ", "x") == []


def test_forbidden_claim_gate():
    from runbook_validator import check_forbidden_claims

    # claim without product caller evidence must fail
    doc = "Dropbox 生产复用已验证，只改配置即可。"
    problems = check_forbidden_claims(doc)
    assert problems
    doc_ok = "fixture E2E 通过；真实 canary 待合格样本（BLOCKED）。"
    assert check_forbidden_claims(doc_ok) == []
