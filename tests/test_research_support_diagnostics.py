"""Read-only economic-support-diagnostics/1 CLI over static native fixtures.

The CLI must never write the input, sources or any production registry, must
not call models or downloads, and every non-supported cell must carry concrete
calibration/parameter/claim-ID reasons instead of one generic "insufficient"."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "research_support_diagnostics.py"
FIXTURES = ROOT / "tests" / "fixtures" / "scoped_calibration_support"


def run_cli(args, tmp_path):
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(CLI), *args],
        capture_output=True, text=True, encoding="utf-8", timeout=60, cwd=str(tmp_path),
    )


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_cli_emits_support_matrix_for_valid_calibrated_fixture(tmp_path):
    source = FIXTURES / "valid_calibrated.json"
    out = tmp_path / "diagnostics.json"
    run = run_cli(["--input", str(source), "--output", str(out)], tmp_path)
    assert run.returncode == 0, run.stderr
    data = load(out)
    assert data["schema_version"] == "economic-support-diagnostics/1"
    assert data["input_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert data["requested_years"] == ["2026", "2027"]
    assert data["economic_truth_inferred"] is False
    segments = {s["segment"]: s for s in data["segments"]}
    assert set(segments) == {"Segment A", "Segment B"}
    by_key = {(e["scenario"], e["year"]): e for e in segments["Segment A"]["entries"]}
    # Segment A FY2026 is fully covered by the referenced-range calibration.
    for scenario in ("low", "base", "high"):
        entry = by_key[(scenario, "2026")]
        assert entry["status"] == "supported", entry
        assert entry["calibration_ids"] == ["reference_bridge"]
        assert entry["reasons"] == []
        assert entry["supported_parameter_ids"] == ["0_" + scenario + "_2026"]
        assert entry["claim_ids"] == ["claim_parameter_reference_lower", "claim_parameter_reference_upper"]
    # The same segment's FY2027 row is not covered by that one-year calibration.
    fy27 = by_key[("low", "2027")]
    assert fy27["status"] == "unsupported"
    assert any("parameter_without_referenced_range_calibration:0_low_2027" in r for r in fy27["reasons"])
    # Segment B was never part of any calibration.
    seg_b = {(e["scenario"], e["year"]): e for e in segments["Segment B"]["entries"]}
    b26 = seg_b[("base", "2026")]
    assert b26["status"] == "unsupported"
    assert "parameter_without_referenced_range_calibration:1_base_2026" in b26["reasons"]
    assert "calibration_scope_not_covering:reference_bridge:Segment B" in b26["reasons"]


def test_cli_marks_partially_covered_multi_driver_cell_conditional(tmp_path):
    source = FIXTURES / "partial_driver_calibration.json"
    run = run_cli(["--input", str(source)], tmp_path)
    assert run.returncode == 0, run.stderr
    data = json.loads(run.stdout)
    segment_a = next(s for s in data["segments"] if s["segment"] == "Segment A")
    by_key = {(e["scenario"], e["year"]): e for e in segment_a["entries"]}
    # FY2026: price driver covered by price_bridge, units driver not covered.
    entry = by_key[("low", "2026")]
    assert entry["status"] == "conditional"
    assert entry["supported_parameter_ids"] == ["price_low_2026"]
    assert entry["unsupported_parameter_ids"] == ["units_low_2026"]
    assert entry["calibration_ids"] == ["price_bridge"]
    assert "parameter_without_referenced_range_calibration:units_low_2026" in entry["reasons"]
    # FY2027: neither driver covered.
    fy27 = by_key[("high", "2027")]
    assert fy27["status"] == "unsupported"
    assert "parameter_without_referenced_range_calibration:price_high_2027" in fy27["reasons"]
    assert "parameter_without_referenced_range_calibration:units_high_2027" in fy27["reasons"]


def test_cli_keeps_unrelated_scope_calibration_out_of_supported(tmp_path):
    source = FIXTURES / "unrelated_conversion_scope.json"
    run = run_cli(["--input", str(source)], tmp_path)
    assert run.returncode == 0, run.stderr
    data = json.loads(run.stdout)
    segment_a = next(s for s in data["segments"] if s["segment"] == "Segment A")
    entry = next(e for e in segment_a["entries"] if e["scenario"] == "low" and e["year"] == "2026")
    assert entry["status"] == "unsupported"
    reasons = " | ".join(entry["reasons"])
    assert "conversion_low" in reasons and "claim_parameter_conversion_low" in reasons
    assert entry["calibration_ids"] == []


def test_cli_reports_unrelated_calibration_scope_with_native_reasons(tmp_path):
    source = FIXTURES / "unrelated_calibration_scope.json"
    out = tmp_path / "diag.json"
    run = run_cli(["--input", str(source), "--output", str(out)], tmp_path)
    assert run.returncode == 0, run.stderr
    data = load(out)
    segment_a = next(s for s in data["segments"] if s["segment"] == "Segment A")
    entry = next(e for e in segment_a["entries"] if e["scenario"] == "base" and e["year"] == "2026")
    assert entry["status"] == "unsupported"
    assert any("calibration_scope_not_native_business:Unrelated Product X" in r for r in entry["reasons"])


def test_cli_without_optional_research_reports_all_unsupported(tmp_path):
    source = FIXTURES / "no_research.json"
    run = run_cli(["--input", str(source)], tmp_path)
    assert run.returncode == 0, run.stderr
    data = json.loads(run.stdout)
    assert data["economic_truth_inferred"] is False
    for segment in data["segments"]:
        for entry in segment["entries"]:
            assert entry["status"] == "unsupported"
            assert entry["reasons"] == ["no_optional_operating_research_declared"]


def test_cli_is_read_only_and_fails_closed_on_bad_input(tmp_path):
    before = {
        p.name: p.read_bytes()
        for p in FIXTURES.iterdir()
    }
    missing = run_cli(["--input", str(tmp_path / "absent.json")], tmp_path)
    assert missing.returncode != 0
    garbage = tmp_path / "garbage.json"
    garbage.write_text("not json", encoding="utf-8")
    invalid = run_cli(["--input", str(garbage)], tmp_path)
    assert invalid.returncode != 0
    # Existing outputs are not silently overwritten by default.
    out = tmp_path / "out.json"
    out.write_text("sentinel", encoding="utf-8")
    clash = run_cli(["--input", str(FIXTURES / "valid_calibrated.json"), "--output", str(out)], tmp_path)
    assert clash.returncode != 0
    assert out.read_text(encoding="utf-8") == "sentinel"
    for name, payload in before.items():
        assert (FIXTURES / name).read_bytes() == payload
