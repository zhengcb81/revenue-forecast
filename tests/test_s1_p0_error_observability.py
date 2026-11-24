"""S1-06 regression tests: filing_fetch_client stderr preservation and cause chains."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import filing_fetch_client as ffc  # noqa: E402


def test_invoke_filing_fetch_includes_redacted_stderr_on_non_json_failure(tmp_path, monkeypatch):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "fetch_filing.py").write_text("# stub\n", encoding="utf-8")

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0],
            returncode=2,
            stdout="",
            stderr="ImportError: missing dependency token=TOPSECRET42\n",
        )

    monkeypatch.setattr(ffc.subprocess, "run", _fake_run)

    with pytest.raises(ffc._ClientError) as exc_info:
        ffc.resolve_filing_result(
            {"company": "Acme"},
            timeout_seconds=10,
            filing_fetch_root=tmp_path,
        )

    msg = str(exc_info.value)
    assert "ImportError" in msg
    assert "TOPSECRET42" not in msg


def test_invoke_filing_fetch_preserves_json_decode_cause_chain(tmp_path, monkeypatch):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "fetch_filing.py").write_text("# stub\n", encoding="utf-8")

    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0],
            returncode=0,
            stdout="{broken-json",
            stderr="",
        )

    monkeypatch.setattr(ffc.subprocess, "run", _fake_run)

    with pytest.raises(ffc._ClientError) as exc_info:
        ffc.resolve_filing_result(
            {"company": "Acme"},
            timeout_seconds=10,
            filing_fetch_root=tmp_path,
        )

    assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)
