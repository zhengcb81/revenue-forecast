"""End-to-end query-first ensure service over adapters, writer, and journal."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any

from .acquisition import (
    AcquisitionCoordinator,
    AcquisitionResult,
    AcquisitionStatus,
)
from .acquisition_journal import AcquisitionAttempt, AcquisitionJournal
from .canonical_writer import (
    CanonicalImportResult,
    CanonicalImportStatus,
    CanonicalSourceWriter,
)
from .resolver import ResolutionResult, SourceRequest


SOURCE_ENSURE_SCHEMA_VERSION = "1.0"


class SourceEnsureStatus(str, Enum):
    REUSED = "reused"
    IMPORTED = "imported"
    DEDUPLICATED = "deduplicated"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"
    GAP = "gap"  # WU-4.2: metadata-only plan returned, nothing downloaded


@dataclass(frozen=True)
class SourceEnsureResult:
    schema_version: str
    status: SourceEnsureStatus
    acquisition: AcquisitionResult
    resolution: ResolutionResult
    attempt: AcquisitionAttempt
    canonical_import: CanonicalImportResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status.value,
            "acquisition": self.acquisition.to_dict(),
            "resolution": self.resolution.to_dict(),
            "attempt": self.attempt.to_dict(),
            "canonical_import": (
                self.canonical_import.to_dict() if self.canonical_import else None
            ),
        }


class SourceAcquisitionService:
    """Resolve first, stage only when required, then commit through the sole writer."""

    def __init__(
        self,
        *,
        coordinator: AcquisitionCoordinator,
        writer: CanonicalSourceWriter,
        journal: AcquisitionJournal,
    ):
        if not isinstance(coordinator, AcquisitionCoordinator):
            raise TypeError("coordinator must be AcquisitionCoordinator")
        if not isinstance(writer, CanonicalSourceWriter):
            raise TypeError("writer must be CanonicalSourceWriter")
        if not isinstance(journal, AcquisitionJournal):
            raise TypeError("journal must be AcquisitionJournal")
        self.coordinator = coordinator
        self.writer = writer
        self.journal = journal

    def _record_failure(
        self,
        request: SourceRequest,
        reason: str,
        content_sha256: str | None,
        exc: Exception,
        side_effects: dict[str, Any],
    ) -> None:
        """I-02-B: classify the failure through the single taxonomy, journal
        the structured fields (code/retryable/side_effects) and attach the
        envelope onto the exception that will pass through the CLI exit."""
        from .error_taxonomy import (
            classify_exception,
            attach_error_envelope,
            ENVELOPE_CODES,
        )

        code, retryable = classify_exception(exc)
        raw_code = getattr(exc, "error_code", None)
        raw_retryable = getattr(exc, "retryable", None)
        if isinstance(raw_code, str) and raw_code in ENVELOPE_CODES:
            # Adapter/harness-declared provider code (e.g. upstream_unavailable,
            # identity_contract): the provider-declared retryability is passed
            # through VERBATIM when it is a bool (passthrough contract, P1);
            # a non-bool declared value fails closed to False.
            code = raw_code
            retryable = raw_retryable if isinstance(raw_retryable, bool) else False
        self.journal.record(
            request_id=request.request_id,
            outcome="failed",
            reason=reason,
            content_sha256=(
                content_sha256
                or (
                    side_effects.get("content_sha256")
                    if isinstance(side_effects.get("content_sha256"), str)
                    else None
                )
            ),
            error_type=type(exc).__name__,
            error=str(exc),
            error_code=code,
            retryable=retryable if isinstance(retryable, bool) else None,
            side_effects_json=json.dumps(side_effects, sort_keys=True),
        )
        attach_error_envelope(
            exc,
            code=code,
            retryable=bool(retryable),
            stage=(
                "catalog_db"
                if code in ("catalog_busy", "catalog_locked", "db_timeout")
                else "staging"
                if reason == "canonical_import_failed" or code == "identity_contract"
                else "provider"
                if code == "upstream_unavailable"
                else "adapter_process"
            ),
            request_id=request.request_id,
            cause_chain=[{"reason": reason, "error_class": type(exc).__name__}],
            side_effects=side_effects,
        )

    def ensure(self, request: SourceRequest) -> SourceEnsureResult:
        if not isinstance(request, SourceRequest):
            raise TypeError("request must be SourceRequest")
        staging_root = getattr(self.coordinator, "staging_root", None)
        snapshot_before = _staging_snapshot(staging_root)
        try:
            acquisition = self.coordinator.resolve_or_stage(request)
        except Exception as exc:
            # I-02-B (D-W02 supplement): the journal carries the STAGED error
            # object (code/retryable/cause as structured fields) plus the REAL
            # side effects that already happened — a partially completed
            # staging window is never reported as zero downloads.
            after = _staging_snapshot(staging_root)
            effects = _diff_side_effects(snapshot_before, after)
            self._record_failure(
                request, "adapter_or_staging_failed", None, exc, effects
            )
            raise

        candidate = acquisition.candidate
        common = {
            "request_id": request.request_id,
            "adapter_name": acquisition.adapter_name,
            "candidate_id": candidate.candidate_id if candidate else None,
            "provider": candidate.provider if candidate else None,
            "provider_document_id": (
                candidate.provider_document_id if candidate else None
            ),
            "source_url": candidate.source_url if candidate else None,
            "reason": acquisition.reason,
        }
        if acquisition.status is AcquisitionStatus.REUSED:
            outcome = (
                "reused_after_discovery"
                if acquisition.candidate is not None
                else "reused_before_download"
            )
            attempt = self.journal.record(outcome=outcome, **common)
            return SourceEnsureResult(
                schema_version=SOURCE_ENSURE_SCHEMA_VERSION,
                status=SourceEnsureStatus.REUSED,
                acquisition=acquisition,
                resolution=acquisition.resolution,
                attempt=attempt,
            )
        if acquisition.status is AcquisitionStatus.MISSING:
            attempt = self.journal.record(outcome="missing", **common)
            return SourceEnsureResult(
                schema_version=SOURCE_ENSURE_SCHEMA_VERSION,
                status=SourceEnsureStatus.MISSING,
                acquisition=acquisition,
                resolution=acquisition.resolution,
                attempt=attempt,
            )
        if acquisition.status is AcquisitionStatus.AMBIGUOUS:
            attempt = self.journal.record(outcome="ambiguous", **common)
            return SourceEnsureResult(
                schema_version=SOURCE_ENSURE_SCHEMA_VERSION,
                status=SourceEnsureStatus.AMBIGUOUS,
                acquisition=acquisition,
                resolution=acquisition.resolution,
                attempt=attempt,
            )
        if acquisition.status is AcquisitionStatus.GAP:
            # WU-4.2: metadata-only plan surfaced to the caller; nothing was
            # downloaded and nothing was written. The plan hash is the basis
            # for any later authorized fetch (WU-4.3).
            plan = acquisition.gap_plan
            attempt = self.journal.record(
                outcome=(
                    "gap_plan_provider_unavailable"
                    if plan is not None and plan.provider_unavailable
                    else "gap_plan"
                ),
                **common,
            )
            return SourceEnsureResult(
                schema_version=SOURCE_ENSURE_SCHEMA_VERSION,
                status=SourceEnsureStatus.GAP,
                acquisition=acquisition,
                resolution=acquisition.resolution,
                attempt=attempt,
            )
        if candidate is None or acquisition.receipt is None:
            raise RuntimeError("staged acquisition is missing candidate or receipt")
        try:
            imported = self.writer.import_staged(
                request,
                candidate,
                acquisition.receipt,
            )
        except Exception as exc:
            # I-02-B: the download already happened and raw is staged — the
            # failure stage is canonical_import and the REAL side effects
            # (download_events=1 + staged bytes) must survive in the journal
            # and the envelope.
            effects = {
                "download_events": 1,
                "raw_bytes_saved": acquisition.receipt.byte_size,
                "staged_path": acquisition.receipt.staged_path,
                "content_sha256": acquisition.receipt.content_sha256,
            }
            self._record_failure(
                request,
                "canonical_import_failed",
                acquisition.receipt.content_sha256,
                exc,
                effects,
            )
            raise
        if imported.status is CanonicalImportStatus.IMPORTED_NEW:
            status = SourceEnsureStatus.IMPORTED
            outcome = "downloaded_new"
        else:
            status = SourceEnsureStatus.DEDUPLICATED
            outcome = "deduplicated_after_download"
        attempt = self.journal.record(
            outcome=outcome,
            content_sha256=imported.content_sha256,
            canonical_path=imported.canonical_path,
            **common,
        )
        return SourceEnsureResult(
            schema_version=SOURCE_ENSURE_SCHEMA_VERSION,
            status=status,
            acquisition=acquisition,
            resolution=imported.resolution,
            attempt=attempt,
            canonical_import=imported,
        )


__all__ = [
    "SOURCE_ENSURE_SCHEMA_VERSION",
    "SourceAcquisitionService",
    "SourceEnsureResult",
    "SourceEnsureStatus",
]


def _staging_snapshot(staging_root: Any) -> dict[str, int]:
    """Bytes per file currently staged (None → empty; never fabricates)."""
    files: dict[str, int] = {}
    if staging_root is None:
        return files
    root = Path(staging_root)
    if not root.is_dir():
        return files
    for item in root.rglob("*"):
        if item.is_file():
            files[str(item.relative_to(root))] = item.stat().st_size
    return files


def _diff_side_effects(
    before: dict[str, int],
    after: dict[str, int],
) -> dict[str, Any]:
    """Real side effects observed by comparing the staging tree across the
    degenerate window: files ADDED during the failed call count as one real
    download event (raw_bytes_saved = their total bytes); pre-existing or
    removed files are NOT counted as new events."""
    added = [name for name in after if name not in before]
    events = min(len(added), 1)
    return {
        "download_events": events,
        "raw_bytes_saved": sum(after[name] for name in added) if added else None,
        "staged_path": sorted(added)[0] if added else None,
    }
