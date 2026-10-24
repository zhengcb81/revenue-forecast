"""Independent RF validation of saved public shared-reading wire; no CWP imports."""

from copy import deepcopy
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from company_wiki_narrative_contracts import (  # noqa: E402
    NarrativeTransportError,
    _diagnostic_target,
    canonical_bytes,
    validate_narrative_response,
)
from company_wiki_narrative_reader import read_narrative_context  # noqa: E402
from test_company_wiki_narrative_reader import _resign  # noqa: E402
from test_narrative_source_preparation_transport import _fake  # noqa: E402
from test_w04_public_consumer import projected_wire  # noqa: E402

FIXTURES = ROOT / "docs/plans/shared-reading-consumer-2026-10-14/fixtures"


def actual(version="090"):
    request = json.loads((FIXTURES / f"actual-{version}-request.json").read_bytes())
    with gzip.open(FIXTURES / f"actual-{version}-bundle.json.gz", "rb") as stream:
        body = stream.read()
    receipt = (FIXTURES / f"actual-{version}-receipt.jsonl").read_bytes()
    assert (
        hashlib.sha256(body).hexdigest() == request["narrative_ref"]["artifact_sha256"]
    )
    return request, body, receipt


def changed(mutate):
    request, raw, receipt = actual()
    bundle, receipt = json.loads(raw), json.loads(receipt)
    mutate(bundle["reading_context"])
    body, receipt = _resign(request, bundle, receipt)
    return request, body, receipt


def test_saved_actual_090_public_bytes_are_consumed_with_full_reading_context():
    request, body, receipt = actual()
    original = json.loads(body)
    context = validate_narrative_response(request, body, receipt)
    value = context.to_dict()
    assert value["schema_version"] == "revenue-narrative-context/1"
    assert value["reading_context"] == original["reading_context"]
    assert value["evidence_spans"] == original["evidence_spans"]
    assert value["summary"] == original["summary"]
    # Semantic/fine-layout completeness does not replace native text coverage.
    assert value["selection"]["coverage_complete"]
    assert value["reading_context"]["layout_coverage"]["complete"] is False
    value["reading_context"]["groups"][0]["evidence_ids"].clear()
    assert context.to_dict()["reading_context"] == original["reading_context"]



def _unit_id(index):
    return "urn:company-wiki:narrative-unit:sha256:" + hashlib.sha256(
        f"unit-{index}".encode()
    ).hexdigest()


@pytest.mark.parametrize(("code", "limit", "closure_size"), [
    ("budget_full", 112, 1),
    ("character_budget", 105, 1),
    ("group_exceeds_limit", 112, 113),
])
def test_v3_diagnostic_target_rejects_used_above_limit(code, limit, closure_size):
    target = {
        "item_id": _unit_id(250), "item_ids": [], "item_count": 1,
        "item_ids_limited": True, "group_id": None, "locator": "loc:v1/page:1",
        "used": limit + 1, "requested": 1, "limit": limit,
        "closure_size": closure_size,
    }
    with pytest.raises(NarrativeTransportError, match="invalid_reading_diagnostic_target"):
        _diagnostic_target(target, code)


def _upgrade_to_v3(reading):
    reading["schema_version"] = "du-production-reading/3"
    refs = list(dict.fromkeys(span_id for group in reading["groups"] for span_id in group["evidence_ids"]))
    for group in reading["groups"]:
        group["citation_views"] = [{
            "support_evidence_ids": list(group["evidence_ids"]), "context_evidence_ids": [],
        }]
    selected = [{"unit_id": _unit_id(index), "span_id": span_id}
                for index, span_id in enumerate(refs)]
    reading["selection_trace"] = {
        "schema_version": "selection-trace/1", "source_unit_count": len(selected),
        "admission": {"count": 0, "admitted_count": 0, "rejected_count": 0,
                      "limited": False, "rejection_counts": {}, "samples": []},
        "eligible_packages": {"count": 0, "limited": False, "samples": []},
        "withheld": {"count": 0, "limited": False, "samples": []},
        "selected": {"count": len(selected), "limited": False, "samples": selected},
    }
    reading["selection_diagnostics"] = [{
        "code": "budget_full", "count": 1, "phase": "selection",
        "external_model_cost": False, "dimension": "selection_spans",
        "used": 112, "limit": 112, "targets": [], "targets_limited": True,
    }]


def _proof_row(left, right):
    return {
        "basis": "observed_adjacent_page_flow", "left": left, "right": right,
        "left_page": 1, "right_page": 2, "left_ordinal": 0, "right_ordinal": 1,
        "column": "A", "coordinate_frame": "page", "furniture_unit_ids": [],
    }


def test_du_production_reading_v3_accepts_bounded_trace_diagnostics_and_proofs():
    def upgrade(reading):
        _upgrade_to_v3(reading)
        left, right = _unit_id(100), _unit_id(101)
        reading["groups"][0].update({
            "source_proof_unit_ids": [left, right],
            "source_proof_target_unit_ids": [],
            "source_proofs": [_proof_row(left, right)],
        })
    value = validate_narrative_response(*changed(upgrade)).to_dict()
    assert value["reading_context"]["schema_version"] == "du-production-reading/3"
    assert value["reading_context"]["groups"][0]["source_proofs"][0]["basis"] == "observed_adjacent_page_flow"
    assert value["reading_context"]["selection_trace"]["selected"]["count"] == len(value["evidence_spans"])

    def known_bare_diagnostic(reading):
        _upgrade_to_v3(reading)
        reading["selection_diagnostics"] = [{
            "code": "DECISION_DEPENDENCIES_UNAVAILABLE", "count": 1,
        }]
    assert validate_narrative_response(*changed(known_bare_diagnostic)).to_dict()["reading_context"]


@pytest.mark.parametrize("mutation", [
    "missing_trace", "extra_trace", "unbound_span", "trace_path", "unknown_diagnostic",
    "unknown_bare_diagnostic", "invalid_schema_type",
    "boolean_count", "bad_proof_page", "unbound_proof", "partial_proof_fields",
])
def test_du_production_reading_v3_rejects_bad_trace_diagnostics_and_proofs(mutation):
    def upgrade(reading):
        _upgrade_to_v3(reading)
        left, right = _unit_id(100), _unit_id(101)
        group = reading["groups"][0]
        group.update({"source_proof_unit_ids": [left, right],
                      "source_proof_target_unit_ids": [], "source_proofs": [_proof_row(left, right)]})
        if mutation == "missing_trace":
            del reading["selection_trace"]
        elif mutation == "extra_trace":
            reading["selection_trace"]["unexpected"] = True
        elif mutation == "unbound_span":
            reading["selection_trace"]["selected"]["samples"][0]["span_id"] = "urn:absent"
        elif mutation == "trace_path":
            reading["selection_trace"]["withheld"]["samples"] = [{"raw_text": "forbidden"}]
            reading["selection_trace"]["withheld"].update(count=1, limited=False)
        elif mutation == "unknown_diagnostic":
            reading["selection_diagnostics"][0]["code"] = "unknown_code"
        elif mutation == "unknown_bare_diagnostic":
            reading["selection_diagnostics"] = [{"code": "unknown_code", "count": 1}]
        elif mutation == "invalid_schema_type":
            reading["schema_version"] = []
        elif mutation == "boolean_count":
            reading["selection_diagnostics"][0]["count"] = True
        elif mutation == "bad_proof_page":
            group["source_proofs"][0]["right_page"] = True
        elif mutation == "unbound_proof":
            group["source_proofs"][0]["right"] = _unit_id(102)
        else:
            del group["source_proof_target_unit_ids"]
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(*changed(upgrade))


def _fit_reading_size(reading, target):
    reading["layout_coverage"]["padding"] = []
    for full_count in range(20):
        padding = ["x" * 16384 for _ in range(full_count)] + [""]
        reading["layout_coverage"]["padding"] = padding
        missing = target - len(canonical_bytes(reading))
        if 0 <= missing <= 16384:
            padding[-1] = "x" * missing
            reading["layout_coverage"]["padding"] = padding
            assert len(canonical_bytes(reading)) == target
            return
    raise AssertionError("unable to fit reading context to its wire bound")


def test_reading_context_accepts_published_bound_and_refuses_one_byte_over():
    def exact(reading):
        _upgrade_to_v3(reading)
        _fit_reading_size(reading, 192 * 1024)
    assert validate_narrative_response(*changed(exact)).to_dict()["reading_context"]
    def over(reading):
        _upgrade_to_v3(reading)
        _fit_reading_size(reading, 192 * 1024 + 1)
    with pytest.raises(NarrativeTransportError, match="reading_bytes_limit"):
        validate_narrative_response(*changed(over))


def test_actual_080_wire_keeps_legacy_context_shape():
    request, body, receipt = actual("080")
    value = validate_narrative_response(request, body, receipt).to_dict()
    assert "reading_context" not in value
    assert value["evidence_spans"] == json.loads(body)["evidence_spans"]
    assert value["schema_version"] == "revenue-narrative-context/1"


def test_real_reader_subprocess_preserves_the_actual_public_context(tmp_path):
    request, body, receipt = actual()
    baseline = {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    value = read_narrative_context(
        request,
        catalog_config=tmp_path / "catalog.yaml",
        reader_command=_fake(tmp_path, body, receipt),
    ).to_dict()
    assert value["reading_context"] == json.loads(body)["reading_context"]
    for name, content in baseline.items():
        assert (tmp_path / name).read_bytes() == content
    (tmp_path / "provider.py").unlink()


def test_cli_projection_retains_validated_reading_context(monkeypatch):
    import narrative_source_preparation as cli

    request, body, receipt = actual()
    context = validate_narrative_response(request, body, receipt)
    output, errors = io.BytesIO(), io.BytesIO()
    monkeypatch.setattr(cli, "read_narrative_context", lambda *args, **kwargs: context)
    monkeypatch.setattr(
        cli.sys, "stdin", SimpleNamespace(buffer=io.BytesIO(canonical_bytes(request)))
    )
    monkeypatch.setattr(cli.sys, "stdout", SimpleNamespace(buffer=output))
    monkeypatch.setattr(cli.sys, "stderr", SimpleNamespace(buffer=errors))
    assert (
        cli.main(
            ["--company-wiki-catalog-config", str(ROOT / "isolated-not-opened.yaml")]
        )
        == 0
    )
    assert not errors.getvalue()
    assert (
        json.loads(output.getvalue())["reading_context"]
        == json.loads(body)["reading_context"]
    )


def projected_context(two_parents=False):
    request, body, receipt = projected_wire()
    bundle, receipt = json.loads(body), json.loads(receipt)
    context = deepcopy(json.loads(actual()[1])["reading_context"])
    if two_parents:
        second = deepcopy(bundle["evidence_spans"][0])
        parent = bundle["subject_binding"]["parent_source_refs"][0]
        second["source_id"] = parent["source_id"]
        second["structured_value"]["parent_content_sha256"] = parent["content_sha256"]
        second["output_sha256"] = hashlib.sha256(
            canonical_bytes(
                {
                    "raw_text": second["raw_text"],
                    "structured_value": second["structured_value"],
                }
            )
        ).hexdigest()
        second["span_id"] = (
            "urn:company-wiki:evidence-span:sha256:"
            + hashlib.sha256(
                canonical_bytes(
                    {
                        "source_id": second["source_id"],
                        "locator": second["locator"],
                        "output_sha256": second["output_sha256"],
                    }
                )
            ).hexdigest()
        )
        bundle["evidence_spans"].append(second)
        bundle["selection"].update(selected_count=2, source_units=2, candidate_count=2)
        bundle["replay"]["locator_count"] = receipt["locator_count"] = 2
    context["groups"][0]["evidence_ids"] = [
        span["span_id"] for span in bundle["evidence_spans"]
    ]
    bundle["reading_context"] = context
    raw, receipt = _resign(request, bundle, receipt)
    return request, raw, receipt


def test_official_json_projection_preserves_scope_and_context():
    request, body, receipt = projected_context()
    value = validate_narrative_response(request, body, receipt).to_dict()
    assert value["schema_version"] == "revenue-narrative-context/3"
    assert value["reading_context"] == json.loads(body)["reading_context"]
    assert (
        value["parent_source_refs"]
        == json.loads(body)["subject_binding"]["parent_source_refs"]
    )


def test_reading_group_cannot_borrow_a_different_original_parent():
    with pytest.raises(NarrativeTransportError, match="reading_group_parent_mismatch"):
        validate_narrative_response(*projected_context(two_parents=True))


@pytest.mark.parametrize(
    "mutation",
    [
        "schema",
        "extra",
        "missing",
        "group_type",
        "duplicate_group",
        "missing_ref",
        "duplicate_ref",
        "empty_ref",
        "unknown_policy",
        "unknown_facet",
        "path",
        "raw_body",
        "false_count",
        "false_limited",
        "partial_sampling_fields",
        "deferred_count",
        "deferred_limited",
        "unknown_diagnostic",
        "boolean_page",
    ],
)
def test_shared_reading_shape_and_reference_errors_are_explicit(mutation):
    def mutate(context):
        if mutation == "schema":
            context["schema_version"] = "du-production-reading/2"
        elif mutation == "extra":
            context["made_up"] = "value"
        elif mutation == "missing":
            del context["groups"]
        elif mutation == "group_type":
            context["groups"] = {}
        elif mutation == "duplicate_group":
            context["groups"].append(deepcopy(context["groups"][0]))
        elif mutation == "missing_ref":
            context["groups"][0]["evidence_ids"][0] = "unknown-span"
        elif mutation == "duplicate_ref":
            context["groups"][0]["evidence_ids"] *= 2
        elif mutation == "empty_ref":
            context["groups"][0]["evidence_ids"] = []
        elif mutation == "unknown_policy":
            context["reading_policies"][0]["new_unpublished_field"] = True
        elif mutation == "unknown_facet":
            context["business_facets"][0]["new_unpublished_field"] = True
        elif mutation == "path":
            context["layout_coverage"]["root_path"] = "somewhere"
        elif mutation == "raw_body":
            context["layout_coverage"]["raw_text"] = "duplicate original"
        elif mutation == "false_count":
            context["unread"]["counts"]["unassigned_unit_ids"] = 0
        elif mutation == "false_limited":
            context["unread"]["limited"] = True
        elif mutation == "partial_sampling_fields":
            del context["unread"]["counts"]
        elif mutation == "deferred_count":
            context["deferred_count"] = True
        elif mutation == "deferred_limited":
            context["deferred_limited"] = True
        elif mutation == "unknown_diagnostic":
            context["selection_diagnostics"] = [
                {"code": "BOUND", "count": 1, "unknown": True}
            ]
        else:
            context["unread"]["opaque_pages"] = [True]

    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(*changed(mutate))


@pytest.mark.parametrize(
    "bound", ["depth", "nodes", "bytes", "string", "groups", "policies", "facets"]
)
def test_reading_context_resource_bounds_are_distinct_contract_errors(bound):
    def mutate(context):
        if bound == "depth":
            nested = None
            for _ in range(16):
                nested = {"x": nested}
            context["layout_coverage"]["nested"] = nested
        elif bound == "nodes":
            context["layout_coverage"]["many"] = [[0] * 3000 for _ in range(12)]
        elif bound == "bytes":
            context["layout_coverage"]["many"] = ["x" * 16000] * 15
        elif bound == "string":
            context["constraints"] = ["x" * 16385]
        elif bound == "groups":
            context["groups"] *= 513
        elif bound == "policies":
            context["reading_policies"] *= 129
        else:
            context["business_facets"] *= 17

    with pytest.raises(NarrativeTransportError, match="reading_.*limit"):
        validate_narrative_response(*changed(mutate))


def test_unsampled_earlier_du1_shape_is_explicitly_supported_without_promoting_coverage():
    def mutate(context):
        for key in ("deferred_count", "deferred_limited", "selection_diagnostics"):
            del context[key]
        for key in ("counts", "limited"):
            del context["unread"][key]

    request, body, receipt = changed(mutate)
    value = validate_narrative_response(request, body, receipt).to_dict()
    assert value["reading_context"] == json.loads(body)["reading_context"]
    assert not value["reading_context"]["unread"]["structure_complete"]


@pytest.mark.parametrize("location", ["bundle", "claim", "versions"])
def test_unpublished_extensions_are_refused_rather_than_dropped(location):
    request, body, receipt = actual()
    bundle, receipt = json.loads(body), json.loads(receipt)
    if location == "bundle":
        bundle["reading_dependencies"] = {"schema_version": "invented"}
    elif location == "claim":
        bundle["summary"]["draft"]["claims"][0]["evidence_group_ids"] = []
    else:
        bundle["versions"]["guessed_causal_version"] = "1"
    body, receipt = _resign(request, bundle, receipt)
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(request, body, receipt)
