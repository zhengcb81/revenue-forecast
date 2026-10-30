"""Synthetic engineering proof only; no real company/forecast adoption is claimed."""

from copy import deepcopy
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests")]
from company_wiki_narrative_contracts import (  # noqa: E402
    NarrativeContext,
    validate_narrative_response,
)  # noqa: E402
from contracts.evidence import canonical_sha256  # noqa: E402
from fix_hashes import apply_hash_fixes  # noqa: E402
from source_narrative_context import consume_narrative_input, narrative_read_receipt  # noqa: E402
from test_du11_narrative_citation_wire import wire, span_id  # noqa: E402
from test_du11_narrative_citation_projection import view_wire  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402
from test_assessed_narrative_consumer import recipe_wire  # noqa: E402

PARAMETER = "0_base_2026"
REASON = "Use this checked operational statement as rationale for the existing native driver, retaining its limits."


def example(kind="raw"):
    if kind == "projected":
        request, body, receipt = view_wire()
    elif kind in {"assessed", "historical_assessed"}:
        request, bundle, receipt_value = recipe_wire(
            "reading-source-scoped/4.2.0"
            if kind == "historical_assessed"
            else "reading-source-scoped/4.3.0"
        )
        claim = bundle["summary"]["draft"]["claims"][0]
        claim["needs_review"] = True
        bundle["summary"]["draft"]["status"] = "needs_review"
        bundle["quality_status"] = receipt_value["quality_status"] = "needs_review"
        bundle["selection"].update(status="partial", coverage_complete=False)
        receipt_value["selection_status"] = "partial"
        bundle["summary_assessment"]["claims_sha256"] = canonical_sha256(
            bundle["summary"]["draft"]["claims"]
        )
        from test_company_wiki_narrative_reader import _resign

        body, receipt = _resign(request, bundle, receipt_value)
    elif kind == "standalone":
        from test_company_wiki_narrative_reader import _valid

        request, body, receipt = _valid()
    else:
        request, body, receipt = wire(
            "2" if kind == "raw" else "1" if kind == "group_only" else None
        )
    context = validate_narrative_response(request, body, receipt)
    value = context.to_dict()
    if kind in {"raw", "group_only", "absent"}:
        selected = span_id(value, "answer")
    else:
        selected = value["summary"]["draft"]["claims"][0]["evidence_ids"][0]
    summary = next(
        c for c in value["summary"]["draft"]["claims"] if selected in c["evidence_ids"]
    )
    refs = value["parent_source_refs"] if kind == "projected" else [value["source_ref"]]
    selected_span = next(s for s in value["evidence_spans"] if s["span_id"] == selected)
    parent = next(r for r in refs if r["source_id"] == selected_span["source_id"])
    data = forecast_document()
    data["as_of_date"] = value["as_of_date"]
    data["sources"][0]["capture"]["snapshot_sha256"] = parent["content_sha256"]
    apply_hash_fixes(data)
    binding = {
        "span_id": selected,
        "claim_id": "summary_use_rf_claim",
        "parameter_id": PARAMETER,
        "support_type": "rationale_support",
    }
    return request, context, data, binding, summary


def choose(binding, summary, **extra):
    entry = deepcopy(binding)
    entry["summary_use"] = {
        "schema_version": "revenue-summary-use-binding/1",
        "summary_claim_id": summary["claim_id"],
        "research_reason": REASON,
        **extra,
    }
    return entry


def consume(request, context, data, bindings):
    with patch(
        "source_narrative_context.read_narrative_context", return_value=context
    ) as reader:
        result = consume_narrative_input(
            data,
            request=request,
            bindings=bindings,
            source_id="filing",
            catalog_config=Path("not-opened.json"),
        )
        assert reader.call_count == 1
        return result


@pytest.mark.parametrize(
    "kind", ["raw", "projected", "assessed", "historical_assessed", "standalone"]
)
def test_optional_lineage_binds_actual_claim_without_changing_native_values(kind):
    request, context, data, binding, summary = example(kind)
    frozen = deepcopy(data)
    legacy, old_receipt = consume(request, context, data, [binding])
    updated, receipt = consume(request, context, data, [choose(binding, summary)])
    assert data == frozen
    assert updated == legacy
    assert {k: v for k, v in receipt.items() if k != "summary_use"} == old_receipt
    claim = next(
        c for c in updated["evidence_claims"] if c["claim_id"] == binding["claim_id"]
    )
    original = next(
        s
        for s in context.to_dict()["evidence_spans"]
        if s["span_id"] == binding["span_id"]
    )
    assert claim["excerpt"] == original["raw_text"]
    if kind == "raw":
        assert claim["excerpt"] != summary["text"]
    assert claim["verification_status"] == "opened_and_checked"
    usage = receipt["summary_use"]
    assert usage["schema_version"] == "revenue-summary-use/1"
    assert usage["status"] == "used_in_parameter_rationale"
    assert usage["narrative_ref"] == context.to_dict()["narrative_ref"]
    assert usage["claims_sha256"] == canonical_sha256(
        context.to_dict()["summary"]["draft"]["claims"]
    )
    assert usage["quality_status"] == context.to_dict()["quality_status"]
    assert usage["selection"] == context.to_dict()["selection"]
    row = usage["entries"][0]
    assert row["summary_claim_id"] == summary["claim_id"]
    assert row["summary_claim_sha256"] == canonical_sha256(summary)
    assert row["claim_type"] == summary["claim_type"]
    assert row["modality"] == summary["modality"]
    assert row["needs_review"] is summary["needs_review"]
    assert row["support_evidence_ids"] == summary["evidence_ids"]
    assert row["context_evidence_ids"] == summary.get("context_evidence_ids", [])
    assert (
        row["rf_claim_id"] == binding["claim_id"] and row["parameter_id"] == PARAMETER
    )
    assert row["formula_refs"] == receipt["dependencies"][0]["formula_refs"]
    assert row["research_reason"] == REASON
    assert (
        row["citation"]["support_evidence_ids"]
        == receipt["citation_trace"]["dependencies"][0]["support_evidence_ids"]
    )
    assert (
        row["source_ref"]["content_sha256"]
        == data["sources"][0]["capture"]["snapshot_sha256"]
    )
    if kind == "assessed":
        assert usage["quality_status"] == "needs_review"
        assert usage["selection"]["status"] == "partial"
        assert (
            usage["semantic_status"]
            == usage["subfact_coverage_status"]
            == "not_evaluated"
        )
        assert usage["assessment_sha256"] == canonical_sha256(
            context.to_dict()["summary_assessment"]
        )
    row["support_evidence_ids"].clear()
    assert context.to_dict()["summary"]["draft"]["claims"][0]["evidence_ids"]


def test_no_selection_read_only_and_old_binding_do_not_claim_summary_use():
    request, context, data, binding, _ = example()
    assert "summary_use" not in narrative_read_receipt(context)
    _, read_only = consume(request, context, data, [])
    assert read_only["status"] == "not_consumed" and "summary_use" not in read_only
    _, used = consume(request, context, data, [binding])
    assert used["status"] == "consumed" and "summary_use" not in used


@pytest.mark.parametrize(
    "field",
    [
        "summary_claim_sha256",
        "summary_text",
        "quality_status",
        "narrative_ref",
        "formula_refs",
        "parameter_id",
        "status",
        "source_ref",
    ],
)
def test_caller_cannot_supply_claim_hash_text_quality_or_native_metadata(field):
    request, context, data, binding, summary = example()
    with pytest.raises(ValueError):
        consume(request, context, data, [choose(binding, summary, **{field: "forged"})])


@pytest.mark.parametrize(
    "change",
    [
        "unknown_id",
        "wrong_version",
        "empty_reason",
        "untrimmed_reason",
        "long_reason",
        "boolean_reason",
        "null_choice",
        "flat_choice",
        "duplicate_binding",
        "unused_parameter",
        "no_formula",
        "unsupported_support",
    ],
)
def test_invalid_selection_and_non_dependency_use_are_refused(change):
    request, context, data, binding, summary = example()
    entry = choose(binding, summary)
    entries = [entry]
    if change == "unknown_id":
        entry["summary_use"]["summary_claim_id"] = "absent"
    elif change == "wrong_version":
        entry["summary_use"]["schema_version"] = "revenue-summary-use-binding/2"
    elif change == "empty_reason":
        entry["summary_use"]["research_reason"] = ""
    elif change == "untrimmed_reason":
        entry["summary_use"]["research_reason"] = " reason "
    elif change == "long_reason":
        entry["summary_use"]["research_reason"] = "x" * 2049
    elif change == "boolean_reason":
        entry["summary_use"]["research_reason"] = True
    elif change == "null_choice":
        entry["summary_use"] = None
    elif change == "flat_choice":
        entry["summary_claim_id"] = summary["claim_id"]
    elif change == "duplicate_binding":
        entries.append(deepcopy(entry))
    elif change == "unused_parameter":
        entry["parameter_id"] = "not_used"
    elif change == "unsupported_support":
        entry["support_type"] = "quantitative_support"
    frozen = deepcopy(data)
    if change == "no_formula":
        with patch("source_narrative_context._formula_refs", return_value=[]):
            with pytest.raises(ValueError, match="actual segment formula"):
                consume(request, context, data, entries)
        assert data == frozen
        return
    with pytest.raises(ValueError):
        consume(request, context, data, entries)
    assert data == frozen


@pytest.mark.parametrize(
    "change",
    [
        "request_artifact",
        "receipt_artifact",
        "duplicate_summary_id",
        "claims_hash",
        "quality_laundering",
        "context_as_support",
        "missing_context",
        "foreign_group_support",
        "foreign_group_context",
        "foreign_parent",
    ],
)
def test_verified_context_pairing_and_summary_closure_cannot_be_forged(change):
    request, context, data, binding, summary = example(
        "assessed" if change == "claims_hash" else "raw"
    )
    value = context.to_dict()
    selected = next(
        c
        for c in value["summary"]["draft"]["claims"]
        if c["claim_id"] == summary["claim_id"]
    )
    if change == "request_artifact":
        request["narrative_ref"]["artifact_sha256"] = "f" * 64
    elif change == "receipt_artifact":
        value["read_receipt"]["narrative_ref"]["artifact_sha256"] = "f" * 64
    elif change == "duplicate_summary_id":
        value["summary"]["draft"]["claims"].append(deepcopy(selected))
    elif change == "claims_hash":
        selected["text"] += " changed after validation"
    elif change == "quality_laundering":
        selected["needs_review"] = True
    elif change == "context_as_support":
        selected["evidence_ids"] = list(selected["context_evidence_ids"])
    elif change == "missing_context":
        selected["context_evidence_ids"] = []
    elif change == "foreign_group_support":
        selected["evidence_ids"].append(span_id(value, "footnote"))
    elif change == "foreign_group_context":
        selected["context_evidence_ids"].append(span_id(value, "footnote"))
    else:
        other = next(
            s
            for s in value["evidence_spans"]
            if s["span_id"] == selected["context_evidence_ids"][0]
        )
        other["source_id"] = "foreign-original"
    with pytest.raises(ValueError):
        consume(request, NarrativeContext(value), data, [choose(binding, summary)])


def test_ambiguous_or_partitionless_closure_is_not_guessed():
    request, context, data, binding, summary = example("group_only")
    with pytest.raises(ValueError):
        consume(request, context, data, [choose(binding, summary)])
    request, context, data, binding, summary = example()
    binding["span_id"] = span_id(context.to_dict(), "table_row")
    summary = next(
        c
        for c in context.to_dict()["summary"]["draft"]["claims"]
        if binding["span_id"] in c["evidence_ids"]
    )
    with pytest.raises(ValueError, match="ambiguous"):
        consume(request, context, data, [choose(binding, summary)])


def test_valid_standalone_has_no_invented_context_partition():
    request, context, data, binding, summary = example("absent")
    # The synthetic answer's summary explicitly depends on question context;
    # without a published partition it cannot be promoted to a standalone.
    with pytest.raises(ValueError):
        consume(request, context, data, [choose(binding, summary)])
