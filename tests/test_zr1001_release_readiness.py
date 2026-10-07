"""ZR-1001 acceptance tests: release readiness is optional and read-only.

C1  default fingerprints this repository only; sibling HEADs are
    ``not_supplied`` and never block.  An explicitly supplied HEAD SHA that
    is malformed, unknown, or does not match the live HEAD is RED.
C2  catalog and scenario registry are explicit versioned inputs: absent ->
    ``not_supplied`` (never "verified"); supplied -> revalidated with the
    existing RF tooling; a bad supplied input is RED.  The default run must
    never open a neighbour repository's internal SQLite.
C3  capacity is a numeric diagnostic (no 2 GB gate) unless an explicit
    budget is supplied.
C4  backup / rollback: check-only writes zero files; ``--backup-dir`` is
    probed read-only (no ``.read-probe``); ``--record-rollback`` is the only
    writer and rejects a bad SHA without writing.
C5  no human receipt gate; the CLI reports one accurate status per gate.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "assurance" / "unified_completion"))

import release_readiness as rr  # noqa: E402
from uc import scenarios  # noqa: E402

REPO_REGISTRY = (
    ROOT / "assurance" / "unified_completion" / "scenarios" / "scenario_registry.json"
)


def _dir_state(directory: Path) -> dict[str, tuple[str, int]]:
    state: dict[str, tuple[str, int]] = {}
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        stat = path.stat()
        state[path.relative_to(directory).as_posix()] = (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            stat.st_mtime_ns,
        )
    return state


# ---------------------------------------------------------------------------
# C1 — fingerprints
# ---------------------------------------------------------------------------


def test_c1_default_never_requires_sibling_heads(monkeypatch):
    monkeypatch.setattr(
        rr,
        "head_fingerprints",
        lambda: {"revenue": "a" * 40, "filing": "", "wiki": ""},
    )
    gate = rr.run_checks()["fingerprints"]
    assert gate["ok"] is True
    assert gate["status"] == "not_supplied"
    assert set(gate["problems"]) == set()


def test_c1_explicit_bad_sha_is_red(monkeypatch):
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {"revenue": "a" * 40})
    gate = rr.run_checks(expect_heads={"revenue": "not-a-sha"})["fingerprints"]
    assert gate["ok"] is False
    assert gate["status"] == "red"
    assert any("not-a-sha" in problem for problem in gate["problems"])


def test_c1_explicit_mismatched_sha_is_red(monkeypatch):
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {"revenue": "a" * 40})
    gate = rr.run_checks(expect_heads={"revenue": "b" * 40})["fingerprints"]
    assert gate["ok"] is False
    assert gate["status"] == "red"


def test_c1_unknown_repo_expectation_is_red(monkeypatch):
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {"revenue": "a" * 40})
    gate = rr.run_checks(expect_heads={"stockwiki": "a" * 40})["fingerprints"]
    assert gate["ok"] is False
    assert any("unknown repo" in problem for problem in gate["problems"])


def test_c1_own_head_missing_is_red(monkeypatch):
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {"revenue": ""})
    gate = rr.run_checks()["fingerprints"]
    assert gate["ok"] is False
    assert gate["status"] == "red"


def test_c1_head_fingerprints_reads_real_repos():
    fps = rr.head_fingerprints()
    assert "revenue" in fps
    own = fps["revenue"]
    assert len(own) == 40 and all(c in "0123456789abcdef" for c in own)


# ---------------------------------------------------------------------------
# C2 — explicit versioned inputs (catalog / scenario registry)
# ---------------------------------------------------------------------------


def test_c2_default_does_not_open_neighbour_catalog(monkeypatch):
    def explode(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("default readiness must not open a SQLite catalog")

    monkeypatch.setattr(rr.sqlite3, "connect", explode)
    gates = rr.run_checks()
    assert gates["integrity"]["status"] == "not_supplied"
    assert gates["integrity"]["ok"] is True


def test_c2_supplied_catalog_is_probed_read_only(tmp_path):
    catalog = tmp_path / "catalog.sqlite3"
    with sqlite3.connect(catalog) as con:
        for table in ("documents", "sources", "locations"):
            con.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
            con.execute(f"INSERT INTO {table} VALUES (1)")
    gate = rr.run_checks(catalog=catalog)["integrity"]
    assert gate["ok"] is True, gate
    assert gate["status"] == "ok"
    assert "documents=1" in gate["detail"]


def test_c2_missing_supplied_catalog_is_red(tmp_path):
    gate = rr.run_checks(catalog=tmp_path / "absent.sqlite3")["integrity"]
    assert gate["ok"] is False
    assert gate["status"] == "red"


def test_c2_corrupt_supplied_catalog_is_red(tmp_path):
    catalog = tmp_path / "catalog.sqlite3"
    catalog.write_bytes(b"not a sqlite database at all")
    gate = rr.run_checks(catalog=catalog)["integrity"]
    assert gate["ok"] is False
    assert gate["status"] == "red"


def test_c2_default_registry_is_not_supplied():
    gate = rr.run_checks()["scenario_evidence"]
    assert gate["ok"] is True
    assert gate["status"] == "not_supplied"
    assert "not_supplied" in gate["detail"]


def test_c2_supplied_legal_registry_runs_the_existing_rf_verifier():
    gate = rr.run_checks(registry=REPO_REGISTRY)["scenario_evidence"]
    assert gate["ok"] is True, gate
    assert gate["status"] == "ok"
    assert "scenarios" in gate["detail"]


def test_c2_supplied_tampered_registry_is_red(tmp_path):
    repo = tmp_path / "revenue"
    for matrix in (scenarios.OLD_MATRIX, scenarios.NEW_MATRIX):
        target = repo / matrix
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / matrix).read_bytes())
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

    gate = rr.run_checks(registry=registry, registry_root=repo)["scenario_evidence"]
    assert gate["ok"] is False
    assert gate["status"] == "red"


def test_c2_missing_supplied_registry_is_red(tmp_path):
    gate = rr.run_checks(registry=tmp_path / "absent.json")["scenario_evidence"]
    assert gate["ok"] is False
    assert gate["status"] == "red"


# ---------------------------------------------------------------------------
# C3 — capacity is a diagnostic number
# ---------------------------------------------------------------------------


def test_c3_capacity_is_a_diagnostic_without_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    (tmp_path / "report.json").write_text("{}", encoding="utf-8")
    gate = rr.run_checks()["capacity"]
    assert gate["ok"] is True
    assert gate["status"] == "diagnostic"
    assert "MB" in gate["detail"]


def test_c3_explicit_budget_over_is_red(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    (tmp_path / "report.json").write_bytes(b"x")
    gate = rr.run_checks(budget_mb=0)["capacity"]
    assert gate["ok"] is False
    assert gate["status"] == "red"


def test_c3_explicit_budget_met_is_ok(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    (tmp_path / "report.json").write_bytes(b"x")
    gate = rr.run_checks(budget_mb=1)["capacity"]
    assert gate["ok"] is True
    assert gate["status"] == "ok"


# ---------------------------------------------------------------------------
# C4 — backup / rollback stay out of check-only
# ---------------------------------------------------------------------------


def test_c4_default_does_not_require_backup(tmp_path):
    gate = rr.run_checks()["backup"]
    assert gate["ok"] is True
    assert gate["status"] == "not_supplied"


def test_c4_supplied_backup_dir_is_probed_read_only(tmp_path):
    sentinel = tmp_path / "keep.txt"
    sentinel.write_bytes(b"owner bytes")
    before = _dir_state(tmp_path)
    gate = rr.run_checks(backup_dir=tmp_path)["backup"]
    assert gate["ok"] is True, gate
    assert gate["status"] == "ok"
    assert _dir_state(tmp_path) == before


def test_c4_missing_supplied_backup_dir_is_red(tmp_path):
    gate = rr.run_checks(backup_dir=tmp_path / "absent")["backup"]
    assert gate["ok"] is False
    assert gate["status"] == "red"


def test_c4_default_rollback_writes_nothing(tmp_path):
    target = tmp_path / "rollback_manifest.json"
    gate = rr.run_checks(record_rollback=None, rollback_path=target)["rollback"]
    assert gate["ok"] is True
    assert gate["status"] == "not_supplied"
    assert not target.exists()


def test_c4_explicit_rollback_records_the_head_snapshot(tmp_path, monkeypatch):
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {"revenue": "a" * 40})
    target = tmp_path / "rollback_manifest.json"
    gate = rr.run_checks(record_rollback=target, rollback_path=target)["rollback"]
    assert gate["ok"] is True, gate
    recorded = json.loads(target.read_text(encoding="utf-8"))
    assert recorded["heads"] == {"revenue": "a" * 40}
    assert recorded["recorded_at_utc"]


def test_c4_bad_fingerprint_does_not_write_rollback_point(tmp_path, monkeypatch):
    path = tmp_path / "rollback_manifest.json"
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(rr, "ROLLBACK_PATH", path)
    monkeypatch.setattr(
        rr,
        "head_fingerprints",
        lambda: {
            "revenue": "a" * 40,
            "filing": "bad",
            "wiki": "c" * 40,
        },
    )
    ok, _detail = rr.write_rollback_point()
    assert ok is False
    assert not path.exists()


def test_c4_rollback_point_written(tmp_path, monkeypatch):
    path = tmp_path / "rollback_manifest.json"
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(rr, "ROLLBACK_PATH", path)
    monkeypatch.setattr(
        rr,
        "head_fingerprints",
        lambda: {
            "revenue": "a" * 40,
            "filing": "b" * 40,
            "wiki": "c" * 40,
        },
    )
    ok, detail = rr.write_rollback_point()
    assert ok, detail
    data = json.loads(path.read_text(encoding="utf-8"))
    assert set(data["heads"]) == {"revenue", "filing", "wiki"}


def test_c4_check_only_writes_zero_files(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "evidence.json").write_text("{}", encoding="utf-8")
    backup = tmp_path / "backup"
    backup.mkdir()
    (backup / "README.md").write_text("owner", encoding="utf-8")
    monkeypatch.setattr(rr, "RUNS_DIR", runs)
    monkeypatch.setattr(rr, "ROLLBACK_PATH", runs / "rollback_manifest.json")
    monkeypatch.setattr(rr, "BACKUP_DIR", backup)
    before_runs = _dir_state(runs)
    before_backup = _dir_state(backup)
    rr.run_checks()
    assert _dir_state(runs) == before_runs
    assert _dir_state(backup) == before_backup


# ---------------------------------------------------------------------------
# C5 — no human receipt gate; accurate CLI statuses
# ---------------------------------------------------------------------------


def test_c5_no_authorization_gate(monkeypatch):
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {"revenue": "a" * 40})
    result = rr.run_checks()
    assert "authorization" not in result
    assert all(gate["ok"] for gate in result.values())


def test_c5_every_gate_reports_ok_or_red_status(monkeypatch):
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {"revenue": "a" * 40})
    result = rr.run_checks()
    assert set(result) == {
        "fingerprints",
        "integrity",
        "scenario_evidence",
        "capacity",
        "backup",
        "rollback",
    }
    for name, gate in result.items():
        assert gate["status"] in {"ok", "red", "not_supplied", "diagnostic"}, name
        assert gate["ok"] is True, (name, gate)
        assert isinstance(gate["problems"], list), name


def test_c5_cli_reports_every_gate_status(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["release_readiness.py"])
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {"revenue": "a" * 40})
    assert rr.main() == 0
    out = capsys.readouterr().out
    for gate in (
        "fingerprints",
        "integrity",
        "scenario_evidence",
        "capacity",
        "backup",
        "rollback",
    ):
        assert gate in out, f"gate {gate} missing from CLI output"
    assert "NOT_SUPPLIED" in out
    assert "authorization" not in out


def test_c5_cli_json_is_machine_readable(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["release_readiness.py", "--json"])
    monkeypatch.setattr(rr, "head_fingerprints", lambda: {"revenue": "a" * 40})
    assert rr.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert set(payload) == {
        "fingerprints",
        "integrity",
        "scenario_evidence",
        "capacity",
        "backup",
        "rollback",
    }


def test_c5_issue_auth_command_is_removed(tmp_path, monkeypatch):
    auth_path = tmp_path / "release_authorization.json"
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(rr, "AUTH_PATH", auth_path, raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        ["release_readiness.py", "issue-auth", "--owner", "x", "--reason", "y"],
    )
    with pytest.raises(SystemExit) as exc:
        rr.main()
    assert exc.value.code == 2
    assert not auth_path.exists()


def test_c5_malformed_expect_head_is_a_configuration_error(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["release_readiness.py", "--expect-head", "oops"])
    with pytest.raises(SystemExit) as exc:
        rr.main()
    assert exc.value.code == 2
