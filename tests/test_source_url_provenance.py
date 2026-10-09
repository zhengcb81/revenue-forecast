"""A raw source URL is provenance, not an instruction to fetch or upgrade it."""
from copy import deepcopy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from contracts.evidence import valid_source_url  # noqa: E402
from company_wiki_source_v2 import build_revenue_source_record_from_verified_read  # noqa: E402
from test_company_wiki_source_v2 import BODY, _inputs, _candidate  # noqa: E402


@pytest.mark.parametrize("scheme", ["http", "https"])
def test_original_public_url_is_preserved_after_actual_verified_local_read(scheme):
    ref, receipt, manifest = deepcopy(_inputs())
    url = scheme + "://static.cninfo.com.cn/finalpage/2025-08-29/1224606011.PDF"
    manifest["source_url"] = url
    result = build_revenue_source_record_from_verified_read(
        source_ref=ref, read_receipt=receipt, source_bytes=BODY,
        source_manifest=manifest, source_candidate=_candidate(ref, manifest),
        as_of_date="2026-10-08", source_type="regulatory_filing",
        publisher="Official issuer disclosure", page_or_section="Business overview",
    )
    assert result["url"] == url
    assert result["company_wiki_trace"]["source_manifest"]["source_url"] == url
    assert result["capture"]["snapshot_sha256"] == ref["content_sha256"]


@pytest.mark.parametrize("url", [
    "file:///C:/original.pdf", "ftp://issuer.com/report.pdf", "javascript:alert(1)",
    "http://localhost/report", "https://www.google.com/search?q=issuer", "http://example.com/report",
])
def test_nonpublic_or_placeholder_reference_is_not_an_original_source(url):
    assert not valid_source_url(url)
