"""DU11 citation closure at the two real RF consumption entries.

Every case starts from a legal public narrative wire (synthetic descriptor, no
company original bytes) that passes ``validate_narrative_response``, and then runs
the real ``consume_narrative_input`` or ``bind_parameter_evidence``. The asserts
describe the closure/coverage contract frozen in the card INTERFACES.md.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from company_wiki_narrative_contracts import validate_narrative_response  # noqa: E402
from contracts.evidence import ForecastInputError  # noqa: E402
from fix_hashes import apply_hash_fixes  # noqa: E402
from research.input_evidence import bind_parameter_evidence  # noqa: E402
from revenue_core import canonical_sha256, run_forecast  # noqa: E402
from source_narrative_context import consume_narrative_input  # noqa: E402
from test_du11_narrative_citation_wire import (  # noqa: E402
    descriptor, resign, span, span_id, validated, wire,
)
from test_recognition_bridge import forecast_document  # noqa: E402

TRACE_SCHEMA = "revenue-narrative-citation-trace/1"
PARAMETER = "0_base_2026"
LEGACY_CLAIM_FIELDS = {
    "claim_id", "source_id", "target_type", "target_id", "support_type", "locator",
    "excerpt", "excerpt_sha256", "content_sha256", "capture_receipt_sha256",
    "verification_status", "verified_by", "verified_date",
}


def as_value(context):
    return context.to_dict() if hasattr(context, "to_dict") else context


def parent_ref(context):
    value = as_value(context)
    return value["source_ref"] if value["schema_version"] == "revenue-narrative-context/1" else value["parent_source_refs"][0]


def document(context):
    data = forecast_document()
    parent = parent_ref(context)
    data["as_of_date"] = as_value(context)["as_of_date"]
    data["sources"][0]["capture"]["snapshot_sha256"] = parent["content_sha256"]
    apply_hash_fixes(data)
    return data


def binding(context, key, *, claim_id="du11_cl", parameter_id=PARAMETER, **extra):
    entry = {"span_id": span_id(context, key), "claim_id": claim_id,
             "parameter_id": parameter_id, "support_type": "rationale_support"}
    entry.update(extra)
    return entry


def consume(context, bindings, *, data=None, request=None):
    data = document(context) if data is None else data
    request = request or {"as_of_date": as_value(context)["as_of_date"]}
    with patch("source_narrative_context.read_narrative_context", return_value=context):
        return consume_narrative_input(
            data, request=request, bindings=bindings, source_id="filing",
            catalog_config=Path("isolated-not-opened.json"),
        )


def assert_legacy_claim_shape(claim):
    assert set(claim) == LEGACY_CLAIM_FIELDS


# ---------------------------------------------------------------------------
# A-RED: a legal public bundle is consumed but loses closure and coverage
# ---------------------------------------------------------------------------

def test_public_reading_wire_consume_keeps_view_closure_and_bounded_coverage():
    context = validated("2")
    value = context.to_dict()
    reading = value["reading_context"]
    group = reading["groups"][0]
    view = group["citation_views"][0]
    updated, receipt = consume(context, [binding(value, "answer")])
    trace = receipt["citation_trace"]
    assert trace["schema_version"] == TRACE_SCHEMA
    assert trace["status"] == "closed"
    assert trace["reading"]["present"] is True
    assert trace["reading"]["schema_version"] == "du-production-reading/2"
    assert trace["reading"]["attribution"] == "source_owned_views"
    assert trace["reading"]["group_count"] == 2
    assert trace["reading"]["citation_view_count"] == 4
    assert trace["reading"]["unread"]["counts"] == reading["unread"]["counts"]
    assert trace["reading"]["unread"]["limited"] is True
    assert trace["reading"]["unread"]["structure_complete"] is False
    assert trace["reading"]["unread"]["opaque_pages"] == 1
    assert trace["reading"]["unread"]["deferred_pages"] == 1
    assert trace["reading"]["unread"]["unassigned_unit_ids"] == 1
    assert trace["reading"]["deferred"] == {"count": 3, "listed": 1, "limited": True}
    assert trace["reading"]["selection_diagnostics"] == [{"code": "BOUND", "count": 2}]
    assert trace["reading"]["layout_complete"] is False
    assert trace["reading"]["coverage_note"] == "diagnostic_only_not_a_permission_gate"
    dependency = trace["dependencies"][0]
    assert dependency["closure"] == "citation_view"
    assert dependency["group_id"] == group["group_id"]
    assert dependency["group_kind"] == group["kind"]
    assert dependency["section_role"] == group["section_role"]
    assert dependency["view_index"] == 0
    assert dependency["source_role"] == "management"
    assert dependency["support_evidence_ids"] == view["support_evidence_ids"]
    assert dependency["context_evidence_ids"] == view["context_evidence_ids"]
    assert dependency["context_evidence"] == [{
        "span_id": span_id(value, "question"),
        "locator": span(value, "question")["locator"],
        "source_role": "investor_question",
    }]
    assert dependency["context_evidence_count"] == 1
    assert dependency["context_evidence_limited"] is False
    assert dependency["projected"] is None
    assert trace["counts"] == {"dependencies": 1, "view_closed": 1, "group_only": 0,
                               "ungrouped": 0, "context_evidence": 1,
                               "context_evidence_unknown": 0, "context_evidence_limited": 0}
    # The claim itself keeps its published shape; context is never promoted into it.
    claim = next(item for item in updated["evidence_claims"] if item["claim_id"] == "du11_cl")
    assert_legacy_claim_shape(claim)
    assert claim["excerpt"] == span(value, "answer")["raw_text"]
    assert claim["locator"] == span(value, "answer")["locator"]
    # The trace joins the existing formula dependency instead of creating a second one.
    formula = next(item for item in receipt["dependencies"] if item["claim_id"] == "du11_cl")
    assert formula["formula_refs"]
    assert formula["parameter_id"] == PARAMETER


def test_prediction_values_are_identical_before_and_after_the_trace():
    context = validated("2")
    data = document(context)
    before = run_forecast(deepcopy(data), mode="draft")
    updated, receipt = consume(context, [binding(context.to_dict(), "answer")], data=data)
    after = run_forecast(updated, mode="draft")
    assert receipt["status"] == "consumed"
    assert canonical_sha256(before["consolidated_forecast"]) == canonical_sha256(after["consolidated_forecast"])
    assert canonical_sha256(before["segments"]) == canonical_sha256(after["segments"])
    assert any(item["claim_id"] == "du11_cl" for item in after["input_document"]["evidence_claims"])


# ---------------------------------------------------------------------------
# A-RED: context is not an independent support fact
# ---------------------------------------------------------------------------

def test_context_only_table_header_cannot_become_support():
    context = validated("2")
    with pytest.raises(ValueError, match="narrative_citation_context_only"):
        consume(context, [binding(context.to_dict(), "table_header")])


def test_question_span_cannot_become_a_management_fact():
    context = validated("2")
    with pytest.raises(ValueError, match="narrative_citation_source_role_refused"):
        consume(context, [binding(context.to_dict(), "question")])


# ---------------------------------------------------------------------------
# A-RED: several legal views are never "first one wins"
# ---------------------------------------------------------------------------

def test_two_legal_views_require_an_explicit_selection():
    context = validated("2")
    value = context.to_dict()
    with pytest.raises(ValueError, match="narrative_citation_view_ambiguous"):
        consume(context, [binding(value, "table_row")])
    _, first = consume(context, [binding(value, "table_row", citation_view=0)])
    dependency = first["citation_trace"]["dependencies"][0]
    assert dependency["view_index"] == 0
    assert dependency["support_evidence_ids"] == [span_id(value, "table_row")]
    assert dependency["context_evidence_ids"] == [
        span_id(value, "table_header"), span_id(value, "footnote"), span_id(value, "unit_note")]
    assert [item["span_id"] for item in dependency["context_evidence"]] == [
        span_id(value, "table_header"), span_id(value, "footnote"), span_id(value, "unit_note")]
    assert [item["source_role"] for item in dependency["context_evidence"]] == [
        "company_filing", "company_filing", "company_filing"]
    assert dependency["context_evidence_count"] == 3
    _, second = consume(context, [binding(value, "table_row", citation_view=1)])
    other = second["citation_trace"]["dependencies"][0]
    assert other["view_index"] == 1
    assert other["support_evidence_ids"] == [span_id(value, "table_row"), span_id(value, "footnote")]
    assert other["context_evidence_ids"] == [span_id(value, "table_header"), span_id(value, "unit_note")]


def test_bad_explicit_selection_is_named_instead_of_guessed():
    context = validated("2")
    value = context.to_dict()
    with pytest.raises(ValueError, match="narrative_citation_view_unknown"):
        consume(context, [binding(value, "table_row", citation_view=9)])
    with pytest.raises(ValueError, match="narrative_citation_view_not_support"):
        consume(context, [binding(value, "table_header", citation_view=0)])
    with pytest.raises(ValueError, match="narrative_citation_binding_fields"):
        consume(context, [binding(value, "table_row", citation_views=0)])
    with pytest.raises(ValueError, match="narrative_citation_binding_fields"):
        consume(context, [binding(value, "table_row", citation_view=True)])


def test_context_evidence_projection_is_bounded_and_counted():
    """Only appended spans are added, so the descriptor key indices stay valid."""
    data = descriptor()
    for index in range(40):
        data["lines"].append(f"Note {index:02d}: regional revenue footnote detail.")
        data["spans"].append({"key": f"note_{index}", "line": len(data["lines"]),
                              "paragraph": len(data["lines"]), "role": "company_filing",
                              "unit_kind": "footnote", "section": "regional_table"})
        data["groups"][1]["members"].append(f"note_{index}")
        for view in data["groups"][1]["views"]:
            view["context"].append(f"note_{index}")
    request, body, receipt = wire("2", data)
    context = validate_narrative_response(request, body, receipt)
    _, consumed = consume(context, [binding(context.to_dict(), "table_row", citation_view=0)])
    dependency = consumed["citation_trace"]["dependencies"][0]
    assert dependency["context_evidence_count"] == 43
    assert len(dependency["context_evidence"]) == 32
    assert dependency["context_evidence_limited"] is True
    assert consumed["citation_trace"]["counts"]["context_evidence_limited"] == 1


# ---------------------------------------------------------------------------
# A-RED: reading shapes that must stay explicit instead of invented
# ---------------------------------------------------------------------------

def test_reading_one_group_closure_has_no_view_claim():
    context = validated("1")
    value = context.to_dict()
    _, receipt = consume(context, [binding(value, "answer")])
    trace = receipt["citation_trace"]
    assert trace["reading"]["attribution"] == "groups_only"
    assert trace["status"] == "group_only"
    dependency = trace["dependencies"][0]
    assert dependency["closure"] == "reading_group"
    assert dependency["group_id"] == value["reading_context"]["groups"][0]["group_id"]
    assert dependency["view_index"] is None
    assert dependency["support_evidence_ids"] is None
    assert dependency["context_evidence_ids"] is None
    assert dependency["context_evidence"] is None


def test_absent_reading_context_never_claims_complete_coverage():
    context = validated(None)
    value = context.to_dict()
    _, receipt = consume(context, [binding(value, "answer")])
    trace = receipt["citation_trace"]
    assert trace["reading"]["present"] is False
    assert trace["reading"]["schema_version"] is None
    assert trace["reading"]["attribution"] == "absent"
    assert trace["reading"]["group_count"] == 0
    assert trace["reading"]["unread"]["counts"] is None
    assert trace["reading"]["unread"]["limited"] is None
    assert trace["reading"]["unread"]["structure_complete"] is None
    assert trace["reading"]["unread"]["opaque_pages"] is None
    assert trace["reading"]["deferred"] == {"count": None, "listed": None, "limited": None}
    assert trace["reading"]["selection_diagnostics"] is None
    assert trace["reading"]["layout_complete"] is None
    assert trace["status"] == "ungrouped"
    assert trace["dependencies"][0]["closure"] == "ungrouped"
    assert receipt["status"] == "consumed"


def test_unknown_sampling_counts_stay_null_instead_of_zero():
    request, body, receipt = wire("2")
    bundle = json.loads(body)
    reading = bundle["reading_context"]
    for key in ("counts", "limited"):
        del reading["unread"][key]
    for key in ("deferred_count", "deferred_limited", "selection_diagnostics"):
        del reading[key]
    request, body, receipt = resign(request, bundle, json.loads(receipt))
    context = validate_narrative_response(request, body, receipt)
    value = context.to_dict()
    _, consumed = consume(context, [binding(value, "answer")])
    trace = consumed["citation_trace"]
    assert trace["reading"]["unread"]["counts"] is None
    assert trace["reading"]["unread"]["limited"] is None
    assert trace["reading"]["unread"]["opaque_pages"] == 1
    assert trace["reading"]["unread"]["unassigned_unit_ids"] == 1
    assert trace["reading"]["deferred"] == {"count": None, "listed": 1, "limited": None}
    assert trace["reading"]["selection_diagnostics"] is None
    assert consumed["status"] == "consumed"


def test_ungrouped_legal_span_is_still_consumed_without_a_group():
    context = validated("2")
    value = context.to_dict()
    updated, receipt = consume(context, [binding(value, "section_heading")])
    dependency = receipt["citation_trace"]["dependencies"][0]
    assert dependency["closure"] == "ungrouped"
    assert dependency["group_id"] is None
    assert receipt["citation_trace"]["status"] == "ungrouped"
    assert receipt["status"] == "consumed"
    claim = next(item for item in updated["evidence_claims"] if item["claim_id"] == "du11_cl")
    assert claim["excerpt"] == span(value, "section_heading")["raw_text"]


def test_two_groups_under_one_parent_keep_their_own_closure():
    context = validated("2")
    value = context.to_dict()
    updated, receipt = consume(context, [
        binding(value, "answer", claim_id="du11_qa"),
        binding(value, "table_row", claim_id="du11_table", citation_view=0),
    ])
    trace = receipt["citation_trace"]
    assert trace["status"] == "closed"
    assert trace["counts"]["dependencies"] == 2
    groups = {item["claim_id"]: item["group_id"] for item in trace["dependencies"]}
    assert groups["du11_qa"] == value["reading_context"]["groups"][0]["group_id"]
    assert groups["du11_table"] == value["reading_context"]["groups"][1]["group_id"]
    parameter = next(item for item in updated["parameters"] if item["parameter_id"] == PARAMETER)
    assert parameter["claim_ids"][-2:] == ["du11_qa", "du11_table"]
    dependencies = {item["claim_id"]: item for item in receipt["dependencies"]}
    assert dependencies["du11_qa"]["source_sha256"] == parent_ref(value)["content_sha256"]
    assert dependencies["du11_table"]["source_sha256"] == parent_ref(value)["content_sha256"]


def test_empty_bindings_stay_not_consumed_with_diagnostics():
    context = validated("2")
    updated, receipt = consume(context, [])
    assert receipt["status"] == "not_consumed"
    assert receipt["dependencies"] == []
    assert receipt["citation_trace"]["status"] == "not_consumed"
    assert receipt["citation_trace"]["dependencies"] == []
    assert receipt["citation_trace"]["reading"]["present"] is True
    assert receipt["citation_trace"]["reading"]["unread"]["limited"] is True
    assert "citation_trace" not in updated


def test_reader_receipt_for_metadata_only_read_carries_the_same_trace():
    from source_narrative_context import narrative_read_receipt

    context = validated("2")
    receipt = narrative_read_receipt(context)
    assert receipt["schema_version"] == "revenue-narrative-consumption/1"
    assert receipt["status"] == "not_consumed"
    assert receipt["citation_trace"]["schema_version"] == TRACE_SCHEMA
    assert receipt["citation_trace"]["status"] == "not_consumed"
    assert receipt["citation_trace"]["reading"]["attribution"] == "source_owned_views"


@pytest.mark.parametrize("layout", [{"complete": "partial"}, {"complete": 1}, {"complete": None}, {}])
def test_free_form_layout_diagnostic_never_gates_consumption(layout):
    """`layout_coverage` is a free-form wire dict; an unreadable value is a null."""
    request, body, receipt = wire("2")
    bundle = json.loads(body)
    bundle["reading_context"]["layout_coverage"] = layout
    request, body, receipt = resign(request, bundle, json.loads(receipt))
    context = validate_narrative_response(request, body, receipt)
    value = context.to_dict()
    updated, consumed = consume(context, [binding(value, "answer")])
    assert consumed["status"] == "consumed"
    assert consumed["citation_trace"]["reading"]["layout_complete"] is None
    assert consumed["citation_trace"]["status"] == "closed"


def test_groups_only_span_in_two_groups_is_recorded_deterministically():
    data = descriptor()
    data["groups"].append({"group_id": "urn:company-wiki:reading-group:sha256:alt-answer",
                           "kind": "paragraph_event", "section_role": "business",
                           "members": ["answer"]})
    request, body, receipt = wire("1", data)
    context = validate_narrative_response(request, body, receipt)
    value = context.to_dict()
    first_id = value["reading_context"]["groups"][0]["group_id"]
    alt_id = value["reading_context"]["groups"][-1]["group_id"]
    _, plain = consume(context, [binding(value, "answer")])
    dependency = plain["citation_trace"]["dependencies"][0]
    assert dependency["closure"] == "reading_group" and dependency["group_id"] == first_id
    _, named = consume(context, [binding(value, "answer", citation_group_id=alt_id)])
    assert named["citation_trace"]["dependencies"][0]["group_id"] == alt_id


# ---------------------------------------------------------------------------
# A-RED: the second real entry shares the same closure semantics
# ---------------------------------------------------------------------------

def parameter():
    return {"parameter_id": PARAMETER, "kind": "analyst_assumption", "value": 110,
            "unit": "USD million", "period": "FY2026", "dimension": "revenue",
            "scenario": "base", "definition": "segment A base revenue",
            "rationale": "driver", "source_ids": [], "claim_ids": []}


def entry_two(context, key, **extra):
    entry = {"role": "mechanism_direction", "source_id": "narrative_transcript",
             "narrative_context": context.to_dict(), "span_id": span_id(context.to_dict(), key),
             "inference_distance": "direct"}
    entry.update(extra)
    return bind_parameter_evidence(
        parameter(), evidence_bindings=[entry], source=None,
        verified_by="du11-test", verified_date=context.to_dict()["as_of_date"],
    )


def test_entry_two_binding_keeps_the_same_closure():
    context = validated("2")
    value = context.to_dict()
    result = entry_two(context, "answer")
    trace = result["citation_trace"]
    assert trace["schema_version"] == TRACE_SCHEMA
    assert trace["status"] == "closed"
    dependency = trace["dependencies"][0]
    assert dependency["claim_id"] == result["claims"][0]["claim_id"]
    assert dependency["parameter_id"] == PARAMETER
    assert dependency["closure"] == "citation_view"
    assert dependency["view_index"] == 0
    assert dependency["context_evidence_ids"] == [span_id(value, "question")]
    assert dependency["source_role"] == "management"
    assert set(result["claims"][0]) == LEGACY_CLAIM_FIELDS | {"evidence_role"}
    assert result["claims"][0]["excerpt"] == span(value, "answer")["raw_text"]
    assert result["claims"][0]["locator"] == span(value, "answer")["locator"]


def test_entry_two_refuses_context_and_question_support_with_the_same_codes():
    context = validated("2")
    with pytest.raises(ForecastInputError, match="narrative_citation_context_only"):
        entry_two(context, "table_header")
    with pytest.raises(ForecastInputError, match="narrative_citation_source_role_refused"):
        entry_two(context, "question")
    with pytest.raises(ForecastInputError, match="narrative_citation_view_ambiguous"):
        entry_two(context, "table_row")
    result = entry_two(context, "table_row", citation_view=1)
    assert result["citation_trace"]["dependencies"][0]["view_index"] == 1


def test_entry_two_unvalidated_context_cannot_smuggle_a_promotion():
    context = validated("2")
    promoted = deepcopy(context.to_dict())
    group = promoted["reading_context"]["groups"][1]
    group["citation_views"] = [{"support_evidence_ids": group["evidence_ids"],
                                "context_evidence_ids": group["evidence_ids"]}]
    with pytest.raises(ForecastInputError, match="narrative_citation_reading_invalid"):
        entry_two(context, "table_header", narrative_context=promoted)
    missing = deepcopy(context.to_dict())
    missing["reading_context"]["groups"][0]["evidence_ids"].append(
        "urn:company-wiki:evidence-span:sha256:absent")
    with pytest.raises(ForecastInputError, match="narrative_citation_reading_invalid"):
        entry_two(context, "answer", narrative_context=missing)
    duplicate = deepcopy(context.to_dict())
    first = duplicate["reading_context"]["groups"][0]["citation_views"][0]
    first["support_evidence_ids"].append(first["support_evidence_ids"][0])
    with pytest.raises(ForecastInputError, match="narrative_citation_reading_invalid"):
        entry_two(context, "answer", narrative_context=duplicate)


@pytest.mark.parametrize(("missing", "message"), [
    ("manifest", "narrative_context is missing its read receipt or manifest"),
    ("source_ref", "narrative_context is missing its source or narrative reference"),
    ("narrative_ref", "narrative_context is missing its source or narrative reference"),
])
def test_entry_two_legacy_refusals_keep_their_published_text(missing, message):
    context = validated("2")
    broken = deepcopy(context.to_dict())
    del broken[missing]
    with pytest.raises(ForecastInputError, match=message):
        entry_two(context, "answer", narrative_context=broken)


def test_entry_two_projected_wire_resolves_parent_and_names_the_publication_gap():
    from test_shared_reading_narrative_contract import projected_context

    request, body, receipt = projected_context()
    context = validate_narrative_response(request, body, receipt)
    value = context.to_dict()
    assert value["schema_version"] == "revenue-narrative-context/3"
    entry = {"role": "mechanism_direction", "source_id": "narrative_transcript",
             "narrative_context": value, "span_id": value["evidence_spans"][0]["span_id"]}
    with pytest.raises(ForecastInputError, match="source_availability_unknown"):
        bind_parameter_evidence(parameter(), evidence_bindings=[entry], source=None,
                                verified_by="du11-test", verified_date=value["as_of_date"])
