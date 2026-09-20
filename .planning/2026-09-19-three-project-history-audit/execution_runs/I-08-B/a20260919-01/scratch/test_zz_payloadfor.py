"""Diagnose _payload_for with explicit expiry overrides."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_attestation_provider_protocol import (  # noqa: E402
    FakeProviderHarness,
    _utc,
)


class DiagPayloadFor(FakeProviderHarness):
    def test_payload_for(self) -> None:
        request, payload = self._payload_for(issued_at=_utc(-100), expires_at=_utc(-50))
        print("REQ   issued/expires:", request["issued_at"], request["expires_at"])
        print("PAY   issued/expires:", payload["issued_at"], payload["expires_at"])
        print("PAY   signed_at     :", payload["signed_at"])
        print("REQ   request_id    :", request["request_id"])
        print("PAY   request_id    :", payload["request_id"])


if __name__ == "__main__":
    unittest.main()
