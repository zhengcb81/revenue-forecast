"""File 2/3: refactor validate_publication_attestation (CC 16) into top-level helpers (cap 10).

Inserts four check-group helpers immediately BEFORE validate_publication_attestation and
replaces its body's check sequence with helper calls; payload-binding + signature-verify
tail stays verbatim in the main function. All require() message strings and their ORDER
are preserved byte-for-byte.
"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path(sys.argv[1])
text = TARGET.read_text(encoding="utf-8")
anchor = "def validate_publication_attestation("
idx = text.index(anchor)
end_anchor = "def publication_attestation_request("
end = text.index(end_anchor)
head = text[:idx]
tail = text[end:]

NEW = '''def _require_attestation_field_set(record: dict) -> None:
    """Closed field set + schema/domain/algorithm constants (B1 / REM-01)."""
    require(
        isinstance(record, dict),
        "attestation_missing_record: publication_attestation must be an object",
    )
    missing = PUBLICATION_ATTESTATION_FIELDS - set(record)
    extra = set(record) - PUBLICATION_ATTESTATION_FIELDS
    require(
        not missing and not extra,
        "attestation_payload_fields: publication_attestation field set mismatch "
        f"(missing={sorted(missing)}, extra={sorted(extra)})",
    )
    require(
        record["attestation_payload_schema_version"]
        == PUBLICATION_ATTESTATION_SCHEMA_VERSION,
        "attestation_payload_fields: publication_attestation schema version mismatch",
    )
    require(
        record["domain_separator"] == PUBLICATION_ATTESTATION_DOMAIN,
        "attestation_domain_mismatch: publication_attestation domain_separator "
        f"must be {PUBLICATION_ATTESTATION_DOMAIN!r}",
    )
    require(
        record["algorithm"] == PUBLICATION_ATTESTATION_ALGORITHM,
        "attestation_payload_fields: publication_attestation algorithm must be "
        f"{PUBLICATION_ATTESTATION_ALGORITHM!r}",
    )


def _require_attestation_identity_fields(record: dict) -> None:
    """Issuer and key_id must be non-empty strings."""
    for field in ("issuer", "key_id"):
        require(
            isinstance(record[field], str) and record[field].strip(),
            f"attestation_payload_fields: publication_attestation.{field} is required",
        )


def _require_attestation_hex_fields(record: dict) -> None:
    """Fingerprint (32 hex) and request_id (64 hex) format checks."""
    require(
        isinstance(record["fingerprint"], str)
        and _HEX32.fullmatch(record["fingerprint"]) is not None,
        "attestation_payload_fields: publication_attestation.fingerprint must be "
        "32 lowercase hex",
    )
    require(
        isinstance(record["request_id"], str)
        and _HEX64.fullmatch(record["request_id"]) is not None,
        "attestation_payload_fields: publication_attestation.request_id must be "
        "64 lowercase hex",
    )


def _require_attestation_signature_fields(record: dict) -> None:
    """signed_at format + signature presence/128-hex checks (E12/E13)."""
    require(
        isinstance(record["signed_at"], str)
        and _RFC3339_Z.fullmatch(record["signed_at"]) is not None,
        "attestation_payload_fields: publication_attestation.signed_at must be "
        "RFC3339 UTC 'Z'",
    )
    require(
        isinstance(record["signature"], str) and record["signature"],
        "attestation_missing_signature: publication_attestation.signature is "
        "required (E12)",
    )
    require(
        _HEX128.fullmatch(record["signature"]) is not None,
        "attestation_malformed_signature: publication_attestation.signature must "
        "be 128 lowercase hex (E13)",
    )


def validate_publication_attestation(
    result: dict[str, Any], receipt: dict[str, Any]
) -> None:
    """Validate the ``publication_attestation`` binding record (B1 / REM-01).

    Raises with the I-08-A code spelling in the message so a caller can classify
    the rejection without parsing prose:

    * ``attestation_missing_record`` (E27) — ``host_signed`` with no record.
    * ``attestation_missing_signature`` (E12) / ``attestation_malformed_signature``
      (E13) — absent or malformed signature.
    * ``attestation_domain_mismatch`` (E17) — wrong domain separator.
    * ``attestation_payload_hash_mismatch`` (E16) — the record does not bind the
      live payload / result / receipt.
    * ``provider_key_untrusted`` (E20) / ``issuer_key_binding_mismatch`` (E21) —
      trust-domain failures.
    * ``attestation_signature_invalid`` (E14) — Ed25519 verification failed.

    Ratchet refactor (RF-RATCHET-REST-B): the field/format checks live in the
    top-level helpers above; check order, messages, exceptions and the
    verification tail are byte-identical to the promotion payload this file was
    promoted as (bc2bb4a3...).
    """
    record = receipt.get("publication_attestation")
    claims_signed = receipt.get("attestation_status") == "host_signed"
    if record is None:
        if claims_signed:
            # I-08-A §6.2 G3b: a package that CLAIMS a signature and cannot
            # produce the record is rejected.  Never silently downgraded.
            raise ForecastInputError(
                "attestation_missing_record: publication_receipt claims "
                "attestation_status='host_signed' but carries no "
                "publication_attestation record (E27)"
            )
        return
    _require_attestation_field_set(record)
    _require_attestation_identity_fields(record)
    _require_attestation_hex_fields(record)
    _require_attestation_signature_fields(record)
    # Binding to the live artifact: the record must describe THIS publication.
    # The record binds the two fields that are knowable BEFORE the receipt
    # exists: the payload digest (everything except `result_sha256` and
    # `publication_receipt`) and the one-shot request id.  `result_sha256` and
    # the receipt's own hash are deliberately NOT record fields — a receipt
    # cannot contain its own hash (no fixpoint), and `result_sha256` covers the
    # receipt, which contains this record.  Nothing is left unbound: the
    # signature is over `request`, and `request` is reconstructed from the
    # record's bound fields, so any change to a bound value breaks the signature.
    require(
        record["payload_sha256"] == receipt.get("validated_payload_sha256"),
        "attestation_payload_hash_mismatch: publication_attestation.payload_sha256 "
        "does not match the receipt's validated payload (E16)",
    )
    # The signed message is rebuilt from the record's fields and the record's
    # signature is verified against it, so a record cannot be assembled from a
    # signature issued for some other request.
    request = publication_attestation_request(
        request_id=record["request_id"],
        payload_sha256=record["payload_sha256"],
        result_sha256=SIGNED_RESULT_SHA256_SENTINEL,
    )
    message = canonical_sha256(request).encode("ascii")
    verify_ed25519_signature(record["fingerprint"], record["signature"], message)


'''

TARGET.write_text(head + NEW + tail, encoding="utf-8", newline="\n")
print(f"spliced chars {idx}..{end}; new size {TARGET.stat().st_size} B")
