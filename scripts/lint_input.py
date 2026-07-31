"""Collect-all static pre-flight linter for schema 3.5 inputs.

Unlike the engine's own validators (which fail fast on the first violation),
this linter accumulates **every** structural / reference / hash / aggregate
finding it can detect without running the forecast, so an author can fix several
problems per round-trip. It is a pre-flight only — the engine remains
authoritative for semantic checks this linter does not replicate.

Hash checks reuse ``fix_hashes.find_hash_drift`` (which itself reuses the
engine's ``canonical_sha256`` / ``text_sha256``), guaranteeing byte-for-byte
agreement with the engine.

CLI mirrors ``revenue_forecast.py``: positional input path, exit 0 when clean /
exit 2 when any finding is reported.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import fix_hashes

TOP_LEVEL_REQUIRED = (
    "schema_version", "company_name", "as_of_date", "currency", "unit",
    "fiscal_year_end", "base_year", "forecast_years", "sources", "parameters",
    "segments", "reported_total_revenue_parameter_id", "historical_revenue",
    "research_coverage",
)
CAPTURE_REQUIRED = (
    "capture_schema_version", "capture_method", "tool_name", "tool_call_id",
    "captured_date", "snapshot_sha256", "content_treatment",
    "prompt_injection_status", "receipt_sha256",
)
CLAIM_REQUIRED = (
    "claim_id", "source_id", "target_type", "target_id", "support_type",
    "locator", "excerpt", "excerpt_sha256", "content_sha256",
    "capture_receipt_sha256", "verification_status",
)
PARAMETER_REQUIRED = (
    "parameter_id", "kind", "value", "unit", "period", "definition", "source_ids",
)


def _finding(category: str, path: str, message: str) -> dict[str, str]:
    return {"category": category, "path": path, "message": message}


def _check_top_level(data: dict[str, Any]) -> list[dict[str, str]]:
    return [
        _finding("top_level_shape", key, f"missing required top-level field: {key}")
        for key in TOP_LEVEL_REQUIRED
        if key not in data
    ]


def _check_capture_shape(data: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for source in data.get("sources", []):
        if not isinstance(source, dict):
            continue
        sid = source.get("source_id", "<unknown>")
        capture = source.get("capture")
        if not isinstance(capture, dict):
            findings.append(_finding("capture_shape", f"sources.{sid}.capture", f"source {sid} is missing a capture object"))
            continue
        if set(capture) != set(CAPTURE_REQUIRED):
            findings.append(_finding(
                "capture_shape", f"sources.{sid}.capture",
                f"source {sid} capture must have exactly the required fields; "
                f"missing={sorted(set(CAPTURE_REQUIRED) - set(capture))} "
                f"unexpected={sorted(set(capture) - set(CAPTURE_REQUIRED))}",
            ))
    return findings


def _check_claim_shape(claims: list[Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        cid = claim.get("claim_id", "<unknown>")
        for key in CLAIM_REQUIRED:
            if key not in claim:
                findings.append(_finding("claim_shape", f"evidence_claims.{cid}", f"claim {cid} is missing required field: {key}"))
    return findings


def _check_parameter_shape(parameters: list[Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for parameter in parameters:
        if not isinstance(parameter, dict):
            continue
        pid = parameter.get("parameter_id", "<unknown>")
        for key in PARAMETER_REQUIRED:
            if key not in parameter:
                findings.append(_finding("parameter_shape", f"parameters.{pid}", f"parameter {pid} is missing required field: {key}"))
    return findings


def _check_references(
    data: dict[str, Any],
    source_ids: set[str],
    claim_index: dict[str, dict[str, Any]],
    parameter_index: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for parameter in data.get("parameters", []):
        if not isinstance(parameter, dict):
            continue
        pid = parameter.get("parameter_id", "<unknown>")
        for sid in parameter.get("source_ids", []):
            if sid not in source_ids:
                findings.append(_finding("reference", f"parameters.{pid}.source_ids", f"parameter {pid} references unknown source {sid}"))
        for cid in parameter.get("claim_ids", []):
            if cid not in claim_index:
                findings.append(_finding("reference", f"parameters.{pid}.claim_ids", f"parameter {pid} references unknown claim {cid}"))
            else:
                claim = claim_index[cid]
                if claim.get("target_type") != "parameter" or claim.get("target_id") != pid:
                    findings.append(_finding("reference", f"parameters.{pid}.claim_ids", f"claim {cid} does not support parameter {pid}"))
    for record in data.get("historical_revenue", []):
        if not isinstance(record, dict):
            continue
        year = record.get("year")
        for cid in record.get("claim_ids", []):
            if cid not in claim_index:
                findings.append(_finding("reference", f"historical_revenue.{year}.claim_ids", f"historical revenue {year} references unknown claim {cid}"))
            elif claim_index[cid].get("target_id") != f"historical_revenue:{year}":
                findings.append(_finding("reference", f"historical_revenue.{year}.claim_ids", f"claim {cid} does not support historical_revenue:{year}"))
    for pid in data.get("base_adjustment_parameter_ids", []):
        if pid not in parameter_index:
            findings.append(_finding("reference", "base_adjustment_parameter_ids", f"unknown base adjustment parameter {pid}"))
    return findings


def _check_hashes(data: dict[str, Any]) -> list[dict[str, str]]:
    return [
        _finding("hash", entry["path"], f"{entry['kind']} hash drift: expected {entry['expected']}")
        for entry in fix_hashes.find_hash_drift(data)
    ]


def _check_aggregates(data: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    tree = data.get("growth_driver_tree")
    if isinstance(tree, dict):
        weights: dict[Any, float] = {}
        for driver in tree.get("drivers", []):
            if not isinstance(driver, dict):
                continue
            for attr in driver.get("segment_attribution", []):
                if not isinstance(attr, dict):
                    continue
                name = attr.get("segment_name")
                weight = attr.get("weight")
                if isinstance(weight, (int, float)) and not isinstance(weight, bool):
                    weights[name] = weights.get(name, 0.0) + weight
        for name, total in weights.items():
            if abs(total - 1.0) > 1e-9:
                findings.append(_finding("aggregate", f"growth_driver_tree.{name}", f"attribution weights for segment {name} sum to {total}, expected 1.0"))
    coverage = data.get("research_coverage")
    if isinstance(coverage, list):
        dims = [record.get("dimension") for record in coverage if isinstance(record, dict)]
        if len(dims) < 9:
            findings.append(_finding("aggregate", "research_coverage", f"research_coverage has {len(dims)} dimensions, expected at least 9"))
        if len(dims) != len(set(dims)):
            findings.append(_finding("aggregate", "research_coverage", "research_coverage has duplicate dimension names"))
    return findings


def lint(data: dict[str, Any]) -> list[dict[str, str]]:
    """Return all detectable pre-flight findings; never raises."""
    if not isinstance(data, dict):
        return [_finding("top_level_shape", "", "input document must be a JSON object")]
    source_ids = {
        source.get("source_id")
        for source in data.get("sources", [])
        if isinstance(source, dict)
    }
    claims = data.get("evidence_claims", [])
    claim_index = {
        claim.get("claim_id"): claim
        for claim in claims
        if isinstance(claim, dict)
    }
    parameters = data.get("parameters", [])
    parameter_index = {
        parameter.get("parameter_id"): parameter
        for parameter in parameters
        if isinstance(parameter, dict)
    }
    findings: list[dict[str, str]] = []
    findings += _check_top_level(data)
    findings += _check_capture_shape(data)
    findings += _check_claim_shape(claims)
    findings += _check_parameter_shape(parameters)
    findings += _check_references(data, source_ids, claim_index, parameter_index)
    findings += _check_hashes(data)
    findings += _check_aggregates(data)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", type=Path, help="schema 3.5 input JSON path")
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    findings = lint(data)
    if not findings:
        print("ok: no findings")
        return 0
    for finding in findings:
        print(f"[{finding['category']}] {finding['path']}: {finding['message']}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
