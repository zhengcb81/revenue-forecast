"""B.VR(B03) extra evidence: the "out-of-root link never leaks bytes" property,
executed on THIS Windows host via a directory JUNCTION.

The author's `test_r4b03_symlink_escape_is_refused_where_symlinks_exist` skips
here (this host cannot create symlinks without elevation).  A junction can be
created without elevation, so the property can still be measured end-to-end:
scan -> resolve -> read_verified_bytes.

Usage: python b03_review_junction.py <out.json>
"""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(WIKI / "src"))

from company_wiki.source_catalog import CatalogConfig, SourceCatalog  # noqa: E402
from company_wiki.source_catalog.models import RootSpec  # noqa: E402
from company_wiki.source_catalog.resolver import SourceRequest, SourceResolver  # noqa: E402

BODY = b"%PDF-1.4 junction-probe"
DIGEST = hashlib.sha256(BODY).hexdigest()
OUT: dict = {}


def sidecar() -> dict:
    return {
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
    }


def main(argv):
    out_path = Path(argv[1]) if len(argv) > 1 else Path(tempfile.gettempdir()) / "b03_review_junction.json"
    tmp = Path(tempfile.mkdtemp(prefix="b03junc-"))
    root = tmp / "companies"
    outside = tmp / "outside"
    annual = root / "Acme" / "raw" / "financial_reports" / "annual"
    annual.mkdir(parents=True)
    outside.mkdir(parents=True)
    (outside / "2025.pdf").write_bytes(BODY)
    (outside / "2025.pdf.source.json").write_text(
        json.dumps(sidecar(), ensure_ascii=False), encoding="utf-8"
    )
    proc = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(annual / "link"), str(outside)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    OUT["junction_created"] = proc.returncode == 0
    OUT["junction_msg"] = ((proc.stdout or "") + (proc.stderr or "")).strip()[:200]
    if proc.returncode != 0:
        _write(out_path)
        return 0

    catalog = SourceCatalog(
        CatalogConfig(
            project_root=tmp,
            catalog_dir=tmp / ".source_catalog",
            reusable_root_kinds=("company_raw", "directory"),
            roots=(
                RootSpec(
                    "company_raw", root, "company_raw", priority=10,
                    adapter_id="company_raw_v1", read_only=False,
                    canonical_write_target="companies",
                ),
            ),
        )
    )
    catalog.scan()
    resolver = SourceResolver(catalog)
    request = SourceRequest(
        entity="Acme", market="US", security_id="ACME",
        document_kind="annual_report", form_type="10-K", fiscal_year=2025,
        provider="sec", provider_document_id="doc-1",
        as_of_date="2026-08-10", mode="exact",
    )
    result = resolver.resolve(request)
    OUT["resolve_status"] = result.status.value
    OUT["resolve_matches"] = len(result.matches)
    OUT["debug_trace"] = list(result.debug_trace)
    if result.matches:
        handle = result.matches[0]
        OUT["handle_canonical_path"] = handle.canonical_path
        out = resolver.read_verified_bytes(handle)
        OUT["read_status"] = out.status
        OUT["read_reason"] = out.reason
        OUT["bytes_leaked"] = out.data is not None
        OUT["n_matches"] = len(result.matches)
    else:
        OUT["note"] = "scan/resolve refused the junction copy (no handle) -> property holds at an earlier layer"
        OUT["bytes_leaked"] = False
    _write(out_path)
    return 0


def _write(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(OUT, fh, ensure_ascii=False, indent=2)
    print(f"wrote {out_path}")
    print(json.dumps({k: v for k, v in OUT.items() if k != "debug_trace"}, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
