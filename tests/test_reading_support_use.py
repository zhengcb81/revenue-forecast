"""Public /4 wire capability, not a downstream source-content classifier."""
from copy import deepcopy
import json

import pytest

from company_wiki_narrative_contracts import NarrativeTransportError, validate_narrative_response
from contracts.evidence import ForecastInputError
from narrative_citation_context import NarrativeCitationError, citation_trace, resolve_span
from test_du11_narrative_citation_consumption import binding, consume, entry_two
from test_du11_narrative_citation_wire import resign, span_id, validated, wire
from test_shared_reading_narrative_contract import _proof_row, _unit_id, _upgrade_to_v3, projected_context


def reading_four(reading, use="support"):
    previous = deepcopy([group["citation_views"] for group in reading["groups"]])
    _upgrade_to_v3(reading)
    reading["schema_version"] = "du-production-reading/4"
    for group, views in zip(reading["groups"], previous, strict=True):
        group["citation_views"] = views
        for view in views:
            view.update(reading_support_use=use, reading_support_reason="source_observed_use")


def public_context(use="support", mutate=None):
    request, body, receipt = wire("2")
    bundle, receipt = json.loads(body), json.loads(receipt)
    reading_four(bundle["reading_context"], use)
    # This fixture also transports an ungrouped span. A sampled trace count is
    # the whole selected denominator, not just members of its reading groups.
    trace = bundle["reading_context"]["selection_trace"]
    trace["source_unit_count"] = len(bundle["evidence_spans"])
    trace["selected"].update(count=len(bundle["evidence_spans"]),
                             limited=len(bundle["evidence_spans"]) > len(trace["selected"]["samples"]))
    if mutate is not None:
        mutate(bundle["reading_context"])
    return validate_narrative_response(*resign(request, bundle, receipt))


def adapter_value(use="support"):
    value = validated("2").to_dict()
    reading_four(value["reading_context"], use)
    return value


def test_v4_wire_preserves_exact_source_owned_fields_and_legacy_reads():
    value = public_context().to_dict()
    view = value["reading_context"]["groups"][0]["citation_views"][0]
    assert view["reading_support_use"] == "support"
    assert view["reading_support_reason"] == "source_observed_use"
    assert value["reading_context"]["selection_trace"]
    for version in (None, "1", "2"):
        old = validated(version).to_dict()
        if version:
            assert old["reading_context"]["schema_version"] == "du-production-reading/"+version
        else:
            assert "reading_context" not in old


@pytest.mark.parametrize(("field", "value"), [
    ("reading_support_use", "approved"), ("reading_support_use", []),
    ("reading_support_reason", ""), ("reading_support_reason", "a"*81),
    ("reading_support_reason", "Free form reason"), ("reading_support_reason", None),
])
def test_v4_wire_rejects_invalid_capability_fields(field, value):
    with pytest.raises(NarrativeTransportError):
        public_context(mutate=lambda reading: reading["groups"][0]["citation_views"][0].update({field: value}))


@pytest.mark.parametrize("field", ["reading_support_use", "reading_support_reason", "selection_trace"])
def test_v4_wire_requires_its_fields(field):
    def mutate(reading):
        target = reading if field == "selection_trace" else reading["groups"][0]["citation_views"][0]
        del target[field]
    with pytest.raises(NarrativeTransportError):
        public_context(mutate=mutate)


@pytest.mark.parametrize("use", ["context_only", "unresolved"])
@pytest.mark.parametrize("explicit", [False, True])
@pytest.mark.parametrize("key", ["answer", "table_row"])
def test_view_owned_non_support_cannot_be_promoted_by_numeric_member_or_explicit_view(use, explicit, key):
    value = adapter_value(use)
    args = {"view": 0} if explicit else {}
    with pytest.raises(NarrativeCitationError, match="narrative_citation_"+use):
        resolve_span(value, span_id=span_id(value, key), **args)
    # Diagnostic read remains available, without a parameter fact or permission request.
    trace = citation_trace(value)
    assert trace["status"] == "not_consumed" and trace["reading"]["present"]


def test_v4_support_survives_both_real_parameter_entries_and_preserves_context():
    context = public_context()
    _, receipt = consume(context, [binding(context.to_dict(), "answer")])
    second = entry_two(context, "answer")
    for trace in (receipt["citation_trace"], second["citation_trace"]):
        dependency = trace["dependencies"][0]
        assert dependency["reading_support_use"] == "support"
        assert dependency["reading_support_reason"] == "source_observed_use"
        assert dependency["context_evidence_ids"] == [span_id(context.to_dict(), "question")]


@pytest.mark.parametrize("use", ["context_only", "unresolved"])
def test_both_real_entries_share_non_support_refusal_without_mutating_forecast(use):
    context = public_context(use)
    before = context.to_dict()
    with pytest.raises(ValueError, match="narrative_citation_"+use):
        consume(context, [binding(before, "answer", citation_view=0)])
    with pytest.raises(ForecastInputError, match="narrative_citation_"+use):
        entry_two(context, "answer", citation_view=0)
    assert context.to_dict() == before


def test_other_view_capability_cannot_be_used_as_a_vote_for_the_selected_view():
    value = adapter_value()
    views = value["reading_context"]["groups"][1]["citation_views"]
    views[0]["reading_support_use"] = "context_only"
    with pytest.raises(NarrativeCitationError, match="narrative_citation_context_only"):
        resolve_span(value, span_id=span_id(value, "table_row"), view=0)
    result = resolve_span(value, span_id=span_id(value, "table_row"), view=1)
    assert result["reading_support_use"] == "support" and result["view_index"] == 1


def test_v4_ungrouped_member_has_no_implicit_support_capability():
    value = adapter_value()
    value["reading_context"]["groups"] = []
    with pytest.raises(NarrativeCitationError, match="narrative_citation_unresolved"):
        resolve_span(value, span_id=span_id(value, "answer"))


def test_v4_optional_source_proofs_and_legacy_v3_shape_keep_the_same_strict_owner():
    def add_proof(reading):
        left, right = _unit_id(100), _unit_id(101)
        reading["groups"][0].update(source_proof_unit_ids=[left, right],
                                    source_proof_target_unit_ids=[], source_proofs=[_proof_row(left, right)])
    value = public_context(mutate=add_proof).to_dict()
    assert value["reading_context"]["groups"][0]["source_proofs"][0]["right_page"] == 2
    def to_legacy(reading):
        reading["schema_version"] = "du-production-reading/3"
        for group in reading["groups"]:
            for view in group["citation_views"]:
                del view["reading_support_use"], view["reading_support_reason"]
    assert public_context(mutate=to_legacy).to_dict()["reading_context"]["schema_version"].endswith("/3")


def test_existing_projected_public_transport_preserves_v4_without_reclassification():
    request, raw, receipt = projected_context()
    bundle, receipt = json.loads(raw), json.loads(receipt)
    reading = bundle["reading_context"]
    # The existing projected fixture is /1 groups-only; source publishes one
    # complete view, not a downstream guess about separate span relevance.
    for group in reading["groups"]:
        group["citation_views"] = [{"support_evidence_ids": list(group["evidence_ids"]),
                                    "context_evidence_ids": []}]
    reading_four(reading)
    value = validate_narrative_response(*resign(request, bundle, receipt)).to_dict()
    assert value["schema_version"] == "revenue-narrative-context/3"
    assert value["reading_context"] == reading
