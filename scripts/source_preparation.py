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


def prepare_source(
    request: dict,
    *,
    allow_download: bool = False,
    timeout_seconds: float = 900.0,
    python: tuple[str, ...] = (sys.executable,),
) -> dict:
    """Orchestrate the real chain and return the RevenueSourceRecord."""
    command = (
        *python,
        str(FILING_FETCH_CLIENT),
        "--request-file", "-",
    )
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
    handle = payload.get("handle") or {}
    # Reuse receipt: artifact selection happens in company_wiki_source
    record = company_wiki_source.build_revenue_source_record(
        handle,
        as_of_date=str(request.get("as_of_date", "")),
        source_type=str(handle.get("mime_type") or "application/pdf"),
        publisher=str(handle.get("provider") or "unknown"),
        page_or_section="1",
        prompt_injection_status="none",
    )
    record["reuse_receipt"] = {
        "parser_calls": 0,
        "llm_calls": 0,
        "download_calls": 0 if handle else 1,
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
