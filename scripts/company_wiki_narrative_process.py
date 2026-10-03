"""Capture a local source-reader process with limits enforced while reading."""

from __future__ import annotations

from dataclasses import dataclass, field
from io import BufferedReader
import math
import os
import signal
import subprocess
import sys
from threading import Event, Thread
import time
from typing import BinaryIO, Sequence, cast

from company_wiki_narrative_contracts import NarrativeTransportError, REQUEST_LIMIT


@dataclass(frozen=True)
class ReaderOutput:
    returncode: int
    stdout: bytes
    stderr: bytes


@dataclass
class _Capture:
    stream: BufferedReader
    limit: int
    overflow: Event
    data: bytearray = field(default_factory=bytearray)
    error: bool = False

    def collect(self) -> None:
        try:
            while True:
                chunk = self.stream.read1(min(4096, self.limit - len(self.data) + 1))
                if not chunk:
                    return
                if len(self.data) + len(chunk) > self.limit:
                    self.overflow.set()
                    return
                self.data.extend(chunk)
        except (OSError, ValueError):
            self.error = True


def _write_input(stream: BinaryIO, data: bytes) -> None:
    try:
        stream.write(data)
        stream.flush()
    except (BrokenPipeError, OSError, ValueError):
        pass
    finally:
        stream.close()


def _terminate_tree(process: subprocess.Popen[bytes]) -> None:
    # This is a local, fixed command with an integer PID and no shell. On
    # Windows it kills descendants that inherited a pipe as well as the reader.
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=5, check=False, creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        process.kill()
    process.wait(timeout=5)


def _options(command: Sequence[str], data: bytes, timeout: float, limits: tuple[int, int]) -> None:
    _command_option(command)
    if not isinstance(data, bytes) or len(data) > REQUEST_LIMIT:
        raise NarrativeTransportError("blocked", "request_size_limit")
    _timeout_option(timeout)
    if any(type(limit) is not int or limit < 1 for limit in limits):
        raise NarrativeTransportError("blocked", "invalid_reader_limit")


def _command_option(command: Sequence[str]) -> None:
    if not command or not all(isinstance(arg, str) and arg for arg in command):
        raise NarrativeTransportError("blocked", "invalid_reader_command")


def _timeout_option(timeout: float) -> None:
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise NarrativeTransportError("blocked", "invalid_reader_timeout")
    if not math.isfinite(timeout) or timeout <= 0:
        raise NarrativeTransportError("blocked", "invalid_reader_timeout")


def _wait(process: subprocess.Popen[bytes], overflow: Event, deadline: float) -> str | None:
    while process.poll() is None:
        if overflow.is_set():
            return "reader_output_limit"
        if time.monotonic() >= deadline:
            return "reader_timeout"
        time.sleep(0.01)
    return None


def _close_pipes(process: subprocess.Popen[bytes], captures: list[_Capture], threads: list[Thread]) -> bool:
    for thread in threads:
        thread.join(timeout=2)
    alive = any(thread.is_alive() for thread in threads)
    if alive:
        _terminate_tree(process)
        for thread in threads:
            thread.join(timeout=2)
        alive = any(thread.is_alive() for thread in threads)
    if not alive:
        for capture in captures:
            capture.stream.close()
    return not alive


def _start(command: Sequence[str]) -> subprocess.Popen[bytes]:
    environment = dict(os.environ)
    environment.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PYTHON_DOTENV_DISABLED="1")
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    try:
        return subprocess.Popen(
            list(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=environment, shell=False, creationflags=flags,
            start_new_session=sys.platform != "win32",
        )
    except OSError as exc:
        raise NarrativeTransportError("unavailable", "reader_unavailable") from exc


def _capture_result(process: subprocess.Popen[bytes], captures: list[_Capture], overflow: Event,
                    reason: str | None, clean: bool) -> ReaderOutput:
    if not clean:
        raise NarrativeTransportError("unavailable", "reader_cleanup_failed")
    if reason or overflow.is_set():
        raise NarrativeTransportError("unavailable", reason or "reader_output_limit")
    if any(capture.error for capture in captures):
        raise NarrativeTransportError("unavailable", "reader_pipe_failed")
    return ReaderOutput(process.returncode, bytes(captures[0].data), bytes(captures[1].data))


def run_bounded(
    command: Sequence[str], data: bytes, *, stdout_limit: int,
    stderr_limit: int, timeout_seconds: float = 30,
) -> ReaderOutput:
    """Only a capped buffer is allocated; timeout/overflow terminate the tree."""
    _options(command, data, timeout_seconds, (stdout_limit, stderr_limit))
    process = _start(command)
    overflow = Event()
    captures = [_Capture(cast(BufferedReader, process.stdout), stdout_limit, overflow),
                _Capture(cast(BufferedReader, process.stderr), stderr_limit, overflow)]
    threads = [Thread(target=capture.collect, daemon=True) for capture in captures]
    threads.append(Thread(target=_write_input, args=(process.stdin, data), daemon=True))
    for thread in threads:
        thread.start()
    reason = None
    try:
        reason = _wait(process, overflow, time.monotonic() + timeout_seconds)
        if reason:
            _terminate_tree(process)
    finally:
        clean = _close_pipes(process, captures, threads)
    return _capture_result(process, captures, overflow, reason, clean)
