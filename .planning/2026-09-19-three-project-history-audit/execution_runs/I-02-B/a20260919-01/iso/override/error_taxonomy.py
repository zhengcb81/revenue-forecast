"""ZR-204: unified DB busy/locked / operation-lock / timeout / paused
error taxonomy with the non-lock-never-retryable rule.

The counterexample (ZR102-F2, replayed fresh): a raw SQLite
``OperationalError("database is locked")`` emitted by the wiki CLI was
classified ``fatal``/non-retryable by filing-fetch, while only the
structured ``CatalogOperationLockedError`` mapped to ``catalog_locked``.
This module is the single classification truth: every raw form maps to a
canonical ``(code, retryable)`` pair, unknown forms fail closed to
``fatal`` (never retryable), and the CLI emits the structured shape.

Versioned: ``ERROR_TAXONOMY_VERSION``/``ERROR_TAXONOMY_SCHEMA``; consumers
treat unknown codes as fatal (N/N-1).
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

ERROR_TAXONOMY_VERSION = "1.0"
ERROR_TAXONOMY_SCHEMA = "error-taxonomy-1.0"

CATALOG_BUSY = "catalog_busy"  # raw SQLite busy/locked
CATALOG_LOCKED = "catalog_locked"  # operation lock (exclusive writer)
DB_TIMEOUT = "db_timeout"  # sqlite timeout / deadline
WORKER_PAUSED = "worker_paused"  # persistent worker pause
FATAL = "fatal"  # everything else (fail closed)
# Canonical codes.  Retryable codes are bounded by the consumer's deadline
# (ZR-205); everything else is fatal and must never be retried.

RETRYABLE_CODES = frozenset({CATALOG_BUSY, CATALOG_LOCKED, DB_TIMEOUT, WORKER_PAUSED})
# I-02-B (D-W02 supplement): the cross-CLI structured error envelope.  Every
# layer keeps the nested structures; consumers may reject unknown codes but
# must NOT stringify the provider payload before this point (the original
# CN-403 failure wrapped a retryable provider error into two outer layers'
# message strings, so the outermost saw ``retryable: false``).
ERROR_ENVELOPE_SCHEMA = "cross-cli-error-envelope/1.0"

ENVELOPE_CODES = frozenset(
    {
        "upstream_unavailable",
        CATALOG_BUSY,
        CATALOG_LOCKED,
        DB_TIMEOUT,
        WORKER_PAUSED,
        "bad_request",
        "identity_contract",
        FATAL,
    }
)

ENVELOPE_STAGES = frozenset(
    {
        "provider",  # remote discovery/API boundary
        "provider_download",  # remote fetch/bytes boundary
        "adapter_process",  # adapter subprocess contract layer
        "staging",  # local staging/identity binding
        "canonical_import",  # writer/import (post-download scan failure)
        "scan",  # catalog scan stage
        "catalog_db",  # SQLite DB busy/locked/deadline
        "envelope_normalization",  # this envelope's own normalization
        "envelope_validation",  # this envelope's own validation
        "invalid",
    }
)


# Table-driven: (code, marker substrings) per raw text family.  The first
# matching family wins; order encodes precedence (lock > timeout > paused).
_TEXT_FAMILIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        CATALOG_BUSY,
        ("database is locked", "database is busy", "database table is locked"),
    ),
    (DB_TIMEOUT, ("timeout", "timed out", "deadline exceeded")),
    (WORKER_PAUSED, ("paused", "worker paused", "persistent_pause")),
)

# Exact serialized-type → canonical code (N-1 structured forms).
_STRUCTURED_TYPES: dict[str, str] = {
    "CatalogOperationLockedError": CATALOG_LOCKED,
    "TimeoutError": DB_TIMEOUT,
    "ProgrammingError": DB_TIMEOUT,
}


def _code_for_text(text: str) -> str | None:
    lowered = text.lower()
    for code, markers in _TEXT_FAMILIES:
        if any(marker in lowered for marker in markers):
            return code
    return None


def classify_exception(exc: BaseException) -> tuple[str, bool]:
    """Classify a raised exception into ``(code, retryable)``."""
    exact = _STRUCTURED_TYPES.get(type(exc).__name__)
    if exact is not None:
        return exact, True
    if isinstance(exc, (TimeoutError, sqlite3.ProgrammingError)):
        return DB_TIMEOUT, True
    if isinstance(exc, sqlite3.OperationalError):
        code = _code_for_text(str(exc))
        return (code, True) if code is not None else (FATAL, False)
    code = _code_for_text(str(exc))
    if code == WORKER_PAUSED:
        return code, True
    return FATAL, False


def classify_error_type(error_type: str, error_text: str = "") -> tuple[str, bool]:
    """Classify a serialized ``error_type`` (+ optional error text) —
    the N-1/raw form: unknown types fail closed to fatal."""
    exact = _STRUCTURED_TYPES.get(error_type)
    if exact is not None:
        return exact, True
    if error_type == "OperationalError":
        code = _code_for_text(error_text)
        return (code, True) if code is not None else (FATAL, False)
    if error_type == "RuntimeError":
        code = _code_for_text(error_text)
        if code == WORKER_PAUSED:
            return code, True
    # N/N-1: unknown / arbitrary error types are fatal, never retryable.
    return FATAL, False


def is_retryable(code: str) -> bool:
    return code in RETRYABLE_CODES


def structured_error(
    exc: BaseException,
    *,
    request_id: str | None = None,
    stage: str | None = None,
    cause_chain: list[Any] | None = None,
    side_effects: dict[str, Any] | None = None,
    local_diag_ref: str | None = None,
) -> dict[str, Any]:
    """The CLI emission shape: {status, error_type, error, retryable}.

    I-02-B: optional envelope fields (request_id/stage/cause_chain/
    side_effects/local_diag_ref) ride alongside the legacy keys and keep the
    nested structures verbatim — never stringified/joined.
    """
    code, retryable = classify_exception(exc)
    payload: dict[str, Any] = {
        "status": "failed",
        "error_type": code,
        "code": code,
        "error": str(exc),
        "retryable": retryable,
        "error_envelope_schema_version": ERROR_ENVELOPE_SCHEMA,
    }
    if getattr(exc, "error_code", None):
        code_override = str(getattr(exc, "error_code"))
        if code_override in ENVELOPE_CODES:
            payload["error_type"] = payload["code"] = code_override
            raw_retryable = getattr(exc, "retryable", None)
            payload["retryable"] = (
                raw_retryable
                if isinstance(raw_retryable, bool)
                else is_retryable(code_override)
            )
    envelope = getattr(exc, "error_envelope", None) or getattr(
        exc, "envelope_fields", None
    )
    if isinstance(envelope, dict):
        request_id = envelope.get("request_id", request_id)
        stage = envelope.get("stage", stage)
        chain = envelope.get("cause_chain")
        if isinstance(chain, list):
            cause_chain = [*chain, *(cause_chain or [])]
        raw_effects = envelope.get("side_effects")
        if isinstance(raw_effects, dict) and side_effects is None:
            side_effects = raw_effects
        local_diag_ref = envelope.get("local_diag_ref", local_diag_ref)
    payload["request_id"] = str(request_id) if request_id else None
    payload["stage"] = str(stage) if stage else None
    payload["cause_chain"] = list(cause_chain) if cause_chain else []
    payload["side_effects"] = side_effects if isinstance(side_effects, dict) else None
    payload["local_diag_ref"] = local_diag_ref
    return payload


def normalize_upstream_payload(
    payload: Any,
    *,
    request_id: str | None = None,
    default_stage: str | None = None,
) -> dict[str, Any] | None:
    """Validate/normalize a candidate upstream error document into the frozen
    envelope.

    Accepted shapes (additive within ``cross-cli-error-envelope/1.0``):
    - the adapter 1.0 worker contract: ``{"schema_version":"1.0","status":
      "failed","adapter":{...},"error":{"code","message","retryable",...}}``
    - a flat envelope: ``{"code","retryable","request_id","stage",
      "cause_chain",...}``

    Returns ``None`` when the payload is not one structured error document
    (broken/garbage bytes are NOT guessed into fields; the caller archives
    the raw text under local_diag_ref instead).  Guarantees:
    - ``code`` is canonicalized; unknown values fail closed to ``fatal`` with
      the raw value preserved in cause_chain (N/N-1).
    - ``retryable`` is boolean-or-false; string ``'true'``/other non-bool
      values fail closed with a validation finding (n2b).
    """
    if not isinstance(payload, dict):
        return None
    findings: list[Any] = []
    candidate = None
    if payload.get("schema_version") == "1.0" and payload.get("status") == "failed":
        error_obj = payload.get("error")
        if not isinstance(error_obj, dict):
            return None
        candidate = dict(error_obj)
        adapter_obj = payload.get("adapter")
        if isinstance(adapter_obj, dict):
            findings.append({"stage": "adapter_process", "adapter": adapter_obj})
    elif isinstance(payload.get("code"), str):
        candidate = dict(payload)
    if candidate is None:
        return None
    raw_code = candidate.get("code")
    if not isinstance(raw_code, str) or not raw_code:
        return None
    findings.append(
        {
            "stage": "provider",
            "message": candidate.get("message"),
            "type": candidate.get("type"),
        }
    )
    if raw_code in ENVELOPE_CODES:
        code = raw_code
    else:
        code = FATAL
        findings.append(
            {
                "stage": "envelope_normalization",
                "unknown_code": raw_code,
                "rule": "N/N-1 unknown code fails closed to fatal, never retried",
            }
        )
    raw_retryable = candidate.get("retryable")
    if isinstance(raw_retryable, bool):
        # Passthrough contract (P1): a legitimately declared provider code
        # keeps its declared retryability; catalog/db codes stay taxonomy-
        # bound; unknown codes already fail closed above (fatal, False).
        retryable = raw_retryable
    else:
        retryable = False
        if raw_retryable is not None:
            # 'true' string etc: fail closed, never open the retry gate
            findings.append(
                {
                    "stage": "envelope_validation",
                    "issue": "retryable_not_bool",
                    "raw": raw_retryable,
                }
            )
    if code == FATAL:
        retryable = False  # n2a: unknown code NEVER opens the retry door
    elif code not in {"upstream_unavailable"}:
        retryable = retryable and is_retryable(code)
        if raw_retryable is not None:
            findings.append(
                {
                    "stage": "envelope_validation",
                    "issue": "retryable_not_bool",
                    "raw": raw_retryable,
                }
            )
    envelope: dict[str, Any] = {
        "error_envelope_schema_version": ERROR_ENVELOPE_SCHEMA,
        "status": "failed",
        "code": code,
        "error_type": code,
        "error": str(candidate.get("message", "")),
        "retryable": retryable,
        "request_id": (
            str(candidate.get("request_id") or request_id)
            if (candidate.get("request_id") or request_id)
            else None
        ),
        "stage": (
            str(candidate.get("stage"))
            if str(candidate.get("stage") or "") in ENVELOPE_STAGES
            else (str(default_stage) if default_stage in ENVELOPE_STAGES else None)
        ),
        "cause_chain": [
            *findings,
            *(
                list(candidate.get("cause_chain"))
                if isinstance(candidate.get("cause_chain"), list)
                else []
            ),
        ],
        "side_effects": (
            candidate["side_effects"]
            if isinstance(candidate.get("side_effects"), dict)
            else {"download_events": 0, "raw_bytes_saved": None, "staged_path": None}
        ),
        "local_diag_ref": candidate.get("local_diag_ref"),
    }
    return envelope


def attach_error_envelope(
    exc: BaseException,
    *,
    code: str | None = None,
    retryable: bool | None = None,
    stage: str | None = None,
    request_id: str | None = None,
    cause_chain: list[Any] | None = None,
    side_effects: dict[str, Any] | None = None,
    local_diag_ref: str | None = None,
) -> BaseException:
    """Best-effort: attach envelope fields to the raised exception so the CLI
    exit can preserve them structurally (classification still N/N-1)."""
    envelope_fields: dict[str, Any] = {}
    if code is not None:
        envelope_fields["code"] = code if code in ENVELOPE_CODES else FATAL
        envelope_fields["error_code"] = envelope_fields["code"]
        envelope_fields["retryable"] = bool(retryable) and is_retryable(
            envelope_fields["code"]
        )
    if stage is not None and stage in ENVELOPE_STAGES:
        envelope_fields["stage"] = stage
    if request_id is not None:
        envelope_fields["request_id"] = request_id
    if cause_chain is not None:
        envelope_fields["cause_chain"] = list(cause_chain)
    if side_effects is not None:
        envelope_fields["side_effects"] = side_effects
    if local_diag_ref is not None:
        envelope_fields["local_diag_ref"] = local_diag_ref
    if envelope_fields:
        setattr(exc, "error_envelope", envelope_fields)
        if "error_code" not in envelope_fields and code in ENVELOPE_CODES:
            exc.error_code = envelope_fields.get("code", code)  # type: ignore[attr-defined]
    return exc


__all__ = [
    "ERROR_TAXONOMY_VERSION",
    "ERROR_TAXONOMY_SCHEMA",
    "ERROR_ENVELOPE_SCHEMA",
    "CATALOG_BUSY",
    "CATALOG_LOCKED",
    "DB_TIMEOUT",
    "WORKER_PAUSED",
    "FATAL",
    "RETRYABLE_CODES",
    "classify_exception",
    "classify_error_type",
    "is_retryable",
    "structured_error",
    "normalize_upstream_payload",
    "attach_error_envelope",
]
