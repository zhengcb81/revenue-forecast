"""Diagnose I08B_FAKE_SIGNED_AT handling inside the real negative-test class."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import attestation_protocol as ap  # noqa: E402
from test_attestation_provider_protocol import ProviderNegativeTests  # noqa: E402


class DiagSignedAt(ProviderNegativeTests):
    def test_diag(self) -> None:
        self.install_valid_domain()
        print("before staging:", os.environ.get("I08B_FAKE_SIGNED_AT"))
        self.use_fake_provider(signed_at=self.at(-599))
        print("after staging :", os.environ.get("I08B_FAKE_SIGNED_AT"))
        request, payload = self.payload_for(
            issued_at=self.at(-600), expires_at=self.at(-500)
        )
        print("after payload :", os.environ.get("I08B_FAKE_SIGNED_AT"))
        print("payload issued:", payload["issued_at"])
        print("payload exp   :", payload["expires_at"])
        print("payload signed:", payload["signed_at"])
        print("expect signed :", self.at(-599))


if __name__ == "__main__":
    unittest.main()
