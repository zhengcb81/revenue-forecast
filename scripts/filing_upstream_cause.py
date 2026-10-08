"""Decode the versioned FF failure diagnostic; no research or retry decision."""
from __future__ import annotations

import json
from typing import Any

SCHEMA_VERSION = "filing-upstream-cause/1"
KEYS = frozenset({"schema_version", "operation", "code", "provider_started", "usage_complete", "retry_scope"})
OPERATIONS = frozenset({"identify", "ensure", "resolve", "close-gap", "query"})
RETRY_SCOPES = frozenset({"none", "catalog_contention", "caller_decision"})
# Versioned public vocabulary, not runtime imports of a provider's private files.
CODES = frozenset({
    "catalog_locked", "catalog_busy", "db_timeout", "worker_paused", "legacy_evidence_archived", "fatal",
    "maintenance_operation_retired", "producer_start_failed", "producer_deadline_exceeded",
    "producer_output_exceeded", "producer_transport_failure", "unknown",
    "adapter_process_failed", "adapter_timeout", "adapter_output_limit", "adapter_response_invalid",
    "adapter_not_bounded", "upstream_unavailable", "network_failed", "budget_exceeded", "provider_failed",
    "provider_not_configured", "invalid_request", "invalid_budget", "invalid_candidate", "missing_scratch",
    "invalid_scratch", "unsupported_language", "unsupported_sec_form", "unsupported_hk_period",
    "identity_mismatch", "invalid_provider_metadata", "primary_missing", "fiscal_period_unresolved",
    "missing_response", "staging_conflict", "sdk_asset_mismatch", "deadline_exceeded",
    "byte_budget_exceeded", "cost_budget_exceeded", "unsupported_content_encoding", "incomplete_response",
    "acquisition_budget_exceeded", "acquisition_validation_failed", "canonical_import_failed",
})


def validated_cause(value: Any) -> dict[str, Any] | None:
    """Retain only a safe six-field wire object, preserving bool/null exactly."""
    if not isinstance(value, dict) or set(value) != KEYS:
        return None
    if any(not isinstance(value[field], str) for field in ("schema_version", "operation", "code", "retry_scope")):
        return None
    if value["schema_version"] != SCHEMA_VERSION or value["operation"] not in OPERATIONS:
        return None
    if value["code"] not in CODES or value["retry_scope"] not in RETRY_SCOPES:
        return None
    if any(value[field] is not None and type(value[field]) is not bool for field in ("provider_started", "usage_complete")):
        return None
    return dict(value)


def failure_detail(payload: dict[str, Any]) -> dict[str, Any]:
    """A v2 filing's failure is independent of its transcript companion."""
    child = payload.get("filing")
    return child if payload.get("schema_version") == "2.0" and isinstance(child, dict) else payload


def extract_cause(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    return validated_cause(failure_detail(payload).get("upstream_cause"))


def parse_error_document(text: str) -> dict[str, Any] | None:
    """Decode a small stderr JSON error once; legacy text remains legacy text."""
    if len(text) > 65536:
        return None
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return None
    return value if isinstance(value, dict) else None
