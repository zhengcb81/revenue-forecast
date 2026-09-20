"""Reproduce the batch-only E16 in the three protocol cases."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import attestation_protocol as ap  # noqa: E402
from test_attestation_provider_protocol import (  # noqa: E402
    ProviderPositiveTests,
    ReplayTests,
    _artifact,
)


class DiagBatch(ProviderPositiveTests):
    def test_diag_o3(self) -> None:
        request = self.make_request(issued_at=self.at(0), expires_at=self.at(100))
        self.install_valid_domain()
        record = self.signed_record(request, signed_at_offset=1)
        artifact = _artifact(record)
        print("ARTIFACT      :", json.dumps(artifact, sort_keys=True))
        print("record ph     :", record["payload_sha256"])
        print("recomputed ph :", ap.payload_sha256(artifact))
        print("findings      :", ap.verify_publication_attestation(artifact))
        print("env_max_window:", __import__("os").environ.get("REVENUE_ATTESTATION_MAX_WINDOW_SECONDS"))


class DiagBatchReplay(ReplayTests):
    def test_diag_tr3(self) -> None:
        artifact = _artifact(self.record)
        print("replay record ph:", self.record["payload_sha256"])
        print("replay computed :", ap.payload_sha256(artifact))
        print("replay findings :", ap.verify_publication_attestation(artifact))


if __name__ == "__main__":
    unittest.main()
