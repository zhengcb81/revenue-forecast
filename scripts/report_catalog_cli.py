"""Fixed, pathless JSON CLI for the owner ReportCatalog.

Examples:
  python scripts/report_catalog_cli.py list-runs --entity-id ENT-123
  python scripts/report_catalog_cli.py get-report --report-id rf-...
  python scripts/report_catalog_cli.py --owner-root C:\\owner list-reports --entity-id ENT-123

The optional ``--owner-root`` is a trusted operator deployment parameter: it
selects the owner workspace that holds the managed catalog and the frozen
report artifacts, so a deployment may keep that workspace apart from the
code checkout. Without it this CLI keeps its original code-root behaviour.
The option never enters a request, never selects a command, a catalog file
or an environment variable, and it is refused for the write command.

The W09 migration command is fail-closed until an owner-installed public
StockWiki identity resolver is available. Caller JSON cannot enable it.
No forecast, model, network call, or artifact discovery runs from this CLI.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys

from report_catalog import CatalogError, ReportCatalog, import_w09
from rf_cli_feedback import note_native, observed_entry
from report_catalog_deployment import (DeploymentError, assert_read_only_command,
                                       build_catalog, resolve_owner_root, split_owner_root)


TRACE_PAGE_PROTOCOL = "rf-calculation-trace-page/1"
# 1 MiB of source bytes stays below 2 MB after base64url and the JSON envelope.
TRACE_PAGE_BYTES = 1024 * 1024


def _trace_page(catalog: ReportCatalog, args: argparse.Namespace) -> dict:
    if args.offset < 0 or (args.offset == 0) != (args.trace_sha256 is None) or (
        args.trace_sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", args.trace_sha256)
    ):
        raise CatalogError("invalid_trace_page", "provide a trace digest with a positive continuation offset")

    envelope = catalog.get_calculation_trace(args.report_id, args.node_id)
    trace = envelope.pop("trace")
    # An unrelated catalog update can change the observation revision while the
    # report-bound graph stays immutable. Page identity binds the graph only.
    body = json.dumps(
        {key: value for key, value in trace.items() if key != "catalog_revision"},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    digest = hashlib.sha256(body).hexdigest()
    if args.trace_sha256 is not None and args.trace_sha256 != digest:
        raise CatalogError("stale_cursor", "the requested trace differs from the first page")
    if args.offset >= len(body):
        raise CatalogError("invalid_trace_page", "the requested offset is outside this trace")
    chunk = body[args.offset:args.offset + TRACE_PAGE_BYTES]
    return {**envelope, "trace_page": {
        "schema_version": TRACE_PAGE_PROTOCOL,
        "report_id": args.report_id,
        "node_id": args.node_id,
        "trace_sha256": digest,
        "total_bytes": len(body),
        "offset": args.offset,
        "content_base64url": base64.urlsafe_b64encode(chunk).decode("ascii"),
    }}


def _emit_error(code: str, message: str) -> int:
    request_refusal = (code.startswith(("owner_root_", "invalid_")) or code in
                       {"not_found", "node_not_found", "identity_unverified", "write_command_forbidden"})
    note_native(code, kind="refusal" if request_refusal else "failure",
                effect="not_started" if request_refusal else "unknown")
    print(json.dumps({"schema_version": "rf-report-catalog/1", "error": {"code": code,
          "message": message}}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
    return 2


def _query_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--entity-id", required=True)
    parser.add_argument("--analysis-subject-id")
    parser.add_argument("--information-as-of")
    parser.add_argument("--cursor")
    parser.add_argument("--limit", type=int, default=50)


@observed_entry
def main(argv: list[str] | None = None) -> int:
    raw = sys.argv[1:] if argv is None else list(argv)
    try:
        owner_root, command_argv = split_owner_root(raw)
        # The trusted workspace is settled before the command is parsed, so a
        # bad deployment argument is refused by name and pathless instead of
        # turning into a parser usage error.
        owner_workspace = resolve_owner_root(owner_root)
    except DeploymentError as exc:
        return _emit_error(exc.code, exc.message)
    parser = argparse.ArgumentParser(description="Read owner-indexed RF runs and exact reports")
    commands = parser.add_subparsers(dest="command", required=True)
    _query_filters(commands.add_parser("list-runs"))
    _query_filters(commands.add_parser("list-reports"))
    for name in ("get-run", "get-report", "get-model", "get-forecast-snapshot"):
        command = commands.add_parser(name)
        command.add_argument("--run-id" if name == "get-run" else "--report-id", required=True)
    attempt = commands.add_parser("get-attempt")
    attempt.add_argument("--run-id", required=True)
    attempt.add_argument("--attempt-id", required=True)
    calculation = commands.add_parser("get-calculation")
    calculation.add_argument("--report-id", required=True)
    calculation.add_argument("--node-id", required=True)
    trace = commands.add_parser("get-calculation-trace")
    trace.add_argument("--report-id", required=True)
    trace.add_argument("--node-id", required=True)
    page = commands.add_parser("get-calculation-trace-page")
    page.add_argument("--report-id", required=True)
    page.add_argument("--node-id", required=True)
    page.add_argument("--offset", type=int, default=0)
    page.add_argument("--trace-sha256")
    snapshot = commands.add_parser("get-source-snapshot")
    snapshot.add_argument("--report-id", required=True)
    snapshot.add_argument("--snapshot-id", required=True)
    migration = commands.add_parser("import-w09")
    migration.add_argument("--entity-id", required=True)
    migration.add_argument("--analysis-subject-id")
    migration.add_argument("--listing-id")
    migration.add_argument("--identity-evidence-json", required=True,
                           help="inline identity assertion; import remains unavailable without an owner resolver")
    args = parser.parse_args(command_argv)
    try:
        assert_read_only_command(args.command, owner_root)
        catalog = build_catalog(owner_workspace)
        if catalog is None:
            catalog = ReportCatalog()
        if args.command == "list-runs":
            output = catalog.list_runs(args.entity_id, analysis_subject_id=args.analysis_subject_id,
                                       information_as_of=args.information_as_of,
                                       cursor=args.cursor, limit=args.limit)
        elif args.command == "list-reports":
            output = catalog.list_reports(args.entity_id, analysis_subject_id=args.analysis_subject_id,
                                          information_as_of=args.information_as_of,
                                          cursor=args.cursor, limit=args.limit)
        elif args.command == "get-run":
            output = catalog.get_run(args.run_id)
        elif args.command == "get-attempt":
            output = catalog.get_attempt(args.run_id, args.attempt_id)
        elif args.command == "get-report":
            output = catalog.get_report(args.report_id)
            output["calculation_trace_page_protocol"] = TRACE_PAGE_PROTOCOL
        elif args.command == "get-model":
            output = catalog.get_model(args.report_id)
        elif args.command == "get-forecast-snapshot":
            output = catalog.get_forecast_snapshot(args.report_id)
        elif args.command == "get-calculation":
            output = catalog.get_calculation(args.report_id, args.node_id)
        elif args.command == "get-calculation-trace":
            output = catalog.get_calculation_trace(args.report_id, args.node_id)
        elif args.command == "get-calculation-trace-page":
            output = _trace_page(catalog, args)
        elif args.command == "get-source-snapshot":
            output = catalog.get_source_snapshot(args.report_id, args.snapshot_id)
        else:
            try:
                identity_evidence = json.loads(args.identity_evidence_json)
            except json.JSONDecodeError as exc:
                raise CatalogError("identity_unverified", "identity evidence must be JSON") from exc
            output = import_w09(catalog, entity_id=args.entity_id,
                                analysis_subject_id=args.analysis_subject_id,
                                listing_id=args.listing_id, identity_evidence=identity_evidence)
        encoder = json.JSONEncoder(ensure_ascii=False, sort_keys=True, allow_nan=False)
        if args.command == "get-calculation-trace":
            # The native projection validates the complete graph before output.
            for chunk in encoder.iterencode(output):
                sys.stdout.write(chunk)
            sys.stdout.write("\n")
        else:
            print(encoder.encode(output))
        return 0
    except DeploymentError as exc:
        return _emit_error(exc.code, exc.message)
    except (CatalogError, OSError, ValueError, KeyError) as exc:
        code = exc.code if isinstance(exc, CatalogError) else "catalog_invalid"
        message = str(exc) if isinstance(exc, CatalogError) else "catalog request failed"
        return _emit_error(code, message)


if __name__ == "__main__":
    raise SystemExit(main())
