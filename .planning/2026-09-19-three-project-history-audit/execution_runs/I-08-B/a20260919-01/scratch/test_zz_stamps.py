"""Print the exact stamps T-N29 sees, inside the real test class."""

from __future__ import annotations

import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import attestation_protocol as ap  # noqa: E402
from test_attestation_provider_protocol import (  # noqa: E402
    FakeProviderHarness,
    _clock,
)


class DiagStamps(FakeProviderHarness):
    def test_stamps(self) -> None:
        t0 = time.monotonic()
        stamp = _clock(datetime.now(timezone.utc))
        issued = stamp(-600)
        expires = stamp(-500)
        t1 = time.monotonic()
        print("STAMP BUILD SECONDS:", round(t1 - t0, 3))
        print("ISSUED  :", issued)
        print("EXPIRES :", expires)
        request, payload = self._payload_for(issued_at=issued, expires_at=expires)
        print("PAYLOAD issued :", payload["issued_at"])
        print("PAYLOAD expires:", payload["expires_at"])
        print("PAYLOAD signed :", payload["signed_at"])
        print("REQUEST issued :", request["issued_at"])
        print("REQUEST expires:", request["expires_at"])
        print("EXPECTED signed:", stamp(-599))
        signed = ap.parse_utc(payload["signed_at"], "signed_at")
        print("SIGNED > EXPIRES:", signed > ap.parse_utc(payload["expires_at"], "expires_at"))
        try:
            ap.validate_payload(payload)
            print("VALIDATE: NOERROR")
        except ap.AttestationError as exc:
            print("VALIDATE:", exc.code)


if __name__ == "__main__":
    unittest.main()
