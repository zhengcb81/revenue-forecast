"""Verify already-admitted RF job evidence using the catalog's read port."""

import hashlib
import json
import re
from typing import Any, Callable

from publication_registry import canonical_sha256, validate_registry_text
from report_catalog_common import CatalogError, require
from rf_job_artifacts import RETAINED_ARTIFACTS


_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_artifact_object(raw: bytes, code: str = "rf_job_artifact_invalid") -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, code, "JSON contains duplicate keys")
            result[key] = value
        return result

    def constant(_: str) -> None:
        raise CatalogError(code, "JSON contains a non-finite number")

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise CatalogError(code, "JSON artifact is invalid") from exc
    require(isinstance(value, dict), code, "JSON artifact must contain an object")
    return value


def validate_retained_attempt(
    attempt: dict[str, Any], read_artifact: Callable[[dict[str, Any]], bytes],
) -> None:
    evidence = attempt.get("source_evidence")
    require(isinstance(evidence, dict) and evidence.get("kind") == "rf_job_record",
          "attempt_unverified", "attempt lacks rf-job evidence")
    require(set(evidence) == {"kind", "job_id", "artifacts", "report_sha256"}
          and isinstance(evidence.get("artifacts"), dict)
          and set(evidence["artifacts"]) == set(RETAINED_ARTIFACTS),
          "attempt_unverified", "rf-job evidence artifact set is incomplete")
    require(evidence.get("job_id") == attempt.get("run_id"),
          "attempt_unverified", "rf-job evidence ID differs from the registered run")
    raw: dict[str, bytes] = {}
    for key, ref in evidence["artifacts"].items():
        require(isinstance(ref, dict), "attempt_unverified", "rf-job artifact reference is invalid")
        raw[key] = read_artifact(ref)
    job = read_artifact_object(raw["job"])
    require(job.get("owner_job_id") == evidence["job_id"]
          and job.get("status") == "succeeded" and job.get("status_known") is True,
          "attempt_unverified", "retained rf-job no longer proves success")
    input_document = read_artifact_object(raw["compute_input"])
    result = read_artifact_object(raw["compute_result"])
    require(canonical_sha256(input_document) == result.get("input_sha256")
          and result.get("result_sha256") == canonical_sha256(
              {key: value for key, value in result.items() if key != "result_sha256"}
          ), "attempt_unverified", "retained rf-job input/result hashes do not verify")
    stage_artifacts = job.get("result", {}).get("stage_artifacts", {})
    for stage, raw_key in (("source", "source_result"), ("compute", "compute_result"),
                           ("publication", "publication_audit")):
        record = stage_artifacts.get(stage, {})
        stage_state = job.get("stages", {}).get(stage, {})
        require(record.get("sha256") == _sha256(raw[raw_key])
              and stage_state.get("status") == "completed"
              and any(isinstance(item, dict) and item.get("exit_code") == 0
                      and item.get("result_sha256") == _sha256(raw[raw_key])
                      for item in stage_state.get("attempts", [])),
              "attempt_unverified", "retained rf-job stage evidence is inconsistent")
    registry = validate_registry_text(raw["publication_registry"].decode("utf-8"))
    require(any(item.get("artifact_type") == "forecast"
              and item.get("input_sha256") == result.get("input_sha256")
              and item.get("result_sha256") == result.get("result_sha256")
              and item.get("validation_status") == "validated" for item in registry),
          "attempt_unverified", "retained publication record does not bind this forecast")
    require(isinstance(evidence.get("report_sha256"), str)
          and _HEX64.fullmatch(evidence["report_sha256"]) is not None
          and _sha256(raw["report_markdown"]) == evidence["report_sha256"],
          "attempt_unverified", "retained report differs from its admitted SHA-256")
    source_result = read_artifact_object(raw["source_result"])
    ff = source_result.get("filing_fetch", {})
    filing = ff.get("filing", {}) if isinstance(ff, dict) else {}
    require(source_result.get("schema_version") == "source-preparation-result/1"
          and isinstance(ff, dict) and ff.get("status") == "source_candidate"
          and isinstance(filing, dict) and filing.get("download_events") == 0
          and filing.get("resolution_outcome") == "reused_existing",
          "attempt_unverified", "retained job did not use the existing source")
