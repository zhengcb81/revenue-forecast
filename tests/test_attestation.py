"""Attestation capability gate and host-receipt signature verification (R2)."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from contracts.evidence import (  # noqa: E402
    ForecastInputError,
    build_host_receipt,
    validate_host_receipt,
)
from revenue_core import (  # noqa: E402
    attestation_capability,
    canonical_sha256,
    run_forecast,
)
from test_recognition_bridge import forecast_document  # noqa: E402


def _signed_host_receipt(public_key_bytes: bytes, private_key) -> dict:
    receipt = build_host_receipt(
        issuer="user@host",
        environment="win11",
        tool_name="filing_fetch",
        action="download",
        event_sha256="a" * 64,
        timestamp="2026-08-08T00:00:00Z",
    )
    fingerprint = hashlib.sha256(public_key_bytes).hexdigest()[:32]
    message = canonical_sha256(receipt).encode("ascii")
    return {**receipt, "signature": private_key.sign(message).hex(),
            "public_key_fingerprint": fingerprint}


class AttestationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env: dict[str, str | None] = {}
        for name in (
            "REVENUE_ATTESTATION_PROVIDER",
            "REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS",
        ):
            self._env[name] = os.environ.get(name)
            os.environ.pop(name, None)
        self._temporary = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        for name, value in self._env.items():
            os.environ.pop(name, None)
            if value is not None:
                os.environ[name] = value
        self._temporary.cleanup()

    def test_no_provider_means_unattested_publication(self) -> None:
        result = run_forecast(forecast_document())
        self.assertEqual(
            result["publication_receipt"]["attestation_status"], "unattested"
        )
        self.assertFalse(attestation_capability())

    def test_configured_provider_means_host_signed_publication(self) -> None:
        os.environ["REVENUE_ATTESTATION_PROVIDER"] = sys.executable
        self.assertTrue(attestation_capability())
        result = run_forecast(forecast_document())
        self.assertEqual(
            result["publication_receipt"]["attestation_status"], "host_signed"
        )

    def _whitelist(self, public_key_bytes: bytes) -> Path:
        path = Path(self._temporary.name) / "trusted_keys.json"
        path.write_text(
            json.dumps(
                {
                    "public_keys": [
                        {
                            "name": "test-signer",
                            "public_key": base64.b64encode(public_key_bytes).decode("ascii"),
                            "fingerprint": hashlib.sha256(public_key_bytes).hexdigest()[:32],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return path

    def _public_bytes(self, private_key):
        from cryptography.hazmat.primitives import serialization

        return private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def test_signed_host_receipt_verifies_against_whitelist(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        private_key = Ed25519PrivateKey.generate()
        public_bytes = self._public_bytes(private_key)
        os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(
            self._whitelist(public_bytes)
        )
        receipt = _signed_host_receipt(public_bytes, private_key)
        validate_host_receipt(receipt)

    def test_forged_signature_is_rejected(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        attacker = Ed25519PrivateKey.generate()
        victim = Ed25519PrivateKey.generate()
        victim_public = self._public_bytes(victim)
        os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(
            self._whitelist(victim_public)
        )
        # Signed by an attacker whose key is NOT in the whitelist: the
        # fingerprint (attacker's key) is untrusted.
        attacker_public = self._public_bytes(attacker)
        receipt = _signed_host_receipt(attacker_public, attacker)
        with self.assertRaisesRegex(ForecastInputError, "not trusted"):
            validate_host_receipt(receipt)

    def test_signature_over_stale_event_is_rejected(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        private_key = Ed25519PrivateKey.generate()
        public_bytes = self._public_bytes(private_key)
        os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(
            self._whitelist(public_bytes)
        )
        receipt = _signed_host_receipt(public_bytes, private_key)
        # Event changed after signing; the attacker re-signs the receipt hash
        # so the receipt stays self-consistent — only the Ed25519 signature is
        # now stale, and that alone must reject the receipt.
        receipt["event_sha256"] = "b" * 64
        receipt["receipt_sha256"] = canonical_sha256(
            {
                key: value
                for key, value in receipt.items()
                if key != "receipt_sha256"
                and key not in ("signature", "public_key_fingerprint")
            }
        )
        with self.assertRaisesRegex(ForecastInputError, "signature verification failed"):
            validate_host_receipt(receipt)

    def test_no_whitelist_rejects_any_signature(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        private_key = Ed25519PrivateKey.generate()
        public_bytes = self._public_bytes(private_key)
        # No whitelist file configured at all -> no trusted signer -> reject.
        receipt = _signed_host_receipt(public_bytes, private_key)
        with self.assertRaisesRegex(ForecastInputError, "not trusted"):
            validate_host_receipt(receipt)

    def test_unsigned_host_receipt_still_validates(self) -> None:
        receipt = build_host_receipt(
            issuer="user@host",
            environment="win11",
            tool_name="filing_fetch",
            action="download",
            event_sha256="a" * 64,
            timestamp="2026-08-08T00:00:00Z",
        )
        validate_host_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
