"""Prove a separately booked pending amount in an authored direct-growth path."""

from __future__ import annotations

import ast
from collections import Counter

from contracts.evidence import ForecastInputError, parse_iso_date, require
from contracts.period_flow import dated_flow_origins, validate_period_flow_fields


def _signed_addends(expression):
    pending = [(expression, 1)]
    while pending:
        node, sign = pending.pop()
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            pending.extend(((node.right, -sign if isinstance(node.op, ast.Sub) else sign),
                            (node.left, sign)))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            pending.append((node.operand, -sign if isinstance(node.op, ast.USub) else sign))
        else:
            yield node, sign


def _binding(parameter):
    try:
        parsed = ast.parse(parameter["formula"], mode="eval")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ForecastInputError("recognition forecast path needs a valid native formula") from exc
    return parsed.body, {f"x{i}": ref for i, ref in enumerate(parameter["input_parameter_ids"])}


def _named_amounts(expression, names, index):
    amounts = []
    for term, sign in _signed_addends(expression):
        if isinstance(term, ast.Constant) and type(term.value) in (int, float) and term.value == 0:
            continue
        ref = names.get(term.id) if isinstance(term, ast.Name) else None
        if index.get(ref, {}).get("dimension") != "revenue":
            return None
        amounts.append((ref, sign))
    return amounts


def _expand_amounts(amounts, index, stop_at=None):
    pending = [(ref, sign, frozenset()) for ref, sign in amounts]
    while pending:
        ref, sign, seen = pending.pop()
        require(ref not in seen, f"{ref}: cycle in recognition forecast path")
        row = index[ref]
        if ref != stop_at and row["kind"] == "derived_fact":
            expression, names = _binding(row)
            children = _named_amounts(expression, names, index)
            if children:
                pending.extend((child, sign * weight, seen | {ref}) for child, weight in children)
                continue
        yield ref, sign


def _weights(terms):
    weights = Counter()
    for ref, sign in terms:
        weights[ref] += sign
    return {ref: weight for ref, weight in weights.items() if weight}


def _native_opening(expression, names, path):
    # A referenced opening amount can itself be the native cumulative formula.
    # Compare actual parameter identities and arithmetic roles, never balances.
    factors = []
    pending = [expression]
    while pending:
        node = pending.pop()
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            pending.extend((node.left, node.right))
        else:
            factors.append(node)
    amounts, growth = [], []
    for factor in factors:
        if isinstance(factor, ast.Name):
            amounts.append(names.get(factor.id))
            continue
        terms = list(_signed_addends(factor))
        if len(terms) != 2:
            return False
        ones = [term for term, sign in terms if sign == 1 and isinstance(term, ast.Constant)
                and type(term.value) in (int, float) and term.value == 1]
        rates = [names.get(term.id) for term, sign in terms if sign == 1 and isinstance(term, ast.Name)]
        if len(ones) != 1 or len(rates) != 1:
            return False
        growth.extend(rates)
    return amounts == path[:1] and Counter(growth) == Counter(path[1:])


def _recognized_amounts(index, path):
    # R[t] = R[t-1]*(1+g[t]). A recognized-amount bridge supplies g as
    # signed revenue amounts divided by that same previous recognized value.
    # Cancel the opening-value term by identity and keep the actual addends.
    previous = [(path[0], 1)]
    for offset, growth_id in enumerate(path[1:], start=1):
        ratio = index[growth_id]
        if ratio["kind"] != "derived_fact":
            previous = None
            continue
        previous_weights = _weights(_expand_amounts(previous, index)) if previous else None

        def is_opening(ref):
            row = index.get(ref, {})
            if row.get("dimension") != "revenue":
                return False
            if previous_weights is not None and _weights(_expand_amounts([(ref, 1)], index)) == previous_weights:
                return True
            return row["kind"] == "derived_fact" and _native_opening(*_binding(row), path[:offset])

        expression, names = _binding(ratio)
        opening_weight = 1
        amounts = []
        for term, sign in _signed_addends(expression):
            if isinstance(term, ast.Constant) and type(term.value) in (int, float):
                opening_weight += sign * term.value
                continue
            if not (isinstance(term, ast.BinOp) and isinstance(term.op, ast.Div)
                    and isinstance(term.right, ast.Name) and is_opening(names.get(term.right.id))):
                break
            dividend = _named_amounts(term.left, names, index)
            if dividend is None:
                break
            for ref, weight in dividend:
                if is_opening(ref):
                    opening_weight += sign * weight
                else:
                    amounts.append((ref, sign * weight))
        else:
            previous = amounts if opening_weight == 0 and amounts else None
            continue
        previous = None
    return previous


def prove_pending_exposure(data, index, path, exposure_id, scenario, year):
    """Return the exact source-period and native growth bindings for a shift."""
    exposure = index.get(exposure_id, {})
    require(exposure.get("dimension") == "revenue" and exposure.get("time_basis") == "period_flow"
            and exposure.get("period") == f"FY{year}" and exposure.get("scenario") in (None, "all", scenario),
            f"{exposure_id}: stress exposure must be dated revenue in the affected fiscal period and scenario")
    fiscal_end = data["fiscal_year_end"]
    window = validate_period_flow_fields(exposure_id, exposure, fiscal_end, data["schema_version"])
    cutoff = parse_iso_date(data["as_of_date"], "as_of_date")
    origins = dated_flow_origins(exposure_id, index, fiscal_end)
    weights = _weights((origin.parameter_id, origin.coefficient) for origin in origins)
    require(bool(weights), f"{exposure_id}: expected an identified pending revenue amount")
    for origin in origins:
        if origin.parameter_id not in weights:
            continue
        row = index[origin.parameter_id]
        require(row["kind"] != "reported_fact",
                f"{exposure_id}: already reported revenue is outside the stress exposure")
        require(row["kind"] in {"analyst_assumption", "scenario_stress", "management_guidance"}
                and row.get("time_basis") == "period_flow"
                and window["period_start"] <= origin.start <= origin.end <= window["period_end"]
                and cutoff < origin.end,
                f"{exposure_id}: stress requires a known, unfinished forecast window")

    recognized = _recognized_amounts(index, path)
    message = f"{exposure_id}: forecast path does not book this pending amount as a separate addend"
    require(recognized is not None, message)
    addends = list(_expand_amounts(recognized, index, stop_at=exposure_id))
    require([weight for ref, weight in addends if ref == exposure_id] == [1], message)
    for ref, _ in addends:
        if ref == exposure_id:
            continue
        other = dated_flow_origins(ref, index, fiscal_end)
        require(not weights.keys() & {origin.parameter_id for origin in other},
                f"{exposure_id}: forecast path reuses the same pending flow in another addend")
    return {
        "growth_parameter_id": path[-1],
        "annual_amount_terms": dict(sorted(_weights(recognized).items())),
        "pending_origin_ids": sorted(weights),
        "pending_window": {key: endpoint.isoformat() for key, endpoint in window.items()},
        "recognized_coefficient": 1,
    }
