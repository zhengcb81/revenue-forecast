"""Real pipe bounds and timeout cleanup for the opt-in narrative reader."""

from __future__ import annotations

import sys
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
