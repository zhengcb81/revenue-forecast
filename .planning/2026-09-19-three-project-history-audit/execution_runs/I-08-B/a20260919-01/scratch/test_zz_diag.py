"""Temporary diagnosis: dump exactly what the fake provider saw and signed
during the real pytest run, next to what the host reconstructs."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_attestation_provider_protocol import (  # noqa: E402
    FakeProviderHarness,
    ISSUER,
)


class DiagTests(FakeProviderHarness):
    def test_dump(self) -> None:
        import attestation_protocol as ap

        self.install_valid_domain()
        self.use_fake_provider()
        request = self.make_request()
        result = self.raw_call(request)
        print("CALL_RC", result.returncode, "CODE", result.code, "DETAIL", result.detail)
        entries = [
            json.loads(line)
            for line in Path(self.provider_log).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        for index, entry in enumerate(entries):
            print("LOG", index, json.dumps(entry, sort_keys=True)[:2000])
        response = ap.validate_response(result.response, request)
        payload = ap.response_to_payload(response, request, gate_ids=("output_recomputation",))
        print("HOST_PAYLOAD", json.dumps(payload, sort_keys=True))
        print("REQUEST", json.dumps(request, sort_keys=True))
        outcome = ap.build_attestation_record(
            response, request, gate_ids=("output_recomputation",), w_enforced=True,
            domain=ap.load_trust_domain(),
        )
        print("RECORD_OK", outcome["signed_at"])


if __name__ == "__main__":
    unittest.main()
