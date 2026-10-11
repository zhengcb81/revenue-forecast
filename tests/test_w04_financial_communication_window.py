"""Typed financial boundaries; synthetic native scope vectors, no acquisitions."""
from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from research.communication_scope import analyze_communication_scope  # noqa: E402
from contracts.evidence import ForecastInputError  # noqa: E402


def source(kind: str, published: str | None) -> dict:
    return {"source_type": "regulatory_filing", "published_date": published,
            "company_wiki_trace": {"source_manifest": {"document_kind": kind}}}


def record(start: str = "2026-08-29") -> dict:
    return {"category": "material_announcements_since_last_filing", "source_ids": [],
            "checked_scope": {"schema_version": "management-communication-scope/1",
                "category": "material_announcements_since_last_filing", "start_date": start,
                "end_date": "2026-10-08", "coverage_complete": True, "items": []}}


class FinancialCommunicationWindowTests(unittest.TestCase):
    def test_prospectus_variants_do_not_move_financial_boundary(self) -> None:
        for kind in ("prospectus", "equity_offering_prospectus", "convertible_bond_prospectus"):
            with self.subTest(kind=kind):
                result = analyze_communication_scope(record(), {
                    "h1": source("semi_annual_report", "2026-08-29"),
                    "offering": source(kind, "2026-09-30")}, "2026-10-08")
                self.assertTrue(result["coverage_complete"])
                self.assertEqual(result["start_date"], "2026-08-29")

    def test_false_shortened_boundary_still_rejected(self) -> None:
        with self.assertRaises(ForecastInputError):
            analyze_communication_scope(record("2026-09-30"), {
                "h1": source("semi_annual_report", "2026-08-29"),
                "offering": source("prospectus", "2026-09-30")}, "2026-10-08")

    def test_annual_and_quarterly_are_valid_financial_boundaries(self) -> None:
        for kind in ("annual_report", "quarterly_report"):
            with self.subTest(kind=kind):
                result = analyze_communication_scope(record(), {"financial": source(kind, "2026-08-29")}, "2026-10-08")
                self.assertTrue(result["coverage_complete"])

    def test_future_financial_is_not_an_asof_boundary(self) -> None:
        result = analyze_communication_scope(record(), {
            "h1": source("semi_annual_report", "2026-08-29"),
            "future": source("quarterly_report", "2026-10-20")}, "2026-10-08")
        self.assertTrue(result["coverage_complete"])

    def test_nonfinancial_only_does_not_claim_known_financial_boundary(self) -> None:
        result = analyze_communication_scope(record("2026-09-30"), {
            "offering": source("prospectus", "2026-09-30")}, "2026-10-08")
        self.assertFalse(result["coverage_complete"])
        self.assertEqual(result["reason"], "financial_filing_anchor_unavailable")

    def test_annual_category_does_not_accept_other_regulatory_kinds(self) -> None:
        for kind in ("prospectus", "semi_annual_report", "quarterly_report"):
            with self.subTest(kind=kind):
                r = record()
                r["category"] = "latest_annual_filing"
                scope = r["checked_scope"]
                scope["category"] = r["category"]
                scope["items"] = [{"item_ref": "read", "source_id": "x", "content_role": "business_original", "selected": True, "read": True}]
                r["source_ids"] = ["x"]
                result = analyze_communication_scope(r, {"x": source(kind, "2026-08-29")}, "2026-10-08")
                self.assertFalse(result["coverage_complete"])
                self.assertEqual(result["reason"], "source_category_not_supported")

    def test_actual_annual_category_remains_valid(self) -> None:
        r = record()
        r["category"] = "latest_annual_filing"
        r["checked_scope"]["category"] = r["category"]
        r["checked_scope"]["items"] = [{"item_ref": "read", "source_id": "x", "content_role": "business_original", "selected": True, "read": True}]
        r["source_ids"] = ["x"]
        self.assertTrue(analyze_communication_scope(r, {"x": source("annual_report", "2026-08-29")}, "2026-10-08")["coverage_complete"])

    def test_legacy_source_without_typed_manifest_retains_contract(self) -> None:
        legacy = {"source_type": "exchange_filing", "published_date": "2026-08-29"}
        self.assertTrue(analyze_communication_scope(record(), {"legacy": legacy}, "2026-10-08")["coverage_complete"])


class NullablePublicationScopeTests(unittest.TestCase):
    def test_unknown_financial_publication_is_diagnostic(self) -> None:
        result = analyze_communication_scope(record(), {"financial": source("annual_report", None)}, "2026-10-08")
        self.assertFalse(result["coverage_complete"])
        self.assertEqual(result["reason"], "financial_filing_anchor_publication_unknown")

    def test_unknown_financial_does_not_certify_latest_known_anchor(self) -> None:
        result = analyze_communication_scope(record(), {
            "known": source("semi_annual_report", "2026-08-29"),
            "unknown": source("annual_report", None)}, "2026-10-08")
        self.assertFalse(result["coverage_complete"])
        self.assertEqual(result["reason"], "financial_filing_anchor_publication_unknown")

    def test_unknown_nonfinancial_publication_does_not_affect_anchor(self) -> None:
        result = analyze_communication_scope(record(), {
            "known": source("semi_annual_report", "2026-08-29"),
            "unknown": source("prospectus", None)}, "2026-10-08")
        self.assertTrue(result["coverage_complete"])

    def test_read_publication_unknown_does_not_use_discovery_clock(self) -> None:
        r = record()
        r["category"] = "latest_annual_filing"
        r["source_ids"] = ["x"]
        scope = r["checked_scope"]
        scope["category"] = r["category"]
        scope["items"] = [{"item_ref": "read", "source_id": "x", "published_date": "2026-08-29",
                           "content_role": "business_original", "selected": True, "read": True}]
        original = source("annual_report", None)
        original["availability_evidence"] = {"available_by": "2026-08-29"}
        result = analyze_communication_scope(r, {"x": original}, "2026-10-08")
        self.assertFalse(result["coverage_complete"])
        self.assertEqual(result["reason"], "source_publication_unknown")
        self.assertEqual(result["read_source_ids"], ["x"])
        self.assertIsNone(original["published_date"])

    def test_boundary_only_with_unknown_read_is_diagnostic(self) -> None:
        r = record()
        r["source_ids"] = ["known", "unknown"]
        r["checked_scope"]["items"] = [
            {"item_ref": sid, "source_id": sid, "content_role": "business_original", "selected": True, "read": True}
            for sid in r["source_ids"]]
        result = analyze_communication_scope(r, {
            "known": source("semi_annual_report", "2026-08-29"),
            "unknown": {"source_type": "company_release", "published_date": None}}, "2026-10-08")
        self.assertFalse(result["coverage_complete"])
        self.assertEqual(result["reason"], "source_publication_unknown")

    def test_malformed_known_date_still_rejected(self) -> None:
        with self.assertRaises(ForecastInputError):
            analyze_communication_scope(record(), {"financial": source("annual_report", "not-a-date")}, "2026-10-08")

    def test_native_verified_capture_with_null_publication_is_consumable(self) -> None:
        import runpy
        from datetime import date
        from revenue_core import validate_sources
        fixture = runpy.run_path(str(ROOT / "tests/test_company_wiki_source_v2.py"))
        ref, receipt, manifest = fixture["_inputs"]()
        manifest["published_date"] = None
        receipt["schema_version"] = "2.2"
        receipt["availability_evidence"] = {
            "schema_version": "source-availability-evidence/1", "source_sha256": ref["content_sha256"],
            "available_by": "2026-02-20", "basis": "prior_verified_capture",
            "evidence_ref": "urn:test:synthetic-prior-capture", "locator": "receipt:synthetic-valid-raw"}
        native = fixture["_build"](ref, receipt, manifest)
        validated = validate_sources({"sources": [native]}, date(2026, 9, 27), require_capture=True)
        self.assertIn(native["source_id"], validated)
        r = record("2026-02-20")
        r["checked_scope"]["end_date"] = "2026-09-27"
        result = analyze_communication_scope(r, validated, "2026-09-27")
        self.assertFalse(result["coverage_complete"])
        self.assertEqual(result["reason"], "financial_filing_anchor_publication_unknown")
        self.assertIsNone(native["published_date"])
