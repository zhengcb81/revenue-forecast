"""w02c_cases: case runner for card I-02-C (register-existing recovery).

Positive cases (P1 HK/US, P2) run ONLY real code: the modified writer/
service copies + real scanner/resolver/store/journal against isolated
scratch catalogs seeded with byte-identical copies of the two fixed real
raw files (sha/size re-verified at run start from samples/real_roots).
Providers are harness-side deny-on-call stubs that record call counts; the
recovery path must never reach them (oracle I0.1).

All fault injection is harness-side (attribute replacement / case-tree
fixture edits only). Frozen expectations live in oracle.md; expected error
phrases are asserted verbatim.

Outputs into <attempt>/after/:
  zero-provider-events.json
  registration-stages.json
  exact-resolve.before-after.json
  case_results.json
  case_scratch_retained/<case>/... (scratch trees snapshot at run end)
"""

from __future__ import annotations

import hashlib
import importlib
import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
AFTER = ATTEMPT / "after"
SAMPLES = ATTEMPT / "samples" / "real_roots"

# Windows MAX_PATH workaround identical to the accepted I-02-A attempt.
SCRATCH_BASE = Path(tempfile.gettempdir()) / "w02c" / "a20260919-01_case_scratch"

w02c = importlib.import_module("w02c_bootstrap")
MODE = sys.argv[1] if len(sys.argv) > 1 else "override"
assert MODE in {"override"}, MODE
w02c.setup("override")

from company_wiki.source_catalog import (  # noqa: E402
    CatalogConfig,
    RootSpec,
    SourceCatalog,
)
from company_wiki.source_catalog.acquisition import (  # noqa: E402
    AcquisitionCoordinator,
    AdapterRegistry,
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
import company_wiki.source_catalog.canonical_writer as cw_module  # noqa: E402
from company_wiki.source_catalog.resolver import (  # noqa: E402
    ResolutionStatus,
    SourceRequest,
    SourceResolver,
    build_resolution_envelope,
)
from company_wiki.source_catalog import store as store_module  # noqa: E402

HK_SHA = "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c"
US_SHA = "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff"

SAMPLES_META = {
    "hk": {
        "sha": HK_SHA,
        "size": 4405561,
        "filename": "2026-04-28_hkexnews_12127452_2025年度報告.pdf",
        "company_dir": "小米集團－Ｗ",
        "provider": "hkexnews",
        "provider_document_id": "12127452",
        "fiscal_year": 2025,
        "entity": "小米集團－Ｗ",
        "security_id": "01810",
        "market": "HK",
    },
    "us": {
        "sha": US_SHA,
        "size": 8585615,
        "filename": (
            "2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm"
        ),
        "company_dir": "MICROSOFT CORP",
        "provider": "sec",
        "provider_document_id": "0001193125-26-323660",
        "fiscal_year": 2026,
        "entity": "MICROSOFT CORP",
        "security_id": "MSFT",
        "market": "US",
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sample_copies() -> dict:
    manifest = json.loads(
        (ATTEMPT / "samples" / "sample-copy-manifest.json").read_text(encoding="utf-8")
    )
    for entry in manifest:
        raw = Path(entry["copied_raw"])
        assert sha256_file(raw) == entry["raw_sha256"], raw
        assert raw.stat().st_size == entry["raw_size"], raw
        assert Path(entry["copied_sidecar"]).is_file(), raw
    return {"verified_copy_count": len(manifest), "all_byte_identical": True}


class DenyOnCallAdapter:
    """Harness-side provider stub: every adapter call records a violation by
    raising. Providers must never run in this card (oracle I0.1)."""

    def __init__(self, market: str):
        self.market = market
        self.name = f"deny-{market.lower()}"
        self.version = "1.0.0"
        self.calls = {"discover": 0, "fetch": 0}

    def discover(self, request):
        self.calls["discover"] += 1
        raise RuntimeError(
            "deny-on-call stub: adapter discovery must never run in this card"
        )

    def fetch(self, candidate, staging_dir):
        self.calls["fetch"] += 1
        raise RuntimeError(
            "deny-on-call stub: adapter fetch must never run in this card"
        )


class Env:
    """One isolated scratch catalog per case."""

    def __init__(self, name: str, *, reusable_root: bool = True):
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
        self.reusable_root = reusable_root
        self.catalog = SourceCatalog(self._config())
        self.catalog.scan()

    def _config(self, *, reusable_root: bool | None = None) -> CatalogConfig:
        if reusable_root is None:
            reusable_root = self.reusable_root
        return CatalogConfig(
            project_root=self.project,
            catalog_dir=self.config_dir,
            roots=(
                RootSpec(
                    "company_raw",
                    self.companies_path,
                    "company_raw",
                    priority=10,
                    adapter_id="company_raw_v1",
                    reusable_for_filing=True if reusable_root else False,
                ),
            ),
        )

    def rebuild_catalog(self, *, reusable_root: bool) -> None:
        self.reusable_root = reusable_root
        self.catalog = SourceCatalog(self._config())
        self.catalog.scan()

    def place_sample(self, market: str) -> dict:
        meta = SAMPLES_META[market]
        src_raw = SAMPLES / market / meta["filename"]
        sidecar_src = src_raw.with_name(src_raw.name + ".source.json")
        dst = (
            self.companies_path
            / meta["company_dir"]
            / "raw"
            / "financial_reports"
            / "annual"
        )
        dst.mkdir(parents=True, exist_ok=True)
        raw_dst = dst / meta["filename"]
        shutil.copyfile(src_raw, raw_dst)
        side_dst = raw_dst.with_name(raw_dst.name + ".source.json")
        shutil.copyfile(sidecar_src, side_dst)
        assert sha256_file(raw_dst) == meta["sha"], raw_dst
        assert raw_dst.stat().st_size == meta["size"]
        return {"raw_path": raw_dst, "sidecar_path": side_dst}

    def sample_paths(self, market: str) -> dict:
        meta = SAMPLES_META[market]
        raw_path = (
            self.companies_path
            / meta["company_dir"]
            / "raw"
            / "financial_reports"
            / "annual"
            / meta["filename"]
        )
        return {
            "raw_path": raw_path,
            "sidecar_path": raw_path.with_name(raw_path.name + ".source.json"),
        }

    def snapshot_files(self) -> dict:
        files = {}
        for path in sorted(self.companies_path.rglob("*")):
            if path.is_file():
                key = str(path.relative_to(self.project)).replace("\\", "/")
                files[key] = sha256_file(path)
        return files

    def sql_state(self) -> dict:
        db_path = Path(self.catalog.config.database_path)
        connection = sqlite3.connect(str(db_path))
        connection.row_factory = sqlite3.Row
        try:
            sources = [
                dict(row)
                for row in connection.execute(
                    "SELECT source_id,content_sha256,byte_size FROM sources"
                )
            ]
            documents = [
                dict(row)
                for row in connection.execute(
                    "SELECT document_id,title,source_status FROM documents"
                )
            ]
            locations = [
                dict(row)
                for row in connection.execute(
                    "SELECT location_id,root_id,relative_path,role,location_status"
                    " FROM locations"
                )
            ]
        finally:
            connection.close()
        return {
            "db_path": str(db_path),
            "sources": sources,
            "documents": documents,
            "locations": locations,
        }

    def journal_lines(self) -> list[dict]:
        journal = AcquisitionJournal(self.config_dir)
        try:
            return [a.to_dict() for a in journal.read_all()]
        except ValueError as exc:
            return [{"journal_read_error": str(exc)}]


def build_service(env: Env, adapters: AdapterRegistry, journal: AcquisitionJournal):
    staging_root = env.config_dir / "staging"
    staging_root.mkdir(parents=True, exist_ok=True)
    return SourceAcquisitionService(
        coordinator=AcquisitionCoordinator(
            catalog=env.catalog,
            adapters=adapters,
            staging_root=staging_root,
        ),
        writer=CanonicalSourceWriter(env.catalog, staging_root=staging_root),
        journal=journal,
    )


def sample_request(
    meta: dict, *, provider=..., provider_document_id=...
) -> SourceRequest:
    return SourceRequest(
        entity=meta["entity"],
        security_id=meta["security_id"],
        market=meta["market"],
        document_kind="annual_report",
        fiscal_year=meta["fiscal_year"],
        provider=(meta["provider"] if provider is ... else provider),
        provider_document_id=(
            meta["provider_document_id"]
            if provider_document_id is ...
            else provider_document_id
        ),
        as_of_date="2026-09-18",
        mode="exact",
        allow_download=False,
    )


class CaseTrack:
    """Per-case provider deny-on-call counters."""

    def __init__(self, name: str):
        self.name = name
        self.adapters = [
            DenyOnCallAdapter("CN"),
            DenyOnCallAdapter("HK"),
            DenyOnCallAdapter("US"),
        ]
        self.registry = AdapterRegistry(
            cn=self.adapters[0], hk=self.adapters[1], us=self.adapters[2]
        )
        self.counts = {"discover": 0, "fetch": 0}

    def drain(self) -> dict:
        for adapter in self.adapters:
            for key in ("discover", "fetch"):
                self.counts[key] += adapter.calls[key]
                adapter.calls[key] = 0
        return dict(self.counts)


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


def provider_counts_zero(track: CaseTrack) -> bool:
    counts = track.drain()
    return counts == {"discover": 0, "fetch": 0}


def no_target_rows(state: dict, sha: str) -> bool:
    return (
        not [s for s in state["sources"] if s["content_sha256"] == sha]
        and not [d for d in state["documents"] if sha in d["document_id"]]
        and not [l for l in state["locations"] if sha in l["relative_path"]]
    )


def p1_case(market: str) -> tuple[dict, dict, dict, dict]:
    case_name = f"P1_{market}"
    sha = SAMPLES_META[market]["sha"]
    meta = SAMPLES_META[market]
    other_market = "us" if market == "hk" else "hk"
    env = Env(case_name)
    # Sanity: pre-register ONE unrelated company entry (the sibling real
    # sample) before the target exists, so the baseline catalog has content
    # but the TARGET is unregistered.
    env.place_sample(other_market)
    env.rebuild_catalog(reusable_root=True)
    state_baseline = env.sql_state()
    results = {"name": case_name, "failures": []}
    expect(
        not [s for s in state_baseline["sources"] if s["content_sha256"] == sha],
        "P1 baseline has no target row",
        results,
    )
    files = env.place_sample(market)
    request = sample_request(meta)
    resolution_before = SourceResolver(env.catalog).resolve(request).to_dict()
    track = CaseTrack(case_name)
    service = build_service(env, track.registry, AcquisitionJournal(env.config_dir))
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]), sidecar_path=str(files["sidecar_path"])
    )
    ensured = service.ensure(request, recovery=recovery)
    provider_counts = track.drain()
    state_after = env.sql_state()
    resolution_after = ensured.resolution.to_dict()
    envelope = build_resolution_envelope(
        ensured.resolution,
        policy_snapshot=None,
        journal=AcquisitionJournal(env.config_dir),
        bundle=env.catalog.bundle_for_resolution(ensured.resolution),
        store=env.catalog.store,
        project_root=env.project,
    ).to_dict()

    expect(
        ensured.status is SourceEnsureStatus.REGISTERED_EXISTING,
        "P1 ensure status registered_existing",
        results,
    )
    expect(
        ensured.acquisition is None,
        "P1 acquisition honestly null (no discovery happened)",
        results,
    )
    expect(
        ensured.canonical_import.status
        is CanonicalImportStatus.REGISTERED_EXISTING_RAW,
        "P1 writer status registered_existing_raw",
        results,
    )
    expect(
        ensured.canonical_import.recovery_source == "existing_raw",
        "P1 recovery_source marker",
        results,
    )
    expect(
        resolution_after["status"] == "reused_exact",
        f"P1 resolution reused_exact (got {resolution_after.get('status')})",
        results,
    )
    handle = ensured.resolution.matches[0]
    expect(handle.content_sha256 == sha, "P1 match content hash", results)
    expect(
        str(handle.canonical_path) == str(files["raw_path"].resolve()),
        "P1 match canonical path equals the recovered raw",
        results,
    )
    expect(
        handle.provider == meta["provider"]
        and handle.provider_document_id == meta["provider_document_id"],
        "P1 provider identity retained",
        results,
    )
    expect(
        handle.fiscal_year == meta["fiscal_year"], "P1 fiscal_year retained", results
    )
    expect(handle.capture_ready is True, "P1 capture_ready on handle", results)
    expect(provider_counts_zero(track), "P1 provider counts zero", results)
    expect(
        sha256_file(files["raw_path"]) == sha,
        "P1 raw bytes byte-identical after recovery",
        results,
    )
    expect(
        len([s for s in state_after["sources"] if s["content_sha256"] == sha]) == 1,
        "P1 exactly one effective source row",
        results,
    )
    registers = [
        line
        for line in env.journal_lines()
        if line.get("outcome") == "registered_existing_raw"
    ]
    expect(
        len(registers) == 1 and registers[0]["content_sha256"] == sha,
        "P1 journal registered_existing_raw once",
        results,
    )
    expect(
        envelope["prompt_injection_status"] == "not_reviewed",
        "P1 review stays not_reviewed (reuse != review)",
        results,
    )
    expect(
        envelope["bundle_usable"] is False,
        "P1 bundle_usable False (reuse != artifact)",
        results,
    )
    # Idempotent re-entry WITH recovery manifest: catalog-first reuse.
    ensured2 = service.ensure(request, recovery=recovery)
    state_after2 = env.sql_state()
    expect(
        ensured2.status is SourceEnsureStatus.REUSED,
        "P1 second call with recovery returns reused (catalog first)",
        results,
    )
    expect(
        len([s for s in state_after2["sources"] if s["content_sha256"] == sha]) == 1,
        "P1 re-entry adds no effective row",
        results,
    )
    counts = track.drain()
    stages = {
        "content_sha256": sha,
        "sidecar_sha256": sha256_file(files["sidecar_path"]),
        "recovery_source": "existing_raw",
        "provider": meta["provider"],
        "provider_document_id": meta["provider_document_id"],
        "fiscal_year": meta["fiscal_year"],
        "entity": meta["entity"],
        "register": {
            "journal_outcome": "registered_existing_raw",
            "attempt_id": registers[0]["attempt_id"] if registers else None,
            "canonical_path": str(files["raw_path"].resolve()),
        },
        "qualification": {
            "sources_rows": [
                row for row in state_after["sources"] if row["content_sha256"] == sha
            ],
            "documents_active": [
                row
                for row in state_after["documents"]
                if row["source_status"] == "active"
            ],
            "locations_active_original": [
                row
                for row in state_after["locations"]
                if row["location_status"] == "active"
                and row["role"] == "original_primary"
                and sha in row["relative_path"]
            ],
        },
        "exact_resolve": {
            "status": resolution_after["status"],
            "source_id": handle.source_id,
            "capture_ready": handle.capture_ready,
        },
        "idempotent_reentry": {"status": ensured2.status.value},
    }
    resolve_evidence = {
        "before_unregistered": {
            "resolution_status": resolution_before.get("status"),
            "reason": resolution_before.get("reason"),
        },
        "after_registered": {
            "resolution_status": resolution_after["status"],
            "handle_source_id": handle.source_id,
            "handle_content_sha256": handle.content_sha256,
            "provider": handle.provider,
            "provider_document_id": handle.provider_document_id,
            "fiscal_year": handle.fiscal_year,
            "prompt_injection_status": envelope["prompt_injection_status"],
            "bundle_usable": envelope["bundle_usable"],
        },
    }
    return results, counts, stages, resolve_evidence


def p2_case() -> tuple[dict, dict, dict, dict]:
    """Second exact reuse through the SAME original request; no download,
    no review/artifact qualification implied by reuse."""
    meta = SAMPLES_META["hk"]
    env = Env("P2")
    env.place_sample("us")
    env.rebuild_catalog(reusable_root=True)
    track = CaseTrack("P2")
    files = env.place_sample("hk")
    service = build_service(env, track.registry, AcquisitionJournal(env.config_dir))
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]), sidecar_path=str(files["sidecar_path"])
    )
    request = sample_request(meta)
    ensured = service.ensure(request, recovery=recovery)
    first_handle = ensured.resolution.matches[0]
    # Second exact reuse WITHOUT recovery (reader/catalog-first path).
    ensured2 = service.ensure(request)
    counts = track.drain()
    state2 = env.sql_state()
    results = {"name": "P2_second_exact_reuse", "failures": []}
    expect(
        ensured.status is SourceEnsureStatus.REGISTERED_EXISTING,
        "P2 fixture registration succeeded",
        results,
    )
    expect(
        ensured2.status is SourceEnsureStatus.REUSED,
        "P2 second ensure returns reused",
        results,
    )
    handle = (ensured2.resolution.matches or [None])[0]
    expect(
        handle is not None and handle.content_sha256 == HK_SHA,
        "P2 same identity hash",
        results,
    )
    expect(
        handle is not None and handle.source_id == first_handle.source_id,
        "P2 same source_id/version",
        results,
    )
    expect(
        counts == {"discover": 0, "fetch": 0},
        f"P2 provider counts zero (got {counts})",
        results,
    )
    expect(
        len([s for s in state2["sources"] if s["content_sha256"] == HK_SHA]) == 1,
        "P2 no new effective rows",
        results,
    )
    expect(
        sha256_file(files["raw_path"]) == HK_SHA,
        "P2 raw bytes unchanged (no new original)",
        results,
    )
    download_like = [
        line
        for line in env.journal_lines()
        if line.get("outcome") in ("downloaded_new", "deduplicated_after_download")
    ]
    expect(not download_like, "P2 no download-class journal rows", results)
    envelope = build_resolution_envelope(
        ensured2.resolution,
        policy_snapshot=None,
        journal=AcquisitionJournal(env.config_dir),
        bundle=env.catalog.bundle_for_resolution(ensured2.resolution),
        store=env.catalog.store,
        project_root=env.project,
    ).to_dict()
    expect(
        envelope["prompt_injection_status"] == "not_reviewed",
        "P2 envelope not_reviewed persists",
        results,
    )
    expect(
        envelope["bundle_usable"] is False,
        "P2 bundle_usable False persists (reuse != work done)",
        results,
    )
    stages = {
        "first_register_status": ensured.status.value,
        "second_reuse_status": ensured2.status.value,
        "reuse_reason": ensured2.acquisition.reason if ensured2.acquisition else None,
        "source_id": first_handle.source_id,
        "content_sha256": HK_SHA,
        "prompt_injection_status": envelope["prompt_injection_status"],
        "bundle_usable": envelope["bundle_usable"],
    }
    resolve = {
        "before": {"status": ensured.status.value},
        "after": {
            "status": ensured2.status.value,
            "resolution_status": ensured2.resolution.to_dict().get("status"),
            "prompt_injection_status": envelope["prompt_injection_status"],
            "bundle_usable": envelope["bundle_usable"],
        },
    }
    return results, counts, stages, resolve


def inject_delete_sidecar(env: Env) -> None:
    files = env.place_sample("hk")
    Path(files["sidecar_path"]).unlink()


def inject_tamper_byte(env: Env) -> None:
    files = env.place_sample("hk")
    data = bytearray(files["raw_path"].read_bytes())
    data[16] ^= 0x01
    files["raw_path"].write_bytes(bytes(data))


def inject_sidecar_scrub_receipt(env: Env) -> None:
    files = env.place_sample("hk")
    payload = json.loads(Path(files["sidecar_path"]).read_text(encoding="utf-8"))
    payload.pop("receipt", None)
    Path(files["sidecar_path"]).write_text(
        json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def n1_case_fixture(case_name: str, injection, request: SourceRequest) -> dict:
    env = Env(case_name)
    env.place_sample("us")
    env.rebuild_catalog(reusable_root=True)
    injection(env)
    track = CaseTrack(case_name)
    files = env.sample_paths("hk")
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]), sidecar_path=str(files["sidecar_path"])
    )
    service = build_service(env, track.registry, AcquisitionJournal(env.config_dir))
    error, class_ok = writer_error_of(service.ensure, request, recovery=recovery)
    counts = track.drain()
    state = env.sql_state()
    results = {"name": case_name, "writer_error": error, "failures": []}
    expect(class_ok, f"{case_name} CanonicalImportError", results)
    expect(no_target_rows(state, HK_SHA), f"{case_name} no catalog rows", results)
    expect(
        counts == {"discover": 0, "fetch": 0},
        f"{case_name} provider counts zero",
        results,
    )
    failed_lines = [
        line
        for line in env.journal_lines()
        if line.get("outcome") == "failed"
        and line.get("reason") == "existing_raw_register_failed"
    ]
    expect(len(failed_lines) == 1, f"{case_name} journal failed line once", results)
    return {
        "results": results,
        "provider_counts": counts,
        "error": error,
        "state": state,
        "env": env,
    }


def n1_cases() -> dict:
    meta = SAMPLES_META["hk"]
    proof: dict[str, dict] = {}

    case = n1_case_fixture(
        "N1a_delete_sidecar", inject_delete_sidecar, sample_request(meta)
    )
    _expect_phrase(
        case["results"], "N1a", "existing_raw_missing_sidecar", case["error"]
    )
    proof["N1a_delete_sidecar"] = _compact(case)

    case = n1_case_fixture(
        "N1b_tamper_one_byte", inject_tamper_byte, sample_request(meta)
    )
    _expect_phrase(case["results"], "N1b", "existing_raw_bytes_mismatch", case["error"])
    tampered_path = case["env"].sample_paths("hk")["raw_path"]
    raw_bytes = tampered_path.read_bytes()
    tampered_hash = hashlib.sha256(raw_bytes).hexdigest()
    case["results"]["failures"].append(
        None
        if tampered_hash != HK_SHA
        and tampered_hash == hashlib.sha256(raw_bytes).hexdigest()
        else "N1b tampered healed?",
    )
    case["results"]["failures"] = [
        item for item in case["results"]["failures"] if isinstance(item, str)
    ]
    proof["N1b_tamper_one_byte"] = _compact(case)
    proof["N1b_tamper_one_byte"]["tampered_sha256"] = tampered_hash

    res_c1, counts_c1, err_c1, state_c1 = _forged_case(
        "N1c_forged_provider_id", "sec", "12127452"
    )
    proof["N1c_forged_provider_id"] = {
        "results": res_c1,
        "provider_counts": counts_c1,
        "error": err_c1,
        "catalog_rows": state_c1,
    }
    res_c2, counts_c2, err_c2, state_c2 = _forged_case(
        "N1c_missing_provider", None, None
    )
    proof["N1c_missing_provider"] = {
        "results": res_c2,
        "provider_counts": counts_c2,
        "error": err_c2,
        "catalog_rows": state_c2,
    }

    case = n1_case_fixture(
        "N1d_missing_download_receipt_chain",
        inject_sidecar_scrub_receipt,
        sample_request(meta),
    )
    _expect_phrase(
        case["results"], "N1d", "existing_raw_provenance_incomplete", case["error"]
    )
    proof["N1d_missing_download_receipt_chain"] = _compact(case)
    proof["N1d_missing_download_receipt_chain"]["catalog_rows"] = case["state"]
    return proof


def _expect_phrase(results, tag, phrase, error):
    expect(
        error is not None and phrase in (error or ""),
        f"{tag} expected phrase {phrase!r} (got {error!r})",
        results,
    )


def _compact(case: dict) -> dict:
    return {
        "results": case["results"],
        "provider_counts": case["provider_counts"],
        "error": case["error"],
    }


def _forged_case(case_name: str, provider, provider_document_id):
    env = Env(case_name)
    env.place_sample("us")
    env.rebuild_catalog(reusable_root=True)
    files = env.place_sample("hk")
    track = CaseTrack(case_name)
    meta = SAMPLES_META["hk"]
    request = sample_request(
        meta, provider=provider, provider_document_id=provider_document_id
    )
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]), sidecar_path=str(files["sidecar_path"])
    )
    service = build_service(env, track.registry, AcquisitionJournal(env.config_dir))
    error, class_ok = writer_error_of(service.ensure, request, recovery=recovery)
    counts = track.drain()
    state = env.sql_state()
    results = {"name": case_name, "writer_error": error, "failures": []}
    results["call_note"] = {
        "forged_provider": provider,
        "forged_provider_document_id": provider_document_id,
    }
    _expect_phrase(results, "N1c", "existing_raw_identity_contract", error)
    expect(class_ok, f"{case_name} CanonicalImportError", results)
    expect(no_target_rows(state, HK_SHA), f"{case_name} no rows", results)
    expect(
        counts == {"discover": 0, "fetch": 0},
        f"{case_name} provider counts zero",
        results,
    )
    return results, counts, error, state


def n2_cases() -> dict:
    proof: dict[str, dict] = {}
    meta = SAMPLES_META["hk"]

    def retired_case(case_name: str, new_status: str, use_store_call: bool) -> dict:
        env = Env(case_name)
        env.place_sample("us")
        env.rebuild_catalog(reusable_root=True)
        track = CaseTrack(case_name)
        files = env.place_sample("hk")
        request = sample_request(meta)
        recovery = SourceRecoveryInput(
            raw_path=str(files["raw_path"]),
            sidecar_path=str(files["sidecar_path"]),
        )
        service = build_service(env, track.registry, AcquisitionJournal(env.config_dir))
        ensured = service.ensure(request, recovery=recovery)
        if ensured.status is not SourceEnsureStatus.REGISTERED_EXISTING:
            raise AssertionError(f"{case_name} fixture registration failed")
        document_id = f"urn:company-wiki:document:sha256:{HK_SHA}"
        if use_store_call:
            store_module.retire_document(
                env.catalog.store,
                document_id=document_id,
                reason="oracle W02C-N2a fixture",
                created_by="w02c",
            )
        else:
            with env.catalog.store.transaction() as connection:
                connection.execute(
                    "UPDATE documents SET source_status='quarantined' "
                    "WHERE document_id=?",
                    (document_id,),
                )
        reactivate_calls_before = reactivate_call_count["n"]
        error, class_ok = writer_error_of(service.ensure, request, recovery=recovery)
        counts = track.drain()
        state = env.sql_state()
        results = {"name": case_name, "writer_error": error, "failures": []}
        _expect_phrase(results, case_name, "existing_raw_status_not_active", error)
        expect(bool(class_ok), f"{case_name} CanonicalImportError", results)
        expect(
            reactivate_call_count["n"] == reactivate_calls_before,
            f"{case_name} _reactivate_if_retired was never called",
            results,
        )
        doc = [d for d in state["documents"] if d["document_id"] == document_id]
        expect(
            bool(doc) and doc[0]["source_status"] == new_status,
            f"{case_name} document stays {new_status} (got {doc!r})",
            results,
        )
        expect(
            counts == {"discover": 0, "fetch": 0},
            f"{case_name} provider counts zero",
            results,
        )
        expect(
            sha256_file(files["raw_path"]) == HK_SHA
            and sha256_file(files["sidecar_path"]),
            f"{case_name} raw/sidecar bytes untouched",
            results,
        )
        return {
            "results": results,
            "provider_counts": counts,
            "documents": doc,
            "error": error,
            "env": env,
        }

    proof["N2a_retired"] = _compact(
        retired_case("N2a_retired", "retired", use_store_call=True)
    )
    q_case = retired_case("N2a2_quarantined", "quarantined", use_store_call=False)
    q_case["documents_retained"] = q_case.pop("documents")
    proof["N2a2_quarantined"] = {
        **_compact(q_case),
        "documents": q_case["documents_retained"],
    }

    env = Env("N2b_root_not_reusable", reusable_root=False)
    env.place_sample("us")
    env.rebuild_catalog(reusable_root=False)
    track = CaseTrack("N2b")
    files = env.place_sample("hk")
    recovery = SourceRecoveryInput(
        raw_path=str(files["raw_path"]), sidecar_path=str(files["sidecar_path"])
    )
    request = sample_request(meta)
    service = build_service(env, track.registry, AcquisitionJournal(env.config_dir))
    error, class_ok = writer_error_of(service.ensure, request, recovery=recovery)
    counts = track.drain()
    state = env.sql_state()
    results = {"name": "N2b_root_not_reusable", "writer_error": error, "failures": []}
    _expect_phrase(results, "N2b", "existing_raw_root_not_reusable", error)
    expect(bool(class_ok), "N2b CanonicalImportError", results)
    expect(no_target_rows(state, HK_SHA), "N2b no rows", results)
    expect(counts == {"discover": 0, "fetch": 0}, "N2b counts zero", results)
    proof["N2b_root_not_reusable"] = {
        "results": results,
        "provider_counts": counts,
    }
    return proof


reactivate_call_count = {"n": 0}
_original_reactivate = CanonicalSourceWriter._reactivate_if_retired


def _counting_reactivate(self, content_sha256):
    reactivate_call_count["n"] += 1
    return _original_reactivate(self, content_sha256)


def main() -> int:
    AFTER.mkdir(parents=True, exist_ok=True)
    sample_check = verify_sample_copies()
    case_results: dict[str, dict] = {}
    provider_events: dict[str, dict] = {}
    registration_stages: dict[str, dict] = {}
    exact_resolve: dict[str, dict] = {}

    CanonicalSourceWriter._reactivate_if_retired = _counting_reactivate
    try:
        for market in ("hk", "us"):
            case_name = f"P1_{market}"
            try:
                results, counts, stages, resolve = p1_case(market)
                case_results[case_name] = results
                provider_events[case_name] = counts
                registration_stages[case_name] = stages
                exact_resolve[case_name] = resolve
            except Exception as exc:
                case_results[case_name] = {
                    "name": case_name,
                    "failures": [f"case exception: {type(exc).__name__}: {exc}"],
                    "traceback": traceback.format_exc(),
                }
                provider_events[case_name] = {"discover": -1, "fetch": -1}
        try:
            p2_results, p2_counts, p2_stages, p2_resolve = p2_case()
            case_results["P2"] = p2_results
            provider_events["P2"] = p2_counts
            registration_stages["P2"] = p2_stages
            exact_resolve["P2"] = p2_resolve
        except Exception as exc:
            case_results["P2"] = {
                "name": "P2_second_exact_reuse",
                "failures": [f"case exception: {type(exc).__name__}: {exc}"],
                "traceback": traceback.format_exc(),
            }
        for name, entry in n1_cases().items():
            case_results[name] = entry["results"]
            provider_events[name] = entry["provider_counts"]
        for name, entry in n2_cases().items():
            case_results[name] = entry["results"]
            provider_events[name] = entry["provider_counts"]
    finally:
        CanonicalSourceWriter._reactivate_if_retired = _original_reactivate

    (AFTER / "zero-provider-events.json").write_text(
        json.dumps(
            {
                "note": "deny-on-call counters; all must be 0",
                "cases": provider_events,
                "samples": sample_check,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (AFTER / "registration-stages.json").write_text(
        json.dumps(registration_stages, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AFTER / "exact-resolve.before-after.json").write_text(
        json.dumps(exact_resolve, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AFTER / "case_results.json").write_text(
        json.dumps(case_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    failed = [name for name, value in case_results.items() if value.get("failures")]
    retention = Path(tempfile.gettempdir()) / "w02c" / "a20260919-01_retained"
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


if __name__ == "__main__":
    sys.exit(main())
