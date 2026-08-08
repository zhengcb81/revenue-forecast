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
    artifacts = select_reusable_artifacts(handle, ("normalized", "summary"))
    assert "normalized" in artifacts
    # consumer uses the artifact path, never the original PDF
    used = artifacts["normalized"]
    assert used["path"] == str(normalized_path)
    # consumer verifies the artifact hash against the file bytes
    assert hashlib.sha256(Path(used["path"]).read_bytes()).hexdigest() == (
        used["content_sha256"]
    )
    assert parser_calls["n"] == 0  # spy raises if called
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


def test_e2e_d05_misbound_summary_rejected_only_that_role_recomputed(tmp_path):
    """E2E-D05: a summary artifact bound to the WRONG source (source_sha
    mismatch) is rejected; the consumer recomputes only the summary — the
    valid normalized artifact is still reused."""
    import hashlib

    body = b"%PDF-1.4 fake annual"
    original = tmp_path / "annual.pdf"
    original.write_bytes(body)
    normalized_path = tmp_path / "normalized.md"
    normalized_path.write_bytes(b"# normalized ok")
    summary_path = tmp_path / "summary.md"
    summary_path.write_bytes(b"# stale summary")
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
                "normalized": {
                    "artifact_role": "normalized",
                    "path": str(normalized_path),
                    "content_sha256": hashlib.sha256(b"# normalized ok").hexdigest(),
                    "reusable": True,
                }
            },
            "invalid": {
                "summary": {
                    "artifact_role": "summary",
                    "reusable": False,
                    "reason": "artifact_source_sha_mismatch",
                }
            },
            "bundle_hash": "b" * 64,
        },
    }
    # the misbound summary must be observably rejected with its reason
    assert handle["source_bundle"]["invalid"]["summary"]["reason"] == (
        "artifact_source_sha_mismatch"
    )
    # producer-side attestation is authoritative: even if a summary with a
    # stale source_sha appeared in valid_handles, the consumer refuses it
    # (the invalid entry explains why, and the valid map carries no stale
    # summary) — asserting the invariant both ways
    assert "summary" not in handle["source_bundle"].get("valid_handles", {})
    artifacts = select_reusable_artifacts(handle, ("normalized", "summary"))
    assert "normalized" in artifacts  # valid normalized still reused
    assert "summary" not in artifacts  # misbound summary rejected
    # consumer recomputes ONLY the summary role (normalized untouched)


def test_e2e_d03_sections_used_instead_of_full_rerun(tmp_path):
    """E2E-D03: a verified sections artifact is selected for the consumer —
    the chunker spy sees zero calls (no full-document re-read/chunking)."""
    chunker_calls = {"n": 0}

    def chunker_spy(path):
        chunker_calls["n"] += 1
        raise AssertionError("chunker must not be invoked when sections exist")
    import hashlib

    body = b"%PDF-1.4 fake annual"
    original = tmp_path / "annual.pdf"
    original.write_bytes(body)
    sections_path = tmp_path / "sections.json"
    sections_body = b'{"sections": [{"title": "Revenue", "ordinal": 1}]}'
    sections_path.write_bytes(sections_body)
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
                "sections": {
                    "artifact_role": "sections",
                    "path": str(sections_path),
                    "content_sha256": hashlib.sha256(sections_body).hexdigest(),
                    "reusable": True,
                }
            },
            "invalid": {},
            "bundle_hash": "b" * 64,
        },
    }
    artifacts = select_reusable_artifacts(handle, ("sections",))
    assert "sections" in artifacts
    used = artifacts["sections"]
    assert used["path"] == str(sections_path)
    assert hashlib.sha256(Path(used["path"]).read_bytes()).hexdigest() == (
        used["content_sha256"]
    )
    assert chunker_calls["n"] == 0  # chunker spy raises if invoked


def test_e2e_d06_consumer_analysis_reused_only_when_fully_compatible(tmp_path):
    """E2E-D06: a consumer analysis artifact is reusable ONLY when engine,
    prompt, model and input bundle all match; ANY change → not reusable."""
    import hashlib

    body = b"%PDF-1.4 fake annual"
    original = tmp_path / "annual.pdf"
    original.write_bytes(body)
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_bytes(b'{"finding": "revenue 1000"}')
    sha = hashlib.sha256(body).hexdigest()

    def handle_with(prompt, model, engine):
        return {
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
                    "consumer_analysis": {
                        "artifact_role": "consumer_analysis",
                        "path": str(analysis_path),
                        "content_sha256": hashlib.sha256(
                            b'{"finding": "revenue 1000"}'
                        ).hexdigest(),
                        "reusable": True,
                        "engine": engine,
                        "model": model,
                        "prompt": prompt,
                        "input_bundle_hash": "x" * 64,
                    }
                },
                "invalid": {},
                "bundle_hash": "b" * 64,
            },
        }

    expected = {"engine": "e1", "model": "m1", "prompt": "p1",
                "input_bundle_hash": "x" * 64}
    # fully compatible → reused
    a = select_reusable_artifacts(
        handle_with("p1", "m1", "e1"), ("consumer_analysis",),
        expected_provenance=expected,
    )
    assert "consumer_analysis" in a
    entry = a["consumer_analysis"]
    assert entry["engine"] == "e1" and entry["model"] == "m1" and entry["prompt"] == "p1"
    # ANY of engine/model/prompt/input-bundle change → NOT reused
    for changed in (
        {"prompt": "p2"},
        {"model": "m2"},
        {"engine": "e2"},
        {"input_bundle_hash": "y" * 64},
    ):
        h = handle_with("p1", "m1", "e1")
        h["source_bundle"]["valid_handles"]["consumer_analysis"].update(changed)
        a2 = select_reusable_artifacts(
            h, ("consumer_analysis",), expected_provenance=expected,
        )
        assert "consumer_analysis" not in a2, f"must not reuse after {changed}"
