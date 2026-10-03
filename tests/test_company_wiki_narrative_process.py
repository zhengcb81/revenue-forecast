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
    if fault == "second_thread" and sys.platform != "win32":
        pytest.skip("POSIX pipes are nonblocking and have no background thread startup")
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



@pytest.mark.skipif(sys.platform == "win32", reason="POSIX session detachment; Windows Job owns descendants")
def test_detached_pipe_holder_cannot_hang_local_reader_host(tmp_path):
    pid_path = tmp_path / "detached.pid"
    wrapper = tmp_path / "wrapper.py"
    child = ("import os,time,pathlib; p=pathlib.Path(" + repr(str(pid_path))
             + "); t=p.with_suffix('.tmp'); t.write_text(str(os.getpid())); t.replace(p); time.sleep(30)")
    wrapper.write_text(
        "import pathlib,subprocess,sys,time\n"
        + "subprocess.Popen([sys.executable,'-c'," + repr(child) + "],start_new_session=True)\n"
        + "while not pathlib.Path(" + repr(str(pid_path)) + ").exists(): time.sleep(0.005)\n",
        encoding="utf-8",
    )
    driver = tmp_path / "host.py"
    driver.write_text(
        "import sys,json,threading,time\n"
        + "sys.path.insert(0," + repr(str(ROOT / "scripts")) + ")\n"
        + "import company_wiki_narrative_process as port\n"
        + "from company_wiki_narrative_contracts import NarrativeTransportError\n"
        + "created=[]; original=port._start\n"
        + "def record(*args):\n p=original(*args);created.append(p);return p\n"
        + "port._start=record;started=time.monotonic()\n"
        + "try:\n port.run_bounded([sys.executable," + repr(str(wrapper))
        + "],b'',stdout_limit=32,stderr_limit=32,timeout_seconds=2)\n"
        + "except NarrativeTransportError as error:\n"
        + " print(json.dumps({'reason':error.reason,'elapsed':time.monotonic()-started,"
        + "'reader_threads':sum(t.name.startswith('rf-narrative-') for t in threading.enumerate()),"
        + "'pipes_closed':all(p.closed for p in (created[0].stdin,created[0].stdout,created[0].stderr))}),flush=True)\n"
        + " raise SystemExit(2)\n", encoding="utf-8",
    )
    host = subprocess.Popen([sys.executable, "-B", str(driver)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = host.communicate(timeout=4)
        assert host.returncode == 2 and stderr == b""
        import json
        result = json.loads(stdout)
        assert result["reason"] == "reader_timeout" and result["elapsed"] < 4
        assert result["pipes_closed"] is True and result["reader_threads"] == 0
        assert pid_path.exists()
        os.kill(int(pid_path.read_text()), 0)  # Escaped PID is out of scope; only local resources must close.
    finally:
        if host.poll() is None:
            host.kill()
        _stop_test_child(pid_path)
        host.communicate(timeout=3)
