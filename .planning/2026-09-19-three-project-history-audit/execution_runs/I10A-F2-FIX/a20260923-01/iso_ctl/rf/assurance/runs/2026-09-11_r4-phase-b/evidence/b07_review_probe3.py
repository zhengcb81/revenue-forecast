"""B.VR (B07) probe 3: what the CONSUMER sees in the drift case
(the S-10 rule-2 row served when no candidate's bytes verify).

Builds a verified catalog, edits the indexed file's bytes, resolves again and
renders the consumer-facing envelope + handle fields.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path(__file__).resolve().parents[4]
CURRENT = REVENUE.parent / "company-wiki"
sys.path.insert(0, str(CURRENT / "src"))


def main() -> int:
    from company_wiki.source_catalog import CatalogConfig, SourceCatalog
    from company_wiki.source_catalog.models import RootSpec
    from company_wiki.source_catalog.resolver import (
        SourceRequest,
        SourceResolver,
        build_resolution_envelope,
    )

    tmp = Path(tempfile.mkdtemp(prefix="b07_review_drift2_"))
    root = tmp / "companies"
    target = root / "Acme" / "raw" / "financial_reports" / "annual" / "2025.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    original = b"%PDF-1.4 b07-review-original-version"
    target.write_bytes(original)
    (target.parent / "2025.pdf.source.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "canonical_entity_id": "ent-acme",
                "display_name": "Acme",
                "market": "US",
                "security_id": "ACME",
                "source_title": "Acme 2025 Annual Report",
                "document_kind": "annual_report",
                "fiscal_year": 2025,
                "period_end": "2025-12-31",
                "filing_date": "2026-02-20",
                "form_type": "10-K",
                "provider": "sec",
                "provider_document_id": "doc-1",
                "source_url": "https://sec.gov/x/2025",
                "content_sha256": hashlib.sha256(original).hexdigest(),
                "retrieved_at": "2026-02-21T00:00:00Z",
                "collector_name": "sec_edgar",
                "collector_version": "1.0",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    catalog = SourceCatalog(
        CatalogConfig(
            project_root=tmp,
            catalog_dir=tmp / ".source_catalog",
            reusable_root_kinds=("company_raw",),
            roots=(
                RootSpec(
                    "company_raw",
                    root,
                    "company_raw",
                    priority=10,
                    adapter_id="company_raw_v1",
                    read_only=False,
                    reusable_for_filing=True,
                    canonical_write_target="companies",
                ),
            ),
        )
    )
    catalog.scan()
    request = SourceRequest(
        entity="Acme",
        market="US",
        security_id="ACME",
        document_kind="annual_report",
        form_type="10-K",
        fiscal_year=2025,
        provider="sec",
        provider_document_id="doc-1",
        as_of_date="2026-08-10",
        mode="exact",
    )
    resolver = SourceResolver(catalog)
    target.write_bytes(b"%PDF-1.4 DIFFERENT-LATER-BYTES-that-are-not-the-version")
    resolution = resolver.resolve(request)
    envelope = build_resolution_envelope(resolution, store=catalog.reader)
    handle = resolution.matches[0]
    report = {
        "resolution_status": resolution.status.value,
        "handle_schema_version": handle.schema_version,
        "handle_capture_ready": handle.capture_ready,
        "handle_missing_capture_fields": list(handle.missing_capture_fields),
        "handle_content_sha256": handle.content_sha256,
        "bytes_on_disk_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "handle_sha_equals_bytes_on_disk": (
            handle.content_sha256 == hashlib.sha256(target.read_bytes()).hexdigest()
        ),
        "envelope_outcome": envelope.outcome,
        "envelope_source_sha256": envelope.source_sha256,
        "envelope_qualification": envelope.qualification,
        "envelope_bundle_status": envelope.bundle_status,
        "resolution_dict_matches_sha": resolution.to_dict()["matches"][0]["content_sha256"],
    }
    out = RUN / "evidence" / "b07_review_probe3.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("wrote", out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
