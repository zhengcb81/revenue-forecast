"""End-to-end query-first ensure service over adapters, writer, and journal."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from .acquisition import (
    AcquisitionCoordinator,
    AcquisitionResult,
    AcquisitionStatus,
    DownloadCandidate,
    DownloadReceipt,
)
from .acquisition_journal import AcquisitionAttempt, AcquisitionJournal
from .canonical_writer import (
    CanonicalImportResult,
    CanonicalImportStatus,
    CanonicalSourceWriter,
)
from .resolver import ResolutionResult, SourceRequest


SOURCE_ENSURE_SCHEMA_VERSION = "1.0"
# I-02-C (D-W02 supplement): approved register-existing recovery callers.
RECOVERY_AUTHORIZED_CALLERS = frozenset(
    {
        "register-existing-manifest",
        "I-02-C sample-copy-manifest",
    }
)


class SourceEnsureStatus(str, Enum):
    REUSED = "reused"
    IMPORTED = "imported"
    DEDUPLICATED = "deduplicated"
    REGISTERED_EXISTING = "registered_existing"  # I-02-C recovery
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"
    GAP = "gap"  # WU-4.2: metadata-only plan returned, nothing downloaded


@dataclass(frozen=True)
class SourceRecoveryInput:
    """I-02-C: caller-supplied binding for an already-on-disk canonical raw.

    Recovery is explicit and location-bound: the caller must name the raw
    file and its adjacent immutable sidecar.  The journal is only used for
    corroboration, never for file-system discovery, and nothing is
    inferred from filenames."""

    raw_path: str
    sidecar_path: str
    authorized_caller: str = "register-existing-manifest"

    def __post_init__(self) -> None:
        for name in ("raw_path", "sidecar_path", "authorized_caller"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"recovery {name} must be non-empty text")
        if self.authorized_caller not in RECOVERY_AUTHORIZED_CALLERS:
            raise ValueError(
                "recovery authorized_caller is not on the approved caller list"
            )
        raw = Path(self.raw_path)
        sidecar = Path(self.sidecar_path)
        if sidecar.name != raw.name + ".source.json":
            raise ValueError(
                "recovery sidecar_path must be the raw file's adjacent "
                "provenance (<raw>.source.json)"
            )


@dataclass(frozen=True)
class SourceEnsureResult:
    schema_version: str
    status: SourceEnsureStatus
    acquisition: AcquisitionResult | None
    resolution: ResolutionResult
    attempt: AcquisitionAttempt
    canonical_import: CanonicalImportResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status.value,
            "acquisition": (
                self.acquisition.to_dict() if self.acquisition is not None else None
            ),
            "resolution": self.resolution.to_dict(),
            "attempt": self.attempt.to_dict(),
            "canonical_import": (
                self.canonical_import.to_dict() if self.canonical_import else None
            ),
        }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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

    # ------------------------------------------------------------------
    # I-02-E: restart selection — the first unfinished stage per durable
    # evidence.  Recovery never invents intermediates, never re-downloads
    # (the coordinator is bypassed when stage rows bind this recovery key)
    # and never verifies cheaply (files are re-hashed each time).
    # ------------------------------------------------------------------
    def _resume_plan(self, request: SourceRequest) -> dict[str, Any] | None:
        rows = [
            item
            for item in self.journal.read_all()
            if item.request_id == request.request_id
            and item.provider == request.provider
            and item.provider_document_id == request.provider_document_id
            and item.content_sha256
            and item.outcome.startswith("stage_")
        ]
        if not rows:
            return None
        staged_rows = [r for r in rows if r.outcome == "stage_staged_verified"]
        if not staged_rows:
            raise RuntimeError(
                "resume stage rows exist without stage_staged_verified; "
                "journal/order is inconsistent for "
                f"{request.request_id} - recovery refuses to guess"
            )
        s1 = max(staged_rows, key=lambda r: r.recorded_at)
        payload = json.loads(s1.payload_json or "{}")
        receipt_dict = json.loads(payload.get("receipt_json", "{}"))
        candidate_dict = json.loads(payload.get("candidate_json", "{}"))
        content_sha256 = s1.content_sha256
        byte_size = int(receipt_dict.get("byte_size", 0))
        staged_path = payload.get("staged_path")
        sidecar_b64 = payload.get("sidecar_bytes_b64")
        raw_saved = False
        raw_path = None
        raw_rows = [r for r in rows if r.outcome == "stage_raw_saved"]
        raw_row = max(raw_rows, key=lambda r: r.recorded_at) if raw_rows else None
        if raw_row is not None and raw_row.canonical_path:
            candidate_raw = Path(raw_row.canonical_path)
            raw_saved = bool(
                candidate_raw.is_file()
                and candidate_raw.stat().st_size == byte_size
                and _sha256_file(candidate_raw) == content_sha256
            )
            raw_path = str(candidate_raw) if candidate_raw.is_file() else None
        sidecar_saved = False
        prov_rows = [r for r in rows if r.outcome == "stage_provenance_saved"]
        prov_row = max(prov_rows, key=lambda r: r.recorded_at) if prov_rows else None
        if prov_row is not None and prov_row.canonical_path:
            prov_payload = json.loads(prov_row.payload_json or "{}")
            candidate_side = Path(prov_row.canonical_path).with_name(
                Path(prov_row.canonical_path).name + ".source.json"
            )
            expected_side = prov_payload.get("sidecar_sha256")
            sidecar_saved = bool(
                candidate_side.is_file()
                and expected_side
                and _sha256_file(candidate_side) == expected_side
            )
        qualified = any(r.outcome == "stage_qualified" for r in rows)
        registered_durable = self._registration_durable(content_sha256)
        return {
            "kind": "import_staged",
            "staged_file_present": bool(staged_path and Path(staged_path).is_file()),
            "receipt": receipt_dict,
            "candidate": candidate_dict,
            "sidecar_payload_b64": sidecar_b64,
            "raw_saved": raw_saved,
            "raw_path": raw_path,
            "sidecar_saved": sidecar_saved,
            "qualified": qualified,
            "registration_durable": registered_durable,
        }

    def _registration_durable(self, content_sha256: str) -> bool:
        """Independent durable-evidence check (D-W02): active original_primary
        location + active document on one source, AND the latest scan run is
        'completed' (an interrupted/running row means the registration rows
        came from a scan that never finished — a FRESH scan must prove the
        target again, the B4 resume action)."""
        store = self.writer.catalog.store
        row = store.fetchone(
            "SELECT source_id FROM sources WHERE content_sha256=?",
            (content_sha256,),
        )
        if row is None:
            return False
        document_row = store.fetchone(
            "SELECT 1 FROM documents WHERE primary_source_id=? AND source_status='active'",
            (row["source_id"],),
        )
        location_row = store.fetchone(
            "SELECT 1 FROM locations l JOIN roots r ON r.root_id=l.root_id "
            "WHERE l.source_id=? AND l.location_status='active' "
            "AND l.role='original_primary' AND r.kind='company_raw'",
            (row["source_id"],),
        )
        if document_row is None or location_row is None:
            return False
        latest_run = store.fetchone(
            "SELECT status FROM scan_runs ORDER BY started_at DESC LIMIT 1"
        )
        return bool(latest_run is not None and latest_run["status"] == "completed")

    def ensure(
        self,
        request: SourceRequest,
        *,
        recovery: SourceRecoveryInput | None = None,
    ) -> SourceEnsureResult:
        if not isinstance(request, SourceRequest):
            raise TypeError("request must be SourceRequest")
        # I-02-E: a durable stage plan binds this exact recovery key — the
        # coordinator (and any network/adapter fetch) is NOT run again.
        resume_plan = self._resume_plan(request)
        if resume_plan is not None and resume_plan.get("kind") == "import_staged":
            candidate = DownloadCandidate(**resume_plan["candidate"])
            receipt_dict = dict(resume_plan["receipt"])
            if resume_plan.get("raw_saved") and resume_plan.get("raw_path"):
                receipt_dict["staged_path"] = resume_plan["raw_path"]
            try:
                receipt = DownloadReceipt(**receipt_dict)
                imported = self.writer.import_staged(
                    request,
                    candidate,
                    receipt,
                    resume=resume_plan,
                )
            except Exception as exc:
                self.journal.record(
                    outcome="failed",
                    request_id=request.request_id,
                    provider=request.provider,
                    provider_document_id=request.provider_document_id,
                    reason="canonical_resume_failed",
                    error_type=type(exc).__name__,
                    error=str(exc),
                )
                raise
            if imported.status is not CanonicalImportStatus.IMPORTED_NEW:
                raise RuntimeError(
                    "resume returned a non-import status; only Imported is expected"
                )
            attempt = self.journal.record(
                outcome="downloaded_new",
                request_id=request.request_id,
                provider=request.provider,
                provider_document_id=request.provider_document_id,
                content_sha256=imported.content_sha256,
                canonical_path=imported.canonical_path,
                reason="w02e_resume_completed_missing_stages",
            )
            return SourceEnsureResult(
                schema_version=SOURCE_ENSURE_SCHEMA_VERSION,
                status=SourceEnsureStatus.IMPORTED,
                # acquisition stays honestly None on resume: the coordinator
                # never ran (no download event happened to fabricate).
                acquisition=None,
                resolution=imported.resolution,
                attempt=attempt,
                canonical_import=imported,
            )
        try:
            acquisition = self.coordinator.resolve_or_stage(request)
        except Exception as exc:
            self.journal.record(
                request_id=request.request_id,
                outcome="failed",
                reason="adapter_or_staging_failed",
                error_type=type(exc).__name__,
                error=str(exc),
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
        if recovery is not None and acquisition.status is AcquisitionStatus.MISSING:
            # I-02-C register-existing recovery: the catalog has no reusable
            # source and NO download is attempted.  The already-on-disk raw
            # is registered through the sole writer, which re-verifies the
            # durable sidecar receipt against the actual bytes.
            try:
                imported = self.writer.register_existing_raw(
                    request,
                    raw_path=Path(recovery.raw_path),
                    sidecar_path=Path(recovery.sidecar_path),
                )
            except Exception as exc:
                self.journal.record(
                    request_id=request.request_id,
                    provider=request.provider,
                    provider_document_id=request.provider_document_id,
                    outcome="failed",
                    reason="existing_raw_register_failed",
                    error_type=type(exc).__name__,
                    error=str(exc),
                )
                raise
            attempt = self.journal.record(
                request_id=request.request_id,
                provider=request.provider,
                provider_document_id=request.provider_document_id,
                content_sha256=imported.content_sha256,
                canonical_path=imported.canonical_path,
                outcome="registered_existing_raw",
                reason="existing_raw_recovery_no_download",
            )
            return SourceEnsureResult(
                schema_version=SOURCE_ENSURE_SCHEMA_VERSION,
                status=SourceEnsureStatus.REGISTERED_EXISTING,
                # acquisition stays honestly None: no discovery happened;
                # fabricating an AcquisitionResult would fake an event that
                # never occurred.
                acquisition=None,
                resolution=imported.resolution,
                attempt=attempt,
                canonical_import=imported,
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
            self.journal.record(
                outcome="failed",
                content_sha256=acquisition.receipt.content_sha256,
                reason="canonical_import_failed",
                error_type=type(exc).__name__,
                error=str(exc),
                **{key: value for key, value in common.items() if key != "reason"},
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
