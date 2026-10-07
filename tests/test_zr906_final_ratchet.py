"""ZR-906 acceptance tests: final six-gate ratchet — hardcode / dead path
(legacy) / complexity / type (mypy) / coverage / encoding.

  C1  scanner gates non-vacuous — injecting a code-level hardcoded name,
      a legacy caller reference, or a BOM-encoded file flips the gate RED
      (defense labels in comments/docstrings are allowed).
  C2  aggregator executable — tools/final_ratchet.py runs and reports all
      six gates with ok/RED; exit code reflects the worst gate.
  C3  zero-growth enforcement — hardcode/legacy/encoding scan real product
      code and must find zero code-level hits (docstring defense labels
      excluded by the code-line filter).
  C4  the type gate reports the REAL mypy tool result: a usable run that
      reports N historical errors is a diagnostic, while mypy that is
      missing, broken, unusable, or times out is RED (never green).
  C5  the default mode is light — it never starts the coverage run — and
      the explicit full mode refuses to start without its own scratch dir.

Hermetic: injection probes use tmp files; the real scripts/ tree is only
read (no writes). Complexity/type gates are exercised for executability
with bounded timeouts rather than full runs.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import final_ratchet as fr  # noqa: E402


def _make_probe_dir(tmp_path: Path) -> Path:
    probe = tmp_path / "scripts"
    probe.mkdir()
    return probe


# ---------------------------------------------------------------------------
# C1 — scanner gates non-vacuous
# ---------------------------------------------------------------------------


def test_c1_hardcode_code_level_detected(tmp_path):
    probe = _make_probe_dir(tmp_path)
    (probe / "mod_a.py").write_text(
        "def f():\n    return 'Zijin'  # hardcoded at code level\n", encoding="utf-8"
    )
    hits = fr.scan_hardcode(probe)
    assert any("Zijin" in hit for hit in hits)


def test_c1_hardcode_comment_allowed(tmp_path):
    probe = _make_probe_dir(tmp_path)
    (probe / "mod_b.py").write_text(
        "# Kamoa defense label in comment is allowed\n"
        '"""Porgera double-count guard (docstring label)."""\n'
        "def f():\n    return 1\n",
        encoding="utf-8",
    )
    assert fr.scan_hardcode(probe) == []


def test_c1_legacy_reference_detected(tmp_path):
    probe = _make_probe_dir(tmp_path)
    (probe / "mod_c.py").write_text("import legacy_bridge\n", encoding="utf-8")
    hits = fr.scan_legacy(probe)
    assert any("legacy_bridge" in hit for hit in hits)


def test_c1_bom_file_detected(tmp_path):
    probe = _make_probe_dir(tmp_path)
    path = probe / "mod_d.py"
    path.write_bytes(b"\xef\xbb\xbf" + b"print(1)\n")
    problems = fr.scan_encoding(tmp_path)
    assert any("BOM" in p for p in problems)


# ---------------------------------------------------------------------------
# C2 — aggregator executable
# ---------------------------------------------------------------------------


def test_c2_aggregator_runs_and_reports_all_gates():
    proc = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "tools" / "final_ratchet.py"),
            "--scripts",
            str(ROOT / "scripts"),
            "--scanners-only",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    out = proc.stdout + proc.stderr
    for gate in ("hardcode", "legacy", "encoding", "complexity", "type", "coverage"):
        assert gate in out, f"gate {gate} missing from aggregator output"
    assert proc.returncode == 0, out


def test_c2_aggregator_json_shape():
    proc = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "tools" / "final_ratchet.py"),
            "--scripts",
            str(ROOT / "scripts"),
            "--print-json",
            "--scanners-only",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    result = json.loads(proc.stdout)
    assert set(result) == {
        "hardcode",
        "legacy",
        "encoding",
        "complexity",
        "type",
        "coverage",
    }
    assert all("ok" in gate for gate in result.values())
    assert all("status" in gate for gate in result.values())


# ---------------------------------------------------------------------------
# C3 — zero-growth enforcement on the real product code
# ---------------------------------------------------------------------------


def test_c3_real_code_zero_code_level_hardcode():
    assert fr.scan_hardcode(ROOT / "scripts") == [], (
        "code-level company/mine hardcode must be zero (docstring labels excluded)"
    )


def test_c3_real_code_zero_legacy_callers():
    assert fr.scan_legacy(ROOT / "scripts") == [], (
        "legacy engine caller references must be zero"
    )


def test_c3_real_code_no_bom():
    assert fr.scan_encoding(ROOT) == [], "BOM-encoded python files must be zero"


# ---------------------------------------------------------------------------
# C4 — the type gate explains itself with the real tool result
# ---------------------------------------------------------------------------


def _completed(returncode: int, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(
        ["python", "-m", "mypy"], returncode, stdout, stderr
    )


def test_c4_historical_error_count_is_a_diagnostic(monkeypatch):
    def fake_run(args, **kwargs):
        if "--version" in args:
            return _completed(0, "mypy 1.19.0\n")
        return _completed(1, "scripts/a.py:1: error: x\n" * 69)

    monkeypatch.setattr(fr.subprocess, "run", fake_run)
    ok, detail = fr.gate_type()
    assert ok is True, detail
    assert "69" in detail
    assert "0 errors" not in detail


def test_c4_clean_mypy_is_ok(monkeypatch):
    def fake_run(args, **kwargs):
        if "--version" in args:
            return _completed(0, "mypy 1.19.0\n")
        return _completed(0, "Success: no issues found\n")

    monkeypatch.setattr(fr.subprocess, "run", fake_run)
    ok, detail = fr.gate_type()
    assert ok is True
    assert "0 errors" in detail


def test_c4_mypy_missing_is_red(monkeypatch):
    def fake_run(args, **kwargs):
        raise FileNotFoundError("python -m mypy could not be started")

    monkeypatch.setattr(fr.subprocess, "run", fake_run)
    ok, detail = fr.gate_type()
    assert ok is False
    assert "unavailable" in detail or "start" in detail


def test_c4_mypy_timeout_is_red(monkeypatch):
    def fake_run(args, **kwargs):
        raise subprocess.TimeoutExpired(args, kwargs.get("timeout", 1))

    monkeypatch.setattr(fr.subprocess, "run", fake_run)
    ok, detail = fr.gate_type()
    assert ok is False
    assert "time" in detail.lower()


def test_c4_mypy_usage_error_is_red(monkeypatch):
    def fake_run(args, **kwargs):
        if "--version" in args:
            return _completed(0, "mypy 1.19.0\n")
        return _completed(2, "", "error: config file not found\n")

    monkeypatch.setattr(fr.subprocess, "run", fake_run)
    ok, detail = fr.gate_type()
    assert ok is False
    assert "rc=2" in detail


def test_c4_mypy_without_version_banner_is_red(tmp_path):
    """A python that resolves ``-m mypy`` to a module which prints nothing
    is not mypy: the real CLI entry must go RED instead of reporting green."""
    stub = tmp_path / "site"
    stub.mkdir()
    (stub / "mypy.py").write_text("", encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(stub)
    proc = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "tools" / "final_ratchet.py"),
            "--print-json",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=300,
        env=env,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["type"]["ok"] is False
    assert payload["type"]["status"] == "red"


def test_c4_type_failure_makes_the_ratchet_red(monkeypatch, capsys):
    monkeypatch.setattr(fr, "gate_type", lambda: (False, "mypy unavailable"))
    monkeypatch.setattr(fr, "gate_complexity", lambda: (True, "complexity ratchet OK"))
    monkeypatch.setattr(sys, "argv", ["final_ratchet.py"])
    assert fr.main() == 1
    out = capsys.readouterr().out
    assert "type: RED" in out


def test_c4_baseline_is_documented_but_not_a_gate(monkeypatch):
    # REV-001 kept the measured number as a reference; it no longer decides ok.
    assert fr.MYPY_BASELINE == 69

    def fake_run(args, **kwargs):
        if "--version" in args:
            return _completed(0, "mypy 1.19.0\n")
        return _completed(1, "scripts/a.py:1: error: x\n" * (fr.MYPY_BASELINE + 5))

    monkeypatch.setattr(fr.subprocess, "run", fake_run)
    ok, detail = fr.gate_type()
    assert ok is True
    assert str(fr.MYPY_BASELINE + 5) in detail


# ---------------------------------------------------------------------------
# C5 — default stays light; full mode is explicit
# ---------------------------------------------------------------------------


def test_c5_default_never_starts_a_coverage_run(tmp_path, monkeypatch):
    monkeypatch.setattr(fr, "gate_complexity", lambda: (True, "ok"))
    monkeypatch.setattr(fr, "gate_type", lambda: (True, "ok"))
    started: list[list[str]] = []

    def fake_run(args, **kwargs):
        started.append([str(a) for a in args])
        raise AssertionError(f"default mode must not spawn: {args}")

    monkeypatch.setattr(fr.subprocess, "run", fake_run)
    result = fr.run_all(ROOT)
    assert result["coverage"]["status"] == "not_supplied"
    assert result["coverage"]["ok"] is True
    assert started == []


def test_c5_default_runs_the_light_gates_only_once_each(monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(
        fr, "gate_complexity", lambda: calls.append("complexity") or (True, "ok")
    )
    monkeypatch.setattr(fr, "gate_type", lambda: calls.append("type") or (True, "ok"))
    monkeypatch.setattr(
        fr, "gate_coverage", lambda: calls.append("coverage") or (True, "ok")
    )
    fr.run_all(ROOT)
    assert calls == ["complexity", "type"]


def test_c5_full_mode_delegates_one_coverage_run(tmp_path, monkeypatch):
    calls: list[list[str]] = []
    monkeypatch.setattr(fr, "gate_complexity", lambda: (True, "ok"))
    monkeypatch.setattr(fr, "gate_type", lambda: (True, "ok"))

    def fake_coverage(scratch, target=None):
        calls.append(["coverage", str(scratch), str(target)])
        return True, "coverage ran once"

    monkeypatch.setattr(fr, "gate_coverage", fake_coverage)
    result = fr.run_all(ROOT, full=True, coverage_scratch=tmp_path)
    assert calls == [["coverage", str(tmp_path), "None"]]
    assert result["coverage"]["ok"] is True


def test_c5_full_mode_without_scratch_is_a_configuration_error():
    proc = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "tools" / "final_ratchet.py"),
            "--scanners-only",
            "--full",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert proc.returncode != 0
    assert "coverage-scratch" in (proc.stdout + proc.stderr)


def test_c5_scanners_only_still_reports_every_gate():
    result = fr.run_all(ROOT, scanners_only=True)
    assert set(result) == {
        "hardcode",
        "legacy",
        "encoding",
        "complexity",
        "type",
        "coverage",
    }
    assert all(gate["ok"] for gate in result.values())


def test_c5_gate_type_reads_the_module_source_shape():
    source = (ROOT / "tools" / "final_ratchet.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert {
        "scan_hardcode",
        "scan_legacy",
        "scan_encoding",
        "gate_type",
        "gate_complexity",
    } <= names
