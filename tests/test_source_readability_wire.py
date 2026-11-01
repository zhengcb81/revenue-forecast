"""RF accepts the source-owned /4 processing completeness wire, not new facts."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from company_wiki_narrative_contracts import (
    NarrativeTransportError,
    _selection_diagnostic,
)
from test_reading_support_use import public_context
from test_shared_reading_narrative_contract import changed, _upgrade_to_v3
from company_wiki_narrative_contracts import validate_narrative_response


def diagnostic(code="source_grammar_unavailable"):
    return {
        "code": code,
        "count": 1,
        "phase": "source_readability",
        "dimension": "source_readability",
        "external_model_cost": False,
        "known_unit_ids": [],
        "known_unit_count": 1,
        "known_unit_ids_limited": True,
    }


@pytest.mark.parametrize("complete", [False, True])
def test_schema_four_preserves_explicit_processing_completeness(complete):
    value = public_context(
        mutate=lambda reading: reading.update(source_processing_complete=complete)
    ).to_dict()
    assert value["reading_context"]["source_processing_complete"] is complete


def test_legacy_four_absence_is_not_promoted_to_true():
    assert (
        "source_processing_complete"
        not in public_context().to_dict()["reading_context"]
    )


@pytest.mark.parametrize("value", [None, 0, 1, "true", [], {}])
def test_processing_completeness_is_a_strict_boolean(value):
    with pytest.raises(NarrativeTransportError, match="invalid_reading_context"):
        public_context(
            mutate=lambda reading: reading.update(source_processing_complete=value)
        )


def test_processing_completeness_is_not_an_older_schema_extension():
    def mutate(reading):
        _upgrade_to_v3(reading)
        reading["source_processing_complete"] = True

    with pytest.raises(NarrativeTransportError, match="invalid_reading_context"):
        validate_narrative_response(*changed(mutate))


@pytest.mark.parametrize(
    "code",
    [
        "source_grammar_unavailable",
        "source_grammar_scope_limit",
        "source_assessment_incomplete",
    ],
)
def test_bounded_source_readability_diagnostic_is_transported_exactly(code):
    row = diagnostic(code)

    def mutate(reading):
        reading.update(source_processing_complete=False, selection_diagnostics=[row])

    value = public_context(mutate=mutate).to_dict()["reading_context"]
    assert value["selection_diagnostics"] == [row]
    assert value["source_processing_complete"] is False


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown_code",
        "extra",
        "phase",
        "dimension",
        "cost",
        "bool_count",
        "zero_count",
        "bad_ids",
        "too_many_ids",
        "bad_total",
        "bool_total",
        "bad_limited",
        "nonbool_limited",
    ],
)
def test_source_readability_diagnostic_rejects_wrong_shape_and_unbounded_data(mutation):
    row = deepcopy(diagnostic())
    if mutation == "unknown_code":
        row["code"] = "unpublished_source_rule"
    elif mutation == "extra":
        row["unexpected"] = True
    elif mutation == "phase":
        row["phase"] = "source_parse"
    elif mutation == "dimension":
        row["dimension"] = "source_parse"
    elif mutation == "cost":
        row["external_model_cost"] = True
    elif mutation == "bool_count":
        row["count"] = True
    elif mutation == "zero_count":
        row["count"] = 0
    elif mutation == "bad_ids":
        row["known_unit_ids"] = ["not-a-unit"]
    elif mutation == "too_many_ids":
        row.update(
            known_unit_ids=[
                "urn:company-wiki:narrative-unit:sha256:" + f"{i:064x}"
                for i in range(17)
            ],
            known_unit_count=17,
            known_unit_ids_limited=False,
        )
    elif mutation == "bad_total":
        row["known_unit_count"] = 0
    elif mutation == "bool_total":
        row["known_unit_count"] = True
    elif mutation == "bad_limited":
        row["known_unit_ids_limited"] = False
    else:
        row["known_unit_ids_limited"] = 1
    with pytest.raises(
        NarrativeTransportError,
        match="invalid_reading_diagnostic|invalid_selection_trace_ids|reading_array_limit",
    ):
        _selection_diagnostic(row, legacy_aggregate=False)


@pytest.mark.parametrize(
    ("case", "complete"), [("complete", True), ("deferred", False)]
)
def test_actual_cwp_handler_golden_passes_rf_reading_subcontract(case, complete):
    from company_wiki_narrative_contracts import _reading_context

    golden = json.loads(
        (
            Path(__file__).parent
            / "fixtures/source_readability_wire/cwp-handler-r5.json"
        ).read_text(encoding="utf-8")
    )
    assert golden["reading_context_contract_feature"] == "reading-context-wire/1.1"
    result = golden["cases"][case]
    spans = {span["span_id"]: span for span in result["evidence_spans"]}
    before = deepcopy(result["reading_context"])
    _reading_context(result["reading_context"], spans)
    assert result["reading_context"] == before
    assert result["reading_context"]["source_processing_complete"] is complete


@pytest.mark.parametrize("code", [[], {}, None, True])
def test_malformed_diagnostic_code_is_a_contract_error(code):
    row = diagnostic()
    row["code"] = code
    with pytest.raises(NarrativeTransportError):
        _selection_diagnostic(row, legacy_aggregate=False)
