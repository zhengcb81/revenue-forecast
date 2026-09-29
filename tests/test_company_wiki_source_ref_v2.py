"""RED for the CWP 2.0 SourceRef reader before FF envelope integration.

The fixture is byte-identical to company-wiki producer commit 3dd41e1,
tests/golden/source_v2/source_ref.json (SHA-256 aca22689b9369151932d8402614c48d0122a8049fee3015b420264bcfd335cf1).
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
GOLDEN = ROOT / "tests" / "fixtures" / "cwp_source_ref_v2.json"
GOLDEN_SHA256 = "aca22689b9369151932d8402614c48d0122a8049fee3015b420264bcfd335cf1"


def _reader():
    try:
        return importlib.import_module("company_wiki_source_reader_v2")
    except ModuleNotFoundError:
        pytest.fail("RF SourceRef 2.0 reader has not been integrated")


def test_producer_golden_is_pinned_and_accepted_by_reader():
    raw = GOLDEN.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == GOLDEN_SHA256
    ref = json.loads(raw)
    assert ref["schema_version"] == "2.0"
    assert ref["byte_size"] == 62
    assert set(ref) == {
        "schema_version", "document_id", "source_id", "content_sha256",
        "byte_size", "mime_type",
    }
    _reader()._validate_ref(ref)


def test_malformed_source_ref_is_rejected_before_reader_io(monkeypatch, tmp_path):
    reader = _reader()

    def forbidden(*_args, **_kwargs):
        pytest.fail("reader IO started for invalid SourceRef")

    monkeypatch.setattr(reader, "_run_reader", forbidden)
    for field, value in (
        ("content_sha256", "not-a-sha256"),
        ("document_id", "urn:source\x00injected"),
    ):
        ref = json.loads(GOLDEN.read_text(encoding="utf-8"))
        ref[field] = value
        with pytest.raises(reader.SourceVersionTransportError):
            reader.open_source_version_v2(
                source_ref=ref,
                catalog_config=tmp_path / "source_catalog.yaml",
                as_of_date="2026-07-18",
                expected_fiscal_year=2025,
            )
