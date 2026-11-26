"""Owner endpoints and optional observations for durable RF feedback."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

from owner_atomic_io import native_path, open_regular_file, replace_file_bytes
from owner_file_lock import OwnerFileLock
from rf_assurance_history import get_run
from rf_feedback_outbox import flush, get_failure, publish, was_published
from rf_local_diagnostics import record_local_error


OWNER = "revenue-forecast"
JOB_SCHEMA = "rf-job/1"
REFERENCE = re.compile(r"rf-job/1/(rfjob-[A-Za-z0-9_-]{1,96})/((source|compute|publication)-[1-9][0-9]*)")
ASSURANCE_REFERENCE = re.compile(r"rf-assurance-run/1/(daily|weekly)/([0-9]{8}T[0-9]{12}Z-[0-9a-f]{32})")
CLI_REFERENCE = re.compile(r"rf-cli/1/([0-9a-f]{32})")
KEY = re.compile(r"[0-9a-f]{64}")
_CODE = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,128}")
_OBSERVATION_IDENTITY = ("owner", "origin_owner", "run_id", "attempt_id", "step_id", "check_id")
_EVIDENCE_READ_ERRORS = (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError, RuntimeError,
                         ArithmeticError, sqlite3.Error)


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


def _failure_reason(attempt: dict) -> str:
    observed = attempt.get("observations") or {}
    return observed.get("failure_reason") or attempt.get("failure_code") or f"stage_{attempt['status']}"


def _stage_outcome(row: dict, stage: str, status: str, reason: str | None = None) -> dict:
    result = dict(row, check_id="stage-outcome", expected="terminal", actual=status)
    if reason is not None:
        result.update(disposition="deviation" if status == "failed" else "unknown",
                      issue_key=f"{stage}/{reason}", reason=reason, details_ref=row["evidence_ref"])
    return result


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
        status = attempt["status"]
        reason = _failure_reason(attempt) if status in ("failed", "interrupted") else None
        row = _stage_outcome(row, attempt["stage"], status, reason)
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


def _observation(payload: dict) -> dict:
    row = payload.get("observation")
    if not isinstance(row, dict):
        raise ValueError("expected a feedback observation")
    return row


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


def _stage_attempt(
    owner_roots: Sequence[Path], row: dict, match: re.Match,
) -> tuple[tuple[dict, dict, dict] | None, str | None]:
    job_id, attempt_id, stage = match.groups()
    if row.get("owner") != OWNER or row.get("step_id") != f"{job_id}/{attempt_id}":
        return None, None
    view, reason = _read_configured_job(owner_roots, job_id)
    if view is None:
        return None, reason
    native = next((entry for entry in view["stages"] if entry["stage"] == stage), None)
    attempt = next((entry for entry in native["attempts"] if entry["attempt_id"] == attempt_id), None) if native else None
    if attempt is None or not _matches_attempt(job_id, attempt, row):
        return None, "native_attempt_mismatch"
    return (view, native, attempt), None


def _cli_failure(row: dict, identifier: str) -> dict | None:
    if row.get("owner") != OWNER:
        return None
    event = get_failure(identifier)
    if (event and event.get("id") == identifier
            and row.get("run_id") == event["run_id"] and row.get("attempt_id") == event["attempt_id"]
            and row.get("step_id") == event["entrypoint"] + "/" + event["id"]
            and type(event.get("exit_code")) is int and event["exit_code"] != 0):
        return event
    return None


def lookup(
    owner_root: Path, request: dict, *, additional_owner_roots: Sequence[Path] = (),
    assurance_ledgers: dict[str, Path] | None = None,
) -> dict:
    _, payload = _action(request, "reconcile", "lookup")
    return _lookup_observation((owner_root, *additional_owner_roots), _observation(payload), assurance_ledgers or {})


def _lookup_observation(owner_roots: Sequence[Path], row: dict, assurance_ledgers: dict[str, Path]) -> dict:
    ref = row.get("evidence_ref")
    assurance = ASSURANCE_REFERENCE.fullmatch(ref) if isinstance(ref, str) else None
    if assurance is not None:
        period, original_id = assurance.groups()
        ledger = assurance_ledgers.get(period)
        if ledger is None:
            ledgers = [root / "assurance" / "runs" / f"{period}_manifest.json"
                       for root in owner_roots]
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
    cli = CLI_REFERENCE.fullmatch(ref) if isinstance(ref, str) else None
    if cli is not None:
        event = _cli_failure(row, cli[1])
        if event is None:
            return {"state": "unknown"}
        effect = event["side_effect_state"]
        cost = "not_applicable" if effect == "not_started" else "unknown"
        return {"state": "done", "result": {
            "status": "cost_unknown" if cost == "unknown" else "known",
            "job_status": "failed", "cost_state": cost, "evidence_ref": ref,
            "native_code": event["native_code"], "side_effect_state": effect,
        }}
    match = REFERENCE.fullmatch(ref) if isinstance(ref, str) else None
    if match is None:
        return {"state": "unknown"}
    found, reason = _stage_attempt(owner_roots, row, match)
    if found is None:
        return {"state": "unknown", "code": reason} if reason else {"state": "unknown"}
    view, native, attempt = found
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


def lookup_batch(owner_roots: Sequence[Path], requests: object, assurance_ledgers: dict[str, Path]) -> list[dict]:
    if not isinstance(requests, list):
        raise ValueError("expected an array of reconcile requests")
    responses = []
    for request in requests:
        fields = request if isinstance(request, dict) else {}
        identity = {}
        for name in ("action_id", "request_digest"):
            value = fields.get(name)
            identity[name] = value if isinstance(value, str) and KEY.fullmatch(value) else None
        try:
            _, payload = _action(fields, "reconcile", "lookup")
            row = _observation(payload)
        except (KeyError, TypeError, ValueError, RecursionError):
            response = {"state": "failed", "code": "action_invalid"}
        else:
            try:
                # Original job status and cost are mutable. Each item reads the
                # owner again while sharing one interpreter startup.
                response = _lookup_observation(owner_roots, row, assurance_ledgers)
            except _EVIDENCE_READ_ERRORS:
                response = {"state": "unknown", "code": "native_status_unavailable"}
        responses.append({**identity, **response})
    return responses


def _triage_scope(request: dict) -> tuple[str, dict]:
    key, payload = _action(request, "triage", "submit")
    row = _observation(payload)
    normalized = {"origin_owner": row.get("owner"), **row}
    identity = [normalized.get(name) for name in _OBSERVATION_IDENTITY]
    if not all(isinstance(value, str) and value.strip() for value in identity):
        raise ValueError("missing original feedback identity")
    occurrence = digest(identity)
    if payload.get("occurrence_id") != occurrence or key != digest(["triage", OWNER, occurrence]):
        raise ValueError("triage identity mismatch")
    return key, row


def _triage_cli_failure(row: dict, identifier: str) -> tuple[dict, list[str]]:
    facts: dict = {"proof": "unavailable", "evidence_ref": row["evidence_ref"]}
    event = _cli_failure(row, identifier)
    if event is None or row.get("actual") != f"exit:{event['exit_code']}":
        return facts, ["original_cli_diagnostic"]
    reason = event.get("native_code")
    if (not isinstance(reason, str) or not _CODE.fullmatch(reason)
            or row.get("version") not in (None, event.get("code_version"))
            or row.get("issue_key") not in (None, f"{event['entrypoint']}/{reason}")):
        return facts, ["matching_cli_diagnostic"]
    effect = "not_started" if event.get("side_effect_state") == "not_started" else "unknown"
    cost = "not_applicable" if effect == "not_started" else "unknown"
    facts.update(proof="owner_diagnostic", outcome="failed", reason_code=reason,
                 exit_code=event["exit_code"], side_effect_state=effect, cost_state=cost)
    operation = event.get("operation")
    if isinstance(operation, str) and _CODE.fullmatch(operation):
        facts["operation"] = operation
    missing = ["original_request_context"]
    if effect == "unknown":
        missing.append("original_side_effect_record")
    return facts, missing


def _triage_stage_failure(
    owner_roots: Sequence[Path], row: dict, match: re.Match,
) -> tuple[dict, list[str]]:
    job_id, attempt_id, stage = match.groups()
    facts: dict = {"proof": "unavailable", "evidence_ref": row["evidence_ref"]}
    if (row.get("actual") != "failed" or row.get("expected") != "terminal"
            or row.get("step_id") != f"{job_id}/{attempt_id}" or row.get("version") not in (None, JOB_SCHEMA)):
        return facts, ["matching_stage_observation"]
    found, diagnostic = _stage_attempt(owner_roots, row, match)
    if found is not None:
        view, _, attempt = found
        if attempt["status"] == "failed":
            reason = _failure_reason(attempt)
            if isinstance(reason, str) and _CODE.fullmatch(reason) and row.get("issue_key") in (None, f"{stage}/{reason}"):
                cost = view["cost_state"]
                facts.update(proof="owner_job", outcome="failed", reason_code=reason,
                             cost_state=cost if cost in ("known", "not_applicable") else "unknown")
                return facts, ["original_stage_inputs"]
        diagnostic = "native_stage_mismatch"

    if diagnostic is not None:
        facts["lookup_code"] = diagnostic
    issue = row.get("issue_key")
    stage_prefix = stage + "/"
    if isinstance(issue, str) and issue.startswith(stage_prefix):
        reason = issue.removeprefix(stage_prefix)
        if _CODE.fullmatch(reason):
            original = _stage_outcome(
                _stage_observation(job_id, attempt_id, row["run_id"], row["attempt_id"]),
                stage, "failed", reason,
            )
            if row.get("details_ref") in (None, original["details_ref"]) and was_published(original):
                facts.update(proof="owner_observation", outcome="failed", reason_code=reason, cost_state="unknown")
    return facts, ["original_job_record"]


def _triage_result(owner_roots: Sequence[Path], key: str, row: dict, assurance_ledgers: dict[str, Path]) -> dict:
    facts: dict = {"proof": "unavailable"}
    missing = ["responsible_owner_evidence"]
    ref = row.get("evidence_ref")
    if isinstance(ref, str) and row.get("owner") == row.get("origin_owner", OWNER) == OWNER:
        try:
            if row["check_id"] == "process-outcome" and (cli := CLI_REFERENCE.fullmatch(ref)):
                facts, missing = _triage_cli_failure(row, cli[1])
            elif row["check_id"] == "stage-outcome" and (stage := REFERENCE.fullmatch(ref)):
                facts, missing = _triage_stage_failure(owner_roots, row, stage)
            elif row["check_id"] == "stage-outcome" and row.get("actual") == "failed" and ASSURANCE_REFERENCE.fullmatch(ref):
                receipt = _lookup_observation(owner_roots, row, assurance_ledgers)
                original = receipt.get("result", {})
                facts["evidence_ref"] = ref
                missing = ["original_assurance_run"]
                if original.get("job_status") == "failed":
                    facts.update(proof="owner_assurance", outcome="failed", reason_code="assurance_check_failed",
                                 cost_state=original["cost_state"], side_effect_state=original["side_effect_state"])
                    missing = ["original_assurance_check_context"]
        except _EVIDENCE_READ_ERRORS:
            missing = ["readable_owner_evidence"]
    issue = f"rf-feedback-triage/1/{key}"
    result = {"decision": "needs_evidence", "issue_ref": issue, "original_facts": facts,
              "next_missing_evidence": missing}
    if "refusal_code" in row:
        result["gate_review"] = {
            "decision": "needs_evidence",
            "reason": "Review the original rejection and a comparable valid input before changing the boundary.",
            "evidence_ref": facts.get("evidence_ref", issue),
        }
    return result


def get_triage(root: Path, key: str) -> dict:
    if not KEY.fullmatch(key):
        raise ValueError("invalid feedback action ID")
    with open_regular_file(root / f"triage-{key}.json") as stream:
        receipt = json.load(stream)
    stored, _ = _triage_scope(receipt["request"])
    result = receipt["result"]
    if (stored != key or not isinstance(result, dict) or result.get("decision") != "needs_evidence"
            or result.get("issue_ref") != f"rf-feedback-triage/1/{key}"):
        raise ValueError("invalid RF triage receipt")
    return {"receipt": receipt}


def record_triage(
    root: Path, owner_roots: Sequence[Path], request: dict, assurance_ledgers: dict[str, Path] | None = None,
) -> dict:
    key, row = _triage_scope(request)
    lock = OwnerFileLock(native_path(root / f"triage-{key}.lock"))
    if not lock.acquire():
        raise ValueError("triage is being recorded")
    try:
        try:
            receipt = get_triage(root, key)["receipt"]
        except FileNotFoundError:
            result = _triage_result(owner_roots, key, row, assurance_ledgers or {})
            receipt = {"request": request, "result": result}
            data = (json.dumps(receipt, ensure_ascii=True, sort_keys=True) + "\n").encode("ascii")
            replace_file_bytes(root / f"triage-{key}.json", data)
        if receipt["request"] != request:
            raise ValueError("conflicting triage for the same action")
        return {"result": receipt["result"]}
    finally:
        lock.release()


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
    for name in ("reconcile", "reconcile-batch", "triage"):
        command = commands.add_parser(name)
        command.add_argument("--owner-root", type=Path, action="append", required=True,
                             help="configured read-only RF owner root; repeat for known additional stores")
        command.add_argument("--assurance-ledger", nargs=2, action="append", default=[],
                             metavar=("PERIOD", "PATH"), help="explicit ledger for daily or weekly assurance")
        if name == "triage":
            command.add_argument("--reports-dir", type=Path, required=True)
    triage_get = commands.add_parser("get-triage")
    triage_get.add_argument("--reports-dir", type=Path, required=True)
    triage_get.add_argument("action_id")
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
        elif args.command in ("reconcile", "reconcile-batch", "triage"):
            ledgers = {period: Path(path) for period, path in args.assurance_ledger}
            request = json.load(sys.stdin)
            if args.command == "reconcile-batch":
                result = lookup_batch(args.owner_root, request, ledgers)
            elif args.command == "triage":
                result = record_triage(args.reports_dir, args.owner_root, request, ledgers)
            else:
                result = lookup(args.owner_root[0], request, additional_owner_roots=args.owner_root[1:],
                                assurance_ledgers=ledgers)
        elif args.command == "get-triage":
            result = get_triage(args.reports_dir, args.action_id)
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
