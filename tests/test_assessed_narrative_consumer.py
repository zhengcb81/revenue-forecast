"""Forward-compatible source observations; no CWP imports or reclassification."""

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from company_wiki_narrative_contracts import (  # noqa: E402
    validate_narrative_response,
    NarrativeTransportError,
)
from source_narrative_context import narrative_read_receipt  # noqa: E402
from contracts.evidence import canonical_sha256  # noqa: E402
from test_company_wiki_narrative_reader import _valid, _resign  # noqa: E402


def assessed_wire():
    import json

    request, body, raw_receipt = _valid()
    bundle, receipt = json.loads(body), json.loads(raw_receipt)
    bundle["schema_version"] = "narrative-bundle/2.1"
    bundle["summary"]["model"]["prompt_version"] = "reading-source-scoped/4.2.0"
    bundle["versions"].update(
        prompt="reading-source-scoped/4.2.0", bundle_producer="1.1.0"
    )
    claims = bundle["summary"]["draft"]["claims"]
    # Explicitly synthetic wire observations, not a producing source-plan proof.
    report = {
        "schema_version": "summary-assessment/1",
        "validator": {
            "version": "source-summary-assessment/1.0.0",
            "implementation_sha256": "a" * 64,
            "dependencies": {"synthetic_wire_fixture": "b" * 64},
        },
        "source_plan_sha256": "c" * 64,
        "plan_max_claims": 40,
        "source_admission_sha256": "d" * 64,
        "claims_sha256": canonical_sha256(claims),
        "scope": "selected_source_tasks_only",
        "source_admitted_task_keys": ["t1"],
        "requested_task_keys": ["t1"],
        "emitted_task_keys": ["t1"],
        "missing_requested_task_keys": [],
        "budget_deferred_task_keys": [],
        "excluded_tasks": [],
        "requested_emission_complete": True,
        "admitted_emission_complete": True,
        "subfact_coverage_status": "not_evaluated",
        "semantic_status": "not_evaluated",
        "known_constraint_status": "no_known_violation",
        "diagnostics": [],
        "diagnostic_count": 0,
        "diagnostics_limited": False,
        "diagnostic_claim_ids": [],
    }
    report["validator"]["dependencies"] = {
        key: canonical_sha256({"synthetic_dependency": key})
        for key in (
            "matching",
            "task_plan",
            "admission",
            "scoped_view",
            "encoding",
            "claim_roles",
            "assessment",
        )
    }
    report["validator"]["implementation_sha256"] = canonical_sha256(
        report["validator"]["dependencies"]
    )
    bundle["summary_assessment"] = report
    return request, bundle, receipt


def read(request, bundle, receipt):
    body, wire_receipt = _resign(request, bundle, receipt)
    return validate_narrative_response(request, body, wire_receipt)


def test_assessment_is_preserved_as_source_observation_not_rf_semantic_verdict():
    request, bundle, receipt = assessed_wire()
    context = read(request, bundle, receipt)
    value = context.to_dict()
    assert value["schema_version"] == "revenue-narrative-context/1"
    assert value["summary_assessment"] == bundle["summary_assessment"]
    consumed = narrative_read_receipt(context)
    assert consumed["summary_assessment"] == bundle["summary_assessment"]
    assert consumed["summary_assessment"]["semantic_status"] == "not_evaluated"
    consumed["summary_assessment"]["requested_task_keys"].clear()
    assert context.to_dict()["summary_assessment"]["requested_task_keys"] == ["t1"]


@pytest.mark.parametrize(
    "mutation", ["missing", "legacy", "claims", "producer", "semantics", "risk_quality"]
)
def test_invalid_observation_envelope_is_refused_without_source_reparse(mutation):
    request, bundle, receipt = assessed_wire()
    if mutation == "missing":
        del bundle["summary_assessment"]
    elif mutation == "legacy":
        bundle["schema_version"] = "narrative-bundle/2.0"
        del bundle["summary_assessment"]
    elif mutation == "claims":
        bundle["summary_assessment"]["claims_sha256"] = "f" * 64
    elif mutation == "producer":
        bundle["versions"]["bundle_producer"] = "1.0.0"
    elif mutation == "semantics":
        bundle["summary_assessment"]["semantic_status"] = "passed"
    else:
        report = bundle["summary_assessment"]
        report.update(
            diagnostic_count=1,
            known_constraint_status="diagnostics_found",
            diagnostic_claim_ids=[bundle["summary"]["draft"]["claims"][0]["claim_id"]],
            diagnostics=[
                {
                    "task_key": "t1",
                    "claim_id": bundle["summary"]["draft"]["claims"][0]["claim_id"],
                    "source_span_id": bundle["evidence_spans"][0]["span_id"],
                    "rule_code": "possible_attribution_loss",
                }
            ],
        )
    with pytest.raises(NarrativeTransportError):
        read(request, bundle, receipt)


def test_projected_context_preserves_observations_without_a_new_context_variant():
    import json
    from test_w04_public_consumer import projected_wire

    request, body, raw_receipt = projected_wire()
    bundle, receipt = json.loads(body), json.loads(raw_receipt)
    _, raw_bundle, _ = assessed_wire()
    bundle["schema_version"] = "narrative-bundle/3.1"
    bundle["summary"]["model"]["prompt_version"] = "reading-source-scoped/4.2.0"
    bundle["versions"].update(
        prompt="reading-source-scoped/4.2.0", bundle_producer="1.1.0"
    )
    bundle["summary_assessment"] = raw_bundle["summary_assessment"]
    bundle["summary_assessment"]["claims_sha256"] = canonical_sha256(
        bundle["summary"]["draft"]["claims"]
    )
    context = read(request, bundle, receipt)
    assert context.to_dict()["schema_version"] == "revenue-narrative-context/3"
    assert (
        narrative_read_receipt(context)["summary_assessment"]
        == bundle["summary_assessment"]
    )


def test_skipped_new_protocol_does_not_fabricate_a_model_or_assessment():
    request, bundle, receipt = assessed_wire()
    bundle["summary"].update(status="summary_not_needed", draft=None, model=None)
    bundle["versions"]["model"] = None
    bundle["selection"].update(status="skipped_no_narrative", selected_count=0)
    bundle.update(
        quality_status="skipped_no_narrative",
        evidence_spans=[],
        summary_assessment=None,
    )
    bundle["transcript_byte_bindings"] = []
    bundle["replay"]["locator_count"] = 0
    receipt.update(
        locator_count=0,
        selection_status="skipped_no_narrative",
        quality_status="skipped_no_narrative",
    )
    context = read(request, bundle, receipt)
    assert context.to_dict()["summary_assessment"] is None
    assert context.to_dict()["summary"]["model"] is None


@pytest.mark.parametrize(
    "mutation",
    [
        "dependency_key",
        "dependency_hash",
        "excluded_status",
        "excluded_overlap",
        "excluded_reason",
        "excluded_representative",
        "diagnostic_rule",
        "diagnostic_task",
        "diagnostic_span",
        "diagnostic_null_scope",
        "quality_laundering",
        "skip_model",
    ],
)
def test_published_wire_invariants_remain_permanent_regressions(mutation):
    request, bundle, receipt = assessed_wire()
    report = bundle["summary_assessment"]
    if mutation == "dependency_key":
        del report["validator"]["dependencies"]["matching"]
        report["validator"]["implementation_sha256"] = canonical_sha256(
            report["validator"]["dependencies"]
        )
    elif mutation == "dependency_hash":
        report["validator"]["implementation_sha256"] = "f" * 64
    elif mutation.startswith("excluded_"):
        row = {
            "task_key": "t2",
            "status": "unavailable",
            "reason": "source_table_unresolved",
        }
        if mutation == "excluded_status":
            row["status"] = "approved"
        elif mutation == "excluded_overlap":
            row["task_key"] = "t1"
        elif mutation == "excluded_reason":
            row["reason"] = "unstructured prose"
        else:
            row.update(
                status="duplicate", reason="duplicate_scope", representative="t999"
            )
        report["excluded_tasks"] = [row]
    elif mutation.startswith("diagnostic_"):
        claim = bundle["summary"]["draft"]["claims"][0]
        claim["needs_review"] = True
        bundle["summary"]["draft"]["status"] = "needs_review"
        bundle["quality_status"] = receipt["quality_status"] = "needs_review"
        report.update(
            diagnostic_count=1,
            known_constraint_status="diagnostics_found",
            diagnostic_claim_ids=[claim["claim_id"]],
            claims_sha256=canonical_sha256(bundle["summary"]["draft"]["claims"]),
        )
        row = {
            "task_key": "t1",
            "claim_id": claim["claim_id"],
            "source_span_id": bundle["evidence_spans"][0]["span_id"],
            "rule_code": "possible_attribution_loss",
        }
        if mutation == "diagnostic_rule":
            row["rule_code"] = "semantically_approved"
        elif mutation == "diagnostic_task":
            row["task_key"] = "t999"
        elif mutation == "diagnostic_span":
            row["source_span_id"] = "urn:company-wiki:evidence-span:sha256:" + "f" * 64
        else:
            row["rule_code"] = "unmatched_claim_scope"
        report["diagnostics"] = [row]
    elif mutation == "quality_laundering":
        bundle["summary"]["draft"]["status"] = "needs_review"
        bundle["summary"]["draft"]["claims"][0]["needs_review"] = True
        report["claims_sha256"] = canonical_sha256(bundle["summary"]["draft"]["claims"])
    else:
        bundle["summary"].update(status="summary_not_needed", draft=None, model=None)
        bundle["versions"]["model"] = "phantom-model"
        bundle["selection"].update(status="skipped_no_narrative", selected_count=0)
        bundle.update(
            quality_status="skipped_no_narrative",
            evidence_spans=[],
            summary_assessment=None,
        )
        bundle["transcript_byte_bindings"] = []
        bundle["replay"]["locator_count"] = 0
        receipt.update(
            locator_count=0,
            selection_status="skipped_no_narrative",
            quality_status="skipped_no_narrative",
        )
    with pytest.raises(NarrativeTransportError):
        read(request, bundle, receipt)


def recipe_wire(prompt, *, projected=False):
    """Synthetic public wire pairing, not producing source/frame evidence."""
    from copy import deepcopy
    import json

    request, bundle, receipt = assessed_wire()
    report = deepcopy(bundle["summary_assessment"])
    if projected:
        from test_w04_public_consumer import projected_wire

        request, body, raw_receipt = projected_wire()
        bundle, receipt = json.loads(body), json.loads(raw_receipt)
        bundle["schema_version"] = "narrative-bundle/3.1"
    bundle["summary"]["model"]["prompt_version"] = prompt
    bundle["versions"].update(prompt=prompt, bundle_producer="1.1.0")
    if prompt == "reading-source-scoped/4.3.0":
        report["validator"]["version"] = "source-summary-assessment/1.1.0"
        report["validator"]["dependencies"]["assertion_frames"] = canonical_sha256(
            {"synthetic_dependency": "assertion_frames"}
        )
    report["validator"]["implementation_sha256"] = canonical_sha256(
        report["validator"]["dependencies"]
    )
    report["claims_sha256"] = canonical_sha256(bundle["summary"]["draft"]["claims"])
    bundle["summary_assessment"] = report
    return request, bundle, receipt


@pytest.mark.parametrize(
    "prompt", ["reading-source-scoped/4.2.0", "reading-source-scoped/4.3.0"]
)
@pytest.mark.parametrize("projected", [False, True])
def test_explicit_recipe_pairs_preserve_existing_context_and_receipt(prompt, projected):
    request, bundle, receipt = recipe_wire(prompt, projected=projected)
    context = read(request, bundle, receipt)
    value = context.to_dict()
    consumption = narrative_read_receipt(context)
    assert (
        value["schema_version"] == "revenue-narrative-context/3"
        if projected
        else value["schema_version"] == "revenue-narrative-context/1"
    )
    assert consumption["summary_assessment"] == bundle["summary_assessment"]
    assert consumption["status"] == "not_consumed"
    assert consumption["summary_assessment"]["semantic_status"] == "not_evaluated"
    consumption["summary_assessment"]["requested_task_keys"].clear()
    assert context.to_dict()["summary_assessment"]["requested_task_keys"] == ["t1"]


@pytest.mark.parametrize(
    "prompt", ["reading-source-scoped/4.2.0", "reading-source-scoped/4.3.0"]
)
@pytest.mark.parametrize("projected", [False, True])
def test_recipe_skip_has_null_model_and_assessment(prompt, projected):
    request, bundle, receipt = recipe_wire(prompt, projected=projected)
    bundle["summary"].update(status="summary_not_needed", draft=None, model=None)
    bundle["versions"]["model"] = None
    bundle["selection"].update(status="skipped_no_narrative", selected_count=0)
    bundle.update(
        quality_status="skipped_no_narrative",
        evidence_spans=[],
        summary_assessment=None,
    )
    if "transcript_byte_bindings" in bundle:
        bundle["transcript_byte_bindings"] = []
    bundle["replay"]["locator_count"] = 0
    receipt.update(
        locator_count=0,
        selection_status="skipped_no_narrative",
        quality_status="skipped_no_narrative",
    )
    context = read(request, bundle, receipt)
    assert context.to_dict()["summary"]["model"] is None
    assert narrative_read_receipt(context)["summary_assessment"] is None
    assert narrative_read_receipt(context)["status"] == "not_consumed"


@pytest.mark.parametrize(
    "prompt", ["reading-source-scoped/4.2.0", "reading-source-scoped/4.3.0"]
)
@pytest.mark.parametrize(
    "mutation",
    [
        "other_assessor",
        "other_recipe_dependencies",
        "missing_dependency",
        "extra_dependency",
        "unknown_prompt",
        "quality_laundering",
    ],
)
def test_recipe_tuple_cannot_mix_versions_or_dependency_sets(prompt, mutation):
    request, bundle, receipt = recipe_wire(prompt)
    validator = bundle["summary_assessment"]["validator"]
    atomic = prompt == "reading-source-scoped/4.3.0"
    if mutation == "other_assessor":
        validator["version"] = (
            "source-summary-assessment/1.0.0"
            if atomic
            else "source-summary-assessment/1.1.0"
        )
    elif mutation == "other_recipe_dependencies":
        if atomic:
            del validator["dependencies"]["assertion_frames"]
        else:
            validator["dependencies"]["assertion_frames"] = "a" * 64
    elif mutation == "missing_dependency":
        del validator["dependencies"]["matching"]
    elif mutation == "extra_dependency":
        validator["dependencies"]["unknown_dependency"] = "a" * 64
    elif mutation == "unknown_prompt":
        bundle["summary"]["model"]["prompt_version"] = bundle["versions"]["prompt"] = (
            "reading-source-scoped/4.4.0"
        )
    else:
        bundle["summary"]["draft"]["status"] = "needs_review"
    validator["implementation_sha256"] = canonical_sha256(validator["dependencies"])
    with pytest.raises(NarrativeTransportError):
        read(request, bundle, receipt)


@pytest.mark.parametrize(
    "prompt", ["reading-source-scoped/4.2.0", "reading-source-scoped/4.3.0"]
)
@pytest.mark.parametrize(
    "rule",
    [
        "possible_attribution_loss",
        "possible_negation_degree_loss",
        "possible_modality_mismatch",
        "unmatched_claim_scope",
        "ambiguous_claim_scope",
        "possible_current_action_as_future",
        "possible_project_capacity_basis_loss",
    ],
)
def test_diagnostic_rules_belong_to_their_explicit_assessor(prompt, rule):
    request, bundle, receipt = recipe_wire(prompt)
    claim = bundle["summary"]["draft"]["claims"][0]
    claim["needs_review"] = True
    bundle["summary"]["draft"]["status"] = "needs_review"
    bundle["quality_status"] = receipt["quality_status"] = "needs_review"
    unscoped = rule in {"unmatched_claim_scope", "ambiguous_claim_scope"}
    report = bundle["summary_assessment"]
    report.update(
        diagnostic_count=1,
        known_constraint_status="diagnostics_found",
        diagnostic_claim_ids=[claim["claim_id"]],
        claims_sha256=canonical_sha256(bundle["summary"]["draft"]["claims"]),
        diagnostics=[
            {
                "task_key": None if unscoped else "t1",
                "claim_id": claim["claim_id"],
                "source_span_id": None
                if unscoped
                else bundle["evidence_spans"][0]["span_id"],
                "rule_code": rule,
            }
        ],
    )
    if prompt == "reading-source-scoped/4.2.0" and rule in {
        "possible_current_action_as_future",
        "possible_project_capacity_basis_loss",
    }:
        with pytest.raises(NarrativeTransportError):
            read(request, bundle, receipt)
    else:
        context = read(request, bundle, receipt)
        observed = narrative_read_receipt(context)
        assert observed["summary_assessment"] == report
        assert observed["summary_assessment"]["semantic_status"] == "not_evaluated"
        assert observed["quality_status"] == "needs_review"
        assert observed["status"] == "not_consumed"


@pytest.mark.parametrize(
    "rule",
    ["possible_current_action_as_future", "possible_project_capacity_basis_loss"],
)
def test_new_projected_diagnostics_preserve_possible_quality(rule):
    request, bundle, receipt = recipe_wire(
        "reading-source-scoped/4.3.0", projected=True
    )
    claim = bundle["summary"]["draft"]["claims"][0]
    claim["needs_review"] = True
    bundle["summary"]["draft"]["status"] = "needs_review"
    bundle["quality_status"] = receipt["quality_status"] = "needs_review"
    report = bundle["summary_assessment"]
    report.update(
        diagnostic_count=1,
        known_constraint_status="diagnostics_found",
        diagnostic_claim_ids=[claim["claim_id"]],
        claims_sha256=canonical_sha256(bundle["summary"]["draft"]["claims"]),
        diagnostics=[
            {
                "task_key": "t1",
                "claim_id": claim["claim_id"],
                "source_span_id": bundle["evidence_spans"][0]["span_id"],
                "rule_code": rule,
            }
        ],
    )
    context = read(request, bundle, receipt)
    assert narrative_read_receipt(context)["summary_assessment"] == report
    assert context.to_dict()["quality_status"] == "needs_review"
