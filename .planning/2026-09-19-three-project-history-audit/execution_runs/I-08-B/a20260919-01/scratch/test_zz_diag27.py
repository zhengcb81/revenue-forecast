"""Diagnose the T-N27 expiry case end to end."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import attestation_protocol as ap  # noqa: E402
from test_attestation_provider_protocol import FakeProviderHarness, GATES, _utc  # noqa: E402


class Diag27(FakeProviderHarness):
    def test_diag(self) -> None:
        self.install_valid_domain()
        self.use_fake_provider()
        request = self.make_request(issued_at=_utc(600), expires_at=_utc(900))
        print("REQ issued  :", request["issued_at"])
        print("REQ expires :", request["expires_at"])
        result = self.raw_call(request)
        print("CODE        :", result.code, result.detail)
        response = ap.validate_response(result.response, request)
        print("RESP signed :", response["signed_at"])
        payload = ap.response_to_payload(response, request, gate_ids=GATES)
        print("PAYLOAD     :", payload["issued_at"], payload["expires_at"], payload["signed_at"])
        try:
            ap.validate_payload(payload)
            print("VALIDATE    : NO ERROR")
        except ap.AttestationError as exc:
            print("VALIDATE    :", exc.code)


if __name__ == "__main__":
    unittest.main()
