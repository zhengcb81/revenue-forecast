"""ZR-710 acceptance tests: publication transaction + atomic write (REV-09).

  C1  atomic write: _atomic_write_text writes via same-dir tmp + fsync +
      os.replace; the target appears atomically; tmp is cleaned up.
  C2  fault injection: write failure / os.replace failure leave NO target
      file and NO tmp orphan; registry append failure exits 2 with no
      half-written output.
  C3  recovery idempotency: the same input published twice produces
      byte-identical outputs and exactly one registry entry per run.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import revenue_forecast  # noqa: E402
from publication_registry import RegistryError, _read_entries  # noqa: E402


# ---------------------------------------------------------------------------
# C1 — atomic write
# ---------------------------------------------------------------------------


def test_c1_atomic_write_complete(tmp_path):
    target = tmp_path / "out.json"
    revenue_forecast._atomic_write_text(target, '{"ok": true}\n')
    assert json.loads(target.read_text(encoding="utf-8")) == {"ok": True}
    # no tmp leftovers
    assert [p.name for p in tmp_path.iterdir()] == ["out.json"]


def test_c1_atomic_write_replaces_existing(tmp_path):
    target = tmp_path / "out.json"
    target.write_text("old", encoding="utf-8")
    revenue_forecast._atomic_write_text(target, '{"new": 1}\n')
    assert json.loads(target.read_text(encoding="utf-8")) == {"new": 1}
    assert [p.name for p in tmp_path.iterdir()] == ["out.json"]


# ---------------------------------------------------------------------------
# C2 — fault injection, no orphans
# ---------------------------------------------------------------------------


def test_c2_replace_failure_leaves_no_target(monkeypatch, tmp_path):
    target = tmp_path / "out.json"

    def boom(src, dst):  # noqa: ARG001
        raise OSError("injected replace failure")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        revenue_forecast._atomic_write_text(target, "data")
    assert not target.exists()
    assert [p.name for p in tmp_path.iterdir()] == []  # tmp cleaned


def test_c2_write_failure_leaves_no_target(monkeypatch, tmp_path):
    target = tmp_path / "out.json"

    class _Boom:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def write(self, text):  # noqa: ARG001
            raise OSError("injected write failure")

        def flush(self):
            pass

        def fileno(self):
            return 0

    monkeypatch.setattr("builtins.open", lambda *a, **k: _Boom())
    with pytest.raises(OSError):
        revenue_forecast._atomic_write_text(target, "data")
    assert not target.exists()


def test_c2_registry_failure_exits_without_half_output(tmp_path, monkeypatch):
    """Registry append failure is injected IN-PROCESS via main() (a
    subprocess would re-import the real _append)."""
    sys.path.insert(0, str(ROOT / "tests"))
    from test_recognition_bridge import forecast_document

    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(forecast_document()), encoding="utf-8")
    out_file = tmp_path / "out.json"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(tmp_path / "publications.jsonl"))
    monkeypatch.setattr(
        sys, "argv",
        ["revenue_forecast.py", str(input_file), "--output", str(out_file)],
    )

    import publication_registry

    def boom_append(entry):  # noqa: ARG001
        raise RegistryError("injected registry failure")

    monkeypatch.setattr(publication_registry, "_append", boom_append)
    rc = revenue_forecast.main()
    assert rc == 2
    # registry failure precedes the output write: no half-written output,
    # no registry file
    assert not out_file.exists()
    assert [p.name for p in tmp_path.iterdir()] == ["input.json"]


# ---------------------------------------------------------------------------
# C3 — recovery idempotency
# ---------------------------------------------------------------------------


def test_c3_same_input_twice_identical_output_and_one_entry_each(
    tmp_path, monkeypatch
):
    sys.path.insert(0, str(ROOT / "tests"))
    from test_recognition_bridge import forecast_document

    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(forecast_document()), encoding="utf-8")
    out1 = tmp_path / "out1.json"
    out2 = tmp_path / "out2.json"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(tmp_path / "publications.jsonl"))
    env = dict(os.environ)
    for out in (out1, out2):
        proc = subprocess.run(
            [sys.executable, "scripts/revenue_forecast.py", str(input_file),
             "--output", str(out)],
            cwd=str(ROOT), text=True, capture_output=True, env=env, timeout=120,
        )
        assert proc.returncode == 0, proc.stderr
    # byte-identical outputs
    assert out1.read_bytes() == out2.read_bytes()
    # exactly 2 registry entries (1 per run), same input anchor
    entries = _read_entries()
    assert len(entries) == 2
    assert entries[0]["input_sha256"] == entries[1]["input_sha256"]
    assert entries[0]["result_sha256"] == entries[1]["result_sha256"]


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
