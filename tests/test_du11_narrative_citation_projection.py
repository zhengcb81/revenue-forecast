"""Projected `/3` citations: real parent, original locator/pointer, no stitching."""
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
from fix_hashes import apply_hash_fixes  # noqa: E402
from source_narrative_context import consume_narrative_input  # noqa: E402
from test_du11_narrative_citation_wire import resign  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402
from test_shared_reading_narrative_contract import projected_context  # noqa: E402

PARAMETER = "0_base_2026"


def view_wire(*, two_parents=False):
    """A projected wire whose reading context carries a source-owned view."""
    request, body, receipt = projected_context(two_parents=two_parents)
    bundle, receipt_value = json.loads(body), json.loads(receipt)
    reading = bundle["reading_context"]
    reading["schema_version"] = "du-production-reading/2"
    if two_parents:
        parents = bundle["subject_binding"]["parent_source_refs"]
        by_parent = {span["source_id"]: span["span_id"] for span in bundle["evidence_spans"]}
        reading["groups"] = [
            {"group_id": f"urn:company-wiki:reading-group:sha256:parent-{index}",
             "kind": "paragraph_event", "section_role": "business",
             "evidence_ids": [by_parent[parent["source_id"]]],
             "citation_views": [{"support_evidence_ids": [by_parent[parent["source_id"]]],
                                 "context_evidence_ids": []}]}
            for index, parent in enumerate(parents)
        ]
    else:
        for group in reading["groups"]:
            group["citation_views"] = [{"support_evidence_ids": list(group["evidence_ids"]),
                                        "context_evidence_ids": []}]
    return resign(request, bundle, receipt_value)


def load(*, two_parents=False):
    request, body, receipt = view_wire(two_parents=two_parents)
    return validate_narrative_response(request, body, receipt)


def parent_of(value, span):
    return next(item for item in value["parent_source_refs"]
                if item["source_id"] == span["source_id"])


def document(context, parent):
    data = forecast_document()
    data["as_of_date"] = context["as_of_date"]
    data["sources"][0]["capture"]["snapshot_sha256"] = parent["content_sha256"]
    apply_hash_fixes(data)
    return data


def binding(value, span, **extra):
    entry = {"span_id": span["span_id"], "claim_id": "du11_projected",
             "parameter_id": PARAMETER, "support_type": "rationale_support"}
    entry.update(extra)
    return entry


def consume(context, data, entries):
    request = {"as_of_date": context.to_dict()["as_of_date"]}
    with patch("source_narrative_context.read_narrative_context", return_value=context):
        return consume_narrative_input(data, request=request, bindings=entries,
                                       source_id="filing", catalog_config=Path("isolated.json"))


def test_projected_span_binds_its_own_parent_locator_and_pointer():
    context = load()
    value = context.to_dict()
    span = value["evidence_spans"][0]
    parent = parent_of(value, span)
    updated, receipt = consume(context, document(value, parent), [binding(value, span)])
    dependency = receipt["citation_trace"]["dependencies"][0]
    assert dependency["closure"] == "citation_view"
    assert dependency["projected"] == {
        "parent_source_id": parent["source_id"],
        "parent_sha256": parent["content_sha256"],
        "source_locator": span["structured_value"]["source_locator"],
        "pointer": span["structured_value"]["pointer"],
    }
    assert receipt["schema_version"] == "revenue-narrative-consumption/3"
    assert receipt["dependencies"][0]["source_sha256"] == parent["content_sha256"]
    assert receipt["dependencies"][0]["source_locator"] == span["structured_value"]["source_locator"]
    claim = next(item for item in updated["evidence_claims"] if item["claim_id"] == "du11_projected")
    assert claim["locator"] == span["structured_value"]["source_locator"]


def test_projected_foreign_parent_is_refused_even_with_a_legal_wire():
    context = load()
    value = context.to_dict()
    span = value["evidence_spans"][0]
    other = next(item for item in value["parent_source_refs"] if item is not parent_of(value, span))
    with pytest.raises(ValueError, match="differs from the captured parent source"):
        consume(context, document(value, other), [binding(value, span)])


def test_two_projected_parents_are_never_stitched_into_one_claim():
    context = load(two_parents=True)
    value = context.to_dict()
    assert len(value["parent_source_refs"]) == 2
    spans = {span["source_id"]: span for span in value["evidence_spans"]}
    captured = value["parent_source_refs"][0]
    other = value["parent_source_refs"][1]
    owned = spans[captured["source_id"]]
    data = document(value, captured)
    updated, receipt = consume(context, data, [binding(value, owned)])
    dependency = receipt["citation_trace"]["dependencies"][0]
    assert dependency["projected"]["parent_sha256"] == captured["content_sha256"]
    assert len(receipt["citation_trace"]["dependencies"]) == 1
    with pytest.raises(ValueError, match="differs from the captured parent source"):
        consume(context, deepcopy(data), [binding(value, spans[other["source_id"]])])


def test_projection_without_reading_views_keeps_group_closure_only():
    request, body, receipt = projected_context()
    context = validate_narrative_response(request, body, receipt)
    value = context.to_dict()
    span = value["evidence_spans"][0]
    parent = parent_of(value, span)
    _, consumed = consume(context, document(value, parent), [binding(value, span)])
    trace = consumed["citation_trace"]
    assert trace["reading"]["attribution"] == "groups_only"
    assert trace["status"] == "group_only"
    dependency = trace["dependencies"][0]
    assert dependency["closure"] == "reading_group"
    assert dependency["support_evidence_ids"] is None
    assert dependency["projected"]["pointer"] == "/records/0/answer"
