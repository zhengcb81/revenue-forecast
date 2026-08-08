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
