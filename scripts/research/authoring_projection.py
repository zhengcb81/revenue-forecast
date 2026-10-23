"""Project reviewed explanation data onto the existing RF input vocabulary.

This is an authoring operation, not a truth classifier or forecast engine.
The caller supplies source-reviewed context and component baselines. Evidence
roles, actual target scopes and scenario cells determine where it may apply.
Claims, amounts, formulae, schema and calibration status are never changed.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, localcontext


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")
    return value.strip()


def _number(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be finite")
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


def _history_projection(document, contexts):
    claims = {row["claim_id"]: row for row in document.get("evidence_claims", [])}
    for driver in document.get("growth_driver_tree", {}).get("drivers", []):
        context = contexts.get(driver["driver_id"])
        if context is None:
            continue
        nodes = [node for node in driver["evidence_nodes"]
                 if node.get("inference_distance") != "contrary"]
        ids = [cid for node in nodes for cid in node["claim_ids"]]
        # Mixed or unclassified evidence cannot be erased by a history context.
        if not ids or not all(claims[cid].get("evidence_role") == "history_base" for cid in ids):
            continue
        historical = _text(context["historical_context"], "historical_context")
        condition = _text(context["forward_condition"], "forward_condition")
        scopes = ", ".join(row["segment_name"] for row in driver["segment_attribution"])
        explanation = (
            f"Historical context for {scopes}: {historical} "
            f"Forward path is an analyst condition: {condition} "
            "No disclosed forward mechanism is claimed."
        )
        driver.update(
            title=f"{scopes}: conditional baseline/perimeter bridge",
            thesis=explanation,
            causal_chain=["Source-reported historical/perimeter context",
                          "Explicit conditional estimate", "Recognized external revenue"],
            persistence_rationale=explanation,
            leading_indicators=list(context["leading_indicators"]),
            falsifiers=list(context["falsifiers"]),
        )
        for node in nodes:
            node.update(evidence_type="issuer_historical_context",
                        inference_distance="direct", conclusion=explanation)


def _scenario_explanations(document, bridges):
    parameters = {row["parameter_id"]: row for row in document.get("parameters", [])}
    for bridge in bridges:
        target = parameters[bridge["explanation_parameter_id"]]
        parent = parameters[bridge["parent_parameter_id"]]
        scenario, period = bridge["scenario"], bridge["period"]
        if target.get("scenario") != scenario or parent.get("scenario") not in (None, "all", scenario):
            raise ValueError("component explanation scenario does not match the native target")
        if target.get("period") != period or parent.get("period") != period:
            raise ValueError("component explanation period does not match the native target")
        unit = _text(bridge["unit"], "unit")
        if parent.get("unit") != unit:
            raise ValueError("component baseline unit differs from the native parent unit")
        with localcontext() as ctx:
            ctx.prec = 40
            amount = _number(parent["value"], "parent value")
            residual = _number(bridge["residual_amount"], "residual_amount")
            comparable = _number(bridge["prior_component_amount"], "prior_component_amount")
            component = amount - residual
            rate = (f"{(component / comparable - 1) * 100:.2f}%"
                    if comparable > 0 else "not defined (non-positive comparable component)")
        target["rationale"] = (
            f"{bridge.get('rationale_context', '').strip()} "
            f"For {scenario} ({bridge['period_label']}), selected parent parameter "
            f"'{bridge['parent_parameter_id']}' is "
            f"{amount:.2f} {unit}. Under the condition '{bridge['condition']}', "
            f"{bridge['component_name']} is {component:.2f} {unit} versus "
            f"{comparable:.2f} {unit} in the comparable period; implied change is {rate}. "
            "This is a conditional decomposition, not an observed rate or an empirical range. "
            "No future actual is supplied."
        ).strip()
        if bridge.get("basis"):
            target["rationale"] += " Basis: " + _text(bridge["basis"], "basis")


def reconcile_authoring_explanations(document, plan):
    """Return a new input with reviewed explanations, preserving its model data."""
    result = deepcopy(document)
    _history_projection(result, plan.get("historical_driver_contexts", {}))
    notes = plan.get("calibration_limitations", {})
    for row in result.get("operating_research", {}).get("calibrations", []):
        if row["scope"] in notes:
            row["limitations"] = list(notes[row["scope"]])
    _scenario_explanations(result, plan.get("scenario_bridges", []))
    return result
