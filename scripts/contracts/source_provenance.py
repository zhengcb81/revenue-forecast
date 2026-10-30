"""HTTP provenance or an exact CWP original, without inventing a URL.

The shared original DTO owner supplies the same rules at source preparation
and persisted forecast input. This layer does no IO or source discovery.
"""

from __future__ import annotations
from datetime import date
from typing import Any
from contracts.evidence import (
    ForecastInputError,
    require,
    valid_source_url,
    validate_source_capture,
)
from contracts.source_clock import InformationEligibility
from contracts.company_wiki_original import (
    OriginalProvenanceError,
    SOURCE_READER_TOOL,
    validate_ref,
    validate_receipt,
    validate_manifest,
)

_FORBIDDEN = {
    "path",
    "canonical_path",
    "relative_path",
    "storage_path",
    "root_path",
    "filesystem_path",
}


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ForecastInputError(f"original provenance requires {label}")
    if _FORBIDDEN.intersection(value):
        raise ForecastInputError(
            f"original provenance {label} contains a physical path"
        )
    return value


def _same(actual: Any, expected: Any, label: str) -> None:
    if actual != expected or type(actual) is not type(expected):
        raise ForecastInputError(f"original provenance {label} mismatch")


def _verified_original_binding(source: dict[str, Any], as_of: date) -> None:
    trace = _object(source.get("company_wiki_trace"), "company_wiki_trace")
    ref = validate_ref(trace.get("source_ref"))
    receipt = validate_receipt(trace.get("read_receipt"), ref)
    manifest, _ = validate_manifest(
        trace.get("source_manifest"),
        ref,
        as_of,
        availability_evidence=receipt.get("availability_evidence"),
        current_read_at=receipt["read_at"],
    )
    capture = _object(source.get("capture"), "capture")
    _same(source.get("source_id"), ref["source_id"], "source_id")
    if manifest["source_url"] is not None:
        raise ForecastInputError(
            "original provenance null URL differs from source manifest"
        )
    _same(manifest["published_date"], source.get("published_date"), "published_date")
    if capture.get("capture_method") != "local_document":
        raise ForecastInputError("original provenance requires local_document capture")
    _same(
        capture.get("snapshot_sha256"), ref["content_sha256"], "capture.snapshot_sha256"
    )
    _same(capture.get("tool_name"), SOURCE_READER_TOOL, "capture.tool_name")
    host = _object(capture.get("host_receipt"), "capture.host_receipt")
    _same(
        host.get("event_sha256"),
        ref["content_sha256"],
        "capture.host_receipt.event_sha256",
    )
    _same(host.get("timestamp"), receipt["read_at"], "capture.host_receipt.timestamp")
    _same(host.get("tool_name"), SOURCE_READER_TOOL, "capture.host_receipt.tool_name")
    _same(host.get("issuer"), "company-wiki", "capture.host_receipt.issuer")
    _same(host.get("action"), "verified_read", "capture.host_receipt.action")


def validate_source_provenance(
    source: dict[str, Any],
    as_of: date,
    *,
    require_capture: bool = False,
    information_eligibility: InformationEligibility | None = None,
) -> None:
    """Preserve collector semantics; null URL always requires original lineage."""
    try:
        if "url" not in source:
            raise ForecastInputError(
                "source provenance requires an explicit url value or null"
            )
        local_original = source["url"] is None
        if local_original:
            _verified_original_binding(source, as_of)
        elif not valid_source_url(source["url"]):
            raise ForecastInputError(
                f"invalid, search-page, or placeholder URL for {source.get('source_id')}"
            )
        if local_original or require_capture:
            validate_source_capture(
                source, as_of, information_eligibility=information_eligibility
            )
    except (OriginalProvenanceError, ForecastInputError) as exc:
        require(False, str(exc))
