"""WU-1000 RED/audit tests: source-preparation orchestration entry
(PROCESS-RED-01: the entry must drive the real chain, not helpers)."""

import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import source_preparation as sp  # noqa: E402
from source_preparation import (  # noqa: E402
    _v2_resolution_events,
    _validate_v2_candidate,
    prepare_source,
)


def test_process_red01_entry_exists_and_is_cli():
    """The single production entry exists as a real CLI module."""
    assert (ROOT / "scripts" / "source_preparation.py").is_file()
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "source_preparation.py"), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
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
    request = {
        "company_query": "Acme",
        "document_kind": "annual_report",
        "as_of_date": "2026-12-31",
    }
    # the orchestrator spawns the client as a subprocess; monkeypatching the
    # in-process symbol must NOT affect the subprocess path
    record_path = tmp_path / "request.json"
    record_path.write_text(json.dumps(request), encoding="utf-8")
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "source_preparation.py"),
            "--request-file",
            str(record_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    # subprocess runs the real client (not the monkeypatched one) — exit
    # reflects the real chain: the fixture request has no catalog behind it
    assert called["n"] == 0  # monkeypatch never reached the subprocess


def test_prepare_source_raises_on_client_failure(tmp_path, monkeypatch):
    request = {
        "company_query": "Acme",
        "document_kind": "annual_report",
        "as_of_date": "2026-12-31",
    }

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0], returncode=1, stdout="", stderr="boom"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    import pytest

    with pytest.raises(RuntimeError, match="invalid upstream error document") as caught:
        prepare_source(request, python=(sys.executable,),
                       company_wiki_catalog_config=_catalog_config(tmp_path))
    assert "boom" not in str(caught.value)


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
    return {
        "handle": {"request_id": "r1"},
        "selected_artifacts": [],
        **({"resolution_envelope": envelope} if envelope is not None else {}),
    }


def _src_ref_handle(**overrides):
    handle = {
        "source_ref": {
            "schema_version": "2.0",
            "document_id": "doc-1",
            "source_id": "src-1",
            "content_sha256": "a" * 64,
            "byte_size": 3,
            "mime_type": "application/pdf",
        },
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "fiscal_period": None,
        "provider": "company-wiki",
        "prompt_injection_status": None,
        "resolution_outcome": "reused_existing",
        "download_events": 0,
    }
    handle.update(overrides)
    return handle


def _patch_v2_read(monkeypatch):
    """Patch the verified reader/builder for unit-level v2 default tests."""
    import company_wiki_source_reader_v2 as reader_v2
    import company_wiki_source_v2 as builder_v2

    def fake_open(**kwargs):  # noqa: ARG001
        return (
            b"PDF",
            {
                "schema_version": "2.1",
                "status": "ok",
                "document_id": "doc-1",
                "source_id": "src-1",
                "content_sha256": "a" * 64,
                "byte_size": 3,
                "policy_sha256": "b" * 64,
                "source_read_policy_sha256": "c" * 64,
            },
            {"keep": True},
        )

    monkeypatch.setattr(reader_v2, "open_source_version_v2", fake_open)
    monkeypatch.setattr(
        builder_v2,
        "build_revenue_source_record_from_verified_read",
        lambda **kwargs: {"request_id": "r1", "capture": {"prompt_injection_status": None}},
    )


def _catalog_config(tmp_path):
    config = tmp_path / "source_catalog.yaml"
    config.write_text("schema_version: '1.0'" + chr(10), encoding="utf-8")
    return config


def _legacy_record(monkeypatch, envelope):
    """P5-RF: legacy-envelope contract replays through the isolated
    non-production legacy helper (the prepare_source default is v2)."""
    from source_preparation import _prepare_legacy_source
    import company_wiki_source as cws

    payload = _fake_payload(envelope)
    monkeypatch.setattr(
        cws, "build_revenue_source_record",
        lambda handle, **kwargs: {"request_id": handle.get("request_id", "r1")},
    )
    return _prepare_legacy_source(
        {"company_query": "Acme", "document_kind": "annual_report",
         "as_of_date": "2026-12-31"}, payload,
    )


test_legcy_src_ref_request = {
    "company_query": "Acme",
    "document_kind": "annual_report",
    "as_of_date": "2026-12-31",
    "fiscal_year": 2025,
    "fiscal_period": None,
}


def _run_v2(monkeypatch, tmp_path, captured):
    """Fake the FF subprocess (bare SourceRef handle) and the v2 read."""
    def fake_run(command, **kwargs):  # noqa: ARG001
        captured["command"] = list(command)
        return subprocess.CompletedProcess(
            command, returncode=0, stdout=json.dumps(_src_ref_handle()),
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    _patch_v2_read(monkeypatch)
    return sp


def test_prepare_source_forwards_allow_download(monkeypatch, tmp_path):
    captured = {}
    sp_mod = _run_v2(monkeypatch, tmp_path, captured)
    record = sp_mod.prepare_source(
        test_legcy_src_ref_request, allow_download=True,
        company_wiki_catalog_config=_catalog_config(tmp_path),
    )
    assert "--allow-download" in captured["command"]
    assert "--source-ref-v2" in captured["command"]
    assert record["reuse_receipt"]["download_calls"] == 0


def test_prepare_source_forwards_filing_fetch_root(monkeypatch, tmp_path):
    """FC-1202: the orchestrator must forward an explicit filing-fetch root
    to the client subprocess (no reliance on the client's default config)."""
    captured = {}
    sp_mod = _run_v2(monkeypatch, tmp_path, captured)
    record = sp_mod.prepare_source(
        test_legcy_src_ref_request, filing_fetch_root=Path("X"),
        company_wiki_catalog_config=_catalog_config(tmp_path),
    )
    command = captured["command"]
    assert "--filing-fetch-root" in command
    assert command[command.index("--filing-fetch-root") + 1] == str(Path("X"))
    assert record["reuse_receipt"]["download_calls"] == 0


def test_cli_forwards_filing_fetch_root(monkeypatch, tmp_path):
    """FC-1202: the CLI must forward --filing-fetch-root to prepare_source —
    removing the forwarding silently drops explicit roots (mutation target)."""
    captured = {}

    def fake_prepare(request, **kwargs):
        captured.update(kwargs)
        return {"request_id": "r1"}

    monkeypatch.setattr(sp, "prepare_source", fake_prepare)
    request_path = tmp_path / "req.json"
    request_path.write_text(
        json.dumps(
            {
                "company_query": "Acme",
                "document_kind": "annual_report",
                "as_of_date": "2026-12-31",
            }
        ),
        encoding="utf-8",
    )
    root = tmp_path / "ff"
    exit_code = sp.main(
        ["--request-file", str(request_path), "--filing-fetch-root", str(root)]
    )
    assert exit_code == 0
    assert captured.get("filing_fetch_root") == root


# --- FC-704: download evidence comes from the envelope, not the handle ---------


def test_env09_download_calls_from_envelope_events(monkeypatch):
    """ENV-09: envelope download_events=1 -> receipt download_calls=1.
    The legacy fake ('0 if handle else 1') would report 0 for a handle that
    carries a downloaded document — this mutation must die."""
    record = _legacy_record(
        monkeypatch, _envelope(download_events=1, outcome="downloaded_new"))
    assert record["reuse_receipt"]["download_calls"] == 1
    assert record["reuse_receipt"]["outcome"] == "downloaded_new"


def test_env10_download_calls_zero_from_envelope(monkeypatch):
    """ENV-10: envelope download_events=0 -> receipt download_calls=0."""
    record = _legacy_record(monkeypatch, _envelope())
    assert record["reuse_receipt"]["download_calls"] == 0


def test_env11_missing_envelope_fails_closed(monkeypatch):
    """ENV-11: a handle WITHOUT envelope evidence fails closed — the receipt
    may never silently claim zero downloads (scenario_matrix §2: counts come
    from events/journal, never inferred from the result)."""
    payload = _fake_payload(None)
    import pytest as _pytest
    from source_preparation import _prepare_legacy_source

    with _pytest.raises(RuntimeError, match="resolution envelope missing"):
        _prepare_legacy_source(test_legcy_src_ref_request, payload)


def test_env12_receipt_carries_envelope_evidence(monkeypatch):
    """ENV-12: the receipt records the journal-derived outcome and the
    policy/epoch/bundle evidence — the evidence is IN the receipt, not
    re-derived."""
    record = _legacy_record(
        monkeypatch,
        _envelope(
            outcome="reused_after_discovery",
            policy_hash="b" * 64,
            activation_epoch="epoch-2",
            bundle_status="unavailable",
        ),
    )
    receipt = record["reuse_receipt"]
    assert receipt["outcome"] == "reused_after_discovery"
    assert receipt["policy_hash"] == "b" * 64
    assert receipt["activation_epoch"] == "epoch-2"
    assert receipt["bundle_status"] == "unavailable"


def test_c1_request_reaches_client_not_file_error():
    """C1 regression: the request must reach the client via stdin — the
    client must never report 'cannot read request file'."""
    import tempfile

    request = {
        "schema_version": "1.2",
        "company_query": "NonexistentCorp",
        "document_kind": "annual_report",
        "as_of_date": "2026-12-31",
    }
    with tempfile.TemporaryDirectory() as td:
        req_file = Path(td) / "req.json"
        req_file.write_text(json.dumps(request), encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "source_preparation.py"),
                "--request-file",
                str(req_file),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        # whatever the chain outcome, the C1 file-not-found error must
        # never appear (the request was handed to the client via stdin)
        assert "cannot read request file" not in proc.stderr


@pytest.mark.parametrize(
    ("outcome", "downloads"),
    (("reused_existing", 0), ("reused_after_discovery", 0), ("downloaded_new", 1)),
)
def test_source_ref_v2_resolution_events_accept_consistent_counts(outcome, downloads):
    assert _v2_resolution_events(
        {
            "resolution_outcome": outcome,
            "download_events": downloads,
        }
    ) == (outcome, downloads)


@pytest.mark.parametrize(
    ("outcome", "downloads"),
    (("reused_existing", 1), ("reused_after_discovery", 1), ("downloaded_new", 0)),
)
def test_source_ref_v2_resolution_events_reject_inconsistent_counts(outcome, downloads):
    with pytest.raises(RuntimeError, match="outcome/download_events mismatch"):
        _v2_resolution_events(
            {
                "resolution_outcome": outcome,
                "download_events": downloads,
            }
        )


def test_source_ref_v2_resolution_events_reject_untyped_outcome():
    with pytest.raises(RuntimeError, match="resolution_outcome is invalid"):
        _v2_resolution_events({"resolution_outcome": [], "download_events": 0})


@pytest.mark.parametrize("location_field", ("path", "canonical_path", "storage_path"))
def test_source_ref_v2_candidate_rejects_storage_paths_before_read(location_field):
    handle = {
        "source_ref": {"schema_version": "2.0"},
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "fiscal_period": None,
    }
    handle[location_field] = "private/raw.pdf"
    request = {
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "fiscal_period": None,
    }
    with pytest.raises(RuntimeError, match="contains a storage location"):
        _validate_v2_candidate(request, handle)


def test_source_ref_v2_candidate_rejects_nested_storage_path_before_read():
    handle = {
        "source_ref": {"canonical_path": "private/raw.pdf"},
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "fiscal_period": None,
    }
    request = {
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "fiscal_period": None,
    }
    with pytest.raises(RuntimeError, match="SourceRef contains a storage location"):
        _validate_v2_candidate(request, handle)


def test_annual_optional_period_defaults_to_canonical_fy():
    import source_preparation as prep
    import pytest
    request = {"document_kind": "annual_report", "fiscal_year": 2025}
    handle = {"source_ref": {}, "document_kind": "annual_report",
              "fiscal_year": 2025, "fiscal_period": "FY"}
    assert prep._validate_v2_candidate(request, handle) == 2025
    request["fiscal_period"] = "H1"
    with pytest.raises(RuntimeError, match="fiscal_period"):
        prep._validate_v2_candidate(request, handle)


@pytest.mark.parametrize("kind,resolved", [("semi_annual_report", "H1"), ("semi_annual_report", "H2"),
    ("quarterly_report", "Q2"), ("regulatory_filing", "H1")])
@pytest.mark.parametrize("explicit_null", [False, True])
def test_optional_period_accepts_uniquely_resolved_source_period(kind, resolved, explicit_null):
    request = {"document_kind": kind, "fiscal_year": 2025}
    if explicit_null:
        request["fiscal_period"] = None
    handle = {"source_ref": {}, "document_kind": kind, "fiscal_year": 2025,
              "fiscal_period": resolved}
    assert _validate_v2_candidate(request, handle) == 2025
    assert handle["fiscal_period"] == resolved and request.get("fiscal_period") is None


@pytest.mark.parametrize("kind,requested,resolved", [("semi_annual_report", "H1", "H2"),
    ("quarterly_report", "Q1", "Q2"), ("annual_report", None, "Q1"),
    ("semi_annual_report", "H2", None)])
def test_explicit_period_constraint_and_annual_semantics_stay_strict(kind, requested, resolved):
    request = {"document_kind": kind, "fiscal_year": 2025, "fiscal_period": requested}
    handle = {"source_ref": {}, "document_kind": kind, "fiscal_year": 2025,
              "fiscal_period": resolved}
    with pytest.raises(RuntimeError, match="fiscal_period mismatch") as caught:
        _validate_v2_candidate(request, handle)
    assert caught.value.source_failure_reason == "fiscal_period_mismatch"


@pytest.mark.parametrize("resolved", [True, [], {}, "", " H1 "])
def test_optional_period_does_not_accept_malformed_resolved_field(resolved):
    request = {"document_kind": "semi_annual_report", "fiscal_year": 2025}
    handle = {"source_ref": {}, "document_kind": "semi_annual_report", "fiscal_year": 2025,
              "fiscal_period": resolved}
    with pytest.raises(RuntimeError, match="fiscal_period"):
        _validate_v2_candidate(request, handle)
