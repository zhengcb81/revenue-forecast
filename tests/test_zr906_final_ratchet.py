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

Hermetic: injection probes use tmp files; the real scripts/ tree is only
read (no writes). Complexity/type/coverage gates are exercised for
executability with bounded timeouts rather than full runs.
"""

from __future__ import annotations

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
        "def f():\n    return 'Zijin'  # hardcoded at code level\n",
        encoding="utf-8")
    hits = fr.scan_hardcode(probe)
    assert any("Zijin" in hit for hit in hits)


def test_c1_hardcode_comment_allowed(tmp_path):
    probe = _make_probe_dir(tmp_path)
    (probe / "mod_b.py").write_text(
        "# Kamoa defense label in comment is allowed\n"
        '"""Porgera double-count guard (docstring label)."""\n'
        "def f():\n    return 1\n",
        encoding="utf-8")
    assert fr.scan_hardcode(probe) == []


def test_c1_legacy_reference_detected(tmp_path):
    probe = _make_probe_dir(tmp_path)
    (probe / "mod_c.py").write_text(
        "import legacy_bridge\n", encoding="utf-8")
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
        [sys.executable, "-B", str(ROOT / "tools" / "final_ratchet.py"),
         "--scripts", str(ROOT / "scripts"), "--scanners-only"],
        capture_output=True, text=True, encoding="utf-8", timeout=120,
    )
    out = proc.stdout + proc.stderr
    for gate in ("hardcode", "legacy", "encoding", "complexity", "type", "coverage"):
        assert gate in out, f"gate {gate} missing from aggregator output"


def test_c2_aggregator_json_shape():
    proc = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "final_ratchet.py"),
         "--scripts", str(ROOT / "scripts"), "--print-json", "--scanners-only"],
        capture_output=True, text=True, encoding="utf-8", timeout=120,
    )
    import json

    result = json.loads(proc.stdout)
    assert set(result) == {"hardcode", "legacy", "encoding",
                           "complexity", "type", "coverage"}
    assert all("ok" in gate for gate in result.values())


# ---------------------------------------------------------------------------
# C3 — zero-growth enforcement on the real product code
# ---------------------------------------------------------------------------


def test_c3_real_code_zero_code_level_hardcode():
    assert fr.scan_hardcode(ROOT / "scripts") == [], (
        "code-level company/mine hardcode must be zero (docstring labels excluded)")


def test_c3_real_code_zero_legacy_callers():
    assert fr.scan_legacy(ROOT / "scripts") == [], (
        "legacy engine caller references must be zero")


def test_c3_real_code_no_bom():
    assert fr.scan_encoding(ROOT) == [], "BOM-encoded python files must be zero"
