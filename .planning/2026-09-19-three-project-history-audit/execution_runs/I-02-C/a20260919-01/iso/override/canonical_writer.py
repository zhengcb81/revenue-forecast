"""Recoverable writer from validated staging into company-owned immutable raw."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import unicodedata
from typing import Any

from company_wiki.source_contract import source_id_for_sha256

from .acquisition import DownloadCandidate, DownloadReceipt
from .lock import CatalogOperationLock
from .policy import _effective_reusable
from .resolver import ResolutionResult, ResolutionStatus, SourceRequest, SourceResolver
from .scanner import scan_catalog, v2_scan_shadow_from_snapshot
from .service import SourceCatalog
from .store import canonical_json


CANONICAL_IMPORT_SCHEMA_VERSION = "1.0"
# I-02-C (D-W02 supplement): recovery-source marker carried on
# register_existing_raw results so callers can tell an on-disk
# registration from a download import without re-parsing errors.
EXISTING_RAW_RECOVERY_SOURCE = "existing_raw"
_INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_SAFE_EXTENSION = re.compile(r"^\.[a-z0-9]{1,10}$")
_RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


class CanonicalImportError(RuntimeError):
    """Raised when staged bytes cannot be safely committed as canonical raw."""


class CanonicalImportStatus(str, Enum):
    IMPORTED_NEW = "imported_new"
    DEDUPLICATED_AFTER_DOWNLOAD = "deduplicated_after_download"
    # I-02-C: bytes recovered from an already-on-disk canonical raw with a
    # verified durable sidecar receipt (no download was performed).
    REGISTERED_EXISTING_RAW = "registered_existing_raw"


@dataclass(frozen=True)
class CanonicalImportResult:
    schema_version: str
    status: CanonicalImportStatus
    request_id: str
    source_id: str
    content_sha256: str
    canonical_path: str
    provenance_path: str | None
    resolution: ResolutionResult
    recovery_source: str | None = None  # I-02-C: "existing_raw" on recovery

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status.value,
            "request_id": self.request_id,
            "source_id": self.source_id,
            "content_sha256": self.content_sha256,
            "canonical_path": self.canonical_path,
            "provenance_path": self.provenance_path,
            "recovery_source": self.recovery_source,
            "resolution": self.resolution.to_dict(),
        }


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_component(value: str, *, limit: int) -> str:
    normalized = unicodedata.normalize("NFC", value).strip()
    normalized = _INVALID_WINDOWS_CHARS.sub("_", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip(" .")
    if not normalized:
        normalized = "document"
    if normalized.upper() in _RESERVED_WINDOWS_NAMES:
        normalized = "_" + normalized
    return normalized[:limit].rstrip(" .") or "document"


def _destination_subdirectory(document_kind: str) -> Path:
    mapping = {
        "annual_report": Path("financial_reports") / "annual",
        "semi_annual_report": Path("financial_reports") / "semi_annual",
        "quarterly_report": Path("financial_reports") / "quarterly",
        "prospectus": Path("prospectus"),
        "broker_research": Path("research"),
        "research": Path("research"),
        "investor_relations": Path("investor_relations"),
        "news": Path("news"),
    }
    return mapping.get(document_kind, Path("other"))


def _extension(receipt: DownloadReceipt) -> str:
    suffix = Path(receipt.staged_path).suffix.lower()
    if _SAFE_EXTENSION.fullmatch(suffix):
        return suffix
    by_mime = {
        "application/pdf": ".pdf",
        "text/html": ".html",
        "text/plain": ".txt",
        "application/json": ".json",
    }
    return by_mime.get(receipt.mime_type, ".bin")


class CanonicalSourceWriter:
    """Own canonical paths, immutable provenance, hash reuse, and catalog registration."""

    def __init__(self, catalog: SourceCatalog, *, staging_root: Path | None = None):
        if not isinstance(catalog, SourceCatalog):
            raise TypeError("catalog must be SourceCatalog")
        if staging_root is not None and not isinstance(staging_root, Path):
            raise TypeError("staging_root must be pathlib.Path or null")
        company_roots = tuple(
            root for root in catalog.config.roots if root.kind == "company_raw"
        )
        if len(company_roots) != 1:
            raise CanonicalImportError("exactly one company_raw root is required")
        self.catalog = catalog
        self.company_root = company_roots[0]
        self.staging_root = (
            staging_root or catalog.config.catalog_dir / "staging"
        ).resolve(strict=False)

    def import_staged(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
    ) -> CanonicalImportResult:
        if not isinstance(request, SourceRequest):
            raise TypeError("request must be SourceRequest")
        if not isinstance(candidate, DownloadCandidate):
            raise TypeError("candidate must be DownloadCandidate")
        if not isinstance(receipt, DownloadReceipt):
            raise TypeError("receipt must be DownloadReceipt")
        staged = self._validate_staged(request, candidate, receipt)
        with CatalogOperationLock(
            self.catalog.config.catalog_dir,
            operation="canonical_import",
        ):
            self._reactivate_if_retired(receipt.content_sha256)
            existing = self._existing_original(receipt.content_sha256)
            if existing is not None:
                self._remove_staged(staged)
                resolution = SourceResolver(self.catalog).resolve(request)
                return CanonicalImportResult(
                    schema_version=CANONICAL_IMPORT_SCHEMA_VERSION,
                    status=CanonicalImportStatus.DEDUPLICATED_AFTER_DOWNLOAD,
                    request_id=request.request_id,
                    source_id=source_id_for_sha256(receipt.content_sha256),
                    content_sha256=receipt.content_sha256,
                    canonical_path=str(existing),
                    provenance_path=None,
                    resolution=resolution,
                )

            destination = self._destination(request, candidate, receipt)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                if _hash_file(destination) != receipt.content_sha256:
                    destination = destination.with_name(
                        destination.stem
                        + "__"
                        + receipt.content_sha256[:12]
                        + destination.suffix
                    )
                if (
                    destination.exists()
                    and _hash_file(destination) != receipt.content_sha256
                ):
                    raise CanonicalImportError(
                        "canonical filename collision after hash suffix"
                    )
            if not destination.exists():
                self._atomic_copy(staged, destination, receipt)
            provenance = destination.with_name(destination.name + ".source.json")
            self._write_provenance(provenance, request, candidate, receipt)
            try:
                report = scan_catalog(
                    self.catalog.config,
                    self.catalog.store,
                    dry_run=False,
                    root_ids={self.company_root.root_id},
                    v2_scan_shadow=v2_scan_shadow_from_snapshot(
                        self.catalog.config.catalog_dir
                    ),
                    # I-02-A: the rescan must return a RECEIPT for this import's
                    # own bytes — completion state, per-root state, and whether
                    # the target was registered BY THIS RUN.  The result is never
                    # discarded again.
                    target_content_sha256s=(receipt.content_sha256,),
                )
            except Exception as exc:
                # D-W02 gate 0: a scan that cannot finish does not give this
                # import a green light; the durable scan_runs row stays
                # ``interrupted`` and the raw + sidecar bytes are kept.
                raise CanonicalImportError(
                    f"post-import scan failed (scan did not complete): "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            # D-W02 gate 1: the scan must report completion.  ``errors =>
            # completed_with_errors`` is already a failure here too (fail
            # closed on any root-level degradation, no partial-success
            # green); ``failed``/``interrupted`` can never appear on a
            # normally-returned report but are rejected identically if a
            # future code path ever produced them.
            completion_status = report.completion_status
            if completion_status != "completed":
                raise CanonicalImportError(
                    "post-import scan failed: completion_status="
                    f"{completion_status!r} for run {report.run_id}"
                )
            # D-W02 gate 2: every root that ran inside this scan must be
            # completed; a failed/degraded root blocks the import even when
            # other rows committed (the committed rows are kept, never
            # cleaned up here to re-earn green).
            degraded = [
                result
                for result in report.per_root_results
                if result.get("status") != "completed"
            ]
            if degraded:
                raise CanonicalImportError(
                    "post-import scan failed: roots not completed "
                    + repr(
                        [
                            (
                                root_result["root_id"],
                                root_result["status"],
                                root_result.get("error_class"),
                            )
                            for root_result in degraded
                        ]
                    )
                )
            # D-W02 gate 3: the target bytes must be registered BY THIS
            # scan run — a healthy file count never stands in for the
            # target's own registration (target_not_registered).
            target_entry = next(
                (
                    item
                    for item in report.target_files
                    if item.get("content_sha256") == receipt.content_sha256
                ),
                None,
            )
            if target_entry is None or not target_entry.get("registered"):
                raise CanonicalImportError(
                    "post-import scan completed but the target file was not "
                    "registered (target_not_registered); report run "
                    f"{report.run_id}"
                )
            # D-W02 gate 4: consume the exact resolve with an IDENTITY
            # check — the resolver must report the target's own bytes at the
            # writer's own canonical path before any success/confident
            # handle leaves this import (no proxy match acceptance).
            exact_request = SourceRequest(
                entity=request.entity,
                market=request.market,
                security_id=request.security_id,
                document_kind=request.document_kind,
                form_type=request.form_type or candidate.form_type,
                fiscal_year=request.fiscal_year or candidate.fiscal_year,
                fiscal_period=request.fiscal_period or candidate.fiscal_period,
                language=request.language or candidate.language,
                provider=candidate.provider,
                provider_document_id=candidate.provider_document_id,
                as_of_date=request.as_of_date,
                allow_download=request.allow_download,
            )
            resolution = SourceResolver(self.catalog).resolve(exact_request)
            if resolution.status is not ResolutionStatus.REUSED_EXACT:
                raise CanonicalImportError(
                    "canonical file was written but exact provider identity did not resolve"
                )
            match = resolution.matches[0] if resolution.matches else None
            if (
                match is None
                or getattr(match, "content_sha256", None) != receipt.content_sha256
                or Path(match.canonical_path) != destination.resolve()
            ):
                raise CanonicalImportError(
                    "exact resolve returned a different identity than the "
                    "imported target (exact_resolve_identity_mismatch)"
                )
            self._remove_staged(staged)
            return CanonicalImportResult(
                schema_version=CANONICAL_IMPORT_SCHEMA_VERSION,
                status=CanonicalImportStatus.IMPORTED_NEW,
                request_id=request.request_id,
                source_id=source_id_for_sha256(receipt.content_sha256),
                content_sha256=receipt.content_sha256,
                canonical_path=str(destination.resolve()),
                provenance_path=str(provenance.resolve()),
                resolution=resolution,
            )

    def register_existing_raw(
        self,
        request: SourceRequest,
        *,
        raw_path: Path,
        sidecar_path: Path,
    ) -> CanonicalImportResult:
        """I-02-C (D-W02 supplement): register an already-on-disk canonical
        raw that owns its immutable provenance sidecar.

        Recovery consumes ONLY proven persistence stages: the durable
        download receipt embedded in the sidecar (written by
        ``_write_provenance`` at capture time) plus a fresh re-hash of the
        actual bytes.  Nothing is downloaded, no receipt is fabricated, no
        identity is inferred from filenames, and retired/quarantined
        documents are never reactivated on this path (N2).  The sidecar
        bytes are never rewritten; the historical ``receipt.staged_path``
        stays as provenance even when the historical staging directory no
        longer exists."""
        if not isinstance(request, SourceRequest):
            raise TypeError("request must be SourceRequest")
        with CatalogOperationLock(
            self.catalog.config.catalog_dir,
            operation="canonical_import",
        ):
            return self._register_existing_locked(
                request,
                raw_path=raw_path,
                sidecar_path=sidecar_path,
            )

    def _register_existing_locked(
        self,
        request: SourceRequest,
        *,
        raw_path: Path,
        sidecar_path: Path,
    ) -> CanonicalImportResult:
        # Gate R1 (root policy, fail-early): a root that is not reusable
        # for filing can never be the recovery target — register may not
        # grant reusability that the root policy withholds (N2b).
        if not _effective_reusable(self.company_root, self.catalog.config):
            raise CanonicalImportError(
                "existing_raw_root_not_reusable: the target company_raw root "
                "is not reusable for filing; registering cannot lift the "
                "root-level reuse ban"
            )
        # Gate R2 (target-root binding + raw presence): the recovery bytes
        # must live inside the bound company_raw root — no out-of-tree raw
        # and no path-derived identity substitution.
        try:
            raw_abs = Path(raw_path).resolve(strict=True)
        except FileNotFoundError as exc:
            raise CanonicalImportError(
                "existing_raw_bytes_mismatch: raw_path does not exist; "
                "recovery requires the already-on-disk raw"
            ) from exc
        try:
            raw_abs.relative_to(self.company_root.path.resolve(strict=True))
        except ValueError as exc:
            raise CanonicalImportError(
                "existing_raw_identity_contract: raw_path is outside the "
                "bound company_raw root; the recovery target root is part "
                "of the recovery key"
            ) from exc
        if not raw_abs.is_file():
            raise CanonicalImportError(
                "existing_raw_bytes_mismatch: raw_path is not a regular file"
            )
        # Gate R3 (sidecar adjacency, N1a): the provenance sidecar must be
        # THE raw file's adjacent immutable sidecar — a sidecar from
        # elsewhere cannot certify these bytes.
        adjacent = raw_abs.with_name(raw_abs.name + ".source.json")
        try:
            sidecar_abs = Path(sidecar_path).resolve(strict=True)
        except FileNotFoundError as exc:
            raise CanonicalImportError(
                "existing_raw_missing_sidecar: the immutable provenance "
                "sidecar (<raw>.source.json beside the raw file) is absent; "
                "without it there is no durable receipt chain"
            ) from exc
        if sidecar_abs != adjacent.resolve(strict=False):
            raise CanonicalImportError(
                "existing_raw_missing_sidecar: sidecar_path is not the "
                "raw file's adjacent provenance (<raw>.source.json)"
            )
        try:
            payload = json.loads(sidecar_abs.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CanonicalImportError(
                f"existing_raw_provenance_incomplete: sidecar is unreadable "
                f"({type(exc).__name__}: {exc})"
            ) from exc
        if not isinstance(payload, dict):
            raise CanonicalImportError(
                "existing_raw_provenance_incomplete: sidecar payload is not "
                "a JSON object"
            )
        # Gate R4 (provenance completeness, N1d): every identity field and
        # the durable download receipt must be present.  Absent fields are
        # NEVER auto-filled — least of all from the filename.
        required_identity = {
            "content_sha256",
            "byte_size",
            "company_name",
            "provider",
            "provider_document_id",
            "source_url",
            "document_kind",
            "filing_date",
            "fiscal_year",
            "market",
            "security_id",
            "mime_type",
        }
        present_empty = sorted(
            key
            for key in required_identity
            if key not in payload or payload[key] in (None, "")
        )
        absent_sections = [
            key
            for key in ("candidate", "request", "receipt")
            if not isinstance(payload.get(key), dict)
        ]
        if present_empty or absent_sections:
            raise CanonicalImportError(
                "existing_raw_provenance_incomplete: sidecar lacks durable "
                f"receipt/identity fields {absent_sections + present_empty!r}; "
                "auto-filling (including from the filename) is forbidden"
            )
        required_receipt = {
            "content_sha256",
            "byte_size",
            "provider",
            "provider_document_id",
            "candidate_id",
            "source_url",
            "http_status",
            "retrieved_at",
            "mime_type",
        }
        receipt_payload = payload["receipt"]
        missing_receipt = sorted(
            key
            for key in required_receipt
            if key not in receipt_payload or receipt_payload[key] in (None, "")
        )
        if missing_receipt:
            raise CanonicalImportError(
                "existing_raw_provenance_incomplete: sidecar receipt lacks "
                f"{missing_receipt!r}; no reliable download receipt -> "
                "recovery refused"
            )
        content_sha256 = str(payload["content_sha256"])
        byte_size = int(payload["byte_size"])
        # Gate R5 (bytes identity vs the durable receipt, N1b / fake
        # receipt): rebuild candidate+receipt ONLY from sidecar fields,
        # then verify against the CURRENT bytes; a single flipped byte or
        # any hash/size drift is rejected.
        try:
            candidate = DownloadCandidate(**payload["candidate"])
            receipt = DownloadReceipt(
                **{**receipt_payload, "staged_path": str(raw_abs)}
            )
        except (TypeError, ValueError) as exc:
            raise CanonicalImportError(
                "existing_raw_provenance_incomplete: sidecar receipt/loose "
                f"identity fields do not satisfy the acquisition contract "
                f"({type(exc).__name__}: {exc})"
            ) from exc
        if (
            candidate.candidate_id != receipt.candidate_id
            or candidate.provider != receipt.provider
            or candidate.provider_document_id != receipt.provider_document_id
            or candidate.source_url != receipt.source_url
            or payload["provider"] != receipt.provider
            or payload["provider_document_id"] != receipt.provider_document_id
            or int(payload["byte_size"]) != receipt.byte_size
        ):
            raise CanonicalImportError(
                "existing_raw_provenance_incomplete: sidecar top-level "
                "identity does not agree with the embedded durable "
                "receipt/candidate"
            )
        if (
            raw_abs.stat().st_size != receipt.byte_size
            or _hash_file(raw_abs) != receipt.content_sha256
        ):
            raise CanonicalImportError(
                f"existing_raw_bytes_mismatch: content_sha256 is "
                f"{receipt.content_sha256} but the on-disk bytes hash/size "
                f"differ (raw_path={raw_abs})"
            )
        # Gate R6 (identity contract, N1c): the caller must have supplied
        # the source identity EXPLICITLY; it must match the durable
        # sidecar identity.  No auto-fill from the filename, ever.
        for text, kind in (
            (request.provider, "provider"),
            (request.provider_document_id, "provider_document_id"),
        ):
            if not text:
                raise CanonicalImportError(
                    "existing_raw_identity_contract: request.provider / "
                    "request.provider_document_id must be supplied "
                    "explicitly for register-existing; inferring provider/"
                    "fiscal_year from the filename is forbidden"
                )
        if (
            request.provider != receipt.provider
            or request.provider_document_id != receipt.provider_document_id
            or request.entity != payload["company_name"]
            or request.document_kind != payload["document_kind"]
            or (
                request.fiscal_year is not None
                and request.fiscal_year != payload["fiscal_year"]
            )
            or (request.market is not None and request.market != payload.get("market"))
        ):
            raise CanonicalImportError(
                "existing_raw_identity_contract: the caller-supplied request "
                "identity does not match the sidecar's durable provider/"
                "entity/kind/year bindings"
            )
        # Gate R7 (retired/quarantined, N2): identical bytes whose document
        # is retired or quarantined must NOT be reactivated by recovery —
        # never via _reactivate_if_retired, never restored to active, and
        # never handed back as a qualified handle.  A user-approved
        # re-acquisition or the documents restore CLI are the only revival
        # paths; both are outside this entry point.
        document_id = source_id_for_sha256(content_sha256).replace(
            "urn:company-wiki:source:", "urn:company-wiki:document:"
        )
        state = self.catalog.store.fetchone(
            "SELECT source_status FROM documents WHERE document_id=?",
            (document_id,),
        )
        if state is not None and state["source_status"] in (
            "retired",
            "quarantined",
        ):
            raise CanonicalImportError(
                "existing_raw_status_not_active: identical bytes are "
                f"{state['source_status']}; register-existing may not "
                "reactivate them and returns no qualified handle"
            )
        existing = self._existing_original(content_sha256)
        if existing is not None:
            # Idempotent re-entry: the same bytes are already registered.
            # No new rows, no rewritten sidecar; just resolve and return
            # the same identity.
            resolution = self._exact_resolve(request, receipt, raw_abs)
            return CanonicalImportResult(
                schema_version=CANONICAL_IMPORT_SCHEMA_VERSION,
                status=CanonicalImportStatus.REGISTERED_EXISTING_RAW,
                request_id=request.request_id,
                source_id=source_id_for_sha256(content_sha256),
                content_sha256=content_sha256,
                canonical_path=str(existing),
                provenance_path=None,
                resolution=resolution,
            )
        # Registration stage: the raw + sidecar are already canonical — the
        # only missing stage is the catalog registration.  The scan must
        # prove completion and register THESE bytes itself (gates 0-3,
        # identical to import_staged).
        try:
            report = scan_catalog(
                self.catalog.config,
                self.catalog.store,
                dry_run=False,
                root_ids={self.company_root.root_id},
                v2_scan_shadow=v2_scan_shadow_from_snapshot(
                    self.catalog.config.catalog_dir
                ),
                target_content_sha256s=(content_sha256,),
            )
        except Exception as exc:
            raise CanonicalImportError(
                f"post-import scan failed (scan did not complete): "
                f"{type(exc).__name__}: {exc}"
            ) from exc
        completion_status = report.completion_status
        if completion_status != "completed":
            raise CanonicalImportError(
                "post-import scan failed: completion_status="
                f"{completion_status!r} for run {report.run_id}"
            )
        degraded = [
            result
            for result in report.per_root_results
            if result.get("status") != "completed"
        ]
        if degraded:
            raise CanonicalImportError(
                "post-import scan failed: roots not completed "
                + repr(
                    [
                        (
                            root_result["root_id"],
                            root_result["status"],
                            root_result.get("error_class"),
                        )
                        for root_result in degraded
                    ]
                )
            )
        target_entry = next(
            (
                item
                for item in report.target_files
                if item.get("content_sha256") == content_sha256
            ),
            None,
        )
        if target_entry is None or not target_entry.get("registered"):
            raise CanonicalImportError(
                "post-import scan completed but the target file was not "
                "registered (target_not_registered); report run "
                f"{report.run_id}"
            )
        resolution = self._exact_resolve(request, receipt, raw_abs)
        return CanonicalImportResult(
            schema_version=CANONICAL_IMPORT_SCHEMA_VERSION,
            status=CanonicalImportStatus.REGISTERED_EXISTING_RAW,
            request_id=request.request_id,
            source_id=source_id_for_sha256(content_sha256),
            content_sha256=content_sha256,
            canonical_path=str(raw_abs),
            provenance_path=str(sidecar_abs),
            resolution=resolution,
            recovery_source=EXISTING_RAW_RECOVERY_SOURCE,
        )

    def _exact_resolve(
        self,
        request: SourceRequest,
        receipt: DownloadReceipt,
        raw_abs: Path,
    ) -> ResolutionResult:
        exact_request = SourceRequest(
            entity=request.entity,
            market=request.market,
            security_id=request.security_id,
            document_kind=request.document_kind,
            form_type=request.form_type,
            fiscal_year=request.fiscal_year,
            fiscal_period=request.fiscal_period,
            language=request.language,
            provider=receipt.provider,
            provider_document_id=receipt.provider_document_id,
            as_of_date=request.as_of_date,
            allow_download=request.allow_download,
        )
        resolution = SourceResolver(self.catalog).resolve(exact_request)
        if resolution.status is not ResolutionStatus.REUSED_EXACT:
            raise CanonicalImportError(
                "canonical file was written but exact provider identity did not resolve"
            )
        match = resolution.matches[0] if resolution.matches else None
        if (
            match is None
            or getattr(match, "content_sha256", None) != receipt.content_sha256
            or Path(match.canonical_path) != raw_abs.resolve()
        ):
            raise CanonicalImportError(
                "exact resolve returned a different identity than the "
                "registered target (exact_resolve_identity_mismatch)"
            )
        return resolution

    def _validate_staged(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
    ) -> Path:
        if candidate.entity != request.entity:
            raise CanonicalImportError("candidate entity does not match request")
        if candidate.candidate_id != receipt.candidate_id:
            raise CanonicalImportError("receipt candidate_id does not match candidate")
        if candidate.provider != receipt.provider:
            raise CanonicalImportError("receipt provider does not match candidate")
        if candidate.provider_document_id != receipt.provider_document_id:
            raise CanonicalImportError(
                "receipt provider identity does not match candidate"
            )
        if candidate.source_url != receipt.source_url:
            raise CanonicalImportError("receipt source URL does not match candidate")
        staged = Path(receipt.staged_path).resolve(strict=True)
        staging_root = self.staging_root.resolve(strict=True)
        try:
            staged.relative_to(staging_root)
        except ValueError as exc:
            raise CanonicalImportError(
                "staged file is outside configured staging root"
            ) from exc
        if not staged.is_file():
            raise CanonicalImportError("staged path is not a regular file")
        if staged.stat().st_size != receipt.byte_size:
            raise CanonicalImportError("staged byte_size does not match receipt")
        if _hash_file(staged) != receipt.content_sha256:
            raise CanonicalImportError("staged SHA-256 does not match receipt")
        return staged

    def _reactivate_if_retired(self, content_sha256: str) -> None:
        """Phase 15.6: a user-authorized re-download of bytes whose
        content-addressed document was retired must bring that document back
        to active (identical document_id, both the import and the dedup
        paths).  Plain rescans never revive retired documents — this is the
        explicit re-acquisition path only."""
        document_id = source_id_for_sha256(content_sha256).replace(
            "urn:company-wiki:source:", "urn:company-wiki:document:"
        )
        with self.catalog.store.transaction() as connection:
            connection.execute(
                "UPDATE documents SET source_status='active' "
                "WHERE document_id=? AND source_status='retired'",
                (document_id,),
            )
            connection.execute(
                "UPDATE locations SET location_status='active' "
                "WHERE document_id=? AND location_status='retired'",
                (document_id,),
            )

    def _existing_original(self, content_sha256: str) -> Path | None:
        # Only canonical company_raw locations are dedup targets: dayu
        # portfolio ingestion lives outside the companies/ subtree and its
        # paths are rejected by the filing-fetch handle contract (MongoDB
        # finding).
        rows = self.catalog.store.fetchall(
            """SELECT l.absolute_path FROM sources s
            JOIN locations l ON l.source_id=s.source_id
            JOIN roots r ON r.root_id=l.root_id
            WHERE s.content_sha256=? AND l.role='original_primary'
            AND l.location_status='active' AND r.kind='company_raw'
            ORDER BY r.priority,l.root_id,l.relative_path""",
            (content_sha256,),
        )
        for row in rows:
            path = Path(row["absolute_path"])
            if path.is_file() and _hash_file(path) == content_sha256:
                return path.resolve()
        return None

    def _destination(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
    ) -> Path:
        company = _safe_component(request.entity, limit=80)
        filename = "_".join(
            (
                candidate.filing_date,
                _safe_component(candidate.provider, limit=24),
                _safe_component(candidate.provider_document_id, limit=64),
                _safe_component(candidate.title, limit=90),
            )
        ) + _extension(receipt)
        return (
            self.company_root.path
            / company
            / "raw"
            / _destination_subdirectory(candidate.document_kind)
            / filename
        ).resolve(strict=False)

    @staticmethod
    def _atomic_copy(
        staged: Path,
        destination: Path,
        receipt: DownloadReceipt,
    ) -> None:
        temporary = destination.with_name(
            destination.name + f".{os.getpid()}.importing"
        )
        try:
            shutil.copyfile(staged, temporary)
            if temporary.stat().st_size != receipt.byte_size:
                raise CanonicalImportError("temporary canonical copy has wrong size")
            if _hash_file(temporary) != receipt.content_sha256:
                raise CanonicalImportError("temporary canonical copy has wrong SHA-256")
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()

    @staticmethod
    def _write_provenance(
        path: Path,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
    ) -> None:
        payload = {
            "schema_version": CANONICAL_IMPORT_SCHEMA_VERSION,
            "request_id": request.request_id,
            "company_name": request.entity,
            # Top-level identity field: the resolver and the scanner's
            # prefer-new metadata merge both read market at top level, while
            # security_id already sits here (portfolio-promotion spike).
            "market": request.market,
            "security_id": request.security_id,
            "source_title": candidate.title,
            "provider": candidate.provider,
            "provider_document_id": candidate.provider_document_id,
            "source_url": candidate.source_url,
            "document_kind": candidate.document_kind,
            "form_type": candidate.form_type,
            "filing_date": candidate.filing_date,
            "fiscal_year": candidate.fiscal_year,
            "fiscal_period": candidate.fiscal_period,
            "language": candidate.language,
            "amended": candidate.amended,
            "content_sha256": receipt.content_sha256,
            "byte_size": receipt.byte_size,
            "mime_type": receipt.mime_type,
            "retrieved_at": receipt.retrieved_at,
            "adapter_name": receipt.adapter_name,
            "adapter_version": receipt.adapter_version,
            "etag": receipt.etag,
            "last_modified": receipt.last_modified,
            "request": request.to_dict(),
            "candidate": candidate.to_dict(),
            "receipt": receipt.to_dict(),
        }
        encoded = (canonical_json(payload) + "\n").encode("utf-8")
        if path.exists():
            if path.read_bytes() != encoded:
                raise CanonicalImportError("immutable provenance sidecar conflict")
            return
        temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
        try:
            temporary.write_bytes(encoded)
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()

    def _remove_staged(self, staged: Path) -> None:
        try:
            staged.resolve(strict=True).relative_to(
                self.staging_root.resolve(strict=True)
            )
        except (FileNotFoundError, ValueError) as exc:
            raise CanonicalImportError(
                "refusing to remove file outside staging"
            ) from exc
        staged.unlink()


__all__ = [
    "CANONICAL_IMPORT_SCHEMA_VERSION",
    "CanonicalImportError",
    "CanonicalImportResult",
    "CanonicalImportStatus",
    "CanonicalSourceWriter",
]
