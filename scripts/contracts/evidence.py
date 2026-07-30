"""Hashes, validation helpers, and ForecastInputError for revenue contracts.

This module contains the pure utilities that every other contract and validation
function depends on.  They import only the standard library so that nothing in
``contracts.*`` creates an import cycle with ``revenue_core``.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date
from typing import Any
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Error contract
# ---------------------------------------------------------------------------


class ForecastInputError(ValueError):
    """Raised when an input violates the auditable revenue contract."""


def require(condition: bool, message: str) -> None:
    """Raise ``ForecastInputError`` when *condition* is falsy."""
    if not condition:
        raise ForecastInputError(message)


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------


def finite_number(value: Any, field: str) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{field} must be numeric")
    number = float(value)
    require(math.isfinite(number), f"{field} must be finite")
    return number


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------


def parse_iso_date(value: Any, field: str) -> date:
    require(isinstance(value, str) and bool(value.strip()), f"{field} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ForecastInputError(f"{field} must use YYYY-MM-DD") from exc


def period_year(value: Any, field: str) -> int:
    require(isinstance(value, str) and re.fullmatch(r"FY\d{4}", value) is not None, f"{field} must use strict FYyyyy format")
    return int(value[2:])


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()


def validate_claim_ids(
    claim_ids: Any,
    claim_index: dict[str, dict[str, Any]],
    target_type: str,
    target_id: str,
    field: str,
    support_type: str | None = None,
) -> list[dict[str, Any]]:
    require(isinstance(claim_ids, list) and claim_ids, f"{field} requires claim_ids")
    require(len(claim_ids) == len(set(claim_ids)), f"{field} contains duplicate claim_ids")
    claims: list[dict[str, Any]] = []
    for claim_id in claim_ids:
        require(claim_id in claim_index, f"unknown claim_id {claim_id} in {field}")
        claim = claim_index[claim_id]
        require(claim["target_type"] == target_type and claim["target_id"] == target_id, f"claim {claim_id} does not support {target_type}:{target_id}")
        if support_type is not None:
            require(claim["support_type"] == support_type, f"claim {claim_id} must use {support_type}")
        claims.append(claim)
    return claims


# ---------------------------------------------------------------------------
# Evidence-capture constants
# ---------------------------------------------------------------------------

EVIDENCE_CAPTURE_SCHEMA_VERSION = "1.0"

BLOCKED_HOSTS: set[str] = {
    "example.com",
    "www.example.com",
    "localhost",
    "127.0.0.1",
    "google.com",
    "www.google.com",
    "bing.com",
    "www.bing.com",
    "baidu.com",
    "www.baidu.com",
}

CAPTURE_METHODS: set[str] = {"browser_open", "api_response", "local_document", "structured_connector", "manual_open"}

PROMPT_INJECTION_STATUSES: set[str] = {"not_detected", "detected_and_ignored"}


# ---------------------------------------------------------------------------
# Source helpers
# ---------------------------------------------------------------------------


def valid_source_url(url: Any) -> bool:
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        return False
    if host in BLOCKED_HOSTS or host.endswith(".example"):
        return False
    return "." in host


def validate_source_capture(source: dict[str, Any], as_of: date) -> dict[str, Any]:
    """Validate a tool-linked source snapshot without claiming external fact truth."""
    source_id = source.get("source_id", "<unknown>")
    capture = source.get("capture")
    require(isinstance(capture, dict), f"{source_id}.capture is required")
    required = {
        "capture_schema_version", "capture_method", "tool_name", "tool_call_id",
        "captured_date", "snapshot_sha256", "content_treatment",
        "prompt_injection_status", "receipt_sha256",
    }
    require(set(capture) == required, f"invalid capture fields for {source_id}")
    require(capture["capture_schema_version"] == EVIDENCE_CAPTURE_SCHEMA_VERSION, f"unsupported capture schema for {source_id}")
    require(capture["capture_method"] in CAPTURE_METHODS, f"unsupported capture method for {source_id}")
    for field in ("tool_name", "tool_call_id"):
        require(isinstance(capture[field], str) and capture[field].strip(), f"{source_id}.capture.{field} is required")
    captured = parse_iso_date(capture["captured_date"], f"{source_id}.capture.captured_date")
    published = parse_iso_date(source.get("published_date"), f"{source_id}.published_date")
    require(published <= captured <= as_of, f"source capture is outside the allowed information set: {source_id}")
    require(source.get("accessed_date") == capture["captured_date"], f"source accessed_date/capture date mismatch: {source_id}")
    require(isinstance(capture["snapshot_sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", capture["snapshot_sha256"]), f"invalid source snapshot hash: {source_id}")
    require(capture["content_treatment"] == "untrusted_data_only", f"source content must be treated as untrusted data: {source_id}")
    require(capture["prompt_injection_status"] in PROMPT_INJECTION_STATUSES, f"invalid prompt-injection status: {source_id}")
    payload = {key: value for key, value in capture.items() if key != "receipt_sha256"}
    require(capture["receipt_sha256"] == canonical_sha256(payload), f"source capture receipt hash mismatch: {source_id}")
    return dict(capture)
