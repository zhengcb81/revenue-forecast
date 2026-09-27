"""Revenue source/capture contracts built from a local acquisition handle."""

from __future__ import annotations

from datetime import date
import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


SKILL_ROOT = Path(__file__).resolve().parents[1]
import sys  # noqa: E402

sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from company_wiki_source import (  # noqa: E402
    CompanyWikiSourceError,
    build_revenue_source_record,
)
from revenue_core import validate_sources  # noqa: E402


class RevenueSourceRecordTests(unittest.TestCase):
    def _handle(self, root: Path) -> dict:
        source = root / "report.pdf"
        source.write_bytes(b"%PDF-1.7\nrevenue source bytes")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        return {
            "request_id": "urn:company-wiki:source-request:sha256:" + "1" * 64,
            "document_id": "urn:company-wiki:document:sha256:" + digest,
            "source_id": "urn:company-wiki:source:sha256:" + digest,
            "title": "ACME 2025 Annual Report",
            "published_date": "2026-03-20",
            "https_url": "https://www.sec.gov/Archives/edgar/data/1/report.htm",
            "canonical_location_id": "urn:company-wiki:location:sha256:" + "2" * 64,
            "canonical_path": str(source),
            "snapshot_sha256": digest,
            "retrieved_at": "2026-07-18T12:00:00Z",
            "provider": "sec",
            "provider_document_id": "0000000001-26-000001",
            "collector_name": "dayu-sec",
            "collector_version": "1.0.0",
            "capture_ready": True,
        }

    def test_source_record_passes_schema_34_capture_validation(self) -> None:
        with TemporaryDirectory() as temporary:
            source = build_revenue_source_record(
                self._handle(Path(temporary)),
                as_of_date="2026-07-18",
                source_type="regulatory_filing",
                publisher="U.S. Securities and Exchange Commission",
                page_or_section="Revenue note, page 42",
                prompt_injection_status="not_detected",
            )

        validated = validate_sources(
            {"sources": [source]},
            date.fromisoformat("2026-07-18"),
            require_capture=True,
        )
        self.assertEqual(
            validated[source["source_id"]]["capture"]["snapshot_sha256"],
            source["capture"]["snapshot_sha256"],
        )

    def test_tampered_local_source_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            handle = self._handle(Path(temporary))
            Path(handle["canonical_path"]).write_bytes(b"tampered")
            with self.assertRaisesRegex(CompanyWikiSourceError, "do not match"):
                build_revenue_source_record(
                    handle,
                    as_of_date="2026-07-18",
                    source_type="regulatory_filing",
                    publisher="SEC",
                    page_or_section="Revenue note",
                    prompt_injection_status="not_detected",
                )

    def test_capture_after_as_of_is_not_backdated(self) -> None:
        with TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(CompanyWikiSourceError, "outside"):
                build_revenue_source_record(
                    self._handle(Path(temporary)),
                    as_of_date="2026-07-17",
                    source_type="regulatory_filing",
                    publisher="SEC",
                    page_or_section="Revenue note",
                    prompt_injection_status="not_detected",
                )


if __name__ == "__main__":
    unittest.main()
