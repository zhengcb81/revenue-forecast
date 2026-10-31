"""Publication keeps full adopted source semantics; no IO/models in validation."""

from copy import deepcopy
import pytest

from test_narrative_summary_usage import example, choose, consume
from revenue_core import run_forecast
from revenue_report import render_markdown, _num, validate_published_forecast
from revenue_backtest import create_snapshot


@pytest.mark.parametrize("kind", ["raw", "projected", "assessed", "standalone"])
def test_summary_choice_survives_inside_native_claim(kind):
    request, context, data, binding, summary = example(kind)
    updated, receipt = consume(request, context, data, [choose(binding, summary)])
    claim = next(
        c for c in updated["evidence_claims"] if c["claim_id"] == binding["claim_id"]
    )
    proof = claim.get("narrative_summary_use")
    assert proof is not None, (
        "return-only side receipt loses adopted semantics at publication"
    )
    assert proof["schema_version"] == "revenue-summary-provenance/1"
    assert proof["narrative_ref"] == receipt["summary_use"]["narrative_ref"]
    assert proof["summary_claim"] == summary
    assert proof["entry"] == receipt["summary_use"]["entries"][0]
    assert {s["span_id"] for s in proof["evidence_spans"]} == set(
        summary["evidence_ids"] + summary.get("context_evidence_ids", [])
    )
    assert updated["parameters"] == data["parameters"] or all(
        p["value"] == q["value"]
        for p, q in zip(updated["parameters"], data["parameters"])
    )


@pytest.mark.parametrize("kind", ["raw", "projected", "assessed", "standalone"])
def test_native_publication_and_snapshot_keep_adoption_without_side_receipt(kind):
    request, context, data, binding, summary = example(kind)
    updated, receipt = consume(request, context, data, [choose(binding, summary)])
    forecast = run_forecast(updated)
    validate_published_forecast(forecast, updated)
    report = render_markdown(forecast)
    snapshot = create_snapshot(updated, "summary-persistence-test")
    for document in [forecast["input_document"], snapshot["input_document"]]:
        claim = next(
            c
            for c in document["evidence_claims"]
            if c["claim_id"] == binding["claim_id"]
        )
        assert claim.get("narrative_summary_use")
    assert receipt["summary_use"]["narrative_ref"]["artifact_sha256"] in report
    assert summary["claim_id"] in report
    assert receipt["summary_use"]["entries"][0]["research_reason"] in report


@pytest.mark.parametrize(
    "value", [0.00010996114816480902, -0.00010996114816480902, 1e-12]
)
def test_nonzero_small_value_never_renders_as_zero(value):
    assert float(_num(value).replace(",", "")) != 0


@pytest.mark.parametrize(
    "fault",
    [
        "missing_support",
        "missing_context",
        "raw_text",
        "summary_id",
        "artifact_sha",
        "source_sha",
        "context_as_support",
        "formula",
        "parameter",
        "context_schema",
    ],
)
def test_persisted_scope_source_and_native_dependency_tampering_is_rejected(fault):
    from revenue_core import validate_document

    request, context, data, binding, summary = example()
    updated, _ = consume(request, context, data, [choose(binding, summary)])
    claim = next(
        c for c in updated["evidence_claims"] if c["claim_id"] == binding["claim_id"]
    )
    proof = claim["narrative_summary_use"]
    if fault in {"missing_support", "missing_context"}:
        key = (
            "support_evidence_ids"
            if fault == "missing_support"
            else "context_evidence_ids"
        )
        removed = proof["entry"][key][0]
        proof["evidence_spans"] = [
            s for s in proof["evidence_spans"] if s["span_id"] != removed
        ]
    elif fault == "raw_text":
        proof["evidence_spans"][0]["raw_text"] += " invented"
    elif fault == "summary_id":
        proof["entry"]["summary_claim_id"] = "foreign"
    elif fault == "artifact_sha":
        proof["narrative_ref"]["artifact_sha256"] = "f" * 64
    elif fault == "source_sha":
        proof["source_ref"]["content_sha256"] = "f" * 64
    elif fault == "context_as_support":
        proof["entry"]["support_evidence_ids"] += proof["entry"]["context_evidence_ids"]
    elif fault == "formula":
        proof["entry"]["formula_refs"].append({"driver": "unrelated"})
    elif fault == "parameter":
        proof["entry"]["parameter_id"] = "unused"
    else:
        proof["context_schema_version"] = "unknown"
    with pytest.raises(ValueError):
        validate_document(updated)


def test_reason_changes_invalidate_existing_publication_anchor():
    request, context, data, binding, summary = example()
    updated, _ = consume(request, context, data, [choose(binding, summary)])
    forecast = run_forecast(updated)
    changed = deepcopy(updated)
    next(c for c in changed["evidence_claims"] if c["claim_id"] == binding["claim_id"])[
        "narrative_summary_use"
    ]["entry"]["research_reason"] += " changed after publication"
    with pytest.raises(ValueError):
        validate_published_forecast(forecast, changed)


def test_parameter_report_displays_its_actual_unit():
    request, context, data, binding, summary = example()
    updated, _ = consume(request, context, data, [choose(binding, summary)])
    forecast = run_forecast(updated)
    report = render_markdown(forecast)
    assert "| 数值 | 单位 |" in report
    for parameter in forecast["parameter_trace"]:
        assert parameter["unit"] in report


@pytest.mark.parametrize("fault", ["present_null", "parameter_unlinked"])
def test_adoption_requires_present_proof_and_parameter_backlink(fault):
    from revenue_core import validate_document

    request, context, data, binding, summary = example()
    updated, _ = consume(request, context, data, [choose(binding, summary)])
    claim = next(
        c for c in updated["evidence_claims"] if c["claim_id"] == binding["claim_id"]
    )
    if fault == "present_null":
        claim["narrative_summary_use"] = None
    else:
        parameter = next(
            p
            for p in updated["parameters"]
            if p["parameter_id"] == binding["parameter_id"]
        )
        parameter["claim_ids"].remove(claim["claim_id"])
    with pytest.raises(ValueError):
        validate_document(updated)


@pytest.mark.parametrize(
    "fault", ["parent_sha", "projection_id", "pointer", "byte_range"]
)
def test_projected_provenance_reuses_parent_pointer_and_byte_contract(fault):
    from contracts.evidence import canonical_sha256
    from company_wiki_narrative_contracts import SPAN_PREFIX
    from narrative_citation_context import resolve_span, citation_dependency
    from revenue_core import validate_document

    request, context, data, binding, summary = example("projected")
    updated, _ = consume(request, context, data, [choose(binding, summary)])
    claim = next(
        c for c in updated["evidence_claims"] if c["claim_id"] == binding["claim_id"]
    )
    proof = claim["narrative_summary_use"]
    span = proof["evidence_spans"][0]
    projected = span["structured_value"]
    if fault == "parent_sha":
        projected["parent_content_sha256"] = "f" * 64
    elif fault == "projection_id":
        projected["projection_id"] += "-different-subject"
    elif fault == "pointer":
        projected["record_pointer"] = "/foreign-record"
    else:
        projected["encoded_body_range"] = [0, proof["source_ref"]["byte_size"] + 100]
    old = span["span_id"]
    span["output_sha256"] = canonical_sha256(
        {"raw_text": span["raw_text"], "structured_value": projected}
    )
    span["span_id"] = SPAN_PREFIX + canonical_sha256(
        {
            "source_id": span["source_id"],
            "locator": span["locator"],
            "output_sha256": span["output_sha256"],
        }
    )
    new = span["span_id"]

    def rename(value):
        if isinstance(value, dict):
            return {k: rename(v) for k, v in value.items()}
        if isinstance(value, list):
            return [rename(v) for v in value]
        return new if value == old else value

    proof = claim["narrative_summary_use"] = rename(proof)
    proof["entry"]["summary_claim_sha256"] = canonical_sha256(proof["summary_claim"])
    local = {
        "schema_version": proof["context_schema_version"],
        "evidence_spans": proof["evidence_spans"],
        "reading_context": proof["reading_context"],
    }
    old_citation = proof["entry"]["citation"]
    resolution = resolve_span(
        local,
        span_id=new,
        group_id=old_citation["group_id"],
        view=old_citation["view_index"],
    )
    proof["entry"]["citation"] = citation_dependency(
        resolution=resolution,
        claim_id=claim["claim_id"],
        parameter_id=claim["target_id"],
    )
    with pytest.raises(ValueError):
        validate_document(updated)
