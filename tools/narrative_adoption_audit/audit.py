"""Read-only narrative adoption observation for final RF forecast artifacts.

This module answers one question: which source-owned information that RF
received is actually referenced by the final forecast's projected nodes
(segment scenarios, annual driver slots, driver-tree evidence, coverage,
targets, adjustments, probabilities), and which is not observable there.

Observation contract (W20 construction card):

* Adoption means an observable canonical citation chain into a *projected*
  node of the final artifact. The embedded ``input_document`` and the
  ``parameter_trace`` echo are input material, never adoption evidence.
* A readable summary, a transported span or a registered source without a
  binding is ``not_observed`` — never "used", and never proven unused.
* ``not_used_when_provable`` needs a structural rule: the claim's parameters
  enter no computation path, or the source partition bars the span from
  support (context_only / unresolved).
* Broken binding material (wrong claim/parameter, wrong source hash, receipt
  from a different run) is ``unverifiable`` with a named reason code.
* The report is a diagnostic. It never rates the forecast, never signs off
  economic quality, and is not a permission gate.

Pure core: no IO, no clock, no network, no model. The CLI owns all IO.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from company_wiki_narrative_contracts import (  # noqa: E402
    validate_narrative_response,
)
from contracts.evidence import canonical_sha256  # noqa: E402
from contracts.evidence import text_sha256  # noqa: E402
from forecast.dependencies import parameter_formula_refs  # noqa: E402

REPORT_SCHEMA = "rf-narrative-adoption-report/1"
CONSUMPTION_SCHEMAS = {
    "revenue-narrative-consumption/1", "revenue-narrative-consumption/3",
}
KNOWN_CONSUMPTION_FIELDS = {
    "schema_version", "status", "narrative_ref", "read_at", "observed_at",
    "quality_status", "selection", "dependencies", "citation_trace",
    "subject_ref", "parent_count", "lineage_sha256",
}
KNOWN_DEPENDENCY_FIELDS = {
    "span_id", "locator", "parser_name", "parser_version", "source_id",
    "source_sha256", "claim_id", "parameter_id", "formula_refs",
    "source_locator", "pointer", "subject_ref",
}
# Top-level keys a published forecast artifact may carry. Anything else is
# reported as unknown material, never interpreted.
KNOWN_FORECAST_FIELDS = {
    "schema_version", "engine_version", "forecast_version", "company_name",
    "as_of_date", "currency", "unit", "fiscal_year_end", "base_year",
    "forecast_years", "historical_revenue", "base_revenue", "segments",
    "consolidated_forecast", "opening_base_bridge", "revenue_constraints",
    "constraint_audit", "research_coverage", "management_target_coverage",
    "growth_driver_analysis", "scenario_probabilities",
    "probability_weighted_forecast", "sensitivities", "theme_analysis",
    "confidence", "data_gaps", "disconfirming_indicators",
    "historical_accuracy_records", "parameter_trace", "sources",
    "evidence_claims", "input_sha256", "input_document",
    "workflow_compliance_receipt", "publication_receipt", "result_sha256",
    "draft_limitations", "reported_total_revenue_parameter_id",
}

LIMITATIONS = (
    "citation_chain_observation_only: a missing citation does not prove the "
    "author's reasoning ignored the material",
    "no_execution_trace: the engine is deterministic over input parameters; "
    "this report observes declared citation wiring, not model cognition",
    "context_evidence_is_not_numeric_support",
    "diagnostic_not_a_permission_gate: no rating and no adoption-rate "
    "sign-off; economic quality stays with RF validation and the four review "
    "roles",
)

_STATUS_ORDER = (
    "used", "not_used_when_provable", "not_observed", "unverifiable",
)

# node_type -> reason code emitted on a "used" item
_USED_REASON = {
    "segment_scenario_driver": "used_via_segment_driver_slot",
    "segment_base_revenue": "used_via_base_revenue",
    "recognition_policy_basis": "used_via_recognition_basis",
    "recognition_progress_parameter": "used_via_progress_parameter",
    "recognition_carry_in_parameter": "used_via_carry_in_parameter",
    "driver_tree_parameter": "used_via_driver_tree_parameter",
    "driver_tree_evidence_node": "used_via_driver_tree_evidence",
    "driver_tree_evidence_sources": "used_via_driver_tree_evidence",
    "coverage_dimension_parameter": "used_via_coverage_dimension",
    "coverage_dimension_source": "used_via_coverage_dimension",
    "management_target_claim": "used_via_management_target",
    "management_target_source": "used_via_management_target",
    "management_target_parameter": "used_via_management_target",
    "management_communication_source": "used_via_management_communication",
    "adjustment_parameter": "used_via_adjustment",
    "scenario_probability": "used_via_scenario_probability",
    "scenario_probability_source": "used_via_scenario_probability",
    "historical_revenue_basis": "used_via_historical_revenue_basis",
    "company_total_parameter": "used_via_company_total",
    "opening_base_adjustment": "used_via_opening_base_adjustment",
    "revenue_constraint_parameter": "used_via_revenue_constraint",
    "derived_parameter_input": "used_via_derived_parameter",
}


class AdoptionAuditError(Exception):
    """Named, machine-readable failure (resource limits, invalid material)."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _diag(diagnostics: list[dict], code: str, detail: str,
          severity: str = "warn", item_id: str | None = None) -> None:
    diagnostics.append(
        {"code": code, "detail": detail, "severity": severity, "item_id": item_id}
    )


def canonical_report_bytes(report: dict) -> bytes:
    """Byte-stable serialisation used for stdout, --output and comparisons."""
    text = json.dumps(report, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))
    return (text + "\n").encode("utf-8")


def _citation_order(citation: dict) -> tuple:
    """Content-determined order: citation unions must not depend on the
    order dependencies arrived in."""
    return (citation.get("node_type", ""), citation.get("location", ""),
            json.dumps(citation.get("ids", {}), sort_keys=True))


def validate_narrative_wire(request: dict, body: bytes, receipt: bytes) -> dict:
    """Validate one public narrative wire triple through the real contract."""
    return validate_narrative_response(request, body, receipt).to_dict()


# ---------------------------------------------------------------------------
# node index: every citation the projected final artifact carries
# ---------------------------------------------------------------------------

def _add(index: dict[str, list[dict]], key: str, citation: dict) -> None:
    index.setdefault(key, []).append(citation)


def _cite(node_type: str, location: str, ids: dict) -> dict:
    return {"node_type": node_type, "location": location, "ids": ids}


class _NodeIndex:
    def __init__(self) -> None:
        self.by_parameter: dict[str, list[dict]] = {}
        self.by_claim: dict[str, list[dict]] = {}
        self.by_source: dict[str, list[dict]] = {}
        self.counts: dict[str, int] = {}
        self.direct_parameter_ids: set[str] = set()
        self.families_missing: list[str] = []

    def parameter(self, node_type: str, location: str, parameter_id: str,
                  ids: dict | None = None, *, wired: bool = False) -> None:
        payload = dict(ids or {})
        payload["parameter_id"] = parameter_id
        self._record("parameter", parameter_id,
                     _cite(node_type, location, payload))
        if wired:
            self.direct_parameter_ids.add(parameter_id)

    def claim(self, node_type: str, location: str, claim_id: str,
              ids: dict | None = None) -> None:
        payload = dict(ids or {})
        payload["claim_id"] = claim_id
        self._record("claim", claim_id, _cite(node_type, location, payload))

    def source(self, node_type: str, location: str, source_id: str,
               ids: dict | None = None) -> None:
        payload = dict(ids or {})
        payload["source_id"] = source_id
        self._record("source", source_id, _cite(node_type, location, payload))

    def _record(self, family: str, key: str, citation: dict) -> None:
        index = getattr(self, f"by_{family}")
        existing = index.setdefault(key, [])
        if citation not in existing:
            existing.append(citation)
            self.counts[citation["node_type"]] = self.counts.get(
                citation["node_type"], 0) + 1


def _build_node_index(forecast: dict, doc: dict,
                      diagnostics: list[dict]) -> tuple[_NodeIndex, list[tuple]]:
    index = _NodeIndex()
    period_checks: list[tuple[str, str | None, str]] = []
    years = [str(year) for year in (forecast.get("forecast_years") or [])]

    def family(name: str, present: bool) -> None:
        if not present:
            index.families_missing.append(name)
            _diag(diagnostics, f"node_family_missing:{name}",
                  f"final artifact carries no {name} family", severity="info")

    segments = forecast.get("segments") or []
    segment_names = {s.get("name") for s in segments}
    for position, segment in enumerate(segments):
        name = segment.get("name")
        base_id = segment.get("base_revenue_parameter_id")
        if base_id:
            index.parameter("segment_base_revenue",
                            f"segments[{position}].base_revenue_parameter_id",
                            base_id, {"segment": name}, wired=True)
        recognition = segment.get("recognition") or {}
        for slot, claim_id in enumerate(recognition.get("basis_claim_ids") or []):
            index.claim("recognition_policy_basis",
                        f"segments[{position}].recognition.basis_claim_ids[{slot}]",
                        claim_id, {"segment": name})
        for source_id in recognition.get("basis_source_ids") or []:
            index.source("recognition_policy_basis",
                         f"segments[{position}].recognition.basis_source_ids",
                         source_id, {"segment": name})
        for scenario, config in (recognition.get("progress_parameter_ids") or {}).items():
            for slot, parameter_id in enumerate(config or []):
                index.parameter(
                    "recognition_progress_parameter",
                    f"segments[{position}].recognition.progress_parameter_ids"
                    f".{scenario}[{slot}]",
                    parameter_id, {"segment": name, "scenario": scenario},
                    wired=True)
        for scenario, config in (recognition.get("carry_in_parameter_ids") or {}).items():
            for slot, parameter_id in enumerate(config or []):
                index.parameter(
                    "recognition_carry_in_parameter",
                    f"segments[{position}].recognition.carry_in_parameter_ids"
                    f".{scenario}[{slot}]",
                    parameter_id, {"segment": name, "scenario": scenario},
                    wired=True)
        for scenario, config in (segment.get("scenarios") or {}).items():
            drivers = config.get("driver_parameter_ids") or {}
            for driver, parameter_ids in drivers.items():
                for slot, parameter_id in enumerate(parameter_ids or []):
                    year = years[slot] if slot < len(years) else None
                    location = (f"segments[{position}].scenarios.{scenario}"
                                f".driver_parameter_ids.{driver}[{slot}]")
                    index.parameter("segment_scenario_driver", location,
                                    parameter_id,
                                    {"segment": name, "scenario": scenario,
                                     "driver": driver, "year": year},
                                    wired=True)
                    period_checks.append((parameter_id, year, location))

    tree = forecast.get("growth_driver_analysis")
    family("growth_driver_analysis", tree is not None)
    for position, driver in enumerate((tree or {}).get("drivers") or []):
        driver_id = driver.get("driver_id")
        for attribution in driver.get("segment_attribution") or []:
            if attribution.get("segment_name") not in segment_names:
                _diag(diagnostics, "unknown_segment_attribution",
                      f"driver={driver_id} cites unmodeled segment "
                      f"{attribution.get('segment_name')}")
        for slot, parameter_id in enumerate(driver.get("parameter_ids") or []):
            index.parameter("driver_tree_parameter",
                            f"growth_driver_analysis.drivers[{position}]"
                            f".parameter_ids[{slot}]",
                            parameter_id, {"driver_id": driver_id})
        for slot, evidence in enumerate(driver.get("evidence_nodes") or []):
            evidence_id = evidence.get("evidence_id")
            for entry, claim_id in enumerate(evidence.get("claim_ids") or []):
                index.claim("driver_tree_evidence_node",
                            f"growth_driver_analysis.drivers[{position}]"
                            f".evidence_nodes[{slot}].claim_ids[{entry}]",
                            claim_id,
                            {"driver_id": driver_id, "evidence_id": evidence_id})
            for entry, source_id in enumerate(evidence.get("source_ids") or []):
                index.source("driver_tree_evidence_node",
                             f"growth_driver_analysis.drivers[{position}]"
                             f".evidence_nodes[{slot}].source_ids[{entry}]",
                             source_id,
                             {"driver_id": driver_id, "evidence_id": evidence_id})
        for entry, source_id in enumerate(driver.get("evidence_source_ids") or []):
            index.source("driver_tree_evidence_sources",
                         f"growth_driver_analysis.drivers[{position}]"
                         f".evidence_source_ids[{entry}]",
                         source_id, {"driver_id": driver_id})

    coverage = forecast.get("research_coverage")
    family("research_coverage", coverage is not None)
    for position, dimension in enumerate((coverage or {}).get("dimensions") or []):
        ids = {"dimension": dimension.get("dimension")}
        for slot, parameter_id in enumerate(dimension.get("parameter_ids") or []):
            index.parameter("coverage_dimension_parameter",
                            f"research_coverage.dimensions[{position}]"
                            f".parameter_ids[{slot}]", parameter_id, ids)
        for slot, source_id in enumerate(dimension.get("source_ids") or []):
            index.source("coverage_dimension_source",
                         f"research_coverage.dimensions[{position}]"
                         f".source_ids[{slot}]", source_id, ids)

    targets = forecast.get("management_target_coverage")
    family("management_target_coverage", targets is not None)
    currency = forecast.get("currency")
    for position, target in enumerate((targets or {}).get("targets") or []):
        target_id = target.get("target_id")
        raw = target.get("raw_currency")
        if currency and raw and raw != currency:
            _diag(diagnostics, "target_currency_mismatch",
                  f"target={target_id} raw_currency={raw} document={currency}")
        for slot, source_id in enumerate(target.get("source_ids") or []):
            index.source("management_target_source",
                         f"management_target_coverage.targets[{position}]"
                         f".source_ids[{slot}]", source_id, {"target_id": target_id})
        for key, node_type in (("claim_ids", "management_target_claim"),
                               ("benchmark_claim_ids", "management_target_claim"),
                               ("mapped_parameter_ids", "management_target_parameter")):
            for slot, entry in enumerate(target.get(key) or []):
                if node_type == "management_target_parameter":
                    index.parameter(node_type,
                                    f"management_target_coverage.targets[{position}]"
                                    f".{key}[{slot}]", entry,
                                    {"target_id": target_id})
                else:
                    index.claim(node_type,
                                f"management_target_coverage.targets[{position}]"
                                f".{key}[{slot}]", entry, {"target_id": target_id})
    for position, comm in enumerate((targets or {}).get("communications") or []):
        for slot, source_id in enumerate(comm.get("source_ids") or []):
            index.source("management_communication_source",
                         f"management_target_coverage.communications[{position}]"
                         f".source_ids[{slot}]", source_id,
                         {"category": comm.get("category")})

    consolidated = forecast.get("consolidated_forecast") or {}
    for scenario, block in consolidated.items():
        for position, adjustment in enumerate(block.get("adjustment_bridge") or []):
            for slot, parameter_id in enumerate(adjustment.get("parameter_ids") or []):
                index.parameter("adjustment_parameter",
                                f"consolidated_forecast.{scenario}"
                                f".adjustment_bridge[{position}].parameter_ids[{slot}]",
                                parameter_id,
                                {"scenario": scenario,
                                 "adjustment": adjustment.get("name")},
                                wired=True)

    weighted = forecast.get("probability_weighted_forecast")
    family("probability_weighted_forecast", weighted is not None)
    if weighted:
        for slot, source_id in enumerate(weighted.get("probability_source_ids") or []):
            index.source("scenario_probability_source",
                         "probability_weighted_forecast.probability_source_ids"
                         f"[{slot}]", source_id)
    probabilities = forecast.get("scenario_probabilities") or doc.get(
        "scenario_probabilities") or {}
    for slot, claim_id in enumerate(probabilities.get("probability_claim_ids") or []):
        index.claim("scenario_probability",
                    "scenario_probabilities.probability_claim_ids"
                    f"[{slot}] -> probability_weighted_forecast", claim_id)

    for position, record in enumerate(doc.get("historical_revenue") or []):
        basis = record.get("revenue_basis") or {}
        for key, entries in (("source_ids", None), ("claim_ids", None)):
            for slot, entry in enumerate(basis.get(key) or []):
                location = f"historical_revenue[{position}].revenue_basis.{key}[{slot}]"
                if key == "source_ids":
                    index.source("historical_revenue_basis", location, entry)
                else:
                    index.claim("historical_revenue_basis", location, entry)
        for slot, component in enumerate(basis.get("components") or []):
            for key in ("source_ids", "claim_ids"):
                for entry, value in enumerate(component.get(key) or []):
                    location = (f"historical_revenue[{position}].revenue_basis"
                                f".components[{slot}].{key}[{entry}]")
                    if key == "source_ids":
                        index.source("historical_revenue_basis", location, value)
                    else:
                        index.claim("historical_revenue_basis", location, value)

    total_id = doc.get("reported_total_revenue_parameter_id")
    if total_id:
        index.parameter("company_total_parameter",
                        "input_document.reported_total_revenue_parameter_id",
                        total_id, wired=True)
    for slot, parameter_id in enumerate(doc.get("base_adjustment_parameter_ids") or []):
        index.parameter("opening_base_adjustment",
                        f"input_document.base_adjustment_parameter_ids[{slot}]",
                        parameter_id, wired=True)
    for position, constraint in enumerate(doc.get("revenue_constraints") or []):
        constraint_id = constraint.get("constraint_id")
        kind = constraint.get("type")
        # Mirror the engine's _constraint_uses shape per constraint type: the
        # same key carries different nestings across types, so flatten only
        # what that type actually means.
        mappings: list[Any] = []
        if kind == "sum_cap":
            for segment in constraint.get("segments") or []:
                mappings.append(constraint.get("scenario_parameter_ids") or {})
                if constraint.get("allocation") == "fixed_weights":
                    mappings.append(
                        (constraint.get("weight_parameter_ids") or {}).get(segment)
                        or {})
        elif kind == "linked_ratio":
            mappings.append(constraint.get("scenario_parameter_ids") or {})
        elif kind == "elimination":
            mappings.extend(
                (constraint.get("segment_adjustment_parameter_ids") or {}).values())
        for mapping in mappings:
            if not isinstance(mapping, dict):
                continue
            for scenario, ids in mapping.items():
                for slot, parameter_id in enumerate(ids or []):
                    index.parameter("revenue_constraint_parameter",
                                    f"input_document.revenue_constraints[{position}]",
                                    parameter_id,
                                    {"constraint_id": constraint_id,
                                     "constraint_type": kind,
                                     "scenario": scenario},
                                    wired=True)
    return index, period_checks


def _wired_parameters(doc: dict, direct: set[str]) -> set[str]:
    """Upstream closure: formula inputs of any computation-reachable parameter.

    Linear worklist over the declared dependency graph; each parameter is
    visited once, so large inputs stay proportional to their size instead of
    rescanning the document per parameter.
    """
    parameters = doc.get("parameters") or doc.get("parameter_trace") or []
    formula_inputs: dict[str, list[str]] = {}
    for parameter in parameters:
        inputs = parameter.get("input_parameter_ids") or []
        if inputs:
            formula_inputs[parameter["parameter_id"]] = list(inputs)
    wired = set(direct)
    work = list(direct)
    while work:
        current = work.pop()
        for upstream in formula_inputs.get(current, ()):
            if upstream not in wired:
                wired.add(upstream)
                work.append(upstream)
    return wired


# ---------------------------------------------------------------------------
# consumption receipts
# ---------------------------------------------------------------------------

def _normalise_refs(refs: Any) -> list[tuple]:
    if not isinstance(refs, list):
        return []
    return sorted(tuple(sorted(item.items())) for item in refs
                  if isinstance(item, dict))


class _DependencyState:
    __slots__ = ("intact", "reasons", "parameter_id", "claim_id", "receipt_index")

    def __init__(self, intact: bool, reasons: list[str],
                 parameter_id: str | None, claim_id: str | None,
                 receipt_index: int = -1) -> None:
        self.intact = intact
        self.reasons = reasons
        self.parameter_id = parameter_id
        self.claim_id = claim_id
        self.receipt_index = receipt_index


def _evaluate_dependency(receipt_index: int, dep: dict, span: dict | None,
                         parent_sha: str | None, doc: dict,
                         claims: dict[str, dict],
                         parameters: dict[str, dict],
                         sources_by_sha: dict[str, list[str]],
                         diagnostics: list[dict]) -> _DependencyState:
    """Resolve one dependency as ONE chain: canonical parent capture ->
    RF local source -> transported span -> claim -> parameter -> run graph.

    Every edge that carries provided material is checked against the actual
    known counterpart (span, capture mapping, claim target); broken edges are
    named and make the dependency unverifiable. A missing hash stays a
    lenient unknown: the chain then rides on the transported span's own
    canonical parent hash, never on the unverified claim.
    """
    span_id = dep.get("span_id") or "<missing>"
    for field in ("span_id", "claim_id", "parameter_id"):
        if not dep.get(field):
            _diag(diagnostics, "consumption_material_missing",
                  f"receipt[{receipt_index}] dependency lacks {field}",
                  item_id=span_id)
            return _DependencyState(False, ["consumption_material_missing"],
                                    None, None, receipt_index)
    claim_id = dep.get("claim_id")
    parameter_id = dep.get("parameter_id")
    reasons: list[str] = []

    # -- transported material + canonical parent -----------------------------
    if span is None:
        _diag(diagnostics, "span_material_not_provided",
              f"span {span_id} is bound by receipt[{receipt_index}] but no "
              "narrative context transports it", severity="info",
              item_id=span_id)
        reasons.append("span_material_not_provided")
    else:
        if dep.get("source_id") and dep["source_id"] != span.get("source_id"):
            _diag(diagnostics, "receipt_source_mismatch",
                  f"receipt[{receipt_index}] names source "
                  f"{dep['source_id']!r} but the transported span belongs to "
                  f"{span.get('source_id')!r}", item_id=span_id)
            reasons.append("receipt_source_mismatch")
        if dep.get("locator") and dep["locator"] != span.get("locator"):
            _diag(diagnostics, "receipt_locator_mismatch",
                  f"receipt[{receipt_index}] locator disagrees with the "
                  "transported span", item_id=span_id)
            reasons.append("receipt_locator_mismatch")
        for field in ("parser_name", "parser_version"):
            if dep.get(field) and dep[field] != span.get(field):
                _diag(diagnostics, "receipt_parser_mismatch",
                      f"receipt[{receipt_index}] {field} disagrees with the "
                      "transported span", item_id=span_id)
                reasons.append("receipt_parser_mismatch")
    local_source = None
    if parent_sha is not None:
        matches = sources_by_sha.get(parent_sha, [])
        if not matches:
            _diag(diagnostics, "consumption_source_hash_mismatch",
                  f"span {span_id}'s canonical parent {parent_sha[:16]}… is "
                  "captured by no source of this input", item_id=span_id)
            reasons.append("consumption_source_hash_mismatch")
        elif len(matches) > 1:
            _diag(diagnostics, "consumption_source_ambiguous",
                  f"span {span_id}'s canonical parent matches several "
                  f"sources {sorted(matches)}", item_id=span_id)
            reasons.append("consumption_source_ambiguous")
        else:
            local_source = matches[0]
    provided_sha = dep.get("source_sha256")
    if provided_sha is None:
        _diag(diagnostics, "hash_missing_unknown",
              f"receipt[{receipt_index}] dependency carries no source hash; "
              "lenient policy: recorded unknown, chain judged from the "
              "transported span's canonical parent", severity="info",
              item_id=span_id)
    elif parent_sha is not None and provided_sha != parent_sha:
        _diag(diagnostics, "receipt_span_hash_mismatch",
              f"receipt[{receipt_index}] source_sha256 {provided_sha[:16]}… "
              "is not the transported span's canonical parent hash",
              item_id=span_id)
        reasons.append("receipt_span_hash_mismatch")

    # -- claim edges ----------------------------------------------------------
    claim = claims.get(claim_id)
    if claim is None:
        _diag(diagnostics, "receipt_claim_not_in_input",
              f"receipt[{receipt_index}] cites claim {claim_id} absent from "
              "this input (display keys never join across runs)", item_id=span_id)
        reasons.append("receipt_claim_not_in_input")
    else:
        if local_source is not None and claim.get("source_id") != local_source:
            _diag(diagnostics, "receipt_claim_source_mismatch",
                  f"receipt[{receipt_index}] claim {claim_id} belongs to "
                  f"{claim.get('source_id')!r}, not the span's captured "
                  f"source {local_source!r}", item_id=span_id)
            reasons.append("receipt_claim_source_mismatch")
        if (claim.get("content_sha256") and parent_sha is not None
                and claim["content_sha256"] != parent_sha):
            _diag(diagnostics, "receipt_claim_material_mismatch",
                  f"receipt[{receipt_index}] claim {claim_id} carries "
                  "material from another capture than the span's parent",
                  item_id=span_id)
            reasons.append("receipt_claim_material_mismatch")
        if (claim.get("target_type") == "parameter"
                and claim.get("target_id") != parameter_id):
            _diag(diagnostics, "receipt_claim_target_mismatch",
                  f"receipt[{receipt_index}] claim {claim_id} targets "
                  f"{claim.get('target_id')!r}, not the bound parameter "
                  f"{parameter_id!r}", item_id=span_id)
            reasons.append("receipt_claim_target_mismatch")
        if span is not None:
            # The consumption adapter creates exactly one new claim per
            # binding with excerpt = the bound span's raw_text and locator =
            # its locator (the projected source_locator for /3 spans), so a
            # receipt-cited claim's own material identity must be this
            # span's material. Contradictions (e.g. a receipt from a
            # sibling run that selected different material of the same
            # capture) are named; missing optional fields stay unknown.
            structured = span.get("structured_value") or {}
            projected = "source_locator" in structured
            expected_locator = (
                structured.get("source_locator") if projected
                else span.get("locator"))
            span_text = span.get("raw_text")
            material_fields_missing = False
            claim_locator = claim.get("locator")
            if claim_locator is not None and expected_locator is not None:
                if claim_locator != expected_locator:
                    _diag(diagnostics, "receipt_claim_material_mismatch",
                          f"receipt[{receipt_index}] claim {claim_id} locator "
                          "points at other material than the transported "
                          "span", item_id=span_id)
                    reasons.append("receipt_claim_material_mismatch")
            elif claim_locator is None or expected_locator is None:
                material_fields_missing = True
            excerpt_sha = claim.get("excerpt_sha256")
            if excerpt_sha is not None and span_text is not None:
                if excerpt_sha != text_sha256(span_text):
                    _diag(diagnostics, "receipt_claim_material_mismatch",
                          f"receipt[{receipt_index}] claim {claim_id} "
                          "excerpt hash is not the transported span's text",
                          item_id=span_id)
                    reasons.append("receipt_claim_material_mismatch")
            elif excerpt_sha is None:
                material_fields_missing = True
            if material_fields_missing:
                _diag(diagnostics, "material_field_missing_unknown",
                      f"receipt[{receipt_index}] claim {claim_id} lacks "
                      "locator/excerpt hash; material identity stays "
                      "unknown (lenient policy)", severity="info",
                      item_id=span_id)
    if parameter_id not in parameters:
        _diag(diagnostics, "receipt_parameter_not_in_input",
              f"receipt[{receipt_index}] cites parameter {parameter_id} "
              "absent from this input", item_id=span_id)
        reasons.append("receipt_parameter_not_in_input")
    if parameter_id in parameters:
        if dep.get("formula_refs") is None:
            _diag(diagnostics, "receipt_formula_refs_missing",
                  f"receipt[{receipt_index}] dependency carries no "
                  "formula_refs; run binding is judged without it",
                  severity="info", item_id=span_id)
        else:
            expected = parameter_formula_refs(doc, parameter_id, parameters)
            if _normalise_refs(dep.get("formula_refs")) != _normalise_refs(expected):
                _diag(diagnostics, "receipt_run_mismatch",
                      f"receipt[{receipt_index}] formula_refs for {parameter_id} "
                      "disagree with this input's dependency graph "
                      "(different run?)", item_id=span_id)
                reasons.append("receipt_run_mismatch")
    intact = not reasons
    return _DependencyState(intact, reasons or ["dependency_intact"],
                            parameter_id, claim_id, receipt_index)


def _iter_dependencies(receipt: dict, receipt_index: int,
                       diagnostics: list[dict]) -> list[dict]:
    if receipt.get("schema_version") not in CONSUMPTION_SCHEMAS:
        _diag(diagnostics, "consumption_schema_unknown",
              f"receipt[{receipt_index}] schema "
              f"{receipt.get('schema_version')!r} is not a known consumption "
              "receipt; its dependencies stay unverifiable")
        return []
    unknown = sorted(set(receipt) - KNOWN_CONSUMPTION_FIELDS)
    if unknown:
        _diag(diagnostics, "unknown_fields_ignored",
              f"receipt[{receipt_index}] carries unknown fields {unknown}; "
              "they are never interpreted", severity="info")
    if receipt.get("status") == "not_consumed":
        _diag(diagnostics, "consumption_not_consumed",
              f"receipt[{receipt_index}] records status not_consumed",
              severity="info")
    dependencies = receipt.get("dependencies")
    if not isinstance(dependencies, list):
        _diag(diagnostics, "consumption_material_missing",
              f"receipt[{receipt_index}] carries no dependencies list")
        return []
    for dep in dependencies:
        if isinstance(dep, dict):
            unknown = sorted(set(dep) - KNOWN_DEPENDENCY_FIELDS)
            if unknown:
                _diag(diagnostics, "unknown_fields_ignored",
                      f"receipt[{receipt_index}] dependency carries unknown "
                      f"fields {unknown}; they are never interpreted",
                      severity="info")
    return dependencies


# ---------------------------------------------------------------------------
# narrative side
# ---------------------------------------------------------------------------

def _span_support_use(reading: dict, span_id: str) -> str | None:
    """Aggregate the source-owned support capability across published views.

    The reader's contract: only a view the source marks ``support`` (or a
    pre-/4 structural support partition) grants fact-support capability;
    views marked ``context_only`` / ``unresolved`` are refused for support
    and a /4 span outside every group has no implicit capability. A span
    supported by any capable view aggregates to support; otherwise an
    explicit context_only / unresolved marking wins; /1 bundles without
    citation views return None (unknown partition).
    """
    saw_support = False
    saw_unresolved = False
    saw_context_marked = False
    saw_structural_context = False
    grouped = False
    for group in (reading or {}).get("groups") or []:
        if span_id not in (group.get("evidence_ids") or []):
            continue
        grouped = True
        views = group.get("citation_views") or []
        if not views:
            return None
        in_context_partition = False
        for view in views:
            support = view.get("support_evidence_ids") or []
            use = view.get("reading_support_use")
            if span_id in support:
                if use == "support" or use is None:
                    saw_support = True
                elif use == "unresolved":
                    saw_unresolved = True
                else:
                    saw_context_marked = True
            if span_id in (view.get("context_evidence_ids") or []):
                in_context_partition = True
        if in_context_partition and not saw_support:
            saw_structural_context = True
    if not grouped:
        if (reading or {}).get("schema_version") == "du-production-reading/4":
            return "unresolved"
        return None
    if saw_support:
        return "support"
    if saw_unresolved:
        return "unresolved"
    if saw_context_marked or saw_structural_context:
        return "context_only"
    return None


def _has_any_views(reading: dict) -> bool:
    return any(group.get("citation_views")
               for group in (reading or {}).get("groups") or [])


# ---------------------------------------------------------------------------
# item assembly
# ---------------------------------------------------------------------------

def _citations_with_reasons(citations: list[dict]) -> tuple[list[dict], list[str]]:
    reasons = []
    seen: set[str] = set()
    for citation in citations:
        reason = _USED_REASON.get(citation["node_type"])
        if reason and reason not in seen:
            seen.add(reason)
            reasons.append(reason)
    return citations, reasons


def _bound_citations(state: "_DependencyState",
                     claim_status: dict[str, dict], index: "_NodeIndex",
                     wired: set[str], direct: set[str]) -> list[dict]:
    """Citation chain of one intact binding: its claim's nodes plus the
    bound parameter's own nodes (and the derived-input hop)."""
    cited: list[dict] = []
    if state.claim_id and state.claim_id in claim_status:
        for citation in claim_status[state.claim_id].get("cited_by", []):
            if citation not in cited:
                cited.append(citation)
    if state.parameter_id:
        for citation in index.by_parameter.get(state.parameter_id, []):
            if citation not in cited:
                cited.append(citation)
        if state.parameter_id in wired and state.parameter_id not in direct:
            cited.append(_cite(
                "derived_parameter_input",
                f"input_document.parameters[{state.parameter_id}]",
                {"parameter_id": state.parameter_id}))
    return cited


class _Items:
    def __init__(self, max_items: int) -> None:
        self.max_items = max_items
        self.entries: list[dict] = []

    def add(self, kind: str, item_id: str, **fields) -> dict:
        if len(self.entries) >= self.max_items:
            raise AdoptionAuditError(
                "resource_limit",
                f"items exceed max_items={self.max_items}; raise --max-items "
                "or audit a smaller artifact")
        item = {"kind": kind, "id": item_id}
        item.update(fields)
        self.entries.append(item)
        return item


def build_adoption_report(
    forecast: dict,
    *,
    consumption_receipts: Sequence[dict] = (),
    narrative_contexts: Sequence[dict] = (),
    narrative_refusals: Sequence[dict] = (),
    input_file_document: dict | None = None,
    snapshot: dict | None = None,
    max_items: int = 20000,
) -> dict:
    """Observe the citation chain of one final forecast artifact.

    All inputs are explicit parsed artifacts; nothing is scanned, fetched or
    recomputed. Deterministic: the same inputs yield byte-identical reports.
    """
    diagnostics: list[dict] = []
    doc = forecast.get("input_document") or forecast
    if "input_document" not in forecast:
        _diag(diagnostics, "embedded_input_absent",
              "artifact embeds no input_document; input-side tables are read "
              "from the top level", severity="info")
    elif forecast.get("input_sha256") and \
            canonical_sha256(forecast["input_document"]) != forecast["input_sha256"]:
        _diag(diagnostics, "input_document_binding_mismatch",
              "embedded input_document does not hash to the declared "
              "input_sha256")
    for key in sorted(set(forecast) - KNOWN_FORECAST_FIELDS):
        _diag(diagnostics, f"unknown_field_ignored:{key}",
              "unknown forecast field is never interpreted", severity="info")

    claims = {claim["claim_id"]: claim
              for claim in (doc.get("evidence_claims")
                            or forecast.get("evidence_claims") or [])
              if isinstance(claim, dict) and claim.get("claim_id")}
    parameters_list = doc.get("parameters") or forecast.get("parameter_trace") or []
    parameters = {entry["parameter_id"]: entry for entry in parameters_list
                  if isinstance(entry, dict) and entry.get("parameter_id")}
    sources = doc.get("sources") or forecast.get("sources") or []
    sources_by_id: dict[str, dict] = {}
    sources_by_sha: dict[str, list[str]] = {}
    for source in sources:
        if not isinstance(source, dict) or not source.get("source_id"):
            continue
        sources_by_id[source["source_id"]] = source
        sha = (source.get("capture") or {}).get("snapshot_sha256")
        if sha:
            sources_by_sha.setdefault(sha, []).append(source["source_id"])
    for sha, owners in sorted(sources_by_sha.items()):
        if len(owners) > 1:
            _diag(diagnostics, "duplicate_capture_sha",
                  f"capture sha {sha[:16]}… is declared by several sources "
                  f"{sorted(owners)} (multi-version material)")

    index, period_checks = _build_node_index(forecast, doc, diagnostics)
    wired = _wired_parameters(doc, index.direct_parameter_ids)
    for parameter_id, slot_year, location in period_checks:
        parameter = parameters.get(parameter_id)
        if parameter and slot_year:
            period = parameter.get("period") or ""
            if period.startswith("FY") and period[2:] != slot_year:
                _diag(diagnostics, "period_mismatch_at_node",
                      f"parameter={parameter_id} period={period} sits in the "
                      f"{slot_year} slot at {location}")

    items = _Items(max_items)

    # -- claim items (input document namespace) -----------------------------
    params_by_claim: dict[str, list[str]] = {}
    for parameter_id, parameter in parameters.items():
        for claim_id in parameter.get("claim_ids") or []:
            params_by_claim.setdefault(claim_id, []).append(parameter_id)
    for claim_id, claim in claims.items():
        target = claim.get("target_id")
        if claim.get("target_type") == "parameter" and target in parameters:
            params_by_claim.setdefault(claim_id, [])
            if target not in params_by_claim[claim_id]:
                params_by_claim[claim_id].append(target)
    claim_status: dict[str, dict] = {}
    for claim_id in claims:
        cited = list(index.by_claim.get(claim_id, []))
        for parameter_id in params_by_claim.get(claim_id, ()):
            for citation in index.by_parameter.get(parameter_id, []):
                if citation not in cited:
                    cited.append(citation)
            if parameter_id in wired and parameter_id not in index.direct_parameter_ids:
                cited.append(_cite("derived_parameter_input",
                                   f"input_document.parameters[{parameter_id}]",
                                   {"parameter_id": parameter_id}))
        cited, reasons = _citations_with_reasons(cited)
        if cited:
            status, extra = "used", []
        elif params_by_claim.get(claim_id):
            unwired = all(
                parameter_id not in wired
                and parameter_id not in index.direct_parameter_ids
                for parameter_id in params_by_claim[claim_id])
            if unwired:
                status = "not_used_when_provable"
                extra = ["parameter_not_wired_to_any_node"]
            else:
                status, extra = "not_observed", ["claim_not_cited_at_any_node"]
        else:
            status, extra = "not_observed", ["claim_not_cited_at_any_node"]
        claim_status[claim_id] = items.add(
            "claim", claim_id,
            id_scope="document_local_display_key",
            input_source_id=claim.get("source_id"),
            status=status,
            cited_by=cited,
            reasons=reasons + extra,
        )

    # -- consumption receipts ----------------------------------------------
    span_material: dict[str, tuple[dict, str | None]] = {}
    for context in narrative_contexts:
        parents = list(context.get("parent_source_refs") or [])
        primary = context.get("source_ref")
        if primary:
            parents.insert(0, primary)
        for span in context.get("evidence_spans") or []:
            if not (isinstance(span, dict) and span.get("span_id")):
                continue
            parent_sha = next(
                (ref.get("content_sha256") for ref in parents
                 if ref.get("source_id") == span.get("source_id")
                 and ref.get("content_sha256")),
                None)
            span_material[span["span_id"]] = (span, parent_sha)
    dep_states: dict[str, list[_DependencyState]] = {}
    for receipt_index, receipt in enumerate(consumption_receipts):
        if not isinstance(receipt, dict):
            _diag(diagnostics, "consumption_material_missing",
                  f"receipt[{receipt_index}] is not an object")
            continue
        for dep in _iter_dependencies(receipt, receipt_index, diagnostics):
            if not isinstance(dep, dict) or not dep.get("span_id"):
                continue
            span, parent_sha = span_material.get(dep["span_id"], (None, None))
            state = _evaluate_dependency(
                receipt_index, dep, span, parent_sha, doc, claims, parameters,
                sources_by_sha, diagnostics)
            dep_states.setdefault(dep["span_id"], []).append(state)

    # -- span items ----------------------------------------------------------
    span_status: dict[str, dict] = {}
    for context in narrative_contexts:
        reading = context.get("reading_context") or {}
        if reading and not _has_any_views(reading):
            _diag(diagnostics, "old_reading_schema_no_support_partition",
                  f"reading {reading.get('schema_version')!r} publishes no "
                  "citation views; span support partition stays unknown",
                  severity="info")
        summary_claims = ((context.get("summary") or {}).get("draft")
                          or {}).get("claims") or []
        summary_ids = {entry.get("claim_id") for entry in summary_claims}
        for claim_id in sorted(summary_ids & set(claims)):
            _diag(diagnostics, "display_key_collision_not_joined",
                  f"summary claim text {claim_id!r} equals an input claim id; "
                  "display keys never join across documents", severity="info")
        for span in context.get("evidence_spans") or []:
            span_id = span.get("span_id")
            if not span_id:
                continue
            support_use = _span_support_use(reading, span_id)
            states = dep_states.get(span_id, [])
            if support_use in ("context_only", "unresolved"):
                # The source partition bars this span from support regardless
                # of any receipt: the binding is flagged, never obeyed.
                if states:
                    _diag(diagnostics, "context_span_bound_as_support",
                          f"a receipt binds span {span_id} the source marks "
                          f"{support_use}; the binding is flagged, not obeyed",
                          item_id=span_id)
                status = "not_used_when_provable"
                extra = (["context_partition_cannot_support"]
                         if support_use == "context_only"
                         else ["unresolved_support_cannot_support"])
                cited: list[dict] = []
                reasons = list(extra)
            elif not states:
                status, extra = "not_observed", ["span_not_bound_in_consumption"]
                cited = []
                reasons = list(extra)
            else:
                # Aggregate every dependency path of this canonical span:
                # valid paths union their citations, invalid paths keep their
                # own named diagnostics without hiding valid uses.
                intact_states = [entry for entry in states if entry.intact]
                invalid_states = [entry for entry in states if not entry.intact]
                receipt_count = len({entry.receipt_index for entry in states})
                _diag(diagnostics, "span_dependencies_aggregated",
                      f"span {span_id} aggregates {len(states)} dependency "
                      f"path(s) across {receipt_count} receipt(s): "
                      f"{len(intact_states)} intact, "
                      f"{len(invalid_states)} invalid", severity="info",
                      item_id=span_id)
                cited = []
                for state in intact_states:
                    for citation in _bound_citations(
                            state, claim_status, index, wired,
                            index.direct_parameter_ids):
                        if citation not in cited:
                            cited.append(citation)
                cited.sort(key=_citation_order)
                cited, node_reasons = _citations_with_reasons(cited)
                if cited:
                    status = "used"
                    reasons = ["used_via_bound_claim"] + node_reasons
                elif intact_states and all(
                        state.parameter_id
                        and state.parameter_id not in wired
                        and state.parameter_id not in index.direct_parameter_ids
                        for state in intact_states):
                    status = "not_used_when_provable"
                    reasons = ["parameter_not_wired_to_any_node"]
                elif intact_states:
                    status = "not_observed"
                    reasons = ["bound_but_not_cited_at_any_node"]
                else:
                    status = "unverifiable"
                    reasons = sorted({reason for state in invalid_states
                                      for reason in state.reasons
                                      if reason != "dependency_intact"})
            span_status[span_id] = items.add(
                "span", span_id,
                id_scope="canonical",
                source_sha256=span_material.get(span_id, ({}, None))[1],
                status=status,
                support_use=support_use,
                cited_by=cited,
                reasons=reasons,
            )

        # -- summary claim items --------------------------------------------
        for entry in summary_claims:
            claim_id = entry.get("claim_id") or "<missing>"
            span_ids = entry.get("evidence_ids") or []
            states = [state for span_id in span_ids
                      for state in dep_states.get(span_id, [])]
            span_items = [span_status[span_id] for span_id in span_ids
                          if span_id in span_status]
            statuses = [item["status"] for item in span_items]
            if "used" in statuses:
                status = "used"
                extra = ["used_via_bound_span"]
            elif "unverifiable" in statuses or (
                    states and not any(state.intact for state in states)):
                status = "unverifiable"
                extra = ["binding_material_invalid"]
            elif statuses and all(
                    value == "not_used_when_provable" for value in statuses):
                status = "not_used_when_provable"
                extra = ["summary_spans_structurally_unused"]
            else:
                status = "not_observed"
                extra = ["summary_claim_spans_not_bound"]
            items.add(
                "summary_claim", claim_id,
                id_scope="document_local_display_key",
                status=status,
                cited_by=[citation for item in span_items
                          for citation in item["cited_by"]],
                reasons=extra,
            )

    # -- spans a receipt cites without transported material ------------------
    for span_id in sorted(dep_states):
        if span_id in span_status:
            continue
        states = dep_states[span_id]
        status = "unverifiable"
        reasons = sorted({reason for state in states
                          for reason in state.reasons
                          if reason != "dependency_intact"})
        span_status[span_id] = items.add(
            "span", span_id,
            id_scope="canonical",
            status=status,
            support_use=None,
            cited_by=[],
            reasons=reasons,
        )

    # -- source items --------------------------------------------------------
    claims_by_source: dict[str, list[str]] = {}
    for claim_id, claim in claims.items():
        claims_by_source.setdefault(claim.get("source_id"), []).append(claim_id)
    for source_id in sorted(sources_by_id):
        cited = list(index.by_source.get(source_id, []))
        own_claims = claims_by_source.get(source_id, [])
        used_claims = [claim_id for claim_id in own_claims
                       if claim_status[claim_id]["status"] == "used"]
        if cited or used_claims:
            status = "used"
            reasons = (["used_directly"] if cited else []) + (
                ["used_via_claims"] if used_claims else [])
        elif own_claims and all(
                claim_status[claim_id]["status"] == "not_used_when_provable"
                for claim_id in own_claims):
            status = "not_used_when_provable"
            reasons = ["all_claims_attach_to_unwired_parameters"]
        else:
            status = "not_observed"
            reasons = ["source_without_observed_citation"]
        items.add(
            "source", source_id,
            id_scope="document_local_display_key",
            source_sha256=(sources_by_id[source_id].get("capture") or {}).get(
                "snapshot_sha256"),
            status=status,
            cited_by=cited,
            reasons=reasons,
        )

    # -- cross checks ---------------------------------------------------------
    cross: dict[str, Any] = {
        "input_match": None,
        "snapshot_match": None,
        "consumption_receipts": len(consumption_receipts),
        "narrative_contexts": len(narrative_contexts),
    }
    if input_file_document is not None and forecast.get("input_sha256"):
        cross["input_match"] = (
            canonical_sha256(input_file_document) == forecast["input_sha256"])
        if not cross["input_match"]:
            _diag(diagnostics, "input_forecast_binding_mismatch",
                  "--input document does not hash to the forecast's "
                  "input_sha256; items stay bound to the embedded copy")
    if snapshot is not None:
        identity = snapshot.get("identity") or snapshot
        stored = snapshot.get("forecast_result") or {}
        input_ok = (not forecast.get("input_sha256")
                    or identity.get("input_sha256") == forecast["input_sha256"])
        # The snapshot's identity hash covers the whole stored result (which
        # already carries its own result_sha256), so the artifact binds
        # through the stored result's declared hash, not the identity hash.
        result_ok = (stored.get("result_sha256") is not None
                     and forecast.get("result_sha256") is not None
                     and stored.get("result_sha256") == forecast["result_sha256"])
        cross["snapshot_match"] = bool(input_ok and result_ok)
        if not cross["snapshot_match"]:
            _diag(diagnostics, "snapshot_binding_mismatch",
                  "--snapshot identity does not bind to this forecast")
    for refusal in narrative_refusals:
        _diag(diagnostics, "narrative_wire_refused",
              f"status={refusal.get('status')} reason={refusal.get('reason')}; "
              "that narrative material stays unverifiable")

    # -- assembly --------------------------------------------------------------
    by_status = {status: 0 for status in _STATUS_ORDER}
    by_kind: dict[str, int] = {}
    for item in items.entries:
        by_status[item["status"]] = by_status.get(item["status"], 0) + 1
        by_kind[item["kind"]] = by_kind.get(item["kind"], 0) + 1
    return {
        "schema_version": REPORT_SCHEMA,
        "diagnostic_only_not_a_permission_gate": True,
        "observation_scope": "final_output_citation_chain_no_execution_trace",
        "forecast": {
            "company_name": forecast.get("company_name"),
            "as_of_date": forecast.get("as_of_date"),
            "engine_version": forecast.get("engine_version"),
            "schema_version": forecast.get("schema_version"),
            "input_sha256": forecast.get("input_sha256"),
            "result_sha256": forecast.get("result_sha256"),
        },
        "cross_checks": cross,
        "node_index": {
            "citations": dict(sorted(index.counts.items())),
            "wired_parameter_ids": sorted(wired),
            "families_missing": sorted(index.families_missing),
        },
        "items": items.entries,
        "counts": {"items": len(items.entries),
                   "by_status": by_status, "by_kind": by_kind},
        "diagnostics": diagnostics,
        "limitations": list(LIMITATIONS),
        "resource": {"max_items": max_items, "items": len(items.entries)},
    }
