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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
FILING_FETCH_CLIENT = PROJECT_ROOT / "scripts" / "filing_fetch_client.py"

import company_wiki_source  # noqa: E402


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


def prepare_source(
    request: dict,
    *,
    allow_download: bool = False,
    timeout_seconds: float = 900.0,
    python: tuple[str, ...] = (sys.executable,),
    company_wiki_config: Path | None = None,
) -> dict:
    """Orchestrate the real chain and return the RevenueSourceRecord."""
    # no --request-file: the client reads the request from stdin (C1 fix)
    command = (*python, str(FILING_FETCH_CLIENT))
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
        cwd=str(PROJECT_ROOT),
        timeout=timeout_seconds + 30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"filing-fetch client exited {proc.returncode}: "
            f"{proc.stderr.strip()[-800:]}"
        )
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
    # Reuse receipt: artifact selection happens in company_wiki_source
    record = company_wiki_source.build_revenue_source_record(
        handle,
        as_of_date=str(request.get("as_of_date", "")),
        source_type=_revenue_source_type(handle),
        publisher=str(handle.get("provider") or "unknown"),
        page_or_section="1",
        prompt_injection_status="not_detected",
    )
    record["reuse_receipt"] = {
        "parser_calls": 0,
        "llm_calls": 0,
        "download_calls": download_events,
        "outcome": envelope.get("outcome"),
        "policy_hash": envelope.get("policy_hash"),
        "activation_epoch": envelope.get("activation_epoch"),
        "bundle_status": envelope.get("bundle_status"),
        "selected_artifacts": payload.get("selected_artifacts", []),
    }
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Revenue source preparation — the single production entry."
    )
    parser.add_argument("--request-file", help="request JSON file (else stdin)")
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument("--company-wiki-config", type=Path, default=None,
                        help="override company-wiki config for the chain (E2E)")
    args = parser.parse_args(argv)

    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    try:
        request = _read_request(args.request_file)
        record = prepare_source(
            request,
            allow_download=args.allow_download,
            timeout_seconds=args.timeout_seconds,
            company_wiki_config=args.company_wiki_config,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(json.dumps({"error_code": "bad_request", "error": str(exc)}))
        sys.stderr.write("\n")
        return 2
    except RuntimeError as exc:
        sys.stderr.write(json.dumps({"error_code": "upstream", "error": str(exc)}))
        sys.stderr.write("\n")
        return 3
    sys.stdout.write(json.dumps(record, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
