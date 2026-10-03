"""Real pipe bounds and timeout cleanup for the opt-in narrative reader."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from threading import enumerate as live_threads
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from company_wiki_narrative_contracts import NarrativeTransportError  # noqa: E402
from company_wiki_narrative_process import run_bounded  # noqa: E402


def test_bounded_runner_reads_stdin_and_both_pipes():
    result = run_bounded(
        [sys.executable, "-c", "import sys; data=sys.stdin.buffer.read(); "
         "sys.stdout.buffer.write(data); sys.stderr.buffer.write(b'receipt\\n')"],
        b"request", stdout_limit=32, stderr_limit=32, timeout_seconds=5,
    )
    assert result.returncode == 0
    assert result.stdout == b"request"
    assert result.stderr == b"receipt\n"


@pytest.mark.parametrize("stream", [1, 2])
def test_oversized_pipe_is_stopped_during_capture(stream):
    with pytest.raises(NarrativeTransportError) as error:
        run_bounded(
            [sys.executable, "-c", f"import os,time; os.write({stream},b'x'*1000000); time.sleep(30)"],
            b"", stdout_limit=1024, stderr_limit=1024, timeout_seconds=5,
        )
    assert error.value.reason == "reader_output_limit"


def test_timeout_kills_provider_and_descendant_before_marker_write(tmp_path):
    marker = tmp_path / "orphan-marker"
    child = "import time,pathlib; time.sleep(4); pathlib.Path(" + repr(str(marker)) + ").write_text('orphan')"
    parent = (
        "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',"
        + repr(child) + "]); time.sleep(30)"
    )
    with pytest.raises(NarrativeTransportError) as error:
        run_bounded([sys.executable, "-c", parent], b"",
                    stdout_limit=1024, stderr_limit=1024, timeout_seconds=1.5)
    assert error.value.reason == "reader_timeout"
    time.sleep(3)
    assert not marker.exists()



def _stop_test_child(pid_path):
    if not pid_path.exists():
        return
    pid = int(pid_path.read_text())
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=5, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def test_deadline_and_tree_cleanup_cover_exited_wrapper_with_live_pipe_holders(tmp_path):
    pid_path, marker = tmp_path / "holder-pid", tmp_path / "orphan-marker"
    child = ("import os,time,pathlib; pathlib.Path(" + repr(str(pid_path))
             + ").write_text(str(os.getpid())); os.write(1,b'held-out'); os.write(2,b'held-err'); "
             + "time.sleep(5); pathlib.Path(" + repr(str(marker)) + ").write_text('orphan'); time.sleep(30)")
    parent = "import subprocess,sys; subprocess.Popen([sys.executable,'-c'," + repr(child) + "]); raise SystemExit(0)"
    baseline = {thread.ident for thread in live_threads()}
    started = time.monotonic()
    try:
        with pytest.raises(NarrativeTransportError) as error:
            run_bounded([sys.executable, "-c", parent], b"",
                        stdout_limit=1024, stderr_limit=1024, timeout_seconds=2.0)
        elapsed = time.monotonic() - started
        assert error.value.reason == "reader_timeout"
        assert elapsed < 4, "the same deadline must cover process wait and both pipe drains"
        assert pid_path.exists(), "the real holder must have started"
        assert {thread.ident for thread in live_threads()} <= baseline
        time.sleep(3.5)
        assert not marker.exists(), "exited wrappers must not leave a running grandchild"
    finally:
        _stop_test_child(pid_path)



@pytest.mark.parametrize("fault", ["tree_attach", "second_thread"])
def test_startup_fault_reaps_suspended_or_partially_started_process(tmp_path, monkeypatch, fault):
    import company_wiki_narrative_process as process_module
    baseline = {thread.ident for thread in live_threads()}
    processes = []
    real_start = process_module._start

    def record_start(command, tree):
        process = real_start(command, tree)
        processes.append(process)
        return process

    monkeypatch.setattr(process_module, "_start", record_start)
    if fault == "tree_attach":
        def fail_attach(_tree, _process):
            raise OSError("simulated job assignment failure")
        monkeypatch.setattr(process_module.ProcessTree, "attach", fail_attach)
    else:
        real_thread_start = process_module.Thread.start
        starts = []

        def fail_second_thread(thread):
            starts.append(thread)
            if len(starts) == 2:
                raise RuntimeError("simulated thread resource exhaustion")
            return real_thread_start(thread)

        monkeypatch.setattr(process_module.Thread, "start", fail_second_thread)
    with pytest.raises(NarrativeTransportError) as error:
        run_bounded([sys.executable, "-c", "import time; time.sleep(30)"], b"",
                    stdout_limit=32, stderr_limit=32, timeout_seconds=2)
    assert error.value.reason == "reader_unavailable"
    assert len(processes) == 1 and processes[0].poll() is not None
    assert all(pipe.closed for pipe in (processes[0].stdin, processes[0].stdout, processes[0].stderr))
    assert {thread.ident for thread in live_threads()} <= baseline
