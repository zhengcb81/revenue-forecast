"""Real persistent CWP producer -> public subprocess -> RF's opt-in CLI.

CI supplies the manifest-pinned producer checkout; missing producer/PDF modules
are failures. Only the two owner raw samples are opt-in. All catalog/runtime
writes stay below pytest scratch; original raw files are read-only.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

RF_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def producer(monkeypatch):
    root = Path(os.environ.get("CWP_NARRATIVE_CODE_ROOT", str(RF_ROOT.parent / "company-wiki"))).resolve()
    support = root / "tests" / "support" / "narrative_transport_fixture.py"
    assert support.is_file(), "inject CWP_NARRATIVE_CODE_ROOT for the published producer; do not skip this boundary"
    assert (root / "src/company_wiki/source_catalog/narrative_transport_cli.py").is_file()
    assert importlib.util.find_spec("fitz") is not None, "install CWP's PyMuPDF parser for PDF E2E"
    monkeypatch.syspath_prepend(str(root / "src"))
    monkeypatch.syspath_prepend(str(root / "tests"))
    monkeypatch.setenv("PYTHONPATH", str(root / "src"))
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "1")
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    monkeypatch.setenv("COMPANY_WIKI_NETWORK", "blocked")
    spec = importlib.util.spec_from_file_location("_rf_cwp_transport_fixture", support)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def _cli(fixture, request, operation="read"):
    body = json.dumps(request).encode("utf-8") if isinstance(request, dict) else request
    return subprocess.run(
        [sys.executable, "-B", str(RF_ROOT / "scripts/narrative_source_preparation.py"),
         "--company-wiki-catalog-config", str(fixture.config_path), "--operation", operation],
        input=body, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=fixture.root, env=dict(os.environ), timeout=45, check=False,
    )


def _reference(fixture):
    result = _cli(fixture, {"schema_version": "narrative-reference-request/1",
                           "source_ref": fixture.source_ref.to_dict()}, "reference")
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert result.stderr == b""
    reference = json.loads(result.stdout)
    assert reference["source_ref"] == fixture.source_ref.to_dict()
    assert reference["artifact_sha256"] == hashlib.sha256(fixture.payload).hexdigest()
    assert reference["byte_size"] == len(fixture.payload)
    return reference


def _request(fixture, reference):
    return {"schema_version": "narrative-read-request/1", "narrative_ref": reference,
            "as_of_date": "2026-09-01", "expected_source": dict(fixture.expected_source)}


def _context(fixture, request):
    result = _cli(fixture, request)
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert result.stderr == b""
    context = json.loads(result.stdout)
    assert context["read_receipt"]["narrative_ref"] == context["narrative_ref"] == request["narrative_ref"]
    assert context["read_receipt"]["as_of_date"] == context["as_of_date"] == request["as_of_date"]
    assert context["read_receipt"]["replay_status"] == "verified"
    assert context["source_ref"] == fixture.source_ref.to_dict()
    spans = context["evidence_spans"]
    assert context["read_receipt"]["locator_count"] == len(spans)
    ids = {span["span_id"] for span in spans}
    for span in spans:
        assert span["source_id"] == fixture.source_ref.source_id
        assert span["locator"].startswith("loc:v1/")
    if context["summary"]["draft"] is not None:
        for claim in context["summary"]["draft"]["claims"]:
            assert claim["evidence_ids"] and set(claim["evidence_ids"]) <= ids
    assert context["summary"]["translate"] is False
    assert str(fixture.root) not in json.dumps(context)
    assert "forecast" not in context and "investment_conclusion" not in context
    return context


@pytest.mark.parametrize("kind", ["txt", "json", "pdf", "skip"])
def test_real_persistent_producer_survives_rf_public_entry_and_restores_scratch(producer, tmp_path, kind):
    baseline = set(tmp_path.iterdir())
    with producer.published_fixture(tmp_path, kind=kind) as fixture:
        before_sha = hashlib.sha256(fixture.raw_path.read_bytes()).hexdigest()
        database = fixture.catalog.store.database_path
        before_db = hashlib.sha256(database.read_bytes()).hexdigest()
        context = _context(fixture, _request(fixture, _reference(fixture)))
        assert hashlib.sha256(fixture.raw_path.read_bytes()).hexdigest() == before_sha
        assert hashlib.sha256(database.read_bytes()).hexdigest() == before_db
        if kind == "skip":
            assert context["quality_status"] == context["selection"]["status"] == "skipped_no_narrative"
            assert context["evidence_spans"] == [] and context["summary"]["draft"] is None
        else:
            assert context["evidence_spans"]
            assert fixture.expected_source["canonical_entity_id"] == "ent-acme"
            assert fixture.expected_source["fiscal_year"] == 2026
            assert fixture.expected_source["fiscal_period"] in {"Q2", "FY"}
    assert set(tmp_path.iterdir()) == baseline


@pytest.mark.parametrize("mutation", ["entity", "year", "period", "asof", "artifact", "raw_tamper"])
def test_real_producer_refusals_are_empty_bounded_and_fail_closed(producer, tmp_path, mutation):
    with producer.published_fixture(tmp_path) as fixture:
        request = _request(fixture, _reference(fixture))
        if mutation == "entity":
            request["expected_source"]["canonical_entity_id"] = "ent-wrong"
        elif mutation == "year":
            request["expected_source"]["fiscal_year"] = 2025
        elif mutation == "period":
            request["expected_source"]["fiscal_period"] = "Q3"
        elif mutation == "asof":
            request["as_of_date"] = "2026-07-31"
        elif mutation == "artifact":
            request["narrative_ref"]["artifact_sha256"] = "a" * 64
        original = fixture.raw_path.read_bytes()
        try:
            if mutation == "raw_tamper":
                fixture.raw_path.write_bytes(original + b"tampered")
            result = _cli(fixture, request)
            assert result.returncode == 2 and result.stdout == b""
            assert result.stderr.count(b"\n") == 1 and len(result.stderr) < 512
            refusal = json.loads(result.stderr)
            assert refusal["schema_version"] == "revenue-narrative-refusal/1"
            assert refusal["reason"] and "Traceback" not in result.stderr.decode()
            assert str(fixture.root) not in result.stderr.decode()
        finally:
            fixture.raw_path.write_bytes(original)


def test_unknown_publication_has_metadata_but_no_historical_evidence(producer, tmp_path):
    spec = {"sidecar_overrides": {"fiscal_period": "Q2", "filing_date": None}}
    with producer.published_fixture(tmp_path, source_spec=spec) as fixture:
        result = _cli(fixture, _request(fixture, _reference(fixture)))
        assert result.returncode == 2 and result.stdout == b""
        assert json.loads(result.stderr)["reason"] == "source_publication_unknown"


@pytest.mark.parametrize("payload", [b"[" * 1100 + b"]" * 1100, b"{}" * 9000])
def test_rf_cli_rejects_nested_or_oversized_input_without_traceback(tmp_path, payload):
    class Fixture:
        config_path = tmp_path / "absent.yaml"
        root = tmp_path
    result = _cli(Fixture, payload)
    assert result.returncode == 2 and result.stdout == b""
    assert result.stderr.count(b"\n") == 1
    assert "Traceback" not in result.stderr.decode()


@pytest.mark.skipif(os.environ.get("RF_RUN_NARRATIVE_REAL_SAMPLES") != "1",
                    reason="owner only: RF_RUN_NARRATIVE_REAL_SAMPLES=1")
@pytest.mark.parametrize("sample_id", ["P01", "T01"])
def test_real_annual_filing_and_original_transcript_are_read_only(producer, tmp_path, sample_id):
    from integration.test_narrative_runtime_e2e import (
        _E6_REAL_SAMPLES, _e6_production_fingerprint, _e6_source_paths,
    )
    sample = next(value for value in _E6_REAL_SAMPLES if value["sample_id"] == sample_id)
    _, paths = _e6_source_paths()
    original = paths[sample_id]
    assert original.is_file(), f"required real sample unavailable: {sample_id}"
    raw = original.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == sample["sha256"]
    stat = original.stat()
    production_before = _e6_production_fingerprint()
    baseline = set(tmp_path.iterdir())
    try:
        spec = dict(sample, data=raw)
        # The copied bytes remain exact; a short scratch filename reduces Windows path length.
        spec["name"] = f"real-{sample_id}.txt" if sample_id == "T01" else f"real-{sample_id}.pdf"
        kind = "txt" if sample_id == "T01" else "pdf"
        with producer.published_fixture(tmp_path, kind=kind, source_spec=spec) as fixture:
            context = _context(fixture, _request(fixture, _reference(fixture)))
            assert context["source_ref"]["content_sha256"] == digest
            assert len(context["evidence_spans"]) > 0
            print(json.dumps({"sample": sample_id, "raw_bytes": len(raw),
                              "artifact_bytes": context["narrative_ref"]["byte_size"],
                              "locators": len(context["evidence_spans"]),
                              "quality": context["quality_status"]}, sort_keys=True))
    finally:
        assert hashlib.sha256(original.read_bytes()).hexdigest() == digest
        assert original.stat().st_mtime_ns == stat.st_mtime_ns
        assert _e6_production_fingerprint() == production_before
        assert set(tmp_path.iterdir()) == baseline
