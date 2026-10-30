"""Pure company-wiki original DTO rules shared by preparation and evidence.

No provider, filesystem, identity refresh, access approval or forecast logic.
Legacy opaque document IDs and reader 2.1/2.2 shapes retain their exact rules.
"""

from __future__ import annotations
from datetime import date, datetime
import re
from typing import Any
from contracts.evidence import valid_source_url
from contracts.source_clock import (
    InformationEligibility,
    SourceClockError,
    qualify_source_information,
    validate_availability_evidence,
    validate_source_events,
)
from source_period_semantics import valid_fiscal_year


class OriginalProvenanceError(ValueError):
    """The supplied original DTO contradicts the existing CWP source contract."""


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PROMPT_INJECTION_STATUSES = {"not_reviewed", "not_detected", "detected_and_ignored"}
SOURCE_READER_TOOL = "company-wiki-source-version-reader"

_REF_FIELDS = {
    "schema_version",
    "document_id",
    "source_id",
    "content_sha256",
    "byte_size",
    "mime_type",
}
_RECEIPT_FIELDS = {
    "schema_version",
    "status",
    "document_id",
    "source_id",
    "content_sha256",
    "byte_size",
    "policy_sha256",
    "source_read_policy_sha256",
    "read_at",
    "review",
}
_MANIFEST_FIELDS = {
    "document_id",
    "source_id",
    "content_sha256",
    "byte_size",
    "mime_type",
    "title",
    "document_kind",
    "published_date",
    "source_url",
    "retrieved_at",
    "collector_name",
    "collector_version",
    "canonical_entity_id",
    "display_name",
    "market",
    "security_id",
    "fiscal_year",
    "fiscal_period",
    "period_end",
    "form_type",
    "provider",
    "provider_document_id",
    "language",
}
_REVIEW_FIELDS = {
    "status",
    "source_sha256",
    "evidence_sha256",
    "policy_hash",
    "reviewed_at",
}
_OUTCOMES = {"reused_existing", "reused_after_discovery", "downloaded_new"}
_FORBIDDEN_LOCATION_FIELDS = {
    "path",
    "canonical_path",
    "relative_path",
    "storage_path",
    "canonical_location_id",
    "root_path",
    "filesystem_path",
}
_TOOL_NAME = "company-wiki-source-version-reader"


def _required_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise OriginalProvenanceError(f"{field_name} must be non-empty trimmed text")
    return value


def _iso_date(value: Any, field_name: str) -> date:
    text = _required_text(value, field_name)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise OriginalProvenanceError(f"{field_name} must use YYYY-MM-DD") from exc
    if parsed.isoformat() != text:
        raise OriginalProvenanceError(f"{field_name} must be canonical YYYY-MM-DD")
    return parsed


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OriginalProvenanceError(f"{label} must be an object")
    return value


def _same(actual: Any, expected: Any, label: str) -> None:
    if type(actual) is not type(expected) or actual != expected:
        raise OriginalProvenanceError(f"{label} mismatch")


def _aware_datetime(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise OriginalProvenanceError(f"{label} must be timezone-aware")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OriginalProvenanceError(f"{label} must be timezone-aware") from exc
    offset = parsed.utcoffset()
    if parsed.tzinfo is None or offset is None:
        raise OriginalProvenanceError(f"{label} must be timezone-aware")
    if offset.total_seconds() != 0:
        raise OriginalProvenanceError(f"{label} must be UTC")
    return parsed


def _validate_ref_schema(ref: dict[str, Any]) -> None:
    if set(ref) != _REF_FIELDS or ref.get("schema_version") != "2.0":
        raise OriginalProvenanceError("source_ref fields/schema are unsupported")


def _validate_ref_metadata(ref: dict[str, Any]) -> None:
    for field in ("document_id", "source_id", "mime_type"):
        _required_text(ref.get(field), f"source_ref.{field}")


def _validate_ref_digest_and_size(ref: dict[str, Any]) -> None:
    digest = ref.get("content_sha256")
    if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
        raise OriginalProvenanceError("source_ref content_sha256 is invalid")
    size = ref.get("byte_size")
    if type(size) is not int or size < 0:
        raise OriginalProvenanceError("source_ref byte_size is invalid")


def validate_ref(source_ref: Any) -> dict[str, Any]:
    ref = _object(source_ref, "source_ref")
    _validate_ref_schema(ref)
    _validate_ref_metadata(ref)
    _validate_ref_digest_and_size(ref)
    return ref


def validate_receipt(receipt_value: Any, ref: dict[str, Any]) -> dict[str, Any]:
    receipt = _object(receipt_value, "read_receipt")
    expected = (
        _RECEIPT_FIELDS
        if receipt.get("schema_version") == "2.1"
        else _RECEIPT_FIELDS | {"availability_evidence"}
    )
    if receipt.get("schema_version") not in {"2.1", "2.2"} or set(receipt) != expected:
        raise OriginalProvenanceError("source read receipt fields/schema are invalid")
    if receipt.get("status") != "ok":
        raise OriginalProvenanceError("source read receipt is not successful")
    for field in ("document_id", "source_id", "content_sha256", "byte_size"):
        _same(receipt.get(field), ref[field], f"source read receipt {field}")
    for field in ("policy_sha256", "source_read_policy_sha256"):
        value = receipt.get(field)
        if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
            raise OriginalProvenanceError(f"source read receipt {field} is invalid")
    _aware_datetime(receipt.get("read_at"), "source read receipt read_at")
    _validate_review(receipt.get("review"), ref)
    try:
        validate_availability_evidence(
            receipt.get("availability_evidence"), ref["content_sha256"]
        )
    except SourceClockError as exc:
        raise OriginalProvenanceError(str(exc)) from exc
    return receipt


def _validate_review_shape(review: dict[str, Any]) -> None:
    if set(review) != _REVIEW_FIELDS:
        raise OriginalProvenanceError("source read receipt review is invalid")
    if review.get("status") not in _PROMPT_INJECTION_STATUSES:
        raise OriginalProvenanceError("source read receipt review is invalid")


def _validate_review_source(review: dict[str, Any], ref: dict[str, Any]) -> None:
    digest = review.get("source_sha256")
    if digest is not None and digest != ref["content_sha256"]:
        raise OriginalProvenanceError("source read receipt review source mismatch")


def _validate_review_hashes(review: dict[str, Any]) -> None:
    for field in ("evidence_sha256", "policy_hash"):
        digest = review.get(field)
        if digest is not None and (
            not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest)
        ):
            raise OriginalProvenanceError(
                f"source read receipt review {field} is invalid"
            )


def _validate_review(review: Any, ref: dict[str, Any]) -> None:
    if review is None:
        return
    value = _object(review, "source read receipt review")
    _validate_review_shape(value)
    _validate_review_source(value, ref)
    _validate_review_hashes(value)
    reviewed_at = value.get("reviewed_at")
    if reviewed_at is not None:
        _aware_datetime(reviewed_at, "source read receipt review reviewed_at")


def _validate_manifest_identity(
    manifest: dict[str, Any],
    ref: dict[str, Any],
) -> None:
    fields = ("document_id", "source_id", "content_sha256", "byte_size", "mime_type")
    for field in fields:
        _same(manifest.get(field), ref[field], f"source manifest {field}")


def _validate_manifest_metadata(manifest: dict[str, Any]) -> None:
    title = manifest.get("title")
    if title is not None and not isinstance(title, str):
        raise OriginalProvenanceError("source manifest title must be text or null")
    _required_text(manifest.get("document_kind"), "source manifest document_kind")
    if not valid_fiscal_year(manifest["document_kind"], manifest.get("fiscal_year")):
        raise OriginalProvenanceError("source manifest fiscal_year is invalid")
    fields = (
        "collector_name",
        "collector_version",
        "canonical_entity_id",
        "display_name",
        "market",
        "security_id",
        "form_type",
        "fiscal_period",
        "provider",
        "provider_document_id",
        "language",
    )
    for field in fields:
        if manifest.get(field) is not None:
            _required_text(manifest[field], f"source manifest {field}")


def _validate_manifest_dates(
    manifest: dict[str, Any],
    as_of: date,
    *,
    availability_evidence: Any = None,
    current_read_at: str | None = None,
) -> InformationEligibility:
    try:
        information = qualify_source_information(
            source_sha256=manifest["content_sha256"],
            published_date=manifest.get("published_date"),
            as_of=as_of,
            availability_evidence=availability_evidence,
        )
        validate_source_events(
            eligibility=information,
            original_retrieved_at=manifest.get("retrieved_at"),
            current_read_at=current_read_at,
        )
    except SourceClockError as exc:
        raise OriginalProvenanceError(str(exc)) from exc
    period_end = manifest.get("period_end")
    if (
        period_end is not None
        and _iso_date(period_end, "source manifest period_end")
        > information.available_by
    ):
        label = (
            "publication"
            if information.published_date is not None
            else "verified availability"
        )
        raise OriginalProvenanceError(f"source manifest period ends after {label}")
    return information


def _validate_manifest_url(manifest: dict[str, Any]) -> None:
    if manifest.get("source_url") is None:
        return
    source_url = _required_text(
        manifest.get("source_url"), "source manifest source_url"
    )
    if not valid_source_url(source_url):
        raise OriginalProvenanceError("source manifest source_url is invalid")


def validate_manifest(
    manifest_value: Any,
    ref: dict[str, Any],
    as_of: date,
    *,
    availability_evidence: Any = None,
    current_read_at: str | None = None,
) -> tuple[dict[str, Any], InformationEligibility]:
    manifest = _object(manifest_value, "source_manifest")
    if set(manifest) != _MANIFEST_FIELDS:
        raise OriginalProvenanceError("source manifest fields are invalid")
    _validate_manifest_identity(manifest, ref)
    _validate_manifest_metadata(manifest)
    published = _validate_manifest_dates(
        manifest,
        as_of,
        availability_evidence=availability_evidence,
        current_read_at=current_read_at,
    )
    _validate_manifest_url(manifest)
    return manifest, published
