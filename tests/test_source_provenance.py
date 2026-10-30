"""SourceRef originals are valid provenance without inventing a web URL."""

from copy import deepcopy
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests")]

import pytest  # noqa: E402

from contracts.evidence import (  # noqa: E402
    Collector,
    collect_mode,
    ForecastInputError,
    valid_source_url,
)
from contracts.document import validate_sources  # noqa: E402
from company_wiki_source import CompanyWikiSourceError  # noqa: E402
from test_company_wiki_source_v2 import _inputs, _build, SOURCE  # noqa: E402

AS_OF = date(2026, 9, 27)


def local_record(kind="investor_relations", unknown=False):
    ref, receipt, manifest = deepcopy(_inputs())
    manifest.update(
        source_url=None,
        document_kind=kind,
        fiscal_year=None,
        fiscal_period=None,
        period_end=None,
        form_type=None,
    )
    if unknown:
        manifest.update(published_date=None, retrieved_at=None)
        receipt.update(
            schema_version="2.2",
            availability_evidence={
                "schema_version": "source-availability-evidence/1",
                "source_sha256": ref["content_sha256"],
                "available_by": AS_OF.isoformat(),
                "basis": "current_verified_open",
                "evidence_ref": "cwp:verified-original",
                "locator": "/verified_open/verified_at",
            },
        )
    return _build(ref, receipt, manifest)


@pytest.mark.parametrize(
    "kind", ["investor_relations", "prospectus", "convertible_bond"]
)
@pytest.mark.parametrize("unknown", [False, True])
def test_verified_original_uses_no_fake_url_year_or_publication(kind, unknown):
    record = local_record(kind, unknown)
    assert record["url"] is None
    assert record["company_wiki_trace"]["source_manifest"]["fiscal_year"] is None
    if unknown:
        assert record["published_date"] is None
    frozen = deepcopy(record)
    for capture in [False, True]:
        assert (
            validate_sources({"sources": [record]}, AS_OF, require_capture=capture)[
                SOURCE
            ]["url"]
            is None
        )
    assert record == frozen
    assert not valid_source_url(None)


@pytest.mark.parametrize(
    "change",
    [
        "no_trace",
        "no_capture",
        "no_ref",
        "no_manifest",
        "no_read_receipt",
        "no_url",
        "ref_sha",
        "manifest_sha",
        "receipt_sha",
        "manifest_document",
        "receipt_source",
        "capture_sha",
        "not_local_capture",
        "manifest_url",
        "bad_status",
        "bad_receipt_version",
        "missing_proof",
        "future_publication",
        "backdated_cutoff",
    ],
)
@pytest.mark.parametrize("require_capture", [False, True])
def test_null_url_never_substitutes_for_current_verified_original(
    change, require_capture
):
    record = local_record(unknown=True)
    trace = record["company_wiki_trace"]
    cutoff = AS_OF
    if change == "no_trace":
        del record["company_wiki_trace"]
    elif change == "no_url":
        del record["url"]
    elif change == "no_capture":
        del record["capture"]
    elif change == "no_ref":
        del trace["source_ref"]
    elif change == "no_manifest":
        del trace["source_manifest"]
    elif change == "no_read_receipt":
        del trace["read_receipt"]
    elif change == "ref_sha":
        trace["source_ref"]["content_sha256"] = "f" * 64
    elif change == "manifest_sha":
        trace["source_manifest"]["content_sha256"] = "f" * 64
    elif change == "receipt_sha":
        trace["read_receipt"]["content_sha256"] = "f" * 64
    elif change == "manifest_document":
        trace["source_manifest"]["document_id"] = "another-original"
    elif change == "receipt_source":
        trace["read_receipt"]["source_id"] = "another-source"
    elif change == "capture_sha":
        record["capture"]["snapshot_sha256"] = "f" * 64
    elif change == "not_local_capture":
        record["capture"]["capture_method"] = "web_fetch"
    elif change == "manifest_url":
        trace["source_manifest"]["source_url"] = "https://sec.gov/original"
    elif change == "bad_status":
        trace["read_receipt"]["status"] = "not_found"
    elif change == "bad_receipt_version":
        trace["read_receipt"]["schema_version"] = "2.0"
    elif change == "missing_proof":
        del record["availability_evidence"]
    elif change == "future_publication":
        record["published_date"] = trace["source_manifest"]["published_date"] = (
            "2026-09-28"
        )
    elif change == "backdated_cutoff":
        cutoff = date(2026, 9, 26)
    with pytest.raises((ForecastInputError, CompanyWikiSourceError, ValueError)):
        validate_sources({"sources": [record]}, cutoff, require_capture=require_capture)


@pytest.mark.parametrize(
    "bad_url", ["", "urn:company-wiki:source:abc", "local_path", "file:///raw.pdf"]
)
def test_invalid_non_null_url_does_not_enter_the_original_branch(bad_url, tmp_path):
    if bad_url == "local_path":
        bad_url = str(tmp_path / "original.pdf")
    record = local_record()
    record["url"] = bad_url
    with pytest.raises(ForecastInputError):
        validate_sources({"sources": [record]}, AS_OF)


def test_existing_http_record_remains_unchanged():
    ref, receipt, manifest = deepcopy(_inputs())
    record = _build(ref, receipt, manifest)
    assert (
        validate_sources({"sources": [record]}, AS_OF, require_capture=True)[SOURCE][
            "url"
        ]
        == manifest["source_url"]
    )


def test_invalid_http_provenance_keeps_collector_mode():
    record = local_record()
    record["url"] = "urn:not-a-public-url"
    collector = Collector()
    with collect_mode(collector):
        validate_sources({"sources": [record]}, AS_OF)
    assert len(collector.errors) == 1
    assert "URL" in collector.errors[0][1]


@pytest.mark.parametrize(
    "change",
    [
        "manifest_missing_kind",
        "manifest_periodic_no_year",
        "manifest_bad_period_end",
        "manifest_future_period_end",
        "manifest_retrieved_before_publication",
        "manifest_retrieved_after_read",
        "receipt_missing_review",
        "receipt_extra_path",
        "capture_tool_mismatch",
        "host_action_mismatch",
        "host_issuer_mismatch",
    ],
)
def test_mutated_original_contract_is_rejected(change, tmp_path):
    record = local_record()
    trace = record["company_wiki_trace"]
    manifest, receipt = trace["source_manifest"], trace["read_receipt"]
    if change == "manifest_missing_kind":
        del manifest["document_kind"]
    elif change == "manifest_periodic_no_year":
        manifest["document_kind"] = "annual_report"
        manifest["fiscal_year"] = None
    elif change == "manifest_bad_period_end":
        manifest["period_end"] = "not-a-date"
    elif change == "manifest_future_period_end":
        manifest["period_end"] = "2027-01-01"
    elif change == "manifest_retrieved_before_publication":
        manifest["retrieved_at"] = "2020-01-01T00:00:00Z"
    elif change == "manifest_retrieved_after_read":
        manifest["retrieved_at"] = "2030-01-01T00:00:00Z"
    elif change == "receipt_missing_review":
        del receipt["review"]
    elif change == "receipt_extra_path":
        receipt["physical_path"] = str(tmp_path / "source.pdf")
    elif change == "capture_tool_mismatch":
        record["capture"]["tool_name"] = "unrelated-tool"
    else:
        key = "action" if change == "host_action_mismatch" else "issuer"
        record["capture"]["host_receipt"][key] = "unrelated"
    # Re-hash only caller-owned receipts to distinguish broken binding from a
    # trivial stale self-hash. This does not pretend to authenticate CWP.
    from contracts.evidence import canonical_sha256

    host = record["capture"]["host_receipt"]
    host["receipt_sha256"] = canonical_sha256(
        {k: v for k, v in host.items() if k != "receipt_sha256"}
    )
    capture = record["capture"]
    capture["receipt_sha256"] = canonical_sha256(
        {k: v for k, v in capture.items() if k != "receipt_sha256"}
    )
    with pytest.raises((ForecastInputError, ValueError)):
        validate_sources({"sources": [record]}, AS_OF, require_capture=False)


def test_valid_local_and_http_stay_pure():
    local = local_record(unknown=True)
    frozen = deepcopy(local)
    validate_sources({"sources": [local]}, AS_OF, require_capture=False)
    assert local == frozen


@pytest.mark.parametrize("period", [["FY"], " FY "])
def test_period_label_is_optional_trimmed_text(period):
    record = local_record()
    record["company_wiki_trace"]["source_manifest"]["fiscal_period"] = period
    with pytest.raises(ForecastInputError):
        validate_sources({"sources": [record]}, AS_OF)


@pytest.mark.parametrize("location", ["capture", "host"])
def test_all_missing_capture_fields_are_collector_safe(location):
    original = local_record()
    fields = (
        original["capture"]
        if location == "capture"
        else original["capture"]["host_receipt"]
    )
    for field in fields:
        record = deepcopy(original)
        target = (
            record["capture"]
            if location == "capture"
            else record["capture"]["host_receipt"]
        )
        del target[field]
        collector = Collector()
        with collect_mode(collector):
            validate_sources({"sources": [record]}, AS_OF, require_capture=False)
        assert collector.errors, (location, field)


@pytest.mark.parametrize("field", ["signature", "public_key_fingerprint"])
def test_optional_signature_pair_is_collector_safe(field):
    record = local_record()
    record["capture"]["host_receipt"][field] = "0" * (
        128 if field == "signature" else 32
    )
    collector = Collector()
    with collect_mode(collector):
        validate_sources({"sources": [record]}, AS_OF)
    assert collector.errors
