"""Caller remaining time bounds local reads without restarting paid batches."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from company_wiki_narrative_contracts import NarrativeTransportError  # noqa: E402
from company_wiki_narrative_reader import read_narrative_context  # noqa: E402
import source_preparation as prep  # noqa: E402


def setup_chain(monkeypatch, tmp_path, ticks):
    config = tmp_path / "catalog.yaml"
    config.write_text("{}", encoding="utf-8")
    calls = []
    ref = {"source_id": "exact fixture source"}
    record = {"company_wiki_trace": {"source_ref": ref}}
    context = SimpleNamespace(to_dict=lambda: {"source_ref": ref})
    monkeypatch.setattr(prep, "time", SimpleNamespace(monotonic=iter(ticks).__next__), raising=False)
    monkeypatch.setattr(prep, "_filing_fetch_command", lambda *a, **kw: ())
    monkeypatch.setattr(prep, "select_filing", lambda value: {"source_ref": ref})
    def fetch(*a):
        calls.append(("fetch", a[-1]))
        return {"downloads": 0}
    def raw(*a, **kw):
        calls.append(("raw", kw["timeout_seconds"]))
        return record
    def narrative(*a, **kw):
        calls.append(("narrative", kw["timeout_seconds"]))
        return context
    monkeypatch.setattr(prep, "_run_filing_fetch", fetch)
    monkeypatch.setattr(prep, "_prepare_source_ref_v2", raw)
    monkeypatch.setattr("company_wiki_narrative_reader.read_narrative_context", narrative)
    monkeypatch.setattr("source_narrative_context.narrative_read_receipt", lambda context: {"status": "not_consumed"})
    return config, calls


def test_public_read_inherits_remaining_caller_deadline_over_thirty(monkeypatch, tmp_path):
    config, calls = setup_chain(monkeypatch, tmp_path, [100, 100, 140, 155])
    prep.prepare_source_result({}, company_wiki_catalog_config=config,
                               narrative_request={}, timeout_seconds=90)
    assert calls == [("fetch", 90), ("raw", 50), ("narrative", 35)]


def test_exhausted_caller_stops_before_next_actual_read(monkeypatch, tmp_path):
    config, calls = setup_chain(monkeypatch, tmp_path, [100, 100, 191])
    with pytest.raises(RuntimeError, match="source_preparation_deadline_exhausted"):
        prep.prepare_source_result({}, company_wiki_catalog_config=config,
                                   narrative_request={}, timeout_seconds=90)
    assert calls == [("fetch", 90)]


@pytest.mark.parametrize("timeout", [0, float("inf"), float("nan")])
def test_invalid_or_unbounded_caller_timeout_refused_before_upstream(monkeypatch, tmp_path, timeout):
    config, calls = setup_chain(monkeypatch, tmp_path, [100])
    with pytest.raises(RuntimeError, match="invalid_source_preparation_timeout"):
        prep.prepare_source_result({}, company_wiki_catalog_config=config, timeout_seconds=timeout)
    assert calls == []


def test_actual_transport_timeout_is_bounded_and_has_no_retry(tmp_path):
    request = json.loads((ROOT / "tests/fixtures/cwp_narrative_transport_v1/read_request.json").read_bytes())
    with pytest.raises(NarrativeTransportError, match="reader_timeout"):
        read_narrative_context(request, catalog_config=(tmp_path / "catalog.yaml").resolve(),
            timeout_seconds=0.15, reader_command=[sys.executable, "-B", "-c", "import time; time.sleep(3)"])
