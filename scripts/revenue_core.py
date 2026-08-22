"""Core validation and calculation primitives for revenue-only forecasts."""

from __future__ import annotations

import copy
import os
import shutil
from pathlib import Path
from typing import Any

from model_registry import (  # noqa: E402  re-export
    MODEL_RATIO_DRIVERS as REGISTERED_MODEL_RATIO_DRIVERS,
    MODEL_SPECS as REGISTERED_MODEL_SPECS,
    ModelRegistryError,
    calculate_registered_model,
)
from contracts.evidence import (  # noqa: E402, F811  re-export
    Collector,
    ForecastInputError,
    MultiValidationError,
    build_host_receipt,  # noqa: F401  re-export for consumers
    canonical_sha256,
    collect_mode,
    finite_number,
    parse_iso_date,
    period_year,
    require,
    text_sha256,
    valid_source_url,
    validate_claim_ids,
    validate_source_capture,
)

from revenue_constraints import (  # noqa: E402  re-export
    RevenueConstraintError,
    apply_revenue_constraints,
    constraint_parameter_ids,
    validate_revenue_constraints,
)


SKILL_VERSION = "4.0.0"
# Compatibility name retained in serialized forecasts and snapshots.
ENGINE_VERSION = SKILL_VERSION

MODEL_SPECS = REGISTERED_MODEL_SPECS
MODEL_RATIO_DRIVERS = REGISTERED_MODEL_RATIO_DRIVERS



def _build_forecast_draft(data: dict[str, Any]) -> dict[str, Any]:
    """Compute the revenue forecast result without a publication receipt.

    The draft carries the execution receipt (what the runtime actually ran) but
    no ``publication_receipt`` and no ``result_sha256``. It is private and must
    never be handed to invest-* consumers; only ``run_forecast`` publishes it.
    """
    validated = validate_document(data)
    result = _run_forecast_core(data)
    result["schema_version"] = data["schema_version"]
    result["engine_version"] = ENGINE_VERSION
    result["research_coverage"] = {
        "dimensions": validated["research_coverage"]["records"],
        "counts": validated["research_coverage"]["counts"],
    }
    result["management_target_coverage"] = add_management_target_analysis(
        validated, result
    )
    add_scenario_analysis(data, validated, result)
    result["growth_driver_analysis"] = calculate_growth_driver_analysis(
        validated, result
    )
    sensitivities = calculate_sensitivities(data, result)
    result["sensitivities"] = sensitivities
    result["theme_analysis"] = calculate_theme_analysis(data, validated, result)
    result["confidence"] = calculate_confidence(data, validated, result, sensitivities)
    result["forecast_version"] = data.get(
        "forecast_version", f"{data['as_of_date']}-v1"
    )
    result["data_gaps"] = list(
        dict.fromkeys(
            [
                *data.get("data_gaps", []),
                *validated["research_coverage"]["gap_messages"],
                *validated["growth_driver_tree"]["gap_messages"],
                *validated["management_target_coverage"]["gap_messages"],
            ]
        )
    )
    # R1.1 (N-01): anchor and embed the input only after every engine step has
    # run — normalization mutates ``data``, so hashing earlier would bind the
    # artifact to a state that no longer exists at validation time (and lets a
    # forged artifact carry an input_document that hashes to nothing).
    result["input_sha256"] = canonical_sha256(data)
    result["input_document"] = copy.deepcopy(data)
    result["disconfirming_indicators"] = list(data.get("disconfirming_indicators", []))
    result["parameter_trace"] = data["parameters"]
    result["sources"] = list(validated["source_index"].values())
    result["evidence_claims"] = list(validated["claim_index"].values())
    result["historical_accuracy_records"] = copy.deepcopy(
        data.get("historical_accuracy_records", [])
    )
    result["workflow_compliance_receipt"] = build_workflow_compliance_receipt(
        result["input_sha256"],
        result["sources"],
        result["evidence_claims"],
        result["parameter_trace"],
        result["data_gaps"],
    )
    return result


def attestation_capability() -> bool:
    """True when an external attestation provider is configured and runnable.

    The provider is named by the ``REVENUE_ATTESTATION_PROVIDER`` environment
    variable (a command on PATH or an absolute path to an executable).  Without
    a runnable provider the runtime can only publish ``"unattested"`` formal
    artifacts, which invest-* consumers reject by default (R2.1).
    """
    provider = os.environ.get("REVENUE_ATTESTATION_PROVIDER")
    if not provider:
        return False
    resolved = shutil.which(provider) or Path(provider).expanduser()
    return resolved is not None and os.path.isfile(resolved)


def run_forecast(data: dict[str, Any], *, mode: str = "formal") -> dict[str, Any]:
    """Run the complete revenue forecast and return the published result.

    The result is computed as a private draft and only published after passing
    the self-contained output validator; any validation failure raises before a
    caller ever sees a publication receipt.

    *mode* may be ``"formal"`` (default — all hard gates must pass) or
    ``"draft"`` (unresolved data gaps are recorded as structured limitations
    but the result is returned with ``formal_output_mode="draft"``).
    invest-* consumers must only accept ``"formal"`` artifacts.

    Formal publications carry an ``attestation_status`` (R2.1): ``"host_signed"``
    only when an external attestation provider is configured, otherwise
    ``"unattested"`` (rejected by invest-* consumers by default).
    """
    from revenue_publication import (
        build_publication_receipt,
        build_draft_receipt,
        validate_publication_receipt,
    )
    from revenue_report import validate_published_forecast

    if mode not in {"formal", "draft"}:
        raise ValueError("mode must be 'formal' or 'draft'")
    result = _build_forecast_draft(data)
    # Phase 6 A1: validate BEFORE signing. The draft has no publication receipt
    # and no result hash; the strong validator recomputes every gate (including
    # input-gated sensitivity shocks) from the embedded input document. Only a
    # strong-validation verification context may issue a formal receipt.
    context = validate_published_forecast(result, data)
    if mode == "draft":
        result.setdefault("draft_limitations", []).append(
            "formal publication gates passed; draft mode requested"
        )
        result["publication_receipt"] = build_draft_receipt(result)
    else:
        # R2.1: host_signed requires a configured, runnable attestation
        # provider; otherwise the publication is explicitly unattested.
        attestation_status = "host_signed" if attestation_capability() else "unattested"
        result["publication_receipt"] = build_publication_receipt(
            result, context, attestation_status=attestation_status
        )
    result["result_sha256"] = canonical_sha256(result)
    if mode == "formal":
        validate_publication_receipt(result)
        # R1.2 (N-01): a formal publication is only real once it is registered —
        # the registry is the artifact-external authority.  A missing or
        # unwritable registry fails the whole publication (fail closed).
        from publication_registry import RegistryError, register_publication

        try:
            register_publication(result)
        except RegistryError as exc:
            raise ForecastInputError(
                f"formal publication failed: registry unavailable: {exc}"
            ) from exc
    return result


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


from forecast.calc import (  # noqa: E402  re-export
    MODEL_DRIVER_DIMENSIONS,
    evaluate_derived_formula,
    parameter_values,
    resolve_driver_series,
    calculate_cagr,
    referenced_parameter_ids,
    parameter_driver_roles,
    collect_parameter_roles,
    base_forecast_parameter_ids,
    base_segment_parameter_ids,
)


from contracts.document import (  # noqa: E402  re-export
    validate_top_level,
    validate_historical_revenue,
    validate_sources,
    validate_parameters,
    validate_evidence_claims,
    validate_scenario_probabilities,
    validate_historical_accuracy_records,
    validate_source_coverage,
    validate_base_reconciliation,
    validate_document,
)


from contracts.constants import (  # noqa: E402  re-export
    ADJUSTMENT_CATEGORIES,
    FORECAST_SCHEMA_VERSION,
    GROWTH_DRIVER_COUNTEREVIDENCE_STATUSES,
    GROWTH_DRIVER_INFERENCE_DISTANCES,
    GROWTH_DRIVER_PERSISTENCE,
    GROWTH_DRIVER_TREE_STATUSES,
    MANAGEMENT_COMMUNICATION_CATEGORIES,
    MANAGEMENT_COMMUNICATION_STATUSES,
    MANAGEMENT_TARGET_COMPARISONS,
    MANAGEMENT_TARGET_MEASUREMENT_BASES,
    MANAGEMENT_TARGET_PERIMETERS,
    MANAGEMENT_TARGET_TREATMENTS,
    MONETARY_DIMENSIONS,
    OPT_IN_SCHEMA_VERSION,
    PARAMETER_DIMENSIONS,
    PARAMETER_KINDS,
    PRESENTATIONS,
    PUBLICATION_RECEIPT_SCHEMA_VERSION,
    RECOGNITION_MODES,
    RECOGNITION_TIMING,
    RESEARCH_COVERAGE_STATUSES,
    RESEARCH_DIMENSIONS,
    SCENARIOS,
    SKILL_VERSION,
    SOURCE_RANKS,
    SUPPORTED_FORECAST_SCHEMA_VERSIONS,
    TIME_BASES,
    WORKFLOW_RECEIPT_SCHEMA_VERSION,
)


from research.drivers import (  # noqa: E402  re-export
    validate_growth_driver_tree,
    calculate_growth_driver_analysis,
)


from research.targets import (  # noqa: E402  re-export
    validate_management_target_coverage,
    add_management_target_analysis,
)


from research.coverage import (  # noqa: E402  re-export
    validate_research_coverage,
)


from analysis.sensitivity import (  # noqa: E402  re-export
    calculate_sensitivities,
    calculate_theme_analysis,
)


from analysis.confidence import (  # noqa: E402  re-export
    parameter_revenue_weights,
    calculate_confidence,
)


from forecast.segments import (  # noqa: E402  re-export
    calculate_model_path,
    calculate_segment_forecasts,
    validate_recognition_metadata,
    apply_revenue_recognition,
    resolve_adjustments,
    calculate_company_forecast,
    _run_forecast_core,
    add_scenario_analysis,
)


__all__ = [
    'ADJUSTMENT_CATEGORIES',
    'Collector',
    'FORECAST_SCHEMA_VERSION',
    'GROWTH_DRIVER_COUNTEREVIDENCE_STATUSES',
    'GROWTH_DRIVER_INFERENCE_DISTANCES',
    'GROWTH_DRIVER_PERSISTENCE',
    'GROWTH_DRIVER_TREE_STATUSES',
    'MANAGEMENT_COMMUNICATION_CATEGORIES',
    'MANAGEMENT_COMMUNICATION_STATUSES',
    'MANAGEMENT_TARGET_COMPARISONS',
    'MANAGEMENT_TARGET_MEASUREMENT_BASES',
    'MANAGEMENT_TARGET_PERIMETERS',
    'MANAGEMENT_TARGET_TREATMENTS',
    'MODEL_DRIVER_DIMENSIONS',
    'MONETARY_DIMENSIONS',
    'OPT_IN_SCHEMA_VERSION',
    'ModelRegistryError',
    'MultiValidationError',
    'PARAMETER_DIMENSIONS',
    'PARAMETER_KINDS',
    'PRESENTATIONS',
    'PUBLICATION_RECEIPT_SCHEMA_VERSION',
    'RECOGNITION_MODES',
    'RECOGNITION_TIMING',
    'RESEARCH_COVERAGE_STATUSES',
    'RESEARCH_DIMENSIONS',
    'RevenueConstraintError',
    'SCENARIOS',
    'SOURCE_RANKS',
    'SUPPORTED_FORECAST_SCHEMA_VERSIONS',
    'TIME_BASES',
    'apply_revenue_constraints',
    'apply_revenue_recognition',
    'base_forecast_parameter_ids',
    'base_segment_parameter_ids',
    'calculate_cagr',
    'calculate_company_forecast',
    'calculate_model_path',
    'calculate_registered_model',
    'calculate_segment_forecasts',
    'collect_mode',
    'collect_parameter_roles',
    'constraint_parameter_ids',
    'evaluate_derived_formula',
    'finite_number',
    'parameter_driver_roles',
    'parameter_revenue_weights',
    'parameter_values',
    'parse_iso_date',
    'period_year',
    'referenced_parameter_ids',
    'require',
    'resolve_adjustments',
    'resolve_driver_series',
    'text_sha256',
    'valid_source_url',
    'validate_base_reconciliation',
    'validate_claim_ids',
    'validate_evidence_claims',
    'validate_growth_driver_tree',
    'validate_historical_accuracy_records',
    'validate_historical_revenue',
    'validate_management_target_coverage',
    'validate_parameters',
    'validate_recognition_metadata',
    'validate_research_coverage',
    'validate_revenue_constraints',
    'validate_scenario_probabilities',
    'validate_source_capture',
    'validate_source_coverage',
    'validate_sources',
    'validate_top_level',
]
