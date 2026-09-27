"""B02 RED/GREEN probe: withdrawn preferred copy must fall through.

Runs the SAME scenario against whatever `company_wiki` is importable:

  1. three roots hold byte-identical copies of one annual report
     (company_raw p10, dropbox p30, future_lake p40) with real sidecars;
  2. resolve once -> the p10 copy is canonical;
  3. delete that file (the preferred copy is withdrawn, the catalog row stays
     active) and resolve again.

Pre-B02 (RED)  : the elected canonical is the deleted p10 path, so the single
                 `_handle` lookup finds no file -> no handle -> MISSING (the
                 request would be re-downloaded even though two copies of the
                 same version are still on disk).
Post-B02 (GREEN): the resolver walks the ordered qualified candidates, skips
                 the unreadable one and serves the p30 copy -> REUSED_EXACT,
                 same document id and same content hash, no download.

Usage (evidence for the B02 verification record):

    python b02_red_green_probe.py --label <pre-b02|post-b02> --out <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

BODY = b"%PDF-1.4 r4b02-red-green-probe"
DIGEST = hashlib.sha256(BODY).hexdigest()


def _write_copy(directory: Path, name: str = "2025.pdf") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_bytes(BODY)
    (directory / f"{name}.source.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "canonical_entity_id": "ent-acme",
                "display_name": "Acme",
                "market": "US",
                "security_id": "ACME",
                "document_kind": "annual_report",
                "fiscal_year": 2025,
                "period_end": "2025-12-31",
                "filing_date": "2026-02-20",
                "form_type": "10-K",
                "provider": "sec",
                "provider_document_id": "doc-1",
                "source_url": "https://sec.gov/x/2025",
                "content_sha256": DIGEST,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def run(label: str) -> dict:
    from company_wiki.source_catalog.models import RootSpec

    # NOTE: the catalog keeps its sqlite handle open for the lifetime of the
    # probe, and Windows refuses to delete a locked file — cleanup errors are
    # therefore ignored (the scratch tree may survive under %TEMP%).
    with tempfile.TemporaryDirectory(
        prefix="r4b02-probe-", ignore_cleanup_errors=True
    ) as raw_tmp:
        tmp = Path(raw_tmp)
        company_root = tmp / "companies"
        companies = company_root / "Acme" / "raw" / "financial_reports" / "annual"
        dropbox = tmp / "Dropbox" / "Stock"
        future = tmp / "future_lake"
        _write_copy(companies)
        _write_copy(dropbox)
        _write_copy(future)

        from company_wiki.source_catalog import CatalogConfig, SourceCatalog
        from company_wiki.source_catalog.resolver import (
            SourceRequest,
            SourceResolver,
        )

        catalog = SourceCatalog(
            CatalogConfig(
                project_root=tmp,
                catalog_dir=tmp / ".source_catalog",
                reusable_root_kinds=("company_raw", "directory"),
                roots=(
                    RootSpec(
                        "company_raw",
                        company_root,
                        "company_raw",
                        priority=10,
                        adapter_id="company_raw_v1",
                        read_only=False,
                        reusable_for_filing=True,
                        canonical_write_target="companies",
                    ),
                    RootSpec(
                        "dropbox_stock",
                        dropbox,
                        "directory",
                        priority=30,
                        adapter_id="sidecar_filing_v1",
                        read_only=True,
                        reusable_for_filing=True,
                    ),
                    RootSpec(
                        "future_lake",
                        future,
                        "directory",
                        priority=40,
                        adapter_id="sidecar_filing_v1",
                        read_only=True,
                        reusable_for_filing=True,
                    ),
                ),
            )
        )
        catalog.scan()

        def resolve() -> dict:
            result = SourceResolver(catalog).resolve(
                SourceRequest(
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
            )
            handle = result.matches[0] if result.matches else None
            return {
                "status": result.status.value,
                "reason": result.reason,
                "download_required": result.download_required,
                "match_count": len(result.matches),
                "canonical_root": (
                    ("companies" if "companies" in handle.canonical_path else
                     "dropbox" if "Dropbox" in handle.canonical_path else
                     "future_lake" if "future_lake" in handle.canonical_path else "?")
                    if handle
                    else ""
                ),
                "document_id": handle.document_id if handle else "",
                "content_sha256": handle.content_sha256 if handle else "",
                "debug_trace": list(result.debug_trace),
            }

        before = resolve()
        preferred = Path(
            catalog.store.fetchone(
                "SELECT absolute_path FROM locations WHERE root_id='company_raw' "
                "AND role='original_primary'"
            )["absolute_path"]
        )
        preferred.unlink()
        after = resolve()

    return {
        "label": label,
        "python": sys.executable,
        "module_file": sys.modules["company_wiki.source_catalog.resolver"].__file__,
        "body_sha256": DIGEST,
        "before_withdrawal": before,
        "after_withdrawal": after,
        "verdict": {
            "falls_through_to_equivalent_copy": (
                after["status"] == "reused_exact"
                and after["canonical_root"] in {"dropbox", "future_lake"}
                and after["content_sha256"] == DIGEST
                and after["document_id"] == before["document_id"]
                and after["download_required"] is False
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    payload = run(args.label)
    Path(args.out).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload["verdict"], ensure_ascii=False))
    print(f"status after withdrawal: {payload['after_withdrawal']['status']}")
    print(f"canonical after: {payload['after_withdrawal']['canonical_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
