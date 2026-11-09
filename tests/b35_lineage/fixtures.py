"""Controlled owner-only projection fixtures. No real company data or acquisition."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from report_catalog import ReportCatalog  # noqa: E402
from publication_registry import canonical_sha256  # noqa: E402


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write(path: Path, value) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (
        value
        if isinstance(value, bytes)
        else (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    path.write_bytes(raw)
    return raw


class ControlledCatalog(ReportCatalog):
    """Bypasses native publication validation only for isolated projection units."""

    def _exact_report(self, report_id):
        from report_catalog import CatalogError

        if report_id != self.record["report_id"]:
            raise CatalogError("not_found", "report absent")
        self.strong_reads += 1
        return self.record, self.result, "a" * 64

    def _index(self):
        return {self.run["run_id"]: self.run}, {}, {}, "a" * 64


def build(tmp_path: Path, body: bytes | None = None):
    c = ControlledCatalog(root=tmp_path)
    c.strong_reads = 0
    rid = "rf-controlled"
    run_id = "controlled-run"
    folder = tmp_path / "delivery" / run_id
    body = (
        body
        if body is not None
        else b"# Controlled release\nAnnual revenue RMB 10 million.\n<script>never execute this captured source</script>\n"
    )
    url = "https://example.com/release"
    request = {"urls": [url], "query_omitted": True, "format": "markdown"}
    response = {
        "request_id": "controlled-request",
        "results": [
            {"url": url, "title": "Controlled release", "raw_content": body.decode()}
        ],
        "failed_results": [],
    }
    transport = json.dumps(response, ensure_ascii=False).encode()
    event = {
        "tool": "controlled-extractor",
        "request_id": "controlled-request",
        "request": request,
        "response_artifact_sha256": sha(transport),
        "retrieved_markdown_sha256": sha(body),
        "recorded_at": "2026-11-01T00:00:00Z",
        "raw_artifact_kind": "tool-returned complete markdown; not raw HTML",
    }
    web = {
        "source_id": "WEB",
        "source_type": "company_release",
        "title": "Controlled release",
        "publisher": "Controlled publisher",
        "url": url,
        "published_date": "2026-10-30",
        "accessed_date": "2026-11-01",
        "capture": {
            "snapshot_sha256": sha(body),
            "receipt_sha256": "c" * 64,
            "tool_call_id": "controlled-request",
            "tool_name": "controlled-extractor",
            "host_receipt": {"event_sha256": canonical_sha256(event)},
        },
    }
    ref = {
        "schema_version": "2.0",
        "document_id": "urn:document:controlled",
        "source_id": "PDF",
        "content_sha256": "b" * 64,
        "byte_size": 1234,
        "mime_type": "application/pdf",
    }
    pdf = {
        "source_id": "PDF",
        "source_type": "regulatory_filing",
        "title": "Controlled filing",
        "publisher": "Controlled publisher",
        "url": None,
        "published_date": None,
        "accessed_date": "2026-11-01",
        "capture": {"snapshot_sha256": "b" * 64, "receipt_sha256": "d" * 64},
        "company_wiki_trace": {"source_ref": ref},
    }

    def param(pid, value, kind, source, claim):
        return {
            "parameter_id": pid,
            "value": value,
            "kind": kind,
            "unit": "CNY million",
            "currency": "CNY",
            "scale": "million",
            "period": "FY2026",
            "scenario": "all" if kind == "reported_fact" else "base",
            "time_basis": "annual",
            "dimension": "revenue",
            "definition": pid,
            "source_ids": source,
            "claim_ids": claim,
            "rationale": None
            if kind == "reported_fact"
            else "Explicit conditional reference, not reported revenue",
        }

    p1 = param("observed", 10, "reported_fact", ["WEB"], ["observed-claim"])
    p2 = param("assumed", 2, "analyst_assumption", ["PDF"], ["assumption-claim"])
    p3 = param("composed", 12, "derived_fact", [], [])
    p3.update(formula="x0+x1", input_parameter_ids=["observed", "assumed"])
    unused = param("unused", 999, "reported_fact", ["WEB"], ["unused-claim"])

    def claim(cid, pid, sid, excerpt, support):
        return {
            "claim_id": cid,
            "target_type": "parameter",
            "target_id": pid,
            "source_id": sid,
            "support_type": support,
            "locator": "PDF physical8 quarterly reference"
            if sid == "PDF"
            else "Annual highlights",
            "excerpt": excerpt,
            "excerpt_sha256": sha(excerpt.encode()),
            "content_sha256": web["capture"]["snapshot_sha256"]
            if sid == "WEB"
            else "b" * 64,
            "capture_receipt_sha256": "c" * 64 if sid == "WEB" else "d" * 64,
            "verification_status": "opened_and_checked",
            "verified_date": "2026-11-01",
        }

    claims = [
        claim(
            "observed-claim",
            "observed",
            "WEB",
            "Annual revenue RMB 10 million.",
            "exact_value",
        ),
        claim(
            "assumption-claim",
            "assumed",
            "PDF",
            "Historical quarter reference only",
            "rationale_support",
        ),
        claim(
            "unused-claim",
            "unused",
            "WEB",
            "Annual revenue RMB 10 million.",
            "exact_value",
        ),
    ]
    claims[0].update(
        extracted_value=10,
        unit="CNY million",
        period="FY2026",
        evidence_role="history_base",
    )
    data = {"sources": [web, pdf], "parameters": [p1, p2, p3, unused]}
    company = {
        "entity_id": "ENT-controlled",
        "listing_id": "LST-controlled",
        "analysis_subject_id": None,
        "resolution_status": "resolved",
        "display_name": "Controlled",
    }
    c.record = {
        "report_id": rid,
        "run_id": run_id,
        "company": company,
        "information_as_of": "2026-11-01",
        "input_sha256": canonical_sha256(data),
        "result_sha256": "e" * 64,
        "reporting_currency": "CNY",
        "reporting_scale": 6,
        "status": "validated",
    }
    c.result = {
        "input_document": copy.deepcopy(data),
        "sources": [{**web, "source_rank": 2}, {**pdf, "source_rank": 1}],
        "parameter_trace": copy.deepcopy(data["parameters"]),
        "evidence_claims": claims,
        "forecast_years": [2026],
        "base_year": 2025,
        "segments": [
            {
                "name": "Controlled segment",
                "base_revenue": 5,
                "scenarios": {
                    "base": {
                        "model": "direct_revenue",
                        "formula": "revenue[t] = direct_revenue[t]",
                        "driver_values": {"revenue": {"2026": 12}},
                        "driver_parameter_ids": {"revenue": ["composed"]},
                        "modeled_activity": {"2026": 12},
                        "effective_revenue": {"2026": 12},
                    }
                },
            }
        ],
        "consolidated_forecast": {
            "base": {
                "annual_revenue": {"2026": 12},
                "segment_bridge": [
                    {"name": "Controlled segment", "annual_revenue": {"2026": 12}}
                ],
                "adjustment_bridge": [],
            }
        },
    }
    source_files = {
        "execution/web-capture-q3-2026/source.markdown": body,
        "execution/web-capture-q3-2026/tool-response.json": transport,
        "execution/web-capture-q3-2026/acquisition-observation.json": {
            "tool": "controlled-extractor",
            "request_id": "controlled-request",
            "request": request,
        },
        "execution/company-release-capture-event.json": event,
        "execution/company-release-q3-2026-source.json": web,
    }
    rows = []
    for rel, value in source_files.items():
        raw = write(folder / rel, value)
        rows.append(
            {
                "artifact": "delivery/" + run_id + "/" + rel,
                "bytes": len(raw),
                "sha256": sha(raw),
            }
        )
    registry = write(folder / "registry/publications.jsonl", b"old registry prefix\n")
    rows.append(
        {
            "artifact": "delivery/" + run_id + "/registry/publications.jsonl",
            "bytes": len(registry),
            "sha256": sha(registry),
        }
    )
    seal = {
        "schema_version": "rf-research-publication-admission/1",
        "report_id": rid,
        "run_id": run_id,
        "company": {
            k: company[k] for k in ("entity_id", "listing_id", "analysis_subject_id")
        },
        "input_observations": rows,
        "source_recovery": {
            "source_id": "WEB",
            "snapshot_sha256": sha(body),
            "transport_sha256": sha(transport),
            "capture_event_sha256": canonical_sha256(event),
            "source_record_sha256": canonical_sha256(web),
        },
    }
    seal_path = tmp_path / "artifacts/report_catalog/evidence/controlled.json"
    sealed = write(seal_path, seal)
    c.run = {
        "run_id": run_id,
        "artifact_revision": sha(sealed),
        "source_evidence": c.artifact_ref(seal_path),
    }
    c.folder, c.body, c.seal_path = folder, body, seal_path
    return c
