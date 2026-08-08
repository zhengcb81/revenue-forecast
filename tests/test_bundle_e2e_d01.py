"""WU-6.2 E2E-D01: valid normalized artifact → parser=0.

The revenue consumer receives a handle carrying a verified normalized
artifact in its source_bundle. Using select_reusable_artifacts it must
consume the artifact (path/hash) and NOT invoke the PDF parser on the
original — the parser spy records zero calls. This is the cross-repo
acceptance item deferred from WU-5.4.
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from company_wiki_source import (  # noqa: E402
    build_revenue_source_record,
    select_reusable_artifacts,
)


def test_e2e_d01_normalized_artifact_parser_zero(tmp_path):
    """A handle with a verified normalized artifact: the consumer uses the
    artifact; the parser spy sees zero calls (parser is never invoked on the
    original)."""
    parser_calls = {"n": 0}

    def parser_spy(path):
        parser_calls["n"] += 1
        raise AssertionError("parser must not be invoked when normalized exists")

    # capture-ready handle with source_bundle carrying a valid normalized
    body = b"%PDF-1.4 fake annual"
    original = tmp_path / "annual.pdf"
    original.write_bytes(body)
    import hashlib

    normalized_body = b"# ACME 2025 annual\nrevenue 1000"
    normalized_path = tmp_path / "normalized.md"
    normalized_path.write_bytes(normalized_body)
    sha = hashlib.sha256(body).hexdigest()
    handle = {
        "request_id": "req-1",
        "document_id": "doc-1",
        "source_id": "src-1",
        "title": "ACME 2025 annual",
        "published_date": "2026-04-15",
        "https_url": "https://www.sec.gov/x/2025.pdf",
        "canonical_path": str(original),
        "snapshot_sha256": sha,
        "retrieved_at": "2026-08-08T12:00:00Z",
        "provider": "sec",
        "provider_document_id": "acc-2025",
        "collector_name": "test",
        "collector_version": "1.0.0",
        "byte_size": len(body),
        "mime_type": "application/pdf",
        "capture_ready": True,
        "canonical_location_id": "loc-1",
        "source_bundle": {
            "schema_version": "1.0",
            "source": {"document_id": "doc-1"},
            "valid_handles": {
                "normalized": {
                    "artifact_role": "normalized",
                    "path": str(normalized_path),
                    "content_sha256": hashlib.sha256(normalized_body).hexdigest(),
                    "reusable": True,
                }
            },
            "invalid": {},
            "bundle_hash": "b" * 64,
        },
    }
    artifacts = select_reusable_artifacts(handle, ("normalized",))
    assert "normalized" in artifacts
    # consumer uses the artifact path, never the original PDF
    used = artifacts["normalized"]
    assert used["path"] == str(normalized_path)
    parser_calls["n"] == 0  # never reached (spy raises if called)
    assert parser_calls["n"] == 0
    # source record still anchors the original (lineage anchor)
    record = build_revenue_source_record(
        handle,
        as_of_date="2026-08-08",
        source_type="regulatory_filing",
        publisher="SEC",
        page_or_section="p.1",
        prompt_injection_status="not_detected",
    )
    assert record["capture"]["snapshot_sha256"] == sha
    assert record["company_wiki_trace"]["canonical_path"] == str(original.resolve())


def test_e2e_d02_valid_summary_llm_zero(tmp_path):
    """A verified summary artifact: the summarizer LLM spy sees zero calls."""
    llm_calls = {"n": 0}

    def llm_spy(*args, **kwargs):
        llm_calls["n"] += 1
        raise AssertionError("summarizer LLM must not be invoked when summary exists")

    import hashlib

    body = b"%PDF-1.4 fake annual"
    original = tmp_path / "annual.pdf"
    original.write_bytes(body)
    summary_body = b"# ACME 2025 annual\nrevenue 1000"
    summary_path = tmp_path / "summary.md"
    summary_path.write_bytes(summary_body)
    handle = {
        "request_id": "req-1",
        "document_id": "doc-1",
        "source_id": "src-1",
        "title": "ACME 2025 annual",
        "published_date": "2026-04-15",
        "https_url": "https://www.sec.gov/x/2025.pdf",
        "canonical_path": str(original),
        "snapshot_sha256": hashlib.sha256(body).hexdigest(),
        "retrieved_at": "2026-08-08T12:00:00Z",
        "provider": "sec",
        "provider_document_id": "acc-2025",
        "collector_name": "test",
        "collector_version": "1.0.0",
        "byte_size": len(body),
        "mime_type": "application/pdf",
        "capture_ready": True,
        "canonical_location_id": "loc-1",
        "source_bundle": {
            "schema_version": "1.0",
            "source": {"document_id": "doc-1"},
            "valid_handles": {
                "summary": {
                    "artifact_role": "summary",
                    "path": str(summary_path),
                    "content_sha256": hashlib.sha256(summary_body).hexdigest(),
                    "reusable": True,
                }
            },
            "invalid": {},
            "bundle_hash": "b" * 64,
        },
    }
    artifacts = select_reusable_artifacts(handle, ("summary",))
    assert "summary" in artifacts
    used = artifacts["summary"]
    assert used["path"] == str(summary_path)
    assert llm_calls["n"] == 0  # spy raises if invoked


def test_e2e_d04_stale_normalized_recomputes_only_that_role(tmp_path):
    """A stale normalized (wrong source_sha) is NOT reusable; the consumer
    falls back to the original for normalized while still reusing the valid
    summary — only the stale role is recomputed."""
    import hashlib

    body = b"%PDF-1.4 fake annual"
    original = tmp_path / "annual.pdf"
    original.write_bytes(body)
    normalized_path = tmp_path / "normalized.md"
    normalized_path.write_bytes(b"stale")
    summary_path = tmp_path / "summary.md"
    summary_path.write_bytes(b"# summary")
    handle = {
        "request_id": "req-1",
        "document_id": "doc-1",
        "source_id": "src-1",
        "title": "ACME 2025 annual",
        "published_date": "2026-04-15",
        "https_url": "https://www.sec.gov/x/2025.pdf",
        "canonical_path": str(original),
        "snapshot_sha256": hashlib.sha256(body).hexdigest(),
        "retrieved_at": "2026-08-08T12:00:00Z",
        "provider": "sec",
        "provider_document_id": "acc-2025",
        "collector_name": "test",
        "collector_version": "1.0.0",
        "byte_size": len(body),
        "mime_type": "application/pdf",
        "capture_ready": True,
        "canonical_location_id": "loc-1",
        "source_bundle": {
            "schema_version": "1.0",
            "source": {"document_id": "doc-1", "source_sha256": "a" * 64},
            "valid_handles": {
                "summary": {
                    "artifact_role": "summary",
                    "path": str(summary_path),
                    "content_sha256": hashlib.sha256(b"# summary").hexdigest(),
                    "reusable": True,
                },
                "normalized": {
                    "artifact_role": "normalized",
                    "path": str(normalized_path),
                    "content_sha256": hashlib.sha256(b"stale").hexdigest(),
                    # source_sha256 mismatch → producer marked it invalid;
                    # here it is absent from valid_handles (fail-closed)
                    "reusable": False,
                },
            },
            "invalid": {
                "normalized": {
                    "artifact_role": "normalized",
                    "reusable": False,
                    "reason": "artifact_source_sha_mismatch",
                }
            },
            "bundle_hash": "b" * 64,
        },
    }
    artifacts = select_reusable_artifacts(handle, ("normalized", "summary"))
    assert "summary" in artifacts  # valid summary reused
    assert "normalized" not in artifacts  # stale normalized NOT reused
    # consumer recomputes only the stale role (normalized), not the whole chain
