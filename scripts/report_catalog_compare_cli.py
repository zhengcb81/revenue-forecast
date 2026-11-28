"""Bounded public stdin/stdout adapter for exact frozen-report comparison.

The optional ``--owner-root`` is a trusted operator deployment parameter: it
selects the owner workspace that holds the managed catalog and the frozen
report artifacts, so a deployment may keep that workspace apart from the
code checkout. It is taken out of the argument list before the request is
read, so the CompareRequest on stdin keeps exactly its four fields and can
never select a path, a catalog, a command or an environment variable.
Without the option this CLI keeps its original code-root behaviour.
"""
from __future__ import annotations

from rf_cli_feedback import Invocation, exit_cli, observed_entry
from rf_local_diagnostics import redact_text

import json
import sys
from typing import Any

from report_catalog import CatalogError
from report_catalog_compare import SCHEMA_VERSION, CompareError, compare_reports
from report_catalog_deployment import (DeploymentError, build_catalog, resolve_owner_root,
                                       split_owner_root)

MAX_INPUT_BYTES = 64 * 1024


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CompareError("invalid_json", "JSON object contains duplicate keys")
        result[key] = value
    return result


def _reject_constant(_: str) -> None:
    raise CompareError("invalid_json", "JSON non-finite numbers are forbidden")


def _error_code(error: BaseException) -> str:
    if isinstance(error, CompareError):
        return error.code
    if isinstance(error, CatalogError):
        if error.code == "not_found":
            return "not_found"
        if error.code in {"catalog_unavailable", "artifact_unavailable"}:
            return "unavailable"
        return "incompatible"
    if isinstance(error, (OSError,)):
        return "unavailable"
    if isinstance(error, (MemoryError, RecursionError)):
        return "resource_limit"
    return "invalid_request"


def _emit_error(runtime: Invocation, code: str, message: str) -> int:
    runtime.note_native(code, kind="refusal" if code.startswith("invalid_") else "failure", effect="not_started")
    payload = {"schema_version": SCHEMA_VERSION,
               "error": {"code": code, "message": redact_text(message)}}
    sys.stderr.write(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                allow_nan=False, separators=(",", ":")) + "\n")
    return 2


@observed_entry(machine_stderr=True)
def main(argv: list[str] | None = None, *, runtime: Invocation) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    try:
        owner_root, command_argv = split_owner_root(argv)
        # The trusted workspace is settled before the command is checked and
        # before the request is read, so a bad deployment argument is refused
        # by name and pathless instead of turning into a command error.
        owner_workspace = resolve_owner_root(owner_root)
    except DeploymentError as exc:
        return _emit_error(runtime, exc.code, exc.message)
    if command_argv != ["compare"]:
        return _emit_error(runtime, "invalid_command", "only the fixed compare command is supported")
    runtime.note_operation("compare", external_work_possible=False)
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        runtime.note_input(raw)
        if len(raw) > MAX_INPUT_BYTES:
            return _emit_error(runtime, "input_too_large", "comparison request exceeds the input limit")
        try:
            text = raw.decode("utf-8", errors="strict")
            request = json.loads(text, object_pairs_hook=_object_no_duplicates,
                                 parse_constant=_reject_constant)
        except CompareError:
            raise
        except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
            raise CompareError("invalid_json", "comparison request must be valid bounded JSON") from exc
        catalog = build_catalog(owner_workspace)
        result = compare_reports(request, catalog=catalog)
        payload = {"schema_version": SCHEMA_VERSION, **result}
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False,
                             separators=(",", ":"))
        sys.stdout.write(encoded + "\n")
        return 0
    except DeploymentError as exc:
        return _emit_error(runtime, exc.code, exc.message)
    except CompareError as exc:
        return _emit_error(runtime, exc.code, str(exc))
    except CatalogError as exc:
        return _emit_error(runtime, _error_code(exc), "exact catalog or report read failed")
    except OSError:
        return _emit_error(runtime, "unavailable", "comparison could not complete within resource limits")
    except (MemoryError, RecursionError):
        return _emit_error(runtime, "resource_limit", "comparison could not complete within resource limits")
    except Exception:
        # No exception text from owner libraries is exposed: it may contain a locator.
        return _emit_error(runtime, "incompatible", "exact catalog or report validation failed")


if __name__ == "__main__":
    raise SystemExit(exit_cli(main))
