"""Publication receipts for formal revenue forecast output.

A publication receipt certifies that a forecast result has passed the
self-contained output validator (``validate_forecast_output``). ``run_forecast``
signs it only after validation succeeds, and it binds the validated payload to
the input, schema, engine and validator version that produced it.

Design rules (task_plan.md Phase 2):

* ``result_sha256`` continues to cover the whole result (including this receipt),
  so existing tamper/rehash contracts are unchanged.
* ``validated_payload_sha256`` excludes both ``result_sha256`` and
  ``publication_receipt`` so the receipt never references itself (no recursion /
  non-determinism).
* This module never re-runs the revenue model — it only hashes and validates.
"""

from __future__ import annotations

from typing import Any

from revenue_core import (
    ENGINE_VERSION,
    PUBLICATION_RECEIPT_SCHEMA_VERSION,
    canonical_sha256,
    require,
)


# The output-recomputation gate is certified by validate_forecast_output, not by
# the execution receipt, so it lives on the publication receipt.
PUBLICATION_GATE_IDS = ("output_recomputation",)

_FORMAL_OUTPUT_MODE = "formal"


def _payload_sha256(result: dict[str, Any]) -> str:
    """Hash the result payload excluding the two receipt/hash fields."""
    payload = {
        key: value
        for key, value in result.items()
        if key not in ("result_sha256", "publication_receipt")
    }
    return canonical_sha256(payload)


def _receipt_sha256(receipt: dict[str, Any]) -> str:
    return canonical_sha256(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )


def build_publication_receipt(result: dict[str, Any]) -> dict[str, Any]:
    """Build a publication receipt binding a result payload to its input."""
    receipt = {
        "receipt_schema_version": PUBLICATION_RECEIPT_SCHEMA_VERSION,
        "schema_version": result["schema_version"],
        "engine_version": ENGINE_VERSION,
        "validated_input_sha256": result["input_sha256"],
        "validated_payload_sha256": _payload_sha256(result),
        "validator_version": ENGINE_VERSION,
        "gate_ids": list(PUBLICATION_GATE_IDS),
        "formal_output_mode": _FORMAL_OUTPUT_MODE,
        "freeform_override_allowed": False,
    }
    receipt["receipt_sha256"] = _receipt_sha256(receipt)
    return receipt


def validate_publication_receipt(result: dict[str, Any]) -> None:
    """Validate the publication receipt bound to a published forecast result."""
    require("publication_receipt" in result, "forecast output missing field: publication_receipt")
    receipt = result["publication_receipt"]
    require(isinstance(receipt, dict), "publication_receipt must be an object")
    require(receipt.get("receipt_schema_version") == PUBLICATION_RECEIPT_SCHEMA_VERSION, "publication_receipt receipt_schema_version mismatch")
    require(receipt.get("schema_version") == result["schema_version"], "publication_receipt schema_version mismatch")
    require(receipt.get("engine_version") == ENGINE_VERSION, "publication_receipt engine_version mismatch")
    require(receipt.get("validated_input_sha256") == result["input_sha256"], "publication_receipt validated_input_sha256 mismatch")
    require(receipt.get("validated_payload_sha256") == _payload_sha256(result), "publication_receipt validated_payload_sha256 mismatch")
    require(receipt.get("validator_version") == ENGINE_VERSION, "publication_receipt validator_version mismatch")
    require(receipt.get("gate_ids") == list(PUBLICATION_GATE_IDS), "publication_receipt gate_ids mismatch")
    require(receipt.get("formal_output_mode") == _FORMAL_OUTPUT_MODE, "publication_receipt formal_output_mode mismatch")
    require(receipt.get("freeform_override_allowed") is False, "publication_receipt freeform_override_allowed must be false")
    require(receipt.get("receipt_sha256") == _receipt_sha256(receipt), "publication_receipt receipt_sha256 mismatch")
