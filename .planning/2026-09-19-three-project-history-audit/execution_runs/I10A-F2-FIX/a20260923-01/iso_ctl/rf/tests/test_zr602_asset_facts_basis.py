"""ZR-602 acceptance tests: asset facts basis contract — resource≠reserve
semantic isolation, ownership/standard/measurement-date basis (fail-closed),
and asset-fact family unit consistency.

  C1  semantic isolation: resource rejects reserve drivers and vice versa
      (unsupported drivers); MODEL_SPECS driver vocabularies are disjoint;
      asset-fact model families are registered as generic constants.
  C2  basis contract: a parameter carrying ``basis`` must be a complete,
      valid basis (ownership_basis enum / reporting_standard / ISO
      measurement_date); half-baked or invalid basis fails closed; additive —
      parameters without ``basis`` are unaffected.
  C3  unit consistency: asset-fact family drivers sharing a dimension must
      carry the same normalized unit; cross-driver/cross-period drift
      (kt vs t) is rejected. Conversion tables are out of scope (ZR-610 ADR).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from contracts.constants import (  # noqa: E402
    ASSET_FACT_BASIS_REQUIRED,
    ASSET_FACT_MODELS,
    ASSET_FACT_OWNERSHIP_BASES,
)
from contracts.document import validate_document, validate_parameter_basis  # noqa: E402
from contracts.evidence import ForecastInputError  # noqa: E402
from revenue_core import MODEL_SPECS, calculate_model_path  # noqa: E402
from test_data_contract import finalize_contract, valid_document  # noqa: E402
from test_models import YEARS, make_parameters  # noqa: E402

VALID_BASIS = {
    "ownership_basis": "one_hundred_percent",
    "reporting_standard": "JORC 2012",
    "measurement_date": "2025-12-31",
}


def _run(model: str, drivers: dict, scenario: str = "base") -> dict:
    params, ids = make_parameters(model, drivers, scenario=scenario)
    return calculate_model_path(model, 0, ids, params, YEARS, scenario)


def _reserve_drivers() -> dict:
    return {
        "opening_reserves": [1000.0, 1020.0],
        "additions": [100.0, 110.0],
        "depletion": [80.0, 90.0],
        "closing_reserves": [1020.0, 1040.0],
        "recovery_rate": [0.9, 0.92],
        "realized_price": [5.0, 5.5],
    }


# ---------------------------------------------------------------------------
# C1 — resource≠reserve semantic isolation
# ---------------------------------------------------------------------------


def _params_for(model: str, drivers: dict, extra: dict | None = None) -> tuple[dict, dict]:
    """Build parameter index + ids for arbitrary driver sets (incl. cross-model
    injection) without make_parameters' dimension lookup."""
    parameters, ids = {}, {}
    all_drivers = dict(drivers)
    all_drivers.update(extra or {})
    for driver, values in all_drivers.items():
        ids[driver] = []
        for year, value in zip(YEARS, values):
            pid = f"{driver}_{year}"
            parameters[pid] = {
                "parameter_id": pid,
                "kind": "analyst_assumption",
                "value": float(value),
                "unit": "test",
                "period": f"FY{year}",
                "definition": driver,
                "scenario": "base",
                "rationale": "zr602 probe",
                "source_ids": [],
                "claim_ids": [],
                "dimension": "quantity",
                "time_basis": "annual",
            }
            ids[driver].append(pid)
    return parameters, ids


def test_c1_reserve_drivers_rejected_by_resource():
    drivers = {"saleable_volume": [10.0, 11.0], "realized_price": [5.0, 5.0]}
    extra = {"opening_reserves": [999.0, 999.0]}
    params, ids = _params_for("resource", drivers, extra)
    with pytest.raises(ForecastInputError, match="unsupported drivers"):
        calculate_model_path("resource", 0, ids, params, YEARS, "base")


def test_c1_resource_drivers_rejected_by_reserve():
    drivers = {"opening_reserves": [1000.0, 1020.0], "additions": [100.0, 110.0],
               "depletion": [80.0, 90.0], "closing_reserves": [1020.0, 1040.0],
               "recovery_rate": [0.9, 0.92], "realized_price": [5.0, 5.5]}
    extra = {"saleable_volume": [1.0, 1.0]}
    params, ids = _params_for("reserve_depletion", drivers, extra)
    with pytest.raises(ForecastInputError, match="unsupported drivers"):
        calculate_model_path("reserve_depletion", 0, ids, params, YEARS, "base")


def test_c1_driver_vocabularies_are_disjoint():
    resource_drivers = set(MODEL_SPECS["resource"]["required"]) | set(
        MODEL_SPECS["resource"]["optional"]
    )
    reserve_drivers = set(MODEL_SPECS["reserve_depletion"]["required"]) | set(
        MODEL_SPECS["reserve_depletion"]["optional"]
    )
    # shared generic drivers (realized_price/other_revenue) are legitimate;
    # family-specific vocabularies must not cross over
    shared = resource_drivers & reserve_drivers
    assert shared <= {"realized_price", "other_revenue"}
    assert "saleable_volume" not in reserve_drivers
    assert {"opening_reserves", "additions", "depletion", "closing_reserves",
            "recovery_rate"}.isdisjoint(resource_drivers)


def test_c1_asset_fact_models_registered_as_generic_constants():
    assert ASSET_FACT_MODELS == frozenset({"resource", "reserve_depletion"})
    for model in ASSET_FACT_MODELS:
        assert model in MODEL_SPECS
    # generic mining vocabulary only — no company/mine name hardcoding
    assert "zijin" not in {name.lower() for name in ASSET_FACT_MODELS}


# ---------------------------------------------------------------------------
# C2 — basis contract (additive, fail-closed when present)
# ---------------------------------------------------------------------------


def _document_with_basis(basis: dict | None) -> dict:
    data = valid_document()
    if basis is not None:
        data["parameters"][0]["basis"] = basis
    return finalize_contract(data)


def _run_with_basis(model: str, drivers: dict, basis: dict) -> dict:
    params, ids = make_parameters(model, drivers)
    # attach the basis key to every driver parameter (additive key)
    for pid in params:
        params[pid]["basis"] = basis
    return calculate_model_path(model, 0, ids, params, YEARS, "base")


def test_c2_valid_basis_accepted_at_document_level():
    data = _document_with_basis(VALID_BASIS)
    validated = validate_document(data)
    assert validated["parameter_index"]["reported_total"]["basis"] == VALID_BASIS


@pytest.mark.parametrize("missing", ["ownership_basis", "reporting_standard",
                                     "measurement_date"])
def test_c2_incomplete_basis_rejected(missing):
    basis = dict(VALID_BASIS)
    basis.pop(missing)
    with pytest.raises(ForecastInputError,
                       match=f"basis.{missing} is required"):
        validate_parameter_basis("p1", basis)


def test_c2_unsupported_ownership_basis_rejected():
    basis = dict(VALID_BASIS)
    basis["ownership_basis"] = "two_thirds_share"
    with pytest.raises(ForecastInputError, match="unsupported ownership_basis"):
        validate_parameter_basis("p1", basis)


@pytest.mark.parametrize("bad", [[], {}, 7, None, 1.5])
def test_c2_unhashable_ownership_basis_rejected(bad):
    # REV-001 regression: unhashable ownership_basis must raise
    # ForecastInputError (never TypeError)
    basis = dict(VALID_BASIS)
    basis["ownership_basis"] = bad
    with pytest.raises(ForecastInputError, match="unsupported ownership_basis"):
        validate_parameter_basis("p1", basis)


def test_c2_empty_reporting_standard_rejected():
    basis = dict(VALID_BASIS)
    basis["reporting_standard"] = "   "
    with pytest.raises(ForecastInputError,
                       match="basis.reporting_standard is required"):
        validate_parameter_basis("p1", basis)


def test_c2_invalid_measurement_date_rejected():
    basis = dict(VALID_BASIS)
    basis["measurement_date"] = "2025/12/31"
    with pytest.raises(ForecastInputError, match="YYYY-MM-DD"):
        validate_parameter_basis("p1", basis)


def test_c2_basis_is_additive_parameters_without_it_pass():
    # legacy parameters without basis must be unaffected (additive contract)
    result = _run("resource", {"saleable_volume": [10.0, 11.0],
                               "realized_price": [5.0, 5.0]})
    assert list(result["annual_revenue"].values()) == [50.0, 55.0]
    # ownership basis vocabulary covers 100% / equity / consolidated
    assert ASSET_FACT_OWNERSHIP_BASES == {
        "one_hundred_percent", "equity_share", "consolidated",
    }
    assert ASSET_FACT_BASIS_REQUIRED == (
        "ownership_basis", "reporting_standard", "measurement_date",
    )


def test_c2_incomplete_basis_rejected_at_document_level():
    # validate_document rejects half-baked basis before any calculation
    data = _document_with_basis({"ownership_basis": "one_hundred_percent"})
    with pytest.raises(ForecastInputError,
                       match="basis.reporting_standard is required"):
        validate_document(data)


# ---------------------------------------------------------------------------
# C3 — asset fact family unit consistency
# ---------------------------------------------------------------------------


def test_c3_mixed_units_across_drivers_rejected():
    params, ids = make_parameters("reserve_depletion", _reserve_drivers())
    # drift: depletion in tonnes while opening reserves are in kt
    for pid, p in params.items():
        if p["parameter_id"].startswith("depletion_"):
            p["unit"] = "t"
    with pytest.raises(ForecastInputError, match="asset fact unit mismatch"):
        calculate_model_path("reserve_depletion", 0, ids, params, YEARS, "base")


def test_c3_case_whitespace_normalized_units_accepted():
    params, ids = make_parameters("reserve_depletion", _reserve_drivers())
    for index, pid in enumerate(params):
        params[pid]["unit"] = " KT " if index % 2 == 0 else "kt"
    result = calculate_model_path("reserve_depletion", 0, ids, params, YEARS,
                                  "base")
    assert len(result["annual_revenue"]) == len(YEARS)


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
