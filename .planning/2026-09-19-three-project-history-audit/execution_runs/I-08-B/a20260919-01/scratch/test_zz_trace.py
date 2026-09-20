"""Trace the exact identity mismatch inside signed_record()."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import attestation_protocol as ap  # noqa: E402
from test_attestation_provider_protocol import (  # noqa: E402
    FakeProviderHarness,
    ISSUER,
    _utc,
)


class TraceTests(FakeProviderHarness):
    def test_trace(self) -> None:
        self.install_valid_domain()
        self.use_fake_provider()
        print("HARNESS FINGERPRINT :", self.fingerprint)
        print("ENV KEY SET         :", bool(__import__("os").environ.get("I08B_FAKE_KEY_HEX")))
        request = self.make_request()
        result = self.raw_call(request)
        print("CALL CODE           :", result.code, result.detail)
        response = result.response or {}
        print("PROVIDER FINGERPRINT:", response.get("key_fingerprint"))
        domain = ap.load_trust_domain()
        print("DOMAIN KEYS         :", sorted(domain))
        payload = ap.response_to_payload(response, request, gate_ids=tuple(request["gate_ids"]))
        print("PAYLOAD FINGERPRINT :", payload["key_fingerprint"])
        print("ISSUER              :", payload["issuer"], "|", ISSUER)


if __name__ == "__main__":
    unittest.main()
