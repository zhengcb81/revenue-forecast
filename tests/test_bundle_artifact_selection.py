"""WU-5.4: revenue consumer selects reusable artifacts from the bundle.

``select_reusable_artifacts(handle, roles)`` returns, for each requested
role, the valid artifact path/hash from the handle's ``source_bundle`` —
so the revenue consumer can skip parsing/LLM work when a verified
normalized/summary/sections artifact exists. Fail-closed: a missing or
invalid artifact is simply not returned (the consumer falls back to the
original), never trusted blindly.

RED phase: the function does not exist (ImportError).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from company_wiki_source import (  # noqa: E402
    CompanyWikiSourceError,
    build_revenue_source_record,
    select_reusable_artifacts,
)



def _bundle_handle(valid_handles: dict | None = None, invalid: dict | None = None):
    return {
        "request_id": "req-1",
        "capture_ready": True,
        "source_bundle": {
            "schema_version": "1.0",
            "source": {"document_id": "doc-1"},
            "valid_handles": valid_handles or {},
            "invalid": invalid or {},
            "bundle_hash": "b" * 64,
        },
    }


def test_returns_valid_normalized(tmp_path):
    handle = _bundle_handle(
        valid_handles={
            "normalized": {
                "artifact_role": "normalized",
                "path": "/x/normalized.md",
                "content_sha256": "a" * 64,
                "reusable": True,
            }
        }
    )
    artifacts = select_reusable_artifacts(handle, ("normalized",))
    assert "normalized" in artifacts
    assert artifacts["normalized"]["path"] == "/x/normalized.md"


def test_missing_role_not_returned(tmp_path):
    handle = _bundle_handle(
        valid_handles={
            "summary": {"artifact_role": "summary", "reusable": True,
                         "path": "/x/summary.md", "content_sha256": "a" * 64}
        }
    )
    artifacts = select_reusable_artifacts(handle, ("normalized", "summary"))
    assert "summary" in artifacts
    assert "normalized" not in artifacts


def test_invalid_artifact_not_returned(tmp_path):
    handle = _bundle_handle(
        invalid={
            "sections": {
                "artifact_role": "sections",
                "reusable": False,
                "reason": "artifact_status_not_completed",
            }
        }
    )
    artifacts = select_reusable_artifacts(handle, ("sections",))
    assert "sections" not in artifacts


def test_no_bundle_returns_empty(tmp_path):
    handle = {"request_id": "req-1", "capture_ready": True}
    assert select_reusable_artifacts(handle, ("normalized",)) == {}


def test_non_reusable_entry_in_valid_handles_rejected(tmp_path):
    """A valid_handles entry with reusable=False must be refused — this is
    the actual guard the mutation targets."""
    handle = _bundle_handle(
        valid_handles={
            "normalized": {
                "artifact_role": "normalized",
                "path": "/x/normalized.md",
                "content_sha256": "a" * 64,
                "reusable": False,
                "reason": "artifact_status_not_completed",
            }
        }
    )
    artifacts = select_reusable_artifacts(handle, ("normalized",))
    assert "normalized" not in artifacts


def test_malformed_bundle_fails_closed(tmp_path):
    handle = {"request_id": "req-1", "capture_ready": True,
              "source_bundle": "not-a-dict"}
    with pytest.raises(CompanyWikiSourceError):
        select_reusable_artifacts(handle, ("normalized",))


def test_malformed_valid_handles_fails_closed(tmp_path):
    """source_bundle.valid_handles non-dict → raises (fail-closed)."""
    handle = {
        "request_id": "req-1",
        "capture_ready": True,
        "source_bundle": {"schema_version": "1.0", "valid_handles": "nope"},
    }
    with pytest.raises(CompanyWikiSourceError):
        select_reusable_artifacts(handle, ("normalized",))


def test_non_dict_artifact_entry_skipped(tmp_path):
    """A valid_handles entry that is not a dict is skipped (not trusted)."""
    handle = {
        "request_id": "req-1",
        "capture_ready": True,
        "source_bundle": {
            "schema_version": "1.0",
            "valid_handles": {"normalized": "not-a-dict"},
        },
    }
    artifacts = select_reusable_artifacts(handle, ("normalized",))
    assert "normalized" not in artifacts


def test_build_record_iso_date_rejects_noncanonical(tmp_path):
    """_iso_date non-canonical form raises (line 80-81 coverage)."""
    from company_wiki_source import CompanyWikiSourceError as E

    handle = _bundle_handle()
    with pytest.raises(E):
        build_revenue_source_record(
            handle,
            as_of_date="2026/08/08",  # non-canonical
            source_type="regulatory_filing",
            publisher="SEC",
            page_or_section="p.1",
            prompt_injection_status="not_detected",
        )


def test_build_record_error_branches(tmp_path):
    """Cover build_revenue_source_record fail-closed branches."""
    from company_wiki_source import CompanyWikiSourceError as E
    import hashlib

    body = b"%PDF-1.4 fake"
    original = tmp_path / "annual.pdf"
    original.write_bytes(body)
    handle = {
        "request_id": "req-1",
        "document_id": "doc-1",
        "source_id": "src-1",
        "title": "ACME annual",
        "published_date": "2026-04-15",
        "https_url": "https://www.sec.gov/x.pdf",
        "canonical_path": str(original),
        "snapshot_sha256": hashlib.sha256(body).hexdigest(),
        "retrieved_at": "2026-08-08T12:00:00Z",
        "provider": "sec",
        "provider_document_id": "acc-1",
        "collector_name": "test",
        "collector_version": "1.0.0",
        "byte_size": len(body),
        "mime_type": "application/pdf",
        "capture_ready": True,
        "canonical_location_id": "loc-1",
    }
    base = dict(
        as_of_date="2026-08-08",
        source_type="regulatory_filing",
        publisher="SEC",
        page_or_section="p.1",
        prompt_injection_status="not_detected",
    )
    # wrong source_type
    with pytest.raises(E):
        build_revenue_source_record(handle, **{**base, "source_type": "nonsense"})
    # empty publisher
    with pytest.raises(E):
        build_revenue_source_record(handle, **{**base, "publisher": ""})
    # invalid prompt_injection_status
    with pytest.raises(E):
        build_revenue_source_record(handle, **{**base, "prompt_injection_status": "x"})
    # capture_ready False
    with pytest.raises(E):
        build_revenue_source_record({**handle, "capture_ready": False}, **base)
    # bad https_url
    with pytest.raises(E):
        build_revenue_source_record({**handle, "https_url": "http://x"}, **base)
    # missing request_id
    with pytest.raises(E):
        build_revenue_source_record({**handle, "request_id": ""}, **base)
    # bad snapshot hash
    with pytest.raises(E):
        build_revenue_source_record({**handle, "snapshot_sha256": "zz"}, **base)
    # canonical file missing
    with pytest.raises(E):
        build_revenue_source_record(
            {**handle, "canonical_path": str(tmp_path / "nope.pdf")}, **base
        )


def test_revenue_forecast_cli_version_and_input_error(tmp_path, monkeypatch):
    """Cover revenue_forecast CLI main() branches in-process so coverage
    counts them (subprocess coverage is unreliable on Windows)."""
    import sys

    from pathlib import Path

    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "scripts"))
    import revenue_forecast as rf

    # --version branch
    monkeypatch.setattr(sys, "argv", ["revenue_forecast", "--version"])
    assert rf.main() == 0
    # missing input → parser error (SystemExit 2)
    monkeypatch.setattr(sys, "argv", ["revenue_forecast"])
    try:
        rf.main()
        raise AssertionError("expected SystemExit for missing input")
    except SystemExit as exc:
        assert exc.code == 2
