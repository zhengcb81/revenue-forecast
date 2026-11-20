"""ZR-604 acceptance tests: dual-assertion conflict resolution —
conflicting parameters (same definition/period/unit/scenario, different
values) may coexist when ALL carry resolution_status and at most one is
accepted; otherwise the original hard-fail applies.

  C1  conflict resolution: unresolved conflicts without resolution_status
      fail as before (backward compatible); resolved conflicts (all carry
      resolution_status, at most one accepted) pass; multiple accepted
      assertions fail closed; partial resolution (some carry, some don't)
      fails closed.
  C2  vocabulary: assertion_status ∈ {primary, secondary};
      resolution_status ∈ {accepted, rejected, pending_review,
      under_review}; invalid values rejected; missing keys unaffected.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from contracts.constants import ASSERTION_STATUSES, RESOLUTION_STATUSES  # noqa: E402
from contracts.document import validate_document  # noqa: E402
from contracts.evidence import ForecastInputError  # noqa: E402
from test_data_contract import finalize_contract, valid_document  # noqa: E402


def _doc_with_two_base_params(
    value_a: float,
    value_b: float,
    *,
    status_a: str | None = None,
    status_b: str | None = None,
    assertion_a: str | None = None,
    assertion_b: str | None = None,
) -> dict:
    data = valid_document()
    param_a = {
        "parameter_id": "conflict_a",
        "kind": "analyst_assumption",
        "value": value_a,
        "unit": "USD million",
        "period": "FY2025",
        "definition": "reported total revenue",
        "scenario": "shared",
        "rationale": "conflict test A",
        "source_ids": ["filing"],
    }
    param_b = {
        "parameter_id": "conflict_b",
        "kind": "analyst_assumption",
        "value": value_b,
        "unit": "USD million",
        "period": "FY2025",
        "definition": "reported total revenue",
        "scenario": "shared",
        "rationale": "conflict test B",
        "source_ids": ["filing"],
    }
    if status_a is not None:
        param_a["resolution_status"] = status_a
    if status_b is not None:
        param_b["resolution_status"] = status_b
    if assertion_a is not None:
        param_a["assertion_status"] = assertion_a
    if assertion_b is not None:
        param_b["assertion_status"] = assertion_b
    data["parameters"].extend([param_a, param_b])
    return finalize_contract(data)


# ---------------------------------------------------------------------------
# C1 — conflict resolution
# ---------------------------------------------------------------------------


def test_c1_unresolved_conflict_fails_backward_compat():
    data = _doc_with_two_base_params(100.0, 95.0)
    with pytest.raises(ForecastInputError, match="unresolved conflicting"):
        validate_document(data)


def test_c1_resolved_conflict_one_accepted_passes():
    data = _doc_with_two_base_params(
        100.0, 95.0, status_a="accepted", status_b="rejected",
    )
    validate_document(data)


def test_c1_multiple_accepted_fails():
    data = _doc_with_two_base_params(
        100.0, 95.0, status_a="accepted", status_b="accepted",
    )
    with pytest.raises(ForecastInputError, match="multiple accepted"):
        validate_document(data)


def test_c1_all_pending_review_passes():
    data = _doc_with_two_base_params(
        100.0, 95.0, status_a="pending_review", status_b="pending_review",
    )
    validate_document(data)


def test_c1_partial_resolution_fails():
    data = _doc_with_two_base_params(100.0, 95.0, status_a="accepted")
    with pytest.raises(ForecastInputError, match="unresolved conflicting"):
        validate_document(data)


def test_c1_same_value_no_conflict():
    data = _doc_with_two_base_params(100.0, 100.0)
    validate_document(data)


# ---------------------------------------------------------------------------
# C2 — vocabulary
# ---------------------------------------------------------------------------


def test_c2_valid_assertion_status_accepted():
    data = _doc_with_two_base_params(
        100.0, 95.0,
        status_a="accepted", status_b="rejected",
        assertion_a="primary", assertion_b="secondary",
    )
    validate_document(data)


def test_c2_invalid_assertion_status_rejected():
    data = _doc_with_two_base_params(
        100.0, 95.0,
        status_a="accepted", status_b="rejected",
        assertion_a="tertiary",
    )
    with pytest.raises(ForecastInputError, match="unsupported assertion_status"):
        validate_document(data)


def test_c2_invalid_resolution_status_rejected():
    data = _doc_with_two_base_params(
        100.0, 95.0, status_a="accepted", status_b="ignored",
    )
    with pytest.raises(ForecastInputError, match="unsupported resolution_status"):
        validate_document(data)


def test_c2_vocabulary_exact():
    assert ASSERTION_STATUSES == {"primary", "secondary"}
    assert RESOLUTION_STATUSES == {
        "accepted", "rejected", "pending_review", "under_review",
    }


def test_c2_missing_status_keys_unchanged():
    # legacy parameters without assertion/resolution status are unaffected
    validate_document(finalize_contract(valid_document()))



def _scope_document() -> dict:
    from test_recognition_bridge import forecast_document

    data = forecast_document()
    colliding = {"0_low_2026", "1_low_2026"}
    for parameter in data["parameters"]:
        if parameter["parameter_id"] in colliding:
            parameter["definition"] = "Expected revenue for the business"
    return finalize_contract(data)


def test_identical_definition_in_distinct_native_segments_is_not_a_conflict():
    from revenue_core import run_forecast
    from revenue_report import validate_published_forecast

    data = _scope_document()
    result = run_forecast(data)
    validate_published_forecast(result, data)
    assert result["consolidated_forecast"]["low"]["annual_revenue"]["2026"] == 150.0


def _use_as_derived(data: dict, segment: int, inputs: list[str], formula: str, value: float) -> None:
    from test_recognition_bridge import add_parameter

    derived_id = add_parameter(data, f"scoped_derived_{segment}", value, 2026, "low")
    parameter = next(p for p in data["parameters"] if p["parameter_id"] == derived_id)
    parameter.update(kind="derived_fact", formula=formula, input_parameter_ids=inputs)
    data["segments"][segment]["scenarios"]["low"]["driver_parameter_ids"]["revenue"][0] = derived_id


@pytest.mark.parametrize("statuses, error", [
    ((None, None), "unresolved conflicting"),
    (("accepted", "accepted"), "multiple accepted"),
])
def test_same_business_conflicting_measure_cannot_use_segment_partition(statuses, error):
    data = _scope_document()
    for parameter, status in zip((p for p in data["parameters"] if p["parameter_id"] in
                                  {"0_low_2026", "1_low_2026"}), statuses, strict=True):
        if status is not None:
            parameter["resolution_status"] = status
    _use_as_derived(data, 0, ["0_low_2026", "1_low_2026"], "2 * (x0 - x1)", 100.0)
    # Segment B uses an independent value, keeping the two incompatible
    # assumptions solely in A even though both have model ancestry.
    _use_as_derived(data, 1, ["1_low_2027"], "x0", 50.0)
    with pytest.raises(ForecastInputError, match=error):
        validate_document(finalize_contract(data))


@pytest.mark.parametrize("shared", [True, False], ids=["shared", "declared-unused"])
def test_shared_or_unused_conflict_is_not_proven_independent(shared):
    data = _scope_document()
    inputs = ["1_low_2026", "0_low_2026"] if shared else ["1_low_2026", "1_low_2027"]
    formula = "x0 + 0.01 * x1" if shared else "x1"
    value = 51.0 if shared else 50.0
    _use_as_derived(data, 1, inputs, formula, value)
    with pytest.raises(ForecastInputError, match="unresolved conflicting"):
        validate_document(finalize_contract(data))



def test_implicit_base_consumption_keeps_shared_observations_in_conflict():
    from revenue_core import run_forecast
    from test_recognition_bridge import add_parameter, forecast_document

    data = forecast_document()
    baseline = [segment["base_revenue_parameter_id"] for segment in data["segments"]]
    values = {p["parameter_id"]: p["value"] for p in data["parameters"]}
    for p in data["parameters"]:
        if p["parameter_id"] in baseline:
            p["definition"] = "IFRS external revenue under review"

    base_driver_ids = []
    for segment, peer in zip(data["segments"], reversed(baseline), strict=True):
        for scenario, shift in (("low", 0.0), ("base", 0.1), ("high", 0.2)):
            rates = []
            for year in data["forecast_years"]:
                pid = add_parameter(data, f'{segment["name"]}_{scenario}_{year}_rate',
                                    values[peer] / 10000 + shift, year, scenario, dimension="ratio")
                parameter = next(p for p in data["parameters"] if p["parameter_id"] == pid)
                parameter.update(kind="derived_fact", source_ids=[], claim_ids=[],
                                 formula=f"x0/10000+{shift}", input_parameter_ids=[peer])
                rates.append(pid)
            segment["scenarios"][scenario].update(
                model="direct_growth", driver_parameter_ids={"growth_rate": rates},
            )
            if scenario == "base":
                base_driver_ids.extend(rates)
    growth = next(record for record in data["research_coverage"] if record["dimension"] == "growth_curve")
    growth["parameter_ids"] = base_driver_ids

    # Each model consumes its own baseline implicitly and the other one
    # through a derived driver. Direct roots alone make them look exclusive.
    with pytest.raises(ForecastInputError, match="unresolved conflicting"):
        run_forecast(finalize_contract(data), mode="draft")


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
