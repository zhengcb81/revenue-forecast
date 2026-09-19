"""WU-1000: the single production orchestration entry — source preparation.

From a FilingRequest, this CLI drives the REAL cross-repo chain as
subprocesses: filing-fetch (resolve/ensure) → company-wiki catalog
(SourceBundle) → artifact selection → RevenueSourceRecord + reuse receipt.

The forecast calculator (revenue_forecast.py) stays pure: it consumes the
validated source record and never touches network/catalog/download.

Exit codes: 0 = source record produced; 1 = not found/not admissible;
2 = usage error; 3 = internal.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# I-02-B isolated-copy note: FILING_FETCH_CLIENT stays LOCAL to the
# override tree (the modified sibling copy), while helper modules that
# are NOT in this card allowlist (company_wiki_source /
# processing_demand) keep loading READ-ONLY from the RF scripts dir.
_ATTEMPT_ROOT = Path(__file__).resolve().parents[2]
_OVERRIDE_DIR = Path(__file__).resolve().parent
_RF_ROOT = Path("C:/Users/郑曾波/Projects/revenue-forecast")
sys.path.insert(0, str(_RF_ROOT / "scripts"))
sys.path.insert(0, str(_ATTEMPT_ROOT / "scripts"))
FILING_FETCH_CLIENT = _OVERRIDE_DIR / "filing_fetch_client.py"

import company_wiki_source  # noqa: E402
from processing_demand import DemandQueue  # noqa: E402

# ZR-701: source preparation submits one demand per prepared source (key =
# the source record's sha-256 identity) so schedulers/consumers can claim,
# heartbeat and complete the work under the shared ProcessingDemand
# contract.  In-memory queue (persistence is a later phase).
_preparation_demands = DemandQueue()


def preparation_demands() -> DemandQueue:
    """The process-level demand queue (test-visible)."""
    return _preparation_demands


def _demand_key(record: dict) -> str:
    """Stable demand key for one prepared source (keeps prepare_source
    within the frozen complexity ratchet)."""
    return str(record.get("source_id") or record.get("source_sha256") or "")


def _submit_preparation_demand(record: dict) -> None:
    """ZR-701: enqueue one deduped processing demand per prepared source."""
    source_key = _demand_key(record)
    if source_key:
        _preparation_demands.enqueue(key=source_key, kind="source_preparation", now=0.0)


def _read_request(request_file: str | None) -> dict:
    if request_file:
        return json.loads(Path(request_file).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


_SOURCE_TYPE_BY_KIND = {
    "annual_report": "regulatory_filing",
    "quarterly_report": "regulatory_filing",
    "semi_annual_report": "regulatory_filing",
    "regulatory_filing": "regulatory_filing",
    "investor_presentation": "investor_presentation",
    "earnings_transcript": "earnings_transcript",
    "official_statistics": "official_statistics",
    "company_release": "company_release",
}


def _revenue_source_type(handle: dict) -> str:
    kind = str(handle.get("document_kind") or "")
    return _SOURCE_TYPE_BY_KIND.get(kind, "regulatory_filing")


class UpstreamEnvelopeError(RuntimeError):
    """I-02-B: carries the parsed upstream cross-CLI error envelope so the
    outer CLI re-emits the structured fields instead of joining them into a
    message string."""

    def __init__(self, message: str, envelope: dict) -> None:
        super().__init__(message)
        self.error_envelope = envelope


def _archive_full_output(proc, diag_dir: Path | None, layer: str) -> str | None:
    """I-02-B: archive the FULL non-zero-child output (never truncated);
    returns the local_diag_ref value or None when no diag dir is configured."""
    if diag_dir is None:
        return None
    try:
        import time

        diag_dir = Path(diag_dir)
        diag_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
        path = diag_dir / f"upstream_raw_{layer}_{stamp}.txt"
        path.write_text(
            f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
            f"\n--- exit code: {proc.returncode} ---\n",
            encoding="utf-8",
        )
        return str(path)
    except OSError:
        return None


def normalize_envelope(envelope: dict, *, request_id: str):
    """Load the frozen error taxonomy from the isolated CW override tree
    and normalize a RAW upstream document into the frozen envelope."""
    from company_wiki.source_catalog.error_taxonomy import (
        normalize_upstream_payload,
    )

    return normalize_upstream_payload(envelope, request_id=request_id)


def _ensure_cw_taxonomy_importable() -> None:
    """I-02-B: isolated-chain wiring.  The CW override copies register
    under the true module names via w02b_bootstrap (synthetic package
    shim over the READ-ONLY CW repo src); idempotent."""
    try:
        import company_wiki.source_catalog.error_taxonomy  # noqa: F401
    except Exception:
        import w02b_bootstrap

        w02b_bootstrap.setup()


def _loads_maybe(text: str):
    """Parse text as JSON, None when empty/invalid (never guessed)."""
    if not text or not text.strip():
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def prepare_source(
    request: dict,
    *,
    allow_download: bool = False,
    timeout_seconds: float = 900.0,
    python: tuple[str, ...] = (sys.executable,),
    company_wiki_config: Path | None = None,
    filing_fetch_root: Path | None = None,
    diag_dir: Path | None = None,
) -> dict:
    """Orchestrate the real chain and return the RevenueSourceRecord."""
    # no --request-file: the client reads the request from stdin (C1 fix)
    command = (*python, str(FILING_FETCH_CLIENT))
    if filing_fetch_root is not None:
        # FC-1202: explicit root override for E2E fixtures — no implicit
        # sibling-location fallback anywhere in the chain.
        command = (*command, "--filing-fetch-root", str(filing_fetch_root))
    if company_wiki_config is not None:
        command = (*command, "--company-wiki-config", str(company_wiki_config))
    if allow_download:
        command = (*command, "--allow-download")
    if timeout_seconds:
        command = (*command, "--timeout-seconds", str(timeout_seconds))
    proc = subprocess.run(
        command,
        input=json.dumps(request, ensure_ascii=False),
        text=True,
        encoding="utf-8",
        capture_output=True,
        cwd=str(_ATTEMPT_ROOT),
        timeout=timeout_seconds + 30,
        check=False,
    )
    if proc.returncode != 0:
        # I-02-B (W02B-N1/N2): the pre-change behaviour truncated stderr to
        # its last 800 characters and wrapped it in a RuntimeError string,
        # destroying the structured envelope.  Now: 1) a VALID upstream JSON
        # envelope is parsed and forwarded structurally; 2) an opaque
        # failure is archived in FULL (local_diag_ref) with a short summary
        # line only.
        for raw_text in (proc.stdout, proc.stderr):
            parsed = _loads_maybe(raw_text)
            if not isinstance(parsed, dict):
                continue
            envelope = parsed.get("error_envelope")
            if not isinstance(envelope, dict):
                continue
            if isinstance(envelope.get("error_envelope_schema_version"), str):
                # Already a validated cross-CLI envelope (CW/FF side):
                # forward structurally, no re-classification.
                pass
            else:
                normalized = normalize_envelope(
                    envelope,
                    request_id="execv2-w02b",
                )
                envelope = (
                    normalized
                    if normalized is not None
                    else {
                        "error_envelope_schema_version": "cross-cli-error-envelope/1.0",
                        "code": "fatal",
                        "error_type": "fatal",
                        "retryable": False,
                        "cause_chain": [
                            {
                                "stage": "envelope_normalization",
                                "opaque_upstream_document": True,
                            }
                        ],
                        "side_effects": None,
                    }
                )
            diag_ref = _archive_full_output(proc, diag_dir, "l1")
            if envelope.get("local_diag_ref") is None and diag_ref:
                envelope["local_diag_ref"] = diag_ref
            raise UpstreamEnvelopeError(
                f"upstream chain failed at exit {proc.returncode} (see error_envelope)",
                envelope,
            )
        diag_ref = _archive_full_output(proc, diag_dir, "l1")
        stderr_text = proc.stderr.strip() or proc.stdout.strip() or "no output"
        summary = stderr_text.splitlines()[-1][:160]
        exc = RuntimeError(f"filing-fetch client exited {proc.returncode}: {summary}")
        exc.local_diag_ref = diag_ref
        raise exc
    payload = json.loads(proc.stdout)
    # the client prints the handle dict directly (no wrapper); FC-704: the
    # handle carries the deep-validated resolution envelope (journal-derived
    # outcome + download event evidence) when company-wiki supplied one.
    handle = payload if isinstance(payload, dict) else {}
    # FC-704: download evidence comes from the resolution envelope, never
    # inferred from whether a handle was returned (scenario_matrix §2).
    # No envelope => fail closed: a receipt claiming zero downloads without
    # event evidence is exactly the fake the plan forbids.
    envelope = handle.get("resolution_envelope")
    if not isinstance(envelope, dict):
        raise RuntimeError(
            "company-wiki resolution envelope missing — download evidence "
            "cannot be derived; fail closed instead of fabricating counts"
        )
    download_events = envelope.get("download_events")
    if isinstance(download_events, bool) or download_events not in (0, 1):
        raise RuntimeError(
            f"invalid download_events in resolution envelope: {download_events!r}"
        )
    # FC-904: artifact selection is DAG-minimal and SOURCED from the envelope
    # bundle (FC-902) via the selector — the unsourced
    # payload.get("selected_artifacts") path is removed.  artifact_read =
    # roles with a verified artifact (producers do not run); producer_events =
    # the DAG closure of the non-reusable roles (never a blind full recompute).
    artifact_read, producer_events = company_wiki_source.select_artifact_roles(handle)
    # FC-905-b: capture/safety evidence comes from the envelope — never
    # hardcoded.  An unreviewed source is blocked per policy; absent parser/
    # llm counts fail closed (never fabricated as 0).
    prompt_injection_status = envelope.get("prompt_injection_status")
    if prompt_injection_status is None:
        prompt_injection_status = "not_reviewed"  # defensive N-1 default
    if prompt_injection_status == "not_reviewed":
        raise RuntimeError(
            "prompt injection not reviewed — source preparation blocked "
            "per policy (prompt_injection_status=not_reviewed)"
        )
    parser_calls = envelope.get("parser_calls")
    llm_calls = envelope.get("llm_calls")
    if parser_calls is None or llm_calls is None:
        raise RuntimeError(
            "parser/llm counts absent from the resolution envelope — fail "
            "closed instead of fabricating 0"
        )
    record = company_wiki_source.build_revenue_source_record(
        handle,
        as_of_date=str(request.get("as_of_date", "")),
        source_type=_revenue_source_type(handle),
        publisher=str(handle.get("provider") or "unknown"),
        page_or_section="1",
        prompt_injection_status=prompt_injection_status,
    )
    record["reuse_receipt"] = {
        "parser_calls": parser_calls,
        "llm_calls": llm_calls,
        "download_calls": download_events,
        "outcome": envelope.get("outcome"),
        "policy_hash": envelope.get("policy_hash"),
        "activation_epoch": envelope.get("activation_epoch"),
        "bundle_status": envelope.get("bundle_status"),
        "prompt_injection_status": prompt_injection_status,
        "artifact_read": artifact_read,
        "producer_events": producer_events,
    }
    # ZR-701: submit one processing demand per prepared source; a repeated
    # preparation of the same source dedupes to the existing demand.
    _submit_preparation_demand(record)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Revenue source preparation — the single production entry."
    )
    parser.add_argument("--request-file", help="request JSON file (else stdin)")
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument(
        "--diag-dir",
        type=Path,
        default=None,
        help="Where to archive FULL raw upstream output on opaque failures "
        "(I-02-B; no truncation).",
    )
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument(
        "--company-wiki-config",
        type=Path,
        default=None,
        help="override company-wiki config for the chain (E2E)",
    )
    parser.add_argument(
        "--filing-fetch-root",
        type=Path,
        default=None,
        help="override the filing-fetch skill root for the chain (E2E)",
    )
    args = parser.parse_args(argv)

    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    try:
        _ensure_cw_taxonomy_importable()
        request = _read_request(args.request_file)
        record = prepare_source(
            request,
            allow_download=args.allow_download,
            timeout_seconds=args.timeout_seconds,
            company_wiki_config=args.company_wiki_config,
            filing_fetch_root=args.filing_fetch_root,
            diag_dir=args.diag_dir,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(json.dumps({"error_code": "bad_request", "error": str(exc)}))
        sys.stderr.write("\n")
        return 2
    except RuntimeError as exc:
        # I-02-B: when an upstream envelope rode on the exception, re-emit its
        # structured fields verbatim (code/retryable/request_id/stage/
        # cause_chain/side_effects) instead of joining the dict into a string.
        envelope = getattr(exc, "error_envelope", None)
        if isinstance(envelope, dict):
            payload = {
                "error_code": envelope.get("code")
                or envelope.get("error_type")
                or "upstream",
                "error": str(exc),
                "retryable": bool(envelope.get("retryable")),
                "error_envelope": envelope,
            }
            for key in (
                "request_id",
                "stage",
                "cause_chain",
                "side_effects",
                "local_diag_ref",
            ):
                if key in envelope:
                    payload[key] = envelope[key]
        else:
            payload = {
                "error_code": "upstream",
                "error": str(exc),
                "retryable": False,
            }
            diag_ref = getattr(exc, "local_diag_ref", None)
            if diag_ref:
                payload["local_diag_ref"] = diag_ref
        sys.stderr.write(json.dumps(payload, ensure_ascii=False))
        sys.stderr.write("\n")
        return 3
    sys.stdout.write(json.dumps(record, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
