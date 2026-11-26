"""Durable owner history for RF's read-only scheduled assurance operations."""

from datetime import UTC, datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
from uuid import uuid4

from owner_atomic_io import native_path, replace_file_bytes
from rf_feedback_outbox import publish

_RUN_ID = re.compile(r"[0-9]{8}T[0-9]{12}Z-[0-9a-f]{32}")


def path_reference(path: Path) -> str:
    """Identify a configured path without copying its location or file contents."""
    return "sha256:" + sha256(str(path.absolute()).encode("utf-8")).hexdigest()


def _directory(ledger: Path, period: str) -> Path:
    return native_path(ledger.parent / "history" / ledger.name / period)


def write_json(path: Path, body: dict) -> None:
    replace_file_bytes(path, (json.dumps(body, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii"))


class AssuranceRun:
    def __init__(self, ledger: Path, period: str, *, sources: tuple[Path, ...], request: dict):
        now = datetime.now(UTC)
        self.run_id = f"{now.strftime('%Y%m%dT%H%M%S%fZ')}-{uuid4().hex}"
        self.path = _directory(ledger, period) / f"{self.run_id}.json"
        version = sha256()
        try:
            for source in sources:
                version.update(source.name.encode("utf-8") + b"\x00")
                version.update(sha256(source.read_bytes()).digest())
        except OSError:
            code_version = None
        else:
            code_version = version.hexdigest()
        self.body = {
            "schema_version": "rf-assurance-run/1", "period": period, "run_id": self.run_id,
            "started_at": now.isoformat(), "ended_at": None, "exit_code": None,
            "request": request, "code_version": code_version, "state": "started",
            "step": "owner_read", "effect": "read_only",
            "feedback_run_id": (os.environ.get("RESEARCH_FEEDBACK_RUN_ID") or "").strip() or self.run_id,
            "feedback_attempt_id": (os.environ.get("RESEARCH_FEEDBACK_ATTEMPT_ID") or "").strip() or self.run_id,
        }
        self._save()

    def finish(self, *, exit_code: int, outcome: str, diagnostic: dict) -> None:
        self.body.update(ended_at=datetime.now(UTC).isoformat(), exit_code=exit_code,
                         state="failed" if exit_code else "completed", outcome=outcome,
                         diagnostic=diagnostic, step="owner_read_finished")
        self._save()

    def _save(self) -> None:
        try:
            write_json(self.path, self.body)
        except OSError as exc:
            print(f"warning: RF assurance history {self.run_id} is unavailable ({type(exc).__name__})",
                  file=sys.stderr)
            return
        self._project()

    def _project(self) -> None:
        period, state = self.body["period"], self.body["state"]
        ref = f"rf-assurance-run/1/{period}/{self.run_id}"
        row = {
            "schema_version": "feedback-observation/1", "owner": "revenue-forecast",
            "run_id": self.body["feedback_run_id"], "attempt_id": self.body["feedback_attempt_id"],
            "step_id": f"assurance/{period}/{self.run_id}",
            "version": self.body["code_version"] or "rf-assurance-run/1",
            "evidence_ref": ref, "disposition": "expected",
        }
        if state == "started":
            row.update(check_id="action-started", expected="started", actual="started",
                       terminal_check_id="stage-outcome")
        else:
            row.update(check_id="stage-outcome", expected="terminal", actual=state)
            if state == "failed":
                row.update(disposition="deviation", reason="assurance_check_failed",
                           issue_key=f"assurance/{period}", details_ref=ref)
        try:
            publish(row)
        except (OSError, TypeError, ValueError, RuntimeError) as exc:
            print(f"warning: RF assurance feedback {self.run_id} is unavailable ({type(exc).__name__})",
                  file=sys.stderr)


def get_run(ledger: Path, period: str, run_id: str | None = None) -> dict | None:
    directory = _directory(ledger, period)
    if run_id is None:
        latest = max((path.stem for path in directory.glob("*.json") if _RUN_ID.fullmatch(path.stem)), default=None)
        if latest is None:
            return None
        run_id = latest
    if not _RUN_ID.fullmatch(run_id):
        return None
    try:
        body = json.loads((directory / f"{run_id}.json").read_bytes())
    except (OSError, ValueError):
        return None
    if not isinstance(body, dict) or body.get("run_id") != run_id or body.get("period") != period:
        return None
    return body


def show_run(ledger: Path, period: str, run_id: str | None) -> int:
    body = get_run(ledger, period, run_id)
    print(json.dumps(body if body is not None else {"state": "missing"}, ensure_ascii=True))
    return 0 if body is not None else 1
