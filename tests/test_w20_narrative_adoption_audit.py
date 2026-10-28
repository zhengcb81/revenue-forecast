"""W20 unit tests: read-only narrative adoption observation (pure core + in-process CLI).

Real layer (never faked): the DU11 synthetic public wire builder that passes
``validate_narrative_response``, the real ``consume_narrative_input`` adapter
(reader transport patched in-process only), the real draft ``run_forecast``
calculator, and the new read-only ``tools/narrative_adoption_audit`` core/CLI.

Faked layer only: none beyond the in-process reader patch documented above
(the subprocess transport stub lives in the W20 e2e module).
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from company_wiki_narrative_contracts import (  # noqa: E402
    NarrativeTransportError, validate_narrative_response,
)
from contracts.evidence import text_sha256  # noqa: E402
from forecast.dependencies import parameter_formula_refs  # noqa: E402
from revenue_core import run_forecast  # noqa: E402
from source_narrative_context import consume_narrative_input  # noqa: E402
from test_du11_narrative_citation_consumption import (  # noqa: E402
    PARAMETER, binding, document,
)
from test_du11_narrative_citation_wire import (  # noqa: E402
    descriptor, draft, resign, span_id, validated, wire,
)

from tools.narrative_adoption_audit import audit, cli  # noqa: E402


def real_chain(claim_id="w20_cl", parameter_id=PARAMETER, key="answer"):
    """One legal wire -> real consume -> real draft forecast -> adoption inputs."""
    context = validated("2")
    value = context.to_dict()
    data = document(context)
    entry = binding(value, key, claim_id=claim_id, parameter_id=parameter_id)
    with patch("source_narrative_context.read_narrative_context", return_value=context):
        linked, receipt = consume_narrative_input(
            data, request={"as_of_date": value["as_of_date"]}, bindings=[entry],
            source_id="filing", catalog_config=Path("isolated-not-opened.json"),
        )
    forecast = run_forecast(linked, mode="draft")
    return value, linked, receipt, forecast


def build(forecast, *, receipts=(), contexts=(), **kwargs):
    return audit.build_adoption_report(
        forecast, consumption_receipts=list(receipts), narrative_contexts=list(contexts),
        **kwargs
    )


def find(report, kind, item_id):
    matches = [i for i in report["items"] if i["kind"] == kind and i["id"] == item_id]
    assert len(matches) == 1, (kind, item_id, len(matches))
    return matches[0]


def codes(report):
    return [d["code"] for d in report["diagnostics"]]


def reasons(item):
    return item["reasons"]


# ---------------------------------------------------------------------------
# 1 same-source correct adoption is observed at the real driver slot
# ---------------------------------------------------------------------------

def test_same_source_correct_adoption_observed_at_driver_slot():
    value, linked, receipt, forecast = real_chain()
    report = build(forecast, receipts=[receipt], contexts=[value])
    assert report["schema_version"] == "rf-narrative-adoption-report/1"
    assert report["diagnostic_only_not_a_permission_gate"] is True
    span = find(report, "span", span_id(value, "answer"))
    assert span["status"] == "used"
    assert "used_via_segment_driver_slot" in reasons(span)
    slot = [c for c in span["cited_by"] if c["node_type"] == "segment_scenario_driver"]
    assert slot and slot[0]["ids"]["parameter_id"] == PARAMETER
    assert slot[0]["ids"]["year"] == "2026"
    claim = find(report, "claim", "w20_cl")
    assert claim["status"] == "used"
    assert "used_via_segment_driver_slot" in reasons(claim)
    source = find(report, "source", "filing")
    assert source["status"] == "used"
    assert report["counts"]["by_status"]["used"] >= 3
    # The claim chain keeps the canonical span urn, never the display text.
    assert span["id_scope"] == "canonical"
    assert claim["id_scope"] == "document_local_display_key"


# ---------------------------------------------------------------------------
# 2 one display key reused across sources must never be joined
# ---------------------------------------------------------------------------

def _second_source_context(claim_text="t1"):
    data = json.loads(json.dumps(descriptor()))
    data["lines"][0] = data["lines"][0] + " SECOND SOURCE"
    parts = draft(data, reading="2")
    parts["bundle"]["summary"]["draft"]["claims"][0]["claim_id"] = claim_text
    request, body, receipt = resign(parts["request"], parts["bundle"], parts["receipt"])
    return validate_narrative_response(request, body, receipt).to_dict(), data


def test_display_key_collision_across_sources_is_never_joined():
    value, linked, receipt, forecast = real_chain(claim_id="t1")
    other, other_desc = _second_source_context("t1")
    forged = {
        "schema_version": "revenue-narrative-consumption/1",
        "status": "consumed",
        "dependencies": [{
            "span_id": span_id(other, "answer", other_desc),
            "source_id": other["source_ref"]["source_id"],
            "source_sha256": other["source_ref"]["content_sha256"],
            "claim_id": "t1",
            "parameter_id": PARAMETER,
            "formula_refs": [{"segment": "Segment 0"}],
        }],
    }
    report = build(forecast, receipts=[receipt, forged], contexts=[value, other])
    foreign = find(report, "span", span_id(other, "answer", other_desc))
    assert foreign["status"] == "unverifiable"
    assert "consumption_source_hash_mismatch" in reasons(foreign)
    assert "consumption_source_hash_mismatch" in codes(report)
    # The legitimate t1 chain keeps exactly its own citations.
    claim = find(report, "claim", "t1")
    assert claim["status"] == "used"
    assert all(c["ids"].get("parameter_id") == PARAMETER for c in claim["cited_by"])
    assert "display_key_collision_not_joined" in codes(report)


# ---------------------------------------------------------------------------
# 3 a context partition span is never numeric support
# ---------------------------------------------------------------------------

def test_context_partition_span_is_never_numeric_support():
    value, linked, receipt, forecast = real_chain()
    report = build(forecast, receipts=[receipt], contexts=[value])
    header = find(report, "span", span_id(value, "table_header"))
    assert header["support_use"] == "context_only"
    assert header["status"] == "not_used_when_provable"
    assert "context_partition_cannot_support" in reasons(header)
    # A receipt that nevertheless binds a context span is flagged, not obeyed.
    forged = json.loads(json.dumps(receipt))
    forged["dependencies"][0]["span_id"] = span_id(value, "table_header")
    flagged = build(forecast, receipts=[forged], contexts=[value])
    assert "context_span_bound_as_support" in codes(flagged)


# ---------------------------------------------------------------------------
# 4 a readable summary without any binding stays not_observed
# ---------------------------------------------------------------------------

def test_summary_readable_without_binding_stays_not_observed():
    value, linked, receipt, forecast = real_chain()
    report = build(forecast, contexts=[value])  # no consumption receipt at all
    summary = find(report, "summary_claim", "claim-replay-000")
    assert summary["status"] == "not_observed"
    assert "summary_claim_spans_not_bound" in reasons(summary)
    assert summary["cited_by"] == []
    assert report["counts"]["by_status"]["not_observed"] >= 1


# ---------------------------------------------------------------------------
# 5 caliber diagnostics: period, segment attribution, target currency
# ---------------------------------------------------------------------------

def minimal_forecast(**override):
    base = {
        "schema_version": "3.7", "engine_version": "test-engine", "company_name": "T",
        "as_of_date": "2026-01-01", "currency": "CNY", "unit": "million",
        "fiscal_year_end": "12-31", "base_year": 2025, "forecast_years": [2026, 2027],
        "parameter_trace": [{
            "parameter_id": "p_growth_2027", "kind": "analyst_assumption",
            "value": 1.1, "unit": "ratio", "period": "FY2027", "definition": "g",
            "dimension": "growth", "time_basis": "annual",
            "source_ids": ["s1"], "claim_ids": ["c1"], "scenario": "base",
            "rationale": "r", "currency": "CNY", "scale": "million",
        }],
        "evidence_claims": [{
            "claim_id": "c1", "source_id": "s1", "target_type": "parameter",
            "target_id": "p_growth_2027", "support_type": "rationale_support",
            "locator": "loc:v1/page:1/paragraph:2/chars:0-10", "excerpt": "growing",
            "excerpt_sha256": text_sha256("growing"), "content_sha256": "f" * 64,
            "capture_receipt_sha256": "e" * 64, "verification_status": "opened_and_checked",
            "verified_by": "t", "verified_date": "2026-01-01",
        }],
        "sources": [{
            "source_id": "s1", "source_type": "company_filing", "url": "https://x",
            "title": "t", "publisher": "p", "page_or_section": "1",
            "published_date": "2025-12-31", "accessed_date": "2026-01-01",
            "capture": {"snapshot_sha256": "f" * 64},
        }],
        "segments": [{
            "name": "Alpha", "base_revenue_parameter_id": "p_base",
            "scenarios": {"base": {
                "model": "direct_revenue", "rationale": "r",
                "driver_parameter_ids": {"revenue": ["p_growth_2027", "p_growth_2027"]},
            }},
        }],
        "management_target_coverage": {
            "communications": [], "counts": {},
            "targets": [{"target_id": "tg1", "raw_currency": "USD", "source_ids": ["s1"]}],
        },
    }
    base.update(override)
    return base


def test_caliber_diagnostics_period_segment_currency():
    forecast = minimal_forecast()
    forecast["growth_driver_analysis"] = {"status": "modeled", "drivers": [{
        "driver_id": "d1", "title": "t", "thesis": "s", "causal_chain": ["a", "b"],
        "parameter_ids": ["p_growth_2027"], "segment_attribution": [
            {"segment_name": "Ghost", "weight": 1.0}],
        "horizon": {"start_year": 2026, "end_year": 2027}, "persistence": "multi_year",
        "persistence_rationale": "r", "evidence_nodes": [], "leading_indicators": ["x"],
        "falsifiers": ["y"], "counterevidence_status": "searched_none_found",
        "counterevidence_rationale": "r",
    }]}
    report = build(forecast)
    found = codes(report)
    assert "period_mismatch_at_node" in found      # FY2027 param sits in the 2026 slot
    assert "unknown_segment_attribution" in found  # Ghost is not a modeled segment
    assert "target_currency_mismatch" in found     # USD target on a CNY document
    claim = find(report, "claim", "c1")
    assert claim["status"] == "used"  # caliber diagnostics do not demote the chain


# ---------------------------------------------------------------------------
# 6 one evidence item cited by many nodes counts once
# ---------------------------------------------------------------------------

def test_multi_node_citation_counts_item_once():
    forecast = minimal_forecast()
    forecast["research_coverage"] = {"counts": {}, "dimensions": [
        {"dimension": "growth_curve", "status": "modeled_driver", "conclusion": "c",
         "revenue_mechanism": "m", "parameter_ids": ["p_growth_2027"],
         "source_ids": ["s1"], "rationale": "r"},
    ]}
    forecast["growth_driver_analysis"] = {"status": "modeled", "drivers": [{
        "driver_id": "d1", "title": "t", "thesis": "s", "causal_chain": ["a", "b"],
        "parameter_ids": ["p_growth_2027"], "segment_attribution": [
            {"segment_name": "Alpha", "weight": 1.0}],
        "horizon": {"start_year": 2026, "end_year": 2027}, "persistence": "multi_year",
        "persistence_rationale": "r", "evidence_nodes": [], "leading_indicators": ["x"],
        "falsifiers": ["y"], "counterevidence_status": "searched_none_found",
        "counterevidence_rationale": "r",
    }]}
    report = build(forecast)
    claim = find(report, "claim", "c1")
    node_types = {c["node_type"] for c in claim["cited_by"]}
    assert node_types == {
        "segment_scenario_driver", "coverage_dimension_parameter", "driver_tree_parameter",
    }
    assert sum(1 for i in report["items"] if i["kind"] == "claim" and i["id"] == "c1") == 1
    assert report["counts"]["by_kind"]["claim"] == 1
    assert report["counts"]["items"] == len(report["items"])


# ---------------------------------------------------------------------------
# 7 old and minimal formats stay observable
# ---------------------------------------------------------------------------

def test_old_reading_schema_and_minimal_forecast_stay_observable():
    legacy = validated("1").to_dict()
    value, linked, receipt, forecast = real_chain()
    report = build(forecast, contexts=[legacy])
    assert "old_reading_schema_no_support_partition" in codes(report)
    assert all(i["support_use"] in (None, "unknown") for i in report["items"]
               if i["kind"] == "span")
    minimal = build(minimal_forecast())
    assert "node_family_missing:growth_driver_analysis" in codes(minimal)
    assert "node_family_missing:probability_weighted_forecast" in codes(minimal)
    assert find(minimal, "claim", "c1")["status"] == "used"
    # A consumption receipt without citation_trace keeps its dependencies.
    stripped = {k: v for k, v in receipt.items() if k != "citation_trace"}
    kept = build(forecast, receipts=[stripped], contexts=[value])
    assert find(kept, "span", span_id(value, "answer"))["status"] == "used"


# ---------------------------------------------------------------------------
# 8 hash mismatch is flagged; a missing hash stays lenient
# ---------------------------------------------------------------------------

def test_hash_mismatch_flagged_and_missing_hash_lenient():
    value, linked, receipt, forecast = real_chain()
    wrong = json.loads(json.dumps(receipt))
    wrong["dependencies"][0]["source_sha256"] = "0" * 64
    report = build(forecast, receipts=[wrong], contexts=[value])
    assert find(report, "span", span_id(value, "answer"))["status"] == "unverifiable"
    assert "consumption_source_hash_mismatch" in codes(report)
    missing = json.loads(json.dumps(receipt))
    del missing["dependencies"][0]["source_sha256"]
    lenient = build(forecast, receipts=[missing], contexts=[value])
    assert find(lenient, "span", span_id(value, "answer"))["status"] == "used"
    assert "hash_missing_unknown" in codes(lenient)


# ---------------------------------------------------------------------------
# 9 unknown fields never fabricate conclusions
# ---------------------------------------------------------------------------

def test_unknown_fields_never_fabricate_conclusions():
    value, linked, receipt, forecast = real_chain()
    noisy = json.loads(json.dumps(receipt))
    noisy["adoption_verdict"] = "PASS"  # unknown material must be ignored
    noisy["dependencies"][0]["confidence"] = 0.99
    forecast_noise = json.loads(json.dumps(forecast))
    forecast_noise["adoption_rate"] = 0.9
    report = build(forecast_noise, receipts=[noisy], contexts=[value])
    assert "unknown_fields_ignored" in codes(report)
    assert "unknown_field_ignored:adoption_rate" in codes(report)
    assert not any("PASS" in json.dumps(i) or "0.99" in json.dumps(i)
                   for i in report["items"])
    assert report["counts"]["by_status"].get("used", 0) >= 3
    # A refused narrative wire is a named diagnostic, never invented items.
    request, body, receipt_bytes = wire("2")
    tampered = body[:-1] + b"X"
    with pytest.raises(NarrativeTransportError):
        audit.validate_narrative_wire(request, tampered, receipt_bytes)
    ok = audit.validate_narrative_wire(request, body, receipt_bytes)
    assert ok["schema_version"] == "revenue-narrative-context/1"


# ---------------------------------------------------------------------------
# 10 the report is deterministic and byte stable
# ---------------------------------------------------------------------------

def test_report_is_deterministic_and_byte_stable():
    value, linked, receipt, forecast = real_chain()
    first = build(forecast, receipts=[receipt], contexts=[value])
    second = build(forecast, receipts=[receipt], contexts=[value])
    assert audit.canonical_report_bytes(first) == audit.canonical_report_bytes(second)


# ---------------------------------------------------------------------------
# 11 scaling stays near linear and the resource bound is enforced
# ---------------------------------------------------------------------------

def scaled_forecast(n):
    trace, claims, sources = [], [], []
    for index in range(n):
        trace.append({
            "parameter_id": f"p{index}", "kind": "analyst_assumption", "value": 1.0,
            "unit": "ratio", "period": "FY2026", "definition": "d", "dimension": "growth",
            "time_basis": "annual", "source_ids": [f"s{index}"],
            "claim_ids": [f"c{index}"], "scenario": "base", "rationale": "r",
            "currency": "CNY", "scale": "million",
        })
        claims.append({
            "claim_id": f"c{index}", "source_id": f"s{index}",
            "target_type": "parameter", "target_id": f"p{index}",
            "support_type": "rationale_support", "locator": "loc", "excerpt": "e",
            "excerpt_sha256": text_sha256("e"), "content_sha256": "f" * 64,
            "capture_receipt_sha256": "e" * 64,
            "verification_status": "opened_and_checked", "verified_by": "t",
            "verified_date": "2026-01-01",
        })
        sources.append({
            "source_id": f"s{index}", "source_type": "company_filing",
            "url": "https://x", "title": "t", "publisher": "p", "page_or_section": "1",
            "published_date": "2025-12-31", "accessed_date": "2026-01-01",
            "capture": {"snapshot_sha256": "f" * 64},
        })
    forecast = minimal_forecast()
    forecast["parameter_trace"] = trace
    forecast["evidence_claims"] = claims
    forecast["sources"] = sources
    return forecast


def test_scaling_is_linear_and_resource_bound_enforced():
    small, large = scaled_forecast(1200), scaled_forecast(2400)
    start = time.perf_counter()
    first = build(small)
    t1 = time.perf_counter() - start
    start = time.perf_counter()
    second = build(large)
    t2 = time.perf_counter() - start
    assert second["counts"]["items"] == 2 * first["counts"]["items"]
    if t1 > 0.05:
        assert t2 < max(4.0 * t1, t1 + 1.0), (t1, t2)
    with pytest.raises(audit.AdoptionAuditError) as caught:
        build(small, max_items=10)
    assert caught.value.code == "resource_limit"
    assert build(small, max_items=5000)["resource"]["items_capped"] is False


# ---------------------------------------------------------------------------
# 12 the wired closure agrees with the existing traversal
# ---------------------------------------------------------------------------

def test_wired_closure_agrees_with_parameter_formula_refs():
    value, linked, receipt, forecast = real_chain()
    report = build(forecast, receipts=[receipt], contexts=[value])
    wired = report["node_index"]["wired_parameter_ids"]
    table = {p["parameter_id"]: p for p in linked["parameters"]}
    for parameter in linked["parameters"]:
        has_refs = bool(parameter_formula_refs(
            linked, parameter["parameter_id"], table))
        if has_refs:
            # the existing traversal's reachable set is inside our closure
            assert parameter["parameter_id"] in wired, parameter["parameter_id"]


# ---------------------------------------------------------------------------
# 13 CLI: new output only, inputs untouched
# ---------------------------------------------------------------------------

def test_cli_writes_new_output_only_and_preserves_inputs(tmp_path, capsys, monkeypatch):
    value, linked, receipt, forecast = real_chain()
    monkeypatch.chdir(tmp_path)
    forecast_path = tmp_path / "forecast.json"
    receipt_path = tmp_path / "consumption.json"
    forecast_path.write_text(json.dumps(forecast, ensure_ascii=False), encoding="utf-8")
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False), encoding="utf-8")
    before = (forecast_path.read_bytes(), receipt_path.read_bytes())
    existing = tmp_path / "out.json"
    existing.write_text("sentinel", encoding="utf-8")
    capsys.readouterr()
    assert cli.main([
        "--forecast", str(forecast_path), "--consumption", str(receipt_path),
        "--output", str(existing),
    ]) == 2
    assert existing.read_text(encoding="utf-8") == "sentinel"
    fresh = tmp_path / "report.json"
    assert cli.main([
        "--forecast", str(forecast_path), "--consumption", str(receipt_path),
        "--output", str(fresh),
    ]) == 0
    assert capsys.readouterr().out == ""  # --output silences stdout
    report = json.loads(fresh.read_text(encoding="utf-8"))
    assert report["schema_version"] == "rf-narrative-adoption-report/1"
    assert cli.main(["--forecast", str(forecast_path),
                     "--consumption", str(receipt_path)]) == 0
    again = json.loads(capsys.readouterr().out)
    assert again == report
    assert (forecast_path.read_bytes(), receipt_path.read_bytes()) == before
    # The output path never equals an input path.
    assert cli.main([
        "--forecast", str(forecast_path), "--output", str(forecast_path),
    ]) == 2
    assert json.loads(forecast_path.read_text(encoding="utf-8"))["company_name"]


# ---------------------------------------------------------------------------
# 14 CLI cross checks for --input and --snapshot
# ---------------------------------------------------------------------------

def test_cli_supports_snapshot_and_input_cross_checks(tmp_path, capsys, monkeypatch):
    value, linked, receipt, forecast = real_chain()
    monkeypatch.chdir(tmp_path)
    forecast_path = tmp_path / "forecast.json"
    input_path = tmp_path / "input.json"
    forecast_path.write_text(json.dumps(forecast, ensure_ascii=False), encoding="utf-8")
    input_path.write_text(json.dumps(linked, ensure_ascii=False), encoding="utf-8")
    assert cli.main(["--forecast", str(forecast_path), "--input", str(input_path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["cross_checks"]["input_match"] is True
    stale = json.loads(json.dumps(linked))
    stale["company_name"] = "Someone Else"
    input_path.write_text(json.dumps(stale, ensure_ascii=False), encoding="utf-8")
    assert cli.main(["--forecast", str(forecast_path), "--input", str(input_path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["cross_checks"]["input_match"] is False
    assert "input_forecast_binding_mismatch" in codes(report)
    snapshot = {
        "input_sha256": forecast["input_sha256"],
        "forecast_result": {"result_sha256": forecast["result_sha256"]},
    }
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
    assert cli.main(["--forecast", str(forecast_path),
                     "--snapshot", str(snapshot_path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["cross_checks"]["snapshot_match"] is True
    snapshot["forecast_result"]["result_sha256"] = "0" * 64
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
    assert cli.main(["--forecast", str(forecast_path),
                     "--snapshot", str(snapshot_path)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["cross_checks"]["snapshot_match"] is False
    assert "snapshot_binding_mismatch" in codes(report)


# ---------------------------------------------------------------------------
# 15 unsupported consumption material is diagnosed, never guessed
# ---------------------------------------------------------------------------

def test_broken_consumption_material_is_diagnosed():
    value, linked, receipt, forecast = real_chain()
    unknown_schema = {"schema_version": "revenue-narrative-consumption/9",
                      "status": "consumed", "dependencies": []}
    missing_fields = {"schema_version": "revenue-narrative-consumption/1",
                      "status": "consumed",
                      "dependencies": [{"span_id": "urn:x", "claim_id": "nope",
                                        "parameter_id": "also_nope",
                                        "formula_refs": []}]}
    report = build(forecast, receipts=[unknown_schema, missing_fields], contexts=[value])
    found = codes(report)
    assert "consumption_schema_unknown" in found
    assert "receipt_claim_not_in_input" in found
    assert "receipt_parameter_not_in_input" in found
    broken = find(report, "span", "urn:x")
    assert broken["status"] == "unverifiable"
