"""Caller contract for a pathless, byte-verified company-wiki source."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from company_wiki_source import CompanyWikiSourceError  # noqa: E402
from company_wiki_source_v2 import (  # noqa: E402
    build_revenue_source_record_from_verified_read,
)
from revenue_core import validate_sources  # noqa: E402


BODY = b"%PDF-1.4\npathless revenue source\x00\xff\n"
SHA = hashlib.sha256(BODY).hexdigest()
POLICY = "a" * 64
READ_POLICY = "b" * 64
DOCUMENT = "urn:company-wiki:document:sha256:" + "b" * 64
SOURCE = "urn:company-wiki:source:sha256:" + SHA


def _inputs() -> tuple[dict, dict, dict]:
    ref = {
        "schema_version": "2.0",
        "document_id": DOCUMENT,
        "source_id": SOURCE,
        "content_sha256": SHA,
        "byte_size": len(BODY),
        "mime_type": "application/pdf",
    }
    receipt = {
        "schema_version": "2.1",
        "status": "ok",
        "document_id": DOCUMENT,
        "source_id": SOURCE,
        "content_sha256": SHA,
        "byte_size": len(BODY),
        "policy_sha256": POLICY,
        "source_read_policy_sha256": READ_POLICY,
        "read_at": "2026-09-27T12:00:00+00:00",
        "review": None,
    }
    manifest = {
        "document_id": DOCUMENT,
        "source_id": SOURCE,
        "content_sha256": SHA,
        "byte_size": len(BODY),
        "mime_type": "application/pdf",
        "title": "Acme 2025 Annual Report",
        "document_kind": "annual_report",
        "published_date": "2026-02-20",
        "source_url": "https://www.sec.gov/Archives/acme-2025",
        "retrieved_at": "2026-02-21T00:00:00Z",
        "collector_name": "sec_edgar",
        "collector_version": "1.0",
        "canonical_entity_id": "ent-acme",
        "display_name": "Acme",
        "market": "US",
        "security_id": "ACME",
        "fiscal_year": 2025,
        "fiscal_period": None,
        "period_end": "2025-12-31",
        "form_type": "10-K",
        "provider": "sec",
        "provider_document_id": "doc-1",
        "language": "en",
    }
    return ref, receipt, manifest


def _candidate(ref: dict, manifest: dict) -> dict:
    return {
        "capture_ready": True,
        "source_ref": ref,
        "document_id": ref["document_id"],
        "source_id": ref["source_id"],
        "snapshot_sha256": ref["content_sha256"],
        "byte_size": ref["byte_size"],
        "mime_type": ref["mime_type"],
        "title": manifest["title"],
        "document_kind": manifest["document_kind"],
        "fiscal_year": manifest["fiscal_year"],
        "published_date": manifest["published_date"],
        "https_url": manifest["source_url"],
        "retrieved_at": manifest["retrieved_at"],
        "provider": manifest["provider"],
        "provider_document_id": manifest["provider_document_id"],
        "prompt_injection_status": "not_reviewed",
        "company_identity": {
            "market": manifest["market"],
            "security_id": manifest["security_id"],
        },
    }


def _build(
    ref: dict,
    receipt: dict,
    manifest: dict,
    body: bytes = BODY,
    candidate: dict | None = None,
    prompt_injection_status: str = "not_reviewed",
) -> dict:
    return build_revenue_source_record_from_verified_read(
        source_ref=ref,
        read_receipt=receipt,
        source_bytes=body,
        source_manifest=manifest,
        source_candidate=candidate or _candidate(ref, manifest),
        as_of_date="2026-09-27",
        source_type="regulatory_filing",
        publisher="U.S. Securities and Exchange Commission",
        page_or_section="Revenue note, page 42",
        prompt_injection_status=prompt_injection_status,
    )


def test_verified_ref_builds_schema_compatible_record_without_physical_path() -> None:
    ref, receipt, manifest = _inputs()
    record = _build(ref, receipt, manifest)

    assert record["source_id"] == SOURCE
    assert record["capture"]["snapshot_sha256"] == SHA
    assert record["capture"]["prompt_injection_status"] == "not_reviewed"
    assert record["company_wiki_trace"]["read_receipt"]["review"] is None
    assert record["capture"]["host_receipt"]["timestamp"] == receipt["read_at"]
    assert record["company_wiki_trace"]["source_ref"] == ref
    assert record["company_wiki_trace"]["read_receipt"] == receipt
    assert "canonical_path" not in record["company_wiki_trace"]
    assert "path" not in json.dumps(record).lower()
    validated = validate_sources(
        {"sources": [record]}, date.fromisoformat("2026-09-27"),
        require_capture=True,
    )
    assert validated[SOURCE]["capture"]["snapshot_sha256"] == SHA


@pytest.mark.parametrize(
    "change",
    ("bytes", "receipt_hash", "missing_read_policy",
     "malformed_read_policy", "manifest_identity", "path_field",
     "candidate_fiscal_year", "candidate_title", "candidate_url", "receipt_schema"),
)
def test_verified_ref_fails_closed_on_drift_or_path_leak(change: str) -> None:
    ref, receipt, manifest = (deepcopy(value) for value in _inputs())
    candidate = _candidate(ref, manifest)
    body = BODY
    if change == "receipt_schema":
        receipt["schema_version"] = "2.0"
    elif change == "bytes":
        body = BODY[:-1] + b"X"  # Same size, different SHA-256.
    elif change == "receipt_hash":
        receipt["content_sha256"] = "0" * 64
    elif change == "missing_read_policy":
        del receipt["source_read_policy_sha256"]
    elif change == "malformed_read_policy":
        receipt["source_read_policy_sha256"] = "not-a-sha"
    elif change == "manifest_identity":
        manifest["source_id"] = "another-source"
    elif change == "path_field":
        ref["canonical_path"] = "private/raw.pdf"
    elif change == "candidate_fiscal_year":
        candidate["fiscal_year"] = 2024
    elif change == "candidate_title":
        candidate["title"] = "wrong document"
    elif change == "candidate_url":
        candidate["https_url"] = "https://example.com/wrong"
    with pytest.raises(CompanyWikiSourceError):
        _build(ref, receipt, manifest, body, candidate)


def test_changed_current_policy_is_audited_without_old_pin() -> None:
    ref, receipt, manifest = _inputs()
    receipt["policy_sha256"] = "0" * 64
    receipt["source_read_policy_sha256"] = "1" * 64
    record = _build(ref, receipt, manifest)
    assert record["company_wiki_trace"]["read_receipt"]["policy_sha256"] == "0" * 64


def test_missing_explicit_title_stays_missing_after_verified_read() -> None:
    ref, receipt, manifest = _inputs()
    manifest["title"] = None
    candidate = _candidate(ref, manifest)
    with pytest.raises(CompanyWikiSourceError, match="title"):
        _build(ref, receipt, manifest, candidate=candidate)
