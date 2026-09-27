"""WC-4 = F12-RC120: a stdout delivery failure at process exit must land in
the frozen rc domain {0, 2}.

Frozen basis (see the card oracle, `execution_runs/WC-4-RC120/a20260923-01`):
I-09-A fault-table row F12 pins the producer exit code to "0 or 2"; the owner
ruled (OWNER_DECISIONS sec23, verbatim "2, record as to-be-repaired") that the
domain stays frozen and the measured rc=120 is a product defect to repair.

Mechanism (corrected wording; SA-DEFECT's "assertion fires after return" is
wrong): when stdout delivery fails (pipe with no reader), the *interpreter
shutdown* flush of the still-buffered stdout fails with OSError and CPython
self-reports process exit code 120, overriding the CLI's own 0/2.  The CLI must
catch that failure inside its own exit path, keep an explanatory message on
stderr, and exit 2.

Two layers of guard:
* end-to-end: spawn the real CLI with a stdout pipe nobody reads;
* in-process: drive ``_finalize_exit_status`` / ``_neutralize_broken_stream``
  directly so every branch of the fix is covered without relying on the
  coverage subprocess hook (tools/run_coverage_gates.py per-module gate).
"""
from __future__ import annotations

import builtins
import io
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "revenue_forecast.py"
FROZEN_DOMAIN = {0, 2}

sys.path.insert(0, str(ROOT / "scripts"))
import revenue_forecast  # noqa: E402


class _BrokenStream:
    """stdout stand-in whose flush fails like a pipe with no reader."""

    def __init__(self) -> None:
        self.flushed = 0

    def write(self, text: str) -> int:
        return len(text)

    def flush(self) -> None:
        self.flushed += 1
        raise OSError(22, "Invalid argument")


class _CountingStream:
    """stdout stand-in that flushes fine (success path)."""

    def __init__(self) -> None:
        self.flushed = 0

    def write(self, text: str) -> int:
        return len(text)

    def flush(self) -> None:
        self.flushed += 1


class _BrokenStderr:
    def write(self, text: str) -> int:
        raise OSError(22, "Invalid argument")

    def flush(self) -> None:
        raise OSError(22, "Invalid argument")


def _spawn_without_stdout_reader(argv: list[str]) -> subprocess.Popen:
    read_fd, write_fd = os.pipe()
    try:
        proc = subprocess.Popen(
            argv,
            cwd=str(ROOT),
            stdout=write_fd,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
        )
    finally:
        os.close(write_fd)
        os.close(read_fd)  # F12 fault: no reader for the child's stdout
    return proc


def test_broken_stdout_flush_exits_2_with_preserved_error_text() -> None:
    proc = _spawn_without_stdout_reader([sys.executable, "-B", str(CLI), "--version"])
    _, err = proc.communicate(timeout=120)
    stderr = (err or b"").decode("utf-8", "replace")
    assert proc.returncode == 2, (
        f"F12 flush failure must exit in the frozen domain {{0,2}} as rc=2, "
        f"got {proc.returncode}; stderr={stderr!r}"
    )
    assert proc.returncode in FROZEN_DOMAIN
    # fail-closed but informative: the flush error survives on stderr ...
    assert "stdout flush failed" in stderr, stderr
    assert "Errno" in stderr, stderr
    # ... and the interpreter no longer has to self-report a shutdown failure
    assert "Exception ignored on flushing sys.stdout" not in stderr, stderr


def test_broken_stdout_baseline_delivery_unchanged() -> None:
    proc = subprocess.run(
        [sys.executable, "-B", str(CLI), "--version"],
        cwd=str(ROOT),
        capture_output=True,
        stdin=subprocess.DEVNULL,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
    assert proc.stdout.decode("utf-8", "replace").startswith("revenue-forecast "), proc.stdout


def test_usage_error_path_still_exits_2() -> None:
    proc = subprocess.run(
        [sys.executable, "-B", str(CLI)],
        cwd=str(ROOT),
        capture_output=True,
        stdin=subprocess.DEVNULL,
        timeout=120,
    )
    assert proc.returncode == 2, proc.stderr.decode("utf-8", "replace")


def test_finalize_exit_status_passes_rc_through_when_flush_works(monkeypatch) -> None:
    stream = _CountingStream()
    monkeypatch.setattr(sys, "stdout", stream)
    assert revenue_forecast._finalize_exit_status(0) == 0
    assert revenue_forecast._finalize_exit_status(2) == 2
    assert stream.flushed == 2


def test_finalize_exit_status_normalizes_flush_failure_to_2(monkeypatch) -> None:
    broken = _BrokenStream()
    capture = io.StringIO()
    monkeypatch.setattr(sys, "stdout", broken)
    monkeypatch.setattr(sys, "stderr", capture)
    assert revenue_forecast._finalize_exit_status(0) == 2
    text = capture.getvalue()
    assert "stdout flush failed" in text, text
    assert "Errno" in text, text
    # the broken stream must be detached, otherwise interpreter shutdown would
    # re-flush it and CPython would override the exit status with 120
    assert sys.stdout is not broken


def test_finalize_exit_status_keeps_existing_error_code_on_flush_failure(monkeypatch) -> None:
    monkeypatch.setattr(sys, "stdout", _BrokenStream())
    capture = io.StringIO()
    monkeypatch.setattr(sys, "stderr", capture)
    assert revenue_forecast._finalize_exit_status(2) == 2


def test_finalize_exit_status_survives_broken_stderr(monkeypatch) -> None:
    monkeypatch.setattr(sys, "stdout", _BrokenStream())
    monkeypatch.setattr(sys, "stderr", _BrokenStderr())
    assert revenue_forecast._finalize_exit_status(0) == 2
    # stderr was replaced by a usable sink instead of propagating the failure
    assert not isinstance(sys.stderr, _BrokenStderr)


def test_neutralize_broken_stream_falls_back_when_devnull_unavailable(monkeypatch) -> None:
    def _boom(*args, **kwargs):
        raise OSError(22, "Invalid argument")

    monkeypatch.setattr(builtins, "open", _boom)
    original = sys.stdout
    revenue_forecast._neutralize_broken_stream("stdout")
    assert sys.stdout is not original
    assert sys.stdout.write("discarded") == 9  # no-op sink, never raises
    sys.stdout.flush()
