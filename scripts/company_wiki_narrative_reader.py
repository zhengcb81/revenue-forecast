"""Explicit, read-only narrative adapter; no download or model fallback."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Sequence

from company_wiki_narrative_contracts import (
    RECEIPT_LIMIT, REQUEST_LIMIT, NarrativeContext, NarrativeTransportError,
    canonical_bytes, decode_object, validate_narrative_request, validate_narrative_response,
    validate_reference_request, validate_reference_response,
)
from company_wiki_narrative_process import run_bounded


def _command(config: Path, operation: str, reader_command: Sequence[str] | None) -> list[str]:
    if not isinstance(config, Path) or not config.is_absolute():
        raise NarrativeTransportError("blocked", "invalid_catalog_configuration")
    command = list(reader_command) if reader_command is not None else [
        sys.executable, "-B", "-m", "company_wiki.source_catalog.narrative_transport_cli",
    ]
    if not command or not all(isinstance(arg, str) and arg for arg in command):
        raise NarrativeTransportError("blocked", "invalid_reader_command")
    return [*command, "--config", str(config), "--operation", operation]


def _refused(returncode: int, stdout: bytes, stderr: bytes) -> None:
    if returncode == 0:
        return
    if stdout:
        raise NarrativeTransportError("unavailable", "partial_body_on_refusal")
    refusal = decode_object(stderr, limit=RECEIPT_LIMIT)
    if set(refusal) != {"schema_version", "status", "reason"} or (
        refusal["schema_version"] not in {"narrative-read-receipt/1", "narrative-read-receipt/3"}
        or refusal["status"] not in {"blocked", "not_found", "not_indexed", "unavailable", "ambiguous"}
        or not isinstance(refusal["reason"], str)
    ):
        raise NarrativeTransportError("unavailable", "reader_refused")
    import re
    if re.fullmatch(r"[a-z][a-z0-9_]{0,80}", refusal["reason"]) is None:
        raise NarrativeTransportError("unavailable", "reader_refused")
    raise NarrativeTransportError(refusal["status"], refusal["reason"])


def read_narrative_context(
    request: dict, *, catalog_config: Path, timeout_seconds: float = 30,
    reader_command: Sequence[str] | None = None,
    max_response_bytes: int | None = None, max_receipt_bytes: int | None = None,
) -> NarrativeContext:
    """Read one exact artifact, then check bytes, identity, time and citations."""
    request = validate_narrative_request(request)
    if max_response_bytes is not None and (type(max_response_bytes) is not int or max_response_bytes <= 0):
        raise NarrativeTransportError("blocked", "invalid_reader_limit")
    declared_size = request["narrative_ref"]["byte_size"]
    response_budget = declared_size if max_response_bytes is None else min(declared_size, max_response_bytes)
    result = run_bounded(
        _command(catalog_config, "read", reader_command), canonical_bytes(request),
        stdout_limit=response_budget, stderr_limit=max_receipt_bytes, timeout_seconds=timeout_seconds,
    )
    _refused(result.returncode, result.stdout, result.stderr)
    return validate_narrative_response(request, result.stdout, result.stderr)


def find_narrative_reference(
    request: dict, *, catalog_config: Path, timeout_seconds: float = 30,
    reader_command: Sequence[str] | None = None,
) -> dict:
    """Discover metadata only. The returned reference is not usable evidence."""
    request = validate_reference_request(request)
    result = run_bounded(
        _command(catalog_config, "reference", reader_command), canonical_bytes(request),
        stdout_limit=REQUEST_LIMIT, stderr_limit=RECEIPT_LIMIT, timeout_seconds=timeout_seconds,
    )
    _refused(result.returncode, result.stdout, result.stderr)
    return validate_reference_response(request, result.stdout, result.stderr)
