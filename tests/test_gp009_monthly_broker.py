"""GP-009 / CA-206 C3: monthly broker-cohort audit + scheduling.

The monthly soak window needs a real monthly run whose ledger entry is
honest: the audit re-verifies the frozen Zijin broker cohort read-only and
fails closed when any corpus document lost its normalized/sections artifact.
These tests are hermetic (temp catalog, temp ledger).
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from daily_t2_schedule import read_ledger  # noqa: E402
from monthly_broker_runner import audit, run  # noqa: E402

SCHEMA = """
CREATE TABLE documents (
    document_id TEXT PRIMARY KEY, title TEXT, document_kind TEXT
);
CREATE TABLE entities (entity_id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE document_entities (document_id TEXT, entity_id TEXT);
CREATE TABLE artifacts (
    artifact_id TEXT, document_id TEXT, artifact_role TEXT
);
"""


def _catalog(tmp_path: Path, documents: dict[str, list[str]]) -> Path:
    path = tmp_path / "catalog.sqlite3"
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.execute("INSERT INTO entities VALUES ('e1', '紫金矿业')")
    for index, (title, roles) in enumerate(documents.items()):
        document_id = f"doc-{index}"
        con.execute(
            "INSERT INTO documents VALUES (?, ?, 'broker_research')",
            (document_id, title),
        )
        con.execute("INSERT INTO document_entities VALUES (?, 'e1')", (document_id,))
        for role in roles:
            con.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?)",
                (f"{document_id}-{role}", document_id, role),
            )
    con.commit()
    con.close()
    return path


def test_audit_ok_when_every_document_has_required_roles(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path, {"报告A": ["normalized", "sections"]})
    result = audit(catalog)
    assert result["ok"] is True
    assert result["corpus"] == 1 and result["complete"] == 1


def test_audit_not_ok_when_a_document_lacks_sections(tmp_path: Path) -> None:
    catalog = _catalog(
        tmp_path,
        {"报告A": ["normalized", "sections"], "报告B": ["normalized"]},
    )
    result = audit(catalog)
    assert result["ok"] is False
    assert result["complete"] == 1
    assert result["incomplete"][0]["missing"] == ["sections"]


def test_audit_ignores_non_broker_and_other_entities(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path, {"报告A": ["normalized", "sections"]})
    con = sqlite3.connect(catalog)
    con.execute("INSERT INTO documents VALUES ('x', '年报', 'annual_report')")
    con.execute("INSERT INTO document_entities VALUES ('x', 'e1')")
    con.commit()
    con.close()
    assert audit(catalog)["corpus"] == 1


def test_audit_includes_title_matched_document_without_entity_link(
    tmp_path: Path,
) -> None:
    """GP-010 corpus: 长江证券's 紫金矿业-vs-陕西煤业 comparison is not
    entity-linked to 紫金矿业; a title match must still pull it in."""
    catalog = _catalog(tmp_path, {"报告A": ["normalized", "sections"]})
    con = sqlite3.connect(catalog)
    con.execute(
        "INSERT INTO documents VALUES ('doc-t', '煤炭行业：紫金矿业VS陕西煤业', "
        "'broker_research')"
    )
    con.execute(
        "INSERT INTO artifacts VALUES ('a1', 'doc-t', 'normalized'), "
        "('a2', 'doc-t', 'sections')"
    )
    con.commit()
    con.close()
    result = audit(catalog)
    assert result["corpus"] == 2 and result["ok"] is True


def test_run_writes_not_ok_ledger_and_alert(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path, {"报告B": ["normalized"]})
    ledger = tmp_path / "monthly_manifest.json"
    alert = tmp_path / "monthly_alert.jsonl"
    rc = run(catalog, ledger, alert, run_id="20261001T050000Z")
    assert rc == 1
    payload = read_ledger(ledger)
    assert payload is not None and payload["ok"] is False
    entries = [json.loads(line) for line in alert.read_text(encoding="utf-8").splitlines()]
    assert entries[-1]["status"] == "not-ok"
    assert entries[-1]["exit_code"] == 1


def test_run_writes_ok_ledger_without_alert(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path, {"报告A": ["normalized", "sections"]})
    ledger = tmp_path / "monthly_manifest.json"
    alert = tmp_path / "monthly_alert.jsonl"
    rc = run(catalog, ledger, alert, run_id="20261001T050000Z")
    assert rc == 0
    payload = read_ledger(ledger)
    assert payload is not None and payload["ok"] is True
    assert not alert.exists()


def test_run_blocked_when_catalog_missing(tmp_path: Path) -> None:
    ledger = tmp_path / "monthly_manifest.json"
    alert = tmp_path / "monthly_alert.jsonl"
    rc = run(tmp_path / "nope.sqlite3", ledger, alert, run_id="20261001T050000Z")
    assert rc == 2
    payload = read_ledger(ledger)
    assert payload is not None and payload["ok"] is False
    entry = json.loads(alert.read_text(encoding="utf-8").strip())
    assert entry["status"] == "blocked"


def test_scheduler_exposes_positional_subcommands() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "monthly_broker_schedule.py"), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    for name in ("run-monthly", "register", "unregister", "query", "verify"):
        assert name in proc.stdout, name


def test_register_action_uses_run_monthly_and_monthly_task(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression class (GP-008/GP-009): the registered Action must match the
    parser's positional subcommand; a bare ``--run-monthly`` flag broke the
    daily task once already."""
    captured: dict[str, list[str]] = {}

    class _Proc:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        captured["cmd"] = cmd
        return _Proc()

    monkeypatch.setattr(subprocess, "run", fake_run)
    sys.path.insert(0, str(ROOT / "tools"))
    import monthly_broker_schedule as scheduler

    rc = scheduler.cmd_register(None)  # type: ignore[arg-type]
    assert rc == 0
    script = captured["cmd"][-1]
    assert "run-monthly" in script
    assert "--run-monthly" not in script
    assert scheduler.MONTHLY_TASK in script


def test_verify_treats_30_day_old_ok_ledger_as_fresh(tmp_path: Path) -> None:
    ledger = tmp_path / "monthly_manifest.json"
    started = (datetime.now(UTC) - timedelta(days=30)).isoformat()
    ledger.write_text(
        json.dumps(
            {
                "latest_run_id": "r",
                "started_at": started,
                "triplet": {"revenue": "", "filing": "", "wiki": ""},
                "ok": True,
                "report_path": "p",
            }
        ),
        encoding="utf-8",
    )
    sys.path.insert(0, str(ROOT / "tools"))
    from daily_t2_schedule import freshness_status

    status, _ = freshness_status(read_ledger(ledger), max_age_hours=35 * 24)
    assert status == "fresh"
    status, _ = freshness_status(read_ledger(ledger), max_age_hours=20 * 24)
    assert status == "stale"
