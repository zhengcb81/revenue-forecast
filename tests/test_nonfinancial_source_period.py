"""Nonfinancial source periods stay unknown; real financial reports stay strict."""
from __future__ import annotations
import json
import subprocess
import pytest
from test_company_wiki_source_reader_v2 import BODY, _ref, _receipt
from company_wiki_source_reader_v2 import SourceVersionTransportError, open_source_version_v2
from company_wiki_source_v2 import build_revenue_source_record_from_verified_read
from company_wiki_source import CompanyWikiSourceError


def opened(monkeypatch, tmp_path, kind, year):
    receipt = _receipt()
    receipt["manifest"].update(document_kind=kind, fiscal_year=year, fiscal_period=None, period_end=None)
    monkeypatch.setattr("subprocess.run", lambda command, **kw: subprocess.CompletedProcess(
        command, 0, BODY, (json.dumps(receipt)+"\n").encode()))
    return open_source_version_v2(source_ref=_ref(), catalog_config=tmp_path/"catalog.yaml",
        as_of_date="2026-07-18", expected_fiscal_year=year)


@pytest.mark.parametrize("kind", ["investor_relations", "investor_call_transcript", "regulatory_filing", "news", "broker_research"])
def test_null_nonfinancial_year_verified_raw_and_source_capture(monkeypatch, tmp_path, kind):
    body, receipt, manifest = opened(monkeypatch, tmp_path, kind, None)
    candidate={"status":"source_candidate", "source_ref":_ref(), "byte_verification":"pending_verified_open",
        "document_kind":kind, "fiscal_year":None, "fiscal_period":None,
        "resolution_outcome":"reused_existing", "download_events":0}
    record=build_revenue_source_record_from_verified_read(source_ref=_ref(), read_receipt=receipt,
        source_bytes=body, source_manifest=manifest, source_candidate=candidate,
        as_of_date="2026-07-18", source_type="company_release", publisher="issuer", page_or_section="1")
    assert record["company_wiki_trace"]["source_manifest"]["fiscal_year"] is None
    assert record["capture"]["snapshot_sha256"] == _ref()["content_sha256"]


@pytest.mark.parametrize("kind", ["annual_report", "semi_annual_report", "quarterly_report"])
def test_null_financial_year_rejected_after_exact_read(monkeypatch, tmp_path, kind):
    with pytest.raises(SourceVersionTransportError, match="fiscal_year"):
        opened(monkeypatch, tmp_path, kind, None)


def test_nonfinancial_numeric_year_still_matches_exact_request(monkeypatch, tmp_path):
    receipt=_receipt()
    receipt["manifest"].update(document_kind="investor_relations", fiscal_year=None)
    monkeypatch.setattr("subprocess.run", lambda command, **kw: subprocess.CompletedProcess(
        command, 0, BODY, (json.dumps(receipt)+"\n").encode()))
    with pytest.raises(SourceVersionTransportError, match="fiscal_year"):
        open_source_version_v2(source_ref=_ref(),catalog_config=tmp_path/"catalog.yaml",
            as_of_date="2026-07-18",expected_fiscal_year=2025)


def test_builder_alone_does_not_relax_financial_year(monkeypatch, tmp_path):
    receipt=_receipt()
    manifest=receipt.pop("manifest")
    manifest.update(fiscal_year=None)
    with pytest.raises(CompanyWikiSourceError,match="fiscal_year"):
        build_revenue_source_record_from_verified_read(source_ref=_ref(),read_receipt=receipt,
            source_bytes=BODY,source_manifest=manifest,source_candidate={},as_of_date="2026-07-18",
            source_type="regulatory_filing",publisher="issuer",page_or_section="1")


def test_registered_official_preparation_uses_same_reader_no_ff(monkeypatch, tmp_path):
    import source_preparation
    receipt=_receipt()
    receipt["manifest"].update(document_kind="investor_relations",fiscal_year=None,fiscal_period=None,period_end=None)
    config=tmp_path/"catalog.yaml"
    config.write_text("synthetic: fixture",encoding="utf-8")
    calls=[]
    def run(command,**kw):
        calls.append(command)
        assert "company_wiki.source_catalog.source_reader_cli" in command
        return subprocess.CompletedProcess(command,0,BODY,(json.dumps(receipt)+"\n").encode())
    monkeypatch.setattr("subprocess.run",run)
    candidate={"status":"source_candidate","source_ref":_ref(),"byte_verification":"pending_verified_open",
        "document_kind":"investor_relations","fiscal_year":None,"fiscal_period":None,
        "resolution_outcome":"reused_existing","download_events":0}
    result=source_preparation.prepare_registered_source_result(candidate,as_of_date="2026-07-18",company_wiki_catalog_config=config)
    assert len(calls)==1
    assert result["filing_fetch"] is None
    assert result["source"]["source_type"]=="company_release"
    assert result["source"]["company_wiki_trace"]["source_manifest"]["fiscal_year"] is None
