"""Deep-layer runner for I-02-B (L4): exercises the CW override copies.

Runs under the attempt venv, cwd = attempt (A), module loading via
scripts/w02b_bootstrap.py (override copies registered under the exact product
module names; the synthetic package __path__ points at the READ-ONLY real
repo src for everything unmodified).  Injection rules follow the I-02-A
precedent: ALL fake behaviour is constructed HERE by stub objects/attribute
replacement; the override product copies contain no harness code.

Modes (arg --case):
  p1_cw       coordinator raises a provider-declared structured failure right
              after resolution (no download window); provider payload is the
              original CN-403 document shape.
  n3          real staging: seed bytes are actually written into the staging
              tree by the stub coordinator; then the writer stage fails
              (post-download scan failure) — side effects must survive.
  n4a         DB busy: sqlite3.OperationalError("database is locked").
  n4b         identity/contract error (error_code=identity_contract,
              retryable False) — must NOT be retried (ledger asserts).
  exit_probe  runs the REAL modified cli.main() in THIS process after the
              scratch config loads successfully: cli.SourceCatalog is
              attribute-replaced (harness only) with a stub whose __init__
              raises a STRUCTURED probe exception carrying a nested cause
              dict; the real main() except block assembles/emits the envelope
              to stderr with exit 1 (verdict on "the exit does not stringify
              dicts" against the true product exit path).

Failure emission mirrors the override cli.py exit exactly (structured_error +
envelope-attr assembly): cli.main cannot be re-entered with an arbitrary
exception without inventing product argv shapes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from w02b_bootstrap import setup  # noqa: E402

setup()

REQUEST_ID = "execv2-w02b"
SEED_BYTES = bytes(range(256)) * 5  # 1280 deterministic bytes
SEED_SHA = hashlib.sha256(SEED_BYTES).hexdigest()
ENTITY = "测试实体星际矿业"
CN403_MESSAGE = (
    "cninfo_api_discover failed: client_error: API client error (HTTP 403): Forbidden"
)


class _StubError(RuntimeError):
    """Harness-only structured failure carrier."""

    error_code: str | None = None
    retryable: bool | None = None
    provider_payload: dict | None = None
    stage: str | None = None
    request_id: str | None = None
    cause_chain: list | None = None
    side_effects: dict | None = None
    local_diag_ref: str | None = None


def _build_request():
    from company_wiki.source_catalog.resolver import SourceRequest

    return SourceRequest(
        entity=ENTITY,
        market="CN",
        document_kind="annual_report",
        fiscal_year=2025,
        fiscal_period="FY",
        as_of_date="2026-04-28",
        allow_download=True,
    )


def _stub_result():
    """A real (frozen-schema) STAGED AcquisitionResult assembled from the
    deterministic seed — candidate+receipt bound to the seed file."""
    from company_wiki.source_catalog.acquisition import (
        ACQUISITION_SCHEMA_VERSION,
        AcquisitionResult,
        AcquisitionStatus,
        DownloadCandidate,
        DownloadReceipt,
    )
    from company_wiki.source_catalog.resolver import (
        ResolutionResult,
        ResolutionStatus,
    )

    candidate = DownloadCandidate(
        candidate_id="cand-w02b",
        provider="fake",
        provider_document_id="doc-w02b",
        market="CN",
        entity=ENTITY,
        title="2025年度报告",
        source_url="https://example.invalid/seed.pdf",
        document_kind="annual_report",
        filing_date="2026-04-28",
        fiscal_year=2025,
    )
    staged_path = Path(sys.argv[sys.argv.index("--staged") + 1])
    receipt = DownloadReceipt(
        candidate_id="cand-w02b",
        provider="fake",
        provider_document_id="doc-w02b",
        source_url="https://example.invalid/seed.pdf",
        staged_path=str(staged_path),
        content_sha256=SEED_SHA,
        byte_size=len(SEED_BYTES),
        mime_type="application/pdf",
        retrieved_at="2026-09-19T08:00:00Z",
        http_status=200,
        adapter_name="fake-cninfo",
        adapter_version="1.1.0",
    )
    resolution = ResolutionResult(
        schema_version="1.0",
        request_id=_build_request().request_id,
        status=ResolutionStatus.REUSED_EXACT,
        reason="download_not_required",
        download_required=False,
        download_allowed=True,
        matches=(),
    )
    return AcquisitionResult(
        schema_version=ACQUISITION_SCHEMA_VERSION,
        status=AcquisitionStatus.STAGED,
        resolution=resolution,
        adapter_name="fake-cninfo",
        candidate=candidate,
        receipt=receipt,
        reason="staged_per_contract",
    ), resolution


def _emit_exit(exc: Exception) -> int:
    """Mirror of the override cli.py except-block envelope assembly."""
    from company_wiki.source_catalog.error_taxonomy import (
        structured_error,
        normalize_upstream_payload,
    )

    envelope = structured_error(
        exc,
        request_id=getattr(exc, "request_id", None),
        stage=getattr(exc, "stage", None),
        cause_chain=(
            list(getattr(exc, "cause_chain", None) or [])
            if isinstance(getattr(exc, "cause_chain", None), (list, tuple))
            else []
        ),
        side_effects=(
            getattr(exc, "side_effects", None)
            if isinstance(getattr(exc, "side_effects", None), dict)
            else None
        ),
        local_diag_ref=getattr(exc, "local_diag_ref", None),
    )
    raw_upstream = getattr(exc, "provider_payload", None)
    if isinstance(raw_upstream, dict):
        upstream_envelope = normalize_upstream_payload(
            raw_upstream,
            request_id=envelope.get("request_id"),
            default_stage="provider",
        )
        if upstream_envelope is not None:
            envelope["cause_chain"].append(
                {"stage": "provider_document", "verbatim_forwarded": upstream_envelope}
            )
    sys.stderr.write(json.dumps(envelope, ensure_ascii=False, sort_keys=True))
    sys.stderr.write("\n")
    return 1


def run_case(case: str, scratch: Path) -> int:
    from company_wiki.source_catalog.acquisition import (
        AcquisitionStatus,
    )
    from company_wiki.source_catalog.acquisition_service import (
        SourceAcquisitionService,
    )
    from company_wiki.source_catalog.acquisition_journal import AcquisitionJournal
    from company_wiki.source_catalog.canonical_writer import CanonicalSourceWriter
    from company_wiki.source_catalog.resolver import SourceRequest

    catalog_dir = scratch / "catalog"
    staging_root = scratch / "staging"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)

    request = _build_request()
    journal = AcquisitionJournal(catalog_dir)

    from company_wiki.source_catalog.acquisition import AcquisitionCoordinator

    class _StubCoordinator(AcquisitionCoordinator):
        """Regression class (tested at the harness injection point): the true
        subtype is passed into the constructor; override resolve_or_stage."""

        def __init__(self) -> None:
            # Class bodies cannot read enclosing locals; instance at this time
            self.staging_root = staging_root

        def resolve_or_stage(self, req: SourceRequest):
            if not isinstance(req, SourceRequest):
                raise TypeError("request must be SourceRequest")
            if case == "p1_cw":
                exc = _StubError(CN403_MESSAGE)
                # Provider-declared carriers (passthrough contract, P1):
                exc.error_code = "upstream_unavailable"
                exc.retryable = True
                exc.provider_payload = {
                    "schema_version": "1.0",
                    "status": "failed",
                    "adapter": {"name": "stockinfo-cninfo", "version": "1.1.0"},
                    "error": {
                        "code": "upstream_unavailable",
                        "message": CN403_MESSAGE,
                        "retryable": True,
                        "type": "AdapterError",
                    },
                    "request_id": REQUEST_ID,
                }
                raise exc
            if case == "n4a":
                raise sqlite3.OperationalError("database is locked")
            if case == "n4b":
                exc = _StubError(
                    "identity contract mismatch: provider_document_id binding "
                    "conflicts with verified identity"
                )
                exc.error_code = "identity_contract"
                exc.retryable = False
                raise exc
            if case == "n3":
                self._staged = Path(sys.argv[sys.argv.index("--staged") + 1])
                self._staged.write_bytes(SEED_BYTES)
                staged_result, resolution_result = _stub_result()
                return staged_result
            raise SystemExit(f"unknown ensure case: {case}")

    service = SourceAcquisitionService(
        coordinator=_StubCoordinator(),
        writer=CanonicalSourceWriter.__new__(CanonicalSourceWriter),
        journal=journal,
    )
    if case == "n3":
        service.writer = _FailingWriter()

    if case in {"p1_cw", "n3", "n4a", "n4b"}:
        try:
            service.ensure(request)
        except Exception as exc:
            return _emit_exit(exc)
        sys.stderr.write(
            json.dumps(
                {"error": f"case {case} unexpectedly succeeded"}, ensure_ascii=False
            )
            + "\n"
        )
        return 2
    return 2


class _FailingWriter:
    """Replacement service.writer AFTER construction (harness-only)."""

    def import_staged(self, *args, **kwargs):
        raise RuntimeError(
            "post-import scan failed: completion_status=failed (roots not completed)"
        )


def run_exit_probe(scratch: Path) -> int:
    """Real modified cli.main() exit path: valid scratch config loads, then
    cli.SourceCatalog (attribute replaced, harness-only) raises a structured
    probe exception with a nested cause dict."""
    import company_wiki.source_catalog.cli as cli

    class _ProbeSourceCatalog:
        def __init__(self, config):
            exc = _StubError(CN403_MESSAGE)
            exc.error_code = "upstream_unavailable"
            exc.retryable = True
            exc.stage = "adapter_process"
            exc.request_id = REQUEST_ID
            exc.cause_chain = [
                {
                    "stage": "provider_document",
                    "verbatim_nested": {
                        "error": {
                            "code": "upstream_unavailable",
                            "message": CN403_MESSAGE,
                            "retryable": True,
                        }
                    },
                    "note": "该嵌套 dict 不得被拼接进 message 字符串",
                }
            ]
            exc.side_effects = {
                "download_events": 0,
                "raw_bytes_saved": None,
                "staged_path": None,
            }
            raise exc

    cli.SourceCatalog = _ProbeSourceCatalog
    config_path = scratch / "cw_exit_probe_config.yaml"
    probe_root = scratch / "probe_root"
    probe_root.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        'schema_version: "1.0"\n'
        f"catalog_dir: {json.dumps(str(scratch / 'catalog_probe'))}\n"
        "roots:\n"
        "  - root_id: probe_root\n"
        f"    path: {json.dumps(str(probe_root))}\n"
        "    kind: directory\n",
        encoding="utf-8",
    )
    return cli.main(["--config", str(config_path), "scan", "--dry-run"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--scratch", required=True)
    parser.add_argument("--staged", default=None)
    args = parser.parse_args()
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    Path(args.scratch).mkdir(parents=True, exist_ok=True)
    if args.staged:
        Path(args.staged).parent.mkdir(parents=True, exist_ok=True)
    if args.case == "exit_probe":
        return run_exit_probe(Path(args.scratch))
    return run_case(args.case, Path(args.scratch))


if __name__ == "__main__":
    raise SystemExit(main())
