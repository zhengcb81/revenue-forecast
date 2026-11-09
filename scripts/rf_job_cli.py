"""Fixed pathless JSON CLI for the RF public job facade (rf-job/1).

Routes:
  python scripts/rf_job_cli.py --owner-root <dir> --deployment-config <path> \
      submit --request-json '<json>'
  python scripts/rf_job_cli.py --owner-root <dir> get-status --job-id rfjob-...
  python scripts/rf_job_cli.py --owner-root <dir> act --job-id rfjob-... --action reconcile
  python scripts/rf_job_cli.py --owner-root <dir> list-jobs [--limit N]

The business request never carries paths, command strings or credentials.
``--owner-root`` selects the trusted workspace that holds the job store
(``<root>/artifacts/rf_jobs/``); it is a deployment parameter in the same
discipline as the report-catalog ``--owner-root`` seam and never enters a
request body.  ``--deployment-config`` selects the trusted chain/budget
configuration.  The facade does not register into the managed report catalog:
that stays with the explicit management import command after a job succeeds.

Exit codes: 0 = ok; 2 = named request/deployment/job error; 3 = internal.
stdout is always one JSON document (schema_version rf-job/1); errors go to
stderr as a named, pathless JSON document.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rf_job_facade import (  # noqa: E402
    JobFacade,
    JobFacadeError,
    Deployment,
    resolve_owner_root,
)

OWNER_ROOT_OPTION = "--owner-root"
DEPLOYMENT_CONFIG_OPTION = "--deployment-config"


def _emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False))


def _emit_error(code: str, message: str) -> int:
    print(json.dumps({"schema_version": "rf-job/1",
                      "error": {"code": code, "message": message}},
                     ensure_ascii=False, sort_keys=True), file=sys.stderr)
    return 2


def _split_deployment_argv(raw: list[str]) -> tuple[str | None, str | None, list[str]]:
    owner_root: str | None = None
    deployment_config: str | None = None
    remaining: list[str] = []
    index = 0
    while index < len(raw):
        token = raw[index]
        matched: str | None = None
        if token in (OWNER_ROOT_OPTION, DEPLOYMENT_CONFIG_OPTION):
            matched = token
            if index + 1 >= len(raw) or raw[index + 1].startswith("-"):
                raise JobFacadeError("owner_root_invalid",
                                     f"{token} requires an absolute workspace path argument")
            value = raw[index + 1]
            index += 2
        else:
            for option in (OWNER_ROOT_OPTION, DEPLOYMENT_CONFIG_OPTION):
                if token.startswith(option + "="):
                    matched = option
                    value = token[len(option) + 1:]
                    break
            else:
                remaining.append(token)
                index += 1
                continue
        if matched == OWNER_ROOT_OPTION:
            if owner_root is not None:
                raise JobFacadeError("owner_root_invalid",
                                     f"{OWNER_ROOT_OPTION} may be given once")
            owner_root = value
        else:
            if deployment_config is not None:
                raise JobFacadeError("deployment_config_invalid",
                                     f"{DEPLOYMENT_CONFIG_OPTION} may be given once")
            deployment_config = value
    return owner_root, deployment_config, remaining


def _read_request(request_json: str | None) -> object:
    if request_json is not None:
        return json.loads(request_json)
    return json.load(sys.stdin)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="strict")
            except (ValueError, OSError):
                pass
    raw = sys.argv[1:] if argv is None else list(argv)
    try:
        owner_root_text, deployment_config_text, command_argv = _split_deployment_argv(raw)
    except JobFacadeError as exc:
        return _emit_error(exc.code, exc.message)

    import argparse

    parser = argparse.ArgumentParser(
        description="RF public full_research job facade (protocol rf-job/1)")
    commands = parser.add_subparsers(dest="command", required=True)
    submit = commands.add_parser(
        "submit", help="submit a full_research job (idempotent by idempotency_key)")
    submit.add_argument("--request-json", help="the rf-job/1 request JSON inline; "
                        "when omitted the request JSON is read from stdin")
    status = commands.add_parser("get-status", help="read-only JobView of one owner job")
    status.add_argument("--job-id", required=True)
    act = commands.add_parser("act", help="act on one owner job (reconcile | resume)")
    act.add_argument("--job-id", required=True)
    act.add_argument("--action", required=True, choices=("reconcile", "resume"))
    listing = commands.add_parser("list-jobs", help="list owner jobs in this store")
    listing.add_argument("--limit", type=int, default=50)
    args = parser.parse_args(command_argv)

    try:
        owner_root = resolve_owner_root(owner_root_text)
        deployment = (Deployment.load(Path(deployment_config_text))
                      if deployment_config_text is not None else None)
    except JobFacadeError as exc:
        return _emit_error(exc.code, exc.message)

    try:
        facade = JobFacade(owner_root, deployment)
        if args.command == "submit":
            request = _read_request(args.request_json)
            result = facade.submit(request)
        elif args.command == "get-status":
            result = facade.get_status(args.job_id)
        elif args.command == "act":
            result = facade.act(args.job_id, args.action)
        else:
            result = facade.list_jobs(args.limit)
        _emit(result)
        return 0
    except JobFacadeError as exc:
        return _emit_error(exc.code, exc.message)
    except json.JSONDecodeError:
        return _emit_error("request_invalid", "the request payload is not valid JSON")
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({"schema_version": "rf-job/1",
                          "error": {"code": "internal", "message": "owner job operation failed"}},
                         ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
