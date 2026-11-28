"""RF source-preparation entry for structured historical statements."""
from __future__ import annotations

from rf_cli_feedback import DiagnosticParser, Invocation, exit_cli, observed_entry

import json
from pathlib import Path
import sys

from company_wiki_narrative_contracts import NarrativeTransportError, decode_object
from filing_fetch_client import STATEMENTS_RESPONSE, request_financial_statements


@observed_entry(machine_stderr=True)
def main(argv: list[str] | None = None, *, runtime: Invocation) -> int:
    parser = DiagnosticParser(description=__doc__)
    parser.add_argument("--request-file", type=Path, help="read JSON from this file instead of stdin")
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    root = parser.add_mutually_exclusive_group()
    root.add_argument("--filing-fetch-root", type=Path)
    root.add_argument("--filing-fetch-root-config", type=Path)
    parser.add_argument("--company-wiki-config", type=Path, help="connection config passed to filing-fetch")
    args = parser.parse_args(argv)
    runtime.stage = "request-decode"

    try:
        raw = args.request_file.read_bytes() if args.request_file else sys.stdin.buffer.read()
        runtime.note_input(raw)
        request = decode_object(raw)
    except (OSError, NarrativeTransportError) as error:
        runtime.note_native("invalid_statement_request", kind="refusal", effect="not_started", error=error)
        envelope = {
            "schema_version": STATEMENTS_RESPONSE, "status": "request_error",
            "reason": "invalid_statement_request", "retryable": False,
        }
        exit_code = 2
    else:
        runtime.note_operation("read-financial-statements", external_work_possible=False)
        result = request_financial_statements(
            request, timeout_seconds=args.timeout_seconds, filing_fetch_root=args.filing_fetch_root,
            filing_fetch_root_config=args.filing_fetch_root_config, company_wiki_config=args.company_wiki_config,
        )
        envelope, exit_code = result.envelope, result.exit_code
        if exit_code:
            runtime.note_native(str(envelope.get("reason", "statement_source_failure")))
        if result.diagnostics:
            sys.stderr.buffer.write(result.diagnostics)
    sys.stdout.buffer.write((json.dumps(envelope, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(exit_cli(main))
