"""Fixed read-only/management CLI for the public RF verified-scope contract.

``--owner-root`` selects a trusted RF business workspace through the existing
deployment seam. ``--data-root`` is the separate owner state root for scope
bindings; ``--subject-fixture`` is a frozen public subject snapshot fixture.
Neither deployment input is part of a business request. The request budget is
inherited from the published compare CLI; responses are never truncated by a
row or byte cap. StockWiki modules, private catalog helpers and neighbouring
databases are never imported.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NoReturn

from report_catalog import CatalogError, ReportCatalog
from report_catalog_compare import CompareError
from report_catalog_compare_cli import MAX_INPUT_BYTES
from report_catalog_deployment import (DeploymentError, build_catalog, resolve_owner_root,
                                       split_owner_root)
from report_catalog_scope_binding import (
    READ_SCHEMA, ScopeBindingStore, build_scope_binding, list_scope_bindings,
)
from report_catalog_subject_resolver import (
    FrozenSubjectResolver, ScopeContractError,
)
from report_catalog_verified_compare import SCHEMA_VERSION, compare_verified_scope


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ScopeContractError("invalid_request", "scope command arguments are invalid")


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ScopeContractError("invalid_json", "request contains duplicate keys")
        result[key] = value
    return result


def _reject_constant(_: str) -> None:
    raise ScopeContractError("invalid_json", "non-finite JSON numbers are forbidden")


def _emit_error(code: str, schema: str) -> int:
    sys.stderr.write(json.dumps({"schema_version": schema,
                                "error": {"code": code,
                                          "message": "Verified scope request refused"}},
                               ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                     + "\n")
    return 2


def _read_request() -> dict[str, Any]:
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ScopeContractError("input_too_large", "comparison request exceeds its input limit")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"),
                           object_pairs_hook=_object_no_duplicates,
                           parse_constant=_reject_constant)
    except ScopeContractError:
        raise
    except (UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise ScopeContractError("invalid_json", "request is not strict bounded JSON") from exc
    if not isinstance(value, dict):
        raise ScopeContractError("invalid_request", "request must be an object")
    return value


def main(argv: list[str] | None = None) -> int:
    schema = SCHEMA_VERSION
    try:
        owner_root_text, raw = split_owner_root(sys.argv[1:] if argv is None else list(argv))
        workspace = resolve_owner_root(owner_root_text)
        parser = _Parser(description="Public RF verified-scope bindings and comparisons")
        shared = _Parser(add_help=False)
        shared.add_argument("--data-root", required=True,
                            help="trusted owner data root for scope bindings")
        shared.add_argument("--subject-fixture", required=True,
                            help="frozen public subject snapshot fixture JSON")
        commands = parser.add_subparsers(dest="command", required=True)
        listing = commands.add_parser("get-bindings", parents=[shared])
        listing.add_argument("--report-id", required=True)
        commands.add_parser("compare", parents=[shared])
        commands.add_parser("append-binding", parents=[shared])
        args = parser.parse_args(raw)
        schema = READ_SCHEMA if args.command == "get-bindings" else SCHEMA_VERSION
        resolver = FrozenSubjectResolver.from_public_fixture(args.subject_fixture)
        catalog = build_catalog(workspace) or ReportCatalog()
        store = ScopeBindingStore(Path(args.data_root))
        if args.command == "get-bindings":
            output = list_scope_bindings(catalog=catalog, store=store,
                                         subject_resolver=resolver,
                                         report_id=args.report_id)
        elif args.command == "append-binding":
            binding = build_scope_binding(catalog=catalog, subject_resolver=resolver,
                                          evidence=_read_request())
            output = store.append(binding)
        else:
            output = compare_verified_scope(_read_request(), catalog=catalog,
                                            subject_resolver=resolver, store=store)
        encoded = json.dumps(output, ensure_ascii=False, sort_keys=True,
                             allow_nan=False, separators=(",", ":"))
        sys.stdout.write(encoded + "\n")
        return 0
    except (ScopeContractError, CompareError, CatalogError, DeploymentError, OSError,
            ValueError, TypeError, KeyError, RecursionError) as exc:
        code = getattr(exc, "code", None) or getattr(exc, "error_code", None)
        if not isinstance(code, str):
            code = "scope_unavailable"
        return _emit_error(code, schema)


if __name__ == "__main__":
    raise SystemExit(main())
