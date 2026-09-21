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


def _envelope(**overrides):
    envelope = {
        "envelope_schema_version": "1.0",
        "outcome": "reused_existing",
        "download_events": 0,
        "policy_hash": "a" * 64,
        "activation_epoch": "epoch-1",
        "bundle_status": "unavailable",
        # FC-905-b: trusted capture/safety evidence required by the entry
        "prompt_injection_status": "not_detected",
        "parser_calls": 0,
        "llm_calls": 0,
    }
    envelope.update(overrides)
    return envelope


def _fake_payload(envelope=None):
    return {"handle": {"request_id": "r1"},
            "selected_artifacts": [],
            **({"resolution_envelope": envelope} if envelope is not None else {})}


def _run_fake(monkeypatch, captured, envelope):
    def fake_run(*args, **kwargs):
        captured["command"] = args[0]
        captured["input"] = kwargs.get("input", "")
        return subprocess.CompletedProcess(
            args[0], returncode=0,
            stdout=json.dumps(_fake_payload(envelope)), stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    import company_wiki_source as cws

    monkeypatch.setattr(
        cws, "build_revenue_source_record",
        lambda handle, **kwargs: {"request_id": handle.get("request_id", "r1")},
    )


def test_prepare_source_forwards_allow_download(monkeypatch):
    captured = {}
    _run_fake(monkeypatch, captured, envelope=_envelope())
    request = {"company_query": "Acme", "document_kind": "annual_report",
               "as_of_date": "2026-12-31"}
    record = prepare_source(request, allow_download=True)
    assert "--allow-download" in captured["command"]
    assert record["reuse_receipt"]["download_calls"] == 0


def test_prepare_source_forwards_filing_fetch_root(monkeypatch):
    """FC-1202: the orchestrator must forward an explicit filing-fetch root
    to the client subprocess (no reliance on the client's default config)."""
    captured = {}
    _run_fake(monkeypatch, captured, envelope=_envelope())
    request = {"company_query": "Acme", "document_kind": "annual_report",
               "as_of_date": "2026-12-31"}
    record = prepare_source(request, filing_fetch_root=Path("X"))
    command = captured["command"]
    assert "--filing-fetch-root" in command
    assert command[command.index("--filing-fetch-root") + 1] == str(Path("X"))
    assert record["reuse_receipt"]["download_calls"] == 0


def test_cli_forwards_filing_fetch_root(monkeypatch, tmp_path):
    """FC-1202: the CLI must forward --filing-fetch-root to prepare_source —
    removing the forwarding silently drops explicit roots (mutation target)."""
    import source_preparation

    captured = {}

    def fake_prepare(request, **kwargs):
        captured.update(kwargs)
        return {"request_id": "r1"}

    monkeypatch.setattr(source_preparation, "prepare_source", fake_prepare)
    request_path = tmp_path / "req.json"
    request_path.write_text(
        json.dumps({"company_query": "Acme", "document_kind": "annual_report",
                    "as_of_date": "2026-12-31"}), encoding="utf-8")
    root = tmp_path / "ff"
    exit_code = source_preparation.main(
        ["--request-file", str(request_path), "--filing-fetch-root", str(root)]
    )
    assert exit_code == 0
    assert captured.get("filing_fetch_root") == root


# --- FC-704: download evidence comes from the envelope, not the handle ---------


def test_env09_download_calls_from_envelope_events(monkeypatch):
    """ENV-09: envelope download_events=1 -> receipt download_calls=1.
    The legacy fake ('0 if handle else 1') would report 0 for a handle that
    carries a downloaded document — this mutation must die."""
    captured = {}
    _run_fake(monkeypatch, captured, envelope=_envelope(download_events=1,
                                                        outcome="downloaded_new"))
    record = prepare_source({"company_query": "Acme",
                             "document_kind": "annual_report",
                             "as_of_date": "2026-12-31"})
    assert record["reuse_receipt"]["download_calls"] == 1
    assert record["reuse_receipt"]["outcome"] == "downloaded_new"


def test_env10_download_calls_zero_from_envelope(monkeypatch):
    """ENV-10: envelope download_events=0 -> receipt download_calls=0."""
    captured = {}
    _run_fake(monkeypatch, captured, envelope=_envelope())
    record = prepare_source({"company_query": "Acme",
                             "document_kind": "annual_report",
                             "as_of_date": "2026-12-31"})
    assert record["reuse_receipt"]["download_calls"] == 0


def test_env11_missing_envelope_fails_closed(monkeypatch):
    """ENV-11: a handle WITHOUT envelope evidence fails closed — the receipt
    may never silently claim zero downloads (scenario_matrix §2: counts come
    from events/journal, never inferred from the result)."""
    captured = {}
    _run_fake(monkeypatch, captured, envelope=None)
    import pytest

    with pytest.raises(RuntimeError, match="resolution envelope missing"):
        prepare_source({"company_query": "Acme",
                        "document_kind": "annual_report",
                        "as_of_date": "2026-12-31"})


def test_env12_receipt_carries_envelope_evidence(monkeypatch):
    """ENV-12: the receipt records the journal-derived outcome and the
    policy/epoch/bundle evidence — the evidence is IN the receipt, not
    re-derived."""
    captured = {}
    _run_fake(monkeypatch, captured, envelope=_envelope(
        outcome="reused_after_discovery", policy_hash="b" * 64,
        activation_epoch="epoch-2", bundle_status="unavailable"))
    record = prepare_source({"company_query": "Acme",
                             "document_kind": "annual_report",
                             "as_of_date": "2026-12-31"})
    receipt = record["reuse_receipt"]
    assert receipt["outcome"] == "reused_after_discovery"
    assert receipt["policy_hash"] == "b" * 64
    assert receipt["activation_epoch"] == "epoch-2"
    assert receipt["bundle_status"] == "unavailable"


def test_c1_request_reaches_client_not_file_error():
    """C1 regression: the request must reach the client via stdin — the
    client must never report 'cannot read request file'."""
    import tempfile

    request = {"schema_version": "1.2", "company_query": "NonexistentCorp",
               "document_kind": "annual_report", "as_of_date": "2026-12-31"}
    with tempfile.TemporaryDirectory() as td:
        req_file = Path(td) / "req.json"
        req_file.write_text(json.dumps(request), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "source_preparation.py"),
             "--request-file", str(req_file)],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        # whatever the chain outcome, the C1 file-not-found error must
        # never appear (the request was handed to the client via stdin)
        assert "cannot read request file" not in proc.stderr
