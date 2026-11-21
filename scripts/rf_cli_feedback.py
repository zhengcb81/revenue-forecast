"""Observe RF's public process exit, keeping the native reason and code location out of argv or stdin."""
from __future__ import annotations

from contextvars import ContextVar
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from uuid import NAMESPACE_URL, uuid4, uuid5

from rf_feedback_outbox import flush, publish

_CURRENT = ContextVar("rf_feedback_invocation", default=None)
_ROOT = Path(__file__).resolve().parent
_CODE = re.compile(r"[a-zA-Z][a-zA-Z0-9_.-]{0,128}")


def note_native(code, *, kind="failure", effect="unknown"):
    """Called by the entry that owns the native return code; never copy arbitrary exception messages."""
    state = _CURRENT.get()
    if state is not None and isinstance(code, str) and _CODE.fullmatch(code):
        state.update(native_code=code, kind=kind, side_effect_state=effect, error=sys.exc_info()[1])


def _chain(error):
    chain, seen = [], set()
    while isinstance(error, BaseException) and id(error) not in seen:
        seen.add(id(error))
        item = {"type": type(error).__name__}
        # Read the built-in exception state. Domain exceptions can override arbitrary
        # attributes with properties that throw exceptions of their own.
        tb = BaseException.__traceback__.__get__(error)
        while tb is not None:
            path = Path(tb.tb_frame.f_code.co_filename)
            if path.parent == _ROOT:
                item.update(file=path.name, line=tb.tb_lineno, function=tb.tb_frame.f_code.co_name)
            tb = tb.tb_next
        if type(error) is json.JSONDecodeError:
            item.update(input_line=error.lineno, input_column=error.colno)
        if isinstance(error, OSError):
            errno = OSError.errno.__get__(error)
            if isinstance(errno, int):
                item["errno"] = errno
        chain.append(item)
        cause = BaseException.__cause__.__get__(error)
        context = None if BaseException.__suppress_context__.__get__(error) else BaseException.__context__.__get__(error)
        error = cause if cause is not None else context
    return chain


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


def _observe(state, code):
    entry = state["entrypoint"]
    source = _ROOT / (entry + ".py")
    version = hashlib.sha256(source.read_bytes()).hexdigest()
    parent = (os.environ.get("RESEARCH_FEEDBACK_PROCESS_STEP_ID") or "").strip()
    supplied_run = (os.environ.get("RESEARCH_FEEDBACK_RUN_ID") or "").strip()
    supplied_attempt = (os.environ.get("RESEARCH_FEEDBACK_ATTEMPT_ID") or "").strip()
    key = (uuid5(NAMESPACE_URL, repr((supplied_run, supplied_attempt, parent, entry))).hex
           if parent and supplied_run and supplied_attempt else uuid4().hex)
    run = supplied_run or "rf-cli-" + key
    attempt = supplied_attempt or key
    reason, kind = state["native_code"], state["kind"]
    ref = "rf-cli/1/" + key
    chain = _chain(state.get("error")) or [{"type": reason, "file": source.name}]
    detail = {"id": key, "entrypoint": entry, "native_code": reason, "classification": kind, "exit_code": code,
              "run_id": run, "attempt_id": attempt, "cause_chain": chain, "code_version": version,
              "side_effect_state": state["side_effect_state"]}
    row = {"schema_version": "feedback-observation/1", "owner": "revenue-forecast", "run_id": run,
           "attempt_id": attempt, "step_id": entry + "/" + key, "check_id": "process-outcome",
           "expected": "exit:0", "actual": f"exit:{code}", "disposition": "deviation",
           "reason": reason, "issue_key": entry + "/" + reason, "version": version,
           "details_ref": ref, "evidence_ref": ref}
    if parent:
        row["parent_step_id"] = parent
    if _stage_owns_terminal(entry, parent):
        # The verified native attempt is responsible for the actionable terminal event.
        # Preserve the child's actual exit, origin, traceback and cause in its durable details.
        row.update(check_id="stage-native-evidence", expected="recorded", actual="recorded", disposition="expected")
    elif kind == "refusal":
        row["refusal_code"] = reason.lower()
    publish(row, detail)


def observed_entry(callback):
    @wraps(callback)
    def run(*args, **kwargs):
        try:
            flush()
        except Exception:
            pass  # Recovering optional delivery may never change the operation about to run.
        entry = Path(callback.__code__.co_filename).stem
        state = {"entrypoint": entry, "kind": "failure", "native_code": "cli_failed", "side_effect_state": "unknown"}
        token = _CURRENT.set(state)
        code = 1
        try:
            result = callback(*args, **kwargs)
            code = result or 0
            return result
        except SystemExit as exc:
            code = exc.code if type(exc.code) is int else int(exc.code is not None)
            if code:
                note_native("invalid_arguments", kind="refusal", effect="not_started")
            raise
        except Exception as exc:
            note_native(type(exc).__name__)
            raise
        finally:
            try:
                if code:
                    _observe(state, code)
            except Exception:
                pass  # The observed return or thrown exception always remains authoritative.
            finally:
                _CURRENT.reset(token)
    return run
