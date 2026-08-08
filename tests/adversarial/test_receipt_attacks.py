"""Adversarial receipt attacks (R6.1) — a pass receipt cannot be self-issued.

These close the F-11 family: no VerificationContext, forged context, or
fabricated gate_ids may ever produce a valid publication receipt.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from revenue_core import ForecastInputError, canonical_sha256, run_forecast  # noqa: E402
from revenue_publication import (  # noqa: E402
    VerificationContext,
    build_publication_receipt,
    validate_publication_receipt,
)
from test_recognition_bridge import forecast_document  # noqa: E402


class ReceiptAttackTests(unittest.TestCase):
    def test_receipt_without_verification_context_is_rejected(self) -> None:
        # F-11: a receipt can never be self-issued without the strong-validator
        # VerificationContext.
        result = run_forecast(forecast_document())
        with self.assertRaisesRegex(TypeError, "VerificationContext"):
            build_publication_receipt(result)

    def test_context_fabrication_is_rejected_by_final_validation(self) -> None:
        # A VerificationContext copied from a legit run with fabricated
        # gate_ids can produce a receipt — but the final validator recomputes
        # the gates from the result and must reject the mismatch.
        from revenue_report import validate_published_forecast

        result = run_forecast(forecast_document())
        legit_context = validate_published_forecast(
            result, result["input_document"]
        )
        forged_context = copy.copy(legit_context)
        forged_context.executed_gate_ids = ["output_recomputation", "input_contract"]
        receipt = build_publication_receipt(
            result, forged_context, attestation_status="host_signed"
        )
        result["publication_receipt"] = receipt
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        with self.assertRaises(ForecastInputError):
            validate_publication_receipt(result)

    def test_fabricated_extra_gate_is_rejected_by_validator(self) -> None:
        # gate_ids are recomputed from the result content; adding a gate the
        # strong validator would not execute must fail.
        result = run_forecast(forecast_document())
        receipt = result["publication_receipt"]
        forged = copy.deepcopy(receipt)
        forged["gate_ids"] = [*receipt["gate_ids"], "fabricated_gate"]
        forged["receipt_sha256"] = canonical_sha256(
            {key: value for key, value in forged.items() if key != "receipt_sha256"}
        )
        result["publication_receipt"] = forged
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        with self.assertRaises(ForecastInputError):
            validate_publication_receipt(result)


if __name__ == "__main__":
    unittest.main()
