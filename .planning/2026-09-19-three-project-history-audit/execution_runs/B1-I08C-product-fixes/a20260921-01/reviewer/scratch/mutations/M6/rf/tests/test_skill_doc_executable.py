"""WU-1004 RED/audit tests: SKILL.md examples are executable and point at
the single production entry (no hand-splicing instructions)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skill_doc_names_source_preparation_as_entry():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "source_preparation.py" in text
    assert "--allow-download" in text


def test_skill_doc_no_hand_splicing_instructions():
    """The documented workflow must not tell the model to manually splice
    the client output into build_revenue_source_record."""
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "deprecated" in text and "two-step" in text  # compat path is labeled
    assert "Do NOT hand-splice" in text


def test_doc_example_commands_are_real_clis():
    for script in ("source_preparation.py", "filing_fetch_client.py"):
        assert (ROOT / "scripts" / script).is_file(), f"{script} missing"


def test_forbidden_claim_gate_in_docs():
    """'生产已接通' 只能在跨仓 E2E 证据后声明——文档不得抢先。"""
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    lowered = text.lower()
    # the doc must NOT claim production integration without evidence markers
    for forbidden in ("生产已接通", "完整复用已验收"):
        assert forbidden not in lowered
