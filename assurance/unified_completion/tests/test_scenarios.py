"""CA-105 scenario registry: parsing, build/verify roundtrip, closure math."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

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
    report = sc.closure_report(payload, tmp_path)
    assert report["closure_ready"] is False
    assert report["unsatisfied"] == 197


def test_closure_report_green_when_filled(tmp_path):
    out = tmp_path / "registry.json"
    sc.build(REPO_ROOT, out)
    payload = json.loads(out.read_text(encoding="utf-8"))
    relative, digest, _path = _evidence(tmp_path)
    for info in payload["scenarios"].values():
        info["status"] = "passed"
        info["evidence_path"] = relative
        info["fixture_hash"] = digest
    assert sc.closure_report(payload, tmp_path)["closure_ready"] is True


def _single_scenario(info: dict) -> dict:
    return {"counts": {"unique_total": 1}, "scenarios": {"S-1": info}}


def _evidence(repo_root: Path) -> tuple[str, str, Path]:
    relative = "assurance/unified_completion/scenarios/evidence/S_1.json"
    path = repo_root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    content = b'{"proof":1}\n'
    path.write_bytes(content)
    return relative, hashlib.sha256(content).hexdigest(), path


def test_closure_report_replays_evidence_bytes_and_detects_tamper(tmp_path):
    relative, digest, path = _evidence(tmp_path)
    payload = _single_scenario(
        {"status": "passed", "evidence_path": relative, "fixture_hash": digest}
    )
    before = json.loads(json.dumps(payload))
    assert sc.closure_report(payload, repo_root=tmp_path)["closure_ready"] is True

    path.write_bytes(b'{"proof":2}\n')  # same-size replacement
    report = sc.closure_report(payload, repo_root=tmp_path)
    assert report["closure_ready"] is False
    assert any("mismatch" in item for item in report["unsatisfied_ids"])
    assert payload == before

    path.unlink()
    assert sc.closure_report(payload, repo_root=tmp_path)["closure_ready"] is False


def test_closure_report_rejects_evidence_path_outside_repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_bytes(b'{"proof":1}\n')
    payload = _single_scenario(
        {
            "status": "passed",
            "evidence_path": "../outside.json",
            "fixture_hash": hashlib.sha256(outside.read_bytes()).hexdigest(),
        }
    )
    report = sc.closure_report(payload, repo_root=root)
    assert report["closure_ready"] is False
    assert any("outside" in item for item in report["unsatisfied_ids"])

    payload["scenarios"]["S-1"]["evidence_path"] = "C:\\outside.json"
    report = sc.closure_report(payload, repo_root=root)
    assert report["closure_ready"] is False
    assert any("outside" in item for item in report["unsatisfied_ids"])


def test_closure_report_rejects_bare_passed_without_evidence(tmp_path):
    report = sc.closure_report(
        _single_scenario(
            {
                "status": "passed",
                "tier": "T1",
                "evidence_path": None,
                "fixture_hash": None,
                "oracle": None,
            }
        ), tmp_path
    )
    assert report["closure_ready"] is False
    assert any("evidence_path" in entry for entry in report["unsatisfied_ids"])


def test_closure_report_rejects_missing_hash_without_mutating_registry(tmp_path):
    payload = _single_scenario(
        {
            "status": "passed",
            "tier": "T1",
            "evidence_path": "evidence/S_1.json",
            "fixture_hash": None,
        }
    )
    before = json.loads(json.dumps(payload))
    report = sc.closure_report(payload, tmp_path)
    assert report["closure_ready"] is False
    assert report["evidence_hash_pending"] == 1
    assert any("fixture_hash" in entry for entry in report["unsatisfied_ids"])
    assert payload == before


def test_closure_report_does_not_count_recorded_hash_as_pending(tmp_path):
    relative, digest, _path = _evidence(tmp_path)
    report = sc.closure_report(
        _single_scenario(
            {
                "status": "passed",
                "tier": "T1",
                "evidence_path": relative,
                "fixture_hash": digest,
            }
        ), tmp_path
    )
    assert report["closure_ready"] is True
    assert report["evidence_hash_pending"] == 0


def test_closure_report_rejects_malformed_fixture_hash(tmp_path):
    report = sc.closure_report(
        _single_scenario(
            {
                "status": "passed",
                "evidence_path": "evidence/S_1.json",
                "fixture_hash": "not-a-sha256",
            }
        ), tmp_path
    )
    assert report["closure_ready"] is False
    assert any("SHA-256" in entry for entry in report["unsatisfied_ids"])


def test_closure_report_rejects_wrong_capability_evidence(tmp_path):
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
        ), tmp_path
    )
    assert report["closure_ready"] is False
    assert any("deadline" in entry for entry in report["unsatisfied_ids"])


def test_closure_report_accepts_covering_capability(tmp_path):
    relative, digest, _path = _evidence(tmp_path)
    report = sc.closure_report(
        _single_scenario(
            {
                "status": "passed",
                "tier": "T1",
                "evidence_path": relative,
                "fixture_hash": digest,
                "required_capability": "deadline",
                "covered_capabilities": ["deadline"],
            }
        ), tmp_path
    )
    assert report["closure_ready"] is True


def test_closure_report_rejects_empty_oracle_content(tmp_path):
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
        report = sc.closure_report(_single_scenario(dict(base, oracle=oracle)), tmp_path)
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
