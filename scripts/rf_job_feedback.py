"""Owner endpoints and optional observations for durable RF feedback."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from owner_atomic_io import replace_file_bytes
from owner_file_lock import OwnerFileLock


OWNER = "revenue-forecast"
JOB_SCHEMA = "rf-job/1"
REFERENCE = re.compile(r"rf-job/1/(rfjob-[A-Za-z0-9_-]{1,96})/((source|compute|publication)-[1-9][0-9]*)")
KEY = re.compile(r"[0-9a-f]{64}")


def publish_attempt(job_id: str, attempt: dict, *, started: bool = False, cost_state: str | None = None) -> None:
    path = os.environ.get("RESEARCH_FEEDBACK_OUT")
    if not path:
        return
    attempt_id = attempt["attempt_id"]
    row = {
        "schema_version": "feedback-observation/1",
        "owner": OWNER,
        "run_id": os.environ.get("RESEARCH_FEEDBACK_RUN_ID") or job_id,
        "attempt_id": os.environ.get("RESEARCH_FEEDBACK_ATTEMPT_ID") or attempt_id,
        "step_id": f"{job_id}/{attempt_id}",
        "evidence_ref": f"{JOB_SCHEMA}/{job_id}/{attempt_id}",
        "version": JOB_SCHEMA,
        "disposition": "expected",
    }
    if cost_state is not None:
        row.update(check_id="job-usage", expected="accounted", actual=cost_state)
        if cost_state == "unknown":
            row["disposition"] = "unknown"
    elif started:
        row.update(check_id="action-started", expected="started", actual="started",
                   terminal_check_id="stage-outcome")
    else:
        row.update(check_id="stage-outcome", expected="terminal", actual=attempt["status"])
        if attempt["status"] == "interrupted":
            row["disposition"] = "unknown"
    try:
        with Path(path).open("ab") as out:
            out.write((json.dumps(row, ensure_ascii=True) + "\n").encode("ascii"))
            out.flush()
            os.fsync(out.fileno())
    except OSError:
        pass  # The durable job record remains authoritative.


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


def lookup(owner_root: Path, request: dict) -> dict:
    from rf_job_facade import JobFacade, JobFacadeError

    _, payload = _action(request, "reconcile", "lookup")
    row = payload["observation"]
    ref = row.get("evidence_ref")
    match = REFERENCE.fullmatch(ref) if isinstance(ref, str) else None
    if match is None:
        return {"state": "unknown"}
    job_id, attempt_id, stage = match.groups()
    if row.get("owner") != OWNER or row.get("step_id") != f"{job_id}/{attempt_id}":
        return {"state": "unknown"}
    try:
        view = JobFacade(owner_root, None).get_status(job_id)["job_view"]
    except JobFacadeError:
        return {"state": "unknown"}
    if view["status_known"] is not True:
        return {"state": "unknown"}
    native = next((entry for entry in view["stages"] if entry["stage"] == stage), None)
    if not native or not native["attempts"] or native["attempts"][-1]["attempt_id"] != attempt_id:
        return {"state": "unknown", "code": "native_attempt_mismatch"}
    if native["status"] == "running":
        return {"state": "pending"}
    if view["status"] not in ("succeeded", "failed", "cancelled", "interrupted"):
        return {"state": "pending"}
    cost = view["cost_state"]
    if cost not in ("known", "not_applicable", "unknown"):
        return {"state": "unknown"}
    return {"state": "done", "result": {
        "status": "cost_unknown" if cost == "unknown" else "known",
        "evidence_ref": ref, "job_status": view["status"], "cost_state": cost,
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
    commands.add_parser("reconcile").add_argument("--owner-root", type=Path, required=True)
    commands.add_parser("report").add_argument("--reports-dir", type=Path, required=True)
    get = commands.add_parser("get-report")
    get.add_argument("--reports-dir", type=Path, required=True)
    get.add_argument("action_id")
    args = parser.parse_args()
    try:
        if args.command == "reconcile":
            result = lookup(args.owner_root, json.load(sys.stdin))
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
