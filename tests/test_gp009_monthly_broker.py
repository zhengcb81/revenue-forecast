"""GP-009 compatibility after retirement of the monthly broker audit."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

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


@pytest.mark.parametrize(
    ("script", "alert_flag", "action"),
    [
        ("monthly_broker_runner.py", "--alert", []),
        ("monthly_broker_schedule.py", "--alerts", ["run-monthly"]),
    ],
)
def test_legacy_commands_cannot_refresh_existing_audit(
    tmp_path: Path, script: str, alert_flag: str, action: list[str],
) -> None:
    # Before retirement this old synthetic catalog produced a success.
    catalog = _catalog(tmp_path, {"Archive source": ["normalized", "sections"]})
    ledger = tmp_path / "monthly_manifest.json"
    alert = tmp_path / "monthly_alert.jsonl"
    report = tmp_path / "previous" / "monthly_broker_report.json"
    report.parent.mkdir()
    ledger.write_bytes(b'{"ok":true,"latest_run_id":"previous"}\n')
    alert.write_bytes(b'{"status":"blocked","run_id":"earlier"}\n')
    report.write_bytes(b'{"ok":true,"run_id":"previous","corpus":7,"complete":7}\n')
    before = {f.relative_to(tmp_path): f.read_bytes() for f in tmp_path.rglob("*") if f.is_file()}
    proc = subprocess.run(
        [
            sys.executable, "-B", str(ROOT / "tools" / script),
            "--catalog", str(catalog), "--ledger", str(ledger),
            alert_flag, str(alert), *action,
        ],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=15,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "monthly_broker_audit_retired" in proc.stderr
    assert not proc.stdout
    after = {f.relative_to(tmp_path): f.read_bytes() for f in tmp_path.rglob("*") if f.is_file()}
    assert after == before


@pytest.mark.parametrize(
    ("script", "action"),
    [
        ("monthly_broker_runner.py", []),
        ("monthly_broker_schedule.py", ["run-monthly"]),
    ],
)
def test_retired_executables_do_not_open_owner_database(
    tmp_path: Path, script: str, action: list[str],
) -> None:
    # Audit events observe actual cold CLI behavior, including SQLite reads
    # that would be invisible to the bytes-at-rest check.
    catalog = _catalog(tmp_path, {"Archive source": ["normalized", "sections"]})
    ledger = tmp_path / "monthly_manifest.json"
    alert_flag = "--alert" if script == "monthly_broker_runner.py" else "--alerts"
    bootstrap = """\
import runpy
import sys
from pathlib import Path

def guard(event, args):
    if event == "sqlite3.connect":
        raise AssertionError("retired RF audit opened a database")
    if event == "open" and isinstance(args[0], str) and args[0].endswith("catalog.sqlite3"):
        raise AssertionError("retired RF audit opened the catalog")

script = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(script.parent))
sys.argv = sys.argv[1:]
sys.addaudithook(guard)
runpy.run_path(str(script), run_name="__main__")
"""
    proc = subprocess.run(
        [
            sys.executable, "-B", "-c", bootstrap, str(ROOT / "tools" / script),
            "--catalog", str(catalog), "--ledger", str(ledger),
            alert_flag, str(tmp_path / "alert.jsonl"), *action,
        ],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=15,
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "monthly_broker_audit_retired" in proc.stderr
    assert {f.name for f in tmp_path.iterdir()} == {catalog.name}


def test_head_uses_safe_directory_for_system_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GP-008 class: the SYSTEM scheduled task needs safe.directory=* or git
    returns an empty HEAD and the ledger records a green run with an empty
    triplet (observed 2026-09-08)."""
    captured: dict[str, list[str]] = {}

    class _Proc:
        returncode = 0
        stdout = "a" * 40 + "\n"

    def fake_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        captured["cmd"] = cmd
        return _Proc()

    sys.path.insert(0, str(ROOT / "tools"))
    import daily_t2_schedule as schedule

    monkeypatch.setattr(subprocess, "run", fake_run)
    schedule._head(ROOT)
    assert "safe.directory=*" in captured["cmd"]


def test_scheduler_exposes_positional_subcommands() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "monthly_broker_schedule.py"), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    for name in ("run-monthly", "register", "unregister", "query", "verify"):
        assert name in proc.stdout, name


def test_register_refuses_retired_task_before_using_windows(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    import monthly_broker_schedule as scheduler

    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):  # noqa: ANN001, ANN003
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert scheduler.cmd_register(None) == 2
    assert calls == []
    assert "monthly_broker_audit_retired" in capsys.readouterr().err


def test_query_and_unregister_still_use_the_existing_task(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    import monthly_broker_schedule as scheduler

    queried: list[str] = []
    commands: list[list[str]] = []

    def query(task: str) -> tuple[str, str]:
        queried.append(task)
        return "registered", "archived host action"

    def run(cmd, **kwargs):  # noqa: ANN001, ANN003
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(scheduler, "query_task_status", query)
    monkeypatch.setattr(subprocess, "run", run)
    assert scheduler.cmd_query(None) == 0  # type: ignore[arg-type]
    assert scheduler.cmd_unregister(None) == 0  # type: ignore[arg-type]
    assert queried == ["revenue_monthly_broker"]
    assert commands == [["schtasks", "/delete", "/tn", "revenue_monthly_broker", "/f"]]
    captured = capsys.readouterr()
    assert "status=registered detail=archived host action" in captured.out
    assert "unregistered revenue_monthly_broker" in captured.out


@pytest.mark.parametrize(("age", "status", "rc"), [(30, "fresh", 0), (40, "stale", 1)])
def test_verify_keeps_previous_historical_ledger_behavior(
    tmp_path: Path, age: int, status: str, rc: int,
) -> None:
    ledger = tmp_path / "monthly_manifest.json"
    started = (datetime.now(UTC) - timedelta(days=age)).isoformat()
    ledger.write_text(
        json.dumps(
            {
                "latest_run_id": "r",
                "started_at": started,
                "triplet": {"revenue": "", "filing": "", "wiki": ""},
                "ok": True,
                "report_path": "monthly-run-r",
            }
        ),
        encoding="utf-8",
    )
    before = ledger.read_bytes()
    proc = subprocess.run(
        [
            sys.executable, "-B", str(ROOT / "tools" / "monthly_broker_schedule.py"),
            "--ledger", str(ledger), "verify",
        ],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=15,
    )
    assert proc.returncode == rc, proc.stdout + proc.stderr
    assert f"last_run={status}" in proc.stdout and "release_gate=" in proc.stdout
    assert ledger.read_bytes() == before


class _QueryProc:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_query_task_status_unknown_when_unreadable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """2026-09-08: a SYSTEM task is not queryable without elevation; reporting
    a successfully registered task as 'missing' is a false signal."""
    sys.path.insert(0, str(ROOT / "tools"))
    import daily_t2_schedule as schedule

    monkeypatch.setattr(schedule, "sys", SimpleNamespace(platform="win32"))
    monkeypatch.setattr(
        schedule, "_schtasks",
        lambda args: _QueryProc(1, stderr="ERROR: Access is denied."),
    )
    status, detail = schedule.query_task_status("revenue_monthly_broker")
    assert status == "unknown"
    assert "elevated" in detail


def test_query_task_status_registered_and_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sys.path.insert(0, str(ROOT / "tools"))
    import daily_t2_schedule as schedule

    monkeypatch.setattr(schedule, "sys", SimpleNamespace(platform="win32"))
    monkeypatch.setattr(
        schedule, "_schtasks",
        lambda args: _QueryProc(0, stdout='TaskName\n\\revenue_monthly_broker\n'),
    )
    assert schedule.query_task_status("revenue_monthly_broker")[0] == "registered"

    monkeypatch.setattr(
        schedule, "_schtasks",
        lambda args: _QueryProc(0, stdout='TaskName\n\\some_other_task\n'),
    )
    assert schedule.query_task_status("revenue_monthly_broker")[0] == "missing"
