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
import json
import sys

from report_catalog import CatalogError, ReportCatalog, import_w09
from report_catalog_deployment import (DeploymentError, assert_read_only_command,
                                       build_catalog, resolve_owner_root, split_owner_root)


def _emit_error(code: str, message: str) -> int:
    print(json.dumps({"schema_version": "rf-report-catalog/1", "error": {"code": code,
          "message": message}}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
    return 2


def _query_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--entity-id", required=True)
    parser.add_argument("--analysis-subject-id")
    parser.add_argument("--information-as-of")
    parser.add_argument("--cursor")
    parser.add_argument("--limit", type=int, default=50)


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
    for name in ("get-run", "get-report", "get-model"):
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
        elif args.command == "get-model":
            output = catalog.get_model(args.report_id)
        elif args.command == "get-calculation":
            output = catalog.get_calculation(args.report_id, args.node_id)
        elif args.command == "get-calculation-trace":
            output = catalog.get_calculation_trace(args.report_id, args.node_id)
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
        encoded = json.dumps(output, ensure_ascii=False, sort_keys=True, allow_nan=False)
        if args.command in {"get-calculation-trace", "get-source-snapshot"} and len(encoded.encode("utf-8")) > 2_000_000:
            raise CatalogError("lineage_limit_exceeded", "public lineage output exceeds its byte bound")
        print(encoded)
        return 0
    except DeploymentError as exc:
        return _emit_error(exc.code, exc.message)
    except (CatalogError, OSError, ValueError, KeyError) as exc:
        code = exc.code if isinstance(exc, CatalogError) else "catalog_invalid"
        message = str(exc) if isinstance(exc, CatalogError) else "catalog request failed"
        return _emit_error(code, message)


if __name__ == "__main__":
    raise SystemExit(main())
