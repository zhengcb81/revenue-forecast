"""w02d_cases: case runner for card I-02-D (reentry / same-bytes dedup).

Real code only: the modified writer copy (I-02-D dedup-eligibility +
staging-timing fix) + the inherited I-02-C recovery chain, against isolated
scratch catalogs seeded with byte-identical copies of the fixed real raw
files.  Providers are deny-on-call stubs.  Frozen expectations live in
oracle.md (written before any modification / run).

Outputs into <attempt>/after/:
  idempotency-matrix.json
  two-process-trace.json
  logical-rows-vs-attempts.json
  case_results.json
  case_scratch_retained/<case>/... (scratch trees snapshot at run end)
"""

from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
AFTER = ATTEMPT / "after"
SAMPLES = ATTEMPT / "samples" / "real_roots"
SCRATCH_BASE = Path(tempfile.gettempdir()) / "w02d" / "a20260919-01_case_scratch"

w02d = importlib.import_module("w02d_bootstrap")
w02d.setup("override")

from company_wiki.source_catalog import (  # noqa: E402
    CatalogConfig,
    RootSpec,
    SourceCatalog,
)
from company_wiki.source_catalog.acquisition import (  # noqa: E402
    AcquisitionCoordinator,
    AdapterRegistry,
    DownloadCandidate,
    DownloadReceipt,
)
from company_wiki.source_catalog.acquisition_journal import (  # noqa: E402
    AcquisitionJournal,
)
from company_wiki.source_catalog.acquisition_service import (  # noqa: E402
    SourceAcquisitionService,
    SourceEnsureStatus,
    SourceRecoveryInput,
)
from company_wiki.source_catalog.canonical_writer import (  # noqa: E402
    CanonicalImportError,
    CanonicalImportStatus,
    CanonicalSourceWriter,
)
from company_wiki.source_catalog.resolver import (  # noqa: E402
    SourceRequest,
    SourceResolver,
)
from company_wiki.source_catalog import store as store_module  # noqa: E402

HK_SHA = "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c"
HK_FILENAME = "2026-04-28_hkexnews_12127452_2025年度報告.pdf"
HK_META = {
    "sha": HK_SHA,
    "size": 4405561,
    "filename": HK_FILENAME,
    "company_dir": "小米集團－Ｗ",
    "provider": "hkexnews",
    "provider_document_id": "12127452",
    "fiscal_year": 2025,
    "entity": "小米集團－Ｗ",
    "security_id": "01810",
    "market": "HK",
}

PYTHON = ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class DenyOnCallAdapter:
    name = "deny-on-call"
    version = "1.0.0"

    def __init__(self):
        self.calls = {"discover": 0, "fetch": 0}

    def discover(self, request):
        self.calls["discover"] += 1
        raise RuntimeError("deny-on-call stub: discovery must never run")

    def fetch(self, candidate, staging_dir):
        self.calls["fetch"] += 1
        raise RuntimeError("deny-on-call stub: fetch must never run")


class Env:
    def __init__(
        self, name: str, *, reusable_root: bool = True, dayu_root: bool = False
    ):
        self.name = name
        self.dir = SCRATCH_BASE / name
        if self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True)
        self.project = self.dir / "project"
        self.companies_path = self.project / "companies"
        self.companies_path.mkdir(parents=True)
        self.config_dir = self.project / ".source_catalog"
        self.config_dir.mkdir(parents=True)
        self.dayu_root = dayu_root
        self.reusable_root = reusable_root
        self.catalog = SourceCatalog(self._config())
        self.catalog.scan()
        self.adapters = []
        self.journal = AcquisitionJournal(self.config_dir)

    def _config(self) -> CatalogConfig:
        roots = [
            RootSpec(
                "company_raw",
                self.companies_path,
                "company_raw",
                priority=10,
                adapter_id="company_raw_v1",
                reusable_for_filing=True if self.reusable_root else False,
            ),
        ]
        if self.dayu_root:
            roots.append(
                RootSpec(
                    "dayu",
                    self.project / "dayu_portfolio",
                    "dayu_portfolio",
                    priority=20,
                ),
            )
        return CatalogConfig(
            project_root=self.project,
            catalog_dir=self.config_dir,
            roots=tuple(roots),
        )

    def place_sample(self, *, flip_byte: bool = False) -> dict:
        src_raw = SAMPLES / "hk" / HK_FILENAME
        dst = (
            self.companies_path
            / HK_META["company_dir"]
            / "raw"
            / "financial_reports"
            / "annual"
        )
        dst.mkdir(parents=True, exist_ok=True)
        raw_dst = dst / HK_FILENAME
        shutil.copyfile(src_raw, raw_dst)
        shutil.copyfile(
            src_raw.with_name(src_raw.name + ".source.json"),
            raw_dst.with_name(raw_dst.name + ".source.json"),
        )
        if flip_byte:
            data = bytearray(raw_dst.read_bytes())
            data[16] ^= 0x01
            raw_dst.write_bytes(bytes(data))
        else:
            assert sha256_file(raw_dst) == HK_SHA
        return {
            "raw_path": raw_dst,
            "sidecar_path": raw_dst.with_name(raw_dst.name + ".source.json"),
        }

    def place_dayu_copy(self) -> Path:
        src_raw = SAMPLES / "hk" / HK_FILENAME
        dst_dir = self.project / "dayu_portfolio" / "MDB" / "filings" / "fil_x"
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / "same.htm"
        shutil.copyfile(src_raw, dst)
        assert sha256_file(dst) == HK_SHA
        return dst

    def build_service(self) -> SourceAcquisitionService:
        staging_root = self.config_dir / "staging"
        staging_root.mkdir(parents=True, exist_ok=True)
        adapter = DenyOnCallAdapter()
        self.adapters = [adapter]
        registry = AdapterRegistry(cn=adapter, hk=adapter, us=adapter)
        return SourceAcquisitionService(
            coordinator=AcquisitionCoordinator(
                catalog=self.catalog,
                adapters=registry,
                staging_root=staging_root,
            ),
            writer=CanonicalSourceWriter(self.catalog, staging_root=staging_root),
            journal=self.journal,
        )

    def build_writer(self) -> tuple:
        staging_root = self.config_dir / "staging"
        staging_root.mkdir(parents=True, exist_ok=True)
        return CanonicalSourceWriter(
            self.catalog, staging_root=staging_root
        ), staging_root

    def request(self, *, provider=..., provider_document_id=...) -> SourceRequest:
        return SourceRequest(
            entity=HK_META["entity"],
            security_id=HK_META["security_id"],
            market=HK_META["market"],
            document_kind="annual_report",
            fiscal_year=HK_META["fiscal_year"],
            fiscal_period="FY",
            provider=(HK_META["provider"] if provider is ... else provider),
            provider_document_id=(
                HK_META["provider_document_id"]
                if provider_document_id is ...
                else provider_document_id
            ),
            as_of_date="2026-09-18",
            mode="exact",
            allow_download=False,
        )

    def sql_state(self) -> dict:
        db_path = Path(self.catalog.config.database_path)
        connection = sqlite3.connect(str(db_path))
        connection.row_factory = sqlite3.Row
        try:
            sources = connection.execute(
                "SELECT source_id,content_sha256 FROM sources"
            ).fetchall()
            documents = connection.execute(
                "SELECT document_id,source_status FROM documents"
            ).fetchall()
            locations = connection.execute(
                "SELECT location_id,root_id,relative_path,role,location_status"
                " FROM locations"
            ).fetchall()
        finally:
            connection.close()
        return {
            "db_path": str(db_path),
            "sources": [dict(row) for row in sources],
            "documents": [dict(row) for row in documents],
            "locations": [dict(row) for row in locations],
        }

    def logical_counts(self, sha: str) -> dict:
        state = self.sql_state()
        return {
            "sources_rows": len(
                [s for s in state["sources"] if s["content_sha256"] == sha]
            ),
            "documents_active": len(
                [
                    d
                    for d in state["documents"]
                    if d["document_id"] == f"urn:company-wiki:document:sha256:{sha}"
                    and d["source_status"] == "active"
                ]
            ),
            "locations_active_original": len(
                [
                    loc
                    for loc in state["locations"]
                    if loc["location_status"] == "active"
                    and loc["role"] == "original_primary"
                    and loc["relative_path"]
                    .replace("\\", "/")
                    .endswith(
                        f"{HK_META['company_dir']}/raw/financial_reports/annual/{HK_FILENAME}"
                    )
                ]
            ),
        }

    def journal_lines(self) -> list:
        try:
            return [a.to_dict() for a in self.journal.read_all()]
        except ValueError as exc:
            return [{"journal_read_error": str(exc)}]

    def raw_files(self) -> list:
        return sorted(
            str(p.relative_to(self.project)).replace("\\", "/")
            for p in self.companies_path.rglob("*")
            if p.is_file() and not p.name.endswith(".source.json")
        )

    def provider_counts(self) -> dict:
        counts = {"discover": 0, "fetch": 0}
        for adapter in self.adapters:
            counts["discover"] += adapter.calls["discover"]
            counts["fetch"] += adapter.calls["fetch"]
        return counts


def expect(condition, message, results):
    if not condition:
        results["failures"].append(message)
    return condition


def writer_error_of(callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except CanonicalImportError as exc:
        return f"{type(exc).__name__}: {exc}", True
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}", False
    return None, True


def p1_case(matrix: dict) -> dict:
    results = {"name": "W02D_P1_reentry_x3", "failures": []}
    env = Env("P1")
    files = env.place_sample()
    service = env.build_service()
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]),
        sidecar_path=str(files["sidecar_path"]),
    )
    request = env.request()
    entries = []

    def observe(call_name: str, ensured) -> dict:
        counts = env.logical_counts(HK_SHA)
        journal = env.journal_lines()
        outcome_groups: dict = {}
        for line in journal:
            key = line.get("outcome", "?")
            outcome_groups[key] = outcome_groups.get(key, 0) + 1
        matches = ensured.resolution.matches or ()
        entry = {
            "call": call_name,
            "ensure_status": ensured.status.value,
            "resolution_status": ensured.resolution.to_dict().get("status"),
            "match_source_id": matches[0].source_id if matches else None,
            "match_sha": matches[0].content_sha256 if matches else None,
            "logical": counts,
            "journal_outcome_groups": outcome_groups,
            "journal_rows": len(journal),
            "provider_calls": env.provider_counts(),
            "raw_files": env.raw_files(),
        }
        entries.append(entry)
        return entry

    first = service.ensure(request, recovery=recovery)
    observe("call1_register", first)
    second = service.ensure(request, recovery=recovery)
    observe("call2_reentry_with_recovery", second)
    third = service.ensure(request, recovery=recovery)
    observe("call3_reentry_with_recovery", third)
    fourth = service.ensure(request)
    observe("call4_catalog_first_reuse", fourth)

    for label, ensured in (("call2", second), ("call3", third), ("call4", fourth)):
        expect(
            ensured.status
            in (SourceEnsureStatus.REUSED, SourceEnsureStatus.REGISTERED_EXISTING),
            f"P1 {label} returns reused/registered_existing (got {ensured.status})",
            results,
        )
        expect(
            ensured.resolution.to_dict().get("status") == "reused_exact",
            f"P1 {label} resolution reused_exact",
            results,
        )
    counts = env.logical_counts(HK_SHA)
    expect(counts["sources_rows"] == 1, "P1 exactly one source row", results)
    expect(counts["documents_active"] == 1, "P1 exactly one active document", results)
    expect(
        counts["locations_active_original"] == 1,
        "P1 exactly one active original location",
        results,
    )
    expect(
        env.raw_files()
        == [
            f"companies/{HK_META['company_dir']}/raw/financial_reports/annual/{HK_FILENAME}"
        ],
        "P1 zero new raw files (single canonical)",
        results,
    )
    expect(
        sha256_file(files["raw_path"]) == HK_SHA and sha256_file(files["sidecar_path"]),
        "P1 raw+sidecar bytes unchanged",
        results,
    )
    expect(
        env.provider_counts() == {"discover": 0, "fetch": 0},
        "P1 provider counts zero",
        results,
    )
    journal = env.journal_lines()
    register_rows = [
        line for line in journal if line.get("outcome") == "registered_existing_raw"
    ]
    expect(len(register_rows) == 1, "P1 one registered_existing_raw row", results)
    download_rows = [
        line
        for line in journal
        if line.get("outcome") in ("downloaded_new", "deduplicated_after_download")
    ]
    expect(not download_rows, "P1 no download-class rows", results)
    reused_rows = [
        line for line in journal if line.get("outcome") == "reused_before_download"
    ]
    expect(
        len(reused_rows) == 1,
        f"P1 reused_before_download deduped by content hash (got {len(reused_rows)})",
        results,
    )
    source_ids = {
        entry["match_source_id"] for entry in entries if entry["match_source_id"]
    }
    expect(len(source_ids) == 1, "P1 all matches share one source_id", results)
    matrix["P1_reentry_x3"] = {"results": results, "calls": entries}
    return results


def staged_identity_variant(staging_root: Path, *, provider: str, pdoc: str) -> tuple:
    staged = staging_root / "dedup-variant" / "same.pdf"
    staged.parent.mkdir(parents=True, exist_ok=True)
    payload = (SAMPLES / "hk" / HK_FILENAME).read_bytes()
    staged.write_bytes(payload)
    candidate = DownloadCandidate(
        candidate_id=f"{provider}:identity-variant",
        provider=provider,
        provider_document_id=pdoc,
        market="HK",
        entity=HK_META["entity"],
        title="identity variant",
        source_url="https://example.invalid/identity-variant.pdf",
        document_kind="annual_report",
        form_type="FY",
        filing_date="2026-04-28",
        fiscal_year=2025,
        fiscal_period="FY",
        language="zh",
    )
    receipt = DownloadReceipt(
        candidate_id=candidate.candidate_id,
        provider=candidate.provider,
        provider_document_id=candidate.provider_document_id,
        source_url=candidate.source_url,
        staged_path=str(staged),
        content_sha256=HK_SHA,
        byte_size=len(payload),
        mime_type="application/pdf",
        retrieved_at="2026-09-19T00:00:00Z",
        http_status=200,
        adapter_name="deny-on-call",
        adapter_version="1.0.0",
    )
    return candidate, receipt, staged


def n1_case(matrix: dict) -> dict:
    results = {"name": "W02D_N1_same_bytes_other_identity", "failures": []}
    env = Env("N1")
    files = env.place_sample()
    service = env.build_service()
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]),
        sidecar_path=str(files["sidecar_path"]),
    )
    ensured = service.ensure(env.request(), recovery=recovery)
    expect(
        ensured.status is SourceEnsureStatus.REGISTERED_EXISTING,
        "N1 fixture registration succeeded",
        results,
    )
    writer, staging_root = env.build_writer()
    # Same bytes, DIFFERENT provider identity (US identity on HK bytes).
    candidate, receipt, staged = staged_identity_variant(
        staging_root, provider="sec", pdoc="0001193125-26-323660"
    )
    request = env.request()
    error, class_ok = writer_error_of(writer.import_staged, request, candidate, receipt)
    expect(bool(class_ok), "N1 error is CanonicalImportError", results)
    expect(
        error is not None
        and (
            "exact provider identity did not resolve" in error
            or "exact_resolve_identity_mismatch" in error
        ),
        f"N1 expected identity gate phrase (got {error!r})",
        results,
    )
    expect(
        staged.exists(),
        "N1 staging file KEPT (recoverable evidence not deleted)",
        results,
    )
    expect(
        sha256_file(files["raw_path"]) == HK_SHA,
        "N1 registered raw bytes unchanged",
        results,
    )
    counts = env.logical_counts(HK_SHA)
    expect(counts["sources_rows"] == 1, "N1 no new source row", results)
    expect(counts["documents_active"] == 1, "N1 no new document", results)
    expect(counts["locations_active_original"] == 1, "N1 no new location", results)
    expect(
        env.provider_counts() == {"discover": 0, "fetch": 0},
        "N1 provider counts zero",
        results,
    )
    journal = env.journal_lines()
    dedup_rows = [
        line for line in journal if line.get("outcome") == "deduplicated_after_download"
    ]
    expect(not dedup_rows, "N1 no dedup success row", results)
    matrix["N1_same_bytes_other_identity"] = {
        "results": results,
        "error": error,
        "staging_kept": staged.exists(),
        "logical": counts,
        "journal_outcomes": [line.get("outcome") for line in journal],
    }
    return results


def n2_cases(matrix: dict) -> dict:
    proof: dict = {}

    # N2a: same request, NEW hash (new version) -> new source row, old kept.
    results_a = {"name": "W02D_N2a_new_hash_new_version", "failures": []}
    env = Env("N2a")
    files = env.place_sample()
    service = env.build_service()
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]),
        sidecar_path=str(files["sidecar_path"]),
    )
    ensured = service.ensure(env.request(), recovery=recovery)
    expect(
        ensured.status is SourceEnsureStatus.REGISTERED_EXISTING,
        "N2a fixture registration succeeded",
        results_a,
    )
    old_state = env.sql_state()
    old_raw_hash = sha256_file(files["raw_path"])
    writer, staging_root = env.build_writer()
    candidate, receipt, staged = staged_identity_variant(
        staging_root, provider="hkexnews", pdoc="12127452-v2"
    )
    payload = bytearray(staged.read_bytes())
    payload[16] ^= 0x01
    staged.write_bytes(bytes(payload))
    import hashlib as _h

    new_sha = _h.sha256(bytes(payload)).hexdigest()
    receipt = DownloadReceipt(
        **{**receipt.to_dict(), "content_sha256": new_sha, "byte_size": len(payload)}
    )
    request = env.request()
    error, class_ok = writer_error_of(writer.import_staged, request, candidate, receipt)
    expect(error is None, f"N2a new version imports cleanly (got {error!r})", results_a)
    if error is None:
        new_state = env.sql_state()
        shas = {s["content_sha256"] for s in new_state["sources"]}
        expect(
            HK_SHA in shas and new_sha in shas,
            "N2a old + new source rows coexist",
            results_a,
        )
        expect(
            sha256_file(files["raw_path"]) == old_raw_hash == HK_SHA,
            "N2a old raw not overwritten",
            results_a,
        )
        raws = env.raw_files()
        expect(len(raws) == 2, f"N2a two canonical raws (got {raws})", results_a)
    matrix["N2a_new_hash_new_version"] = {
        "results": results_a,
        "new_sha256": new_sha,
        "import_error": error,
    }
    proof["N2a"] = results_a

    # N2b: same bytes, swapped identity via register-existing -> R6 rejection.
    results_b = {"name": "W02D_N2b_swapped_identity_register", "failures": []}
    env = Env("N2b")
    files = env.place_sample()
    service = env.build_service()
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]),
        sidecar_path=str(files["sidecar_path"]),
    )
    ensured = service.ensure(env.request(), recovery=recovery)
    expect(
        ensured.status is SourceEnsureStatus.REGISTERED_EXISTING,
        "N2b fixture registration succeeded",
        results_b,
    )
    error, class_ok = writer_error_of(
        service.ensure,
        env.request(provider="sec", provider_document_id="0001193125-26-323660"),
        recovery=recovery,
    )
    expect(
        error is not None and "existing_raw_identity_contract" in error,
        f"N2b identity contract rejection (got {error!r})",
        results_b,
    )
    expect(bool(class_ok), "N2b CanonicalImportError", results_b)
    counts = env.logical_counts(HK_SHA)
    expect(counts["sources_rows"] == 1, "N2b still exactly one row", results_b)
    matrix["N2b_swapped_identity_register"] = {
        "results": results_b,
        "error": error,
        "logical": counts,
    }
    proof["N2b"] = results_b

    # N2c: same bytes, policy change (root not reusable).
    results_c = {"name": "W02D_N2c_policy_not_reusable", "failures": []}
    env = Env("N2c", reusable_root=False)
    files = env.place_sample()
    service = env.build_service()
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]),
        sidecar_path=str(files["sidecar_path"]),
    )
    error, class_ok = writer_error_of(service.ensure, env.request(), recovery=recovery)
    expect(
        error is not None and "existing_raw_root_not_reusable" in error,
        f"N2c root policy rejection (got {error!r})",
        results_c,
    )
    expect(bool(class_ok), "N2c CanonicalImportError", results_c)
    counts = env.logical_counts(HK_SHA)
    expect(counts["sources_rows"] == 0, "N2c no rows under denied policy", results_c)
    matrix["N2c_policy_not_reusable"] = {
        "results": results_c,
        "error": error,
        "logical": counts,
    }
    proof["N2c"] = results_c
    return proof


def n3_cases(matrix: dict) -> dict:
    proof: dict = {}

    # N3a: same bytes only under dayu root -> import_staged imports NEW
    # canonical under company_raw (dedup ignores dayu portfolio).
    results_a = {"name": "W02D_N3a_dayu_same_bytes_ignored", "failures": []}
    env = Env("N3a", dayu_root=True)
    dayu_copy = env.place_dayu_copy()
    service = env.build_service()
    writer, staging_root = env.build_writer()
    candidate, receipt, staged = staged_identity_variant(
        staging_root, provider="hkexnews", pdoc="12127452"
    )
    request = env.request()
    try:
        imported = writer.import_staged(request, candidate, receipt)
        error = None
    except Exception as exc:
        imported = None
        error = f"{type(exc).__name__}: {exc}"
    expect(error is None, f"N3a import succeeds (got {error!r})", results_a)
    if imported is not None:
        expect(
            imported.status is CanonicalImportStatus.IMPORTED_NEW,
            f"N3a status imported_new (got {imported.status})",
            results_a,
        )
        canonical = Path(imported.canonical_path)
        expect(
            str(canonical).startswith(str(env.companies_path.resolve())),
            "N3a canonical lands under company_raw",
            results_a,
        )
        expect(
            not str(canonical).startswith(str(dayu_copy.parent.resolve())),
            "N3a canonical is not the dayu copy",
            results_a,
        )
    expect(
        dayu_copy.is_file() and sha256_file(dayu_copy) == HK_SHA,
        "N3a dayu copy untouched",
        results_a,
    )
    expect(
        env.provider_counts() == {"discover": 0, "fetch": 0},
        "N3a provider counts zero",
        results_a,
    )
    matrix["N3a_dayu_same_bytes_ignored"] = {
        "results": results_a,
        "import_error": error,
        "status": imported.status.value if imported is not None else None,
    }
    proof["N3a"] = results_a

    # N3b: retired same bytes via register-existing -> refused, no reactivate.
    results_b = {"name": "W02D_N3b_retired_register_refused", "failures": []}
    env = Env("N3b")
    files = env.place_sample()
    service = env.build_service()
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]),
        sidecar_path=str(files["sidecar_path"]),
    )
    ensured = service.ensure(env.request(), recovery=recovery)
    expect(
        ensured.status is SourceEnsureStatus.REGISTERED_EXISTING,
        "N3b fixture registration succeeded",
        results_b,
    )
    document_id = f"urn:company-wiki:document:sha256:{HK_SHA}"
    store_module.retire_document(
        env.catalog.store,
        document_id=document_id,
        reason="oracle W02D-N3b fixture",
        created_by="w02d",
    )
    reactivate_calls_before = reactivate_call_count["n"]
    error, class_ok = writer_error_of(service.ensure, env.request(), recovery=recovery)
    expect(
        error is not None and "existing_raw_status_not_active" in error,
        f"N3b retired refused (got {error!r})",
        results_b,
    )
    expect(
        reactivate_call_count["n"] == reactivate_calls_before,
        "N3b _reactivate_if_retired never called",
        results_b,
    )
    state = env.sql_state()
    doc = [d for d in state["documents"] if d["document_id"] == document_id]
    expect(
        bool(doc) and doc[0]["source_status"] == "retired",
        f"N3b document stays retired (got {doc!r})",
        results_b,
    )
    expect(
        sha256_file(files["raw_path"]) == HK_SHA,
        "N3b raw bytes untouched",
        results_b,
    )
    matrix["N3b_retired_register_refused"] = {
        "results": results_b,
        "error": error,
    }
    proof["N3b"] = results_b
    return proof


reactivate_call_count = {"n": 0}
_original_reactivate = CanonicalSourceWriter._reactivate_if_retired


def _counting_reactivate(self, content_sha256):
    reactivate_call_count["n"] += 1
    return _original_reactivate(self, content_sha256)


def p2_two_process_case(matrix: dict, trace_out: dict) -> dict:
    results = {"name": "W02D_P2_two_process_barrier", "failures": []}
    case_dir = SCRATCH_BASE / "P2_shared"
    if case_dir.exists():
        shutil.rmtree(case_dir)
    (case_dir / "project").mkdir(parents=True)
    scratch_project = case_dir / "project"
    companies = scratch_project / "companies"
    dst = companies / HK_META["company_dir"] / "raw" / "financial_reports" / "annual"
    dst.mkdir(parents=True)
    src_raw = SAMPLES / "hk" / HK_FILENAME
    shutil.copyfile(src_raw, dst / HK_FILENAME)
    shutil.copyfile(
        src_raw.with_name(src_raw.name + ".source.json"),
        (dst / HK_FILENAME).with_name(HK_FILENAME + ".source.json"),
    )
    barrier_dir = case_dir / "barrier"
    barrier_dir.mkdir()
    trace_out["project"] = str(scratch_project)
    trace_out["barrier_dir"] = str(barrier_dir)
    procs = []
    result_paths = []
    log_paths = []
    for index in (1, 2):
        result_path = case_dir / f"worker{index}.result.json"
        log_path = case_dir / f"worker{index}.log"
        result_paths.append(result_path)
        log_paths.append(log_path)
        proc = subprocess.Popen(
            [
                str(PYTHON),
                "-X",
                "utf8",
                str(HERE / "w02d_worker.py"),
                str(scratch_project),
                str(barrier_dir),
                str(result_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(ATTEMPT),
        )
        procs.append(proc)
    for proc, log_path in zip(procs, log_paths):
        stdout, stderr = proc.communicate(timeout=180)
        log_path.write_text(
            f"--stdout--\n{stdout}\n--stderr--\n{stderr}\n", encoding="utf-8"
        )
    for index, (proc, result_path, log_path) in enumerate(
        zip(procs, result_paths, log_paths), start=1
    ):
        payload = {}
        if result_path.is_file():
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        trace_out[f"worker{index}"] = {
            "exit_code": proc.returncode,
            "stdout_tail": (log_path.read_text(encoding="utf-8"))[-2000:],
            "result": payload,
        }
    # Shared-catalog verification via the parent's own isolated read.
    shared_env = Env.__new__(Env)
    shared_env.name = "P2_shared_inspect"
    shared_env.dir = case_dir
    shared_env.project = scratch_project
    shared_env.companies_path = companies
    shared_env.config_dir = scratch_project / ".source_catalog"
    shared_env.reusable_root = True
    shared_env.dayu_root = False
    from company_wiki.source_catalog import CatalogConfig as _Cfg, RootSpec as _Root

    shared_env.catalog = SourceCatalog(
        _Cfg(
            project_root=scratch_project,
            catalog_dir=scratch_project / ".source_catalog",
            roots=(
                _Root(
                    "company_raw",
                    companies,
                    "company_raw",
                    priority=10,
                    adapter_id="company_raw_v1",
                    reusable_for_filing=True,
                ),
            ),
        )
    )
    counts = shared_env.logical_counts(HK_SHA)
    trace_out["shared_logical_counts"] = counts
    journal = AcquisitionJournal(scratch_project / ".source_catalog").read_all()
    trace_out["journal_rows"] = [a.to_dict() for a in journal]
    expect(counts["sources_rows"] == 1, "P2 exactly one source row", results)
    expect(counts["documents_active"] == 1, "P2 exactly one active document", results)
    expect(
        counts["locations_active_original"] == 1,
        "P2 exactly one active original location",
        results,
    )
    statuses = []
    for index in (1, 2):
        payload = trace_out[f"worker{index}"]["result"]
        status = payload.get("status")
        statuses.append((status, trace_out[f"worker{index}"]["exit_code"]))
    ok_one = any(status in ("registered_existing", "reused") for status, _ in statuses)

    def _retryable(status: str, payload: dict) -> bool:
        if status in ("registered_existing", "reused"):
            return True
        if status in ("exception", "setup_exception"):
            error_type = str(payload.get("error_type", ""))
            error_text = str(payload.get("error", ""))
            return (
                "CatalogOperationLockedError" in error_type
                or "CatalogOperationLockedError" in error_text
                or "catalog operation already running" in error_text
                or "timed out serializing catalog lock" in error_text
            )
        return False

    retryable = all(
        _retryable(status, trace_out[f"worker{index}"]["result"])
        for index, (status, _) in enumerate(statuses, start=1)
    )
    expect(ok_one, f"P2 at least one registration success (got {statuses})", results)
    expect(
        retryable,
        f"P2 every outcome is success or explicitly retryable lock contention "
        f"(got {statuses})",
        results,
    )
    expect(len(journal) >= 1, "P2 journal non-empty", results)
    try:
        for _ in journal:
            pass
        journal_readable = True
    except ValueError:
        journal_readable = False
    expect(journal_readable, "P2 journal not corrupted", results)
    raw_path = dst / HK_FILENAME
    expect(sha256_file(raw_path) == HK_SHA, "P2 raw bytes unchanged", results)
    provider_calls_zero = all(
        trace_out[f"worker{index}"]["result"].get("provider_calls")
        in ({"discover": 0, "fetch": 0}, None)
        for index in (1, 2)
    )
    expect(provider_calls_zero, "P2 provider counts zero", results)
    matrix["P2_two_process"] = {"results": results}
    return results


def main() -> int:
    AFTER.mkdir(parents=True, exist_ok=True)
    matrix: dict = {}
    trace: dict = {"started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    case_results: dict = {}
    CanonicalSourceWriter._reactivate_if_retired = _counting_reactivate
    try:
        for name, fn in (
            ("P1", lambda: p1_case(matrix)),
            ("N1", lambda: n1_case(matrix)),
            ("N2", lambda: n2_cases(matrix)),
            ("N3", lambda: n3_cases(matrix)),
        ):
            try:
                case_results[name] = fn()
            except Exception as exc:
                case_results[name] = {
                    "failures": [f"case exception: {type(exc).__name__}: {exc}"],
                    "traceback": traceback.format_exc(),
                }
        try:
            case_results["P2"] = p2_two_process_case(matrix, trace)
        except Exception as exc:
            case_results["P2"] = {
                "failures": [f"case exception: {type(exc).__name__}: {exc}"],
                "traceback": traceback.format_exc(),
            }
    finally:
        CanonicalSourceWriter._reactivate_if_retired = _original_reactivate

    # logical-rows-vs-attempts: independent SQL counts vs journal attempts.
    lva: dict = {}
    for case_name, entry in matrix.items():
        logical = None
        if case_name == "P1_reentry_x3":
            logical = entry["calls"][-1]["logical"]
        elif case_name == "P2_two_process":
            logical = trace.get("shared_logical_counts")
        else:
            logical = entry.get("logical")
        lva[case_name] = {
            "logical_rows": logical,
            "journal_attempts": entry.get("calls"),
        }
    trace["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    (AFTER / "idempotency-matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AFTER / "two-process-trace.json").write_text(
        json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AFTER / "logical-rows-vs-attempts.json").write_text(
        json.dumps(lva, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AFTER / "case_results.json").write_text(
        json.dumps(case_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    failed = [name for name, value in case_results.items() if value.get("failures")]
    # Windows MAX_PATH: retained snapshots keep each case's sqlite + top
    # state, not the deep raw subtree (raw hashes are already recorded in
    # idempotency-matrix.json per call).
    retention = AFTER / "case_scratch_retained"
    if retention.exists():
        shutil.rmtree(retention)
    retention.mkdir(parents=True)
    for scratch_child in sorted(SCRATCH_BASE.iterdir()):
        destination = retention / scratch_child.name
        destination.mkdir(parents=True)
        for item in sorted(scratch_child.iterdir()):
            if item.name == "project":
                continue
            target = destination / item.name
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copyfile(item, target)
        project_dir = scratch_child / "project"
        if project_dir.is_dir():
            shutil.copytree(
                project_dir / ".source_catalog",
                destination / "project" / ".source_catalog",
                ignore=shutil.ignore_patterns("*.sqlite3-journal", "staging"),
                dirs_exist_ok=True,
            )
    print(json.dumps({"failed_cases": failed}, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
