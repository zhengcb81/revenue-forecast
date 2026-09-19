"""Append-only, idempotent acquisition attempt journal and CSV read model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .lock import _acquisition_mutex
from .store import canonical_json


ACQUISITION_JOURNAL_SCHEMA_VERSION = "1.0"
ACQUISITION_OUTCOMES = frozenset(
    {
        "reused_before_download",
        "reused_after_discovery",
        "downloaded_new",
        "deduplicated_after_download",
        "missing",
        "ambiguous",
        "failed",
        # WU-4.2: metadata-only outcomes (nothing downloaded).
        "gap_plan",
        "gap_plan_provider_unavailable",
    }
)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _optional(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError("optional journal text must be null or non-empty trimmed text")
    return value


def _side_effects(value: str | None) -> str | None:
    """I-02-B: validate the side-effects JSON payload for the journal.

    Applies only to failure/receipt rows that carry real event counters;
    ``None`` stays ``None`` (strictly BEFORE any download window — never a
    silently-zero placeholder)."""
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError("side_effects_json must be null or valid JSON text")
    try:
        effects = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError("side_effects_json must be valid JSON") from exc
    if not isinstance(effects, dict):
        raise ValueError("side_effects_json must contain a JSON object")
    download_events = effects.get("download_events")
    if download_events is not None:
        if isinstance(download_events, bool) or not isinstance(download_events, int):
            raise ValueError("side_effects download_events must be an integer or null")
        if download_events not in (0, 1):
            raise ValueError(
                "side_effects download_events must be 0 (no download window) or 1"
            )
    raw_bytes = effects.get("raw_bytes_saved")
    if raw_bytes is not None and (
        isinstance(raw_bytes, bool) or not isinstance(raw_bytes, int) or raw_bytes < 0
    ):
        raise ValueError("side_effects raw_bytes_saved must be a non-negative integer")
    return canonical_json(effects)


@dataclass(frozen=True)
class AcquisitionAttempt:
    schema_version: str
    attempt_id: str
    recorded_at: str
    request_id: str
    outcome: str
    adapter_name: str | None = None
    candidate_id: str | None = None
    provider: str | None = None
    provider_document_id: str | None = None
    source_url: str | None = None
    content_sha256: str | None = None
    canonical_path: str | None = None
    reason: str | None = None
    error_type: str | None = None
    error: str | None = None
    # I-02-B (D-W02 supplement, additive): structured failure fields.  Legacy
    # journal lines (schema 1.0) simply omit them; defaults keep read_all
    # compatible.
    error_code: str | None = None
    retryable: bool | None = None
    side_effects_json: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


class AcquisitionJournal:
    """Persist one deterministic record per effective acquisition outcome."""

    def __init__(self, catalog_dir: Path):
        if not isinstance(catalog_dir, Path):
            raise TypeError("catalog_dir must be pathlib.Path")
        self.catalog_dir = catalog_dir
        self.path = catalog_dir / "acquisition_attempts.jsonl"

    def record(
        self,
        *,
        request_id: str,
        outcome: str,
        adapter_name: str | None = None,
        candidate_id: str | None = None,
        provider: str | None = None,
        provider_document_id: str | None = None,
        source_url: str | None = None,
        content_sha256: str | None = None,
        canonical_path: str | None = None,
        reason: str | None = None,
        error_type: str | None = None,
        error: str | None = None,
        error_code: str | None = None,
        retryable: bool | None = None,
        side_effects_json: str | None = None,
    ) -> AcquisitionAttempt:
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("request_id must be non-empty text")
        if outcome not in ACQUISITION_OUTCOMES:
            raise ValueError(f"unsupported acquisition outcome: {outcome}")
        values = {
            "request_id": request_id,
            "outcome": outcome,
            "adapter_name": _optional(adapter_name),
            "candidate_id": _optional(candidate_id),
            "provider": _optional(provider),
            "provider_document_id": _optional(provider_document_id),
            "source_url": _optional(source_url),
            "content_sha256": _optional(content_sha256),
            "canonical_path": _optional(canonical_path),
            "reason": _optional(reason),
            "error_type": _optional(error_type),
            "error": _optional(error),
            "error_code": _optional(error_code),
            # I-02-B: retryability is a BOOL or absent in the journal (never a
            # rented string from the provider payload).
            "retryable": (
                retryable if retryable is None or isinstance(retryable, bool) else False
            ),
            # side_effects_json: canonical JSON text of the real side-effects
            # counters ({download_events, raw_bytes_saved, ...}); validated.
            "side_effects_json": _side_effects(side_effects_json),
        }
        attempt_hash = hashlib.sha256(
            canonical_json(values).encode("utf-8")
        ).hexdigest()
        attempt = AcquisitionAttempt(
            schema_version=ACQUISITION_JOURNAL_SCHEMA_VERSION,
            attempt_id="urn:company-wiki:acquisition-attempt:sha256:" + attempt_hash,
            recorded_at=_utc_now(),
            **values,
        )
        # Append-only with unique attempt_ids: a per-file mutex suffices.
        # The global catalog operation lock must NOT be used here — the
        # worker's long batches hold it for hours, and journaling every
        # acquisition outcome (even read-only MISSING) would block on it.
        with _acquisition_mutex(self.path):
            existing = {item.attempt_id: item for item in self.read_all()}
            if attempt.attempt_id in existing:
                return existing[attempt.attempt_id]
            self.catalog_dir.mkdir(parents=True, exist_ok=True)
            encoded = (canonical_json(attempt.to_dict()) + "\n").encode("utf-8")
            with self.path.open("ab") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
        return attempt

    def read_all(self) -> tuple[AcquisitionAttempt, ...]:
        if not self.path.is_file():
            return ()
        attempts: list[AcquisitionAttempt] = []
        for line_number, raw in enumerate(
            self.path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
                attempts.append(AcquisitionAttempt(**value))
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(
                    f"invalid acquisition journal line {line_number}: {exc}"
                ) from exc
        return tuple(attempts)


__all__ = [
    "ACQUISITION_JOURNAL_SCHEMA_VERSION",
    "ACQUISITION_OUTCOMES",
    "AcquisitionAttempt",
    "AcquisitionJournal",
]
