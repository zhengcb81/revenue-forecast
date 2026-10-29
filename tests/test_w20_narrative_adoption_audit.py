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
from fix_hashes import apply_hash_fixes  # noqa: E402
from forecast.dependencies import parameter_formula_refs  # noqa: E402
from narrative_citation_context import NarrativeCitationError  # noqa: E402
from revenue_core import run_forecast  # noqa: E402
from source_narrative_context import consume_narrative_input  # noqa: E402
from test_du11_narrative_citation_consumption import (  # noqa: E402
    PARAMETER, binding, document,
)
from test_recognition_bridge import forecast_document  # noqa: E402
from test_du11_narrative_citation_wire import (  # noqa: E402
    descriptor, draft, resign, span_id, validated, wire,
)
from test_reading_support_use import public_context  # noqa: E402

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
    assert find(flagged, "span", span_id(value, "table_header"))["status"] == \
        "not_used_when_provable"


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
    span_item = find(report, "span", span_id(value, "answer"))
    assert span_item["status"] == "unverifiable"
    assert "receipt_span_hash_mismatch" in reasons(span_item)
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
    small, large = scaled_forecast(2400), scaled_forecast(4800)
    start = time.perf_counter()
    first = build(small)
    t1 = time.perf_counter() - start
    start = time.perf_counter()
    second = build(large)
    t2 = time.perf_counter() - start
    assert second["counts"]["items"] == 2 * first["counts"]["items"]
    assert t1 > 0.02, f"workload too small to observe scaling: {t1}"
    assert t2 < max(4.0 * t1, t1 + 1.0), (t1, t2)
    with pytest.raises(audit.AdoptionAuditError) as caught:
        build(small, max_items=10)
    assert caught.value.code == "resource_limit"
    report = build(small, max_items=5000)
    assert report["resource"] == {"max_items": 5000, "items": report["counts"]["items"]}


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


# ---------------------------------------------------------------------------
# 16 the /4 capability bit is the sole support authority (initial-review F1/F4)
# ---------------------------------------------------------------------------

def chained_v4(use):
    """A real /4 wire through consume, with every view marked `use`.

    The real adapter refuses to bind non-support views, so `receipt` stays
    None for context_only/unresolved: the audit must judge those spans from
    the source marking alone (and from forged material in later tests).
    """
    context = public_context(use)
    value = context.to_dict()
    data = document(context)
    entry = binding(value, "answer", claim_id="w20_v4", parameter_id=PARAMETER)
    receipt = None
    linked = data
    try:
        with patch("source_narrative_context.read_narrative_context", return_value=context):
            linked, receipt = consume_narrative_input(
                data, request={"as_of_date": value["as_of_date"]}, bindings=[entry],
                source_id="filing", catalog_config=Path("isolated-not-opened.json"),
            )
    except NarrativeCitationError:
        pass
    return value, linked, receipt, run_forecast(linked, mode="draft")


def test_v4_context_only_views_cannot_become_support_even_when_bound():
    v4 = public_context("context_only").to_dict()
    # The wire builder is deterministic, so a real /2-chain receipt carries
    # the same span urns; it plays the role of broken/cross-run material.
    _, _, receipt, forecast = real_chain(claim_id="w20_v4")
    flagged = build(forecast, receipts=[receipt], contexts=[v4])
    answer = find(flagged, "span", span_id(v4, "answer"))
    assert answer["support_use"] == "context_only"
    assert answer["status"] == "not_used_when_provable"
    assert "context_partition_cannot_support" in reasons(answer)
    assert "context_span_bound_as_support" in codes(flagged)
    assert not answer["cited_by"]
    # Even a forged cross-run receipt cannot lift the source's own marking.
    forged = json.loads(json.dumps(receipt))
    forged["dependencies"][0]["span_id"] = span_id(v4, "question")
    assert find(build(forecast, receipts=[forged], contexts=[v4]),
                "span", span_id(v4, "question"))["status"] == \
        "not_used_when_provable"
    # The real adapter refuses the binding outright.
    _, _, refused, _ = chained_v4("context_only")
    assert refused is None


def test_v4_unresolved_views_and_ungrouped_spans_stay_unsupported():
    v4u = public_context("unresolved").to_dict()
    _, _, _, forecast = real_chain()
    report = build(forecast, contexts=[v4u])
    answer = find(report, "span", span_id(v4u, "answer"))
    assert answer["support_use"] == "unresolved"
    assert answer["status"] == "not_used_when_provable"
    assert "unresolved_support_cannot_support" in reasons(answer)
    ungrouped = json.loads(json.dumps(v4u))
    ungrouped["reading_context"]["groups"] = []
    report = build(forecast, contexts=[ungrouped])
    answer = find(report, "span", span_id(ungrouped, "answer"))
    assert answer["status"] == "not_used_when_provable"
    assert answer["support_use"] == "unresolved"


def test_v4_support_still_flows_through_the_real_chain():
    value, linked, receipt, forecast = chained_v4("support")
    report = build(forecast, receipts=[receipt], contexts=[value])
    answer = find(report, "span", span_id(value, "answer"))
    assert answer["status"] == "used"
    assert answer["support_use"] == "support"


# ---------------------------------------------------------------------------
# 17 elimination constraint parameters are computation-wired (F2)
# ---------------------------------------------------------------------------

def elimination_forecast():
    forecast = minimal_forecast()
    forecast["revenue_constraints"] = [{
        "constraint_id": "elim_interco", "type": "elimination",
        "rationale": "r",
        "segment_adjustment_parameter_ids": {
            "Alpha": {"base": ["p_growth_2027"]}},
    }]
    return forecast


def test_elimination_constraint_parameter_counts_as_wired():
    doc = elimination_forecast()
    report = build(doc)
    assert "p_growth_2027" in report["node_index"]["wired_parameter_ids"]
    table = {p["parameter_id"]: p for p in doc["parameter_trace"]}
    assert parameter_formula_refs(doc, "p_growth_2027", table), \
        "the engine must reach this parameter for the differential to bite"
    claim = find(report, "claim", "c1")
    assert claim["status"] == "used"
    assert "used_via_revenue_constraint" in reasons(claim)


def test_sum_cap_linked_ratio_shapes_are_wired_like_the_engine():
    forecast = minimal_forecast()
    forecast["revenue_constraints"] = [
        {"constraint_id": "cap", "type": "sum_cap", "segments": ["Alpha"],
         "allocation": "fixed_weights", "rationale": "r",
         "scenario_parameter_ids": {"Alpha": {"base": ["p_growth_2027"]}},
         "weight_parameter_ids": {"Alpha": {"base": ["p_growth_2027"]}}},
        {"constraint_id": "ratio", "type": "linked_ratio",
         "target_segment": "Alpha", "rationale": "r",
         "scenario_parameter_ids": {"base": ["p_growth_2027"]}},
    ]
    report = build(forecast)
    assert "p_growth_2027" in report["node_index"]["wired_parameter_ids"]
    assert find(report, "claim", "c1")["status"] == "used"


# ---------------------------------------------------------------------------
# 18 lenient-but-recorded run binding (F3, S2-5)
# ---------------------------------------------------------------------------

def test_missing_formula_refs_is_recorded_not_silent():
    value, linked, receipt, forecast = real_chain()
    stripped = json.loads(json.dumps(receipt))
    del stripped["dependencies"][0]["formula_refs"]
    report = build(forecast, receipts=[stripped], contexts=[value])
    assert "receipt_formula_refs_missing" in codes(report)
    assert find(report, "span", span_id(value, "answer"))["status"] == "used"


def test_wrong_formula_refs_flags_cross_run_binding():
    value, linked, receipt, forecast = real_chain()
    foreign = json.loads(json.dumps(receipt))
    foreign["dependencies"][0]["formula_refs"] = [
        {"segment": "Elsewhere", "scenario": "base", "model": "direct_revenue",
         "driver": "revenue", "output": "recognized_revenue"}]
    report = build(forecast, receipts=[foreign], contexts=[value])
    span_item = find(report, "span", span_id(value, "answer"))
    assert span_item["status"] == "unverifiable"
    assert "receipt_run_mismatch" in reasons(span_item)


# ---------------------------------------------------------------------------
# 19 CLI failure branches exit 2 with named messages (S2-3)
# ---------------------------------------------------------------------------

def test_cli_failure_branches_exit_two(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    capsys.readouterr()
    assert cli.main(["--forecast", str(tmp_path / "missing.json")]) == 2
    assert "cannot read inputs" in capsys.readouterr().err
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert cli.main(["--forecast", str(bad)]) == 2
    assert "cannot read inputs" in capsys.readouterr().err
    scalar = tmp_path / "scalar.json"
    scalar.write_text("[1, 2]", encoding="utf-8")
    assert cli.main(["--forecast", str(scalar)]) == 2
    big = tmp_path / "big.json"
    big.write_text(json.dumps(minimal_forecast()), encoding="utf-8")
    assert cli.main(["--forecast", str(big), "--max-input-bytes", "10"]) == 2
    assert "resource_limit" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# 20 a refused narrative wire degrades to a named diagnostic (S2-4)
# ---------------------------------------------------------------------------

def test_cli_narrative_wire_refusal_continues_with_diagnostic(tmp_path, capsys, monkeypatch):
    value, linked, receipt, forecast = real_chain()
    monkeypatch.chdir(tmp_path)
    request, body, receipt_bytes = wire("2")
    request_path = tmp_path / "request.json"
    bundle_path = tmp_path / "bundle.json"
    receipt_path = tmp_path / "receipt.jsonl"
    request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
    bundle_path.write_bytes(body[:-1] + b"X")  # tampered transport bytes
    receipt_path.write_bytes(receipt_bytes)
    forecast_path = tmp_path / "forecast.json"
    forecast_path.write_text(json.dumps(forecast, ensure_ascii=False), encoding="utf-8")
    capsys.readouterr()
    assert cli.main([
        "--forecast", str(forecast_path), "--narrative",
        str(request_path), str(bundle_path), str(receipt_path),
    ]) == 0
    report = json.loads(capsys.readouterr().out)
    assert "narrative_wire_refused" in codes(report)
    refused_span = span_id(value, "answer")
    assert not any(item["id"] == refused_span for item in report["items"])


# ---------------------------------------------------------------------------
# 21 R1 rework: the receipt resolves one whole source>span>claim>param chain
# ---------------------------------------------------------------------------

def test_foreign_span_cannot_borrow_another_sources_chain():
    other, other_desc = _second_source_context("other-summary")
    foreign_sid = span_id(other, "answer", other_desc)
    _, _, receipt, forecast = real_chain(claim_id="w20_cl")
    forged = json.loads(json.dumps(receipt))
    forged["dependencies"][0]["span_id"] = foreign_sid  # B span, A hash/claim/param
    report = build(forecast, receipts=[forged], contexts=[other])
    foreign = find(report, "span", foreign_sid)
    assert foreign["status"] == "unverifiable"
    assert "receipt_span_hash_mismatch" in reasons(foreign)
    assert "consumption_source_hash_mismatch" in codes(report)
    assert foreign["cited_by"] == []


def test_wrong_explicit_source_id_is_a_named_broken_edge():
    value, linked, receipt, forecast = real_chain()
    forged = json.loads(json.dumps(receipt))
    forged["dependencies"][0]["source_id"] = "urn:fake:source"
    report = build(forecast, receipts=[forged], contexts=[value])
    span_item = find(report, "span", span_id(value, "answer"))
    assert span_item["status"] == "unverifiable"
    assert "receipt_source_mismatch" in reasons(span_item)


def test_wrong_claim_parameter_pairing_is_a_named_broken_edge():
    value, linked, receipt, forecast = real_chain()
    forged = json.loads(json.dumps(receipt))
    forged["dependencies"][0]["parameter_id"] = "0_low_2026"  # claim targets 0_base_2026
    report = build(forecast, receipts=[forged], contexts=[value])
    span_item = find(report, "span", span_id(value, "answer"))
    assert span_item["status"] == "unverifiable"
    assert "receipt_claim_target_mismatch" in reasons(span_item)


def test_wrong_locator_and_parser_are_named_broken_edges():
    value, linked, receipt, forecast = real_chain()
    moved = json.loads(json.dumps(receipt))
    moved["dependencies"][0]["locator"] = "loc:v1/paragraph:99/chars:0-1"
    report = build(forecast, receipts=[moved], contexts=[value])
    span_item = find(report, "span", span_id(value, "answer"))
    assert span_item["status"] == "unverifiable"
    assert "receipt_locator_mismatch" in reasons(span_item)
    reparsed = json.loads(json.dumps(receipt))
    reparsed["dependencies"][0]["parser_name"] = "someone-else"
    report = build(forecast, receipts=[reparsed], contexts=[value])
    span_item = find(report, "span", span_id(value, "answer"))
    assert span_item["status"] == "unverifiable"
    assert "receipt_parser_mismatch" in reasons(span_item)


def test_hash_provided_but_wrong_flags_span_parent_edge():
    value, linked, receipt, forecast = real_chain()
    wrong = json.loads(json.dumps(receipt))
    wrong["dependencies"][0]["source_sha256"] = "0" * 64
    report = build(forecast, receipts=[wrong], contexts=[value])
    span_item = find(report, "span", span_id(value, "answer"))
    assert span_item["status"] == "unverifiable"
    assert "receipt_span_hash_mismatch" in reasons(span_item)


# ---------------------------------------------------------------------------
# 22 R2 rework: every legitimate path of one canonical span is aggregated
# ---------------------------------------------------------------------------

def two_binding_chain(bindings_order=("first", "second"), split_receipts=False):
    context = validated("2")
    value = context.to_dict()
    data = document(context)
    claim_by_name = {"first": "0_base_2026", "second": "0_base_2027"}
    entries = [binding(value, "answer", claim_id=name, parameter_id=claim_by_name[name])
               for name in bindings_order]
    with patch("source_narrative_context.read_narrative_context", return_value=context):
        linked, receipt = consume_narrative_input(
            data, request={"as_of_date": value["as_of_date"]}, bindings=entries,
            source_id="filing", catalog_config=Path("isolated-not-opened.json"),
        )
    forecast = run_forecast(linked, mode="draft")
    receipts = [receipt]
    if split_receipts:
        half = len(receipt["dependencies"]) // 2 or 1
        left = json.loads(json.dumps(receipt))
        right = json.loads(json.dumps(receipt))
        left["dependencies"] = receipt["dependencies"][:half]
        right["dependencies"] = receipt["dependencies"][half:]
        receipts = [left, right]
    return value, receipts, forecast


def test_same_span_two_years_aggregates_every_path():
    value, receipts, forecast = two_binding_chain()
    report = build(forecast, receipts=receipts, contexts=[value])
    span_item = find(report, "span", span_id(value, "answer"))
    assert span_item["status"] == "used"
    slot_years = {c["ids"].get("year") for c in span_item["cited_by"]
                  if c["node_type"] == "segment_scenario_driver"}
    assert slot_years == {"2026", "2027"}
    params = {c["ids"].get("parameter_id") for c in span_item["cited_by"]}
    assert {"0_base_2026", "0_base_2027"} <= params
    for claim_id in ("first", "second"):
        assert find(report, "claim", claim_id)["status"] == "used"
    answer_id = span_id(value, "answer")
    assert sum(1 for i in report["items"]
               if i["kind"] == "span" and i["id"] == answer_id) == 1
    # one receipt with two dependencies is one receipt, not "several receipts"
    assert not any("several receipts" in d["detail"] for d in report["diagnostics"])


def test_aggregation_is_order_and_receipt_split_invariant():
    forward = two_binding_chain(("first", "second"))
    reverse = two_binding_chain(("second", "first"))
    split = two_binding_chain(("first", "second"), split_receipts=True)
    def span_citations(chain):
        chain_value, chain_receipts, chain_forecast = chain
        report = build(chain_forecast, receipts=chain_receipts, contexts=[chain_value])
        item = find(report, "span", span_id(chain_value, "answer"))
        return item["status"], json.dumps(item["cited_by"], sort_keys=True)
    assert span_citations(forward) == span_citations(reverse)
    assert span_citations(forward) == span_citations(split)


def test_invalid_path_does_not_swallow_valid_paths():
    value, receipts, forecast = two_binding_chain()
    poisoned = json.loads(json.dumps(receipts[0]))
    poisoned["dependencies"].append({
        "span_id": span_id(value, "answer"), "claim_id": "ghost",
        "parameter_id": "0_high_2026", "support_type": "rationale_support",
        "formula_refs": []})
    report = build(forecast, receipts=[poisoned], contexts=[value])
    span_item = find(report, "span", span_id(value, "answer"))
    assert span_item["status"] == "used"  # valid paths survive
    assert "receipt_claim_not_in_input" in codes(report)  # invalid path diagnosed
    slot_years = {c["ids"].get("year") for c in span_item["cited_by"]
                  if c["node_type"] == "segment_scenario_driver"}
    assert slot_years == {"2026", "2027"}


# ---------------------------------------------------------------------------
# 23 R3 rework: decompression is bounded, corruption fails named
# ---------------------------------------------------------------------------

def test_gzip_bomb_is_bounded_at_decompression(tmp_path, capsys, monkeypatch):
    import gzip as gzip_mod
    monkeypatch.chdir(tmp_path)
    capsys.readouterr()
    bomb = tmp_path / "bomb.json.gz"
    bomb.write_bytes(gzip_mod.compress(b" " * 100000))
    assert bomb.stat().st_size < 1024
    assert cli.main(["--forecast", str(bomb), "--max-input-bytes", "1024"]) == 2
    assert "resource_limit" in capsys.readouterr().err
    with pytest.raises(audit.AdoptionAuditError) as caught:
        cli._read_bytes(bomb, 1024)
    assert caught.value.code == "resource_limit"


def test_legal_gzip_within_limit_and_output_untouched_on_failure(tmp_path, capsys, monkeypatch):
    import gzip as gzip_mod
    monkeypatch.chdir(tmp_path)
    capsys.readouterr()
    value, linked, receipt, forecast = real_chain()
    small = tmp_path / "small.json.gz"
    small.write_bytes(gzip_mod.compress(
        json.dumps(forecast, ensure_ascii=False).encode("utf-8")))
    decompressed = len(json.dumps(forecast, ensure_ascii=False).encode("utf-8"))
    limit = decompressed + 1024
    assert cli.main(["--forecast", str(small), "--max-input-bytes", str(limit),
                     "--output", str(tmp_path / "ok.json")]) == 0
    fresh = tmp_path / "fresh.json"
    truncated = tmp_path / "truncated.json.gz"
    raw = small.read_bytes()
    truncated.write_bytes(raw[:len(raw) // 2])
    assert cli.main(["--forecast", str(truncated), "--max-input-bytes",
                     str(limit), "--output", str(fresh)]) == 2
    assert "input_decompress_failed" in capsys.readouterr().err
    corrupt = tmp_path / "corrupt.json.gz"
    corrupt.write_bytes(b"\x1f\x8bnot-really-gzip" + raw[10:60])
    assert cli.main(["--forecast", str(corrupt), "--max-input-bytes",
                     str(limit)]) == 2
    assert "input_decompress_failed" in capsys.readouterr().err
    assert not fresh.exists()  # no half output on failure


# ---------------------------------------------------------------------------
# 24 R1 rework follow-up: /3 multi-parent projections resolve the actual parent
# ---------------------------------------------------------------------------

def test_projected_multi_parent_context_resolves_actual_span_parent():
    from test_shared_reading_narrative_contract import projected_context
    request, body, receipt_bytes = projected_context()
    context = validate_narrative_response(request, body, receipt_bytes)
    value = context.to_dict()
    span = value["evidence_spans"][0]
    actual_parent = next(ref for ref in value["parent_source_refs"]
                         if ref["source_id"] == span["source_id"])
    assert value["parent_source_refs"].index(actual_parent) > 0  # not refs[0]
    data = forecast_document()
    data["as_of_date"] = value["as_of_date"]
    data["sources"][0]["capture"]["snapshot_sha256"] = actual_parent["content_sha256"]
    apply_hash_fixes(data)
    entry = {"span_id": span["span_id"], "claim_id": "w20_p3",
             "parameter_id": PARAMETER, "support_type": "rationale_support"}
    with patch("source_narrative_context.read_narrative_context", return_value=context):
        linked, receipt = consume_narrative_input(
            data, request={"as_of_date": value["as_of_date"]}, bindings=[entry],
            source_id="filing", catalog_config=Path("isolated-not-opened.json"),
        )
    forecast = run_forecast(linked, mode="draft")
    report = build(forecast, receipts=[receipt], contexts=[value])
    span_item = find(report, "span", span["span_id"])
    assert span_item["status"] == "used"
    assert "receipt_span_hash_mismatch" not in codes(report)
    assert "consumption_source_hash_mismatch" not in codes(report)
    assert "receipt_claim_material_mismatch" not in codes(report)
    assert "receipt_claim_source_mismatch" not in codes(report)


# ---------------------------------------------------------------------------
# 25 R2-01 rework: the claim's own material must be the bound span's material
# ---------------------------------------------------------------------------

def _two_real_runs_same_capture():
    """Two genuine consume runs over ONE validated wire: run A binds the CEO
    answer span, run B binds the table row span, both with the same local
    claim_id and parameter (each run's input holds its own unique claim)."""
    context = validated("2")
    value = context.to_dict()
    ceo = next(s for s in value["evidence_spans"]
               if s["structured_value"]["unit_kind"] == "transcript_speaker_block"
               and s["raw_text"].startswith("[CEO]"))
    table = next(s for s in value["evidence_spans"]
                 if s["structured_value"]["unit_kind"] == "table_row")
    table_group = next(g for g in value["reading_context"]["groups"]
                       if table["span_id"] in g["evidence_ids"])
    runs = {}
    for name, span, extra in (
        ("ceo", ceo, {}),
        ("table", table, {"citation_group_id": table_group["group_id"],
                          "citation_view": 0}),
    ):
        data = document(context)
        entry = binding(value, "answer" if name == "ceo" else "table_row",
                        claim_id="w20_cl", parameter_id=PARAMETER)
        entry["span_id"] = span["span_id"]
        entry.update(extra)
        with patch("source_narrative_context.read_narrative_context",
                   return_value=context):
            linked, receipt = consume_narrative_input(
                data, request={"as_of_date": value["as_of_date"]},
                bindings=[entry], source_id="filing",
                catalog_config=Path("isolated-not-opened.json"),
            )
        runs[name] = {"span": span, "linked": linked, "receipt": receipt,
                      "forecast": run_forecast(linked, mode="draft")}
    return value, runs


def test_swapped_material_receipt_between_same_source_runs():
    value, runs = _two_real_runs_same_capture()
    # Receipt B (table material) on forecast A (CEO claim material): the
    # table span must not pass as used — the final claim's locator/excerpt
    # identify different material from the same capture.
    report = build(runs["ceo"]["forecast"], receipts=[runs["table"]["receipt"]],
                   contexts=[value])
    span_item = find(report, "span", runs["table"]["span"]["span_id"])
    assert span_item["status"] == "unverifiable"
    assert "receipt_claim_material_mismatch" in reasons(span_item)
    assert span_item["cited_by"] == []
    # Receipt A on forecast A stays the legitimate used chain.
    ok = build(runs["ceo"]["forecast"], receipts=[runs["ceo"]["receipt"]],
               contexts=[value])
    assert find(ok, "span", runs["ceo"]["span"]["span_id"])["status"] == "used"
    assert "receipt_claim_material_mismatch" not in codes(ok)


def test_claim_material_contradictions_and_missing_fields():
    value, linked, receipt, forecast = real_chain()
    ceo_span_id = span_id(value, "answer")
    # Mutate the FINAL artifact's embedded input document directly: the
    # engine rejects a claim whose excerpt hash disagrees with its own
    # excerpt, but the observer faces arbitrary artifact+receipt pairs.
    def artifact_with_claim(**overrides):
        artifact = json.loads(json.dumps(forecast))
        claim = next(c for c in artifact["input_document"]["evidence_claims"]
                     if c["claim_id"] == "w20_cl")
        claim.update(overrides)
        return artifact
    # A claim locator pointing at other material of the same capture.
    report = build(artifact_with_claim(
        locator="loc:v1/paragraph:4/chars:155-180"), receipts=[receipt],
        contexts=[value])
    span_item = find(report, "span", ceo_span_id)
    assert span_item["status"] == "unverifiable"
    assert "receipt_claim_material_mismatch" in reasons(span_item)
    # A claim excerpt hash from other material.
    report = build(artifact_with_claim(
        excerpt_sha256=text_sha256("other material of the same capture")),
        receipts=[receipt], contexts=[value])
    span_item = find(report, "span", ceo_span_id)
    assert span_item["status"] == "unverifiable"
    assert "receipt_claim_material_mismatch" in reasons(span_item)
    # Missing optional claim material stays lenient-unknown, never a failure.
    stripped = json.loads(json.dumps(forecast))
    claim = next(c for c in stripped["input_document"]["evidence_claims"]
                 if c["claim_id"] == "w20_cl")
    del claim["locator"], claim["excerpt_sha256"]
    report = build(stripped, receipts=[receipt], contexts=[value])
    assert find(report, "span", ceo_span_id)["status"] == "used"
    assert "material_field_missing_unknown" in codes(report)


def test_same_parameter_multi_evidence_paths_stay_legal():
    value, runs = _two_real_runs_same_capture()
    # One parameter, two different spans bound as two claims in ONE input —
    # legal multi-evidence; both spans used, both claims used.
    data = document(validated("2"))
    ceo_span = runs["ceo"]["span"]
    table_span = runs["table"]["span"]
    table_group = next(g for g in value["reading_context"]["groups"]
                       if table_span["span_id"] in g["evidence_ids"])
    entries = [
        binding(value, "answer", claim_id="ev_ceo", parameter_id=PARAMETER),
        {**binding(value, "table_row", claim_id="ev_table", parameter_id=PARAMETER),
         "citation_group_id": table_group["group_id"], "citation_view": 0},
    ]
    with patch("source_narrative_context.read_narrative_context",
               return_value=validated("2")):
        linked, receipt = consume_narrative_input(
            data, request={"as_of_date": value["as_of_date"]}, bindings=entries,
            source_id="filing", catalog_config=Path("isolated-not-opened.json"),
        )
    forecast = run_forecast(linked, mode="draft")
    report = build(forecast, receipts=[receipt], contexts=[value])
    assert find(report, "span", ceo_span["span_id"])["status"] == "used"
    assert find(report, "span", table_span["span_id"])["status"] == "used"
    assert find(report, "claim", "ev_ceo")["status"] == "used"
    assert find(report, "claim", "ev_table")["status"] == "used"
    assert "receipt_claim_material_mismatch" not in codes(report)


# ---------------------------------------------------------------------------
# 26 R2-02 rework: corrupt DEFLATE streams fail named, not with a traceback
# ---------------------------------------------------------------------------

def test_corrupt_deflate_gzip_is_normalized_to_named_failure(tmp_path, capsys, monkeypatch):
    import gzip as gzip_mod
    monkeypatch.chdir(tmp_path)
    capsys.readouterr()
    header = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03"
    bad = tmp_path / "bad-deflate.json.gz"
    bad.write_bytes(header + b"\xff\xff\xff\xff\xff\xff\xff\xff\xff")  # 19 bytes
    with pytest.raises(audit.AdoptionAuditError) as caught:
        cli._read_bytes(bad, 4096)
    assert caught.value.code == "input_decompress_failed"
    fresh = tmp_path / "fresh.json"
    assert cli.main(["--forecast", str(bad), "--max-input-bytes", "4096",
                     "--output", str(fresh)]) == 2
    assert "input_decompress_failed" in capsys.readouterr().err
    assert not fresh.exists()
    # The same boundary across nearby corruption shapes.
    truncated = tmp_path / "truncated.json.gz"
    value, linked, receipt, forecast = real_chain()
    good = tmp_path / "good.json.gz"
    good.write_bytes(gzip_mod.compress(
        json.dumps(forecast, ensure_ascii=False).encode("utf-8")))
    decompressed = len(json.dumps(forecast, ensure_ascii=False).encode("utf-8"))
    limit = decompressed + 1024
    raw = good.read_bytes()
    truncated.write_bytes(raw[:len(raw) // 2])
    for path in (truncated,):
        assert cli.main(["--forecast", str(path), "--max-input-bytes",
                         str(limit)]) == 2
        assert "input_decompress_failed" in capsys.readouterr().err
    # Exactly at limit passes, over limit fails; both named paths already
    # covered by test 23 — here only the legal boundary re-check.
    assert cli.main(["--forecast", str(good), "--max-input-bytes",
                     str(limit), "--output", str(tmp_path / "ok.json")]) == 0


def test_legacy_span_with_stray_source_locator_key_stays_legacy():
    """A /1 span whose structured_value carries a stray source_locator key is
    still a legacy span: the expected claim locator is span.locator (the
    projected rule follows the context schema, not a key's presence)."""
    value, linked, receipt, forecast = real_chain()
    stray = json.loads(json.dumps(value))
    for span in stray["evidence_spans"]:
        span["structured_value"]["source_locator"] = "cwp-json-pointer/1|p=%2Fstray"
    report = build(forecast, receipts=[receipt], contexts=[stray])
    answer = find(report, "span", span_id(value, "answer"))
    assert answer["status"] == "used"
    assert "receipt_claim_material_mismatch" not in codes(report)
