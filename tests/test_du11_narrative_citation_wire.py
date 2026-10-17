"""Synthetic DU11 citation-closure wire, built from the frozen local descriptor.

The descriptor is RF-owned synthetic material (no company original bytes). This
module only builds the published ``narrative-bundle``/``narrative-read`` wire so
the consumer tests can exercise the real validator and the real consumption
entries; it never bypasses ``validate_narrative_response``.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from company_wiki_narrative_contracts import (  # noqa: E402
    SPAN_PREFIX,
    canonical_bytes,
    validate_narrative_response,
)

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "du11_narrative_citation"
    / "synthetic_reading2.json"
)
SHA_POLICY = "a" * 64


def descriptor() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _sha(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _text_sha(value: str) -> str:
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()


def _locator(coordinates: dict) -> str:
    parts = ["loc:v1"]
    for label, key in (
        ("page", "page_number"),
        ("paragraph", "paragraph_index"),
        ("table", "table_index"),
        ("row", "row_index"),
        ("column", "column_index"),
    ):
        if coordinates[key] is not None:
            parts.append(f"{label}:{coordinates[key]}")
    parts.append(f"chars:{coordinates['char_start']}-{coordinates['char_end']}")
    return "/".join(parts)


def _span(source_id: str, raw_text: str, coordinates: dict, structured: dict) -> dict:
    locator = _locator(coordinates)
    output_sha256 = _sha({"raw_text": raw_text, "structured_value": structured})
    span_sha = _sha(
        {"source_id": source_id, "locator": locator, "output_sha256": output_sha256}
    )
    return {
        "schema_version": "1.0.0",
        "span_id": SPAN_PREFIX + span_sha,
        "source_id": source_id,
        "locator": locator,
        "coordinates": coordinates,
        "raw_text": raw_text,
        "structured_value": structured,
        "parser_name": "du11-fixture-parser",
        "parser_version": "1.0.0",
        "output_sha256": output_sha256,
        "parse_status": "parsed",
        "quality_flags": [],
    }


def _coordinates(spec: dict, start: int, end: int) -> dict:
    return {
        "page_number": None,
        "paragraph_index": spec.get("paragraph"),
        "table_index": spec.get("table"),
        "row_index": spec.get("row"),
        "column_index": spec.get("column"),
        "char_start": start,
        "char_end": end,
    }


def _reading_context(data: dict, spans: dict[str, dict], *, schema: str, views: bool,
                     sampling: bool) -> dict:
    groups = []
    for group in data["groups"]:
        entry = {
            "group_id": group["group_id"],
            "kind": group["kind"],
            "section_role": group["section_role"],
            "evidence_ids": [spans[key]["span_id"] for key in group["members"]],
        }
        if views:
            entry["citation_views"] = [
                {
                    "support_evidence_ids": [spans[key]["span_id"] for key in view["support"]],
                    "context_evidence_ids": [spans[key]["span_id"] for key in view["context"]],
                }
                for view in group["views"]
            ]
        groups.append(entry)
    reading = data["reading"]
    unread = deepcopy(reading["unread"])
    context = {
        "schema_version": schema,
        "reading_policy_version": "du-sent-policy/1+" + reading["policy_version_seed"],
        "reading_policies": [],
        "business_facets": [],
        "constraints": [],
        "groups": groups,
        "unread": unread,
        "deferred": deepcopy(reading["deferred"]),
        "layout_coverage": deepcopy(reading["layout_coverage"]),
    }
    if sampling:
        context["deferred_count"] = reading["deferred_count"]
        context["deferred_limited"] = reading["deferred_limited"]
        context["selection_diagnostics"] = deepcopy(reading["selection_diagnostics"])
    else:
        for key in ("counts", "limited"):
            unread.pop(key)
    return context


def draft(desc: dict | None = None, *, reading: str | None = "2") -> dict:
    """Build the unsigned parts of one legal public narrative read.

    ``reading``: ``"2"`` keeps ``du-production-reading/2`` with citation views,
    ``"1"`` keeps the older ``du-production-reading/1`` group shape, ``None``
    publishes no reading context at all (the legacy single-span path).
    """
    data = descriptor() if desc is None else desc
    lines = data["lines"]
    text = "\n".join(lines)
    content = text.encode("utf-8")
    content_sha256 = hashlib.sha256(content).hexdigest()
    source_ref = {
        "schema_version": "2.0",
        "document_id": f"urn:company-wiki:document:sha256:{content_sha256}",
        "source_id": f"urn:company-wiki:source:sha256:{content_sha256}",
        "content_sha256": content_sha256,
        "byte_size": len(content),
        "mime_type": "text/plain",
    }
    offsets = {}
    cursor = 0
    for number, line in enumerate(lines, start=1):
        offsets[number] = cursor
        cursor += len(line) + 1
    spans: dict[str, dict] = {}
    by_line: dict[int, dict] = {}
    for spec in data["spans"]:
        line = spec["line"]
        raw_text = lines[line - 1]
        start = offsets[line]
        structured = {
            "language": "en",
            "section": spec["section"],
            "source_role": spec["role"],
            "unit_kind": spec["unit_kind"],
            "text_sha256": _text_sha(raw_text),
        }
        span = _span(
            source_ref["source_id"], raw_text,
            _coordinates(spec, start, start + len(raw_text)), structured,
        )
        spans[spec["key"]] = span
        by_line[line] = span
    claims = []
    for index, claim in enumerate(data["summary_claims"]):
        entry = {
            "claim_id": f"claim-replay-{index:03d}",
            "text": claim["text"],
            "evidence_ids": [spans[claim["span"]]["span_id"]],
            "claim_type": claim["claim_type"],
            "modality": claim["modality"],
            "needs_review": False,
        }
        if claim["context"]:
            entry["context_evidence_ids"] = [
                spans[key]["span_id"] for key in claim["context"]
            ]
        claims.append(entry)
    bindings = []
    for number, span in sorted(by_line.items()):
        raw_bytes = lines[number - 1].encode("utf-8")
        start = offsets[number]
        bindings.append({
            "evidence_id": span["span_id"],
            "material_line_start": number,
            "material_line_end": number,
            "source_byte_ranges": [{"start": start, "end": start + len(raw_bytes)}],
        })
    bundle = {
        "schema_version": "narrative-bundle/2.0",
        "source_ref": source_ref,
        "expected_read_policy_sha256": SHA_POLICY,
        "source_metadata": {
            "source_class": data["source_class"],
            "title": "ACME business update",
            "document_kind": data["document_kind"],
            "language": "en",
        },
        "quality_status": "verified",
        "selection": {
            "status": "selected",
            "coverage_complete": True,
            "source_units": len(spans),
            "candidate_count": len(spans),
            "selected_count": len(spans),
            "omitted_candidate_count": 0,
            "dropped_financial_count": 0,
            "pages_total": 0,
            "pages_read": 0,
            "lines_total": len(lines),
            "tables_total": 1,
            "tables_scanned": 1,
        },
        "evidence_spans": [spans[spec["key"]] for spec in data["spans"]],
        "summary": {
            "status": "completed",
            "translate": False,
            "draft": {
                "source_id": source_ref["source_id"],
                "source_sha256": content_sha256,
                "language": "en",
                "claims": claims,
                "status": "draft",
            },
            "model": {
                "adapter_id": "fixture-adapter",
                "model_id": "fixture-model",
                "prompt_version": "fixture-prompt-1",
                "response_sha256": "c" * 64,
            },
        },
        "prompt_review": {
            "status": "not_detected",
            "source_sha256": content_sha256,
            "evidence_sha256": None,
            "policy_hash": None,
            "reviewed_at": None,
        },
        "transcript_lineage": {
            "schema_version": "transcript-material/2",
            "original_source_id": source_ref["source_id"],
            "original_sha256": content_sha256,
            "original_byte_size": len(content),
            "original_mime_type": "text/plain",
            "text_sha256": content_sha256,
            "text_byte_size": len(content),
            "line_count": len(lines),
            "extractor_version": "du11-fixture-transcript/1.0.0",
        },
        "transcript_byte_bindings": bindings,
        "versions": {
            "parser": "du11-fixture-parser-1",
            "selector": "du11-fixture-selector-1",
            "material": "du11-fixture-material-1",
            "model": "fixture-model",
            "prompt": "fixture-prompt-1",
            "bundle_producer": "du11-fixture-producer-1",
        },
        "replay": {"required": True, "locator_count": len(spans)},
    }
    if reading is not None:
        bundle["reading_context"] = _reading_context(
            data, spans,
            schema="du-production-reading/2" if reading == "2" else "du-production-reading/1",
            views=reading == "2", sampling=True,
        )
    manifest = {
        "document_id": source_ref["document_id"],
        "source_id": source_ref["source_id"],
        "content_sha256": content_sha256,
        "byte_size": len(content),
        "mime_type": "text/plain",
        "title": "ACME business update",
        "document_kind": data["document_kind"],
        "published_date": data["published_date"],
        "source_url": "https://fixtures.invalid/sources/acme-call.txt",
        "retrieved_at": data["read_at"],
        "collector_name": "du11-fixture-collector",
        "collector_version": "1.0.0",
        "canonical_entity_id": "US_ACME",
        "display_name": "ACME",
        "market": "US",
        "security_id": "ACME",
        "fiscal_year": 2026,
        "fiscal_period": "Q2",
        "period_end": "2026-06-30",
        "form_type": "transcript",
        "provider": "fixture-provider",
        "provider_document_id": "fixture-doc-1",
        "language": "en",
    }
    narrative_ref = {
        "schema_version": "narrative-ref/1",
        "artifact_version_id": "du11-fixture-narrative-v1",
        "artifact_sha256": "0" * 64,
        "byte_size": 1,
        "source_ref": source_ref,
    }
    receipt = {
        "schema_version": "narrative-read-receipt/1",
        "status": "ok",
        "narrative_ref": narrative_ref,
        "as_of_date": data["as_of_date"],
        "manifest": manifest,
        "source_read_policy_sha256": SHA_POLICY,
        "read_at": data["read_at"],
        "locator_count": len(spans),
        "selection_status": "selected",
        "quality_status": "verified",
        "replay_status": "verified",
    }
    request = {
        "schema_version": "narrative-read-request/1",
        "narrative_ref": narrative_ref,
        "as_of_date": data["as_of_date"],
        "expected_source": {
            "canonical_entity_id": "US_ACME",
            "market": "US",
            "security_id": "ACME",
            "document_kind": data["document_kind"],
            "fiscal_year": 2026,
            "fiscal_period": "Q2",
        },
    }
    return {"request": request, "bundle": bundle, "receipt": receipt, "spans": spans}


def finalize(parts: dict) -> tuple[dict, bytes, bytes]:
    """Canonicalise the artifact and re-sign the receipt echoes for one wire."""
    request = deepcopy(parts["request"])
    receipt = deepcopy(parts["receipt"])
    body = canonical_bytes(parts["bundle"])
    ref = request["narrative_ref"]
    ref["artifact_sha256"] = hashlib.sha256(body).hexdigest()
    ref["byte_size"] = len(body)
    receipt["narrative_ref"] = deepcopy(ref)
    receipt["locator_count"] = len(parts["bundle"]["evidence_spans"])
    receipt["selection_status"] = parts["bundle"]["selection"]["status"]
    receipt["quality_status"] = parts["bundle"]["quality_status"]
    return request, body, canonical_bytes(receipt) + b"\n"


def resign(request: dict, bundle: dict, receipt: dict) -> tuple[dict, bytes, bytes]:
    return finalize({"request": request, "bundle": bundle, "receipt": receipt})


def wire(reading: str | None = "2", desc: dict | None = None) -> tuple[dict, bytes, bytes]:
    return finalize(draft(desc, reading=reading))


def validated(reading: str | None = "2", desc: dict | None = None):
    request, body, receipt = wire(reading, desc)
    return validate_narrative_response(request, body, receipt)


def span_id(context: dict, key: str, desc: dict | None = None) -> str:
    """Resolve a descriptor span key to the transported span id of that wire."""
    data = descriptor() if desc is None else desc
    index = [spec["key"] for spec in data["spans"]].index(key)
    return context["evidence_spans"][index]["span_id"]


def span(context: dict, key: str, desc: dict | None = None) -> dict:
    data = descriptor() if desc is None else desc
    index = [spec["key"] for spec in data["spans"]].index(key)
    return context["evidence_spans"][index]
