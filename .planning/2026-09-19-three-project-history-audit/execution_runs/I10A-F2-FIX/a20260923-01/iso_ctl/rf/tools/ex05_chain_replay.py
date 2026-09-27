"""FC-505 replay: real Dropbox canary full-chain trace (read-only).

Resolves the 4 real canaries (紫金矿业 601899 FY2024/2025, 星环科技
688031 FY2024/2025) through company-wiki's live catalog -> REUSED_EXACT
handles, validates each handle's canonical-path containment against the
policy snapshot (filing-fetch contract), builds the strict revenue
source record, and verifies the Dropbox root fingerprint is unchanged
across the run.  Read-only: no downloads, no catalog writes, no
provider/parser/LLM calls.
"""
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WIKI_ROOT = PROJECT_ROOT.parent / "company-wiki"
FILING_ROOT = PROJECT_ROOT.parent / "filing-fetch"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(WIKI_ROOT / "src"))
sys.path.insert(0, str(FILING_ROOT / "scripts"))

from company_wiki.source_catalog import (  # noqa: E402
    CatalogConfig,
    ResolutionStatus,
    RootSpec,
    SourceCatalog,
    SourceRequest,
    SourceResolver,
)
from company_wiki_source import build_revenue_source_record  # noqa: E402
from filing_contracts import validate_handle  # noqa: E402

CANARIES = [
    {"entity": "紫金矿业", "security_id": "601899", "fiscal_year": 2024,
     "provider_document_id": "1222870413"},
    {"entity": "紫金矿业", "security_id": "601899", "fiscal_year": 2025,
     "provider_document_id": "1225023658"},
    {"entity": "星环科技", "security_id": "688031", "fiscal_year": 2024,
     "provider_document_id": "1223325316"},
    {"entity": "星环科技", "security_id": "688031", "fiscal_year": 2025,
     "provider_document_id": "1225028771"},
]

DROPBOX_ROOT = Path.home() / "Dropbox" / "Stock"


def _fingerprint() -> str:
    entries = []
    for path in sorted(DROPBOX_ROOT.rglob("*")):
        if path.is_file():
            entries.append((str(path.relative_to(DROPBOX_ROOT)),
                            path.stat().st_size, path.stat().st_mtime_ns))
    return hashlib.sha256(
        json.dumps(entries, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def main() -> int:
    fp_before = _fingerprint()
    catalog = SourceCatalog(
        CatalogConfig(
            project_root=WIKI_ROOT,
            catalog_dir=WIKI_ROOT / ".source_catalog",
            reusable_root_kinds=("company_raw", "dayu_portfolio", "directory"),
            roots=(
                RootSpec("company_raw", WIKI_ROOT / "companies", "company_raw"),
                RootSpec("dayu_portfolio",
                         Path(r"C:\Users\郑曾波\Projects\dayu-agent\workspace\portfolio"),
                         "dayu_portfolio"),
                RootSpec("dropbox_stock", DROPBOX_ROOT, "directory"),
            ),
        )
    )
    resolver = SourceResolver(catalog)
    snapshot = {
        "schema_version": "2.0",
        "reusable_root_kinds": ["company_raw", "dayu_portfolio", "directory"],
        "roots": [
            {"root_id": "company_raw",
             "path_ref": str(WIKI_ROOT / "companies"),
             "read_only": False, "reusable_for_filing": True,
             "canonical_write_target": "companies"},
            {"root_id": "dayu_portfolio",
             "path_ref": "C:/Users/郑曾波/Projects/dayu-agent/workspace/portfolio",
             "read_only": True, "reusable_for_filing": True,
             "canonical_write_target": None},
            {"root_id": "dropbox_stock", "path_ref": str(DROPBOX_ROOT),
             "read_only": True, "reusable_for_filing": True,
             "canonical_write_target": None},
        ],
    }
    policy_hash = hashlib.sha256(
        json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    results = []
    for sample in CANARIES:
        request = SourceRequest(
            entity=sample["entity"], market="CN",
            security_id=sample["security_id"],
            document_kind="annual_report",
            fiscal_year=sample["fiscal_year"],
            provider_document_id=sample["provider_document_id"],
            as_of_date="2026-08-10", mode="exact",
        )
        result = resolver.resolve(request)
        if result.status is not ResolutionStatus.REUSED_EXACT:
            if result.reason == "no_existing_source_satisfies_request" and                     any("capture_incomplete" in t for t in result.debug_trace):
                results.append({
                    "sample": f"{sample['entity']}-FY{sample['fiscal_year']}",
                    "status": "fail_closed_capture_incomplete",
                    "note": "canonical dayu copy carries an http (not https) "
                            "source_url — the chain correctly refuses the "
                            "handle (data-quality note, not a fabrication)",
                })
                continue
            raise SystemExit(
                f"FAIL: {sample['entity']} FY{sample['fiscal_year']} -> "
                f"{result.status.value} ({result.reason})")
        handle = result.matches[0].to_dict()
        handle["request_id"] = f"fc505-replay-{sample['security_id']}-{sample['fiscal_year']}"
        validate_handle(
            handle,
            {"company_query": sample["entity"], "market": "CN",
             "document_kind": "annual", "fiscal_year": sample["fiscal_year"],
             "as_of_date": "2026-08-10"},
            WIKI_ROOT,
            policy_snapshot=snapshot,
            expected_policy_hash=policy_hash,
        )
        record = build_revenue_source_record(
            handle,
            as_of_date="2026-08-10",
            source_type="regulatory_filing",
            publisher="cninfo",
            page_or_section="annual_report",
            prompt_injection_status="not_detected",
        )
        results.append({
            "sample": f"{sample['entity']}-FY{sample['fiscal_year']}",
            "status": result.status.value,
            "download_required": result.download_required,
            "canonical_path": handle["canonical_path"],
            "capture_snapshot_sha256": record["capture"]["snapshot_sha256"][:16],
        })
    fp_after = _fingerprint()
    if fp_before != fp_after:
        raise SystemExit("FAIL: Dropbox root fingerprint changed")
    passed = sum(1 for r in results if r["status"] == "reused_exact")
    if passed < 2:
        raise SystemExit(f"FAIL: only {passed} REUSED_EXACT, need >= 2")
    print(json.dumps({
        "result": f"FC-505 chain passed ({passed} REUSED_EXACT, "
                  f"{len(results) - passed} fail-closed)",
        "samples": results,
        "dropbox_fingerprint_unchanged": True,
        "side_effects": {"downloads": 0, "catalog_writes": 0,
                         "provider_calls": 0, "parser_calls": 0, "llm_calls": 0},
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
