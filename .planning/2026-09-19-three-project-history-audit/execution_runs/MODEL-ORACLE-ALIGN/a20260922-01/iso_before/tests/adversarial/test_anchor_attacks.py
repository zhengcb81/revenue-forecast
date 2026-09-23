"""Adversarial anchor attacks (R6.1) — promoted from review_audit probes.

Every attack here re-signs all hashes (receipt, result, workflow receipt) so
the artifact is internally self-consistent; the validator must still reject it
on semantic grounds.  These were the N-01 probes; R1.1 made them green.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from revenue_backtest import create_snapshot, validate_snapshot  # noqa: E402
from revenue_core import (  # noqa: E402
    ENGINE_VERSION,
    ForecastInputError,
    canonical_sha256,
    run_forecast,
)
from revenue_publication import (  # noqa: E402
    VerificationContext,
    build_publication_receipt,
    expected_publication_gates,
)
from revenue_report import validate_forecast_output  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def _inflate_input(data: dict) -> dict:
    attacker_input = copy.deepcopy(data)
    for parameter in attacker_input["parameters"]:
        if isinstance(parameter.get("value"), (int, float)) and parameter.get(
            "kind"
        ) in {"analyst_assumption", "scenario_stress"}:
            parameter["value"] = float(parameter["value"]) * 1.5
    return attacker_input


def _anchor_and_resign(forged: dict, anchor: str) -> dict:
    forged["input_sha256"] = anchor
    forged["workflow_compliance_receipt"]["input_sha256"] = anchor
    forged["workflow_compliance_receipt"]["receipt_sha256"] = canonical_sha256(
        {
            key: value
            for key, value in forged["workflow_compliance_receipt"].items()
            if key != "receipt_sha256"
        }
    )
    forged["publication_receipt"] = build_publication_receipt(
        forged,
        VerificationContext(
            forged["input_sha256"],
            expected_publication_gates(forged),
            ENGINE_VERSION,
        ),
    )
    forged["result_sha256"] = canonical_sha256(
        {key: value for key, value in forged.items() if key != "result_sha256"}
    )
    return forged


class AnchorAttackTests(unittest.TestCase):
    def test_d1_swapped_embedded_input_is_rejected(self) -> None:
        data = forecast_document()
        legit = run_forecast(copy.deepcopy(data))
        forged = copy.deepcopy(legit)
        swapped = copy.deepcopy(data)
        swapped["forecast_version"] = "attacker-version"
        forged["input_document"] = swapped
        _anchor_and_resign(forged, legit["input_sha256"])
        with self.assertRaises(ForecastInputError):
            validate_forecast_output(forged)

    def test_d2_inflated_numbers_anchored_to_legit_hash_are_rejected(self) -> None:
        data = forecast_document()
        legit = run_forecast(copy.deepcopy(data))
        forged = run_forecast(_inflate_input(data))
        self.assertNotEqual(
            forged["consolidated_forecast"]["base"]["terminal_revenue"],
            legit["consolidated_forecast"]["base"]["terminal_revenue"],
        )
        _anchor_and_resign(forged, legit["input_sha256"])
        with self.assertRaises(ForecastInputError):
            validate_forecast_output(forged)

    def test_d3_snapshot_swap_anchored_is_rejected(self) -> None:
        data = forecast_document()
        snapshot = create_snapshot(copy.deepcopy(data), "v1")
        forged_result = run_forecast(_inflate_input(data))
        _anchor_and_resign(forged_result, snapshot["input_sha256"])
        forged = copy.deepcopy(snapshot)
        forged["forecast_result"] = forged_result
        forged["input_document"] = _inflate_input(data)
        forged["forecast_result_sha256"] = canonical_sha256(forged_result)
        identity = {
            key: forged[key]
            for key in (
                "company_name",
                "as_of_date",
                "forecast_version",
                "input_sha256",
                "forecast_result_sha256",
                "engine_version",
                "forecast_schema_version",
                "snapshot_schema_version",
            )
        }
        forged["snapshot_id"] = canonical_sha256(identity)
        with self.assertRaises(ForecastInputError):
            validate_snapshot(forged)


if __name__ == "__main__":
    unittest.main()
