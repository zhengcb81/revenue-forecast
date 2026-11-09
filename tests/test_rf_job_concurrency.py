"""Real lock ownership and deterministic interleavings of job actions."""

from pathlib import Path
import subprocess
import sys
import time

import pytest

from test_rf_job_facade import _facade, _request, _recorded_requests
from rf_job_facade import JobFacadeError, JobLock, SimulatedProcessDeath


def test_kernel_lock_is_released_by_process_death_without_unlink(tmp_path):
    path = tmp_path / "owner.lock"
    legacy = b'{"pid":2147483647}'
    path.write_bytes(legacy)
    ready = tmp_path / "ready"
    script = (
        "import pathlib,sys;"
        "sys.path.insert(0,sys.argv[1]);"
        "from rf_job_facade import JobLock;"
        "lock=JobLock(pathlib.Path(sys.argv[2]));"
        "assert lock.acquire();"
        "pathlib.Path(sys.argv[3]).touch();"
        "sys.stdin.read()"
    )
    child = subprocess.Popen(
        [sys.executable, "-B", "-c", script,
         str(Path(__file__).resolve().parents[1] / "scripts"), str(path), str(ready)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        deadline = time.monotonic() + 10
        while not ready.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        assert ready.exists(), "the holder never acquired the owner lock"
        assert not JobLock(path).acquire()
    finally:
        if child.poll() is None:
            child.kill()
        child.communicate(timeout=10)
    with JobLock(path):
        pass
    assert path.read_bytes() == legacy


def _interrupted(tmp_path, *, stage="source"):
    first, _ = _facade(tmp_path, die_on_stage=stage)
    with pytest.raises(SimulatedProcessDeath):
        first.submit(_request())
    return first.store.list_job_ids()[0]


def test_reconcile_is_read_only_while_owner_is_active(tmp_path):
    job_id = _interrupted(tmp_path)
    restarted, _ = _facade(tmp_path)
    path = restarted.store.job_file(job_id)
    with restarted.store.lock(job_id):
        before = path.read_bytes()
        active = restarted.act(job_id, "reconcile")["job_view"]
        assert active["status"] == "running"
        assert path.read_bytes() == before
    assert restarted.act(job_id, "reconcile")["job_view"]["status"] == "interrupted"
    assert path.read_bytes() != before


def test_resume_reloads_after_a_competitor_finishes(tmp_path, monkeypatch):
    job_id = _interrupted(tmp_path, stage="compute")
    calls = []
    restarted, _ = _facade(tmp_path, calls=calls)
    competitor, _ = _facade(tmp_path, calls=calls)
    original_acquire = JobLock.acquire
    raced = False

    def acquire(lock):
        nonlocal raced
        if not raced and lock.path.name == f"{job_id}.lock":
            raced = True
            assert competitor.act(job_id, "resume")["job_view"]["status"] == "succeeded"
        return original_acquire(lock)

    monkeypatch.setattr(JobLock, "acquire", acquire)
    with pytest.raises(JobFacadeError) as refused:
        restarted.act(job_id, "resume")
    assert refused.value.code == "action_not_allowed"
    assert [record["stage"] for record in _recorded_requests(calls)] == ["compute", "publication"]
