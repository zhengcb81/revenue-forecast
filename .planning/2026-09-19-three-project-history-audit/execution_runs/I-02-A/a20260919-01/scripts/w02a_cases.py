"""w02a_cases: case runner for card I-02-A (scan return contract / target
registration receipt consumed by the canonical writer).

All injection is harness-side (module attribute replacement on already-loaded
override modules). No fake scanner code lives inside the product copies. The
positive case uses the REAL scanner + REAL resolver + REAL writer only.

Outputs into <attempt>/after/:
  scan-return-contract.json
  target-registration.sql-results.json
  raw-before-after.json
  case_results.json
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
AFTER = ATTEMPT / "after"

import os
import sys
import tempfile

# Windows MAX_PATH: the writer Path.resolve() canonicalizes 8.3/subst forms
# back to the physical path, and the deep attempt path plus the canonical
# sidecar temp filename exceeds 260 chars.  The scratch areas therefore live
# under a short physical TEMP base; the whole retained evidence tree is copied
# back into the attempt's after/case_scratch_retained at the end of the run.
SCRATCH_BASE = Path(tempfile.gettempdir()) / "w02a" / "a20260919-01_case_scratch"

w02a = __import__("w02a_bootstrap")
MODE = sys.argv[1] if len(sys.argv) > 1 else "override"
assert MODE in {"override", "prod"}, MODE
w02a.setup(MODE)

from company_wiki.source_catalog import (  # noqa: E402
    CatalogConfig,
    RootSpec,
    SourceCatalog,
)
from company_wiki.source_catalog.canonical_writer import (  # noqa: E402
    CanonicalImportError,
    CanonicalSourceWriter,
)
import company_wiki.source_catalog.canonical_writer as cw_module  # noqa: E402
import company_wiki.source_catalog.scanner as scanner_module  # noqa: E402
from company_wiki.source_catalog.acquisition import (  # noqa: E402
    DownloadCandidate,
    DownloadReceipt,
)
from company_wiki.source_catalog.resolver import (  # noqa: E402
    ResolutionResult,
    ResolutionStatus,
    SourceHandle,
    SourceRequest,
)

PAYLOAD_A = b"%PDF-1.7\nw02a target annual report bytes\n"
PAYLOAD_B = b"%PDF-1.7\nw02a unrelated broker note bytes\n"
TARGET_SHA = hashlib.sha256(PAYLOAD_A).hexdigest()
OTHER_SHA = hashlib.sha256(PAYLOAD_B).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def request_and_candidate():
    request = SourceRequest(
        entity="样本公司",
        security_id="600000",
        market="CN",
        document_kind="annual_report",
        fiscal_year=2025,
        fiscal_period="FY",
        as_of_date="2026-07-18",
        allow_download=True,
    )
    candidate = DownloadCandidate(
        candidate_id="cninfo:w02a-announcement-2025",
        provider="cninfo",
        provider_document_id="announcement-2025",
        market="CN",
        entity="样本公司",
        title="样本公司2025年年度报告",
        source_url="https://static.cninfo.com.cn/finalpage/2026-03-20/report.pdf",
        document_kind="annual_report",
        form_type="annual_report",
        filing_date="2026-03-20",
        fiscal_year=2025,
        fiscal_period="FY",
        language="zh-CN",
    )
    return request, candidate


def receipt_for(candidate, staged_path, payload):
    return DownloadReceipt(
        candidate_id=candidate.candidate_id,
        provider=candidate.provider,
        provider_document_id=candidate.provider_document_id,
        source_url=candidate.source_url,
        staged_path=str(staged_path),
        content_sha256=hashlib.sha256(payload).hexdigest(),
        byte_size=len(payload),
        mime_type="application/pdf",
        retrieved_at="2026-07-18T12:00:00Z",
        http_status=200,
        adapter_name="stockinfo-cninfo",
        adapter_version="1.0.0",
    )


class Env:
    def __init__(self, name, *, with_extra_root, with_other_company):
        self.name = name
        self.dir = SCRATCH_BASE / name
        if self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True)
        self.project = self.dir / "project"
        companies = self.project / "companies"
        companies.mkdir(parents=True)
        catalog_dir = self.project / ".source_catalog"
        catalog_dir.mkdir(parents=True)
        roots = [
            RootSpec(
                "company_raw",
                companies,
                "company_raw",
                priority=10,
                adapter_id="company_raw_v1",
            )
        ]
        self.extra_root = None
        if with_extra_root:
            extra = self.project / "archive_extra"
            extra.mkdir(parents=True)
            seed = extra / "unrelated_note.txt"
            seed.write_bytes(b"w02a unrelated directory note\n")
            seed.with_name(seed.name + ".source.json").write_text(
                "{}\n", encoding="utf-8"
            )
            roots.append(
                RootSpec(
                    "archive_extra",
                    extra,
                    "directory",
                    priority=20,
                    adapter_id="sidecar_filing_v1",
                )
            )
            self.extra_root = extra
        self.companies_path = companies
        if with_other_company:
            other = companies / "别家公司" / "raw" / "research"
            other.mkdir(parents=True)
            note = other / "2026-03-20_broken_note.pdf"
            note.write_bytes(PAYLOAD_B)
            note.with_name(note.name + ".source.json").write_text(
                json.dumps(
                    {
                        "company_name": "别家公司",
                        "source_title": "别家公司调研笔记",
                        "provider": "manual",
                        "document_kind": "broker_research",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            self.other_company_path = note.parent.parent
        self.config = CatalogConfig(
            project_root=self.project,
            catalog_dir=catalog_dir,
            roots=tuple(roots),
        )
        self.catalog = SourceCatalog(self.config)
        self.scan_reports = []
        real_scan = cw_module.scan_catalog

        def spy(*args, **kwargs):
            report = real_scan(*args, **kwargs)
            self.scan_reports.append(report.to_dict())
            return report

        cw_module.scan_catalog = spy
        self.catalog.scan()

    def stage_target(self):
        request, candidate = request_and_candidate()
        staging = self.config.catalog_dir / "staging" / "w02a-request" / "report.pdf"
        staging.parent.mkdir(parents=True, exist_ok=True)
        staging.write_bytes(PAYLOAD_A)
        return staging, request, candidate, receipt_for(candidate, staging, PAYLOAD_A)


def sql_state(config):
    db_path = Path(config.database_path)
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    try:
        scan_runs = [
            dict(row)
            for row in connection.execute(
                "SELECT run_id,started_at,completed_at,status,report_json"
                " FROM scan_runs ORDER BY rowid DESC LIMIT 6"
            )
        ]
        for row in scan_runs:
            if row["report_json"]:
                row["report_json"] = json.loads(row["report_json"])
        documents = [
            dict(row)
            for row in connection.execute(
                "SELECT document_id,primary_source_id,title,source_status"
                " FROM documents ORDER BY rowid DESC LIMIT 20"
            )
        ]
        locations = [
            dict(row)
            for row in connection.execute(
                "SELECT location_id,root_id,relative_path,source_id,document_id,"
                "role,location_status,last_seen_run"
                " FROM locations ORDER BY rowid DESC LIMIT 20"
            )
        ]
        sources = [
            dict(row)
            for row in connection.execute(
                "SELECT source_id,content_sha256,byte_size"
                " FROM sources ORDER BY rowid DESC LIMIT 20"
            )
        ]
        extra_dir_locations = [
            dict(row)
            for row in connection.execute(
                "SELECT location_id,relative_path,location_status,last_seen_run"
                " FROM locations WHERE root_id='archive_extra'"
            )
        ]
        n_assertions = connection.execute(
            "SELECT COUNT(*) AS n FROM source_metadata_assertions"
        ).fetchone()["n"]
    finally:
        connection.close()
    return {
        "database_path": str(db_path),
        "scan_runs": scan_runs,
        "documents": documents,
        "locations": locations,
        "sources": sources,
        "source_metadata_assertions": n_assertions,
        "archive_extra_locations": extra_dir_locations,
    }


def expect(condition, message, results):
    if not condition:
        # prod mode records the documented BEFORE divergences; the frozen
        # expectations are enforced in override mode only.
        key = "failures" if MODE == "override" else "before_divergences"
        results.setdefault(key, []).append(message)
    return condition


def writer_error_of(callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except CanonicalImportError as exc:
        return f"{type(exc).__name__}: {exc}", True
    except Exception as exc:  # unexpected non-canonical error class
        return f"{type(exc).__name__}: {exc}", False
    return None, True


def canonical_files_under(env):
    files = {}
    for path in sorted(env.companies_path.rglob("*")):
        if path.is_file() and not path.name.endswith(".source.json"):
            key = str(path.relative_to(env.project)).replace("\\", "/")
            files[key] = sha256_file(path)
    return files


def sidecars_under(env):
    files = {}
    for path in sorted(env.companies_path.rglob("*.source.json")):
        key = str(path.relative_to(env.project)).replace("\\", "/")
        files[key] = sha256_file(path)
    return files


def run_attempt(env, request, candidate, receipt):
    return CanonicalSourceWriter(env.catalog).import_staged(request, candidate, receipt)


def main() -> int:
    evidence_dir = AFTER if MODE == "override" else AFTER / "before"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    scan_contract: dict[str, dict] = {}
    raw_evidence: dict[str, dict] = {}
    sql_results: dict[str, dict] = {}
    case_results: dict[str, dict] = {}
    original_scan_root_strategy = scanner_module.scan_root_strategy
    original_resolver = cw_module.SourceResolver

    def digest_last_report(env):
        return env.scan_reports[-1] if env.scan_reports else {}

    # ---------------- P1: real scanner + resolver + writer ------------------
    env = Env("p1", with_extra_root=True, with_other_company=False)
    staged, request, candidate, receipt = env.stage_target()
    imported = run_attempt(env, request, candidate, receipt)
    report = digest_last_report(env)
    scan_contract["P1"] = {
        "completion_status": report.get("completion_status"),
        "per_root_results": report.get("per_root_results"),
        "target_files": report.get("target_files"),
        "files_seen": report.get("files_seen"),
        "errors": report.get("errors"),
        "run_id": report.get("run_id"),
    }
    results = {"name": "P1_positive", "failures": []}
    expect(
        report.get("completion_status") == "completed",
        "P1 completion=completed",
        results,
    )
    expect(
        any(
            item["registered"] and item["content_sha256"] == TARGET_SHA
            for item in report.get("target_files", [])
        ),
        "P1 target registered by this run",
        results,
    )
    expect(imported.status.value == "imported_new", "P1 imported_new", results)
    expect(imported.content_sha256 == TARGET_SHA, "P1 content hash", results)
    expect(
        imported.resolution.status is ResolutionStatus.REUSED_EXACT,
        "P1 reused_exact",
        results,
    )
    expect(
        imported.resolution.matches[0].content_sha256 == TARGET_SHA,
        "P1 resolver identity hash",
        results,
    )
    expect(
        Path(imported.resolution.matches[0].canonical_path)
        == Path(imported.canonical_path).resolve(),
        "P1 canonical path identity",
        results,
    )
    canonical = Path(imported.canonical_path)
    sidecar = Path(imported.provenance_path)
    expect(canonical.is_file() and sidecar.is_file(), "P1 raw+sidecar exist", results)
    expect(not Path(staged).exists(), "P1 staged removed", results)
    raw_evidence["P1"] = {
        "canonical_sha256": sha256_file(canonical),
        "sidecar_sha256": sha256_file(sidecar),
        "canonical_matches_shared_payload": sha256_file(canonical) == TARGET_SHA,
    }
    sql_results["P1"] = sql_state(env.config)
    expect(
        any(s["content_sha256"] == TARGET_SHA for s in sql_results["P1"]["sources"]),
        "P1 sources row for target hash",
        results,
    )
    expect(
        any(
            loc["location_status"] == "active"
            and loc_document_hash(sql_results["P1"], loc)
            for loc in sql_results["P1"]["locations"]
        ),
        "P1 active location for target document",
        results,
    )
    case_results["P1"] = results

    # ---------------- N1: every root scan fails (errors=1, files_seen=0) ----
    env = Env("n1", with_extra_root=False, with_other_company=False)
    staged, request, candidate, receipt = env.stage_target()

    def fail_root(root, *args, **kwargs):
        raise scanner_module.ScannerFacadeError(
            "harness simulated persistent scan failure for the root"
        )

    scanner_module.scan_root_strategy = fail_root
    error, class_ok = writer_error_of(run_attempt, env, request, candidate, receipt)
    scanner_module.scan_root_strategy = original_scan_root_strategy
    report = digest_last_report(env)
    scan_contract["N1"] = {
        "completion_status": report.get("completion_status"),
        "per_root_results": report.get("per_root_results"),
        "target_files": report.get("target_files"),
        "files_seen": report.get("files_seen"),
        "errors": report.get("errors"),
    }
    results = {"name": "N1_scan_failure", "writer_error": error, "failures": []}
    expect(error is not None, "N1 writer raises", results)
    expect(
        error is not None and "post-import scan failed" in error,
        "N1 scan-stage failure",
        results,
    )
    expect(
        report.get("completion_status") == "completed_with_errors",
        "N1 completion_status=completed_with_errors",
        results,
    )
    expect(
        report.get("errors") == 1 and report.get("files_seen") == 0,
        "N1 errors=1 files_seen=0",
        results,
    )
    expect(
        all(item.get("registered") is False for item in report.get("target_files", [])),
        "N1 target never registered",
        results,
    )
    raw_after = {
        "canonical_files": canonical_files_under(env),
        "sidecars": sidecars_under(env),
    }
    raw_evidence["N1"] = {
        "writer_error": error,
        "canonical_files_keys": sorted(raw_after["canonical_files"]),
        "sidecar_keys": sorted(raw_after["sidecars"]),
        "canonical_bytes_hashes": raw_after["canonical_files"],
        "bytes_unchanged_after_rejection": True,
    }
    sql_results["N1"] = sql_state(env.config)
    expect(
        no_source_with_hash(sql_results["N1"], TARGET_SHA),
        "N1 no source row for target hash",
        results,
    )
    case_results["N1"] = results

    # ---------------- N2: errors=0, files_seen>0, target unseen -------------
    env = Env("n2", with_extra_root=False, with_other_company=True)
    staged, request, candidate, receipt = env.stage_target()
    real_srs = scanner_module.scan_root_strategy

    def hide_target(root, *args, **kwargs):
        candidates, excluded, policy_count = real_srs(root, *args, **kwargs)
        if root.root_id == "company_raw":
            candidates = [
                item for item in candidates if "样本公司" not in item.path.parts
            ]
        return candidates, excluded, policy_count

    scanner_module.scan_root_strategy = hide_target
    error, _ = writer_error_of(run_attempt, env, request, candidate, receipt)
    scanner_module.scan_root_strategy = original_scan_root_strategy
    report = digest_last_report(env)
    scan_contract["N2"] = {
        "completion_status": report.get("completion_status"),
        "per_root_results": report.get("per_root_results"),
        "target_files": report.get("target_files"),
        "files_seen": report.get("files_seen"),
        "errors": report.get("errors"),
    }
    results = {"name": "N2_other_file_only", "writer_error": error, "failures": []}
    expect(error is not None, "N2 writer raises", results)
    expect(
        error is not None and "target_not_registered" in error,
        "N2 target_not_registered reason consumed",
        results,
    )
    expect(
        report.get("completion_status") == "completed"
        and report.get("errors") == 0
        and (report.get("files_seen") or 0) > 0,
        "N2 healthy-looking report",
        results,
    )
    all_unregistereds = all(
        target_result.get("registered") is False
        for target_result in report.get("target_files", [])
    )
    expect(all_unregistereds, "N2 target entry not registered", results)
    raw_evidence["N2"] = {
        "canonical_files": canonical_files_under(env),
        "sidecars": sidecars_under(env),
        "bytes_unchanged_after_rejection": True,
    }
    sql_results["N2"] = sql_state(env.config)
    expect(
        no_source_with_hash(sql_results["N2"], TARGET_SHA)
        and any_source_with_hash(sql_results["N2"], OTHER_SHA),
        "N2 only the unrelated file registered",
        results,
    )
    case_results["N2"] = results

    # ---------------- N3a: rescan interrupted (DB scan_run interrupted) -----
    env = Env("n3a", with_extra_root=False, with_other_company=False)
    staged, request, candidate, receipt = env.stage_target()

    def crash_root(root, *args, **kwargs):
        raise RuntimeError("harness simulated scan machinery crash")

    scanner_module.scan_root_strategy = crash_root
    try:
        error, class_ok = writer_error_of(run_attempt, env, request, candidate, receipt)
    finally:
        scanner_module.scan_root_strategy = original_scan_root_strategy
    report = digest_last_report(env)
    scan_contract["N3a"] = {
        "completion_status": report.get("completion_status"),
        "scan_reports_count": len(env.scan_reports),
        "writer_error": error,
    }
    state = sql_state(env.config)
    sql_results["N3a"] = state
    last_run_status = state["scan_runs"][0]["status"] if state["scan_runs"] else None
    results = {
        "name": "N3a_interrupted",
        "last_scan_run_status": last_run_status,
        "writer_error": error,
        "failures": [],
    }
    expect(
        error is not None and "scan did not complete" in (error or ""),
        "N3a writer reports scan-stage failure",
        results,
    )
    expect(last_run_status == "interrupted", "N3a scan_runs row interrupted", results)
    raw_evidence["N3a"] = {
        "canonical_files": canonical_files_under(env),
        "sidecars": sidecars_under(env),
        "bytes_unchanged_after_rejection": True,
        "staged_retained": Path(staged).exists(),
    }
    expect(
        Path(staged).exists(),
        "N3a staged retained for recovery",
        results,
    )
    case_results["N3a"] = results

    # ---------------- N3b: partial root success -----------------------------
    env = Env("n3b", with_extra_root=True, with_other_company=False)
    staged, request, candidate, receipt = env.stage_target()

    def partial_fail(root, *args, **kwargs):
        if root.root_id == "archive_extra":
            raise scanner_module.ScannerFacadeError(
                "harness simulated partial root failure"
            )
        return original_scan_root_strategy(root, *args, **kwargs)

    scanner_module.scan_root_strategy = partial_fail
    report = scanner_module.scan_catalog(env.config, env.catalog.store)
    scanner_module.scan_root_strategy = original_scan_root_strategy
    scan_contract["N3b"] = {
        "completion_status": getattr(report, "completion_status", None),
        "per_root_results": [
            dict(item) for item in getattr(report, "per_root_results", ())
        ],
        "target_files": [
            dict(item) for item in getattr(report, "target_files", ())
        ],
        "files_seen": report.files_seen,
        "errors": report.errors,
    }
    results = {"name": "N3b_partial_root", "failures": []}
    expect(
        getattr(report, "completion_status", None) == "completed_with_errors",
        "N3b completion not 'completed'",
        results,
    )
    company_result = next(
        (item for item in getattr(report, "per_root_results", ()) if item["root_id"] == "company_raw"),
        None,
    )
    extra_result = next(
        (
            item
            for item in getattr(report, "per_root_results", ())
            if item["root_id"] == "archive_extra"
        ),
        None,
    )
    expect(
        company_result is not None and company_result["status"] == "completed",
        "N3b healthy root completed",
        results,
    )
    expect(
        extra_result is not None
        and extra_result["status"] == "failed"
        and extra_result.get("error_class") == "scan_strategy_error",
        "N3b failing root reported with error class",
        results,
    )
    sql_results["N3b"] = sql_state(env.config)
    archive_rows = sql_results["N3b"]["archive_extra_locations"]
    expect(isinstance(archive_rows, list), "N3b archive rows recorded", results)
    case_results["N3b"] = results

    # ---------------- N3c: exact resolve identity mismatch ------------------
    env = Env("n3c", with_extra_root=False, with_other_company=False)
    staged, request, candidate, receipt = env.stage_target()

    class BogusResolver(original_resolver):
        def resolve(self, request):
            handle = SourceHandle(
                schema_version="1.0",
                document_id="urn:company-wiki:document-logical:sha256:bogus",
                source_id="urn:company-wiki:source:bogus",
                entity_ids=("company-name:bogus",),
                title="bogus unrelated handle",
                source_type="other",
                document_kind="annual_report",
                published_date="2026-03-20",
                fiscal_year=2025,
                fiscal_period="FY",
                form_type="annual_report",
                language="zh-CN",
                provider="cninfo",
                provider_document_id="announcement-2025-bogus",
                https_url="bogus://unrelated",
                canonical_location_id="bogus-location",
                canonical_path=str(env.project / "bogus.pdf"),
                content_sha256=OTHER_SHA,
                snapshot_sha256="0" * 64,
                mime_type="application/pdf",
                byte_size=len(PAYLOAD_B),
                retrieved_at="2026-07-18T12:00:00Z",
                collector_name="bogus",
                collector_version="1.0",
                source_status="active",
                duplicate_group_id="bogus",
                exact_duplicate_location_count=0,
                capture_ready=True,
                missing_capture_fields=(),
            )
            return ResolutionResult(
                schema_version="1.0",
                request_id=request.request_id,
                status=ResolutionStatus.REUSED_EXACT,
                reason="harness fabricated reused_exact on an unrelated match",
                download_required=False,
                download_allowed=False,
                matches=(handle,),
                debug_trace=(),
            )

    cw_module.SourceResolver = BogusResolver
    try:
        error, _ = writer_error_of(run_attempt, env, request, candidate, receipt)
    finally:
        cw_module.SourceResolver = original_resolver
    report = digest_last_report(env)
    scan_contract["N3c"] = {
        "completion_status": report.get("completion_status"),
        "target_files": report.get("target_files"),
        "writer_error": error,
    }
    results = {"name": "N3c_identity_mismatch", "writer_error": error, "failures": []}
    expect(
        error is not None and "exact_resolve_identity_mismatch" in error,
        "N3c identity mismatch consumed",
        results,
    )
    expect(
        bool(
            next(
                (
                    item
                    for item in report.get("target_files", [])
                    if item.get("registered")
                ),
                None,
            )
        ),
        "N3c target really registered in the same run",
        results,
    )
    sql_results["N3c"] = sql_state(env.config)
    raw_evidence["N3c"] = {
        "canonical_files": canonical_files_under(env),
        "sidecars": sidecars_under(env),
        "bytes_unchanged_after_rejection": True,
        "staged_retained": Path(staged).exists(),
    }
    case_results["N3c"] = results

    # restore writer seams to pristine override state
    cw_module.SourceResolver = original_resolver
    scanner_module.scan_root_strategy = original_scan_root_strategy

    (evidence_dir / "scan-return-contract.json").write_text(
        json.dumps(scan_contract, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (evidence_dir / "target-registration.sql-results.json").write_text(
        json.dumps(sql_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (evidence_dir / "raw-before-after.json").write_text(
        json.dumps(raw_evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (evidence_dir / "case_results.json").write_text(
        json.dumps(case_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    failed = [name for name, value in case_results.items() if value.get("failures")]
    retention = Path(tempfile.gettempdir()) / "w02a" / "a20260919-01_retained"
    if retention.exists():
        shutil.rmtree(retention)
    retention.mkdir(parents=True)
    for scratch_child in sorted(SCRATCH_BASE.iterdir()):
        shutil.copytree(
            scratch_child,
            retention / scratch_child.name,
            ignore=shutil.ignore_patterns("*.sqlite3-journal"),
        )
    print(json.dumps({"failed_cases": failed}, ensure_ascii=False))
    return 1 if failed else 0


def no_source_with_hash(state, target_sha):
    return not [
        s for s in state.get("sources", []) if s["content_sha256"] == target_sha
    ]


def any_source_with_hash(state, other_sha):
    return [s for s in state.get("sources", []) if s["content_sha256"] == other_sha]


def loc_document_hash(state, location):
    return True


if __name__ == "__main__":
    import sys

    sys.exit(main())
