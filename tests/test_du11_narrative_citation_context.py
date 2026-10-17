"""Unit coverage of the shared pure citation-closure adapter.

These pin the named refusals and the diagnostic-only coverage semantics without
touching either consumption entry.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from narrative_citation_context import (  # noqa: E402
    CONTEXT_EVIDENCE_LIMIT,
    NarrativeCitationError,
    TRACE_SCHEMA,
    citation_dependency,
    citation_trace,
    reading_trace,
    resolve_span,
    selection,
    trace_status,
)
from test_du11_narrative_citation_wire import (  # noqa: E402
    descriptor, span_id, validated, wire,
)


def minimal_span(name, *, parent="p", role=None, extra=None):
    structured = {} if role is None else {"source_role": role}
    structured.update(extra or {})
    return {"span_id": name, "source_id": parent, "locator": f"loc:{name}",
            "raw_text": f"text {name}", "structured_value": structured}


def minimal(groups=(), spans=None, schema="du-production-reading/2",
            context_schema="revenue-narrative-context/1"):
    reading = {
        "schema_version": schema, "groups": list(groups),
        "unread": {"opaque_pages": [], "deferred_pages": [], "deferred_unit_ids": [],
                   "unassigned_unit_ids": [], "native_scan": None, "structure_complete": None},
        "deferred": [], "layout_coverage": {},
    }
    return {"schema_version": context_schema,
            "evidence_spans": list(spans or []), "reading_context": reading}


def test_reading_trace_reports_attribution_and_never_claims_completeness():
    two = reading_trace(validated("2").to_dict())
    assert two["attribution"] == "source_owned_views"
    assert two["group_count"] == 2 and two["citation_view_count"] == 4
    assert two["coverage_note"] == "diagnostic_only_not_a_permission_gate"
    one = reading_trace(validated("1").to_dict())
    assert one["attribution"] == "groups_only"
    assert one["citation_view_count"] == 0
    absent = reading_trace(validated(None).to_dict())
    assert absent["present"] is False and absent["attribution"] == "absent"
    assert all(absent["unread"][key] is None for key in
               ("counts", "limited", "opaque_pages", "structure_complete"))
    assert absent["deferred"] == {"count": None, "listed": None, "limited": None}


@pytest.mark.parametrize("layout", [{"complete": "partial"}, {"complete": 1},
                                    {"complete": []}, "not-an-object", {"nested": {}}])
def test_free_form_layout_is_reduced_to_null_never_to_a_refusal(layout):
    context = validated("2").to_dict()
    context["reading_context"]["layout_coverage"] = layout
    assert reading_trace(context)["layout_complete"] is None
    assert resolve_span(context, span_id=span_id(context, "answer"))["closure"] == "citation_view"


@pytest.mark.parametrize("name", list(("opaque_pages", "deferred_pages",
                                       "deferred_unit_ids", "unassigned_unit_ids")))
@pytest.mark.parametrize("broken", ["wrong-type", "missing"])
def test_unreadable_unread_list_degrades_the_counts_to_null(name, broken):
    """A valid `counts` block plus one unreadable list is a null, never a TypeError."""
    context = validated("2").to_dict()
    unread = context["reading_context"]["unread"]
    if broken == "wrong-type":
        unread[name] = "not-a-list"
    else:
        del unread[name]
    trace = reading_trace(context)
    assert trace["unread"]["counts"] is None
    assert trace["unread"]["limited"] is None
    assert trace["unread"][name] is None
    assert trace["unread"]["structure_complete"] is False
    assert resolve_span(context, span_id=span_id(context, "answer"))["closure"] == "citation_view"


def test_unread_material_is_a_diagnostic_not_a_refusal():
    context = validated("2").to_dict()
    trace = reading_trace(context)
    assert trace["unread"]["limited"] is True
    assert trace["unread"]["opaque_pages"] == 1
    assert trace["deferred"]["limited"] is True
    # The same context resolves support normally.
    assert resolve_span(context, span_id=span_id(context, "answer"))["closure"] == "citation_view"


def test_two_legal_views_need_the_view_index_and_never_the_first_element():
    context = validated("2").to_dict()
    row = span_id(context, "table_row")
    with pytest.raises(NarrativeCitationError, match="narrative_citation_view_ambiguous"):
        resolve_span(context, span_id=row)
    table = context["reading_context"]["groups"][1]["group_id"]
    with pytest.raises(NarrativeCitationError, match="narrative_citation_view_ambiguous"):
        resolve_span(context, span_id=row, group_id=table)
    first = resolve_span(context, span_id=row, group_id=table, view=0)
    second = resolve_span(context, span_id=row, group_id=table, view=1)
    assert first["support_evidence_ids"] != second["support_evidence_ids"]
    assert first["context_evidence_ids"] == [
        span_id(context, "table_header"), span_id(context, "footnote"), span_id(context, "unit_note")]
    assert second["context_evidence_ids"] == [
        span_id(context, "table_header"), span_id(context, "unit_note")]


def test_both_legal_directions_of_a_two_view_group_resolve_positively():
    spans = [minimal_span("a", role="company_filing"), minimal_span("b", role="company_filing")]
    group = {"group_id": "g", "kind": "qa_exchange", "section_role": "business",
             "evidence_ids": ["a", "b"],
             "citation_views": [
                 {"support_evidence_ids": ["a"], "context_evidence_ids": ["b"]},
                 {"support_evidence_ids": ["b"], "context_evidence_ids": ["a"]}]}
    context = minimal(groups=[group], spans=spans)
    first = resolve_span(context, span_id="a")
    second = resolve_span(context, span_id="b")
    assert (first["view_index"], first["support_evidence_ids"], first["context_evidence_ids"]) == (0, ["a"], ["b"])
    assert (second["view_index"], second["support_evidence_ids"], second["context_evidence_ids"]) == (1, ["b"], ["a"])


def test_context_only_span_and_question_role_are_refused():
    context = validated("2").to_dict()
    with pytest.raises(NarrativeCitationError, match="narrative_citation_context_only"):
        resolve_span(context, span_id=span_id(context, "table_header"))
    with pytest.raises(NarrativeCitationError, match="narrative_citation_source_role_refused"):
        resolve_span(context, span_id=span_id(context, "question"))
    with pytest.raises(NarrativeCitationError, match="narrative_citation_view_not_support"):
        resolve_span(context, span_id=span_id(context, "table_header"),
                     group_id=context["reading_context"]["groups"][1]["group_id"], view=0)


def test_selection_errors_are_named():
    context = validated("2").to_dict()
    table = context["reading_context"]["groups"][1]["group_id"]
    with pytest.raises(NarrativeCitationError, match="narrative_citation_view_unknown"):
        resolve_span(context, span_id=span_id(context, "table_row"), group_id=table, view=9)
    with pytest.raises(NarrativeCitationError, match="narrative_citation_group_unknown"):
        resolve_span(context, span_id=span_id(context, "table_row"), group_id="urn:none")
    with pytest.raises(NarrativeCitationError, match="narrative_citation_span_unknown"):
        resolve_span(context, span_id="urn:absent")
    with pytest.raises(NarrativeCitationError, match="narrative_citation_binding_fields"):
        selection({"citation_view": True})
    with pytest.raises(NarrativeCitationError, match="narrative_citation_binding_fields"):
        selection({"citation_group_id": ""})
    assert selection({"citation_group_id": "g", "citation_view": 1}) == ("g", 1)


def test_span_in_more_than_one_group_is_ambiguous_until_the_group_is_named():
    data = descriptor()
    data["groups"].append({"group_id": "urn:company-wiki:reading-group:sha256:alt-answer",
                           "kind": "qa_exchange", "section_role": "business",
                           "members": ["answer"],
                           "views": [{"support": ["answer"], "context": []}]})
    request, body, receipt = wire("2", data)
    context = validated("2", data).to_dict()
    answer = span_id(context, "answer")
    with pytest.raises(NarrativeCitationError, match="narrative_citation_group_ambiguous"):
        resolve_span(context, span_id=answer)
    primary = context["reading_context"]["groups"][0]["group_id"]
    resolved = resolve_span(context, span_id=answer, group_id=primary)
    assert resolved["group_id"] == primary and resolved["view_index"] == 0


def test_ungrouped_span_keeps_the_original_consumption_path():
    context = validated("2").to_dict()
    resolution = resolve_span(context, span_id=span_id(context, "section_heading"))
    assert resolution["closure"] == "ungrouped"
    assert resolution["group_id"] is None
    assert resolution["support_evidence_ids"] is None
    assert resolution["context_evidence"] is None
    assert resolution["projected"] is None


def test_cross_parent_group_is_refused_instead_of_stitched():
    spans = [minimal_span("a", parent="parent-a"), minimal_span("b", parent="parent-b")]
    context = minimal(groups=[{"group_id": "g", "kind": "paragraph_event",
                               "section_role": "business", "evidence_ids": ["a", "b"],
                               "citation_views": [{"support_evidence_ids": ["a"],
                                                   "context_evidence_ids": ["b"]}]}], spans=spans)
    with pytest.raises(NarrativeCitationError, match="narrative_citation_reading_invalid"):
        resolve_span(context, span_id="a")


@pytest.mark.parametrize("mutation", [
    "unknown_schema", "groups_not_list", "member_not_transported", "duplicate_view",
    "missing_partition", "overlap", "empty_support", "duplicate_member",
])
def test_malformed_reading_context_is_named(mutation):
    spans = [minimal_span("a"), minimal_span("b")]
    view = {"support_evidence_ids": ["a"], "context_evidence_ids": ["b"]}
    group = {"group_id": "g", "kind": "paragraph_event", "section_role": "business",
             "evidence_ids": ["a", "b"], "citation_views": [view]}
    context = minimal(groups=[group], spans=spans)
    if mutation == "unknown_schema":
        context["reading_context"]["schema_version"] = "du-production-reading/9"
    elif mutation == "groups_not_list":
        context["reading_context"]["groups"] = {"g": group}
    elif mutation == "member_not_transported":
        group["evidence_ids"] = ["a", "absent"]
        view["context_evidence_ids"] = ["absent"]
    elif mutation in {"duplicate_view", "missing_partition", "overlap", "empty_support", "duplicate_member"}:
        if mutation == "duplicate_view":
            group["citation_views"] = [view, dict(view)]
        elif mutation == "missing_partition":
            view["context_evidence_ids"] = []
        elif mutation == "overlap":
            view["context_evidence_ids"] = ["a", "b"]
        elif mutation == "empty_support":
            view["support_evidence_ids"] = []
        else:
            view["support_evidence_ids"] = ["a", "a"]
    with pytest.raises(NarrativeCitationError, match="narrative_citation_reading_invalid"):
        resolve_span(context, span_id="a")


def test_projected_span_must_carry_its_own_parent_pointer():
    span = minimal_span("a", extra={"parent_content_sha256": "a" * 64,
                                    "source_locator": "cwp-json-pointer/1|p=%2Fx|b=1:2|d=0:1|x=json-string-decode/1",
                                    "pointer": "/x"})
    group = {"group_id": "g", "kind": "paragraph_event", "section_role": "business",
             "evidence_ids": ["a"],
             "citation_views": [{"support_evidence_ids": ["a"], "context_evidence_ids": []}]}
    projected = dict(context_schema="revenue-narrative-context/3")
    resolved = resolve_span(minimal(groups=[group], spans=[span], **projected), span_id="a")
    assert resolved["projected"]["parent_sha256"] == "a" * 64
    assert resolved["projected"]["pointer"] == "/x"
    # A `/1` span keeps the same structured value without being treated as projected.
    legacy = resolve_span(minimal(groups=[group], spans=[span]), span_id="a")
    assert legacy["projected"] is None
    broken = minimal_span("a", extra={"parent_content_sha256": "a" * 64, "source_locator": "loc"})
    with pytest.raises(NarrativeCitationError, match="narrative_citation_span_invalid"):
        resolve_span(minimal(spans=[broken], **projected), span_id="a")


def test_trace_status_counts_and_json_shape():
    context = validated("2").to_dict()
    view = resolve_span(context, span_id=span_id(context, "answer"))
    free = resolve_span(context, span_id=span_id(context, "section_heading"))
    closed = citation_trace(context, dependencies=[
        citation_dependency(resolution=view, claim_id="c1", parameter_id="p1")])
    assert closed["schema_version"] == TRACE_SCHEMA
    assert closed["status"] == "closed" and closed["counts"]["view_closed"] == 1
    mixed = citation_trace(context, dependencies=[
        citation_dependency(resolution=view, claim_id="c1", parameter_id="p1"),
        citation_dependency(resolution=free, claim_id="c2", parameter_id="p1")])
    assert mixed["status"] == "partial"
    assert mixed["counts"] == {"dependencies": 2, "view_closed": 1, "group_only": 0,
                               "ungrouped": 1, "context_evidence": 1,
                               "context_evidence_unknown": 1,
                               "context_evidence_limited": 0}
    assert free["context_evidence_limited"] is None
    assert trace_status([]) == "not_consumed"
    json.dumps(mixed, sort_keys=True, allow_nan=False)
    assert CONTEXT_EVIDENCE_LIMIT == 32
