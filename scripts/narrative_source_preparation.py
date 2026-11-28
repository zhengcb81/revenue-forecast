"""Opt-in narrative source preparation via CWP's published, pathless reader.

stdin is narrative-read-request/1 (or narrative-reference-request/1).
stdout is RF's source-only context (or metadata reference), never a forecast.
"""

from __future__ import annotations

from rf_cli_feedback import Invocation, exit_cli, observed_entry

import argparse
from pathlib import Path
import sys
from typing import Sequence

from company_wiki_narrative_contracts import (
    NarrativeTransportError, canonical_bytes, decode_object,
)
from company_wiki_narrative_reader import find_narrative_reference, read_narrative_context


class _Parser(argparse.ArgumentParser):
    def error(self, _message):
        raise NarrativeTransportError("blocked", "invalid_cli_arguments")


@observed_entry(machine_stderr=True)
def main(argv: Sequence[str] | None = None, *, runtime: Invocation) -> int:
    parser = _Parser(description=__doc__)
    parser.add_argument("--company-wiki-catalog-config", type=Path, required=True)
    parser.add_argument("--operation", choices=("reference", "read"), default="read")
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--max-response-bytes", type=int, help="explicit transport resource budget, not a source quality threshold")
    parser.add_argument("--max-receipt-bytes", type=int, help="optional explicit transport diagnostic budget")
    parser.add_argument("--reader-executable", help="explicit installed CWP command; default Python module")
    try:
        args = parser.parse_args(argv)
        runtime.note_operation(args.operation, external_work_possible=False)
        raw = sys.stdin.buffer.read()
        runtime.note_input(raw)
        request = decode_object(raw)
        command = [args.reader_executable] if args.reader_executable else None
        kwargs = {
            "catalog_config": args.company_wiki_catalog_config,
            "timeout_seconds": args.timeout_seconds, "reader_command": command,
        }
        if args.operation == "read":
            if args.max_response_bytes is not None:
                kwargs["max_response_bytes"] = args.max_response_bytes
            if args.max_receipt_bytes is not None:
                kwargs["max_receipt_bytes"] = args.max_receipt_bytes
        if args.operation == "reference":
            result = find_narrative_reference(request, **kwargs)
        else:
            result = read_narrative_context(request, **kwargs).to_dict()
        sys.stdout.buffer.write(canonical_bytes(result) + b"\n")
        sys.stdout.buffer.flush()
        return 0
    except NarrativeTransportError as error:
        runtime.note_native(error.reason, kind="refusal", effect="not_started", error=error)
        refusal = {"schema_version": "revenue-narrative-refusal/1",
                   "status": error.status, "reason": error.reason}
    except (TypeError, ValueError, OSError, RecursionError) as error:
        runtime.note_native("invalid_request", kind="refusal", effect="not_started", error=error)
        refusal = {"schema_version": "revenue-narrative-refusal/1",
                   "status": "blocked", "reason": "invalid_request"}
    sys.stderr.buffer.write(canonical_bytes(refusal) + b"\n")
    sys.stderr.buffer.flush()
    return 2


if __name__ == "__main__":
    raise SystemExit(exit_cli(main))
