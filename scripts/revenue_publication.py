"""Publication receipts for formal revenue forecast output.

A publication receipt certifies that a forecast result has passed the
self-contained output validator.  Since the receipt is only issued from a
verification context produced by ``validate_published_forecast`` (the strong,
input-required entry), a weakly-validated or forged artifact cannot obtain a
valid receipt.

Design rules (task_plan.md Phase 2 / Phase 6 A1):

* ``result_sha256`` continues to cover the whole result (including this receipt),
  so existing tamper/rehash contracts are unchanged.
* ``validated_payload_sha256`` excludes both ``result_sha256`` and
  ``publication_receipt`` so the receipt never references itself (no recursion /
  non-determinism).
* ``gate_ids`` reflect the gates that actually executed during strong
  validation (see ``expected_publication_gates``), never a fixed claim.
* ``verification_context_sha256`` binds the receipt to the exact
  ``VerificationContext`` returned by ``validate_published_forecast``; the
  validator recomputes it so a receipt built from a weaker or fabricated
  context is rejected.
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


# Gates certified by the strong validator (validate_published_forecast) when
# the artifact carries sensitivity results.
OUTPUT_RECOMPUTATION_GATE = "output_recomputation"
SENSITIVITY_SHOCK_RECOMPUTATION_GATE = "sensitivity_shock_recomputation"


def expected_publication_gates(result: dict[str, Any]) -> tuple[str, ...]:
    """The gates the strong validator actually executes for *result*.

    Deterministic so the verification-context binding can be recomputed by any
    consumer.  Sensitivity shock recomputation only runs when the result
    carries sensitivity data; otherwise only the structural output
    recomputation gate applies.
    """
    gates = [OUTPUT_RECOMPUTATION_GATE]
    if result.get("sensitivities"):
        gates.append(SENSITIVITY_SHOCK_RECOMPUTATION_GATE)
    return tuple(gates)


class VerificationContext:
    """Opaque record of a successful strong validation.

    Produced only by ``validate_published_forecast`` (or by test helpers that
    deliberately simulate a fully-informed attacker recomputing every hash).
    ``executed_gate_ids`` is derived from the result content, so a receipt built
    for an artifact whose sensitivity was forged without running the shock
    recomputation cannot match the strong gate contract.
    """

    __slots__ = ("validated_input_sha256", "executed_gate_ids", "validator_version")

    def __init__(
        self,
        validated_input_sha256: str,
        executed_gate_ids: tuple[str, ...],
        validator_version: str,
    ) -> None:
        if not isinstance(validated_input_sha256, str) or not validated_input_sha256:
            raise TypeError("validated_input_sha256 must be a non-empty string")
        if not isinstance(executed_gate_ids, tuple) or not executed_gate_ids:
            raise TypeError("executed_gate_ids must be a non-empty tuple")
        if not isinstance(validator_version, str) or not validator_version:
            raise TypeError("validator_version must be a non-empty string")
        self.validated_input_sha256 = validated_input_sha256
        self.executed_gate_ids = executed_gate_ids
        self.validator_version = validator_version

    def to_dict(self) -> dict[str, Any]:
        return {
            "validated_input_sha256": self.validated_input_sha256,
            "executed_gate_ids": list(self.executed_gate_ids),
            "validator_version": self.validator_version,
        }

    def context_sha256(self) -> str:
        return canonical_sha256(self.to_dict())


# The output-recomputation gate is certified by validate_published_forecast, not
# by the execution receipt, so it lives on the publication receipt.
PUBLICATION_GATE_IDS = expected_publication_gates({"sensitivities": []})


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


ATTESTATION_STATUSES = {"host_signed", "unattested"}


def build_publication_receipt(
    result: dict[str, Any],
    verification_context: VerificationContext | None = None,
    *,
    attestation_status: str = "unattested",
) -> dict[str, Any]:
    """Build a publication receipt from a strong-validation verification context.

    Without a ``VerificationContext`` the receipt cannot certify the strong
    gates, so the call fails closed (RED: the public API must never hand back a
    pass receipt before strong validation has run).

    *attestation_status* records whether the host attestation was actually
    signed (R2.1): ``"host_signed"`` requires an external attestation provider
    to be configured; without one the runtime can only produce ``"unattested"``
    publications, which invest-* consumers reject by default.
    """
    if not isinstance(verification_context, VerificationContext):
        raise TypeError(
            "build_publication_receipt requires a VerificationContext produced "
            "by validate_published_forecast; a receipt cannot be self-issued"
        )
    if attestation_status not in ATTESTATION_STATUSES:
        raise ValueError(
            f"attestation_status must be one of {sorted(ATTESTATION_STATUSES)}"
        )
    receipt = {
        "receipt_schema_version": PUBLICATION_RECEIPT_SCHEMA_VERSION,
        "schema_version": result["schema_version"],
        "engine_version": ENGINE_VERSION,
        "validated_input_sha256": verification_context.validated_input_sha256,
        "validated_payload_sha256": _payload_sha256(result),
        "validator_version": verification_context.validator_version,
        "gate_ids": list(verification_context.executed_gate_ids),
        "verification_context_sha256": verification_context.context_sha256(),
        "formal_output_mode": "formal",
        "freeform_override_allowed": False,
        "attestation_status": attestation_status,
    }
    receipt["receipt_sha256"] = _receipt_sha256(receipt)
    return receipt


def build_draft_receipt(result: dict[str, Any]) -> dict[str, Any]:
    """Build a draft-mode receipt that certifies no strong gate.

    Draft artifacts are not investment-consumable; the receipt records the
    draft mode so consumers can distinguish draft from formal at a glance.
    """
    receipt = {
        "receipt_schema_version": PUBLICATION_RECEIPT_SCHEMA_VERSION,
        "schema_version": result["schema_version"],
        "engine_version": ENGINE_VERSION,
        "validated_input_sha256": result["input_sha256"],
        "validated_payload_sha256": _payload_sha256(result),
        "validator_version": ENGINE_VERSION,
        "gate_ids": [],
        "verification_context_sha256": None,
        "formal_output_mode": "draft",
        "freeform_override_allowed": False,
    }
    receipt["receipt_sha256"] = _receipt_sha256(receipt)
    return receipt


def validate_publication_receipt(result: dict[str, Any]) -> None:
    """Validate the publication receipt bound to a published forecast result.

    Recomputes the expected verification context from the result content, so a
    receipt whose ``gate_ids`` do not match the gates the strong validator would
    execute (forged sensitivity without shock recomputation) is rejected.
    """
    require(
        "publication_receipt" in result,
        "forecast output missing field: publication_receipt",
    )
    receipt = result["publication_receipt"]
    require(isinstance(receipt, dict), "publication_receipt must be an object")
    require(
        receipt.get("receipt_schema_version") == PUBLICATION_RECEIPT_SCHEMA_VERSION,
        "publication_receipt receipt_schema_version mismatch",
    )
    require(
        receipt.get("schema_version") == result["schema_version"],
        "publication_receipt schema_version mismatch",
    )
    require(
        receipt.get("engine_version") == ENGINE_VERSION,
        "publication_receipt engine_version mismatch",
    )
    require(
        receipt.get("validated_input_sha256") == result["input_sha256"],
        "publication_receipt validated_input_sha256 mismatch",
    )
    require(
        receipt.get("validated_payload_sha256") == _payload_sha256(result),
        "publication_receipt validated_payload_sha256 mismatch",
    )
    require(
        receipt.get("validator_version") == ENGINE_VERSION,
        "publication_receipt validator_version mismatch",
    )
    attestation = receipt.get("attestation_status")
    require(
        attestation in (None, "host_signed", "unattested"),
        "publication_receipt attestation_status mismatch",
    )
    expected_gates = expected_publication_gates(result)
    require(
        receipt.get("gate_ids") == list(expected_gates),
        "publication_receipt gate_ids mismatch",
    )
    if receipt.get("formal_output_mode") == "formal":
        expected_context = VerificationContext(
            result["input_sha256"], expected_gates, ENGINE_VERSION
        )
        require(
            receipt.get("verification_context_sha256")
            == expected_context.context_sha256(),
            "publication_receipt verification context mismatch",
        )
    require(
        receipt.get("formal_output_mode") in {"formal", "draft"},
        "publication_receipt formal_output_mode mismatch",
    )
    # REV-08a (ZR-705): mode/state consistency — a draft-marked receipt must
    # carry the empty gate set; a downgraded formal receipt (formal_output_mode
    # flipped to "draft" while gate_ids stay non-empty, receipt rehashed) would
    # otherwise pass the checks above.  Reject the inconsistency.
    if receipt.get("formal_output_mode") == "draft":
        require(
            not receipt.get("gate_ids"),
            "publication_receipt draft mode must have empty gate_ids",
        )
    require(
        receipt.get("freeform_override_allowed") is False,
        "publication_receipt freeform_override_allowed must be false",
    )
    require(
        receipt.get("receipt_sha256") == _receipt_sha256(receipt),
        "publication_receipt receipt_sha256 mismatch",
    )
