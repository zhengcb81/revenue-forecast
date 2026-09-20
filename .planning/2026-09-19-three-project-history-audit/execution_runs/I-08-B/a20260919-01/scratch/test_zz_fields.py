"""Print the payload/record field sets used by the harness."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import attestation_protocol as ap  # noqa: E402
from test_attestation_provider_protocol import (  # noqa: E402
    ATTESTATION_RECORD_FIELDS,
    FakeProviderHarness,
    GATES,
)


class DiagFields(FakeProviderHarness):
    def test_fields(self) -> None:
        self.install_valid_domain()
        self.use_fake_provider()
        request = self.make_request()
        _, response, payload, _ = self.signed_sides(request)
        print("PAYLOAD KEYS      :", sorted(payload))
        print("RECORD EXPECTED   :", sorted(ATTESTATION_RECORD_FIELDS))
        print("PROTOCOL CONSTANT :", sorted(ap.ATTESTATION_RECORD_FIELDS))
        record = self.record_from(payload, response["signature"])
        print("RECORD ACTUAL     :", sorted(record))
        print("GATES             :", GATES)


if __name__ == "__main__":
    unittest.main()
