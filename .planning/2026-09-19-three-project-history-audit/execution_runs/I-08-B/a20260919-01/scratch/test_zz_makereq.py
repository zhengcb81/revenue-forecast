"""Diagnose make_request overrides directly."""

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


class DiagMakeRequest(FakeProviderHarness):
    def test_override(self) -> None:
        print("UTIL -100 :", _utc(-100))
        print("UTIL  -50 :", _utc(-50))
        request = self.make_request(issued_at=_utc(-100), expires_at=_utc(-50))
        print("REQ issued :", request["issued_at"])
        print("REQ expires:", request["expires_at"])
        plain = self.make_request()
        print("PLAIN issued :", plain["issued_at"])
        print("PLAIN expires:", plain["expires_at"])


if __name__ == "__main__":
    unittest.main()
