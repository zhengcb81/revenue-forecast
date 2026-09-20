"""Trace signed_record() internals directly via the harness method."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import attestation_protocol as ap  # noqa: E402
from test_attestation_provider_protocol import FakeProviderHarness  # noqa: E402


class Trace2Tests(FakeProviderHarness):
    def test_trace_signed_record(self) -> None:
        self.install_valid_domain()
        self.use_fake_provider()
        print("BEFORE  fingerprint:", self.fingerprint)
        print("BEFORE  provider   :", os.environ.get(ap.PROVIDER_ENV_VAR))
        print("BEFORE  argv       :", self.provider_argv())
        print("BEFORE  keyhex len :", len(os.environ.get("I08B_FAKE_KEY_HEX", "")))
        request = self.make_request()
        try:
            record = self.signed_record(request)
        except Exception as exc:  # noqa: BLE001
            print("SIGNED_RECORD RAISED:", type(exc).__name__, exc)
            print("AFTER-RUN fingerprint:", self.fingerprint)
            print("AFTER-RUN argv       :", self.provider_argv())
            print("AFTER-RUN domain     :", sorted(ap.load_trust_domain()))
            raise
        print("RECORD OK", sorted(record))


if __name__ == "__main__":
    unittest.main()
