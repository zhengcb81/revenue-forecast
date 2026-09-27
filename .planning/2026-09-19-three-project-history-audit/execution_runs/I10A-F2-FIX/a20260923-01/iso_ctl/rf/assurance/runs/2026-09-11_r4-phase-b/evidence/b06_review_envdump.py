"""Dump FC-704 envelopes for one tree, for the B06 pre/post behaviour check.

usage: python b06_review_envdump.py <tree_root> <out.json>
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

TREE = Path(sys.argv[1])
OUT = Path(sys.argv[2])
sys.path.insert(0, str(TREE / "src"))

from company_wiki.source_catalog import CatalogConfig, SourceCatalog  # noqa: E402
from company_wiki.source_catalog.models import RootSpec  # noqa: E402
from company_wiki.source_catalog.resolver import (  # noqa: E402
    SourceRequest,
    SourceResolver,
    build_resolution_envelope,
)

BODY = b"%PDF-1.4 b06-prepost-payload"
DIGEST = hashlib.sha256(BODY).hexdigest()


def sidecar(**overrides) -> dict:
    payload = {
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
        "content_sha256": DIGEST,
        "retrieved_at": "2026-02-21T00:00:00Z",
        "collector_name": "sec_edgar",
        "collector_version": "1.0",
    }
    payload.update(overrides)
    return payload


def write_copy(directory: Path, sc: dict) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "2025.pdf").write_bytes(BODY)
    (directory / "2025.pdf.source.json").write_text(
        json.dumps(sc, ensure_ascii=False), encoding="utf-8"
    )


def root(root_id: str, path: Path, kind: str, priority: int) -> RootSpec:
    return RootSpec(
        root_id,
        path,
        kind,
        priority=priority,
        adapter_id="company_raw_v1" if kind == "company_raw" else "sidecar_filing_v1",
        read_only=kind != "company_raw",
        reusable_for_filing=True,
        canonical_write_target="companies" if kind == "company_raw" else None,
    )


def request(**overrides) -> SourceRequest:
    base = dict(
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
    base.update(overrides)
    return SourceRequest(**base)


def build(tmp: Path, roots: list[RootSpec], req: SourceRequest) -> dict:
    cat = SourceCatalog(
        CatalogConfig(
            project_root=tmp,
            catalog_dir=tmp / ".source_catalog",
            reusable_root_kinds=("company_raw", "directory"),
            roots=tuple(roots),
        )
    )
    cat.scan()
    res = SourceResolver(cat).resolve(req)
    env = build_resolution_envelope(res, store=cat.store, project_root=tmp)
    return {"resolution": res.to_dict(), "envelope": env.to_dict()}


def main() -> None:
    out: dict[str, object] = {}
    # (1) plain complete handle
    tmp = Path(tempfile.mkdtemp(prefix="b06pp-plain-"))
    base = tmp / "companies"
    write_copy(base / "Acme" / "raw" / "financial_reports" / "annual", sidecar())
    out["plain"] = build(tmp, [root("company_raw", base, "company_raw", 10)], request())
    # (2) real field conflict (two captures, equal priorities)
    tmp2 = Path(tempfile.mkdtemp(prefix="b06pp-conf-"))
    base2 = tmp2 / "companies"
    dropbox = tmp2 / "Dropbox" / "Stock"
    write_copy(base2 / "Acme" / "raw" / "financial_reports" / "annual", sidecar())
    write_copy(dropbox, sidecar(source_title="Acme 2025 Annual Report (restated)"))
    out["conflict"] = build(
        tmp2,
        [
            root("company_raw", base2, "company_raw", 10),
            root("dropbox_stock", dropbox, "directory", 10),
        ],
        request(),
    )
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
