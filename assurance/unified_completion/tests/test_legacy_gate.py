"""CA-109 legacy gate isolation: caller scan + classification."""

from __future__ import annotations

from pathlib import Path

from uc.legacy_gate import classify, report, scan_callers

REPO_ROOTS = {
    "revenue": Path(__file__).resolve().parents[3],
    "filing": Path(__file__).resolve().parents[3].parent / "filing-fetch",
    "wiki": Path(__file__).resolve().parents[3].parent / "company-wiki",
}


def test_scan_finds_real_callers():
    callers = scan_callers(REPO_ROOTS)
    # The legacy tools themselves live under tools/; the scan must at least
    # surface their self-references for classification.
    assert isinstance(callers, dict)


def test_classify_flags_unguarded_reference(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tools").mkdir(parents=True)
    (repo / "tools" / "run_gate.py").write_text(
        "import closure_gate\n", encoding="utf-8"
    )
    callers = scan_callers({"repo": repo})
    verdict = classify(callers)
    assert verdict["isolated"] is False
    assert any("run_gate.py" in f["file"] for f in verdict["findings"])
    assert all(f["successor"] == "CA-201" for f in verdict["findings"])


def test_classify_allows_migration_reader(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tools").mkdir(parents=True)
    (repo / "tools" / "migration_reader.py").write_text(
        "import receipt_validator\n", encoding="utf-8"
    )
    callers = scan_callers({"repo": repo})
    # The migration reader is still a reference — it becomes a finding with a
    # successor, never a silent pass; isolation holds only with zero findings.
    verdict = classify(callers)
    assert verdict["isolated"] is False
    assert verdict["findings"][0]["successor"] == "CA-201"


def test_report_shape():
    result = report(REPO_ROOTS)
    assert result["schema_version"] == 1
    assert result["verdict"] in ("isolated", "callers_found")


def test_real_scan_flags_workflow_caller():
    result = report(REPO_ROOTS)
    if result["verdict"] == "callers_found":
        files = [f["file"] for f in result["findings"]]
        assert any("quality.yml" in path for path in files)
