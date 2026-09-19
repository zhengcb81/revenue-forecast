    def import_staged(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
        *,
        resume: dict[str, Any] | None = None,
    ) -> CanonicalImportResult:
        if not isinstance(request, SourceRequest):
            raise TypeError("request must be SourceRequest")
        if not isinstance(candidate, DownloadCandidate):
            raise TypeError("candidate must be DownloadCandidate")
        if not isinstance(receipt, DownloadReceipt):
            raise TypeError("receipt must be DownloadReceipt")
        with CatalogOperationLock(
            self.catalog.config.catalog_dir,
            operation="canonical_import",
        ):
            if resume is not None:
                return self._import_staged_resumed(request, candidate, receipt, resume)
            return self._import_staged_fresh(request, candidate, receipt)

    def _import_staged_fresh(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
    ) -> CanonicalImportResult:
        staged = self._validate_staged(request, candidate, receipt)
        # I-02-E S1 (B1): the durable sidecar bytes are committed (fsync)
        # BEFORE the raw rename, so a crash after this row can rebuild the
        # sidecar WITHOUT guessing any field (capture time rides the
        # durable receipt).
        sidecar_bytes = self._sidecar_bytes(request, candidate, receipt)
        sidecar_b64 = base64.b64encode(sidecar_bytes).decode("ascii")
        self._stage(
            "stage_staged_verified",
            {
                "staged_path": str(staged.resolve()),
                "byte_size": receipt.byte_size,
                "sidecar_bytes_b64": sidecar_b64,
            },
            request=request,
            candidate=candidate,
            receipt=receipt,
        )
        _w02e_inject(
            "staged_verified",
            {"staged_path": str(staged), "content_sha256": receipt.content_sha256},
        )
        self._reactivate_if_retired(receipt.content_sha256)
        existing = self._existing_original(receipt.content_sha256)
        if existing is not None:
            # I-02-D (bytes-for-bytes carried over): dedup success is only
            # reportable after the exact resolve PROVES the DOWNLOAD's own
            # provider identity at the same canonical path.  The staging
            # file is removed only AFTER that proof succeeds.
            exact_request = dedup_exact_request(request, candidate)
            resolution = SourceResolver(self.catalog).resolve(exact_request)
            if resolution.status is not ResolutionStatus.REUSED_EXACT:
                raise CanonicalImportError(
                    "canonical file was written but exact provider identity did not resolve"
                )
            match = resolution.matches[0] if resolution.matches else None
            if (
                match is None
                or getattr(match, "content_sha256", None) != receipt.content_sha256
                or Path(match.canonical_path) != Path(existing).resolve()
            ):
                raise CanonicalImportError(
                    "exact resolve returned a different identity than the "
                    "deduplicated target (exact_resolve_identity_mismatch)"
                )
            self._stage(
                "stage_qualified",
                {
                    "import_status": "deduplicated_after_download",
                    "source_id": source_id_for_sha256(receipt.content_sha256),
                    "canonical_path": str(Path(existing).resolve()),
                },
                request=request,
                candidate=candidate,
                receipt=receipt,
                canonical_path=str(Path(existing).resolve()),
            )
            _w02e_inject(
                "qualified",
                {
                    "import_status": "deduplicated_after_download",
                    "source_id": source_id_for_sha256(receipt.content_sha256),
                    "canonical_path": str(Path(existing).resolve()),
                },
            )
            self._remove_staged(staged)
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
        # I-02-E S2 (B2 window): the canonical raw rename is durable; the
        # row is fsynced BEFORE the sidecar write.  sidecar bytes ride the
        # row so a later missing sidecar is rebuildable without guessing.
        self._stage(
            "stage_raw_saved",
            {
                "canonical_path": str(destination.resolve()),
                "byte_size": receipt.byte_size,
                "sidecar_bytes_b64": sidecar_b64,
            },
            request=request,
            candidate=candidate,
            receipt=receipt,
            canonical_path=str(destination.resolve()),
        )
        _w02e_inject(
            "raw_saved",
            {
                "canonical_path": str(destination),
                "content_sha256": receipt.content_sha256,
            },
        )
        provenance = destination.with_name(destination.name + ".source.json")
        self._write_provenance(provenance, request, candidate, receipt)
        self._stage(
            "stage_provenance_saved",
            {
                "sidecar_path": str(provenance.resolve()),
                "sidecar_sha256": _hash_file(provenance),
                "content_sha256": receipt.content_sha256,
            },
            request=request,
            candidate=candidate,
            receipt=receipt,
            canonical_path=str(destination.resolve()),
        )
        _w02e_inject(
            "provenance_saved",
            {"canonical_path": str(destination), "sidecar_path": str(provenance)},
        )
        return self._scan_gates_and_qualified(
            request,
            candidate,
            receipt,
            destination,
            provenance,
            staged,
            skip_scan=False,
        )

    def _import_staged_resumed(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
        resume: dict[str, Any],
    ) -> CanonicalImportResult:
        """I-02-E: restart consumes ONLY durable stage evidence; the first
        UNfinished stage is run again, completed stages' bytes untouched."""
        payload_b64 = resume.get("sidecar_payload_b64")
        raw_saved = bool(resume.get("raw_saved"))
        staged = None
        canonical_path = None
        if not raw_saved:
            staged = self._validate_staged(request, candidate, receipt)
            self._reactivate_if_retired(receipt.content_sha256)
            existing = self._existing_original(receipt.content_sha256)
            if existing is not None:
                raise CanonicalImportError(
                    "resume planner selected pre-raw stages but a dedup "
                    "target appeared in catalog; planner evidence disagrees"
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
            canonical_path = destination.resolve()
            self._stage(
                "stage_raw_saved",
                {
                    "canonical_path": str(canonical_path),
                    "byte_size": receipt.byte_size,
                    "sidecar_bytes_b64": payload_b64,
                },
                request=request,
                candidate=candidate,
                receipt=receipt,
                canonical_path=str(canonical_path),
            )
            _w02e_inject(
                "raw_saved",
                {"canonical_path": str(canonical_path), "content_sha256": receipt.content_sha256},
            )
        else:
            canonical_path = Path(resume["raw_path"]).resolve(strict=True)
            if (
                not canonical_path.is_file()
                or canonical_path.stat().st_size != receipt.byte_size
                or _hash_file(canonical_path) != receipt.content_sha256
            ):
                # N3a: the raw drifted after the crash.  Never a silent
                # reuse of the old receipt; raw is preserved, not deleted.
                raise CanonicalImportError(
                    f"resume_raw_bytes_mismatch: stage_raw_saved claims "
                    f"{receipt.content_sha256} (size {receipt.byte_size}) but "
                    f"the canonical bytes at {canonical_path} differ now; "
                    "raw preserved, no rewrite, no re-download"
                )
        provenance = canonical_path.with_name(canonical_path.name + ".source.json")
        self._ensure_sidecar_durable(provenance, payload_b64)
        self._stage(
            "stage_provenance_saved",
            {
                "sidecar_path": str(provenance.resolve()),
                "sidecar_sha256": _hash_file(provenance),
                "content_sha256": receipt.content_sha256,
            },
            request=request,
            candidate=candidate,
            receipt=receipt,
            canonical_path=str(canonical_path),
        )
        _w02e_inject(
            "provenance_saved",
            {"canonical_path": str(canonical_path), "sidecar_path": str(provenance)},
        )
        return self._scan_gates_and_qualified(
            request,
            candidate,
            receipt,
            canonical_path,
            provenance,
            staged,
            skip_scan=bool(resume.get("registration_durable")),
        )

    def _ensure_sidecar_durable(
        self, provenance: Path, payload_b64: str | None
    ) -> None:
        if provenance.exists():
            if payload_b64 is None:
                raise CanonicalImportError(
                    "resume_sidecar_state_mismatch: provenance sidecar exists "
                    "but no durable sidecar payload row is recorded; recovery "
                    "keeps raw + sidecar and refuses to guess contents"
                )
            expected = base64.b64decode(payload_b64)
            if provenance.read_bytes() != expected:
                raise CanonicalImportError(
                    f"resume_sidecar_mismatch: sidecar at {provenance} does "
                    "not match the durable S1/S2 payload bytes; immutable "
                    "provenance is never rewritten to different content"
                )
            return
        if payload_b64 is None:
            raise CanonicalImportError(
                "resume_requires_sidecar_payload: sidecar is missing and no "
                "durable sidecar payload row exists; recovery refuses without "
                "a reliable receipt (raw preserved)"
            )
        encoded = base64.b64decode(payload_b64)
        temporary = provenance.with_name(provenance.name + f".{os.getpid()}.w02echk")
        try:
            temporary.write_bytes(encoded)
            provenance.parent.mkdir(parents=True, exist_ok=True)
            os.replace(temporary, provenance)
        finally:
            if temporary.exists():
                temporary.unlink()

    def _scan_gates_and_qualified(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
        destination: Path,
        provenance: Path,
        staged: Path | None,
        *,
        skip_scan: bool,
    ) -> CanonicalImportResult:
        if not skip_scan:
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
                    # the target was registered BY THIS RUN.  It is never
                    # discarded.
                    target_content_sha256s=(receipt.content_sha256,),
                )
            except Exception as exc:
                # D-W02 gate 0
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
            self._stage(
                "stage_scan_registered",
                {
                    "run_id": report.run_id,
                    "content_sha256": receipt.content_sha256,
                },
                request=request,
                candidate=candidate,
                receipt=receipt,
                canonical_path=str(destination.resolve()),
            )
        # D-W02 gate 4: final identity resolve — ALWAYS reruns, including on
        # resume (no old receipt reuse, N3).
        exact_request = dedup_exact_request(request, candidate)
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
        # I-02-E S5: durable BEFORE any cleanup (B5 window).
        self._stage(
            "stage_qualified",
            {
                "import_status": "imported_new",
                "source_id": source_id_for_sha256(receipt.content_sha256),
                "match_source_id": match.source_id,
                "canonical_path": str(destination.resolve()),
            },
            request=request,
            candidate=candidate,
            receipt=receipt,
            canonical_path=str(destination.resolve()),
        )
        _w02e_inject(
            "qualified",
            {
                "import_status": "imported_new",
                "source_id": source_id_for_sha256(receipt.content_sha256),
                "canonical_path": str(destination),
            },
        )
        if staged is not None:
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

    def register_existing_raw_stage_records(
        self,
        request: SourceRequest,
        *,
        sidecar_abs: Path,
        raw_abs: Path,
        content_sha256: str,
        receipt: DownloadReceipt,
        registration_durable: bool = False,
    ) -> None:
        """I-02-E: stage-row maintenance for the register-existing path —
        the sidecar is already durable, so only S3/S4/S5 markers apply and
        each is idempotent by content hash."""
        self._stage(
            "stage_provenance_saved",
            {
                "sidecar_path": str(sidecar_abs),
                "sidecar_sha256": _hash_file(sidecar_abs),
                "content_sha256": content_sha256,
            },
            request=request,
            candidate=DownloadCandidate(
                candidate_id="existing-raw-recovery",
                provider=request.provider or "",
                provider_document_id=request.provider_document_id or "",
                market=request.market or "",
                entity=request.entity,
                title="existing_raw",
                source_url="https://existing-raw.invalid/none",
                document_kind=request.document_kind,
                filing_date="1970-01-01",
                fiscal_year=1900,
            ),
            receipt=DownloadReceipt(
                candidate_id="existing-raw-recovery",
                provider=request.provider or "",
                provider_document_id=request.provider_document_id or "",
                source_url="https://existing-raw.invalid/",
                staged_path=str(raw_abs),
                content_sha256=content_sha256,
                byte_size=raw_abs.stat().st_size,
                mime_type="application/octet-stream",
                retrieved_at="1970-01-01T00:00:00Z",
                http_status=200,
                adapter_name="register_existing_raw",
                adapter_version="1.0.0",
            ),
            canonical_path=str(raw_abs),
        )
        if registration_durable:
            self._stage(
                "stage_scan_registered",
                {"content_sha256": content_sha256, "run_id": "pre-existing-durable"},
                request=request,
                candidate=DownloadCandidate(
                    candidate_id="existing-raw-recovery",
                    provider=request.provider or "",
                    provider_document_id=request.provider_document_id or "",
                    market=request.market or "",
                    entity=request.entity,
                    title="existing_raw",
                    source_url="https://existing-raw.invalid/",
                    document_kind=request.document_kind,
                    filing_date="1970-01-01",
                    fiscal_year=1900,
                ),
                receipt=DownloadReceipt(
                    candidate_id="existing-raw-recovery",
                    provider=request.provider or "",
                    provider_document_id=request.provider_document_id or "",
                    source_url="https://existing-raw.invalid/",
                    staged_path=str(raw_abs),
                    content_sha256=content_sha256,
                    byte_size=raw_abs.stat().st_size,
                    mime_type="application/octet-stream",
                    retrieved_at="1970-01-01T00:00:00Z",
                    http_status=200,
                    adapter_name="register_existing_raw",
                    adapter_version="1.0.0",
                ),
                canonical_path=str(raw_abs),
            )

    def _sidecar_payload_dict(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
    ) -> dict[str, Any]:
        payload = self._provenance_payload(request, candidate, receipt)
        payload["canonical_path_placeholder"] = None
        payload.pop("canonical_path_placeholder", None)
        return payload
