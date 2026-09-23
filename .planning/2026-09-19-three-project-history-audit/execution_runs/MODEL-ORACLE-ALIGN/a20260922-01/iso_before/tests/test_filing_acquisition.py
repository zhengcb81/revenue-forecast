"""Legacy filing data contracts survive as fixtures; the download owner is gone (R3).

The old ``scripts/filing_acquisition.py`` (AcquisitionManager / AdapterRegistry /
CanonicalSourceWriter / resolve_filing download paths) was removed in R3 —
filing acquisition has exactly one owner, ``filing_fetch_client.py``, which
delegates to the standalone filing-fetch skill.  Only the pure data
constructors remain, as ``tests/fixtures/legacy_filing_data.py``.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests" / "fixtures"))

from legacy_filing_data import (  # noqa: E402
    DownloadCandidate,
    DownloadReceipt,
    FilingAcquisitionError,
    SourceRequest,
    _redact,
)


class LegacyDataContractTests(unittest.TestCase):
    def test_source_request_validates_market_and_fiscal_year(self) -> None:
        request = SourceRequest(
            entity="Example Corp",
            document_kind="annual_report",
            as_of_date="2026-03-31",
            market="CN",
            fiscal_year=2025,
        )
        self.assertEqual(request.market, "CN")
        self.assertEqual(request.document_kind, "annual_report")
        self.assertTrue(request.request_id.startswith("urn:revenue-forecast:"))
        with self.assertRaisesRegex(FilingAcquisitionError, "market"):
            SourceRequest(
                entity="Example Corp",
                document_kind="annual_report",
                as_of_date="2026-03-31",
                market="XX",
            )
        with self.assertRaisesRegex(FilingAcquisitionError, "fiscal_year"):
            SourceRequest(
                entity="Example Corp",
                document_kind="annual_report",
                as_of_date="2026-03-31",
                fiscal_year=1800,
            )

    def test_download_candidate_validates_https_and_market(self) -> None:
        candidate = DownloadCandidate(
            candidate_id="CN:2025",
            provider="cninfo",
            provider_document_id="CN-2025",
            market="cn",
            entity="Example Corp",
            title="Annual report",
            source_url="https://example.com/report.pdf",
            document_kind="annual_report",
            filing_date="2026-03-31",
            fiscal_year=2025,
        )
        self.assertEqual(candidate.market, "CN")
        self.assertEqual(candidate.provider, "cninfo")
        with self.assertRaisesRegex(FilingAcquisitionError, "HTTPS"):
            DownloadCandidate(
                candidate_id="CN:2025",
                provider="cninfo",
                provider_document_id="CN-2025",
                market="CN",
                entity="Example Corp",
                title="Annual report",
                source_url="http://example.com/report.pdf",
                document_kind="annual_report",
                filing_date="2026-03-31",
                fiscal_year=2025,
            )

    def test_download_receipt_validates_hash_and_version(self) -> None:
        receipt = DownloadReceipt(
            candidate_id="CN:2025",
            provider="cninfo",
            provider_document_id="CN-2025",
            source_url="https://example.com/report.pdf",
            staged_path="C:/tmp/report.pdf",
            content_sha256="a" * 64,
            byte_size=1024,
            mime_type="application/pdf",
            retrieved_at="2026-08-08T00:00:00Z",
            http_status=200,
            adapter_name="cninfo-cli",
            adapter_version="1.2.3",
        )
        self.assertEqual(receipt.provider, "cninfo")
        with self.assertRaisesRegex(FilingAcquisitionError, "content_sha256"):
            DownloadReceipt(
                candidate_id="CN:2025",
                provider="cninfo",
                provider_document_id="CN-2025",
                source_url="https://example.com/report.pdf",
                staged_path="C:/tmp/report.pdf",
                content_sha256="not-a-hash",
                byte_size=1024,
                mime_type="application/pdf",
                retrieved_at="2026-08-08T00:00:00Z",
                http_status=200,
                adapter_name="cninfo-cli",
                adapter_version="1.2.3",
            )

    def test_error_redaction_hides_common_secret_forms(self) -> None:
        redacted = _redact("Authorization: Bearer-secret API_KEY=abc123 token=xyz987")
        self.assertNotIn("Bearer-secret", redacted)
        self.assertNotIn("abc123", redacted)
        self.assertNotIn("xyz987", redacted)
        self.assertGreaterEqual(redacted.count("[REDACTED]"), 3)


class RemovedOwnerGuardTests(unittest.TestCase):
    def test_legacy_download_module_is_gone(self) -> None:
        # The second filing owner must not be importable.
        import importlib.util

        self.assertIsNone(
            importlib.util.find_spec("filing_acquisition"),
            "scripts/filing_acquisition.py must not exist (single owner R3)",
        )
        self.assertFalse((ROOT / "scripts" / "filing_acquisition.py").exists())

    def test_fixtures_module_has_no_download_owner_symbols(self) -> None:
        import legacy_filing_data

        for name in ("resolve_filing", "AcquisitionManager", "AdapterRegistry"):
            self.assertFalse(
                hasattr(legacy_filing_data, name),
                f"legacy fixtures must not export {name}",
            )


if __name__ == "__main__":
    unittest.main()
