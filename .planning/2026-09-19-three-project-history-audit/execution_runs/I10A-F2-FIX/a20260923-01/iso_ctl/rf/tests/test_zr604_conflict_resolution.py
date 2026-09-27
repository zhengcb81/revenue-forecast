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


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
