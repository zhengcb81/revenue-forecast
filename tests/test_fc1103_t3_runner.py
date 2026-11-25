"""The standalone weekly CLI keeps its RF report and reads only FF evidence."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

RUNNER = Path(__file__).resolve().parents[1] / "tools" / "weekly_t3_runner.py"


@pytest.mark.parametrize("legacy_flag", [[], ["--force"]], ids=["no-flag", "legacy-force"])
def test_missing_foreign_tool_blocks_without_producing_an_actuation_request(tmp_path, legacy_flag):
    report_root = tmp_path / "report"
    absent = tmp_path / "no-ff-tool"
    result = subprocess.run(
        [sys.executable, "-B", str(RUNNER), "--report-root", str(report_root),
         "--filing-fetch-root", str(absent), "--run-id", "old-local-id", *legacy_flag],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=20, check=False,
    )
    assert result.returncode == 2 and "BLOCKED" in result.stderr
    (report,) = report_root.rglob("t3_report.json")
    assert report.parent.name == "old-local-id"
    value = json.loads(report.read_bytes())
    assert value["status"] == "blocked" and value["detail"] == "owner_lookup_unavailable"
    assert value["force"] is bool(legacy_flag)
    assert not absent.exists()
    assert [path for path in tmp_path.rglob("*") if path.is_file()] == [report]
