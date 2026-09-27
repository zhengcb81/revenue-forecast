"""CA-105 scenario registry: parsing, build/verify roundtrip, closure math."""

from __future__ import annotations

import json
import shutil

import pytest

import uc.scenarios as sc
from conftest import REPO_ROOT


def test_extract_ids_from_real_matrices():
    old_ids = sc._extract_ids((REPO_ROOT / sc.OLD_MATRIX).read_text(encoding="utf-8"))
    new_ids = sc._extract_ids((REPO_ROOT / sc.NEW_MATRIX).read_text(encoding="utf-8"))
    assert len(old_ids) == 95
    assert len(new_ids) == 102
    assert not (set(old_ids) & set(new_ids))


def test_extract_tiered_rows():
    sample = (
        "| READ-01 | T0/T1 | desc | oracle |\n"
        "| READ-02 | T1 | desc | oracle |\n"
        "| BR-01 | 研报场景 | desc | oracle |\n"
    )
    tiers = sc._extract_tiered(sample)
    assert tiers == {"READ-01": "T0/T1", "READ-02": "T1"}


def test_real_build_and_verify(tmp_path):
    out = tmp_path / "registry.json"
    sc.build(REPO_ROOT, out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["counts"] == {"old95": 95, "new102": 102, "unique_total": 197}
    assert len(payload["scenarios"]) == 197
    assert sc.verify(REPO_ROOT, out) == []


def test_closure_report_red_until_filled(tmp_path):
    out = tmp_path / "registry.json"
    sc.build(REPO_ROOT, out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    report = sc.closure_report(payload)
    assert report["closure_ready"] is False
    assert report["unsatisfied"] == 197


def test_closure_report_green_when_filled(tmp_path):
    out = tmp_path / "registry.json"
    sc.build(REPO_ROOT, out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    for info in payload["scenarios"].values():
        info["status"] = "passed"
        info["evidence_path"] = "evidence/filled.json"
        info["fixture_hash"] = "ab" * 32
    assert sc.closure_report(payload)["closure_ready"] is True


def _single_scenario(info: dict) -> dict:
    return {"counts": {"unique_total": 1}, "scenarios": {"S-1": info}}


def test_closure_report_rejects_bare_passed_without_evidence():
    report = sc.closure_report(
        _single_scenario(
            {
                "status": "passed",
                "tier": "T1",
                "evidence_path": None,
                "fixture_hash": None,
                "oracle": None,
            }
        )
    )
    assert report["closure_ready"] is False
    assert any("evidence_path" in entry for entry in report["unsatisfied_ids"])


def test_closure_report_rejects_missing_hash_without_mutating_registry():
    payload = _single_scenario(
        {
            "status": "passed",
            "tier": "T1",
            "evidence_path": "evidence/S_1.json",
            "fixture_hash": None,
        }
    )
    before = json.loads(json.dumps(payload))
    report = sc.closure_report(payload)
    assert report["closure_ready"] is False
    assert report["evidence_hash_pending"] == 1
    assert any("fixture_hash" in entry for entry in report["unsatisfied_ids"])
    assert payload == before


def test_closure_report_does_not_count_recorded_hash_as_pending():
    report = sc.closure_report(
        _single_scenario(
            {
                "status": "passed",
                "tier": "T1",
                "evidence_path": "evidence/S_1.json",
                "fixture_hash": "ab" * 32,
            }
        )
    )
    assert report["closure_ready"] is True
    assert report["evidence_hash_pending"] == 0


def test_closure_report_rejects_malformed_fixture_hash():
    report = sc.closure_report(
        _single_scenario(
            {
                "status": "passed",
                "evidence_path": "evidence/S_1.json",
                "fixture_hash": "not-a-sha256",
            }
        )
    )
    assert report["closure_ready"] is False
    assert any("SHA-256" in entry for entry in report["unsatisfied_ids"])


def test_closure_report_rejects_wrong_capability_evidence():
    report = sc.closure_report(
        _single_scenario(
            {
                "status": "passed",
                "tier": "T1",
                "evidence_path": "evidence/S_1.json",
                "fixture_hash": "ab" * 32,
                "required_capability": "deadline",
                "covered_capabilities": ["artifact"],
            }
        )
    )
    assert report["closure_ready"] is False
    assert any("deadline" in entry for entry in report["unsatisfied_ids"])


def test_closure_report_accepts_covering_capability():
    report = sc.closure_report(
        _single_scenario(
            {
                "status": "passed",
                "tier": "T1",
                "evidence_path": "evidence/S_1.json",
                "fixture_hash": "ab" * 32,
                "required_capability": "deadline",
                "covered_capabilities": ["deadline"],
            }
        )
    )
    assert report["closure_ready"] is True


def test_closure_report_rejects_empty_oracle_content():
    base = {
        "status": "passed",
        "tier": "T1",
        "evidence_path": "evidence/S_1.json",
        "fixture_hash": "cd" * 32,
    }
    for oracle in (
        {"validated_commands": [], "invariants": ["i1"]},
        {"validated_commands": ["c1"], "invariants": []},
        {"validated_commands": [], "invariants": []},
    ):
        report = sc.closure_report(_single_scenario(dict(base, oracle=oracle)))
        assert report["closure_ready"] is False, oracle


@pytest.fixture
def fixture_repo(tmp_path):
    root = tmp_path / "repo"
    for rel in (sc.OLD_MATRIX, sc.NEW_MATRIX):
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, dest)
    return root


def test_source_drift_detected(fixture_repo, tmp_path):
    out = tmp_path / "registry.json"
    sc.build(fixture_repo, out)
    src = fixture_repo / sc.NEW_MATRIX
    src.write_text(src.read_text(encoding="utf-8") + "# drift\n", encoding="utf-8")
    problems = sc.verify(fixture_repo, out)
    assert any("source drift" in p for p in problems)


def test_scenario_set_drift_detected(fixture_repo, tmp_path):
    out = tmp_path / "registry.json"
    sc.build(fixture_repo, out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    payload["scenarios"]["FAKE-01"] = {"source": "old95", "status": "pending"}
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    problems = sc.verify(fixture_repo, out)
    assert any("scenario set differs" in p for p in problems)
