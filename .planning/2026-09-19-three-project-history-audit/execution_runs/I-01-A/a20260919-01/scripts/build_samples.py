"""Build CFG-REAL / CFG-GOOD / CFG-FIFTH / N2 / N3 sample directories.

Fixture writer only: it does NOT call any behavior-under-test (the effective
config judgment); the snapshot hash formula is reimplemented here as an
independent disclosure of how every sample policy was built.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent / "samples"

PROD_FLAGS = {
    "legacy_bridge_enabled": False,
    "v2_bundle_active": False,
    "v2_persist_assertions": True,
    "v2_resolve_active": True,
    "v2_resolve_shadow": True,
    "v2_scan_shadow": True,
}
LEGACY_FLAGS = {
    # approved legacy state (card D-W01: bridge-v2 mixing refused; all-v2-off
    # with no incumbent snapshot users is the degraded-friendly legacy state)
    "legacy_bridge_enabled": False,
    "v2_bundle_active": False,
    "v2_persist_assertions": False,
    "v2_resolve_active": False,
    "v2_resolve_shadow": False,
    "v2_scan_shadow": False,
}


def snapshot_sha256(payload: dict) -> str:
    without_hash = {k: v for k, v in payload.items() if k != "snapshot_sha256"}
    return hashlib.sha256(
        json.dumps(without_hash, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def write_policy(sample: Path, flags: dict) -> None:
    payload = {
        "schema_version": "1.0",
        "policy_hash": "c" * 64,
        "flags": flags,
        "current_epoch": "epoch-" + sample.name,
        "active_cohorts": [],
        "updated_at": "2026-09-19T00:00:00Z",
    }
    payload["snapshot_sha256"] = snapshot_sha256(payload)
    cat = sample / ".scratch" / ".source_catalog"
    (cat / "security_master").mkdir(parents=True, exist_ok=True)
    for market in ("cn", "hk", "us"):
        (cat / "security_master" / f"{market}.json").write_text("{}", encoding="utf-8")
    (cat / "runtime_policy.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )


def base_yaml(roots: str, *, policy_flags: dict, sample: Path) -> None:
    header = 'schema_version: "1.0"\n'
    header += 'catalog_dir: "${PROJECT_ROOT}/.scratch/.source_catalog"\n'
    header += "reusable_root_kinds: [company_raw, dayu_portfolio, directory]\n"
    header += "roots:\n"
    (sample / "source_catalog.yaml").write_text(header + roots, encoding="utf-8")
    write_policy(sample, policy_flags)


# --- scratch fixture builders -------------------------------------------------


def build_scratch_companies(project: Path, *, with_raw_fixture: bool) -> None:
    """company_raw layout: companies/{company}/raw/... plus .source.json."""
    company = project / "companies" / "Acme"
    raw = company / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    if with_raw_fixture:
        body = b"%PDF-1.4\n% cfg-good acme annual\n"
        (raw / "2025.pdf").write_bytes(body)
        (raw / "2025.pdf.source.json").write_text(
            json.dumps(
                {
                    "form_type": "10-K",
                    "fiscal_year": 2025,
                    "fiscal_period": "FY",
                    "period_end": "2025-12-31",
                    "document_kind": "annual_report",
                    "provider": "sec",
                    "accession_number": "0000000000-26-000001",
                    "source_url": "https://example.sec.gov/acme-2025.htm",
                    "market": "US",
                    "security_id": "ACME",
                    "company_name": "Acme",
                    "content_sha256": hashlib.sha256(body).hexdigest(),
                }
            ),
            encoding="utf-8",
        )


def build_scratch_empty(project: Path, *names: str) -> None:
    for name in names:
        (project / name).mkdir(parents=True, exist_ok=True)


def build_scratch_plain(
    project: Path, *, name: str = "dropbox_stock", files: int = 1
) -> None:
    root = project / name
    root.mkdir(parents=True, exist_ok=True)
    for index in range(files):
        (root / f"note-{index}.md").write_bytes(b"# plain file %d\n" % index)


def build_scratch_archive(project: Path) -> None:
    """CFG-FIFTH archive_extra: 2 .txt originals + 1 standalone sidecar."""
    root = project / "archive_extra"
    root.mkdir(parents=True, exist_ok=True)
    body_a = b"archive original a (%s)\n"
    (root / "a.txt").write_bytes(body_a % b"full-sidecar")
    (root / "a.txt.source.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "canonical_entity_id": "ent-archive-a",
                "display_name": "Archive A",
                "company_name": "Archive A",
                "market": "US",
                "security_id": "ARCHA",
                "document_kind": "annual_report",
                "fiscal_year": 2025,
                "period_end": "2025-12-31",
                "published_at": "2026-03-01",
                "form_type": "10-K",
                "provider": "sec",
                "provider_document_id": "archive-a-1",
                "content_sha256": hashlib.sha256(
                    (root / "a.txt").read_bytes()
                ).hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    (root / "b.txt").write_bytes(b"archive original b (no sidecar)\n")
    # standalone sidecar WITHOUT a paired original: must not become a document
    (root / "c.source.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "canonical_entity_id": "ent-archive-c",
                "display_name": "Archive C",
                "market": "US",
                "security_id": "ARCHC",
                "document_kind": "annual_report",
                "fiscal_year": 2025,
                "period_end": "2025-12-31",
                "provider": "sec",
                "provider_document_id": "archive-c-1",
            }
        ),
        encoding="utf-8",
    )


# --- CFG-REAL -----------------------------------------------------------------

CFG_REAL_ROOTS = """\
  - root_id: company_raw
    kind: company_raw
    path: "${PROJECT_ROOT}/.scratch/companies"
    priority: 10
    privacy_class: public
  - root_id: dayu_portfolio
    kind: dayu_portfolio
    path: "${PROJECT_ROOT}/.scratch/portfolio"
    priority: 20
    privacy_class: public
  - root_id: dropbox_stock
    kind: directory
    path: "${PROJECT_ROOT}/.scratch/dropbox_stock"
    priority: 30
    privacy_class: public
  - root_id: future_lake
    kind: directory
    path: "${PROJECT_ROOT}/.scratch/future_lake"
    adapter_id: sidecar_filing_v1
    read_only: true
    reusable_for_filing: true
    priority: 40
    privacy_class: public
"""


def build_cfg_real() -> None:
    sample = SAMPLES / "cfg_real"
    sample.mkdir(parents=True, exist_ok=True)
    base_yaml(CFG_REAL_ROOTS, policy_flags=PROD_FLAGS, sample=sample)
    build_scratch_empty(
        sample / ".scratch", "companies", "portfolio", "dropbox_stock", "future_lake"
    )
    build_scratch_plain(sample / ".scratch", name="dropbox_stock")


# --- CFG-GOOD -----------------------------------------------------------------


def build_cfg_good() -> None:
    sample = SAMPLES / "cfg_good"
    sample.mkdir(parents=True, exist_ok=True)
    project = sample / ".scratch"
    roots = """\
  - root_id: company_raw
    kind: company_raw
    path: "${PROJECT_ROOT}/.scratch/companies"
    adapter_id: company_raw_v1
    read_only: false
    priority: 10
    privacy_class: public
  - root_id: dayu_portfolio
    kind: dayu_portfolio
    path: "${PROJECT_ROOT}/.scratch/portfolio"
    adapter_id: dayu_filing_v1
    read_only: false
    priority: 20
    privacy_class: public
  - root_id: dropbox_stock
    kind: directory
    path: "${PROJECT_ROOT}/.scratch/dropbox_stock"
    priority: 30
    privacy_class: public
  - root_id: future_lake
    kind: directory
    path: "${PROJECT_ROOT}/.scratch/future_lake"
    adapter_id: sidecar_filing_v1
    read_only: true
    reusable_for_filing: true
    priority: 40
    privacy_class: public
"""
    base_yaml(roots, policy_flags=LEGACY_FLAGS, sample=sample)
    build_scratch_companies(project, with_raw_fixture=True)
    build_scratch_empty(project, "portfolio", "future_lake")
    build_scratch_plain(project, name="dropbox_stock", files=1)


# --- CFG-FIFTH ----------------------------------------------------------------

CFG_GOOD_ROOTS = """\
  - root_id: company_raw
    kind: company_raw
    path: "${PROJECT_ROOT}/.scratch/companies"
    adapter_id: company_raw_v1
    read_only: false
    priority: 10
    privacy_class: public
  - root_id: dayu_portfolio
    kind: dayu_portfolio
    path: "${PROJECT_ROOT}/.scratch/portfolio"
    adapter_id: dayu_filing_v1
    read_only: false
    priority: 20
    privacy_class: public
  - root_id: dropbox_stock
    kind: directory
    path: "${PROJECT_ROOT}/.scratch/dropbox_stock"
    priority: 30
    privacy_class: public
  - root_id: future_lake
    kind: directory
    path: "${PROJECT_ROOT}/.scratch/future_lake"
    adapter_id: sidecar_filing_v1
    read_only: true
    reusable_for_filing: true
    priority: 40
    privacy_class: public
"""

CFG_EXTRA_ROOT = """\
  - root_id: archive_extra
    kind: directory
    path: "${PROJECT_ROOT}/.scratch/archive_extra"
    adapter_id: sidecar_filing_v1
    read_only: true
    reusable_for_filing: true
    priority: 50
    privacy_class: public
"""


def build_cfg_fifth() -> None:
    sample = SAMPLES / "cfg_fifth"
    sample.mkdir(parents=True, exist_ok=True)
    project = sample / ".scratch"
    roots = CFG_GOOD_ROOTS + CFG_EXTRA_ROOT
    base_yaml(roots, policy_flags=LEGACY_FLAGS, sample=sample)
    build_scratch_companies(project, with_raw_fixture=True)
    build_scratch_empty(project, "portfolio", "future_lake")
    build_scratch_plain(project, name="dropbox_stock", files=1)
    build_scratch_archive(project)


# --- N2 / N3 mutation samples (single company_raw root, no snapshot) ----------


def _mutation_sample(name: str, root_lines: str) -> None:
    sample = SAMPLES / name
    sample.mkdir(parents=True, exist_ok=True)
    base_yaml(root_lines, policy_flags=LEGACY_FLAGS, sample=sample)
    build_scratch_companies(sample / ".scratch", with_raw_fixture=True)
    build_scratch_empty(sample / ".scratch", "portfolio")


def build_mutations() -> None:
    _mutation_sample(
        "n2_unknown_adapter",
        """\
  - root_id: company_raw
    kind: company_raw
    path: "${PROJECT_ROOT}/.scratch/companies"
    adapter_id: nonexistent_adapter_9f
    read_only: false
    priority: 10
""",
    )
    _mutation_sample(
        "n2_no_scanner_impl",
        """\
  - root_id: company_raw
    kind: company_raw
    path: "${PROJECT_ROOT}/.scratch/companies"
    adapter_id: generic_document_v1
    read_only: false
    priority: 10
""",
    )
    _mutation_sample(
        "n2_version_unsupported",
        """\
  - root_id: company_raw
    kind: company_raw
    path: "${PROJECT_ROOT}/.scratch/companies"
    adapter_id: company_raw_v1
    adapter_version_range: ">=1.11.0"
    read_only: false
    priority: 10
""",
    )
    _mutation_sample(
        "n2_unknown_profile",
        """\
  - root_id: company_raw
    kind: company_raw
    path: "${PROJECT_ROOT}/.scratch/companies"
    adapter_id: company_raw_v1
    admission_profile_id: no_profile_zz
    read_only: false
    priority: 10
""",
    )
    _mutation_sample(
        "n3_readonly_write_target",
        """\
  - root_id: archive_quick
    kind: directory
    path: "${PROJECT_ROOT}/.scratch/archive_quick"
    adapter_id: sidecar_filing_v1
    read_only: true
    canonical_write_target: "${PROJECT_ROOT}/.scratch/write_target"
    priority: 50
""",
    )
    _mutation_sample(
        "n3_profile_mismatch",
        """\
  - root_id: archive_quick
    kind: directory
    path: "${PROJECT_ROOT}/.scratch/archive_quick"
    adapter_id: sidecar_filing_v1
    admission_profile_id: generic_document_v1
    read_only: true
    priority: 50
""",
    )
    (SAMPLES / "n3_readonly_write_target" / ".scratch" / "archive_quick").mkdir(
        parents=True, exist_ok=True
    )
    (
        SAMPLES / "n3_readonly_write_target" / ".scratch" / "archive_quick" / "x.txt"
    ).write_bytes(b"x\n")
    (SAMPLES / "n3_profile_mismatch" / ".scratch" / "archive_quick").mkdir(
        parents=True, exist_ok=True
    )
    (
        SAMPLES / "n3_profile_mismatch" / ".scratch" / "archive_quick" / "x.txt"
    ).write_bytes(b"x\n")


if __name__ == "__main__":
    build_cfg_real()
    build_cfg_good()
    build_cfg_fifth()
    build_mutations()
    manifest = {
        "samples": sorted(p.name for p in SAMPLES.iterdir() if p.is_dir()),
        "note": "all paths redirected under <sample>/.scratch; policy hashes "
        "computed by the formula reimplemented in this file (snapshot_sha256)",
    }
    (SAMPLES / "samples_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("samples built:", manifest["samples"])
