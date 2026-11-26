"""Owner endpoints and optional observations for durable RF feedback."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import hashlib
import json
from pathlib import Path
import re
import sys

from owner_atomic_io import native_path, replace_file_bytes
from owner_file_lock import OwnerFileLock
from rf_assurance_history import get_run
from rf_feedback_outbox import flush, get_failure, publish, was_published
from rf_local_diagnostics import record_local_error


OWNER = "revenue-forecast"
JOB_SCHEMA = "rf-job/1"
REFERENCE = re.compile(r"rf-job/1/(rfjob-[A-Za-z0-9_-]{1,96})/((source|compute|publication)-[1-9][0-9]*)")
ASSURANCE_REFERENCE = re.compile(r"rf-assurance-run/1/(daily|weekly)/([0-9]{8}T[0-9]{12}Z-[0-9a-f]{32})")
KEY = re.compile(r"[0-9a-f]{64}")


def _feedback_identity(job_id: str, attempt: dict) -> tuple[str, str]:
    return (
        attempt.get("feedback_run_id") or job_id,
        attempt.get("feedback_attempt_id") or attempt["attempt_id"],
    )


def _stage_observation(job_id: str, attempt_id: str, run_id: str, wrapper_attempt: str) -> dict:
    return {
        "schema_version": "feedback-observation/1",
        "owner": OWNER,
        "run_id": run_id,
        "attempt_id": wrapper_attempt,
        "step_id": f"{job_id}/{attempt_id}",
        "evidence_ref": f"{JOB_SCHEMA}/{job_id}/{attempt_id}",
        "version": JOB_SCHEMA,
        "disposition": "expected",
    }


def _started(row: dict) -> dict:
    return dict(row, check_id="action-started", expected="started", actual="started",
                terminal_check_id="stage-outcome")


def _matches_attempt(job_id: str, attempt: dict, observation: dict) -> bool:
    run_id, wrapper_attempt = observation.get("run_id"), observation.get("attempt_id")
    if (run_id, wrapper_attempt) == _feedback_identity(job_id, attempt):
        return True
    if attempt.get("feedback_run_id") is not None or attempt.get("feedback_attempt_id") is not None:
        return False
    if not isinstance(run_id, str) or not run_id or not isinstance(wrapper_attempt, str) or not wrapper_attempt:
        return False
    # A pre-metadata wrapper can be attributed only if its exact native stage
    # start is still in RF's outbox. The business outcome stays owner-verified.
    return was_published(_started(_stage_observation(job_id, attempt["attempt_id"], run_id, wrapper_attempt)))


def publish_attempt(job_id: str, attempt: dict, *, started: bool = False, cost_state: str | None = None) -> None:
    attempt_id = attempt["attempt_id"]
    row = _stage_observation(job_id, attempt_id, *_feedback_identity(job_id, attempt))
    if cost_state is not None:
        row.update(check_id="job-usage", expected="accounted", actual=cost_state)
        if cost_state == "unknown":
            row["disposition"] = "unknown"
    elif started:
        row = _started(row)
    else:
        row.update(check_id="stage-outcome", expected="terminal", actual=attempt["status"])
        if attempt["status"] in ("failed", "interrupted"):
            observed = attempt.get("observations") or {}
            reason = observed.get("failure_reason") or attempt.get("failure_code") or f"stage_{attempt['status']}"
            row.update(disposition="deviation" if attempt["status"] == "failed" else "unknown",
                       issue_key=f"{attempt['stage']}/{reason}", reason=reason, details_ref=row["evidence_ref"])
    try:
        publish(row)
    except (OSError, TypeError, ValueError, RuntimeError) as exc:
        record_local_error("rf_job_feedback", code="attempt_delivery_unavailable",
                           job_id=job_id, attempt_id=attempt_id, exception_type=type(exc).__name__)


def digest(value) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def _action(request: dict, kind: str, method: str) -> tuple[str, dict]:
    if (request["schema_version"], request["owner"], request["kind"], request["method"]) != (
        "feedback-action/1", OWNER, kind, method,
    ):
        raise ValueError("unexpected feedback action")
    key, payload = request["action_id"], request["payload"]
    if (not KEY.fullmatch(key) or not isinstance(payload, dict)
            or request["request_digest"] != digest([OWNER, kind, key, payload])):
        raise ValueError("feedback action identity mismatch")
    return key, payload


def _job_proof(view: dict) -> tuple:
    # Compare the original scope, attempt lineage, output bytes and settlement.
    # Presentation and allowed-action fields do not establish replica identity.
    return tuple(view[key] for key in (
        "owner_job_id", "scope", "created_at", "stages", "result", "status", "cost_state", "cost",
    ))


def _read_configured_job(owner_roots: Sequence[Path], job_id: str) -> tuple[dict | None, str | None]:
    from rf_job_facade import JobFacade, JobFacadeError

    try:
        roots = dict.fromkeys(native_path(root).resolve() for root in owner_roots)
    except (OSError, RuntimeError):
        return None, "native_owner_unverified"

    observed = []
    unverified = False
    for root in roots:
        try:
            view = JobFacade(root, None).get_status(job_id)["job_view"]
        except JobFacadeError as exc:
            if exc.code != "owner_job_not_found":
                unverified = True
            continue
        except OSError:
            unverified = True
            continue
        if view["status_known"] is True:
            observed.append(view)
        else:
            unverified = True

    if unverified:
        return None, "native_owner_unverified"
    if not observed:
        return None, None
    first = observed[0]
    if any(_job_proof(view) != _job_proof(first) for view in observed[1:]):
        return None, "native_owner_conflict"
    return first, None


def lookup(
    owner_root: Path, request: dict, *, additional_owner_roots: Sequence[Path] = (),
    assurance_ledgers: dict[str, Path] | None = None,
) -> dict:
    _, payload = _action(request, "reconcile", "lookup")
    row = payload["observation"]
    ref = row.get("evidence_ref")
    assurance = ASSURANCE_REFERENCE.fullmatch(ref) if isinstance(ref, str) else None
    if assurance is not None:
        period, original_id = assurance.groups()
        ledger = (assurance_ledgers or {}).get(period)
        if ledger is None:
            ledgers = [root / "assurance" / "runs" / f"{period}_manifest.json"
                       for root in (owner_root, *additional_owner_roots)]
        else:
            ledgers = [ledger]
        records = [record for file in dict.fromkeys(ledgers) if (record := get_run(file, period, original_id))]
        record = records[0] if records else None
        if any(other != record for other in records[1:]):
            return {"state": "unknown", "code": "native_owner_conflict"}
        if (record is None or row.get("owner") != OWNER
                or row.get("step_id") != f"assurance/{period}/{original_id}"
                or row.get("run_id") != record["feedback_run_id"]
                or row.get("attempt_id") != record["feedback_attempt_id"]):
            return {"state": "unknown"}
        if record["state"] == "started":
            return {"state": "pending"}
        if record["state"] in ("completed", "failed"):
            return {"state": "done", "result": {
                "status": "known", "job_status": "succeeded" if record["state"] == "completed" else "failed",
                "evidence_ref": ref, "cost_state": "not_applicable", "side_effect_state": "read_only",
            }}
        return {"state": "unknown"}
    if isinstance(ref, str) and re.fullmatch(r"rf-cli/1/[0-9a-f]{32}", ref) and row.get("owner") == OWNER:
        event = get_failure(ref.rsplit("/", 1)[1])
        if (event and row.get("run_id") == event["run_id"] and row.get("attempt_id") == event["attempt_id"]
                and row.get("step_id") == event["entrypoint"] + "/" + event["id"]):
            code = event.get("exit_code")
            if type(code) is int and code != 0:
                effect = event["side_effect_state"]
                cost = "not_applicable" if effect == "not_started" else "unknown"
                return {"state": "done", "result": {
                    "status": "cost_unknown" if cost == "unknown" else "known",
                    "job_status": "failed", "cost_state": cost, "evidence_ref": ref,
                    "native_code": event["native_code"], "side_effect_state": effect,
                }}
        return {"state": "unknown"}
    match = REFERENCE.fullmatch(ref) if isinstance(ref, str) else None
    if match is None:
        return {"state": "unknown"}
    job_id, attempt_id, stage = match.groups()
    if row.get("owner") != OWNER or row.get("step_id") != f"{job_id}/{attempt_id}":
        return {"state": "unknown"}

    view, reason = _read_configured_job((owner_root, *additional_owner_roots), job_id)
    if view is None:
        return {"state": "unknown", "code": reason} if reason else {"state": "unknown"}
    native = next((entry for entry in view["stages"] if entry["stage"] == stage), None)
    attempt = next((entry for entry in native["attempts"] if entry["attempt_id"] == attempt_id), None) if native else None
    if attempt is None or not _matches_attempt(job_id, attempt, row):
        return {"state": "unknown", "code": "native_attempt_mismatch"}
    # An interrupted old stage remains interrupted when a newer stage has
    # succeeded. A read-only check may discover the interruption before repair.
    outcome = attempt["status"]
    if outcome == "running" and native["status"] == "interrupted" and native["attempts"][-1] is attempt:
        outcome = "interrupted"
    if outcome == "running":
        return {"state": "pending"}
    status = outcome if outcome in ("failed", "interrupted") and row.get("check_id") != "job-usage" else view["status"]
    if status not in ("succeeded", "failed", "cancelled", "interrupted"):
        return {"state": "pending"}
    cost = "unknown" if outcome == "interrupted" else view["cost_state"]
    if cost not in ("known", "not_applicable", "unknown"):
        return {"state": "unknown"}
    return {"state": "done", "result": {
        "status": "cost_unknown" if cost == "unknown" else "known",
        "evidence_ref": ref, "job_status": status, "cost_state": cost,
    }}


def record_report(root: Path, request: dict) -> dict:
    key, payload = _action(request, "report", "submit")
    names = ("occurrence_id", "original_occurrence_id", "origin_owner", "issue_ref", "fixed_version", "evidence_ref")
    if (payload.get("verdict") not in ("verified", "regressed")
            or any(not isinstance(payload.get(name), str) or not payload[name].strip() for name in names)):
        raise ValueError("expected a bound consumer replay result")
    scope = [payload["occurrence_id"], OWNER, payload["issue_ref"], payload["fixed_version"], payload["verdict"]]
    if key != digest(["report", OWNER, *scope]):
        raise ValueError("report identity mismatch")
    path = root / f"{key}.json"
    data = (json.dumps(request, ensure_ascii=True, sort_keys=True) + "\n").encode("ascii")
    lock = OwnerFileLock(root / f"{key}.lock")
    if not lock.acquire():
        raise ValueError("report is being recorded")
    try:
        if path.is_file():
            if path.read_bytes() != data:
                raise ValueError("conflicting report for the same action")
        else:
            replace_file_bytes(path, data)
    finally:
        lock.release()
    return {"result": {"recorded": True}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("flush-feedback")
    commands.add_parser("get-failure").add_argument("identifier")
    reconcile = commands.add_parser("reconcile")
    reconcile.add_argument(
        "--owner-root", type=Path, action="append", required=True,
        help="configured read-only RF owner root; repeat for known additional stores",
    )
    reconcile.add_argument("--assurance-ledger", nargs=2, action="append", default=[],
                           metavar=("PERIOD", "PATH"), help="explicit ledger for daily or weekly assurance")
    commands.add_parser("report").add_argument("--reports-dir", type=Path, required=True)
    get = commands.add_parser("get-report")
    get.add_argument("--reports-dir", type=Path, required=True)
    get.add_argument("action_id")
    args = parser.parse_args()
    try:
        if args.command == "flush-feedback":
            result = flush()
        elif args.command == "get-failure":
            result = get_failure(args.identifier)
            if result is None:
                raise ValueError("unknown RF feedback occurrence")
        elif args.command == "reconcile":
            ledgers = {period: Path(path) for period, path in args.assurance_ledger}
            result = lookup(args.owner_root[0], json.load(sys.stdin), additional_owner_roots=args.owner_root[1:],
                            assurance_ledgers=ledgers)
        elif args.command == "report":
            result = record_report(args.reports_dir, json.load(sys.stdin))
        else:
            if not KEY.fullmatch(args.action_id):
                raise ValueError("invalid feedback action ID")
            result = {"report": json.loads((args.reports_dir / f"{args.action_id}.json").read_bytes())}
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": type(error).__name__}))
        return 1
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
