"""Pure workflow-compliance receipt construction.

Extracted from ``revenue_core`` so the report layer can consume the same leaf
contract without importing the core aggregate. ``revenue_core`` re-exports the
function, keeping ``from revenue_core import build_workflow_compliance_receipt``
compatible for existing callers.
"""
from __future__ import annotations

from typing import Any

from contracts.constants import WORKFLOW_RECEIPT_SCHEMA_VERSION
from contracts.evidence import canonical_sha256


def build_workflow_compliance_receipt(
    input_sha256: str,
    sources: list[dict[str, Any]],
    evidence_claims: list[dict[str, Any]],
    parameters: list[dict[str, Any]],
    data_gaps: list[str],
) -> dict[str, Any]:
    """Recompute the formal workflow receipt from validated revenue artifacts."""
    capture_hashes = sorted(source["capture"]["receipt_sha256"] for source in sources)
    receipt = {
        "receipt_schema_version": WORKFLOW_RECEIPT_SCHEMA_VERSION,
        "status": "pass",
        "workflow": "revenue_forecast_nine_dimension_driver_model",
        "execution_mode": "deterministic_runtime",
        "gate_ids": [
            "input_contract",
            "source_capture",
            "evidence_claims",
            "research_coverage",
            "management_targets",
            "growth_driver_tree",
            "revenue_model",
        ],
        "input_sha256": input_sha256,
        "source_capture_receipt_sha256s": capture_hashes,
        "source_capture_count": len(capture_hashes),
        "checked_claim_count": len(evidence_claims),
        "assumption_parameter_ids": sorted(
            parameter["parameter_id"]
            for parameter in parameters
            if parameter["kind"] in {"analyst_assumption", "scenario_stress"}
        ),
        "data_gap_count": len(data_gaps),
        "data_gaps_sha256": canonical_sha256(data_gaps),
        "prompt_injection_flagged_source_ids": sorted(
            source["source_id"]
            for source in sources
            if source["capture"]["prompt_injection_status"] == "detected_and_ignored"
        ),
        "untrusted_content_treatment": "data_only_never_instructions",
        "formal_output_authority": "validated_runtime_renderer_only",
        "freeform_formal_output_allowed": False,
    }
    receipt["receipt_sha256"] = canonical_sha256(receipt)
    return receipt
