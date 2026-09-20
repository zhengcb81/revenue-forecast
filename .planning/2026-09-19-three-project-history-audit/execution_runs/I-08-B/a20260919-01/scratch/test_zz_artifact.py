"""Diagnose the remaining harness E16 by comparing both projections."""

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
    _artifact,
)


class DiagArtifact(FakeProviderHarness):
    def test_compare(self) -> None:
        self.install_valid_domain()
        self.use_fake_provider()
        request = self.make_request()
        record = self.signed_record(request)
        artifact = _artifact(record)
        print("RECORD commitment :", record["payload_sha256"])
        print("ARTIFACT recomputed:", ap.payload_sha256(artifact))
        projection = {
            k: v
            for k, v in artifact.items()
            if k not in ("result_sha256", "publication_receipt", "publication_attestation", "payload_sha256")
        }
        print("ARTIFACT projection keys:", sorted(projection))
        print("ARTIFACT projection json:", json.dumps(projection, sort_keys=True)[:400])
        # now the same projection with input_sha256 REMOVED
        without = {k: v for k, v in projection.items() if k != "input_sha256"}
        print("without input_sha256      :", ap.payload_sha256(without))
        print("findings                  :", ap.verify_publication_attestation(artifact))


if __name__ == "__main__":
    unittest.main()
