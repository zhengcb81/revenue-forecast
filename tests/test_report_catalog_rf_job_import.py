"""Owner-public import of an already completed rf-job into ReportCatalog."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import threading

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from publication_registry import canonical_sha256  # noqa: E402
from report_catalog import CatalogError, ReportCatalog  # noqa: E402
from report_catalog_rf_job_import import (  # noqa: E402
    import_rf_job, make_stockwiki_resolvers, validate_source_export,
)
from revenue_report import render_markdown  # noqa: E402
from revenue_core import run_forecast  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402
import report_catalog_identity_cli as identity_cli  # noqa: E402
import report_catalog_identity_resolver as identity_bridge  # noqa: E402
import report_catalog_source_alias as source_alias  # noqa: E402


ENTITY_ID = "ENT_11111111-1111-4111-8111-111111111111"
LISTING_ID = "LST_22222222-2222-4222-8222-222222222222"
JOB_ID = "rfjob-test-20261109-issuer-one"
SOURCE_URL = "https://www.sec.gov/Archives/test/issuer-one-10k.htm"


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_ref() -> dict:
    digest = _sha(b"original annual filing")
    return {
        "schema_version": "2.0",
        "document_id": f"urn:company-wiki:document:sha256:{digest}",
        "source_id": f"urn:company-wiki:source:sha256:{digest}",
        "content_sha256": digest,
        "byte_size": len(b"original annual filing"),
        "mime_type": "application/pdf",
    }


def _manifest(ref: dict) -> dict:
    return {
        "byte_size": ref["byte_size"],
        "canonical_entity_id": None,
        "collector_name": "fixture",
        "collector_version": "1",
        "content_sha256": ref["content_sha256"],
        "display_name": "Test Co",
        "document_id": ref["document_id"],
        "document_kind": "annual_report",
        "fiscal_period": "FY",
        "fiscal_year": 2025,
        "form_type": "10-K",
        "language": "en",
        "market": "US",
        "mime_type": "application/pdf",
        "period_end": "2025-12-31",
        "provider": "sec",
        "provider_document_id": "test-accession",
        "published_date": "2026-03-01",
        "retrieved_at": "2026-03-02T00:00:00Z",
        "security_id": "TST",
        "source_id": ref["source_id"],
        "source_url": SOURCE_URL,
        "title": "Test Co FY2025 Form 10-K",
    }


def _source_bundle(ref: dict, *, manifest_changes: dict | None = None) -> dict:
    manifest = {**_manifest(ref), **(manifest_changes or {})}
    payload = {
        "schema_version": "2.0.0",
        "source_manifest_schema_version": "2.0.0",
        "evidence_span_schema_version": "1.0.0",
        "counts": {"source_manifests": 1, "evidence_spans": 0},
        "manifests": [manifest],
        "evidence_spans": [],
    }
    digest = canonical_sha256(payload)
    return {
        **payload,
        "bundle_sha256": digest,
        "export_id": f"urn:company-wiki:source-export:sha256:{digest}",
    }


def _identity() -> dict:
    listing = {
        "entity_id": ENTITY_ID,
        "listing_id": LISTING_ID,
        "security_id": "SEC_test-security",
        "market": "US",
        "exchange_raw": "NASDAQ",
        "exchange_mic": "XNAS",
        "ticker_raw": "TST",
        "ticker": "TST",
        "listing_status": "active",
        "source_binding_ref": "BIND_test",
        "valid_from": None,
        "valid_to": None,
        "currency": "USD",
    }
    return {
        "schema_version": "stockwiki.dashboard_identity/1",
        "authority": "stockwiki",
        "resolution_status": "resolved",
        "display_name": "Test Co",
        "entity_id": ENTITY_ID,
        "lookup_receipt_sha256": "a" * 64,
        "source_revision": f"identity_schema_version=2.0.0;identity_revision=1;entity={ENTITY_ID}",
        "entity": {
            "entity_id": ENTITY_ID,
            "canonical_name": "Test Co",
            "identity_state": "verified",
            "identity_revision": 1,
            "selected_listing_id": LISTING_ID,
            "listings": [listing],
            "securities": [{
                "entity_id": ENTITY_ID,
                "security_id": "SEC_test-security",
                "security_type": "ordinary",
                "share_class": None,
                "ordinary_security_ref": None,
                "adr_ratio": None,
            }],
        },
    }


def _proof(query: dict) -> dict:
    receipt_id = "IVR_test-receipt"
    listing = _identity()["entity"]["listings"][0]
    security = _identity()["entity"]["securities"][0]
    receipt = {
        "receipt_id": receipt_id,
        "kind": "verified_issuer",
        "effective_status": "active",
        "same_legal_issuer": True,
        "entity_id": ENTITY_ID,
        "canonical_name": "Test Co",
        "identity_revision": 1,
        "listing_ids": [LISTING_ID],
        "security_ids": ["SEC_test-security"],
        "evidence_ref": SOURCE_URL,
        "listing_attributes": {
            LISTING_ID: {
                **{key: value for key, value in listing.items() if key not in {"entity_id", "listing_id"}},
                "source_canonical_name": "Test Co",
                "source_namespace": "verified-fixture",
                "source_record_id": "US:TST",
            },
        },
        "security_attributes": {"SEC_test-security": security},
    }
    payload = {
        "entity_id": ENTITY_ID,
        "canonical_name": "Test Co",
        "identity_state": "verified",
        "identity_revision": 1,
        "identity_schema_version": "2.1.0",
        "verified_issuer_receipt_id": receipt_id,
        "listings": [listing],
        "securities": [security],
    }
    body = {
        "schema_version": "stockwiki.dashboard_issuer_proof/1",
        "authority": "stockwiki",
        "state": "available",
        "library_revision": "not_provided_no_global_revision",
        "reason_codes": [],
        "identity_revision": 1,
        "selected_listing_id": LISTING_ID,
        "query": query,
        "owner_package": {
            "object_type": "entity",
            "schema_version": "2.2.0",
            "payload": payload,
            "trusted_context": {
                "source_bindings": {},
                "market_registry": {"US": ["XNAS", "XNYS"]},
                "identity_receipts": {receipt_id: receipt},
            },
        },
    }
    return {**body, "receipt_sha256": canonical_sha256(body)}


def _job_fixture(
    tmp_path: Path, *, source_envelope_changes: dict | None = None,
) -> tuple[Path, dict]:
    ref = _source_ref()
    data = forecast_document()
    data["forecast_version"] = "test-job-v1"
    data["company_name"] = "Test Co"
    data["as_of_date"] = "2026-07-12"
    source_id = ref["source_id"]
    for source in data["sources"]:
        source["source_id"] = source_id
        source["url"] = SOURCE_URL
        source["published_date"] = "2026-03-01"
        source["company_wiki_trace"] = {
            "source_ref": ref,
            "source_manifest": _manifest(ref),
        }
    def bind_source_aliases(value: object) -> None:
        if isinstance(value, dict):
            for key, child in list(value.items()):
                if key == "source_id" and child == "filing":
                    value[key] = source_id
                elif key == "source_ids" and isinstance(child, list):
                    value[key] = [source_id if item == "filing" else item for item in child]
                else:
                    bind_source_aliases(child)
        elif isinstance(value, list):
            for child in value:
                bind_source_aliases(child)

    bind_source_aliases(data)
    result = run_forecast(data)
    input_bytes = _json_bytes(data)
    result_bytes = _json_bytes(result)
    report_bytes = render_markdown(result).encode("utf-8")
    manifest = _manifest(ref)
    source_envelope = {
        "schema_version": "source-preparation-result/1",
        "source": {
            "source_id": source_id,
            "url": SOURCE_URL,
            "company_wiki_trace": {"source_ref": ref, "source_manifest": manifest},
        },
        "filing_fetch": {
            "schema_version": "2.0",
            "status": "source_candidate",
            "calls": 2,
            "downloads": 0,
            "request_period": {
                "mode": "exact", "fiscal_year": 2025, "fiscal_period": None,
                "as_of_date": data["as_of_date"],
            },
            "filing": {
                "status": "source_candidate", "resolution_outcome": "reused_existing",
                "download_events": 0, "document_kind": "annual_report",
                "fiscal_year": 2025, "fiscal_period": "FY", "source_ref": ref,
            },
        },
    }
    if source_envelope_changes:
        source_envelope.update(source_envelope_changes)
    audit_bytes = b""
    registry_payload = {
        "schema_version": result["schema_version"],
        "engine_version": result["engine_version"],
        "input_sha256": result["input_sha256"],
        "result_sha256": result["result_sha256"],
        "validation_status": "validated",
        "publisher": "revenue-forecast",
        "artifact_type": "forecast",
        "registered_at": "2026-07-12T12:00:00Z",
        "receipt_sha256": "b" * 64,
    }
    registry_row = {
        **registry_payload,
        "line_sha256": canonical_sha256(registry_payload),
    }
    registry_bytes = (_json_bytes(registry_row) + b"\n")

    job_dir = tmp_path / "job-root" / "artifacts" / "rf_jobs" / "jobs" / JOB_ID
    files = {
        "job.json": b"",
        "stages/source/result-envelope.json": _json_bytes(source_envelope),
        "stages/compute/input.json": input_bytes,
        "stages/compute/result.json": result_bytes,
        "stages/compute/report.md": report_bytes,
        "stages/publication/audit.json": audit_bytes,
        "registry/publications.jsonl": registry_bytes,
    }
    hashes = {name: _sha(value) for name, value in files.items() if name != "job.json"}
    stage_artifacts = {
        "source": {"artifact": "result-envelope.json", "sha256": hashes["stages/source/result-envelope.json"]},
        "compute": {"artifact": "result.json", "sha256": hashes["stages/compute/result.json"]},
        "publication": {"artifact": "audit.json", "sha256": hashes["stages/publication/audit.json"]},
    }
    job = {
        "schema_version": "rf-job-state/1",
        "protocol": "rf-job/1",
        "kind": "rf_job",
        "owner_job_id": JOB_ID,
        "workflow": "full_research",
        "status": "succeeded",
        "status_known": True,
        "created_at": "2026-07-12T12:00:00Z",
        "updated_at": "2026-07-12T12:01:00Z",
        "forecast_input": data,
        "scope": {
            "company_query": "Test Co", "information_as_of": data["as_of_date"],
            "source_snapshot_ids": [source_id], "scenario_set": ["low", "base", "high"],
            "horizon_end_year": max(data["forecast_years"]),
        },
        "budget": {"new_downloads": 0, "paid_model_calls": 0, "wall_seconds_used": 1.0},
        "limits": {"max_cost_usd": "1.00", "max_new_downloads": 0},
        "limits_ref": "test-budget",
        "result": {"stage_artifacts": stage_artifacts},
        "stages": {
            stage: {
                "status": "completed",
                "attempts": [{
                    "stage": stage,
                    "attempt_id": f"{stage}-1",
                    "attempt_no": 1,
                    "status": "completed",
                    "exit_code": 0,
                    "result_sha256": hashes[path],
                }],
            }
            for stage, path in (
                ("source", "stages/source/result-envelope.json"),
                ("compute", "stages/compute/result.json"),
                ("publication", "stages/publication/audit.json"),
            )
        },
    }
    files["job.json"] = _json_bytes(job)
    for relative, content in files.items():
        path = job_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return job_dir.parents[3], {
        "job": job, "result": result, "input": data, "ref": ref,
        "job_sha256": _sha(files["job.json"]),
        "report_sha256": _sha(report_bytes),
    }


def _adapters(metadata: dict, *, proof_url: str | None = None, market: str = "US") -> tuple:
    manifest = _manifest(metadata["ref"])
    manifest["market"] = market
    bundle = _source_bundle(metadata["ref"], manifest_changes={"market": market})
    query_holder: dict = {}

    def export(source_ref: dict) -> dict:
        assert source_ref == metadata["ref"]
        return bundle

    def identity(entity_id: str, listing_id: str) -> dict:
        assert (entity_id, listing_id) == (ENTITY_ID, LISTING_ID)
        return _identity()

    def proof(query: dict) -> dict:
        query_holder.update(query)
        response = _proof(query)
        if proof_url is not None:
            receipt = response["owner_package"]["trusted_context"]["identity_receipts"]["IVR_test-receipt"]
            receipt["evidence_ref"] = proof_url
            response["receipt_sha256"] = canonical_sha256({
                key: value for key, value in response.items() if key != "receipt_sha256"
            })
        return response

    return export, identity, proof


def test_public_import_registers_completed_job_and_replays_without_duplication(tmp_path: Path) -> None:
    job_root, metadata = _job_fixture(tmp_path)
    catalog = ReportCatalog(root=tmp_path / "catalog")
    export, identity, proof = _adapters(metadata)
    first = import_rf_job(
        catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
        listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
        expected_report_sha256=metadata["report_sha256"],
        source_export=export,
        identity_resolver=identity, issuer_proof=proof,
    )
    second = import_rf_job(
        catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
        listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
        expected_report_sha256=metadata["report_sha256"],
        source_export=export,
        identity_resolver=identity, issuer_proof=proof,
    )

    assert first["status"] == "registered"
    assert first["forecast_executions"] == 0
    assert second["status"] == "already_registered"
    assert first["report_id"] == second["report_id"]
    assert len(catalog.list_reports(ENTITY_ID)["items"]) == 1
    report_id = first["report_id"]
    report = catalog.get_report(report_id)["view"]["report"]
    assert report["result_sha256"] == metadata["result"]["result_sha256"]
    assert report["company"]["listing_id"] == LISTING_ID
    run = catalog._index()[0][JOB_ID]
    assert run["company"]["entity_id"] == ENTITY_ID
    assert run["source_bound_identity_evidence"]["binding"]["kind"] == "issuer_receipt_exact_source_url"


@pytest.mark.parametrize(
    ("proof_url", "manifest_market", "expected_code"),
    [
        ("https://example.com/unrelated", "US", "source_identity_mismatch"),
        (None, "HK", "source_identity_mismatch"),
    ],
)
def test_source_identity_mismatch_is_refused_before_catalog_admission(
    tmp_path: Path, proof_url: str | None, manifest_market: str, expected_code: str,
) -> None:
    job_root, metadata = _job_fixture(tmp_path)
    catalog = ReportCatalog(root=tmp_path / "catalog")
    export, identity, proof = _adapters(metadata, proof_url=proof_url, market=manifest_market)
    with pytest.raises(CatalogError) as error:
        import_rf_job(
            catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
            listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
            expected_report_sha256=metadata["report_sha256"],
            source_export=export,
            identity_resolver=identity, issuer_proof=proof,
        )
    assert error.value.code == expected_code
    assert catalog.list_reports(ENTITY_ID)["items"] == []


def test_changed_job_artifact_cannot_overwrite_an_admitted_report(tmp_path: Path) -> None:
    job_root, metadata = _job_fixture(tmp_path)
    catalog = ReportCatalog(root=tmp_path / "catalog")
    export, identity, proof = _adapters(metadata)
    import_rf_job(
        catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
        listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
        expected_report_sha256=metadata["report_sha256"],
        source_export=export,
        identity_resolver=identity, issuer_proof=proof,
    )
    report_path = (
        job_root / "artifacts" / "rf_jobs" / "jobs" / JOB_ID
        / "stages" / "compute" / "report.md"
    )
    report_path.write_bytes(report_path.read_bytes() + b"tampered")
    with pytest.raises(CatalogError):
        import_rf_job(
            catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
            listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
            expected_report_sha256=metadata["report_sha256"],
            source_export=export,
            identity_resolver=identity, issuer_proof=proof,
        )
    assert len(catalog.list_reports(ENTITY_ID)["items"]) == 1


def test_job_must_match_independently_frozen_sha_before_catalog_admission(tmp_path: Path) -> None:
    job_root, metadata = _job_fixture(tmp_path)
    job_file = job_root / "artifacts" / "rf_jobs" / "jobs" / JOB_ID / "job.json"
    job_file.write_bytes(job_file.read_bytes() + b"\n")
    catalog = ReportCatalog(root=tmp_path / "catalog")
    export, identity, proof = _adapters(metadata)
    with pytest.raises(CatalogError) as error:
        import_rf_job(
            catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
            listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
            expected_report_sha256=metadata["report_sha256"],
            source_export=export, identity_resolver=identity, issuer_proof=proof,
        )
    assert error.value.code == "rf_job_artifact_mismatch"
    assert catalog.list_reports(ENTITY_ID)["items"] == []


def test_owner_identity_cli_routes_existing_job_through_public_import_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    owner = tmp_path / "rf-owner"
    scripts = owner / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "report_catalog.py").write_text("", encoding="utf-8")
    (scripts / "revenue_core.py").write_text("", encoding="utf-8")
    deployment_file = tmp_path / "deployment.json"
    deployment_file.write_text("{}", encoding="utf-8")
    job_root = tmp_path / "job-root"
    (job_root / "artifacts" / "rf_jobs" / "jobs" / JOB_ID).mkdir(parents=True)
    deployment = type("Deployment", (), {"company_wiki": object()})()
    source_runner = object()

    def identity_resolver(entity_id: str, listing_id: str) -> dict:
        return {"entity_id": entity_id, "listing_id": listing_id}

    def issuer_proof(query: dict) -> dict:
        return {"query": query}

    monkeypatch.setattr(identity_cli, "load_job_import_deployment", lambda path: deployment)
    monkeypatch.setattr(identity_cli, "make_source_export_runner", lambda config: source_runner)
    monkeypatch.setattr(identity_cli, "make_stockwiki_resolvers", lambda value: (identity_resolver, issuer_proof))
    captured_stdout = io.StringIO()
    monkeypatch.setattr(identity_cli.sys, "stdout", captured_stdout)
    seen: dict = {}

    def import_job(catalog, **kwargs):
        seen["root"] = catalog.root
        seen["kwargs"] = kwargs
        return {"status": "registered", "forecast_executions": 0}

    monkeypatch.setattr(identity_cli, "import_rf_job", import_job)
    code = identity_cli.main([
        "--owner-root", str(owner), "import-rf-job",
        "--deployment-config", str(deployment_file),
        "--job-root", str(job_root), "--job-id", JOB_ID,
        "--job-sha256", "b" * 64, "--report-sha256", "a" * 64,
        "--entity-id", ENTITY_ID, "--listing-id", LISTING_ID,
    ])
    assert code == 0
    assert seen["root"] == owner.resolve()
    assert seen["kwargs"]["job_root"] == Path(job_root)
    assert seen["kwargs"]["expected_job_sha256"] == "b" * 64
    assert seen["kwargs"]["expected_report_sha256"] == "a" * 64
    assert seen["kwargs"]["source_export"] is source_runner
    assert seen["kwargs"]["identity_resolver"] is identity_resolver
    assert seen["kwargs"]["issuer_proof"] is issuer_proof
    assert json.loads(captured_stdout.getvalue())["status"] == "registered"


def test_stockwiki_adapter_preserves_full_public_identity_dto(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bridge_config = object()
    deployment = type("Deployment", (), {
        "stockwiki_bridge_config": Path("bridge-config.json"),
    })()
    full_identity = {
        "schema_version": "stockwiki.dashboard_identity/1",
        "authority": "stockwiki",
        "resolution_status": "resolved",
        "entity_id": ENTITY_ID,
        "entity": {"entity_id": ENTITY_ID, "selected_listing_id": LISTING_ID},
    }
    proof = {"schema_version": "stockwiki.dashboard_issuer_proof/1"}
    monkeypatch.setattr(identity_bridge, "load_bridge_config", lambda path: bridge_config)

    def resolve_record(entity_id: str, *, config: object, listing_id: str | None = None) -> dict:
        assert (entity_id, config, listing_id) == (ENTITY_ID, bridge_config, LISTING_ID)
        return full_identity

    monkeypatch.setattr(identity_bridge, "resolve_identity_record", resolve_record)
    monkeypatch.setattr(source_alias, "read_issuer_proof", lambda config, query: proof)
    identity_resolver, issuer_proof = make_stockwiki_resolvers(deployment)
    assert identity_resolver(ENTITY_ID, LISTING_ID) == full_identity
    assert issuer_proof({"entity_id": ENTITY_ID}) == proof


def test_source_export_rejects_nested_versions_and_invalid_manifest_shape() -> None:
    ref = _source_ref()
    for field in ("source_manifest_schema_version", "evidence_span_schema_version"):
        bundle = _source_bundle(ref)
        bundle[field] = "unsupported"
        with pytest.raises(CatalogError, match="nested contract version"):
            validate_source_export(bundle, ref)

    missing_field = _source_bundle(ref)
    missing_field["manifests"][0].pop("market")
    with pytest.raises(CatalogError, match="manifest fields"):
        validate_source_export(missing_field, ref)

    invalid_type = _source_bundle(ref)
    invalid_type["manifests"][0]["fiscal_year"] = "2025"
    with pytest.raises(CatalogError, match="manifest values"):
        validate_source_export(invalid_type, ref)


def test_failed_owner_recheck_removes_staged_artifacts_and_retry_succeeds(tmp_path: Path) -> None:
    job_root, metadata = _job_fixture(tmp_path)
    catalog = ReportCatalog(root=tmp_path / "catalog")
    export, identity, proof = _adapters(metadata)
    calls = 0

    def fail_before_admission(source_ref: dict) -> dict:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise CatalogError("source_export_unavailable", "synthetic current-owner failure")
        return export(source_ref)

    with pytest.raises(CatalogError, match="synthetic current-owner failure"):
        import_rf_job(
            catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
            listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
            expected_report_sha256=metadata["report_sha256"], source_export=fail_before_admission,
            identity_resolver=identity, issuer_proof=proof,
        )

    artifact_dir = catalog.root / "artifacts" / "report_catalog" / "rf_job_imports" / JOB_ID
    assert catalog.list_reports(ENTITY_ID)["items"] == []
    assert not artifact_dir.exists()

    recovered = import_rf_job(
        catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
        listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
        expected_report_sha256=metadata["report_sha256"], source_export=export,
        identity_resolver=identity, issuer_proof=proof,
    )
    assert recovered["status"] == "registered"
    assert recovered["forecast_executions"] == 0


def test_concurrent_same_job_import_cannot_delete_admitted_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    job_root, metadata = _job_fixture(tmp_path)
    catalog = ReportCatalog(root=tmp_path / "catalog")
    export, identity, proof = _adapters(metadata)
    first_entered_append = threading.Event()
    allow_first_append = threading.Event()
    first_result: list[dict] = []
    first_error: list[BaseException] = []
    original_add_records = ReportCatalog.add_records

    def pause_first_append(self: ReportCatalog, **kwargs: object) -> dict:
        if threading.current_thread().name == "rf-job-import-first":
            first_entered_append.set()
            if not allow_first_append.wait(timeout=10):
                raise RuntimeError("test did not release first importer")
        return original_add_records(self, **kwargs)

    monkeypatch.setattr(ReportCatalog, "add_records", pause_first_append)

    def first_import() -> None:
        try:
            first_result.append(import_rf_job(
                catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
                listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
                expected_report_sha256=metadata["report_sha256"], source_export=export,
                identity_resolver=identity, issuer_proof=proof,
            ))
        except BaseException as exc:
            first_error.append(exc)

    worker = threading.Thread(target=first_import, name="rf-job-import-first")
    worker.start()
    if not first_entered_append.wait(timeout=10):
        allow_first_append.set()
        worker.join(timeout=10)
        pytest.fail("first importer did not reach the catalog append")

    try:
        with pytest.raises(CatalogError) as busy:
            import_rf_job(
                catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
                listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
                expected_report_sha256=metadata["report_sha256"], source_export=export,
                identity_resolver=identity, issuer_proof=proof,
            )
        assert busy.value.code == "rf_job_import_busy"
        assert catalog.list_reports(ENTITY_ID)["items"] == []
    finally:
        allow_first_append.set()
        worker.join(timeout=10)

    assert not worker.is_alive()
    assert first_error == []
    assert first_result[0]["status"] == "registered"
    replay = import_rf_job(
        catalog, job_root=job_root, job_id=JOB_ID, entity_id=ENTITY_ID,
        listing_id=LISTING_ID, expected_job_sha256=metadata["job_sha256"],
        expected_report_sha256=metadata["report_sha256"], source_export=export,
        identity_resolver=identity, issuer_proof=proof,
    )
    assert replay["status"] == "already_registered"
    assert replay["forecast_executions"] == 0

    runs, attempts, reports, _ = catalog._index()
    assert list(runs) == [JOB_ID]
    assert list(reports) == [first_result[0]["report_id"]]
    stored_attempt = attempts[(JOB_ID, JOB_ID + ".succeeded")]
    for artifact in stored_attempt["source_evidence"]["artifacts"].values():
        catalog._read_artifact(artifact)
    catalog._validate_attempt_source(stored_attempt)
    catalog._validate_report_artifact(reports[first_result[0]["report_id"]])


def test_stockwiki_public_adapters_round_trip_real_process_dtos(tmp_path: Path) -> None:
    owner = tmp_path / "stockwiki-owner"
    sw_root = tmp_path / "stockwiki-data"
    owner.mkdir()
    sw_root.mkdir()
    full_identity = {
        "schema_version": "stockwiki.dashboard_identity/1",
        "command": "resolve",
        "authority": "stockwiki",
        "resolution_status": "resolved",
        "entity_id": ENTITY_ID,
        "display_name": "Test Co",
        "source_revision": "identity_schema_version=2.0.0;identity_revision=1",
        "library_revision": "not_provided_no_global_revision",
        "library_scope": "stockwiki_canonical_identity_store",
        "entity": {
            "entity_id": ENTITY_ID,
            "canonical_name": "Test Co",
            "identity_state": "verified",
            "identity_revision": 1,
            "selected_listing_id": LISTING_ID,
        },
    }
    full_identity["lookup_receipt_sha256"] = canonical_sha256(full_identity)
    identity_json = json.dumps(full_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    identity_cli = owner / "dashboard_identity_bridge_cli.py"
    identity_cli.write_text(
        "import json, sys\n"
        f"payload = json.loads({identity_json!r})\n"
        "print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')))\n",
        encoding="utf-8",
    )
    proof_cli = owner / "dashboard_issuer_proof_cli.py"
    proof_cli.write_text(
        "import hashlib, json, sys\n"
        "query = json.loads(sys.stdin.buffer.read().decode('utf-8'))\n"
        "proof = {'schema_version':'stockwiki.dashboard_issuer_proof/1',"
        "'authority':'stockwiki','state':'available',"
        "'library_revision':'not_provided_no_global_revision','reason_codes':[],"
        "'query':query}\n"
        "body = json.dumps(proof, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')\n"
        "proof['receipt_sha256'] = hashlib.sha256(body).hexdigest()\n"
        "print(json.dumps(proof, ensure_ascii=False, sort_keys=True, separators=(',', ':')))\n",
        encoding="utf-8",
    )
    config_path = tmp_path / "bridge.json"
    config_path.write_text(json.dumps({
        "python": sys.executable,
        "cli": str(identity_cli),
        "owner_root": str(owner),
        "timeout_seconds": 5,
        "max_output_bytes": 65536,
        "sw_root": str(sw_root),
    }), encoding="utf-8")
    deployment = type("Deployment", (), {"stockwiki_bridge_config": config_path})()

    identity_resolver, issuer_proof = make_stockwiki_resolvers(deployment)
    identity = identity_resolver(ENTITY_ID, LISTING_ID)
    query = {"entity_id": ENTITY_ID, "listing_id": LISTING_ID, "as_of": "2026-11-09T23:59:59Z"}
    proof = issuer_proof(query)

    assert identity == full_identity
    assert proof["query"] == query
    assert proof["receipt_sha256"] == canonical_sha256({
        key: value for key, value in proof.items() if key != "receipt_sha256"
    })
