"""RF consumes support/context without importing CWP or touching a source root."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from company_wiki_narrative_contracts import (  # noqa: E402
    NarrativeTransportError, _claim, _reading_context, validate_narrative_response,
)
from test_shared_reading_narrative_contract import actual  # noqa: E402
from test_company_wiki_narrative_reader import _resign  # noqa: E402


def spans():
    return {"q": {"source_id": "source-one", "structured_value": {"source_role": "investor_question"}},
            "a": {"source_id": "source-one", "structured_value": {"source_role": "management"}},
            "other": {"source_id": "source-two", "structured_value": {"source_role": "management"}}}


def claim(*, question=False):
    return {"claim_id": "answer", "text": "What was disclosed?" if question else "Management disclosed product progress.",
            "evidence_ids": ["q" if question else "a"],
            "context_evidence_ids": ["a" if question else "q"],
            "claim_type": "analyst_question" if question else "company_statement",
            "modality": "question" if question else "actual", "needs_review": False}


def context():
    value = deepcopy(json.loads(actual()[1])["reading_context"])
    value["schema_version"] = "du-production-reading/2"
    value["groups"] = [{"group_id": "real-native-qa-scope", "kind": "qa_exchange", "section_role": "business",
        "evidence_ids": ["q", "a"], "citation_views": [
            {"support_evidence_ids": ["a"], "context_evidence_ids": ["q"]},
            {"support_evidence_ids": ["q"], "context_evidence_ids": ["a"]}]}]
    return value


@pytest.mark.parametrize("question", [False, True])
def test_source_owned_claim_attribution_is_preserved_without_promotion(question):
    value = claim(question=question)
    assert _claim(value, spans()) == value


def test_both_native_qa_views_are_validated_against_the_transported_span_table():
    _reading_context(context(), spans())


@pytest.mark.parametrize("bad", ["unknown", "duplicate", "overlap", "foreign_parent", "promoted_question"])
def test_context_cannot_authorize_unknown_or_wrongly_attributed_company_facts(bad):
    value = claim()
    if bad == "unknown":
        value["context_evidence_ids"] = ["absent"]
    elif bad == "duplicate":
        value["context_evidence_ids"] *= 2
    elif bad == "overlap":
        value["context_evidence_ids"] = ["a"]
    elif bad == "foreign_parent":
        value["context_evidence_ids"] = ["other"]
    else:
        value["evidence_ids"], value["context_evidence_ids"] = ["q"], ["a"]
    with pytest.raises(NarrativeTransportError):
        _claim(value, spans())


@pytest.mark.parametrize("bad", ["missing", "unknown", "overlap", "empty_support", "duplicate_view", "old_schema"])
def test_invalid_native_views_do_not_cross_the_consumer_contract(bad):
    value = context()
    group = value["groups"][0]
    first = group["citation_views"][0]
    if bad == "missing":
        first["context_evidence_ids"] = []
    elif bad == "unknown":
        first["context_evidence_ids"] = ["other"]
    elif bad == "overlap":
        first["context_evidence_ids"] = ["a", "q"]
    elif bad == "empty_support":
        first["support_evidence_ids"] = []
    elif bad == "duplicate_view":
        group["citation_views"][1] = deepcopy(first)
    else:
        value["schema_version"] = "du-production-reading/1"
    with pytest.raises(NarrativeTransportError):
        _reading_context(value, spans())


def test_complete_public_bundle_keeps_new_context_and_old_native_bytes():
    request, raw, receipt = actual()
    bundle, receipt = json.loads(raw), json.loads(receipt)
    original = deepcopy(bundle)
    bundle["reading_context"]["schema_version"] = "du-production-reading/2"
    for group in bundle["reading_context"]["groups"]:
        group["citation_views"] = [{"support_evidence_ids": list(group["evidence_ids"]),
                                     "context_evidence_ids": []}]
    body, receipt = _resign(request, bundle, receipt)
    value = validate_narrative_response(request, body, receipt).to_dict()
    assert value["reading_context"] == bundle["reading_context"]
    assert value["evidence_spans"] == original["evidence_spans"]
    assert value["summary"] == original["summary"]
