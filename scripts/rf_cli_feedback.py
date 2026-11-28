"""One per-invocation RF failure boundary, before parsing and without machine stream side effects."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from uuid import NAMESPACE_URL, uuid4, uuid5

from rf_feedback_outbox import Delivery, flush, publish_outcome
from rf_local_diagnostics import record_local_error, redact_text, source_version, traceback_facts, warn_local_failure

_CODE = re.compile(r"[a-zA-Z][a-zA-Z0-9_.-]{0,128}")
_PROJECTION_VERSION = "rf-cli-outcome/1"


class DiagnosticParser(argparse.ArgumentParser):
    """Keep argparse's public usage, codes and option handling with safe diagnostics."""

    def error(self, message):
        super().error(redact_text(message))


@dataclass
class Invocation:
    source: Path
    request_ref: str
    machine_stderr: bool
    publish_feedback: bool
    native_code: str = "cli_failed"
    kind: str = "failure"
    effect: str = "unknown"
    stage: str = "argument-parsing"
    operation: str | None = None
    producer_exit_code: int | None = None
    cause_chain: list[dict] = field(default_factory=list)
    transport_facts: dict = field(default_factory=dict)

    def note_input(self, data: bytes | str) -> None:
        """Link the consumed input while keeping its content out of diagnostics."""
        payload = data if isinstance(data, bytes) else data.encode("utf-8", errors="surrogatepass")
        self.request_ref = "sha256:" + hashlib.sha256(payload).hexdigest()

    def note_operation(self, operation: str, *, external_work_possible: bool) -> None:
        self.operation = operation
        self.stage = operation
        if not external_work_possible:
            self.effect = "not_started"

    def note_native(self, code: str, *, kind: str = "failure", effect: str | None = None,
                    producer_exit_code: int | None = None, error: BaseException | None = None) -> None:
        """Detach the active exception without copying its values or keeping its frames live."""
        if not isinstance(code, str) or not _CODE.fullmatch(code):
            return
        self.native_code, self.kind = code, kind
        if effect is not None and self.effect != "not_started":
            self.effect = effect
        self.cause_chain = traceback_facts(error if error is not None else sys.exc_info()[1])
        if type(producer_exit_code) is int:
            self.producer_exit_code = producer_exit_code


def _stage_owns_terminal(entry, parent):
    receipt = os.environ.get("RF_JOB_ACTIVE_RECORD")
    match = re.fullmatch(r"(rfjob-[A-Za-z0-9_-]+)/((source|compute|publication)-[1-9][0-9]*)", parent)
    if not receipt or not match:
        return False
    job_id, attempt_id, stage = match.groups()
    if {"source": "source_preparation", "compute": "revenue_forecast", "publication": "publication_registry"}[stage] != entry:
        return False
    try:
        path = Path(receipt)
        if path.name != "job.json" or path.parent.name != job_id:
            return False
        record = json.loads(path.read_bytes())
        native = record["stages"][stage]["attempts"][-1]
        return record["owner_job_id"] == job_id and native["attempt_id"] == attempt_id and native["status"] == "running"
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return False


def _invocation_detail(invocation: Invocation, code: int, parent: str) -> dict:
    source = invocation.source
    entry = source.stem
    version = source_version(source)
    supplied_run = os.environ.get("RESEARCH_FEEDBACK_RUN_ID", "").strip()
    supplied_attempt = os.environ.get("RESEARCH_FEEDBACK_ATTEMPT_ID", "").strip()
    key = (uuid5(NAMESPACE_URL, repr((supplied_run, supplied_attempt, parent, entry))).hex
           if parent and supplied_run and supplied_attempt else uuid4().hex)
    run = supplied_run or "rf-cli-" + key
    attempt = supplied_attempt or key
    reason, kind = invocation.native_code, invocation.kind
    chain = invocation.cause_chain or [{"type": reason, "file": source.name}]
    detail = {"id": key, "entrypoint": entry, "native_code": reason, "classification": kind, "exit_code": code,
              "run_id": run, "attempt_id": attempt, "cause_chain": chain, "code_version": version,
              "side_effect_state": invocation.effect, "stage": invocation.stage, "input_ref": invocation.request_ref}
    if invocation.operation is not None:
        detail["operation"] = invocation.operation
    if invocation.producer_exit_code is not None:
        detail["producer_exit_code"] = invocation.producer_exit_code
    return detail


def _publish_invocation(detail: dict, parent: str) -> Delivery:
    key, entry, reason = detail["id"], detail["entrypoint"], detail["native_code"]
    ref = "rf-cli/1/" + key
    row = {"schema_version": "feedback-observation/1", "owner": "revenue-forecast", "run_id": detail["run_id"],
           "attempt_id": detail["attempt_id"], "step_id": entry + "/" + key, "check_id": "process-outcome",
           "expected": "exit:0", "actual": f"exit:{detail['exit_code']}", "disposition": "deviation",
           "reason": reason, "issue_key": entry + "/" + reason, "version": detail["code_version"] or _PROJECTION_VERSION,
           "details_ref": ref, "evidence_ref": ref}
    if parent:
        row["parent_step_id"] = parent
    if _stage_owns_terminal(entry, parent):
        row.update(check_id="stage-native-evidence", expected="recorded", actual="recorded", disposition="expected")
    elif detail["classification"] == "refusal":
        row["refusal_code"] = reason.lower()
    return publish_outcome(row, detail)


def _observe(invocation: Invocation, code: int) -> None:
    parent = os.environ.get("RESEARCH_FEEDBACK_PROCESS_STEP_ID", "").strip()
    detail = _invocation_detail(invocation, code, parent)
    delivery = _publish_invocation(detail, parent) if invocation.publish_feedback else Delivery(False)
    local = {"operation": detail["entrypoint"], **detail, **invocation.transport_facts}
    if delivery.code is not None:
        local.update(operation="feedback_delivery", code=delivery.code, delivery_cause_chain=delivery.cause_chain)
    if not record_local_error(**local) and not delivery.durable and not invocation.machine_stderr:
        warn_local_failure("entry")


def _request_ref(argv: object) -> str:
    items = argv if isinstance(argv, (list, tuple)) else []
    encoded = json.dumps([redact_text(value) for value in items if isinstance(value, str)], ensure_ascii=True)
    return "sha256:" + hashlib.sha256(encoded.encode("ascii")).hexdigest()


def _resume_delivery() -> None:
    try:
        flush()
    except Exception as exc:
        record_local_error("feedback_flush", code="flush_unavailable", cause_chain=traceback_facts(exc))


def _record_failure(invocation: Invocation, code: int) -> None:
    if not code:
        return
    try:
        _observe(invocation, code)
    except Exception as exc:
        saved = record_local_error("feedback_observation", code="observe_unavailable",
                                   cause_chain=traceback_facts(exc))
        if not saved and not invocation.machine_stderr:
            warn_local_failure("entry")


def _run_entry(entry, invocation: Invocation, args: tuple, kwargs: dict):
    code = 1
    try:
        result = entry(*args, **kwargs, runtime=invocation)
        code = result or 0
        return result
    except SystemExit as exc:
        code = exc.code if type(exc.code) is int else int(exc.code is not None)
        if code and invocation.native_code == "cli_failed":
            invocation.note_native("invalid_arguments", kind="refusal", effect="not_started", error=exc)
        raise
    except KeyboardInterrupt as exc:
        code = 130
        invocation.note_native("KeyboardInterrupt", error=exc)
        raise
    except Exception as exc:
        invocation.note_native(type(exc).__name__, error=exc)
        raise
    finally:
        _record_failure(invocation, code)


def observed_entry(callback=None, *, machine_stderr: bool = False, owner: bool = False):
    """Bind this invocation's native facts without shared logger state or feedback recursion."""
    def decorate(entry):
        @wraps(entry)
        def run(*args, **kwargs):
            supplied = args[0] if args else kwargs.get("argv")
            inv = Invocation(Path(entry.__code__.co_filename),
                             _request_ref(sys.argv[1:] if supplied is None else supplied),
                             machine_stderr, not owner)
            if not owner:
                _resume_delivery()
            return _run_entry(entry, inv, args, kwargs)
        return run
    return decorate if callback is None else decorate(callback)


def exit_cli(entry) -> int:
    """Python's unhandled-exception exit, with safe diagnostics owned by the entry."""
    try:
        return entry()
    except KeyboardInterrupt:
        return 130
    except Exception as error:
        if sys.stderr is not None:
            sys.stderr.write(f"error: {type(error).__name__}\n")
        return 1
