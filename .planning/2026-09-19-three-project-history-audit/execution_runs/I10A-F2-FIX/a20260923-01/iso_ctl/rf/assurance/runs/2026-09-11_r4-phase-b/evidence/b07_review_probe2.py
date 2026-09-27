"""B.VR (B07) probe 2: the S-10 rule-2 path, the pre-change envelope behaviour,
and the consumer-side identity of the compared payload.

  (A) drift after scan: the indexed copy no longer has the requested version's
      bytes -> does `resolve` answer MISSING (explicit failure) or serve the
      claim-trusted row?  And does the B03 read path still refuse the bytes?
  (B) baseline (phase-A frozen 7d4852f) `build_resolution_envelope` with a
      foreign schema_version: accepted (claim 2's "before this it did not check
      at all").
  (C) the payload the FILING-FETCH consumer verifies is the same object the
      author's script compares: recompute the consumer's own document hash from
      the wiki payload and compare it with the payload's policy_hash.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path(__file__).resolve().parents[4]
CURRENT = REVENUE.parent / "company-wiki"
BASELINE_WT = Path(r"C:\Users\郑曾波\AppData\Local\Temp\cw-preb")
FIXED_PROJECT_ROOT = Path(r"C:\r4-b07-payload-baseline")
FILING_SCRIPTS = REVENUE.parent / "filing-fetch" / "scripts"

sys.path.insert(0, str(CURRENT / "src"))

OUT: dict = {}


def rule2_drift() -> dict:
    from company_wiki.source_catalog import CatalogConfig, SourceCatalog
    from company_wiki.source_catalog.models import RootSpec
    from company_wiki.source_catalog.resolver import SourceRequest, SourceResolver

    tmp = Path(tempfile.mkdtemp(prefix="b07_review_drift_"))
    root = tmp / "companies"
    target = root / "Acme" / "raw" / "financial_reports" / "annual" / "2025.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    original = b"%PDF-1.4 b07-review-original-version"
    target.write_bytes(original)
    sidecar = {
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
    }
    (target.parent / "2025.pdf.source.json").write_text(
        json.dumps(sidecar, ensure_ascii=False), encoding="utf-8"
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
    before = resolver.resolve(request)
    # drift: the bytes on disk are replaced AFTER indexing
    drifted = b"%PDF-1.4 DIFFERENT-LATER-BYTES-that-are-not-the-version"
    target.write_bytes(drifted)
    after = resolver.resolve(request)
    read = (
        resolver.read_verified_bytes(after.matches[0]) if after.matches else None
    )
    return {
        "before": {
            "status": before.status.value,
            "matches": len(before.matches),
            "reason": before.reason,
            "served_sha_is_original": (
                bool(before.matches)
                and before.matches[0].content_sha256 == hashlib.sha256(original).hexdigest()
            ),
        },
        "after_drift": {
            "status": after.status.value,
            "matches": len(after.matches),
            "reason": after.reason,
            "trace": list(after.debug_trace),
            "served_sha256": after.matches[0].content_sha256 if after.matches else None,
            "served_sha_is_indexed_original": (
                bool(after.matches)
                and after.matches[0].content_sha256 == hashlib.sha256(original).hexdigest()
            ),
            "bytes_now_on_disk_sha256": hashlib.sha256(drifted).hexdigest(),
            "read_path": (
                None
                if read is None
                else {
                    "status": read.status,
                    "reason": read.reason,
                    "bytes_returned": 0 if read.data is None else len(read.data),
                }
            ),
        },
    }


BASELINE_ENVELOPE_PROBE = r'''
import json, sys
from pathlib import Path
sys.path.insert(0, r"{src}")
from company_wiki.source_catalog.resolver import (
    SOURCE_RESOLVER_SCHEMA_VERSION, ResolutionResult, ResolutionStatus,
    build_resolution_envelope,
)
result = ResolutionResult(
    schema_version="2.0", request_id="urn:test", status=ResolutionStatus.MISSING,
    reason="r", download_required=True, download_allowed=False, matches=(),
    debug_trace=(),
)
try:
    env = build_resolution_envelope(result)
    out = {{"current_constant": SOURCE_RESOLVER_SCHEMA_VERSION,
            "foreign_version_result": "ACCEPTED",
            "envelope_schema_version": env.envelope_schema_version}}
except Exception as exc:
    out = {{"current_constant": SOURCE_RESOLVER_SCHEMA_VERSION,
            "foreign_version_result": f"refused:{{type(exc).__name__}}"}}
print(json.dumps(out, ensure_ascii=False))
'''


def baseline_envelope() -> dict:
    out = {}
    for label, checkout in (("baseline_7d4852f", BASELINE_WT), ("current", CURRENT)):
        script = BASELINE_ENVELOPE_PROBE.format(src=str(checkout / "src"))
        proc = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, cwd=str(checkout)
        )
        out[label] = (
            json.loads(proc.stdout.strip().splitlines()[-1])
            if proc.returncode == 0
            else {"error": proc.stderr[-800:]}
        )
    return out


def consumer_identity() -> dict:
    sys.path.insert(0, str(FILING_SCRIPTS))
    from filing_contracts import _policy_document_hash  # type: ignore

    from company_wiki.source_catalog.cli import _policy_export_payload
    from company_wiki.source_catalog.config import load_catalog_config

    config = load_catalog_config(
        CURRENT / "config" / "source_catalog.yaml", project_root=CURRENT
    )
    payload = _policy_export_payload(config)
    source = (FILING_SCRIPTS / "fetch_filing.py").read_text(encoding="utf-8")
    return {
        "consumer_document_hash": _policy_document_hash(payload),
        "payload_policy_hash": payload["policy_hash"],
        "consumer_hash_matches": _policy_document_hash(payload) == payload["policy_hash"],
        "fetch_filing_reads_key": 'resolution.get("policy_export")' in source,
        "script_compared_function": "company_wiki.source_catalog.cli._policy_export_payload",
        "same_function_used_by_cli_response": (
            'resolution_dict["policy_export"] = _policy_export_payload(config)'
            in (CURRENT / "src" / "company_wiki" / "source_catalog" / "cli.py").read_text(
                encoding="utf-8"
            )
        ),
        "filed_payload_roots_are_absolute": all(
            Path(r["path_ref"]).is_absolute() for r in payload["roots"]
        ),
    }


def main() -> int:
    OUT["rule2_drift_after_scan"] = rule2_drift()
    OUT["baseline_vs_current_envelope_on_foreign_version"] = baseline_envelope()
    OUT["consumer_identity_of_compared_payload"] = consumer_identity()
    out = RUN / "evidence" / "b07_review_probe2.json"
    out.write_text(json.dumps(OUT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(OUT, ensure_ascii=False, indent=2))
    print("wrote", out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
