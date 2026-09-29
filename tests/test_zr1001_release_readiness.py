"""ZR-1001 acceptance tests: automated release readiness.

  C1  fingerprints: three repo HEADs recorded and consistent (real git).
  C2  read-only catalog probes and actual scenario evidence bytes.
  C3  capacity: assurance/runs within the frozen space budget.
  C4  backup + rollback dry-run: backup dir readable; rollback point written
      with current HEADs (nothing executes).
  C5  a separate manual authorization file cannot decide readiness.
"""

from __future__ import annotations

import json
import hashlib
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "assurance" / "unified_completion"))

import release_readiness as rr  # noqa: E402
from uc import scenarios  # noqa: E402


# ---------------------------------------------------------------------------
# C1 — fingerprints
# ---------------------------------------------------------------------------


def test_c1_three_repo_heads_recorded():
    fps = rr.head_fingerprints()
    assert set(fps) == {"revenue", "filing", "wiki"}
    for name, sha in fps.items():
        assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha), (
            f"{name} HEAD not a 40-hex sha: {sha}")


def test_c1_missing_fingerprint_blocks_readiness(monkeypatch):
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {
        "revenue": "a" * 40, "filing": "", "wiki": "b" * 40,
    })
    monkeypatch.setattr(rr, "catalog_integrity", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "scenario_evidence_integrity", lambda: (True, "ok"), raising=False)
    monkeypatch.setattr(rr, "capacity_ok", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "backup_readable", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "write_rollback_point", lambda _heads=None: (True, "ok"))
    assert rr.run_checks()["fingerprints"]["ok"] is False


def test_c1_rollback_uses_the_same_head_snapshot(tmp_path, monkeypatch):
    heads = {
        "revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40,
    }
    calls = 0

    def one_snapshot():
        nonlocal calls
        calls += 1
        assert calls == 1, "readiness must pin one HEAD triplet"
        return heads

    monkeypatch.setattr(rr, "head_fingerprints", one_snapshot)
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    rollback = tmp_path / "rollback_manifest.json"
    monkeypatch.setattr(rr, "ROLLBACK_PATH", rollback)
    monkeypatch.setattr(rr, "catalog_integrity", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "scenario_evidence_integrity", lambda: (True, "ok"), raising=False)
    monkeypatch.setattr(rr, "capacity_ok", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "backup_readable", lambda: (True, "ok"))
    result = rr.run_checks()
    assert result["fingerprints"]["ok"] is True
    assert result["rollback"]["ok"] is True
    assert json.loads(rollback.read_text(encoding="utf-8"))["heads"] == heads


# ---------------------------------------------------------------------------
# C2 — catalog integrity
# ---------------------------------------------------------------------------


def test_c2_catalog_integrity_ok(tmp_path, monkeypatch):
    catalog = tmp_path / "catalog.sqlite3"
    with sqlite3.connect(catalog) as con:
        for table in ("documents", "sources", "locations"):
            con.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
    monkeypatch.setattr(rr, "CATALOG", catalog)
    ok, detail = rr.catalog_integrity()
    assert ok, detail


def test_c2_tampered_scenario_evidence_blocks_readiness(tmp_path, monkeypatch):
    repo = tmp_path / "revenue"
    for matrix in (scenarios.OLD_MATRIX, scenarios.NEW_MATRIX):
        target = repo / matrix
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / matrix, target)
    registry = repo / "assurance/unified_completion/scenarios/scenario_registry.json"
    registry.parent.mkdir(parents=True)
    scenarios.build(repo, registry)
    evidence_rel = "assurance/unified_completion/scenarios/evidence/proof.json"
    evidence = repo / evidence_rel
    evidence.parent.mkdir(parents=True)
    evidence.write_bytes(b'{"proof":1}\n')
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    payload = json.loads(registry.read_text(encoding="utf-8"))
    for row in payload["scenarios"].values():
        row.update(status="passed", evidence_path=evidence_rel, fixture_hash=digest)
    next(iter(payload["scenarios"].values()))["fixture_hash"] = "0" * 64
    registry.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(rr, "ROOT", repo)
    monkeypatch.setattr(rr, "SCENARIO_REGISTRY_PATH", registry, raising=False)
    ok, detail = rr.scenario_evidence_integrity()
    assert ok is False
    assert "1" in detail


# ---------------------------------------------------------------------------
# C3 — capacity budget
# ---------------------------------------------------------------------------


def test_c3_capacity_within_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    (tmp_path / "report.json").write_text("{}", encoding="utf-8")
    ok, detail = rr.capacity_ok()
    assert ok, detail
    assert "MB" in detail


def test_c3_one_byte_over_exact_budget_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(rr, "BUDGET_RUNS_MB", 0)
    (tmp_path / "report.json").write_bytes(b"x")
    ok, _detail = rr.capacity_ok()
    assert ok is False


# ---------------------------------------------------------------------------
# C4 — backup readability + rollback dry-run
# ---------------------------------------------------------------------------


def test_c4_backup_readable(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "BACKUP_DIR", tmp_path)
    ok, detail = rr.backup_readable()
    assert ok, detail


def test_c4_rollback_point_written(tmp_path, monkeypatch):
    path = tmp_path / "rollback_manifest.json"
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(rr, "ROLLBACK_PATH", path)
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {
        "revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40,
    })
    ok, detail = rr.write_rollback_point()
    assert ok, detail
    data = json.loads(path.read_text(encoding="utf-8"))
    assert set(data["heads"]) == {"revenue", "filing", "wiki"}
    assert data["recorded_at_utc"]


def test_c4_bad_fingerprint_does_not_write_rollback_point(tmp_path, monkeypatch):
    path = tmp_path / "rollback_manifest.json"
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(rr, "ROLLBACK_PATH", path)
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {
        "revenue": "a" * 40, "filing": "bad", "wiki": "c" * 40,
    })
    ok, _detail = rr.write_rollback_point()
    assert ok is False
    assert not path.exists()


# ---------------------------------------------------------------------------
# C5 — no human receipt gate
# ---------------------------------------------------------------------------


def test_c5_missing_manual_receipt_does_not_block_readiness(
    tmp_path, monkeypatch,
):
    monkeypatch.setattr(
        rr, "AUTH_PATH", tmp_path / "release_authorization.json", raising=False,
    )
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {
        "revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40,
    })
    monkeypatch.setattr(rr, "catalog_integrity", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "scenario_evidence_integrity", lambda: (True, "ok"), raising=False)
    monkeypatch.setattr(rr, "capacity_ok", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "backup_readable", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "write_rollback_point", lambda _heads=None: (True, "ok"))
    result = rr.run_checks()
    assert "authorization" not in result
    assert all(gate["ok"] for gate in result.values())


def test_c5_cli_reports_all_gates(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["release_readiness.py"])
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {
        "revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40,
    })
    monkeypatch.setattr(rr, "catalog_integrity", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "scenario_evidence_integrity", lambda: (True, "ok"), raising=False)
    monkeypatch.setattr(rr, "capacity_ok", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "backup_readable", lambda: (True, "ok"))
    monkeypatch.setattr(rr, "write_rollback_point", lambda _heads=None: (True, "ok"))
    assert rr.main() == 0
    out = capsys.readouterr().out
    for gate in ("fingerprints", "integrity", "scenario_evidence", "capacity", "backup",
                 "rollback"):
        assert gate in out, f"gate {gate} missing from CLI output"
    assert "authorization" not in out


def test_c5_issue_auth_command_is_removed(tmp_path, monkeypatch):
    auth_path = tmp_path / "release_authorization.json"
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(rr, "AUTH_PATH", auth_path, raising=False)
    monkeypatch.setattr(
        sys, "argv", ["release_readiness.py", "issue-auth", "--owner", "x", "--reason", "y"],
    )
    with pytest.raises(SystemExit) as exc:
        rr.main()
    assert exc.value.code == 2
    assert not auth_path.exists()
