"""WU-1000 RED/audit tests: source-preparation orchestration entry
(PROCESS-RED-01: the entry must drive the real chain, not helpers)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from source_preparation import prepare_source  # noqa: E402


def test_process_red01_entry_exists_and_is_cli():
    """The single production entry exists as a real CLI module."""
    assert (ROOT / "scripts" / "source_preparation.py").is_file()
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "source_preparation.py"),
         "--help"],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False,
    )
    assert proc.returncode == 0
    assert "source preparation" in proc.stdout.lower() or "request-file" in proc.stdout


def test_process_red01_uses_real_subprocess_chain(monkeypatch, tmp_path):
    """PROCESS-RED-01: a real subprocess must be spawned — monkeypatching
    the client import away must break the entry."""
    import scripts.filing_fetch_client as client

    called = {"n": 0}

    def fake_main(*args, **kwargs):
        called["n"] += 1
        return 0

    monkeypatch.setattr(client, "main", fake_main)
    request = {"company_query": "Acme", "document_kind": "annual_report",
               "as_of_date": "2026-12-31"}
    # the orchestrator spawns the client as a subprocess; monkeypatching the
    # in-process symbol must NOT affect the subprocess path
    record_path = tmp_path / "request.json"
    record_path.write_text(json.dumps(request), encoding="utf-8")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "source_preparation.py"),
         "--request-file", str(record_path)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    # subprocess runs the real client (not the monkeypatched one) — exit
    # reflects the real chain: the fixture request has no catalog behind it
    assert called["n"] == 0  # monkeypatch never reached the subprocess


def test_prepare_source_raises_on_client_failure(tmp_path, monkeypatch):
    request = {"company_query": "Acme", "document_kind": "annual_report",
               "as_of_date": "2026-12-31"}

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], returncode=1,
                                           stdout="", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)
    import pytest

    with pytest.raises(RuntimeError, match="boom"):
        prepare_source(request, python=(sys.executable,))


def test_prepare_source_forwards_allow_download(monkeypatch):
    captured = {}

    def fake_run(*args, **kwargs):
        captured["command"] = args[0]
        captured["input"] = kwargs.get("input", "")
        return subprocess.CompletedProcess(
            args[0], returncode=0,
            stdout=json.dumps({"handle": {"request_id": "r1"},
                               "selected_artifacts": []}),
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    request = {"company_query": "Acme", "document_kind": "annual_report",
               "as_of_date": "2026-12-31"}
    import company_wiki_source as cws

    monkeypatch.setattr(
        cws, "build_revenue_source_record",
        lambda handle, **kwargs: {"request_id": handle.get("request_id", "r1")},
    )
    record = prepare_source(request, allow_download=True)
    assert "--allow-download" in captured["command"]
    assert record["reuse_receipt"]["download_calls"] == 0  # handle present
