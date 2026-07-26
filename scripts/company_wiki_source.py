"""Build revenue schema-3.4 source records from a local acquisition handle.

The bundled ``filing_acquisition`` module owns identity, reuse-first lookup,
explicit market-routed download, canonical write, and provenance. This module
keeps only the revenue-specific conversion: turning one capture-ready handle
into a schema-3.4 source record with an immutable capture receipt. It verifies
the local whole-file hash but does not claim that a passage supports any
revenue parameter.
"""

from __future__ import annotations

from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any


_SOURCE_TYPES = {
    "audited_filing",
    "exchange_filing",
    "regulatory_filing",
    "official_statistics",
    "company_release",
    "investor_presentation",
    "earnings_transcript",
    "official_operating_data",
    "contract_award",
    "customer_filing",
    "tender_document",
    "sector_regulator",
    "industry_association",
    "primary_market_dataset",
    "specialist_research",
    "reputable_news",
}
_PROMPT_INJECTION_STATUSES = {"not_detected", "detected_and_ignored"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class CompanyWikiSourceError(RuntimeError):
    """Raised when a capture-ready source cannot be built from a handle."""


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise CompanyWikiSourceError(f"{field_name} must be non-empty trimmed text")
    return value


def _iso_date(value: Any, field_name: str) -> date:
    text = _required_text(value, field_name)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise CompanyWikiSourceError(f"{field_name} must use YYYY-MM-DD") from exc
    if parsed.isoformat() != text:
        raise CompanyWikiSourceError(f"{field_name} must be canonical YYYY-MM-DD")
    return parsed


def build_revenue_source_record(
    handle: dict[str, Any],
    *,
    as_of_date: str,
    source_type: str,
    publisher: str,
    page_or_section: str,
    prompt_injection_status: str,
) -> dict[str, Any]:
    """Build a strict revenue source/capture record from one verified handle.

    ``handle`` is returned by bundled ``filing_acquisition.resolve_filing``.
    ``source_type``, ``publisher``, evidence locator, and prompt-injection
    status remain explicit caller judgments. This function verifies the whole
    local file hash but does not claim that a passage supports any revenue
    parameter.
    """

    if not isinstance(handle, dict):
        raise TypeError("handle must be a dict")
    as_of = _iso_date(as_of_date, "as_of_date")
    if source_type not in _SOURCE_TYPES:
        raise CompanyWikiSourceError(f"unsupported revenue source_type: {source_type}")
    publisher = _required_text(publisher, "publisher")
    locator = _required_text(page_or_section, "page_or_section")
    if prompt_injection_status not in _PROMPT_INJECTION_STATUSES:
        raise CompanyWikiSourceError("prompt_injection_status must be explicitly reviewed")
    if handle.get("capture_ready") is not True:
        raise CompanyWikiSourceError("company-wiki handle is not capture_ready")
    published = _iso_date(handle.get("published_date"), "published_date")
    retrieved_at = _required_text(handle.get("retrieved_at"), "retrieved_at")
    try:
        captured = datetime.strptime(retrieved_at, "%Y-%m-%dT%H:%M:%SZ").date()
    except ValueError as exc:
        raise CompanyWikiSourceError("retrieved_at must be UTC YYYY-MM-DDTHH:MM:SSZ") from exc
    if not published <= captured <= as_of:
        raise CompanyWikiSourceError(
            "source capture is outside published <= captured <= as_of"
        )
    snapshot_sha256 = _required_text(
        handle.get("snapshot_sha256"), "snapshot_sha256"
    )
    if not _SHA256_RE.fullmatch(snapshot_sha256):
        raise CompanyWikiSourceError("snapshot_sha256 must be lowercase SHA-256")
    canonical_path = Path(_required_text(handle.get("canonical_path"), "canonical_path"))
    if not canonical_path.is_file():
        raise CompanyWikiSourceError("canonical_path does not identify a local source file")
    if _file_sha256(canonical_path) != snapshot_sha256:
        raise CompanyWikiSourceError("canonical source bytes do not match snapshot_sha256")
    url = _required_text(handle.get("https_url"), "https_url")
    if not url.startswith("https://"):
        raise CompanyWikiSourceError("https_url must use HTTPS")
    request_id = _required_text(handle.get("request_id"), "request_id")
    location_id = _required_text(
        handle.get("canonical_location_id"), "canonical_location_id"
    )
    capture = {
        "capture_schema_version": "1.0",
        "capture_method": "local_document",
        "tool_name": "revenue-forecast-filing-acquisition",
        "tool_call_id": f"{request_id}|{location_id}",
        "captured_date": captured.isoformat(),
        "snapshot_sha256": snapshot_sha256,
        "content_treatment": "untrusted_data_only",
        "prompt_injection_status": prompt_injection_status,
    }
    capture["receipt_sha256"] = _canonical_sha256(capture)
    return {
        "source_id": _required_text(handle.get("source_id"), "source_id"),
        "source_type": source_type,
        "title": _required_text(handle.get("title"), "title"),
        "publisher": publisher,
        "url": url,
        "published_date": published.isoformat(),
        "accessed_date": captured.isoformat(),
        "page_or_section": locator,
        "capture": capture,
        "company_wiki_trace": {
            "document_id": handle.get("document_id"),
            "source_id": handle.get("source_id"),
            "canonical_location_id": location_id,
            "canonical_path": str(canonical_path.resolve()),
            "provider": handle.get("provider"),
            "provider_document_id": handle.get("provider_document_id"),
            "collector_name": handle.get("collector_name"),
            "collector_version": handle.get("collector_version"),
        },
    }


__all__ = [
    "CompanyWikiSourceError",
    "build_revenue_source_record",
]
