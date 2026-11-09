"""Read-only, report-bound numeric lineage and captured-source projections.

No collection, registration, source repair or forecast calculation lives here.
The catalog first performs its existing strong immutable publication checks.
"""

from __future__ import annotations

import base64
import copy
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
from typing import Any
from urllib.parse import urlsplit

from publication_registry import canonical_sha256
from report_catalog import CatalogError, SOURCE_REF_FIELDS, _assert_pathless
from report_catalog_research_attempt import _Observation, _not_linked, _json

TRACE_SCHEMA = "rf-calculation-trace/1"
SNAPSHOT_SCHEMA = "rf-source-snapshot/1"
SHA = re.compile(r"^[a-f0-9]{64}$")
TOKEN = re.compile(r"^rfsnap1-[a-f0-9]{64}$")
MAX_BODY = 262144
MAX_TRACE_BYTES = 240000
MAX_DEPTH = 32
LIMITS = {
    "nodes": 128,
    "bindings": 512,
    "parameters": 128,
    "claims": 256,
    "sources": 64,
}


def need(value: Any, message: str, code: str = "lineage_evidence_mismatch") -> None:
    if not value:
        raise CatalogError(code, message)


def decimal(value: Any) -> str:
    need(
        not isinstance(value, bool) and isinstance(value, (int, float)),
        "lineage amount is not numeric",
    )
    try:
        number = Decimal(str(value))
        need(number.is_finite(), "lineage amount is not finite")
        return format(number, "f")
    except InvalidOperation as exc:
        raise CatalogError(
            "lineage_evidence_mismatch", "lineage amount is invalid"
        ) from exc


def index(rows: Any, key: str) -> dict[str, dict]:
    need(isinstance(rows, list), "lineage collection is not an array")
    result: dict[str, dict] = {}
    for row in rows:
        need(isinstance(row, dict), "lineage entry is not an object")
        ident = row.get(key)
        need(
            isinstance(ident, str) and 0 < len(ident) <= 512 and ident not in result,
            "lineage identifier is absent, duplicate or too long",
        )
        result[ident] = row
    return result


def snapshot_id(report: dict, source: dict) -> str | None:
    capture = source.get("capture")
    if (
        not isinstance(capture, dict)
        or not SHA.fullmatch(str(capture.get("snapshot_sha256")))
        or not SHA.fullmatch(str(capture.get("receipt_sha256")))
    ):
        return None
    body = "\0".join(
        [
            "revenue-forecast:source-snapshot:1",
            report["report_id"],
            source["source_id"],
            capture["snapshot_sha256"],
            capture["receipt_sha256"],
        ]
    )
    return "rfsnap1-" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def locator(claim: dict) -> dict:
    raw = claim.get("locator")
    excerpt = claim.get("excerpt")
    need(
        isinstance(raw, str)
        and 0 < len(raw) <= 4096
        and isinstance(excerpt, str)
        and 0 < len(excerpt) <= 8192,
        "claim locator or excerpt exceeds its bound",
    )
    assert isinstance(raw, str) and isinstance(excerpt, str)
    # Only an explicit single physical-page marker is navigable. Never turn
    # printed page numbers, page ranges or arbitrary prose into physical pages.
    match = re.match(r"^PDF physical([1-9][0-9]{0,3})(?=[\s,;:.]|$)", raw)
    if match:
        suffix = raw[match.end() :]
        repeated = re.search(r"\bphysical(?:\s+pages?)?\s*[0-9]", suffix, re.IGNORECASE)
        span = re.match(
            r"^\s*(?:[\[(]\s*)?(?:[-\u2010-\u2015\u2212~\u301c]+|\.{2,}|(?:to|through|until|thru)(?=\s|[0-9(\[])|\u81f3|\u5230)",
            suffix,
            re.IGNORECASE,
        )
        listed = re.match(
            r"^\s*(?:[\[(]\s*)?(?:[,;\uFF0C\uFF1B/&+\u3001]|and(?=\s|[0-9(\[]))\s*(?:(?:PDF\s+)?physical(?:\s+pages?)?\s*|pages?\s*)?[\[(]?\s*[0-9]",
            suffix,
            re.IGNORECASE,
        )
        if repeated or span or listed:
            match = None
    return {
        "kind": "page" if match else "section",
        "value": match.group(1) if match else raw,
        "page_kind": "physical" if match else None,
        "excerpt": excerpt,
    }


class Sources:
    def __init__(self, catalog: Any, report: dict, result: dict):
        self.catalog, self.report = catalog, report
        # Native result.sources adds normalized source_rank. Capture seals bind
        # the original registered input SourceRecord, not that enriched view.
        original = result.get("input_document")
        if not isinstance(original, dict) or canonical_sha256(original) != report.get(
            "input_sha256"
        ):
            original = catalog._read_json(report["input_artifact"])
        need(
            canonical_sha256(original) == report.get("input_sha256"),
            "source input anchor differs",
        )
        self.source_index = index(original.get("sources", []), "source_id")
        self.cache: dict[str, dict] = {}
        self.bodies: dict[str, bytes] = {}
        self.seal_loaded = False
        self.seal: dict | None = None

    def publication_seal(self) -> dict | None:
        if self.seal_loaded:
            return self.seal
        self.seal_loaded = True
        runs, _, _, _ = self.catalog._index()
        run = runs.get(self.report["run_id"])
        need(isinstance(run, dict), "report run is absent")
        ref = run.get("source_evidence")
        if not isinstance(ref, dict) or set(ref) != {"relative_path", "bytes_sha256"}:
            return None
        relative = ref.get("relative_path")
        need(
            isinstance(relative, str) and "\\" not in relative,
            "registered source seal locator is invalid",
        )
        assert isinstance(relative, str)
        parts = PurePosixPath(relative)
        need(
            not parts.is_absolute()
            and not any(part in {".", ".."} for part in parts.parts),
            "registered source seal locator is invalid",
        )
        _not_linked(self.catalog.root, self.catalog.root / Path(*parts.parts))
        raw = self.catalog._read_artifact(ref)
        try:
            seal = _json(raw)
        except (ValueError, UnicodeError) as exc:
            raise CatalogError(
                "lineage_evidence_mismatch", "registered source seal is invalid"
            ) from exc
        if (
            not isinstance(seal, dict)
            or seal.get("schema_version") != "rf-research-publication-admission/1"
        ):
            return None
        need(
            hashlib.sha256(raw).hexdigest() == run.get("artifact_revision"),
            "registered source seal revision differs",
        )
        need(
            seal.get("report_id") == self.report["report_id"]
            and seal.get("run_id") == self.report["run_id"],
            "registered source seal names another report",
        )
        company = {
            k: self.report["company"].get(k)
            for k in ("entity_id", "listing_id", "analysis_subject_id")
        }
        need(
            seal.get("company") == company,
            "registered source seal names another company scope",
        )
        self.seal = seal
        return seal

    def _captured_body(self, source: dict) -> bytes | None:
        seal = self.publication_seal()
        if seal is None:
            return None
        recovery = seal.get("source_recovery")
        need(isinstance(recovery, dict), "registered source recovery is absent")
        assert isinstance(recovery, dict)
        if recovery.get("schema_version") == "rf-research-source-evidence/1":
            from report_catalog_research_publication_sources import retained_response

            rows = recovery.get("sources")
            need(isinstance(rows, list) and 2 <= len(rows) <= 16,
                 "registered multi-source evidence is invalid")
            assert isinstance(rows, list)
            selected_rows = [r for r in rows if isinstance(r, dict)
                             and r.get("source_id") == source["source_id"]]
            need(len(selected_rows) == 1, "registered source evidence is absent or ambiguous")
            row = selected_rows[0]
            if row.get("kind") == "company_wiki_anchor":
                need(row.get("source_record_sha256") == canonical_sha256(source),
                     "registered original source record changed")
                return None
            run_id = self.report["run_id"]
            need(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,191}", run_id),
                 "registered run basename is invalid")
            run = self.catalog.root / "delivery" / run_id
            _not_linked(self.catalog.root, run)
            observations = seal.get("input_observations")
            need(isinstance(observations, list) and len(observations) <= 4096,
                 "registered source observation manifest is invalid")
            assert isinstance(observations, list)
            relative = row.get("response_artifact")
            need(isinstance(relative, str), "registered response artifact is invalid")
            entries = [entry for entry in observations if isinstance(entry, dict)
                       and entry.get("artifact") == "delivery/" + run_id + "/" + relative]
            need(len(entries) == 1, "registered source response observation is missing")
            obs = _Observation(run)
            try:
                body = retained_response(obs, run, source, row)
                raw = obs.read(run / relative)
            except (CatalogError, ValueError, TypeError, KeyError) as exc:
                raise CatalogError("lineage_evidence_mismatch",
                                   "registered retained source response differs") from exc
            need(type(entries[0].get("bytes")) is int
                 and entries[0]["bytes"] == len(raw)
                 and entries[0].get("sha256") == hashlib.sha256(raw).hexdigest(),
                 "registered source response bytes changed")
            need(0 < len(body) <= MAX_BODY, "captured source exceeds its byte bound",
                 "lineage_limit_exceeded")
            obs.recheck()  # Only this selected response, never shared mutable state.
            self.bodies[source["source_id"]] = body
            return body
        if recovery.get("source_id") != source["source_id"]:
            return None
        run_id = self.report["run_id"]
        need(
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,191}", run_id),
            "registered run basename is invalid",
        )
        run = self.catalog.root / "delivery" / run_id
        _not_linked(self.catalog.root, run)
        obs = _Observation(run)
        rows = seal.get("input_observations")
        need(
            isinstance(rows, list) and len(rows) <= 4096,
            "registered source observation manifest is invalid",
        )
        assert isinstance(rows, list)
        selected: dict[str, dict] = {}
        for row in rows:
            need(
                isinstance(row, dict) and isinstance(row.get("artifact"), str),
                "source observation row is invalid",
            )
            key = row["artifact"]
            need(
                key not in selected,
                "source observation manifest has duplicate artifacts",
            )
            selected[key] = row
        # These roles are fixed by the admitted schema, never chosen from a
        # caller path, a directory scan or a filename supplied by the source.
        names = {
            "body": "execution/web-capture-q3-2026/source.markdown",
            "transport": "execution/web-capture-q3-2026/tool-response.json",
            "observation": "execution/web-capture-q3-2026/acquisition-observation.json",
            "event": "execution/company-release-capture-event.json",
            "source": "execution/company-release-q3-2026-source.json",
        }
        blobs: dict[str, bytes] = {}
        for role, relative in names.items():
            entry = selected.get("delivery/" + run_id + "/" + relative)
            need(isinstance(entry, dict), "registered source observation is missing")
            assert isinstance(entry, dict)
            if role == "body":
                need(
                    type(entry.get("bytes")) is int and 0 < entry["bytes"] <= MAX_BODY,
                    "captured source exceeds its registered byte bound",
                    "lineage_limit_exceeded",
                )
            raw = obs.read(run / relative)
            need(
                type(entry.get("bytes")) is int
                and entry["bytes"] == len(raw)
                and entry.get("sha256") == hashlib.sha256(raw).hexdigest(),
                "registered captured source bytes changed",
            )
            blobs[role] = raw
        body = blobs["body"]
        need(
            0 < len(body) <= MAX_BODY,
            "captured source exceeds its byte bound",
            "lineage_limit_exceeded",
        )
        try:
            decoded = body.decode("utf-8", errors="strict")
            parsed = {
                key: _json(value) for key, value in blobs.items() if key != "body"
            }
        except (ValueError, UnicodeError) as exc:
            raise CatalogError(
                "lineage_evidence_mismatch", "captured source is not strict UTF-8 data"
            ) from exc
        capture = source.get("capture", {})
        need(isinstance(capture, dict), "source capture is not typed metadata")
        assert isinstance(capture, dict)
        event = parsed["event"]
        response = parsed["transport"]
        observation = parsed["observation"]
        need(
            isinstance(response, dict)
            and isinstance(response.get("results"), list)
            and len(response["results"]) == 1
            and response.get("failed_results") == [],
            "captured source response is not complete",
        )
        page = response["results"][0]
        need(
            isinstance(page, dict)
            and page.get("raw_content") == decoded
            and page.get("url") == source.get("url")
            and page.get("title") == source.get("title"),
            "captured source does not bind its actual tool body",
        )
        body_sha = hashlib.sha256(body).hexdigest()
        transport_sha = hashlib.sha256(blobs["transport"]).hexdigest()
        need(
            canonical_sha256(parsed["source"])
            == canonical_sha256(source)
            == recovery.get("source_record_sha256"),
            "captured source record differs from registered input",
        )
        need(
            body_sha
            == capture.get("snapshot_sha256")
            == recovery.get("snapshot_sha256")
            == event.get("retrieved_markdown_sha256")
            and transport_sha
            == recovery.get("transport_sha256")
            == event.get("response_artifact_sha256")
            and canonical_sha256(event)
            == recovery.get("capture_event_sha256")
            == capture.get("host_receipt", {}).get("event_sha256"),
            "captured source registered hashes disagree",
        )
        request = event.get("request")
        need(
            isinstance(request, dict)
            and request.get("query_omitted") is True
            and request.get("urls") == [source.get("url")]
            and request.get("format") == "markdown"
            and request == observation.get("request"),
            "captured source observation targets another source",
        )
        need(
            event.get("request_id")
            == observation.get("request_id")
            == response.get("request_id")
            == capture.get("tool_call_id")
            and event.get("tool") == observation.get("tool") == capture.get("tool_name")
            and event.get("raw_artifact_kind")
            == "tool-returned complete markdown; not raw HTML",
            "captured source event disagrees with its receipt",
        )
        obs.recheck()  # Only the five selected source files, not mutable registry/ledger.
        self.bodies[source["source_id"]] = body
        return body

    def get(self, source_id: str) -> dict:
        if source_id in self.cache:
            return self.cache[source_id]
        need(source_id in self.source_index, "claim source is absent from exact report")
        source = self.source_index[source_id]
        capture = (
            source.get("capture") if isinstance(source.get("capture"), dict) else {}
        )
        assert isinstance(capture, dict)
        content_sha = capture.get("snapshot_sha256")
        receipt_sha = capture.get("receipt_sha256")
        need(
            content_sha is None or SHA.fullmatch(str(content_sha)),
            "source capture content hash is invalid",
        )
        need(
            receipt_sha is None or SHA.fullmatch(str(receipt_sha)),
            "source capture receipt hash is invalid",
        )
        output = {
            "source_id": source_id,
            "title": source.get("title"),
            "source_type": source.get("source_type"),
            "publisher": source.get("publisher"),
            "url": source.get("url"),
            "published_date": source.get("published_date"),
            "accessed_date": source.get("accessed_date"),
            "content_sha256": content_sha if SHA.fullmatch(str(content_sha)) else None,
            "capture_receipt_sha256": receipt_sha
            if SHA.fullmatch(str(receipt_sha))
            else None,
            "binding_state": "partial",
            "missing_reason": "source_original_binding_unavailable",
            "source_ref": None,
            "source_snapshot_id": None,
            "original_format": "unavailable",
            "note": "Original source binding is unavailable; no replacement is fetched.",
        }
        wiki = source.get("company_wiki_trace")
        ref = wiki.get("source_ref") if isinstance(wiki, dict) else None
        if isinstance(ref, dict):
            need(
                set(ref) == SOURCE_REF_FIELDS
                and ref.get("schema_version") == "2.0"
                and SHA.fullmatch(str(ref.get("content_sha256")))
                and type(ref.get("byte_size")) is int
                and ref["byte_size"] > 0
                and all(
                    isinstance(ref.get(key), str) and bool(ref[key])
                    for key in ("document_id", "source_id", "mime_type")
                ),
                "source has an invalid complete CWP reference",
            )
            if content_sha is not None:
                need(
                    ref.get("content_sha256") == content_sha,
                    "CWP reference differs from its captured source hash",
                )
            output["content_sha256"] = ref["content_sha256"]
            if content_sha is not None and output["capture_receipt_sha256"] is not None:
                output.update(
                    binding_state="available",
                    missing_reason=None,
                    source_ref=copy.deepcopy(ref),
                    original_format="cwp_document",
                    note="Immutable CWP six-field reference; physical locations are claim-declared. Current CWP reading policy still applies on open.",
                )
        elif (
            source.get("source_type") == "company_release"
            and output["content_sha256"]
            and output["capture_receipt_sha256"]
        ):
            body = self._captured_body(source)
            if body is not None:
                output.update(
                    binding_state="available",
                    missing_reason=None,
                    source_snapshot_id=snapshot_id(self.report, source),
                    original_format="captured_markdown",
                    note="Complete tool-returned Markdown captured for this report; not publisher HTML, not signed host attestation. Render as untrusted plain text.",
                )
        self.cache[source_id] = output
        return output


def public_pathless(value: Any) -> None:
    """Only typed URL metadata may be an HTTP citation, never a file locator."""
    text_limits = {
        "parameter_id": 512,
        "claim_id": 512,
        "source_id": 512,
        "target_id": 512,
        "report_id": 192,
        "node_id": 192,
        "input_name": 1024,
        "definition": 8192,
        "rationale": 16384,
        "formula": 2048,
        "native_locator": 4096,
        "excerpt": 8192,
        "unit": 256,
        "currency": 32,
        "scale": 128,
        "period": 256,
        "time_basis": 128,
        "dimension": 128,
        "title": 4096,
        "publisher": 2048,
        "url": 8192,
        "note": 4096,
        "missing_reason": 1024,
        "verification_status": 128,
        "evidence_role": 128,
    }

    def mask(item: Any) -> Any:
        if isinstance(item, list):
            return [mask(child) for child in item]
        if not isinstance(item, dict):
            return item
        result = {}
        for key, child in item.items():
            if isinstance(child, str) and key in text_limits:
                need(
                    len(child) <= text_limits[key],
                    "lineage text exceeds its " + key + " bound",
                    "lineage_limit_exceeded",
                )
            if key == "value" and isinstance(child, str):
                limit = 4096 if "page_kind" in item else 160
                need(
                    len(child) <= limit,
                    "lineage value exceeds its text bound",
                    "lineage_limit_exceeded",
                )
            if key == "url" and child is not None:
                need(
                    isinstance(child, str)
                    and len(child) <= 8192
                    and bool(
                        re.fullmatch(r"https?://[^\s<>\"'\\]+", child, flags=re.I)
                    ),
                    "source URL is not a public HTTP citation",
                )
                try:
                    parsed = urlsplit(child)
                    need(
                        bool(parsed.hostname)
                        and parsed.username is None
                        and parsed.password is None
                        and (parsed.port is None or 0 < parsed.port <= 65535),
                        "source URL authority is invalid",
                    )
                except ValueError as exc:
                    raise CatalogError(
                        "lineage_evidence_mismatch", "source URL authority is invalid"
                    ) from exc
                result[key] = ""
            else:
                result[key] = mask(child)
        return result

    _assert_pathless(mask(value))


def _anchors(record: dict) -> None:
    need(
        record.get("status") in {"validated", "published"}
        and SHA.fullmatch(str(record.get("input_sha256")))
        and SHA.fullmatch(str(record.get("result_sha256"))),
        "this report has no supported immutable input/result lineage",
        "lineage_unavailable",
    )


def get_source_snapshot(
    catalog: Any, record: dict, result: dict, requested: str
) -> dict:
    _anchors(record)
    need(
        isinstance(requested, str) and TOKEN.fullmatch(requested),
        "snapshot ID must be an opaque report-bound token",
        "invalid_id",
    )
    sources = Sources(catalog, record, result)
    matches = [
        source
        for source in sources.source_index.values()
        if source.get("source_type") == "company_release"
        and snapshot_id(record, source) == requested
    ]
    need(len(matches) == 1, "snapshot is absent from this exact report", "not_found")
    source = matches[0]
    public = sources.get(source["source_id"])
    need(
        public["original_format"] == "captured_markdown"
        and public["source_snapshot_id"] == requested,
        "registered captured source is unavailable",
        "lineage_unavailable",
    )
    body = sources.bodies[source["source_id"]]
    value = {
        "schema_version": SNAPSHOT_SCHEMA,
        "report_id": record["report_id"],
        "snapshot_id": requested,
        "source_id": source["source_id"],
        "input_sha256": record["input_sha256"],
        "result_sha256": record["result_sha256"],
        "content_sha256": hashlib.sha256(body).hexdigest(),
        "byte_size": len(body),
        "media_type": "text/markdown",
        "content_base64url": base64.urlsafe_b64encode(body).decode("ascii").rstrip("="),
        "source": public,
        "note": "Retained complete captured Markdown, not raw publisher HTML. No live request or repair performed.",
    }
    public_pathless(value)
    return value


def get_calculation_trace(
    catalog: Any, record: dict, result: dict, revision: str, requested: str
) -> dict:
    _anchors(record)
    valid_nodes = set(catalog._node_ids(result))
    need(
        requested in valid_nodes,
        "calculation node is absent from this exact report",
        "node_not_found",
    )
    parameters = index(result.get("parameter_trace", []), "parameter_id")
    claims = index(result.get("evidence_claims", []), "claim_id")
    sources = Sources(catalog, record, result)
    nodes: dict[str, dict] = {}
    bindings: list[dict] = []
    parameter_rows: dict[str, dict] = {}
    parameter_heights: dict[str, int] = {}
    claim_rows: dict[str, dict] = {}
    source_rows: dict[str, dict] = {}
    reasons: set[str] = set()
    years = list(result.get("forecast_years", []))

    def bounded(key: str, count: int) -> None:
        need(
            count <= LIMITS[key],
            "calculation lineage exceeds its " + key + " bound",
            "lineage_limit_exceeded",
        )

    def add_parameter(pid: str, stack: set[str]) -> bool:
        need(
            len(stack) < MAX_DEPTH and pid not in stack,
            "parameter dependency depth or cycle is invalid",
            "lineage_limit_exceeded",
        )
        if pid in parameter_rows:
            need(
                len(stack) + parameter_heights[pid] <= MAX_DEPTH,
                "shared parameter dependency path exceeds its depth bound",
                "lineage_limit_exceeded",
            )
            return parameter_rows[pid]["is_conditional"]
        need(pid in parameters, "bound parameter is absent")
        row = parameters[pid]
        kind = row.get("kind")
        dependencies = (
            row.get("input_parameter_ids", []) if kind == "derived_fact" else []
        )
        need(
            isinstance(dependencies, list), "parameter dependencies are not ordered IDs"
        )
        declared_claims = row.get("claim_ids", [])
        need(isinstance(declared_claims, list), "parameter claim IDs are invalid")
        conditional = kind in {
            "management_guidance",
            "analyst_assumption",
            "scenario_stress",
        }
        public = {
            key: row.get(key)
            for key in (
                "parameter_id",
                "kind",
                "unit",
                "currency",
                "scale",
                "period",
                "period_start",
                "period_end",
                "scenario",
                "time_basis",
                "dimension",
                "definition",
                "rationale",
                "formula",
            )
        }
        public.update(
            value=decimal(row.get("value")),
            input_parameter_ids=list(dependencies),
            claim_ids=list(declared_claims),
            is_conditional=False,
        )
        parameter_rows[pid] = public
        bounded("parameters", len(parameter_rows))
        height = 1
        for dep in dependencies:
            conditional = add_parameter(dep, stack | {pid}) or conditional
            height = max(height, 1 + parameter_heights[dep])
        parameter_heights[pid] = height
        public["is_conditional"] = conditional
        if kind != "derived_fact" and not declared_claims:
            reasons.add("parameter_claims_unavailable:" + pid)
        for cid in declared_claims:
            need(cid in claims, "bound claim is absent")
            claim = claims[cid]
            need(
                claim.get("target_type") == "parameter"
                and claim.get("target_id") == pid,
                "claim does not target its bound parameter",
            )
            sid = claim.get("source_id")
            need(
                isinstance(sid, str) and sid in row.get("source_ids", []),
                "claim source is not declared by its parameter",
            )
            assert isinstance(sid, str)
            source = sources.get(sid)
            need(
                claim.get("excerpt_sha256")
                == hashlib.sha256(claim["excerpt"].encode("utf-8")).hexdigest(),
                "claim excerpt hash differs",
            )
            need(
                claim.get("content_sha256") == source["content_sha256"]
                and claim.get("capture_receipt_sha256")
                == source["capture_receipt_sha256"],
                "claim hashes differ from its exact source",
            )
            if source["original_format"] == "captured_markdown":
                need(
                    claim["excerpt"] in sources.bodies[sid].decode("utf-8"),
                    "claim excerpt is absent from captured source",
                )
            if source["binding_state"] != "available":
                reasons.add("source_original_unavailable:" + sid)
            public_claim = {
                key: claim.get(key)
                for key in (
                    "claim_id",
                    "target_type",
                    "target_id",
                    "source_id",
                    "support_type",
                    "excerpt_sha256",
                    "content_sha256",
                    "capture_receipt_sha256",
                    "verification_status",
                    "verified_date",
                    "unit",
                    "period",
                    "evidence_role",
                )
            }
            public_claim.update(
                native_locator=claim["locator"],
                locator=locator(claim),
                extracted_value=decimal(claim["extracted_value"])
                if claim.get("extracted_value") is not None
                else None,
            )
            claim_rows[cid], source_rows[sid] = public_claim, source
            bounded("claims", len(claim_rows))
            bounded("sources", len(source_rows))
        return conditional

    def attach(
        node: dict,
        position: int,
        name: str,
        pids: list[str],
        children: list[str],
        missing: str | None,
    ) -> None:
        bindings.append(
            {
                "node_id": node["node_id"],
                "input_index": position,
                "input_name": name,
                "parameter_ids": pids,
                "calculation_node_ids": children,
                "missing_reason": missing,
            }
        )
        bounded("bindings", len(bindings))
        provenance = node["inputs"][position]["provenance"]
        if missing:
            reasons.add(missing + ":" + node["node_id"] + ":" + str(position))
            provenance["missing_reason"] = missing
            return
        provenance.update(quality="owner_validated_binding", missing_reason=None)
        if pids:
            row = parameter_rows[pids[0]]
            provenance["kind"] = (
                "fact"
                if row["kind"] == "reported_fact"
                else "calculation"
                if row["kind"] == "derived_fact"
                else "assumption"
            )
            direct = [claim_rows[cid] for cid in row["claim_ids"]]
            direct_sources = {
                claim["source_id"]: source_rows[claim["source_id"]] for claim in direct
            }
            provenance["source_refs"] = [
                copy.deepcopy(source["source_ref"])
                for source in direct_sources.values()
                if source["source_ref"] is not None
            ]
            provenance["locator"] = (
                copy.deepcopy(direct[0]["locator"]) if len(direct) == 1 else None
            )

    def add_node(nid: str, stack: set[str]) -> None:
        need(
            len(stack) < MAX_DEPTH and nid not in stack,
            "calculation dependency depth or cycle is invalid",
            "lineage_limit_exceeded",
        )
        if nid in nodes:
            return
        need(nid in valid_nodes, "child calculation is absent")
        node = copy.deepcopy(
            catalog._calculation_from_validated(record, result, revision, nid)[
                "calculation"
            ]
        )
        nodes[nid] = node
        bounded("nodes", len(nodes))
        parts = nid.split(":")
        scenario, year = parts[-2], int(parts[-1])
        for pos, item in enumerate(node["inputs"]):
            name = item["name"]
            pids: list[str] = []
            children: list[str] = []
            missing = None
            if parts[0] == "consolidated":
                bridges = result["consolidated_forecast"][scenario].get(
                    "segment_bridge", []
                )
                if pos < len(bridges):
                    matches = [
                        i
                        for i, segment in enumerate(result["segments"])
                        if segment.get("name") == bridges[pos].get("name")
                    ]
                    if len(matches) == 1:
                        child = f"segment:{matches[0]}:{scenario}:{year}"
                        add_node(child, stack | {nid})
                        children.append(child)
                        child_output = nodes[child].get("output")
                        need(
                            child_output is not None
                            and Decimal(child_output["number"]["value"])
                            == Decimal(item["number"]["value"]),
                            "aggregate input differs from its child output",
                        )
                    else:
                        missing = "aggregate_segment_binding_unavailable"
                else:
                    missing = "adjustment_lineage_unavailable"
            else:
                segment = result["segments"][int(parts[1])]
                detail = segment["scenarios"][scenario]
                if name == "previous_revenue":
                    position = years.index(year)
                    if position:
                        child = f"segment:{parts[1]}:{scenario}:{years[position - 1]}"
                        add_node(child, stack | {nid})
                        children.append(child)
                    elif isinstance(segment.get("base_revenue_parameter_id"), str):
                        pids = [segment["base_revenue_parameter_id"]]
                    else:
                        missing = "base_revenue_parameter_binding_unavailable"
                else:
                    ids = detail.get("driver_parameter_ids", {}).get(name)
                    if isinstance(ids, list) and len(ids) == len(years):
                        pids = [ids[years.index(year)]]
                    else:
                        missing = "default_or_driver_parameter_binding_unavailable"
                for pid in pids:
                    add_parameter(pid, set())
                    parameter = parameters[pid]
                    expected_year = (
                        years[years.index(year) - 1]
                        if name == "previous_revenue" and years.index(year)
                        else result.get("base_year")
                        if name == "previous_revenue"
                        else year
                    )
                    need(
                        parameter.get("period") == f"FY{expected_year}"
                        and parameter.get("scenario") in {None, "all", scenario},
                        "parameter period or scenario differs from its input",
                    )
                    need(
                        Decimal(decimal(parameter["value"]))
                        == Decimal(item["number"]["value"]),
                        "parameter value differs from its input",
                    )
            attach(node, pos, name, pids, children, missing)
        own = [b for b in bindings if b["node_id"] == nid]
        child_incomplete = any(
            nodes[c]["trace_state"] != "available"
            for b in own
            for c in b["calculation_node_ids"]
        )
        if node.get("output") is None or not node.get("expression"):
            reasons.add(node.get("missing_reason") or "native_calculation_unavailable")
        else:
            missing_bindings = [b["missing_reason"] for b in own if b["missing_reason"]]
            node.update(
                trace_state="partial"
                if missing_bindings or child_incomplete
                else "available",
                missing_reason=";".join(missing_bindings)
                if missing_bindings
                else "child_lineage_partial"
                if child_incomplete
                else None,
            )

    add_node(requested, set())
    value = {
        "schema_version": TRACE_SCHEMA,
        "report_id": record["report_id"],
        "node_id": requested,
        "input_sha256": record["input_sha256"],
        "result_sha256": record["result_sha256"],
        "catalog_revision": revision,
        "state": "unavailable"
        if nodes[requested].get("output") is None
        else "partial"
        if reasons
        else "available",
        "missing_reasons": sorted(reasons),
        "nodes": list(nodes.values()),
        "bindings": bindings,
        "parameters": list(parameter_rows.values()),
        "claims": list(claim_rows.values()),
        "sources": list(source_rows.values()),
    }
    public_pathless(value)
    need(
        len(json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        <= MAX_TRACE_BYTES,
        "calculation trace exceeds its serialized byte bound",
        "lineage_limit_exceeded",
    )
    return value
