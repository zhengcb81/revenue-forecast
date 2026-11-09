"""Register an already completed rf-job through RF's managed report catalog.

The importer never runs source preparation or forecast computation. It reads
one immutable job, verifies the job's own stage artifacts and publication
record, refreshes the source through company-wiki SourceExport v2, and binds
that exact source URL to StockWiki's public verified-issuer receipt.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unicodedata
from typing import Any, Callable

from owner_file_lock import OwnerFileLock
from publication_registry import canonical_sha256, validate_registry_text
from report_catalog import (
    CatalogError,
    ReportCatalog,
    _frozen_reporting_scale,
    _sha,
)


IMPORT_SCHEMA = "rf-job-import/1"
DEPLOYMENT_SCHEMA = "rf-job-import-deployment/1"
SOURCE_EXPORT_SCHEMA = "2.0.0"
SOURCE_MANIFEST_SCHEMA = "2.0.0"
EVIDENCE_SPAN_SCHEMA = "1.0.0"
SOURCE_EXPORT_ID_PREFIX = "urn:company-wiki:source-export:sha256:"
MAX_DEPLOYMENT_CONFIG_BYTES = 65536
MAX_SOURCE_EXPORT_BYTES = 8 * 1024 * 1024
SOURCE_FILES = {
    "job": "job.json",
    "source_result": "stages/source/result-envelope.json",
    "compute_input": "stages/compute/input.json",
    "compute_result": "stages/compute/result.json",
    "report_markdown": "stages/compute/report.md",
    "publication_audit": "stages/publication/audit.json",
    "publication_registry": "registry/publications.jsonl",
}
_OPAQUE_JOB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,191}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_ENTITY_ID = re.compile(
    r"^ENT_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_LISTING_ID = re.compile(
    r"^LST_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_SOURCE_EXPORT_MANIFEST_FIELDS = frozenset({
    "document_id", "source_id", "content_sha256", "byte_size", "mime_type",
    "title", "document_kind", "published_date", "source_url", "retrieved_at",
    "collector_name", "collector_version", "canonical_entity_id", "display_name",
    "market", "security_id", "fiscal_period", "period_end", "form_type", "provider",
    "provider_document_id", "language", "fiscal_year",
})
_SOURCE_EXPORT_MANIFEST_TEXT_FIELDS = _SOURCE_EXPORT_MANIFEST_FIELDS - {
    "byte_size", "fiscal_year",
}


def _need(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise CatalogError(code, message)


def _read_json_bytes(raw: bytes, code: str = "rf_job_artifact_invalid") -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            _need(key not in result, code, "JSON contains duplicate keys")
            result[key] = value
        return result

    def constant(_: str) -> None:
        raise CatalogError(code, "JSON contains a non-finite number")

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise CatalogError(code, "JSON artifact is invalid") from exc
    _need(isinstance(value, dict), code, "JSON artifact must contain an object")
    return value


def _text(value: Any, code: str = "rf_job_artifact_invalid") -> str:
    _need(isinstance(value, str) and bool(value.strip()) and value == value.strip(),
          code, "required text field is invalid")
    return value


def _normalized_name(value: Any) -> str:
    text = _text(value, "source_identity_mismatch")
    return "".join(
        character for character in unicodedata.normalize("NFKC", text).casefold()
        if character.isalnum()
    )


def _source_ref(value: Any) -> dict[str, Any]:
    _need(isinstance(value, dict), "source_identity_mismatch", "SourceRef is missing")
    expected = {"schema_version", "document_id", "source_id", "content_sha256", "byte_size", "mime_type"}
    _need(set(value) == expected, "source_identity_mismatch", "SourceRef fields differ from the public contract")
    digest = value.get("content_sha256")
    _need(isinstance(digest, str) and _HEX64.fullmatch(digest) is not None,
          "source_identity_mismatch", "SourceRef content hash is invalid")
    _need(
        value.get("schema_version") == "2.0"
        and value.get("document_id") == f"urn:company-wiki:document:sha256:{digest}"
        and value.get("source_id") == f"urn:company-wiki:source:sha256:{digest}"
        and type(value.get("byte_size")) is int and value["byte_size"] > 0
        and isinstance(value.get("mime_type"), str) and bool(value["mime_type"].strip()),
        "source_identity_mismatch", "SourceRef values are inconsistent",
    )
    return value


def validate_source_export(bundle: dict[str, Any], expected_ref: dict[str, Any]) -> dict[str, Any]:
    """Validate CWP's pathless export envelope and return its one manifest."""
    ref = _source_ref(expected_ref)
    required = {
        "schema_version", "source_manifest_schema_version", "evidence_span_schema_version",
        "counts", "manifests", "evidence_spans", "bundle_sha256", "export_id",
    }
    _need(isinstance(bundle, dict) and set(bundle) == required,
          "source_export_invalid", "CWP SourceExport v2 response fields are invalid")
    _need(bundle.get("schema_version") == SOURCE_EXPORT_SCHEMA,
          "source_export_invalid", "CWP SourceExport v2 version is unsupported")
    _need(bundle.get("source_manifest_schema_version") == SOURCE_MANIFEST_SCHEMA
          and bundle.get("evidence_span_schema_version") == EVIDENCE_SPAN_SCHEMA,
          "source_export_invalid", "CWP SourceExport nested contract version is unsupported")
    manifests = bundle.get("manifests")
    spans = bundle.get("evidence_spans")
    counts = bundle.get("counts")
    _need(isinstance(manifests, list) and len(manifests) == 1
          and isinstance(manifests[0], dict), "source_export_invalid", "export must contain one manifest")
    manifest = manifests[0]
    _need(set(manifest) == _SOURCE_EXPORT_MANIFEST_FIELDS,
          "source_export_invalid", "CWP SourceExport manifest fields are invalid")
    _need(all(manifest[field] is None or isinstance(manifest[field], str)
              for field in _SOURCE_EXPORT_MANIFEST_TEXT_FIELDS)
          and (manifest["fiscal_year"] is None or type(manifest["fiscal_year"]) is int)
          and (manifest["byte_size"] is None or type(manifest["byte_size"]) is int),
          "source_export_invalid", "CWP SourceExport manifest values are invalid")
    _need(spans == [] and isinstance(counts, dict)
          and counts == {"source_manifests": 1, "evidence_spans": 0},
          "source_export_invalid", "export counts differ from the requested one-source export")
    payload = {key: value for key, value in bundle.items() if key not in {"bundle_sha256", "export_id"}}
    digest = canonical_sha256(payload)
    _need(bundle.get("bundle_sha256") == digest
          and bundle.get("export_id") == SOURCE_EXPORT_ID_PREFIX + digest,
          "source_export_invalid", "CWP SourceExport v2 hash does not verify")
    for field in ("document_id", "source_id", "content_sha256", "byte_size", "mime_type"):
        _need(manifest.get(field) == ref[field], "source_export_mismatch",
              "CWP manifest differs from the job SourceRef")
    return manifest


_SOURCE_SCOPE_FIELDS = (
    "document_id", "source_id", "content_sha256", "byte_size", "mime_type", "display_name",
    "document_kind", "fiscal_year", "fiscal_period", "form_type", "market", "security_id",
    "published_date", "period_end", "provider", "provider_document_id", "source_url",
)


def _source_from_input(input_document: dict[str, Any], source_envelope: dict[str, Any]) -> tuple[dict, dict]:
    ref = None
    sources = input_document.get("sources")
    _need(isinstance(sources, list), "source_identity_mismatch", "forecast input sources are missing")
    traced: list[tuple[dict, dict]] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        trace = source.get("company_wiki_trace")
        if isinstance(trace, dict) and isinstance(trace.get("source_ref"), dict):
            traced.append((source, trace))
    _need(len(traced) == 1, "source_identity_mismatch",
          "forecast input must carry exactly one primary CWP SourceRef")
    source, trace = traced[0]
    ref = _source_ref(trace.get("source_ref"))
    manifest = trace.get("source_manifest")
    _need(isinstance(manifest, dict), "source_identity_mismatch", "input source manifest is missing")
    _need(source.get("source_id") == ref["source_id"], "source_identity_mismatch",
          "forecast source ID differs from CWP SourceRef")
    envelope_source = source_envelope.get("source")
    _need(isinstance(envelope_source, dict), "source_identity_mismatch",
          "source preparation result lacks its source")
    envelope_trace = envelope_source.get("company_wiki_trace")
    _need(isinstance(envelope_trace, dict)
          and envelope_trace.get("source_ref") == ref,
          "source_identity_mismatch", "source preparation SourceRef differs from forecast input")
    envelope_manifest = envelope_trace.get("source_manifest")
    _need(isinstance(envelope_manifest, dict), "source_identity_mismatch",
          "source preparation manifest is missing")
    _need(envelope_source.get("source_id") == source.get("source_id") == ref["source_id"]
          and envelope_source.get("url") == source.get("url")
          and envelope_source.get("url") == manifest.get("source_url"),
          "source_identity_mismatch", "source preparation locator differs from the forecast source")
    _need(all(manifest.get(field) == envelope_manifest.get(field) for field in _SOURCE_SCOPE_FIELDS),
          "source_identity_mismatch", "source preparation scope differs from the forecast source")
    return ref, manifest


def _validate_issuer_proof(
    identity: dict[str, Any], proof: dict[str, Any], *,
    entity_id: str, listing_id: str, query: dict[str, str],
    manifest: dict[str, Any], company_name: str,
) -> dict[str, Any]:
    """Validate current StockWiki identity and its exact source-URL issuer proof."""
    _need(identity.get("schema_version") == "stockwiki.dashboard_identity/1"
          and identity.get("authority") == "stockwiki"
          and identity.get("resolution_status") == "resolved"
          and identity.get("entity_id") == entity_id
          and isinstance(identity.get("entity"), dict)
          and identity["entity"].get("selected_listing_id") == listing_id,
          "identity_unverified", "StockWiki did not resolve the requested entity/listing")
    identity_receipt = identity.get("lookup_receipt_sha256")
    _need(isinstance(identity_receipt, str) and _HEX64.fullmatch(identity_receipt) is not None,
          "identity_unverified", "StockWiki identity receipt is invalid")
    identity_entity = identity.get("entity")
    _need(isinstance(identity_entity, dict)
          and identity_entity.get("entity_id") == entity_id
          and identity_entity.get("identity_state") == "verified",
          "identity_unverified", "StockWiki entity is not verified")
    canonical_name = _text(identity_entity.get("canonical_name"), "identity_unverified")
    _need(_normalized_name(canonical_name) == _normalized_name(company_name)
          and _normalized_name(canonical_name) == _normalized_name(manifest.get("display_name")),
          "source_identity_mismatch", "CWP source, RF input and StockWiki names do not identify one issuer")
    listings = identity_entity.get("listings")
    selected = [item for item in listings if isinstance(item, dict)
                and item.get("listing_id") == listing_id] if isinstance(listings, list) else []
    _need(len(selected) == 1 and selected[0].get("entity_id") == entity_id
          and selected[0].get("listing_status") == "active",
          "identity_unverified", "requested StockWiki listing is not uniquely active")
    listing = selected[0]
    _need(all(isinstance(listing.get(field), str) and bool(listing[field])
              for field in ("market", "security_id", "exchange_mic")),
          "identity_unverified", "selected StockWiki listing lacks market, security, or exchange identity")
    _need(identity_entity.get("identity_revision") == identity.get("entity", {}).get("identity_revision"),
          "identity_unverified", "StockWiki identity revision is inconsistent")

    _need(proof.get("schema_version") == "stockwiki.dashboard_issuer_proof/1"
          and proof.get("authority") == "stockwiki"
          and proof.get("state") == "available"
          and proof.get("reason_codes") == []
          and proof.get("query") == query
          and proof.get("selected_listing_id") == listing_id,
          "issuer_proof_unavailable", "StockWiki issuer proof is unavailable or bound to another query")
    receipt_sha = proof.get("receipt_sha256")
    _need(isinstance(receipt_sha, str) and _HEX64.fullmatch(receipt_sha) is not None
          and receipt_sha == canonical_sha256(
              {key: value for key, value in proof.items() if key != "receipt_sha256"}
          ), "issuer_proof_invalid", "StockWiki issuer proof receipt hash does not verify")
    package = proof.get("owner_package")
    _need(isinstance(package, dict) and package.get("object_type") == "entity"
          and package.get("schema_version") == "2.2.0",
          "issuer_proof_invalid", "StockWiki issuer proof package is incompatible")
    payload = package.get("payload")
    context = package.get("trusted_context")
    _need(isinstance(payload, dict) and isinstance(context, dict)
          and payload.get("identity_schema_version") == "2.1.0"
          and payload.get("identity_state") == "verified"
          and payload.get("entity_id") == entity_id
          and payload.get("canonical_name") == canonical_name
          and payload.get("identity_revision") == identity_entity.get("identity_revision")
          and proof.get("identity_revision") == identity_entity.get("identity_revision"),
          "issuer_proof_invalid", "StockWiki issuer proof identity differs from fresh resolution")
    proof_listings = payload.get("listings")
    proof_listing = [item for item in proof_listings if isinstance(item, dict)
                     and item.get("listing_id") == listing_id] if isinstance(proof_listings, list) else []
    _need(len(proof_listing) == 1 and proof_listing[0] == listing,
          "issuer_proof_invalid", "StockWiki issuer proof listing differs from fresh resolution")
    receipt_id = _text(payload.get("verified_issuer_receipt_id"), "issuer_proof_invalid")
    receipts = context.get("identity_receipts")
    _need(isinstance(receipts, dict), "issuer_proof_invalid", "issuer receipt is missing")
    receipt = receipts.get(receipt_id)
    _need(isinstance(receipt, dict)
          and receipt.get("receipt_id") == receipt_id
          and receipt.get("kind") == "verified_issuer"
          and receipt.get("effective_status") == "active"
          and receipt.get("same_legal_issuer") is True
          and receipt.get("entity_id") == entity_id
          and receipt.get("identity_revision") == identity_entity.get("identity_revision")
          and listing_id in receipt.get("listing_ids", [])
          and receipt.get("evidence_ref") == manifest.get("source_url"),
          "source_identity_mismatch", "verified issuer receipt does not bind the exact CWP source URL")
    listing_attributes = receipt.get("listing_attributes")
    receipt_listing = listing_attributes.get(listing_id) if isinstance(listing_attributes, dict) else None
    _need(isinstance(receipt_listing, dict)
          and all(receipt_listing.get(field) == listing.get(field)
                  for field in (
                      "market", "security_id", "exchange_mic", "exchange_raw", "ticker",
                      "ticker_raw", "listing_status", "currency", "valid_from", "valid_to",
                      "source_binding_ref",
                  ) if field in listing),
          "issuer_proof_invalid", "verified issuer receipt listing identity differs")
    return {
        "schema_version": "rf-composite-source-identity-proof/1",
        "authority": "company-wiki+stockwiki-public-owners",
        "entity_id": entity_id,
        "listing_id": listing_id,
        "canonical_name": canonical_name,
        "identity_revision": identity_entity["identity_revision"],
        "identity_lookup_receipt_sha256": identity_receipt,
        "issuer_receipt_id": receipt_id,
        "issuer_proof_receipt_sha256": receipt_sha,
        "issuer_proof_query": query,
        "source_export_id": _text(proof.get("query", {}).get("source_export_id"))
        if isinstance(proof.get("query"), dict) and "source_export_id" in proof["query"]
        else None,
        "source_ref": manifest["source_id"],
        "source_url": manifest["source_url"],
        "source_market": manifest["market"],
        "source_security_id": manifest["security_id"],
        "source_document_kind": manifest["document_kind"],
        "source_fiscal_year": manifest["fiscal_year"],
        "source_fiscal_period": manifest["fiscal_period"],
        "binding": {"kind": "issuer_receipt_exact_source_url", "evidence_ref": manifest["source_url"]},
    }


def _job_files(job_root: Path, job_id: str) -> tuple[Path, dict[str, Path]]:
    _need(isinstance(job_id, str) and _OPAQUE_JOB_ID.fullmatch(job_id) is not None,
          "job_id_invalid", "job ID is invalid")
    try:
        root = job_root.resolve(strict=True)
        job_dir = (root / "artifacts" / "rf_jobs" / "jobs" / job_id).resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise CatalogError("rf_job_unavailable", "selected rf-job is unavailable") from exc
    _need(root.is_dir() and job_dir.is_dir() and job_dir.is_relative_to(root),
          "rf_job_unavailable", "selected rf-job is outside the source job root")
    paths: dict[str, Path] = {}
    for key, relative in SOURCE_FILES.items():
        candidate = (job_dir / Path(relative)).resolve(strict=True)
        _need(candidate.is_relative_to(job_dir) and candidate.is_file(),
              "rf_job_unavailable", "required rf-job artifact is unavailable")
        paths[key] = candidate
    return job_dir, paths


def _read_job(
    paths: dict[str, Path], job_id: str, *, expected_report_sha256: str,
) -> tuple[dict[str, Any], dict[str, bytes], dict[str, dict]]:
    raw = {key: path.read_bytes() for key, path in paths.items()}
    job = _read_json_bytes(raw["job"])
    _need(job.get("schema_version") == "rf-job-state/1"
          and job.get("protocol") == "rf-job/1"
          and job.get("kind") == "rf_job"
          and job.get("owner_job_id") == job_id
          and job.get("status") == "succeeded"
          and job.get("status_known") is True,
          "rf_job_not_succeeded", "rf-job does not record one known successful terminal state")
    _need(job.get("workflow") == "full_research", "rf_job_invalid", "rf-job workflow is not a research forecast")
    input_document = _read_json_bytes(raw["compute_input"])
    result = _read_json_bytes(raw["compute_result"])
    source_result = _read_json_bytes(raw["source_result"])
    _need(job.get("forecast_input") == input_document,
          "rf_job_artifact_mismatch", "job request input differs from the actual compute input")
    _need(canonical_sha256(input_document) == result.get("input_sha256"),
          "rf_job_artifact_mismatch", "compute input does not reproduce the forecast input hash")
    _need(result.get("result_sha256") == canonical_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"}
    ), "rf_job_artifact_mismatch", "compute result self-hash does not verify")
    _need(result.get("schema_version") == input_document.get("schema_version")
          and result.get("company_name") == input_document.get("company_name")
          and result.get("as_of_date") == input_document.get("as_of_date"),
          "rf_job_artifact_mismatch", "result identity differs from the executed input")
    stage_artifacts = job.get("result", {}).get("stage_artifacts")
    stages = job.get("stages")
    _need(isinstance(stage_artifacts, dict) and isinstance(stages, dict),
          "rf_job_artifact_mismatch", "job terminal stage record is incomplete")
    stage_map = {
        "source": ("source_result", "stages/source/result-envelope.json"),
        "compute": ("compute_result", "stages/compute/result.json"),
        "publication": ("publication_audit", "stages/publication/audit.json"),
    }
    for stage, (artifact_key, _) in stage_map.items():
        record = stage_artifacts.get(stage)
        stage_state = stages.get(stage)
        _need(isinstance(record, dict) and isinstance(stage_state, dict)
              and record.get("sha256") == _sha(raw[artifact_key])
              and stage_state.get("status") == "completed",
              "rf_job_artifact_mismatch", f"{stage} stage does not bind its retained artifact")
        attempts = stage_state.get("attempts")
        successful = [item for item in attempts if isinstance(item, dict)
                      and item.get("status") == "completed" and item.get("exit_code") == 0
                      and item.get("result_sha256") == _sha(raw[artifact_key])]
        _need(isinstance(attempts, list) and len(successful) >= 1,
              "rf_job_artifact_mismatch", f"{stage} has no successful artifact-producing attempt")
    _need(source_result.get("schema_version") == "source-preparation-result/1",
          "source_evidence_invalid", "source stage result schema is unsupported")
    ff = source_result.get("filing_fetch")
    _need(isinstance(ff, dict) and ff.get("status") == "source_candidate"
          and ff.get("downloads") == 0,
          "source_evidence_invalid", "source stage did not retain a reusable filing candidate")
    period = ff.get("request_period")
    _need(isinstance(period, dict)
          and period.get("fiscal_year") == input_document.get("base_year")
          and period.get("as_of_date") == input_document.get("as_of_date"),
          "source_evidence_invalid", "source stage request period differs from forecast base")
    filing = ff.get("filing")
    _need(isinstance(filing, dict) and filing.get("status") == "source_candidate"
          and filing.get("resolution_outcome") == "reused_existing"
          and filing.get("download_events") == 0,
          "source_evidence_invalid", "source stage did not prove existing-source reuse")
    ref, input_manifest = _source_from_input(input_document, source_result)
    _need(filing.get("source_ref") == ref,
          "source_evidence_invalid", "filing candidate SourceRef differs from forecast input")
    report_bytes = raw["report_markdown"]
    _need(isinstance(expected_report_sha256, str)
          and _HEX64.fullmatch(expected_report_sha256) is not None
          and _sha(report_bytes) == expected_report_sha256,
          "rf_job_artifact_mismatch", "retained Markdown differs from the independently recorded report hash")
    try:
        report_bytes.decode("utf-8")
    except UnicodeError as exc:
        raise CatalogError("rf_job_artifact_invalid", "retained Markdown is not UTF-8") from exc
    registry = validate_registry_text(raw["publication_registry"].decode("utf-8"))
    matches = [item for item in registry if item.get("artifact_type") == "forecast"
               and item.get("input_sha256") == result.get("input_sha256")
               and item.get("result_sha256") == result.get("result_sha256")
               and item.get("validation_status") == "validated"]
    _need(len(matches) == 1, "rf_job_publication_invalid",
          "job publication registry lacks one matching validated forecast")
    return job, raw, {
        "input": input_document,
        "result": result,
        "source_result": source_result,
        "source_ref": ref,
        "source_manifest": input_manifest,
        "publication": matches[0],
    }


def _validate_source_period(
    manifest: dict[str, Any], *, input_document: dict[str, Any], source_result: dict[str, Any]
) -> None:
    _need(manifest.get("document_kind") == "annual_report"
          and manifest.get("fiscal_year") == input_document.get("base_year")
          and manifest.get("fiscal_period") == "FY",
          "source_period_mismatch", "CWP source is not the forecast's matching annual fiscal period")
    ff = source_result["filing_fetch"]
    filing = ff["filing"]
    for field in ("document_kind", "fiscal_year", "fiscal_period"):
        _need(filing.get(field) == manifest.get(field), "source_period_mismatch",
              "CWP manifest period differs from the FF source candidate")
    _need(manifest.get("published_date") <= input_document.get("as_of_date"),
          "source_period_mismatch", "source was published after the forecast information date")


def _validate_job_attempt(catalog: ReportCatalog, attempt: dict[str, Any]) -> None:
    evidence = attempt.get("source_evidence")
    _need(isinstance(evidence, dict) and evidence.get("kind") == "rf_job_record",
          "attempt_unverified", "attempt lacks rf-job evidence")
    _need(set(evidence) == {"kind", "job_id", "artifacts", "report_sha256"}
          and isinstance(evidence.get("artifacts"), dict)
          and set(evidence["artifacts"]) == set(SOURCE_FILES),
          "attempt_unverified", "rf-job evidence artifact set is incomplete")
    _need(evidence.get("job_id") == attempt.get("run_id"),
          "attempt_unverified", "rf-job evidence ID differs from the registered run")
    raw: dict[str, bytes] = {}
    for key, ref in evidence["artifacts"].items():
        _need(isinstance(ref, dict), "attempt_unverified", "rf-job artifact reference is invalid")
        raw[key] = catalog._read_artifact(ref)
    job = _read_json_bytes(raw["job"])
    _need(job.get("owner_job_id") == evidence["job_id"]
          and job.get("status") == "succeeded" and job.get("status_known") is True,
          "attempt_unverified", "retained rf-job no longer proves success")
    input_document = _read_json_bytes(raw["compute_input"])
    result = _read_json_bytes(raw["compute_result"])
    _need(canonical_sha256(input_document) == result.get("input_sha256")
          and result.get("result_sha256") == canonical_sha256(
              {key: value for key, value in result.items() if key != "result_sha256"}
          ), "attempt_unverified", "retained rf-job input/result hashes do not verify")
    stage_artifacts = job.get("result", {}).get("stage_artifacts", {})
    for stage, raw_key in (("source", "source_result"), ("compute", "compute_result"),
                           ("publication", "publication_audit")):
        record = stage_artifacts.get(stage, {})
        stage_state = job.get("stages", {}).get(stage, {})
        _need(record.get("sha256") == _sha(raw[raw_key])
              and stage_state.get("status") == "completed"
              and any(isinstance(item, dict) and item.get("exit_code") == 0
                      and item.get("result_sha256") == _sha(raw[raw_key])
                      for item in stage_state.get("attempts", [])),
              "attempt_unverified", "retained rf-job stage evidence is inconsistent")
    registry = validate_registry_text(raw["publication_registry"].decode("utf-8"))
    _need(any(item.get("artifact_type") == "forecast"
              and item.get("input_sha256") == result.get("input_sha256")
              and item.get("result_sha256") == result.get("result_sha256")
              and item.get("validation_status") == "validated" for item in registry),
          "attempt_unverified", "retained publication record does not bind this forecast")
    _need(isinstance(evidence.get("report_sha256"), str)
          and _HEX64.fullmatch(evidence["report_sha256"]) is not None
          and _sha(raw["report_markdown"]) == evidence["report_sha256"],
          "attempt_unverified", "retained report differs from its admitted SHA-256")
    source_result = _read_json_bytes(raw["source_result"])
    ff = source_result.get("filing_fetch", {})
    filing = ff.get("filing", {}) if isinstance(ff, dict) else {}
    _need(source_result.get("schema_version") == "source-preparation-result/1"
          and isinstance(ff, dict) and ff.get("status") == "source_candidate"
          and isinstance(filing, dict) and filing.get("download_events") == 0
          and filing.get("resolution_outcome") == "reused_existing",
          "attempt_unverified", "retained job did not use the existing source")


def _catalog_artifacts(
    catalog: ReportCatalog, job_id: str, raw: dict[str, bytes]
) -> tuple[dict[str, dict[str, Any]], list[Path]]:
    import_root = (catalog.root / "artifacts" / "report_catalog" / "rf_job_imports").resolve()
    _need(import_root.is_relative_to(catalog.root), "catalog_path_forbidden",
          "import artifact root escapes the RF owner root")
    directory = (import_root / job_id).resolve()
    _need(directory.is_relative_to(import_root), "catalog_path_forbidden",
          "job import directory escapes the RF artifact root")
    directory.mkdir(parents=True, exist_ok=True)
    refs: dict[str, dict[str, Any]] = {}
    created: list[Path] = []
    try:
        for key, relative in SOURCE_FILES.items():
            filename = relative.replace("/", "__")
            path = directory / filename
            expected = raw[key]
            if path.exists():
                _need(path.is_file() and path.read_bytes() == expected,
                      "rf_job_import_conflict", "an imported job artifact already exists with different bytes")
            else:
                from owner_atomic_io import replace_file_bytes
                replace_file_bytes(path, expected)
                created.append(path)
            refs[key] = catalog.artifact_ref(path)
        return refs, created
    except Exception:
        _remove_created_files(created, directory, import_root)
        raise


def _remove_created_files(created: list[Path], directory: Path, import_root: Path) -> None:
    for path in reversed(created):
        try:
            resolved = path.resolve(strict=False)
            if resolved.is_relative_to(import_root) and resolved.is_file():
                resolved.unlink()
        except OSError:
            pass
    for directory_to_remove in (directory, directory.parent):
        try:
            if directory_to_remove.is_relative_to(import_root) and directory_to_remove.is_dir():
                directory_to_remove.rmdir()
        except OSError:
            pass


def _job_import_lock(catalog: ReportCatalog, job_id: str) -> OwnerFileLock:
    owner_root = catalog.root.resolve()
    managed_root = (owner_root / "artifacts" / "report_catalog").resolve()
    _need(managed_root.is_relative_to(owner_root), "catalog_path_forbidden",
          "managed report catalog escapes the RF owner root")
    lock_root = managed_root / ".locks" / "rf_job_imports"
    try:
        lock_root.mkdir(parents=True, exist_ok=True)
        lock_root = lock_root.resolve(strict=True)
    except OSError as exc:
        raise CatalogError("rf_job_import_unavailable", "rf-job import lock is unavailable") from exc
    _need(lock_root.is_relative_to(managed_root) and lock_root.is_dir(),
          "catalog_path_forbidden", "rf-job import lock directory escapes the managed catalog")
    # Job IDs are opaque protocol identifiers, not filesystem path components.
    lock_name = hashlib.sha256(job_id.encode("utf-8")).hexdigest() + ".lock"
    return OwnerFileLock(lock_root / lock_name)


def _register_import_records(
    catalog: ReportCatalog, *, job_id: str, source_raw: dict[str, bytes],
    run: dict[str, Any], result: dict[str, Any], ref: dict[str, Any],
    job: dict[str, Any], publication: dict[str, Any], report_id: str,
    verify_current: Callable[[], None],
) -> dict[str, Any]:
    """Stage and register one job while its job-ID lock is held."""
    refs, created_files = _catalog_artifacts(catalog, job_id, source_raw)
    attempt_id = job_id + ".succeeded"
    company = run["company"]
    attempt = {
        "run_id": job_id,
        "attempt_id": attempt_id,
        "status": "succeeded",
        "started_at": job.get("created_at"),
        "ended_at": job.get("updated_at"),
        "report_ids": [report_id],
        "error_code": None,
        "source_evidence": {
            "kind": "rf_job_record", "job_id": job_id, "artifacts": refs,
            "report_sha256": _sha(source_raw["report_markdown"]),
        },
    }
    years = result["forecast_years"]
    report = {
        "report_id": report_id,
        "run_id": job_id,
        "attempt_id": attempt_id,
        "company": company,
        "artifact_kind": "revenue_forecast",
        "artifact_revision": result["forecast_version"],
        "input_sha256": result["input_sha256"],
        "result_sha256": result["result_sha256"],
        "created_at": publication["registered_at"],
        "status": "validated",
        "schema_version": result["schema_version"],
        "engine_version": result["engine_version"],
        "information_as_of": result["as_of_date"],
        "forecast_horizon": f"{min(years)}-{max(years)}",
        "supersedes_report_id": None,
        "missing_reason": None,
        "reporting_currency": result["currency"],
        "reporting_scale": _frozen_reporting_scale(result),
        "forecast_artifact": refs["compute_result"],
        "input_artifact": refs["compute_input"],
        "markdown_artifact": refs["report_markdown"],
        "snapshot_artifact": None,
        "snapshot_id": None,
    }
    try:
        existing_runs, existing_attempts, existing_reports, _ = catalog._index()
        if job_id in existing_runs:
            existing_attempt = existing_attempts.get((job_id, attempt_id))
            existing_report = existing_reports.get(report_id)
            _need(existing_runs[job_id] == run and existing_attempt == attempt
                  and existing_report == report,
                  "rf_job_import_conflict", "this immutable job ID is already bound to different evidence")
            verify_current()
            catalog._validate_attempt_source(existing_attempt)
            catalog._validate_report_artifact(existing_report)
            return {
                "schema_version": IMPORT_SCHEMA,
                "status": "already_registered",
                "run_id": job_id,
                "attempt_id": attempt_id,
                "report_id": report_id,
                "catalog_revision": catalog._index()[3],
                "input_sha256": result["input_sha256"],
                "result_sha256": result["result_sha256"],
                "source_ref": ref,
                "forecast_executions": 0,
            }
        receipt = catalog.add_records(
            runs=[run], attempts=[attempt], reports=[report], before_append=verify_current,
        )
    except Exception:
        if created_files:
            _remove_created_files(
                created_files,
                (catalog.root / "artifacts" / "report_catalog" / "rf_job_imports" / job_id).resolve(),
                (catalog.root / "artifacts" / "report_catalog" / "rf_job_imports").resolve(),
            )
        raise
    return {
        "schema_version": IMPORT_SCHEMA,
        "status": "registered",
        "run_id": job_id,
        "attempt_id": attempt_id,
        "report_id": report_id,
        "catalog_revision": receipt["catalog_revision"],
        "input_sha256": result["input_sha256"],
        "result_sha256": result["result_sha256"],
        "source_ref": ref,
        "forecast_executions": 0,
    }


def import_rf_job(
    catalog: ReportCatalog,
    *,
    job_root: Path,
    job_id: str,
    expected_job_sha256: str,
    expected_report_sha256: str,
    entity_id: str,
    listing_id: str,
    source_export: Callable[[dict[str, Any]], dict[str, Any]],
    identity_resolver: Callable[[str, str], dict[str, Any]],
    issuer_proof: Callable[[dict[str, str]], dict[str, Any]],
) -> dict[str, Any]:
    """Admit one already-succeeded RF job, or return exact idempotent replay."""
    _need(isinstance(entity_id, str) and _ENTITY_ID.fullmatch(entity_id) is not None
          and isinstance(listing_id, str) and _LISTING_ID.fullmatch(listing_id) is not None,
          "identity_input_invalid", "entity and listing IDs must be owner UUIDs")
    job_dir, source_paths = _job_files(Path(job_root), job_id)
    _need(isinstance(expected_job_sha256, str) and _HEX64.fullmatch(expected_job_sha256) is not None,
          "rf_job_artifact_mismatch", "an independently recorded job SHA-256 is required")
    _need(_sha(source_paths["job"].read_bytes()) == expected_job_sha256,
          "rf_job_artifact_mismatch", "rf-job differs from its independently recorded SHA-256")
    job, source_raw, parsed = _read_job(
        source_paths, job_id, expected_report_sha256=expected_report_sha256,
    )
    input_document = parsed["input"]
    result = parsed["result"]
    source_result = parsed["source_result"]
    ref = parsed["source_ref"]
    source_bundle = source_export(ref)
    manifest = validate_source_export(source_bundle, ref)
    _validate_source_period(manifest, input_document=input_document, source_result=source_result)
    input_manifest = parsed["source_manifest"]
    for field in (
        "display_name", "document_kind", "fiscal_year", "fiscal_period", "form_type",
        "market", "security_id", "published_date", "period_end", "provider",
        "provider_document_id", "source_url",
    ):
        mismatch_code = "source_identity_mismatch" if field in {"display_name", "market", "security_id"} else "source_export_mismatch"
        _need(input_manifest.get(field) == manifest.get(field), mismatch_code,
              "fresh CWP SourceExport differs from the forecast's captured source scope")
    _need(input_manifest.get("source_id") == ref["source_id"],
          "source_export_mismatch", "captured source manifest is bound to another SourceRef")

    info_date = _text(input_document.get("as_of_date"), "rf_job_invalid")
    query = {
        "entity_id": entity_id,
        "listing_id": listing_id,
        "as_of": info_date + "T23:59:59Z",
    }
    identity = identity_resolver(entity_id, listing_id)
    proof = issuer_proof(query)
    composite = _validate_issuer_proof(
        identity, proof, entity_id=entity_id, listing_id=listing_id, query=query,
        manifest=manifest, company_name=result.get("company_name"),
    )
    composite["source_export_id"] = source_bundle["export_id"]
    composite["source_export_sha256"] = source_bundle["bundle_sha256"]

    company = {
        "entity_id": entity_id,
        "listing_id": listing_id,
        "analysis_subject_id": None,
        "resolution_status": "resolved",
        "display_name": result["company_name"],
    }
    scenario_set = sorted({
        scenario
        for segment in result.get("segments", []) if isinstance(segment, dict)
        for scenario in (segment.get("scenarios") or {})
    })
    _need(scenario_set, "rf_job_invalid", "forecast has no scenarios")
    forecast_years = result.get("forecast_years")
    _need(isinstance(forecast_years, list) and forecast_years
          and all(type(year) is int for year in forecast_years),
          "rf_job_invalid", "forecast horizon is invalid")
    run_id = job_id
    report_id = "rfjob-" + canonical_sha256({
        "job_id": job_id,
        "input_sha256": result["input_sha256"],
        "result_sha256": result["result_sha256"],
        "report_sha256": _sha(source_raw["report_markdown"]),
    })
    run = {
        "run_id": run_id,
        "parent_run_id": None,
        "company": company,
        "source_as_of": result["as_of_date"],
        "created_at": job["created_at"],
        "status": "complete",
        "scenario_set": scenario_set,
        "reporting_currency": result["currency"],
        "model_metadata": {"schema_version": result["schema_version"],
                           "engine_version": result["engine_version"]},
        "artifact_revision": result["forecast_version"],
        "source_snapshot_refs": [ref],
        "source_bound_identity_evidence": composite,
    }
    # Re-read both public owners immediately before first admission.
    def verify_current() -> None:
        current_bundle = source_export(ref)
        current_manifest = validate_source_export(current_bundle, ref)
        current_identity = identity_resolver(entity_id, listing_id)
        current_proof = issuer_proof(query)
        current = _validate_issuer_proof(
            current_identity, current_proof, entity_id=entity_id, listing_id=listing_id,
            query=query, manifest=current_manifest, company_name=result.get("company_name"),
        )
        current["source_export_id"] = current_bundle["export_id"]
        current["source_export_sha256"] = current_bundle["bundle_sha256"]
        _need(current_manifest == manifest and current == composite,
              "source_identity_changed", "owner source or issuer proof changed before admission")

    # The same job-ID lock covers staging, admission, replay and cleanup; the
    # catalog's own lock still serializes appends from different jobs.
    job_lock = _job_import_lock(catalog, job_id)
    if not job_lock.acquire():
        raise CatalogError("rf_job_import_busy", "the same rf-job import is already active")
    try:
        return _register_import_records(
            catalog, job_id=job_id, source_raw=source_raw, run=run, result=result,
            ref=ref, job=job, publication=parsed["publication"], report_id=report_id,
            verify_current=verify_current,
        )
    finally:
        job_lock.release()


@dataclass(frozen=True)
class CompanyWikiExportConfig:
    python: Path
    code_root: Path
    catalog_config: Path
    timeout_seconds: int
    max_output_bytes: int


@dataclass(frozen=True)
class JobImportDeployment:
    company_wiki: CompanyWikiExportConfig
    stockwiki_bridge_config: Path


def load_job_import_deployment(path: Path) -> JobImportDeployment:
    try:
        raw = path.read_bytes()
        _need(len(raw) <= MAX_DEPLOYMENT_CONFIG_BYTES,
              "deployment_config_invalid", "import deployment config is too large")
        data = _read_json_bytes(raw, "deployment_config_invalid")
    except OSError as exc:
        raise CatalogError("deployment_config_unavailable", "import deployment config is unavailable") from exc
    _need(data.get("schema_version") == DEPLOYMENT_SCHEMA
          and set(data) == {"schema_version", "company_wiki", "stockwiki_bridge_config"},
          "deployment_config_invalid", "import deployment config schema is unsupported")
    company = data.get("company_wiki")
    _need(isinstance(company, dict)
          and set(company) == {"python", "code_root", "catalog_config", "timeout_seconds", "max_output_bytes"},
          "deployment_config_invalid", "company-wiki deployment config is incomplete")
    def configured_path(value: Any, label: str, *, file: bool = False) -> Path:
        _need(isinstance(value, str) and value.strip() and Path(value).is_absolute()
              and "\x00" not in value,
              "deployment_config_invalid", f"{label} must be an absolute path")
        try:
            resolved = Path(value).resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as exc:
            raise CatalogError("deployment_config_invalid", f"{label} is unavailable") from exc
        _need(resolved.is_file() if file else resolved.is_dir(),
              "deployment_config_invalid", f"{label} has the wrong filesystem type")
        return resolved

    python = configured_path(company.get("python"), "company-wiki Python", file=True)
    _need(python.name.lower() in {"python.exe", "python", "python3.exe", "python3"},
          "deployment_config_invalid", "company-wiki interpreter is invalid")
    code_root = configured_path(company.get("code_root"), "company-wiki code root")
    source_export_cli = (code_root / "src" / "company_wiki" / "source_catalog"
                         / "source_export_v2_cli.py").resolve()
    _need(source_export_cli.is_file() and source_export_cli.is_relative_to(code_root),
          "deployment_config_invalid", "fixed CWP SourceExport v2 CLI is unavailable")
    catalog_config = configured_path(company.get("catalog_config"), "company-wiki catalog config", file=True)
    timeout = company.get("timeout_seconds")
    max_output = company.get("max_output_bytes")
    _need(type(timeout) is int and 1 <= timeout <= 120
          and type(max_output) is int and 4096 <= max_output <= MAX_SOURCE_EXPORT_BYTES,
          "deployment_config_invalid", "company-wiki process bounds are invalid")
    stockwiki_config = configured_path(
        data.get("stockwiki_bridge_config"), "StockWiki bridge config", file=True,
    )
    return JobImportDeployment(
        company_wiki=CompanyWikiExportConfig(
            python=python, code_root=code_root, catalog_config=catalog_config,
            timeout_seconds=timeout, max_output_bytes=max_output,
        ),
        stockwiki_bridge_config=stockwiki_config,
    )


def make_source_export_runner(config: CompanyWikiExportConfig) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def source_export(source_ref: dict[str, Any]) -> dict[str, Any]:
        request = {
            "schema_version": "2.0",
            "source_refs": [source_ref],
            "evidence_spans": [],
        }
        payload = json.dumps(request, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
        cli_module = "company_wiki.source_catalog.source_export_v2_cli"
        argv = [str(config.python), "-X", "utf8", "-B", "-m", cli_module,
                "--config", str(config.catalog_config)]
        env = dict(os.environ)
        source_path = str(config.code_root / "src")
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = source_path if not existing else source_path + os.pathsep + existing
        try:
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                completed = subprocess.run(
                    argv, input=payload, stdout=stdout, stderr=stderr,
                    timeout=config.timeout_seconds, cwd=config.code_root, env=env,
                )
                _need(completed.returncode == 0, "source_export_unavailable",
                      "company-wiki SourceExport v2 refused the source")
                stdout.seek(0)
                raw = stdout.read(config.max_output_bytes + 1)
        except subprocess.TimeoutExpired as exc:
            raise CatalogError("source_export_timeout", "company-wiki SourceExport deadline expired") from exc
        except OSError as exc:
            raise CatalogError("source_export_unavailable", "company-wiki SourceExport could not start") from exc
        _need(len(raw) <= config.max_output_bytes,
              "source_export_unavailable", "company-wiki SourceExport exceeded its response budget")
        return _read_json_bytes(raw, "source_export_invalid")

    return source_export


def make_stockwiki_resolvers(deployment: JobImportDeployment):
    from report_catalog_identity_resolver import load_bridge_config, resolve_identity_record
    from report_catalog_source_alias import read_issuer_proof

    bridge = load_bridge_config(deployment.stockwiki_bridge_config)
    def identity(entity_id: str, listing_id: str) -> dict[str, Any]:
        return resolve_identity_record(entity_id, config=bridge, listing_id=listing_id)
    def proof(query: dict[str, str]) -> dict[str, Any]:
        return read_issuer_proof(bridge, query)
    return identity, proof


__all__ = [
    "CompanyWikiExportConfig", "DEPLOYMENT_SCHEMA", "IMPORT_SCHEMA", "JobImportDeployment",
    "import_rf_job", "load_job_import_deployment", "make_source_export_runner",
    "make_stockwiki_resolvers", "validate_source_export",
]
