"""Pure optional summary-use lineage over one already verified RF context.

This joins explicit research choices to existing original-text citations and
native dependencies. It performs no IO, source classification or calculation.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from company_wiki_narrative_contracts import (
    NarrativeTransportError,
    validate_narrative_ref,
)
from contracts.evidence import canonical_sha256
from narrative_citation_context import citation_dependency

BINDING_SCHEMA = "revenue-summary-use-binding/1"
RECEIPT_SCHEMA = "revenue-summary-use/1"
_CHOICE_FIELDS = {"schema_version", "summary_claim_id", "research_reason"}
MAX_REASON_CHARS = 2048


class SummaryUsageError(ValueError):
    """Stable, bounded summary-use refusal; no caller text is echoed."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise SummaryUsageError(code)


def _object(value: Any, code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SummaryUsageError(code)
    return value


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def _ids(value: Any, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not _text(key) for key in value):
        raise SummaryUsageError("summary_use_scope_invalid")
    _require(
        (allow_empty or bool(value)) and len(set(value)) == len(value),
        "summary_use_scope_invalid",
    )
    return value


def _summary(value: dict, request: dict | None = None) -> tuple[dict, list[dict]]:
    try:
        ref = validate_narrative_ref(value.get("narrative_ref"))
    except (NarrativeTransportError, TypeError, ValueError) as exc:
        raise SummaryUsageError("summary_use_reference_invalid") from exc
    receipt = _object(value.get("read_receipt"), "summary_use_reference_invalid")
    _require(
        receipt.get("status") == "ok" and receipt.get("narrative_ref") == ref,
        "summary_use_reference_mismatch",
    )
    if request is not None:
        _require(
            request.get("narrative_ref") == ref
            and request.get("as_of_date") == value.get("as_of_date"),
            "summary_use_request_mismatch",
        )
    summary = _object(value.get("summary"), "summary_use_summary_unavailable")
    draft = _object(summary.get("draft"), "summary_use_summary_unavailable")
    _require(
        summary.get("status") == "completed"
        and draft.get("status") in {"draft", "needs_review"},
        "summary_use_summary_unavailable",
    )
    claims = draft.get("claims")
    _require(
        isinstance(claims, list) and bool(claims), "summary_use_summary_unavailable"
    )
    if not isinstance(claims, list):
        raise SummaryUsageError("summary_use_summary_unavailable")
    ids = [
        claim.get("claim_id") if isinstance(claim, dict) else None for claim in claims
    ]
    _require(
        all(_text(key) for key in ids) and len(set(ids)) == len(ids),
        "summary_use_summary_ids_invalid",
    )
    if value.get("schema_version") == "revenue-narrative-context/3":
        subject = _object(value.get("subject_binding"), "summary_use_reference_invalid")
        _require(
            draft.get("subject_id") == subject.get("item_key")
            and draft.get("subject_sha256") == subject.get("subject_sha256"),
            "summary_use_summary_identity_mismatch",
        )
    else:
        source = _object(value.get("source_ref"), "summary_use_reference_invalid")
        _require(
            ref.get("source_ref") == source
            and draft.get("source_id") == source.get("source_id")
            and draft.get("source_sha256") == source.get("content_sha256"),
            "summary_use_summary_identity_mismatch",
        )
    _require(
        draft.get("status") != "needs_review"
        or value.get("quality_status") == "needs_review",
        "summary_use_quality_mismatch",
    )
    if "summary_assessment" in value:
        report = _object(value["summary_assessment"], "summary_use_assessment_invalid")
        _require(
            report.get("claims_sha256") == canonical_sha256(claims),
            "summary_use_claims_hash_mismatch",
        )
        _require(
            report.get("semantic_status")
            == report.get("subfact_coverage_status")
            == "not_evaluated",
            "summary_use_assessment_invalid",
        )
    return draft, claims


def summary_use_entry(
    value: dict,
    *,
    request: dict,
    choice: Any,
    resolution: dict,
    source_ref: dict,
    native_claim: dict,
    formula_refs: list[dict],
) -> dict:
    """Join caller's ID/reason to owner-computed citation and native claim data."""
    options = _object(choice, "summary_use_binding_invalid")
    _require(
        set(options) == _CHOICE_FIELDS
        and options.get("schema_version") == BINDING_SCHEMA,
        "summary_use_binding_invalid",
    )
    selected_id, reason = (
        options.get("summary_claim_id"),
        options.get("research_reason"),
    )
    _require(
        _text(selected_id)
        and isinstance(reason, str)
        and _text(reason)
        and len(reason) <= MAX_REASON_CHARS,
        "summary_use_binding_invalid",
    )
    draft, claims = _summary(value, request)
    selected = next(
        (claim for claim in claims if claim["claim_id"] == selected_id), None
    )
    if selected is None:
        raise SummaryUsageError("summary_use_claim_unknown")
    support, context = (
        _ids(selected.get("evidence_ids")),
        _ids(selected.get("context_evidence_ids", []), allow_empty=True),
    )
    _require(not set(support).intersection(context), "summary_use_scope_invalid")
    span_id = resolution.get("span_id")
    _require(span_id in support, "summary_use_selected_span_not_support")
    known = {span["span_id"]: span for span in value["evidence_spans"]}
    parents = (
        value["parent_source_refs"]
        if value["schema_version"] == "revenue-narrative-context/3"
        else [value["source_ref"]]
    )
    _require(
        source_ref in parents
        and all(
            key in known and known[key]["source_id"] == source_ref["source_id"]
            for key in support + context
        ),
        "summary_use_parent_mismatch",
    )
    if resolution["closure"] == "citation_view":
        _require(
            set(support) == set(resolution["support_evidence_ids"])
            and set(context) == set(resolution["context_evidence_ids"]),
            "summary_use_citation_scope_mismatch",
        )
    elif resolution["closure"] == "ungrouped":
        _require(
            support == [span_id] and not context, "summary_use_closure_unavailable"
        )
    else:
        raise SummaryUsageError("summary_use_closure_unavailable")
    _require(
        bool(formula_refs)
        and native_claim.get("target_type") == "parameter"
        and native_claim.get("support_type") == "rationale_support",
        "summary_use_native_dependency_missing",
    )
    _require(
        native_claim.get("excerpt") == known[span_id]["raw_text"]
        and native_claim.get("content_sha256") == source_ref["content_sha256"],
        "summary_use_original_claim_mismatch",
    )
    _require(type(selected.get("needs_review")) is bool, "summary_use_quality_mismatch")
    _require(
        not selected["needs_review"]
        or (
            draft["status"] == "needs_review"
            and value.get("quality_status") == "needs_review"
        ),
        "summary_use_quality_mismatch",
    )
    return {
        "summary_claim_id": selected["claim_id"],
        "summary_claim_sha256": canonical_sha256(selected),
        "claim_type": selected["claim_type"],
        "modality": selected["modality"],
        "needs_review": selected["needs_review"],
        "support_evidence_ids": list(support),
        "context_evidence_ids": list(context),
        "source_ref": deepcopy(source_ref),
        "span_id": span_id,
        "rf_claim_id": native_claim["claim_id"],
        "parameter_id": native_claim["target_id"],
        "formula_refs": deepcopy(formula_refs),
        "research_reason": reason,
        "citation": citation_dependency(
            resolution=resolution,
            claim_id=native_claim["claim_id"],
            parameter_id=native_claim["target_id"],
        ),
    }


def summary_use_receipt(value: dict, entries: list[dict]) -> dict:
    """Serialize only actual joined uses; reading alone has no such receipt."""
    _require(bool(entries), "summary_use_native_dependency_missing")
    draft, claims = _summary(value)
    report = value.get("summary_assessment")
    return {
        "schema_version": RECEIPT_SCHEMA,
        "status": "used_in_parameter_rationale",
        "narrative_ref": deepcopy(value["narrative_ref"]),
        "claims_sha256": canonical_sha256(claims),
        "quality_status": value["quality_status"],
        "selection": deepcopy(value["selection"]),
        "draft_status": draft["status"],
        "assessment_sha256": canonical_sha256(report) if report is not None else None,
        "semantic_status": report["semantic_status"]
        if isinstance(report, dict)
        else None,
        "subfact_coverage_status": report["subfact_coverage_status"]
        if isinstance(report, dict)
        else None,
        "entries": deepcopy(entries),
    }
