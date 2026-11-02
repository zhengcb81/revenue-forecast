"""Opt-in exact-version source read through company-wiki's binary CLI.

The caller supplies a pathless SourceRef and a catalog configuration path.
Only the catalog chooses a physical location; this adapter checks its returned
bytes, receipt, identity, period and information date before use by RF.
"""

from __future__ import annotations

from datetime import date
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from contracts.company_wiki_original import (
    OriginalProvenanceError, VerifiedOriginalRead, verify_original_read,
)
from filing_upstream_cause import validated_source_failure_reason


_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
_REF_FIELDS = frozenset({
    "schema_version", "document_id", "source_id", "content_sha256",
    "byte_size", "mime_type",
})
_RECEIPT_FIELDS = frozenset({
    "schema_version", "status", "document_id", "source_id",
    "content_sha256", "byte_size", "policy_sha256",
    "source_read_policy_sha256", "read_at", "manifest", "review",
})
_MANIFEST_FIELDS = frozenset({
    "document_id", "source_id", "content_sha256", "byte_size", "mime_type",
    "title", "document_kind", "published_date", "source_url", "retrieved_at",
    "collector_name", "collector_version", "canonical_entity_id", "display_name",
    "market", "security_id", "fiscal_year", "fiscal_period", "period_end",
    "form_type", "provider", "provider_document_id", "language",
})
_REVIEW_FIELDS = frozenset({
    "status", "source_sha256", "evidence_sha256", "policy_hash", "reviewed_at",
})
_REVIEW_STATUSES = frozenset({
    "not_detected", "detected_and_ignored", "not_reviewed",
})
_REFUSAL_STATUSES = frozenset({
    "not_found", "not_indexed", "unavailable", "blocked", "ambiguous",
})
_REFUSAL_REASON = re.compile(r"[a-z][a-z0-9_]{0,80}\Z")


class SourceVersionTransportError(RuntimeError):
    """An exact source version could not be opened and verified."""

    def __init__(self, message: str, *, source_failure_reason: str | None = None):
        super().__init__(message)
        self.source_failure_reason = validated_source_failure_reason(source_failure_reason)






def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SourceVersionTransportError("duplicate JSON key in source receipt")
        result[key] = value
    return result

def _reject_nonfinite(_value: str) -> None:
    raise SourceVersionTransportError("nonfinite JSON number in source receipt")


def _one_json_line(raw: bytes) -> dict[str, Any]:
    try:
        decoded = raw.decode("utf-8", errors="strict")
        if not decoded.endswith("\n") or len(decoded.splitlines()) != 1:
            raise SourceVersionTransportError("source receipt must be one JSON line")
        value = json.loads(
            decoded, object_pairs_hook=_unique_pairs, parse_constant=_reject_nonfinite,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SourceVersionTransportError("source receipt is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise SourceVersionTransportError("source receipt must be a JSON object")
    return value


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _date(value: Any, field: str) -> date:
    if not isinstance(value, str) or not _DATE.fullmatch(value):
        raise SourceVersionTransportError(f"{field} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SourceVersionTransportError(f"{field} must be an ISO date") from exc






def _valid_ref_text(value: Any) -> bool:
    return (
        isinstance(value, str) and bool(value.strip()) and value == value.strip()
        and all(ord(char) >= 32 for char in value)
    )


def _validate_ref_identifiers(source_ref: dict[str, Any]) -> None:
    for field in ("document_id", "source_id", "mime_type"):
        if not _valid_ref_text(source_ref[field]):
            raise SourceVersionTransportError(f"source_ref {field} is invalid")


def _validate_ref(source_ref: dict[str, Any]) -> None:
    if not isinstance(source_ref, dict) or set(source_ref) != _REF_FIELDS:
        raise SourceVersionTransportError("source_ref fields are not exact")
    if source_ref["schema_version"] != "2.0":
        raise SourceVersionTransportError("source_ref schema is unsupported")
    _validate_ref_identifiers(source_ref)
    if not _valid_sha256(source_ref["content_sha256"]):
        raise SourceVersionTransportError("source_ref SHA-256 is invalid")
    size = source_ref["byte_size"]
    if type(size) is not int or size < 0:
        raise SourceVersionTransportError("source_ref byte_size is invalid")


def _run_reader(
    source_ref: dict[str, Any], config: Path, timeout_seconds: float, *,
    source_reader_receipt_version: str = "2.1",
) -> subprocess.CompletedProcess[bytes]:
    command = [
        sys.executable, "-B", "-m", "company_wiki.source_catalog.source_reader_cli",
        "--config", str(config),
        "--document-id", source_ref["document_id"],
        "--source-id", source_ref["source_id"],
        "--content-sha256", source_ref["content_sha256"],
        "--purpose", "filing_reuse",
    ]
    if source_reader_receipt_version == "2.2":
        command.append("--include-availability-evidence")
    environment = dict(os.environ)
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0  # type: ignore[attr-defined]
    try:
        return subprocess.run(
            command, env=environment, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=timeout_seconds, check=False,
            shell=False, creationflags=creationflags,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SourceVersionTransportError("source reader CLI unavailable", source_failure_reason="reader_unavailable") from exc














def _validate_timeout(timeout_seconds: float) -> None:
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)):
        raise SourceVersionTransportError("source reader timeout is invalid")
    if timeout_seconds <= 0 or not math.isfinite(timeout_seconds):
        raise SourceVersionTransportError("source reader timeout is invalid")


def _validate_open_request(
    source_ref: dict[str, Any], catalog_config: Path, as_of_date: str,
    expected_fiscal_year: int | None, timeout_seconds: float,
) -> date:
    _validate_ref(source_ref)
    if not isinstance(catalog_config, Path) or not catalog_config.is_absolute():
        raise SourceVersionTransportError("catalog_config must be an absolute Path")
    _validate_timeout(timeout_seconds)
    as_of = _date(as_of_date, "as_of_date")
    if expected_fiscal_year is not None and (type(expected_fiscal_year) is not int or expected_fiscal_year < 1):
        raise SourceVersionTransportError("expected_fiscal_year is invalid")
    return as_of


def _valid_refusal(refusal: dict[str, Any]) -> bool:
    return (
        set(refusal) == {"schema_version", "status", "reason"}
        and isinstance(refusal["schema_version"], str)
        and refusal["schema_version"] in {"2.1", "2.2"}
        and isinstance(refusal["status"], str)
        and refusal["status"] in _REFUSAL_STATUSES
        and isinstance(refusal["reason"], str)
        and _REFUSAL_REASON.fullmatch(refusal["reason"]) is not None
    )


def _raise_reader_refusal(opened: subprocess.CompletedProcess[bytes]) -> None:
    if opened.stdout:
        raise SourceVersionTransportError("source reader emitted partial bytes on refusal")
    try:
        refusal = _one_json_line(opened.stderr)
    except SourceVersionTransportError:
        raise SourceVersionTransportError("source reader refused current version") from None
    if _valid_refusal(refusal):
        reason = validated_source_failure_reason(refusal["reason"])
        message = f"source reader refused: {reason}" if reason is not None else "source reader refused current version"
        raise SourceVersionTransportError(message, source_failure_reason=reason)
    raise SourceVersionTransportError("source reader refused current version")


def validate_source_reader_receipt_version(value: Any) -> str:
    if not isinstance(value, str) or value not in {"2.1", "2.2"}:
        raise SourceVersionTransportError("source reader receipt capability must be 2.1 or 2.2")
    return value


def _validate_receipt_shape(receipt: dict[str, Any], *, source_reader_receipt_version: str = "2.1") -> None:
    expected = _RECEIPT_FIELDS if source_reader_receipt_version == "2.1" else _RECEIPT_FIELDS | {"availability_evidence"}
    if set(receipt) != expected or receipt.get("schema_version") != source_reader_receipt_version or receipt.get("status") != "ok":
        raise SourceVersionTransportError("source receipt fields/status invalid")










def open_source_version_v2(
    *, source_ref: dict[str, Any], catalog_config: Path,
    as_of_date: str, expected_fiscal_year: int | None,
    timeout_seconds: float = 30.0, source_reader_receipt_version: str = "2.1",
) -> VerifiedOriginalRead:
    """Return one immutable verified read; historical tuple unpack remains supported."""
    version = validate_source_reader_receipt_version(source_reader_receipt_version)
    as_of = _validate_open_request(
        source_ref, catalog_config, as_of_date, expected_fiscal_year, timeout_seconds,
    )
    reader_options = {"source_reader_receipt_version": version} if version == "2.2" else {}
    opened = _run_reader(source_ref, catalog_config, timeout_seconds, **reader_options)
    if opened.returncode != 0:
        _raise_reader_refusal(opened)
    receipt = _one_json_line(opened.stderr)
    _validate_receipt_shape(receipt, source_reader_receipt_version=version)
    bare_receipt = {key: value for key, value in receipt.items() if key != "manifest"}
    try:
        return verify_original_read(body=opened.stdout, source_ref=source_ref, receipt=bare_receipt,
            manifest=receipt["manifest"], as_of=as_of, expected_fiscal_year=expected_fiscal_year)
    except OriginalProvenanceError as exc:
        raise SourceVersionTransportError(str(exc),
            source_failure_reason=validated_source_failure_reason(str(exc).partition(":")[0])) from exc



__all__ = ["SourceVersionTransportError", "open_source_version_v2"]
