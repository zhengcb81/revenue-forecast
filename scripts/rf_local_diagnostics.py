"""Persist RF-owned failure facts separately from its machine streams."""

from __future__ import annotations

import builtins

from datetime import datetime, timezone
from errno import errorcode
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from time import monotonic, sleep
from typing import Any

from owner_atomic_io import native_path, open_regular_file, separate_partial_line
from owner_file_lock import OwnerFileLock


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
    for line in stderr.splitlines():
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



_LOG_BYTES = 1024 * 1024
_LOG_LOCK_WAIT = 1.0
_AUTH = re.compile(
    r"(?i)\b(bearer|basic)(?:[ \t]+|\r?\n[ \t]+)(?:\r?\n[ \t]+)*"
    r"[^\s,;\"'<>]+(?:[ \t]*\r?\n[ \t]+[^\r\n]*)*"
)
_COOKIE = re.compile(r"(?im)(\b(?:set-cookie|cookie)[\"']?\s*:\s*)[^\r\n]*(?:\r?\n[ \t]+[^\r\n]*)*")
_USERINFO = re.compile(r"(?i)(https?://)[^/@\s\"'<>]+@")
_CREDENTIAL = re.compile(
    r"(?i)(\b(?:[\w-]*[-_])?(?:api[-_]?key|token|password|secret|credential)\b[\"']?\s*[:=]\s*)"
    r"(?:\"[^\"]*\"|'[^']*'|[^\s&,;<>]+)"
)
_CLI_SECRET = re.compile(r"(?i)(--(?:[\w-]*[-_])?(?:api[-_]?key|token|password|secret|credential)\b[\s=]+)[^\s,<>]+")
_PREFIX = re.compile(r"(?<![\w])(?:sk-|tvly-|ghp_|AIza)[A-Za-z0-9_-]{8,}")
_SENSITIVE_FIELDS = re.compile(
    r"(?i)(?:authorization|proxy-authorization|cookie|set-cookie|(?:[\w-]*[-_])?"
    r"(?:api[-_]?key|token|password|secret|credential))"
)
_SYMBOL = re.compile(r"(?:[\w.<>-]{1,160}|<frozen [\w.]{1,120}>)", re.ASCII)


def redact_text(value: str) -> str:
    value = _AUTH.sub(r"\1 [REDACTED]", value)
    value = _COOKIE.sub(r"\1[REDACTED]", value)
    value = _USERINFO.sub(r"\1[REDACTED]@", value)
    value = _CREDENTIAL.sub(r"\1[REDACTED]", value)
    value = _CLI_SECRET.sub(r"\1[REDACTED]", value)
    return _PREFIX.sub("[REDACTED]", value)


def redact_facts(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {redact_text(key) if isinstance(key, str) else key:
                "[REDACTED]" if isinstance(key, str) and _SENSITIVE_FIELDS.fullmatch(key) else redact_facts(item)
                for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact_facts(item) for item in value]
    return value


def public_reference(value: str, kind: str) -> str:
    if redact_text(value) == value:
        return value
    return f"{kind}-{hashlib.sha256(value.encode('utf-8', errors='surrogatepass')).hexdigest()[:16]}"


def same_reference(left: object, right: object, kind: str) -> bool:
    return (isinstance(left, str) and isinstance(right, str)
            and public_reference(left, kind) == public_reference(right, kind))


def public_diagnostic(row: dict) -> dict:
    """Sanitize diagnostic values without changing ordinary occurrence IDs."""
    projected = redact_facts(row)
    for field, kind in (("run_id", "run"), ("attempt_id", "attempt"), ("step_id", "step"),
                        ("parent_step_id", "step")):
        value = row.get(field)
        if isinstance(value, str):
            projected[field] = public_reference(value, kind)
    return projected


def source_version(path: Path) -> str | None:
    try:
        return hashlib.sha256(native_path(path).read_bytes()).hexdigest()
    except (OSError, ValueError):
        return None


def _include_frames(item: dict, error: BaseException, root: Path) -> None:
    frames = []
    trace = BaseException.__traceback__.__get__(error)
    while trace is not None:
        code = trace.tb_frame.f_code
        path = Path(code.co_filename)
        if _SYMBOL.fullmatch(path.name) and _SYMBOL.fullmatch(code.co_name):
            local = path.is_absolute() and path.is_relative_to(root)
            frame = {
                "file": path.relative_to(root).as_posix().removeprefix("scripts/") if local else path.name,
                "line": trace.tb_lineno,
                "function": code.co_name,
            }
            frames.append(frame)
            if local and path.parent.name == "scripts":
                item.update(frame)
        trace = trace.tb_next
    if frames:
        item["frames"] = frames


def _exception_fact(error: BaseException, relation: str, root: Path) -> dict:
    item: dict = {"type": type(error).__name__, "relation": relation}
    _include_frames(item, error, root)
    if type(error) is json.JSONDecodeError:
        item.update(input_line=error.lineno, input_column=error.colno)
    if isinstance(error, OSError) and type(errno := OSError.errno.__get__(error)) is int:
        item["errno"] = errno
    return item


def traceback_facts(error: BaseException | None) -> list[dict]:
    """Detach real cause and context frames without locals, paths or exception values."""
    seen = set()
    trail = []
    pending = [(error, "raised")]
    root = Path(__file__).resolve().parent.parent
    while pending:
        current, relation = pending.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        cause = BaseException.__cause__.__get__(current)
        context = BaseException.__context__.__get__(current)
        if context is not None and context is not cause:
            pending.append((context, "context"))
        if cause is not None:
            pending.append((cause, "cause"))
        trail.append(_exception_fact(current, relation, root))
    return trail


def warn_local_failure(operation: str) -> None:
    if sys.stderr is not None:
        try:
            sys.stderr.write(f"warning: rf_{operation}_diagnostics_unavailable\n")
        except (OSError, ValueError):
            return


def _segments(active: Path) -> tuple[Path, Path, Path, Path]:
    return (active.with_name(active.name + ".2"), active.with_name(active.name + ".rotate"),
            active.with_name(active.name + ".1"), active)


def find_local_error(identifier: str) -> dict | None:
    """Cold-read a named diagnostic, including an interrupted rotation."""
    active = native_path(state_dir() / "logs" / "runtime-errors.jsonl")
    for path in reversed(_segments(active)):
        try:
            with open_regular_file(path) as stream:
                for line in stream:
                    try:
                        entry = json.loads(line)
                    except (ValueError, RecursionError):
                        continue
                    if isinstance(entry, dict) and entry.get("id") == identifier:
                        return public_diagnostic(entry)
        except OSError:
            continue
    return None


def _rotate(active: Path, incoming: int) -> None:
    if not active.exists() or active.stat().st_size + incoming <= _LOG_BYTES:
        return
    oldest, pending, newest, _ = _segments(active)
    if pending.exists():
        pending.replace(oldest if newest.exists() else newest)
    if newest.exists():
        newest.replace(pending)
    try:
        active.replace(newest)
    except OSError:
        if pending.exists():
            pending.replace(newest)
        raise
    if pending.exists():
        pending.replace(oldest)


def record_local_error(operation: str, **facts: Any) -> bool:
    """Append one durable, sanitized RF fact with a bounded writer wait."""
    try:
        path = native_path(state_dir() / "logs" / "runtime-errors.jsonl")
        lock = OwnerFileLock(path.with_suffix(".lock"))
        deadline = monotonic() + _LOG_LOCK_WAIT
        while not lock.acquire():
            remaining = deadline - monotonic()
            if remaining <= 0:
                return False
            sleep(min(0.02, remaining))
        try:
            entry = public_diagnostic({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "operation": operation,
                "run_id": os.environ.get("RESEARCH_FEEDBACK_RUN_ID"),
                "attempt_id": os.environ.get("RESEARCH_FEEDBACK_ATTEMPT_ID"),
                **facts,
            })
            data = (json.dumps(entry, ensure_ascii=True) + "\n").encode("ascii")
            try:
                _rotate(path, len(data))
            except OSError as error:
                entry["rotation_deferred"] = type(error).__name__
                data = (json.dumps(entry, ensure_ascii=True) + "\n").encode("ascii")
            with open_regular_file(path, append=True) as stream:
                separate_partial_line(stream)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            return True
        finally:
            lock.release()
    except (OSError, TypeError, ValueError, RuntimeError):
        return False
