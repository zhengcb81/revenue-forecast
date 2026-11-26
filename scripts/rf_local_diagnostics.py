"""Persist RF-owned failure facts separately from its machine streams."""

from __future__ import annotations

import builtins
from datetime import datetime, timezone
from errno import errorcode
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import re
from typing import Any

from owner_atomic_io import native_path
from owner_file_lock import OwnerFileLock


_TAIL_LENGTH = 16 * 1024
_TRACEBACK = "Traceback (most recent call last):"
_FRAME = re.compile(r'^  File "([^"]+)", line ([0-9]+)')
_ERROR_LINE = re.compile(
    r"^([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)(?::(?=\s|$)(?: \[Errno ([0-9]{1,5})\])?|$)",
    re.ASCII,
)


def state_dir() -> Path:
    parent = os.environ.get("LOCALAPPDATA") if os.name == "nt" else os.environ.get("XDG_STATE_HOME")
    return (Path(parent) if parent else Path.home() / ".local/state") / "revenue-forecast"


def child_traceback_facts(stderr: str | None, *, source: str | None = None) -> list[dict[str, str | int]]:
    """Read exception structure from the tail without retaining untrusted text."""
    if not stderr:
        return []
    facts: list[dict[str, str | int]] = []
    in_trace = saw_frame = False
    frame_line = None
    for line in stderr[-_TAIL_LENGTH:].splitlines():
        if line == _TRACEBACK:
            in_trace = True
            saw_frame = False
            frame_line = None
        elif in_trace and line.startswith("  File "):
            saw_frame = True
            frame = _FRAME.match(line)
            if source is not None and frame and frame[1].replace("\\", "/").rsplit("/", 1)[-1] == source:
                frame_line = int(frame[2])
        elif in_trace and saw_frame and (match := _ERROR_LINE.match(line)):
            name, raw_errno = match.groups()
            if len(name) <= 96:
                fact: dict[str, str | int] = {"type": name}
                exception = getattr(builtins, name, None)
                if (isinstance(exception, type) and issubclass(exception, OSError)
                        and raw_errno and int(raw_errno) in errorcode):
                    fact["errno"] = int(raw_errno)
                if source is not None and frame_line is not None:
                    fact.update(file=source, line=frame_line)
                facts.append(fact)
            in_trace = False
    return facts


class _FileOnlyHandler(RotatingFileHandler):
    def handleError(self, record: logging.LogRecord) -> None:
        # A broken diagnostic destination must not append text to the CLI's JSON stderr.
        raise


def record_local_error(operation: str, **facts: Any) -> None:
    """Append structured facts supplied by the owner; logging is best effort."""
    try:
        path = native_path(state_dir() / "logs" / "runtime-errors.jsonl")
        lock = OwnerFileLock(path.with_suffix(".lock"))
        if not lock.acquire():
            return
        try:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "operation": operation,
                "run_id": os.environ.get("RESEARCH_FEEDBACK_RUN_ID"),
                **facts,
            }
            handler = _FileOnlyHandler(path, maxBytes=1024 * 1024, backupCount=2, encoding="utf-8")
            try:
                handler.emit(logging.LogRecord(
                    __name__, logging.ERROR, __file__, 0, json.dumps(entry, ensure_ascii=True), (), None,
                ))
            finally:
                handler.close()
        finally:
            lock.release()
    except (OSError, TypeError, ValueError, RuntimeError):
        pass
