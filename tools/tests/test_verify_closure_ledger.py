"""WU-10.2: closure ledger schema / id-coverage / test-ref checks (RED first)."""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from verify_closure_ledger import (  # type: ignore[import-not-found]
    VALID_STATUSES,
    validate_schema,
    check_id_coverage,
    check_test_refs,
    honesty_rows,
)


def _minimal_ledger() -> dict:
    return {
        "schema_version": "1.0",
        "scope": {"findings": ["F-001"], "historical": ["A-F01"], "risks": ["R-001"]},
        "rows": [
            {
                "id": "F-001",
                "category": "finding",
                "final_status": "not_a_defect",
                "fix_wu": ["WU-0.1"],
                "red_test": [],
                "regression_tests": [],
                "production_evidence": [],
                "remaining_risk": "",
                "reviewer": "independent",
                "commit_or_config_hash": "73a23c6",
                "rationale": "informational",
            },
            {
                "id": "A-F01",
                "category": "historical",
                "final_status": "resolved",
                "fix_wu": ["WU-7.1"],
                "red_test": [],
                "regression_tests": [],
                "production_evidence": [],
                "remaining_risk": "",
                "reviewer": "independent",
                "commit_or_config_hash": "73a23c6",
                "rationale": "guarded",
            },
            {
                "id": "R-001",
                "category": "risk",
                "final_status": "controlled",
                "fix_wu": ["WU-2A.1"],
                "red_test": [],
                "regression_tests": [],
                "production_evidence": [],
                "remaining_risk": "",
                "reviewer": "independent",
                "commit_or_config_hash": "73a23c6",
                "rationale": "contract test",
            },
        ],
    }


def test_schema_missing_required_field_fails():
    ledger = _minimal_ledger()
    del ledger["rows"][0]["rationale"]
    assert validate_schema(ledger)


def test_schema_invalid_status_fails():
    ledger = _minimal_ledger()
    ledger["rows"][0]["final_status"] = "banana"
    assert validate_schema(ledger)


def test_schema_valid_passes():
    assert validate_schema(_minimal_ledger()) == []


def test_id_coverage_missing_finding_fails():
    ledger = _minimal_ledger()
    ledger["rows"] = ledger["rows"][1:]  # drop F-001
    problems = check_id_coverage(ledger)
    assert any("F-001" in p for p in problems)


def test_id_coverage_missing_risk_fails():
    ledger = _minimal_ledger()
    ledger["rows"] = ledger["rows"][:2]  # drop R-001
    problems = check_id_coverage(ledger)
    assert any("R-001" in p for p in problems)


def test_id_coverage_missing_historical_fails():
    ledger = _minimal_ledger()
    ledger["rows"] = [ledger["rows"][0], ledger["rows"][2]]
    problems = check_id_coverage(ledger)
    assert any("A-F01" in p for p in problems)


def test_honesty_rows_lists_unresolved():
    ledger = _minimal_ledger()
    ledger["rows"][0]["final_status"] = "unresolved"
    flagged = honesty_rows(ledger)
    assert any(r["id"] == "F-001" for r in flagged)


def test_valid_statuses_allow_partial_and_unresolved():
    assert "partial" in VALID_STATUSES
    assert "unresolved" in VALID_STATUSES
    assert "not_a_defect" in VALID_STATUSES
    assert "superseded" in VALID_STATUSES
    assert "controlled" in VALID_STATUSES


def test_check_test_refs_missing_file_fails(tmp_path):
    """A regression ref that pytest cannot collect must be reported."""
    problems = check_test_refs(
        [{"repo": "test", "nodeid": "does_not_exist.py::test_x", "skip_exemption": None}],
        repo_dir=str(tmp_path),
        repo_name="test",
        python=(sys.executable,),
    )
    assert problems


def test_check_test_refs_passing_file_ok(tmp_path):
    (tmp_path / "test_ok.py").write_text(
        "def test_passes():\n    assert 1 + 1 == 2\n", encoding="utf-8"
    )
    problems = check_test_refs(
        [{"repo": "test", "nodeid": "test_ok.py::test_passes", "skip_exemption": None}],
        repo_dir=str(tmp_path),
        repo_name="test",
        python=(sys.executable,),
    )
    assert problems == []


def test_check_test_refs_skipped_requires_exemption(tmp_path):
    (tmp_path / "test_skip.py").write_text(
        "import pytest\n\n"
        "@pytest.mark.skip(reason='platform gate')\n"
        "def test_skipped():\n    assert False\n",
        encoding="utf-8",
    )
    ref = {"repo": "test", "nodeid": "test_skip.py::test_skipped", "skip_exemption": None}
    assert check_test_refs([ref], repo_dir=str(tmp_path), repo_name="test",
                           python=(sys.executable,))
    ref["skip_exemption"] = "platform-gated skip (documented)"
    assert check_test_refs([ref], repo_dir=str(tmp_path), repo_name="test",
                           python=(sys.executable,)) == []


def test_check_test_refs_ignores_other_repos(tmp_path):
    (tmp_path / "test_ok.py").write_text("def test_p():\n    pass\n", encoding="utf-8")
    ref = {"repo": "other", "nodeid": "not_checked.py::test_x", "skip_exemption": None}
    assert check_test_refs([ref], repo_dir=str(tmp_path), repo_name="test",
                           python=(sys.executable,)) == []
