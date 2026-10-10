"""Read-only economic-support-diagnostics/1 CLI over static native fixtures.

The CLI must never write the input, sources or any production registry, must
not call models or downloads, and every non-supported cell must carry concrete
calibration/parameter/claim-ID reasons instead of one generic "insufficient"."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

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


def replace_parameter_references(value, replacements):
    if isinstance(value, str):
        return replacements.get(value, value)
    if isinstance(value, list):
        replaced = [replace_parameter_references(item, replacements) for item in value]
        return list(dict.fromkeys(replaced)) if all(isinstance(item, str) for item in replaced) else replaced
    if isinstance(value, dict):
        return {key: replace_parameter_references(item, replacements) for key, item in value.items()}
    return value


def shared_root_document():
    from test_research_evidence_roles import calibrated_document

    document = calibrated_document()
    replacements = {}
    for scenario in ("low", "base", "high"):
        shared = f"0_{scenario}_2026"
        replacements[f"1_{scenario}_2026"] = shared
        document["segments"][1]["scenarios"][scenario]["driver_parameter_ids"]["revenue"][0] = shared
    for key in ("research_coverage", "growth_driver_tree"):
        document[key] = replace_parameter_references(document[key], replacements)
    return document


def support_cell(diagnostics, segment, scenario, year):
    return next(entry for row in diagnostics["segments"] if row["segment"] == segment
                for entry in row["entries"] if entry["scenario"] == scenario and entry["year"] == str(year))


def diagnose_document(document):
    from research_support_diagnostics import build_support_diagnostics

    return build_support_diagnostics(document, "0" * 64)


def test_shared_root_does_not_borrow_another_segments_calibration_scope():
    document = shared_root_document()
    before = deepcopy(document)
    diagnostics = diagnose_document(document)  # Actual native validation remains legal.
    assert document == before
    for scenario in ("low", "base", "high"):
        a = support_cell(diagnostics, "Segment A", scenario, 2026)
        b = support_cell(diagnostics, "Segment B", scenario, 2026)
        assert a["status"] == "supported"
        assert a["calibration_ids"] == ["reference_bridge"]
        assert b["status"] == "unsupported", b
        assert b["calibration_ids"] == b["claim_ids"] == b["supported_parameter_ids"] == []
        assert b["unsupported_parameter_ids"] == [f"0_{scenario}_2026"]
        assert "calibration_scope_not_covering:reference_bridge:Segment B" in b["reasons"]


def add_segment_b_calibration(document):
    research = document["operating_research"]
    calibration = deepcopy(research["calibrations"][0])
    calibration["calibration_id"] = "reference_bridge_b"
    calibration["scope"] = "Segment B"
    claims = {claim["claim_id"]: claim for claim in document["evidence_claims"]}
    observations = {row["claim_id"]: row for row in research["observations"]}
    replacements = {}
    for old in calibration["source_claim_ids"]:
        new = f"{old}_segment_b"
        replacements[old] = new
        claim = deepcopy(claims[old])
        claim["claim_id"] = new
        document["evidence_claims"].append(claim)
        parameter = next(p for p in document["parameters"] if p["parameter_id"] == claim["target_id"])
        parameter["claim_ids"].append(new)
        observation = deepcopy(observations[old])
        observation["claim_id"] = new
        observation["scope"] = "Segment B"
        research["observations"].append(observation)
    calibration["source_claim_ids"] = [replacements[claim] for claim in calibration["source_claim_ids"]]
    research["calibrations"].append(calibration)
    return calibration["source_claim_ids"]


@pytest.mark.parametrize("reverse_calibrations", [False, True])
def test_shared_root_with_distinct_scoped_calibrations_keeps_each_cells_claims(reverse_calibrations):
    document = shared_root_document()
    b_claims = add_segment_b_calibration(document)
    a_claims = document["operating_research"]["calibrations"][0]["source_claim_ids"]
    if reverse_calibrations:
        document["operating_research"]["calibrations"].reverse()
    before = deepcopy(document)
    diagnostics = diagnose_document(document)
    assert document == before
    for scenario in ("low", "base", "high"):
        a = support_cell(diagnostics, "Segment A", scenario, 2026)
        b = support_cell(diagnostics, "Segment B", scenario, 2026)
        assert a["status"] == b["status"] == "supported"
        assert a["calibration_ids"] == ["reference_bridge"]
        assert b["calibration_ids"] == ["reference_bridge_b"]
        assert a["claim_ids"] == sorted(a_claims)
        assert b["claim_ids"] == sorted(b_claims)
        assert support_cell(diagnostics, "Segment B", scenario, 2027)["status"] == "unsupported"


def test_company_scope_covers_shared_roots_in_each_actual_cell():
    document = shared_root_document()
    research = document["operating_research"]
    research["calibrations"][0]["scope"] = document["company_name"]
    for observation in research["observations"]:
        observation["scope"] = document["company_name"]
    diagnostics = diagnose_document(document)
    for segment in ("Segment A", "Segment B"):
        for scenario in ("low", "base", "high"):
            entry = support_cell(diagnostics, segment, scenario, 2026)
            assert entry["status"] == "supported"
            assert entry["calibration_ids"] == ["reference_bridge"]
            assert entry["reasons"] == []
            assert support_cell(diagnostics, segment, scenario, 2027)["status"] == "unsupported"
