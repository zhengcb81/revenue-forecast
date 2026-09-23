#!/usr/bin/env python
"""F-EE1-FIX judged harness — oracle.md cases (a), (b), (c), (d).

Constructs state locally through the SAME production writer paths the live
chain uses (unit-harness truth, NOT mock-live; zero network):

  SourceAcquisitionService.ensure            (cli.py:789-802)
    -> AcquisitionCoordinator.resolve_or_stage
    -> CanonicalSourceWriter.import_staged   (the divergent mint, E2)
    -> AcquisitionJournal.record             (the journal mint, E1)
  build_resolution_envelope(..., journal=..) (cli.py:812-819 ensure face)
  build_resolution_envelope(read-only)       (cli.py:1188-1195 resolve face)

All scratch state lives under the process temp dir (%TEMP%).  Exits 0 iff
every frozen case passes (GREEN); a fake download zero fails (a)/(c) (RED).

argv: --iso-cw-src PATH --ff-scripts PATH --out PATH [--label NAME]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path


# --------------------------------------------------------------------------
# controlled local adapter (inputs are local bytes; no network anywhere)
# --------------------------------------------------------------------------

class _LocalAdapter:
    name = "local-controlled"
    version = "1.0.0"

    def __init__(self) -> None:
        self.discover_calls = 0
        self.fetch_calls = 0

    def discover(self, request):
        from company_wiki.source_catalog import DownloadCandidate

        self.discover_calls += 1
        return (
            DownloadCandidate(
                candidate_id="local:ann-9001",
                provider="localprov",
                provider_document_id="ann-9001",
                market=request.market or "CN",
                entity=request.entity,
                title="示例公司2025年年度报告",
                source_url="https://example.invalid/local/ann-9001.pdf",
                document_kind="annual_report",
                form_type="annual_report",
                filing_date="2026-03-20",
                fiscal_year=2025,
                fiscal_period="FY",
                language="zh-CN",
                amended=False,
            ),
        )

    def fetch(self, candidate, staging_dir):
        from company_wiki.source_catalog import DownloadReceipt

        self.fetch_calls += 1
        path = staging_dir / "report.pdf"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = b"%PDF-1.7\n" + b"F-EE1 committed-download bytes\n" * 16
        path.write_bytes(payload)
        return DownloadReceipt(
            candidate_id=candidate.candidate_id,
            provider=candidate.provider,
            provider_document_id=candidate.provider_document_id,
            source_url=candidate.source_url,
            staged_path=str(path),
            content_sha256=hashlib.sha256(payload).hexdigest(),
            byte_size=len(payload),
            mime_type="application/pdf",
            retrieved_at="2026-07-18T12:00:00Z",
            http_status=200,
            adapter_name=self.name,
            adapter_version=self.version,
        )


def _make_catalog(root: Path):
    from company_wiki.source_catalog import CatalogConfig, RootSpec, SourceCatalog

    project = root / "project"
    companies = project / "companies"
    companies.mkdir(parents=True)
    catalog = SourceCatalog(
        CatalogConfig(
            project_root=project,
            catalog_dir=project / ".source_catalog",
            roots=(
                RootSpec(
                    "company_raw",
                    companies,
                    "company_raw",
                    priority=10,
                    adapter_id="company_raw_v1",
                ),
            ),
        )
    )
    catalog.scan()
    return catalog


def _make_service(catalog, adapter):
    from company_wiki.source_catalog import (
        AcquisitionCoordinator,
        AcquisitionJournal,
        AdapterRegistry,
        CanonicalSourceWriter,
        SourceAcquisitionService,
    )

    staging = catalog.config.catalog_dir / "staging"
    return SourceAcquisitionService(
        coordinator=AcquisitionCoordinator(
            catalog=catalog,
            adapters=AdapterRegistry(cn=adapter, hk=adapter, us=adapter),
            staging_root=staging,
        ),
        writer=CanonicalSourceWriter(catalog, staging_root=staging),
        journal=AcquisitionJournal(catalog.config.catalog_dir),
    )


def _ensure_face_envelope(catalog, resolution):
    """Mirror CW cli.py:804-819 (the ensure face that produced the fake 0)."""
    from company_wiki.source_catalog.acquisition_journal import AcquisitionJournal
    from company_wiki.source_catalog.resolver import build_resolution_envelope
    from company_wiki.source_catalog.runtime_policy import (
        RuntimePolicyError,
        load_runtime_policy,
    )

    try:
        policy = load_runtime_policy(
            catalog.config.catalog_dir / "runtime_policy.json")
    except RuntimePolicyError:
        policy = None
    return build_resolution_envelope(
        resolution,
        policy_snapshot=policy,
        journal=AcquisitionJournal(catalog.config.catalog_dir),
        bundle=catalog.bundle_for_resolution(resolution),
        store=catalog.store,
        project_root=catalog.config.project_root,
    )


def _resolve_face_envelope(catalog, resolution):
    """Mirror CW cli.py:1165-1195 (the read-only resolve face)."""
    from company_wiki.source_catalog.acquisition_journal import AcquisitionJournal
    from company_wiki.source_catalog.resolver import build_resolution_envelope
    from company_wiki.source_catalog.runtime_policy import (
        RuntimePolicyError,
        load_runtime_policy,
    )

    try:
        policy = load_runtime_policy(
            catalog.config.catalog_dir / "runtime_policy.json")
    except RuntimePolicyError:
        policy = None
    return build_resolution_envelope(
        resolution,
        policy_snapshot=policy,
        journal=AcquisitionJournal(catalog.config.catalog_dir),
        bundle=catalog.bundle_for_resolution(resolution),
        store=catalog.reader,
        project_root=catalog.config.project_root,
    )


def _check(case: dict, name: str, expected, actual) -> None:
    # journal-file comparisons pass raw bytes; record them as sha256 so the
    # evidence JSON stays serializable (equality semantics preserved).
    if isinstance(expected, bytes):
        expected = "sha256:" + hashlib.sha256(expected).hexdigest()
    if isinstance(actual, bytes):
        actual = "sha256:" + hashlib.sha256(actual).hexdigest()
    case["checks"].append(
        {"name": name, "expected": expected, "actual": actual,
         "ok": actual == expected})
    if actual != expected:
        case["failures"].append(name)


def _case(cid: str, title: str) -> dict:
    return {"id": cid, "title": title, "checks": [], "failures": [],
            "pass": False}


def _finalize(case: dict) -> dict:
    case["pass"] = not case["failures"]
    return case


def _dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


# --------------------------------------------------------------------------

def run(iso_cw_src: Path, ff_scripts: Path) -> dict:
    sys.path.insert(0, str(ff_scripts))
    sys.path.insert(0, str(iso_cw_src))

    from company_wiki.source_catalog import (
        AcquisitionJournal,
        SourceRequest,
        SourceResolver,
        SourceEnsureStatus,
    )
    import fetch_filing
    from filing_contracts import validate_resolution_envelope

    cases = [_case("a", "committed download is truthful (downloads==1)"),
             _case("b", "genuine reuse stays an honest zero"),
             _case("c", "request_id equality after committed download"),
             _case("d", "retry / second-resolve idempotency")]
    by_id = {c["id"]: c for c in cases}
    ctx: dict = {}

    work = Path(tempfile.mkdtemp(prefix="f_ee1_harness_"))
    try:
        # ---------------- shared state: one catalog, ensure#1 (download)
        catalog = _make_catalog(work)
        adapter = _LocalAdapter()
        service = _make_service(catalog, adapter)
        journal = AcquisitionJournal(catalog.config.catalog_dir)
        request = SourceRequest(
            entity="示例公司",
            market="CN",
            security_id="600000",
            document_kind="annual_report",
            fiscal_year=2025,
            as_of_date="2026-07-18",
            allow_download=True,
        )
        ctx["request_id"] = request.request_id

        first = service.ensure(request)
        rows_after_first = list(journal.read_all())
        download_rows = [r for r in rows_after_first
                         if r.outcome == "downloaded_new"]
        row1 = download_rows[-1] if download_rows else None
        env1 = _ensure_face_envelope(catalog, first.resolution)

        # ---- case (a): the download run must be truthful end-to-end
        c = by_id["a"]
        _check(c, "a1_ensure_status_is_imported",
               SourceEnsureStatus.IMPORTED.value, first.status.value)
        _check(c, "a1_adapter_fetch_calls", 1, adapter.fetch_calls)
        _check(c, "a2_journal_has_one_downloaded_new", 1, len(download_rows))
        _check(c, "a2_journal_row_keyed_to_original_request",
               request.request_id, row1.request_id if row1 else None)
        _check(c, "a3_resolution_id_matches_journal_row",
               row1.request_id if row1 else None,
               first.resolution.request_id)
        _check(c, "a4_envelope_outcome_downloaded_new",
               "downloaded_new", env1.outcome)
        _check(c, "a5_envelope_download_events", 1, env1.download_events)
        stats: dict = {}
        fetch_filing._record_download_events(
            stats, {"resolution_envelope": env1.to_dict()})
        _check(c, "a6_ff_record_download_events_downloads", 1,
               stats.get("downloads"))
        try:
            validate_resolution_envelope(env1.to_dict())
            accepted, detail = True, None
        except Exception as exc:  # noqa: BLE001
            accepted, detail = False, f"{type(exc).__name__}: {exc}"
        _check(c, "a7_ff_accepts_envelope", True, accepted)
        if detail:
            c["checks"][-1]["envelope_error"] = detail

        # a8: read-only resolve face immediately after ensure#1 (journal holds
        # exactly the one downloaded_new row) — green in BOTH arms.
        ro1 = SourceResolver(catalog).resolve(request)
        env_ro1 = _resolve_face_envelope(catalog, ro1)
        _check(c, "a8_readonly_face_outcome_downloaded_new",
               "downloaded_new", env_ro1.outcome)
        _check(c, "a8_readonly_face_download_events", 1,
               env_ro1.download_events)

        # ---- case (c): three-way request_id equality (ruling face)
        c = by_id["c"]
        resolution_dict = first.resolution.to_dict()
        _check(c, "c1_request_id_equals_journal_row_id",
               row1.request_id if row1 else None, resolution_dict["request_id"])
        _check(c, "c2_resolution_dict_id_equals_original_request_id",
               request.request_id, resolution_dict["request_id"])
        _check(c, "c3_journal_row_id_equals_original_request_id",
               request.request_id,
               row1.request_id if row1 else None)
        # fetch_filing.py:880 — the FF handle copies this exact field.
        _check(c, "c4_ff_handle_would_carry_matching_id",
               row1.request_id if row1 else None,
               resolution_dict["request_id"])

        # ---- case (d): determinism + zero-write before mutating further
        c = by_id["d"]
        journal_bytes_before = journal.path.read_bytes()
        env_ro1b = _resolve_face_envelope(catalog, ro1)
        _check(c, "d2_envelope_rebuild_byte_identical",
               _dumps(env_ro1.to_dict()), _dumps(env_ro1b.to_dict()))
        _check(c, "d3_envelope_build_does_not_write_journal",
               journal_bytes_before, journal.path.read_bytes())

        # ---- case (b1) + (d1): second ensure of the same request (reuse)
        second = service.ensure(request)
        rows_after_second = list(journal.read_all())
        env2 = _ensure_face_envelope(catalog, second.resolution)
        outcomes = [r.outcome for r in rows_after_second]

        c = by_id["b"]
        _check(c, "b1_second_ensure_status_reused",
               SourceEnsureStatus.REUSED.value, second.status.value)
        _check(c, "b1_latest_journal_row_reused_before_download",
               "reused_before_download",
               rows_after_second[-1].outcome if rows_after_second else None)
        _check(c, "b1_envelope_outcome_reused_existing",
               "reused_existing", env2.outcome)
        _check(c, "b1_envelope_download_events_zero", 0, env2.download_events)
        b_stats: dict = {}
        fetch_filing._record_download_events(
            b_stats, {"resolution_envelope": env2.to_dict()})
        _check(c, "b1_ff_downloads_stays_zero", 0, b_stats.get("downloads"))

        c = by_id["d"]
        _check(c, "d1_adapter_fetch_calls_still_one", 1, adapter.fetch_calls)
        _check(c, "d1_downloaded_new_row_count", 1,
               outcomes.count("downloaded_new"))
        _check(c, "d1_journal_row_count", 2, len(outcomes))
        _check(c, "d1_journal_outcomes_deterministic",
               ["downloaded_new", "reused_before_download"], outcomes)
        # read-only face again after ensure#2: latest matching row wins
        # (reused_before_download) — deterministic, no new rows, no writes.
        jb2 = journal.path.read_bytes()
        ro2 = SourceResolver(catalog).resolve(request)
        env_ro2 = _resolve_face_envelope(catalog, ro2)
        _check(c, "d3_second_readonly_face_deterministic",
               "reused_existing", env_ro2.outcome)
        _check(c, "d3_second_readonly_face_zero_download_events",
               0, env_ro2.download_events)
        _check(c, "d3_journal_unchanged_after_second_resolve_face",
               jb2, journal.path.read_bytes())

        # ---- case (b2): fresh catalog, scan-seeded reuse, EMPTY journal
        b2_root = Path(tempfile.mkdtemp(prefix="f_ee1_b2_", dir=work.parent))
        try:
            raw = (b2_root / "project" / "companies" / "示例公司" / "raw"
                   / "financial_reports" / "annual")
            raw.mkdir(parents=True)
            report = raw / "2026-02-20_localprov_2025_annual_report.txt"
            report.write_text("existing audited annual report", encoding="utf-8")
            sidecar = report.with_suffix(".txt.source.json")
            sidecar.write_text(json.dumps({
                "market": "CN", "security_id": "600000",
                "source_title": "示例公司2025年年度报告",
                "source_url": "https://example.invalid/local/ann-9001.pdf",
                "fiscal_year": 2025, "fiscal_period": "FY",
                "form_type": "annual_report", "document_kind": "annual_report",
                "provider": "localprov",
                "provider_document_id": "ann-9001",
            }, ensure_ascii=False), encoding="utf-8")
            catalog2 = _make_catalog(b2_root)
            ro = SourceResolver(catalog2).resolve(request)
            env_b2 = _resolve_face_envelope(catalog2, ro)
            c = by_id["b"]
            _check(c, "b2_fresh_catalog_readonly_status_reused",
                   True, ro.status.value in ("reused_exact", "reused_equivalent"))
            _check(c, "b2_fresh_catalog_envelope_outcome",
                   "reused_existing", env_b2.outcome)
            _check(c, "b2_fresh_catalog_download_events_zero", 0,
                   env_b2.download_events)
        finally:
            import shutil

            shutil.rmtree(b2_root, ignore_errors=True)

        ctx.update({
            "journal_outcomes": [r.outcome for r in journal.read_all()],
            "ensure1_resolution_id": first.resolution.request_id,
            "ensure1_resolution_status": first.resolution.status.value,
            "ensure1_envelope": env1.to_dict(),
            "ff_stats_downloads_after_download": stats.get("downloads"),
            "work_root": str(work),
        })
    except Exception:  # noqa: BLE001
        ctx["harness_exception"] = traceback.format_exc()
        for case in cases:
            if not case["checks"]:
                case["checks"].append(
                    {"name": "harness_ran_to_completion", "expected": True,
                     "actual": False, "ok": False})
                case["failures"].append("harness_ran_to_completion")
    finally:
        import shutil

        shutil.rmtree(work, ignore_errors=True)

    for case in cases:
        _finalize(case)
    overall = all(case["pass"] for case in cases)
    return {
        "harness": "F-EE1-FIX run_cases",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "iso_cw_src": str(iso_cw_src),
        "ff_scripts": str(ff_scripts),
        "cases": cases,
        "context": ctx,
        "overall_pass": overall,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iso-cw-src", type=Path, required=True)
    ap.add_argument("--ff-scripts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--label", default="run")
    args = ap.parse_args(argv)

    result = run(args.iso_cw_src, args.ff_scripts)
    result["label"] = args.label
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    for case in result["cases"]:
        status = "PASS" if case["pass"] else "FAIL"
        print(f"[{status}] ({case['id']}) {case['title']}"
              + (f"  failures={case['failures']}" if case["failures"] else ""))
    print(f"[{'GREEN' if result['overall_pass'] else 'RED'}] "
          f"overall_pass={result['overall_pass']} -> {args.out}")
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
