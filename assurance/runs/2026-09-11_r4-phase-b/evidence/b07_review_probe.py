"""B.VR (B07) independent probe.  Read-only w.r.t. the product repo.

Reproduces the author's payload numbers, then attacks the claims:

  * version-entry-point enumeration (a): which wiki-side entry points still
    accept a foreign ``schema_version``;
  * the five-value vocabulary (a): is an unknown version refused with one of
    the operation contract's five values, or with a bare ValueError;
  * the "no qualified copy -> explicit failure" sentence in the new contract
    comment (c): a synthetic catalog whose only copy's bytes do NOT match its
    declared content_sha256;
  * payload comparison soundness (d): real project_root vs fixed project_root,
    production runtime_policy.json cross-check.

Writes evidence/b07_review_probe.json (UTF-8, ensure_ascii=False).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path(__file__).resolve().parents[4]
CURRENT = REVENUE.parent / "company-wiki"
BASELINE_WT = Path(
    r"C:\Users\郑曾波\AppData\Local\Temp\cw-preb"
)  # worktree of phase-A frozen revision 7d4852f
FIXED_PROJECT_ROOT = Path(r"C:\r4-b07-payload-baseline")

sys.path.insert(0, str(CURRENT / "src"))

OUT: dict = {}


# ---------------------------------------------------------------------------
# 1. payload: real project_root vs fixed project_root (defeat attempt on (d))
# ---------------------------------------------------------------------------

PAYLOAD_PROBE = r'''
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, r"{src}")
from company_wiki.source_catalog.cli import _policy_export_payload
from company_wiki.source_catalog.config import load_catalog_config

checkout = Path(r"{checkout}")
project_root = Path(r"{project_root}")
config = load_catalog_config(checkout / "config" / "source_catalog.yaml",
                             project_root=project_root)
payload = _policy_export_payload(config)
canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
print(json.dumps({{
    "checkout": str(checkout),
    "project_root": str(project_root),
    "policy_hash": payload.get("policy_hash"),
    "canonical_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    "canonical_bytes": len(canonical.encode("utf-8")),
    "path_refs": [r.get("path_ref") for r in payload.get("roots") or []],
    "payload": payload,
}}, ensure_ascii=False))
'''


def measure_payload(checkout: Path, project_root: Path) -> dict:
    script = PAYLOAD_PROBE.format(
        src=str(checkout / "src"), checkout=str(checkout), project_root=str(project_root)
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, cwd=str(checkout)
    )
    if result.returncode != 0:
        raise SystemExit(f"probe failed in {checkout}:\n{result.stderr[-2000:]}")
    return json.loads(result.stdout.strip().splitlines()[-1])


def payload_section() -> dict:
    fixed_base = measure_payload(BASELINE_WT, FIXED_PROJECT_ROOT)
    fixed_cur = measure_payload(CURRENT, FIXED_PROJECT_ROOT)
    real_base = measure_payload(BASELINE_WT, BASELINE_WT)
    real_cur = measure_payload(CURRENT, CURRENT)
    # the production artifact the shipped catalog carries (real project_root)
    runtime = json.loads(
        (CURRENT / ".source_catalog" / "runtime_policy.json").read_text(encoding="utf-8")
    )
    return {
        "fixed_project_root": {
            "root": str(FIXED_PROJECT_ROOT),
            "exists": FIXED_PROJECT_ROOT.exists(),
            "baseline_canonical_sha256": fixed_base["canonical_sha256"],
            "current_canonical_sha256": fixed_cur["canonical_sha256"],
            "identical": fixed_base["canonical_sha256"] == fixed_cur["canonical_sha256"],
            "policy_hash_equal": fixed_base["policy_hash"] == fixed_cur["policy_hash"],
            "baseline_bytes": fixed_base["canonical_bytes"],
            "current_bytes": fixed_cur["canonical_bytes"],
        },
        "real_project_root": {
            "baseline_canonical_sha256": real_base["canonical_sha256"],
            "current_canonical_sha256": real_cur["canonical_sha256"],
            "identical": real_base["canonical_sha256"] == real_cur["canonical_sha256"],
            "baseline_policy_hash": real_base["policy_hash"],
            "current_policy_hash": real_cur["policy_hash"],
            "baseline_path_refs": real_base["path_refs"],
            "current_path_refs": real_cur["path_refs"],
        },
        "production_runtime_policy_hash": runtime.get("policy_hash"),
        "current_real_root_hash_matches_production": (
            real_cur["policy_hash"] == runtime.get("policy_hash")
        ),
        "fixed_root_payload_matches_current_real_root_modulo_prefix": None,
        "payload_bytes_at_fixed_root": fixed_cur["canonical_bytes"],
    }


# ---------------------------------------------------------------------------
# 2. version entry points (question a) + no-qualified-copy behaviour (question c)
# ---------------------------------------------------------------------------


def _sidecar(body_sha: str, **overrides) -> dict:
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
        "content_sha256": body_sha,
        "retrieved_at": "2026-02-21T00:00:00Z",
        "collector_name": "sec_edgar",
        "collector_version": "1.0",
    }
    payload.update(overrides)
    return payload


def _build_catalog(tmp: Path, bytes_on_disk: bytes, declared_sha: str):
    from company_wiki.source_catalog import CatalogConfig, SourceCatalog
    from company_wiki.source_catalog.models import RootSpec

    root = tmp / "companies"
    target = root / "Acme" / "raw" / "financial_reports" / "annual" / "2025.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(bytes_on_disk)
    (target.parent / "2025.pdf.source.json").write_text(
        json.dumps(_sidecar(declared_sha), ensure_ascii=False), encoding="utf-8"
    )
    spec = RootSpec(
        "company_raw",
        root,
        "company_raw",
        priority=10,
        adapter_id="company_raw_v1",
        read_only=False,
        reusable_for_filing=True,
        canonical_write_target="companies",
    )
    catalog = SourceCatalog(
        CatalogConfig(
            project_root=tmp,
            catalog_dir=tmp / ".source_catalog",
            reusable_root_kinds=("company_raw",),
            roots=(spec,),
        )
    )
    catalog.scan()
    return catalog


def version_section() -> dict:
    from company_wiki.source_catalog.resolver import (
        SOURCE_RESOLVER_SCHEMA_VERSION,
        ResolutionResult,
        ResolutionStatus,
        SourceHandle,
        SourceRequest,
        SourceResolver,
        build_resolution_envelope,
    )

    report: dict = {"current_version": SOURCE_RESOLVER_SCHEMA_VERSION}

    # (i) SourceRequest
    try:
        SourceRequest(
            entity="Acme",
            document_kind="annual_report",
            as_of_date="2026-08-10",
            schema_version="2.0",
        )
        report["SourceRequest_foreign_version"] = "ACCEPTED"
    except Exception as exc:  # noqa: BLE001
        report["SourceRequest_foreign_version"] = f"refused:{type(exc).__name__}"

    # (ii) SourceHandle construction
    handle_fields = dict(
        document_id="d",
        source_id="s",
        entity_ids=(),
        title="t",
        source_type="filing",
        document_kind="annual_report",
        published_date="2025-12-31",
        fiscal_year=2025,
        fiscal_period=None,
        form_type=None,
        language=None,
        provider=None,
        provider_document_id=None,
        https_url=None,
        canonical_location_id="l",
        canonical_path=str(CURRENT / "README.md"),
        content_sha256="0" * 64,
        snapshot_sha256="0" * 64,
        mime_type="application/pdf",
        byte_size=1,
        retrieved_at="2026-02-21T00:00:00Z",
        collector_name="c",
        collector_version="1",
        source_status="active",
        duplicate_group_id="g",
        exact_duplicate_location_count=1,
        capture_ready=True,
        missing_capture_fields=(),
    )
    foreign_handle = SourceHandle(schema_version="2.0", **handle_fields)
    report["SourceHandle_foreign_version"] = (
        "ACCEPTED (constructed with schema_version=2.0)" if foreign_handle else "refused"
    )
    report["SourceHandle_to_dict_version"] = foreign_handle.to_dict()["schema_version"]

    # (iii) ResolutionResult construction + to_dict
    foreign_result = ResolutionResult(
        schema_version="2.0",
        request_id="urn:test",
        status=ResolutionStatus.MISSING,
        reason="r",
        download_required=True,
        download_allowed=False,
        matches=(),
        debug_trace=(),
    )
    report["ResolutionResult_foreign_version_construct"] = "ACCEPTED"
    report["ResolutionResult_to_dict_version"] = foreign_result.to_dict()["schema_version"]

    # (iv) build_resolution_envelope: unknown version
    try:
        build_resolution_envelope(foreign_result)
        report["build_resolution_envelope_foreign_version"] = "ACCEPTED"
    except Exception as exc:  # noqa: BLE001
        report["build_resolution_envelope_foreign_version"] = (
            f"refused:{type(exc).__name__}:{str(exc)[:80]}"
        )

    # (v) current-version result carrying a FOREIGN-version handle
    mixed = ResolutionResult(
        schema_version=SOURCE_RESOLVER_SCHEMA_VERSION,
        request_id="urn:test",
        status=ResolutionStatus.MISSING,
        reason="r",
        download_required=True,
        download_allowed=False,
        matches=(foreign_handle,),
        debug_trace=(),
    )
    try:
        env = build_resolution_envelope(mixed)
        report["envelope_with_foreign_handle"] = (
            f"ACCEPTED (no handle-version check); sibling resolution dict carries "
            f"{mixed.to_dict()['matches'][0]['schema_version']!r}; "
            f"envelope outcome={env.outcome!r}"
        )
    except Exception as exc:  # noqa: BLE001
        report["envelope_with_foreign_handle"] = f"refused:{type(exc).__name__}"

    # (vi) read_verified_bytes on a foreign-version handle (does it check?)
    tmp = Path(tempfile.mkdtemp(prefix="b07_review_ok_"))
    body = b"%PDF-1.4 b07-review"
    catalog = _build_catalog(tmp, body, hashlib.sha256(body).hexdigest())
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
    good = resolver.resolve(request)
    report["verified_case_status"] = good.status.value
    report["verified_case_matches"] = len(good.matches)
    if good.matches:
        foreign = dataclasses.replace(good.matches[0], schema_version="2.0")
        read = resolver.read_verified_bytes(foreign)
        report["read_verified_bytes_foreign_handle"] = {
            "status": read.status,
            "reason": read.reason,
            "bytes_returned": 0 if read.data is None else len(read.data),
            "handle_version": foreign.schema_version,
        }
        # CLI read-only ensure renderer: does it validate the version?
        from company_wiki.source_catalog.cli import _read_only_ensure_result

        rendered = _read_only_ensure_result(
            dataclasses.replace(good, schema_version="2.0")
        )
        report["cli_read_only_ensure_foreign_version"] = rendered["resolution"][
            "schema_version"
        ]

    # (vii) the S-10 rule-2 path: declared sha != bytes on disk
    tmp2 = Path(tempfile.mkdtemp(prefix="b07_review_mismatch_"))
    actual = b"%PDF-1.4 actual-bytes"
    declared = hashlib.sha256(b"declared-bytes-never-on-disk").hexdigest()
    catalog2 = _build_catalog(tmp2, actual, declared)
    res2 = SourceResolver(catalog2).resolve(request)
    report["mismatched_declaration_case"] = {
        "status": res2.status.value,
        "matches": len(res2.matches),
        "served_handle_content_sha256": (
            res2.matches[0].content_sha256[12:] if res2.matches else None
        ),
        "served_digest_equals_declared": (
            bool(res2.matches) and res2.matches[0].content_sha256 == declared
        ),
        "trace": list(res2.debug_trace),
        "capture_ready": res2.matches[0].capture_ready if res2.matches else None,
    }
    return report


def main() -> int:
    OUT["payload"] = payload_section()
    OUT["version_entry_points"] = version_section()
    out_path = RUN / "evidence" / "b07_review_probe.json"
    out_path.write_text(json.dumps(OUT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(OUT, ensure_ascii=False, indent=2))
    print("wrote", out_path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
