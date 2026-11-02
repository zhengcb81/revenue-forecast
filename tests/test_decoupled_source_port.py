"""Public source port substitution; no producer implementation is imported."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import company_wiki_source_reader_v2 as reader  # noqa: E402
import source_preparation as prepare  # noqa: E402
from test_company_wiki_source_reader_v2 import BODY, _ref, _receipt  # noqa: E402


def test_raw_port_is_injected_and_keeps_receipt_verification(monkeypatch, tmp_path):
    calls = []
    def child(command, **kwargs):
        calls.append(command)
        assert command[:2] == [sys.executable, "opaque-reader.py"]
        assert "company_wiki.source_catalog.source_reader_cli" not in command
        return subprocess.CompletedProcess(command, 0, BODY,
            (json.dumps(_receipt()) + "\n").encode())
    monkeypatch.setattr(reader.subprocess, "run", child)
    result = reader.open_source_version_v2(source_ref=_ref(),
        catalog_config=tmp_path / "opaque.handle", as_of_date="2026-07-18",
        expected_fiscal_year=2025, reader_command=(sys.executable, "opaque-reader.py"))
    assert result.body == BODY
    assert len(calls) == 1


def test_registered_preparation_forwards_port_without_inspecting_producer_config(monkeypatch, tmp_path):
    # The public registered path accepts the same pathless filing fields.
    from test_company_wiki_source_v2 import _candidate
    candidate = _candidate(_ref(), _receipt()["manifest"])
    seen = {}
    def read(**kwargs):
        seen.update(kwargs)
        return BODY, {k:v for k,v in _receipt().items() if k != "manifest"}, _receipt()["manifest"]
    monkeypatch.setattr(reader, "open_source_version_v2", read)
    prepare.prepare_registered_source_result(candidate, as_of_date="2026-07-18",
        company_wiki_catalog_config=tmp_path / "not-a-local-catalog.handle",
        source_reader_command=("independent-reader",))
    assert seen["reader_command"] == ("independent-reader",)


def test_diagnostic_extension_is_non_authoritative(monkeypatch, tmp_path):
    receipt = _receipt()
    receipt["extensions"] = {"future_observer": {"state": "unknown"}}
    monkeypatch.setattr(reader.subprocess, "run", lambda command, **kw:
        subprocess.CompletedProcess(command, 0, BODY,
            (json.dumps(receipt, indent=2) + "\n").encode()))
    assert reader.open_source_version_v2(source_ref=_ref(),
        catalog_config=tmp_path / "config", as_of_date="2026-07-18",
        expected_fiscal_year=2025).body == BODY


def test_extension_cannot_hide_bad_core_bytes(monkeypatch, tmp_path):
    receipt = _receipt()
    receipt["extensions"] = {"verified": True}
    monkeypatch.setattr(reader.subprocess, "run", lambda command, **kw:
        subprocess.CompletedProcess(command, 0, BODY[:-1] + b"X",
            (json.dumps(receipt) + "\n").encode()))
    with pytest.raises(reader.SourceVersionTransportError, match="SHA-256"):
        reader.open_source_version_v2(source_ref=_ref(), catalog_config=tmp_path / "config",
            as_of_date="2026-07-18", expected_fiscal_year=2025)


def test_full_preparation_forwards_both_public_ports(monkeypatch, tmp_path):
    import company_wiki_narrative_reader as narrative
    import source_narrative_context
    candidate = {"source_ref": _ref()}
    seen = {}
    monkeypatch.setattr(prepare, "_run_filing_fetch", lambda *a: {"status": "ready"})
    monkeypatch.setattr(prepare, "select_filing", lambda *a: candidate)
    monkeypatch.setattr(prepare, "_prepare_source_ref_v2", lambda *a, **kw: {"source": "verified"})
    class Context:
        def to_dict(self):
            return {"source_ref": _ref()}
    def read(request, **kwargs):
        seen.update(kwargs)
        return Context()
    monkeypatch.setattr(narrative, "read_narrative_context", read)
    monkeypatch.setattr(source_narrative_context, "narrative_read_receipt", lambda *a: {"status": "ready"})
    result = prepare.prepare_source_result({}, company_wiki_catalog_config=tmp_path / "opaque.handle",
        source_reader_command=("raw-reader",), narrative_request={"operation": "read"},
        narrative_reader_command=("separate-narrative-reader",))
    assert result["narrative"] == {"status": "ready"}
    assert seen["reader_command"] == ("separate-narrative-reader",)
