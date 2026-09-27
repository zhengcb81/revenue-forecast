"""CA-004 legacy disposition: parsing, validation, cycle detection, and the
real frozen-table build/verify roundtrip."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import uc.legacy_disposition as ld
from conftest import REPO_ROOT

SAMPLE_FC = """| FC | 旧登记 | 类 | 原因 | 唯一successor |
|---|---|---:|---|---|
| FC-101 | accepted | I | G1 | CA-101, CA-102 |
| FC-102 | accepted | C | G2 | CA-104 |
| FC-1501 | pending | P | Z1 | CA-107 |
"""

SAMPLE_WAVES = """| 波次 | 当前分类 | 当前事实 | 新处置 |
|---|---|---|---|
| R0 | C | text | CA-001～109、CA-201 |
| R1 | I | text | CA-003、ZR-1002 |
"""


def test_parse_fc_rows():
    rows = ld.parse_fc_rows(SAMPLE_FC)
    assert [r["fc_id"] for r in rows] == ["FC-101", "FC-102", "FC-1501"]
    assert rows[0]["class_name"] == "implemented_not_independently_verified"
    assert rows[0]["successors"] == ["CA-101", "CA-102"]
    assert rows[1]["class_name"] == "contradicted_by_current_behavior"


def test_parse_waves_with_fullwidth_range():
    waves = ld.parse_waves(SAMPLE_WAVES)
    assert [w["wave"] for w in waves] == ["R0", "R1"]
    assert waves[0]["successors"][0] == "CA-001"
    assert "CA-109" in waves[0]["successors"]
    assert waves[0]["successors"][-1] == "CA-201"


def test_validate_unknown_successor(monkeypatch):
    monkeypatch.setattr(ld, "EXPECTED_COUNTS", {"I": 1, "C": 1, "S": 0, "P": 1})
    rows = ld.parse_fc_rows(SAMPLE_FC)
    rows[0]["successors"] = ["CA-999"]
    problems = ld.validate(rows, ld.parse_waves(SAMPLE_WAVES), {"CA-101"})
    assert any("unknown successors" in p for p in problems)


def test_validate_missing_successor(monkeypatch):
    monkeypatch.setattr(ld, "EXPECTED_COUNTS", {"I": 1, "C": 1, "S": 0, "P": 1})
    rows = ld.parse_fc_rows(SAMPLE_FC)
    rows[1]["successors"] = []
    problems = ld.validate(rows, ld.parse_waves(SAMPLE_WAVES), {"CA-101"})
    assert any("no successor" in p for p in problems)


def test_cycle_check_detects_unit_cycle():
    fc_rows = [{"fc_id": "FC-101", "successors": ["ZR-1"]}]
    unit_deps = {"ZR-1": ["ZR-2"], "ZR-2": ["ZR-1"]}
    problems = ld._cycle_check(fc_rows, unit_deps)
    assert any("cycle" in p for p in problems)


def test_cycle_check_clean():
    fc_rows = [{"fc_id": "FC-101", "successors": ["CA-101"]}]
    unit_deps = {"CA-101": [], "ZR-1": ["CA-101"]}
    assert ld._cycle_check(fc_rows, unit_deps) == []


@pytest.fixture
def fixture_repo(tmp_path):
    """Copies of the five real frozen sources under the same relative layout."""
    root = tmp_path / "repo"
    files = [
        ld.FC_REGISTRY,
        ld.TRANSITION_MATRIX,
        ld.COMPLETION_AUDIT,
        Path(
            "audit_review/2026-08-13_three_repo_completion_rebaseline_plan/"
            "completion_assurance_registry.md"
        ),
        Path(
            "audit_review/2026-08-13_zijin_data_lake_remediation_plan/work_unit_registry.md"
        ),
    ]
    for rel in files:
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, dest)
    return root


def test_real_frozen_build_and_verify(fixture_repo, tmp_path):
    out = tmp_path / "disposition.json"
    ld.build(fixture_repo, out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert len(payload["fc_entries"]) == 71
    assert payload["counts"] == {"I": 31, "C": 26, "S": 9, "P": 5}
    assert len(payload["waves"]) == 10
    assert len(payload["closure_items"]) == 5
    assert ld.verify(fixture_repo, out) == []


def test_real_source_drift_detected(fixture_repo, tmp_path):
    out = tmp_path / "disposition.json"
    ld.build(fixture_repo, out)
    src = fixture_repo / ld.FC_REGISTRY
    src.write_text(src.read_text(encoding="utf-8") + "# tampered\n", encoding="utf-8")
    problems = ld.verify(fixture_repo, out)
    assert any("source drift" in p for p in problems)
