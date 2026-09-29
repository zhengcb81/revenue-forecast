"""Opt-in exact-version source read through company-wiki's binary CLI.

The caller supplies a pathless SourceRef and a catalog configuration path.
Only the catalog chooses a physical location; this adapter checks its returned
bytes, receipt, identity, period and information date before use by RF.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


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


def _datetime(value: Any, field: str, *, require_utc: bool = False) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise SourceVersionTransportError(f"{field} must be timezone-aware")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SourceVersionTransportError(f"{field} must be timezone-aware") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SourceVersionTransportError(f"{field} must be timezone-aware")
    if require_utc and parsed.utcoffset().total_seconds() != 0:
        raise SourceVersionTransportError(f"{field} must be UTC")
    return parsed.astimezone(UTC)


def _validate_ref(source_ref: dict[str, Any]) -> None:
    if not isinstance(source_ref, dict) or set(source_ref) != _REF_FIELDS:
        raise SourceVersionTransportError("source_ref fields are not exact")
    if source_ref["schema_version"] != "2.0":
        raise SourceVersionTransportError("source_ref schema is unsupported")
    for field in ("document_id", "source_id", "mime_type"):
        value = source_ref[field]
        if (
            not isinstance(value, str) or not value.strip()
            or value != value.strip() or any(ord(char) < 32 for char in value)
        ):
            raise SourceVersionTransportError(f"source_ref {field} is invalid")
    if not _valid_sha256(source_ref["content_sha256"]):
        raise SourceVersionTransportError("source_ref SHA-256 is invalid")
    size = source_ref["byte_size"]
    if type(size) is not int or size < 0:
        raise SourceVersionTransportError("source_ref byte_size is invalid")


def _run_reader(
    source_ref: dict[str, Any], config: Path, timeout_seconds: float,
) -> subprocess.CompletedProcess[bytes]:
    command = [
        sys.executable, "-B", "-m", "company_wiki.source_catalog.source_reader_cli",
        "--config", str(config),
        "--document-id", source_ref["document_id"],
        "--source-id", source_ref["source_id"],
        "--content-sha256", source_ref["content_sha256"],
        "--purpose", "filing_reuse",
    ]
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
        raise SourceVersionTransportError("source reader CLI unavailable") from exc


def _validate_review(review: Any, source_ref: dict[str, Any]) -> None:
    # The review is diagnostic. It is not an authorization or a precondition.
    if review is None:
        return
    if not isinstance(review, dict) or set(review) != _REVIEW_FIELDS:
        raise SourceVersionTransportError("source receipt review shape invalid")
    if review["status"] not in _REVIEW_STATUSES:
        raise SourceVersionTransportError("source receipt review status invalid")
    if review["source_sha256"] is not None and (
        review["source_sha256"] != source_ref["content_sha256"]
    ):
        raise SourceVersionTransportError("source receipt review source mismatch")
    for field in ("evidence_sha256", "policy_hash"):
        if review[field] is not None and not _valid_sha256(review[field]):
            raise SourceVersionTransportError(f"source receipt review {field} invalid")
    if review["reviewed_at"] is not None:
        _datetime(review["reviewed_at"], "source receipt review reviewed_at")


def _validate_manifest(
    manifest: Any, source_ref: dict[str, Any], as_of: date, fiscal_year: int,
) -> dict[str, Any]:
    if not isinstance(manifest, dict) or set(manifest) != _MANIFEST_FIELDS:
        raise SourceVersionTransportError("source receipt manifest fields invalid")
    for field in ("document_id", "source_id", "content_sha256", "byte_size", "mime_type"):
        if type(manifest[field]) is not type(source_ref[field]) or (
            manifest[field] != source_ref[field]
        ):
            raise SourceVersionTransportError(f"source manifest {field} mismatch")
    if type(manifest["fiscal_year"]) is not int or manifest["fiscal_year"] != fiscal_year:
        raise SourceVersionTransportError("source manifest fiscal_year mismatch")
    published = _date(manifest["published_date"], "source manifest published_date")
    retrieved = _datetime(manifest["retrieved_at"], "source manifest retrieved_at")
    period_end = manifest["period_end"]
    if period_end is not None and _date(period_end, "source manifest period_end") > published:
        raise SourceVersionTransportError("source manifest period ends after publication")
    if not (published <= retrieved.date() <= as_of):
        raise SourceVersionTransportError("source manifest is outside as_of_date")
    return manifest


def open_source_version_v2(
    *, source_ref: dict[str, Any], catalog_config: Path,
    as_of_date: str, expected_fiscal_year: int,
    timeout_seconds: float = 30.0,
) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    """Return verified source bytes, a pathless receipt, and a same-call manifest."""
    _validate_ref(source_ref)
    if not isinstance(catalog_config, Path) or not catalog_config.is_absolute():
        raise SourceVersionTransportError("catalog_config must be an absolute Path")
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)):
        raise SourceVersionTransportError("source reader timeout is invalid")
    if timeout_seconds <= 0 or not math.isfinite(timeout_seconds):
        raise SourceVersionTransportError("source reader timeout is invalid")
    as_of = _date(as_of_date, "as_of_date")
    if type(expected_fiscal_year) is not int or expected_fiscal_year < 1:
        raise SourceVersionTransportError("expected_fiscal_year is invalid")

    opened = _run_reader(source_ref, catalog_config, timeout_seconds)
    if opened.returncode != 0:
        if opened.stdout:
            raise SourceVersionTransportError("source reader emitted partial bytes on refusal")
        try:
            refusal = _one_json_line(opened.stderr)
        except SourceVersionTransportError:
            raise SourceVersionTransportError("source reader refused current version") from None
        reason = refusal.get("reason")
        if (
            set(refusal) == {"schema_version", "status", "reason"}
            and refusal["schema_version"] == "2.1"
            and refusal["status"] in _REFUSAL_STATUSES
            and isinstance(reason, str)
            and _REFUSAL_REASON.fullmatch(reason)
        ):
            raise SourceVersionTransportError(f"source reader refused: {reason}")
        raise SourceVersionTransportError("source reader refused current version")

    receipt = _one_json_line(opened.stderr)
    if set(receipt) != _RECEIPT_FIELDS or (
        receipt["schema_version"] != "2.1" or receipt["status"] != "ok"
    ):
        raise SourceVersionTransportError("source receipt fields/status invalid")
    for field in ("document_id", "source_id", "content_sha256", "byte_size"):
        if type(receipt[field]) is not type(source_ref[field]) or (
            receipt[field] != source_ref[field]
        ):
            raise SourceVersionTransportError(f"source receipt {field} mismatch")
    for field in ("policy_sha256", "source_read_policy_sha256"):
        if not _valid_sha256(receipt[field]):
            raise SourceVersionTransportError(f"source receipt {field} invalid")
    _datetime(receipt["read_at"], "source receipt read_at", require_utc=True)
    _validate_review(receipt["review"], source_ref)
    manifest = _validate_manifest(
        receipt["manifest"], source_ref, as_of, expected_fiscal_year,
    )
    if len(opened.stdout) != source_ref["byte_size"] or (
        hashlib.sha256(opened.stdout).hexdigest() != source_ref["content_sha256"]
    ):
        raise SourceVersionTransportError("source bytes SHA-256/size mismatch")
    bare_receipt = {key: value for key, value in receipt.items() if key != "manifest"}
    return opened.stdout, bare_receipt, manifest


__all__ = ["SourceVersionTransportError", "open_source_version_v2"]
