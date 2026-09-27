"""Does a served handle in `latest_as_of` mode carry a period fact?

The B06 review's P1 (B-VR06-01) says a handle with no ``fiscal_year`` is labelled
``verified_input``, contradicting the author's own plan (period = fiscal_year AND
(period_end OR published_date)).  Making the code plan-conformant is only safe if
the mode where filing-fetch FORBIDS fiscal_year (``latest_as_of``) still yields a
period fact on the handle - otherwise every latest_as_of answer would turn
``blocked``.  This probe measures exactly that.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

REVENUE = Path(__file__).resolve().parents[4]
WIKI = REVENUE.parent / "company-wiki"
sys.path.insert(0, str(WIKI / "src"))

from company_wiki.source_catalog import CatalogConfig, SourceCatalog  # noqa: E402
from company_wiki.source_catalog.models import RootSpec  # noqa: E402
from company_wiki.source_catalog.resolver import (  # noqa: E402
    SourceRequest,
    SourceResolver,
    build_resolution_envelope,
)

BODY = b"%PDF-1.4 b06-period-probe"
DIGEST = hashlib.sha256(BODY).hexdigest()


def sidecar(**over) -> dict:
    payload = {
        "schema_version": "1.0", "canonical_entity_id": "ent-acme", "display_name": "Acme",
        "market": "US", "security_id": "ACME", "source_title": "Acme report",
        "document_kind": "annual_report", "fiscal_year": 2025, "period_end": "2025-12-31",
        "filing_date": "2026-02-20", "form_type": "10-K", "provider": "sec",
        "provider_document_id": "doc-1", "source_url": "https://sec.gov/x/2025",
        "content_sha256": DIGEST, "retrieved_at": "2026-02-21T00:00:00Z",
        "collector_name": "sec_edgar", "collector_version": "1.0",
    }
    payload.update(over)
    return payload


def build(tmp: Path, **over):
    root = tmp / "companies"
    target = root / "Acme" / "raw" / "financial_reports" / "annual"
    target.mkdir(parents=True, exist_ok=True)
    (target / "2025.pdf").write_bytes(BODY)
    (target / "2025.pdf.source.json").write_text(json.dumps(sidecar(**over)), encoding="utf-8")
    catalog = SourceCatalog(CatalogConfig(
        project_root=tmp, catalog_dir=tmp / ".source_catalog",
        reusable_root_kinds=("company_raw",), roots=(RootSpec(
            "company_raw", root, "company_raw", priority=10, adapter_id="company_raw_v1",
            read_only=False, reusable_for_filing=True, canonical_write_target="companies"),)))
    catalog.scan()
    return catalog


def show(label: str, catalog, request) -> None:
    resolution = SourceResolver(catalog).resolve(request)
    envelope = build_resolution_envelope(resolution, store=catalog.store, project_root=catalog.config.project_root)
    if not resolution.matches:
        print(f"{label}: no handle ({resolution.status}) trace={list(resolution.debug_trace)[:2]}")
        return
    handle = resolution.matches[0]
    print(f"{label}: fiscal_year={handle.fiscal_year!r} fiscal_period={handle.fiscal_period!r} "
          f"published_date={handle.published_date!r} missing={handle.missing_capture_fields} "
          f"qualification={envelope.qualification}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="b06-period-", ignore_cleanup_errors=True) as tmpdir:
        tmp = Path(tmpdir)
        # 1. exact mode, sidecar WITHOUT fiscal_year (but with filing_date)
        cat = build(tmp / "exact", fiscal_year=None)
        show("exact/no_fiscal_year        ", cat, SourceRequest(
            entity="Acme", market="US", security_id="ACME", document_kind="annual_report",
            form_type="10-K", fiscal_year=2025, provider="sec", provider_document_id="doc-1",
            as_of_date="2026-08-10", mode="exact"))
        cat.close()

        # 2. latest_as_of, sidecar WITHOUT fiscal_year
        cat = build(tmp / "latest", fiscal_year=None)
        show("latest_as_of/no_fiscal_year ", cat, SourceRequest(
            entity="Acme", market="US", security_id="ACME", document_kind="annual_report",
            provider="sec", provider_document_id="doc-1", as_of_date="2026-08-10",
            mode="latest_as_of"))
        cat.close()

        # 3. latest_as_of WITH fiscal_year in the sidecar (control)
        cat = build(tmp / "latest2")
        show("latest_as_of/with_fy       ", cat, SourceRequest(
            entity="Acme", market="US", security_id="ACME", document_kind="annual_report",
            provider="sec", provider_document_id="doc-1", as_of_date="2026-08-10",
            mode="latest_as_of"))
        cat.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
