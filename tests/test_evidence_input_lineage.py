"""R6-RF-INPUT I3/I4: evidence roles, inference distance, and real input lineage.

A valid claim ID over real source text does not automatically support a future
growth range: a historical base is history, an accounting policy carries
recognition only, a peer's competitive fact is an analogy — never the company's
own mechanism — and directional support is not a numeric range. A
NarrativeRef file that exists is not an RF input until a span is bound into a
parameter/driver dependency. These tests pin the machine-checkable half of
those rules; the economic semantics stay with MAIN's independent review.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from revenue_core import ForecastInputError, canonical_sha256, run_forecast, text_sha256  # noqa: E402
from contracts.evidence import build_host_receipt  # noqa: E402
from company_wiki_narrative_contracts import (  # noqa: E402
    SPAN_PREFIX, canonical_bytes, validate_narrative_response,
)
from test_data_contract import apply_parameter_contract, finalize_contract  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


# ---------------------------------------------------------------------------
# Offline NarrativeRef protocol fixture builder (published wire contract v2.0)
# ---------------------------------------------------------------------------

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _span(source_id: str, raw_text: str, char_start: int) -> dict:
    coordinates = {
        "page_number": None, "paragraph_index": 1, "table_index": None,
        "row_index": None, "column_index": None,
        "char_start": char_start, "char_end": char_start + len(raw_text),
    }
    locator = (
        f"loc:v1/paragraph:1/chars:{char_start}-{char_start + len(raw_text)}"
    )
    structured_value = {
        "language": "en",
        "section": "prepared_remarks",
        "source_role": "management",
        "text_sha256": text_sha256(raw_text),
    }
    output_sha256 = sha256_hex(canonical_bytes(
        {"raw_text": raw_text, "structured_value": structured_value}
    ))
    span_sha = sha256_hex(canonical_bytes({
        "source_id": source_id, "locator": locator, "output_sha256": output_sha256,
    }))
    return {
        "schema_version": "1.0.0",
        "span_id": SPAN_PREFIX + span_sha,
        "source_id": source_id,
        "locator": locator,
        "coordinates": coordinates,
        "raw_text": raw_text,
        "structured_value": structured_value,
        "parser_name": "fixture-parser",
        "parser_version": "1.0.0",
        "output_sha256": output_sha256,
        "parse_status": "parsed",
        "quality_flags": [],
    }


def build_narrative_fixture(text: str, span_texts: list[str], *, read_at: str = "2026-07-01T00:00:00Z"):
    """Build a fully valid narrative-read wire triple for offline tests."""
    content = text.encode("utf-8")
    content_sha256 = sha256_hex(content)
    source_ref = {
        "schema_version": "2.0",
        "document_id": f"urn:company-wiki:document:sha256:{content_sha256}",
        "source_id": f"urn:company-wiki:source:sha256:{content_sha256}",
        "content_sha256": content_sha256,
        "byte_size": len(content),
        "mime_type": "text/plain",
    }
    spans = []
    char_cursor = 0
    for raw_text in span_texts:
        spans.append(_span(source_ref["source_id"], raw_text, char_cursor))
        char_cursor += len(raw_text) + 1
    line_count = text.count("\n") + 1
    line_starts = [0]
    for char in text:
        if char == "\n":
            line_starts.append(line_starts[-1])
            line_starts[-1] = text.index("\n", line_starts[-2] if len(line_starts) > 1 else 0) + 1
    # Simple deterministic byte ranges: each span maps to its own text range.
    bindings = []
    cursor = 0
    for index, span in enumerate(spans):
        span_len = len(span["raw_text"].encode("utf-8"))
        bindings.append({
            "evidence_id": span["span_id"],
            "material_line_start": index + 1,
            "material_line_end": index + 1,
            "source_byte_ranges": [{"start": cursor, "end": cursor + span_len}],
        })
        cursor += span_len + 1
    lineage = {
        "schema_version": "transcript-material/2",
        "original_source_id": source_ref["source_id"],
        "original_sha256": content_sha256,
        "original_byte_size": len(content),
        "original_mime_type": "text/plain",
        "text_sha256": sha256_hex(content),
        "text_byte_size": len(content),
        "line_count": line_count,
        "extractor_version": "fixture-extractor-1",
    }
    claims = [
        {
            "claim_id": f"claim-replay-{index:03d}",
            "text": span["raw_text"],
            "evidence_ids": [span["span_id"]],
            "claim_type": "company_statement",
            "modality": "actual",
            "needs_review": False,
        }
        for index, span in enumerate(spans)
    ]
    bundle = {
        "schema_version": "narrative-bundle/2.0",
        "source_ref": source_ref,
        "expected_read_policy_sha256": "b" * 64,
        "source_metadata": {
            "source_class": "transcript",
            "title": "ACME business update",
            "document_kind": "investor_call_transcript",
            "language": "en",
        },
        "quality_status": "verified",
        "selection": {
            "status": "selected", "coverage_complete": True, "source_units": 1,
            "candidate_count": len(spans), "selected_count": len(spans),
            "omitted_candidate_count": 0, "dropped_financial_count": 0,
            "pages_total": 1, "pages_read": 1, "lines_total": line_count,
            "tables_total": 0, "tables_scanned": 0,
        },
        "evidence_spans": spans,
        "summary": {
            "status": "completed", "translate": False,
            "draft": {
                "source_id": source_ref["source_id"],
                "source_sha256": content_sha256,
                "language": "en",
                "claims": claims,
                "status": "draft",
            },
            "model": {
                "adapter_id": "fixture-adapter", "model_id": "fixture-model",
                "prompt_version": "fixture-prompt-1",
                "response_sha256": "c" * 64,
            },
        },
        "prompt_review": {
            "status": "not_detected", "source_sha256": content_sha256,
            "evidence_sha256": None, "policy_hash": None, "reviewed_at": read_at,
        },
        "transcript_lineage": lineage,
        "transcript_byte_bindings": bindings,
        "versions": {
            "parser": "fixture-parser-1", "selector": "fixture-selector-1",
            "material": "fixture-material-1", "model": "fixture-model",
            "prompt": "fixture-prompt-1", "bundle_producer": "fixture-producer-1",
        },
        "replay": {"required": True, "locator_count": len(spans)},
    }
    body = canonical_bytes(bundle)
    manifest = {
        "document_id": source_ref["document_id"],
        "source_id": source_ref["source_id"],
        "content_sha256": content_sha256,
        "byte_size": len(content),
        "mime_type": "text/plain",
        "title": "ACME business update",
        "document_kind": "investor_call_transcript",
        "published_date": "2026-06-01",
        "source_url": "https://fixtures.invalid/sources/transcript.txt",
        "retrieved_at": read_at,
        "collector_name": "fixture-collector", "collector_version": "1.0.0",
        "canonical_entity_id": "US_ACME", "display_name": "ACME",
        "market": "US", "security_id": "ACME", "fiscal_year": 2026,
        "fiscal_period": "Q2", "period_end": "2026-06-30",
        "form_type": "transcript", "provider": "fixture-provider",
        "provider_document_id": "fixture-doc-1", "language": "en",
    }
    narrative_ref = {
        "schema_version": "narrative-ref/1",
        "artifact_version_id": "artifact-fixture-001",
        "artifact_sha256": sha256_hex(body),
        "byte_size": len(body),
        "source_ref": source_ref,
    }
    receipt = {
        "schema_version": "narrative-read-receipt/1",
        "status": "ok",
        "narrative_ref": narrative_ref,
        "as_of_date": "2026-10-08",
        "manifest": manifest,
        "source_read_policy_sha256": "d" * 64,
        "read_at": read_at,
        "locator_count": len(spans),
        "selection_status": "selected",
        "quality_status": "verified",
        "replay_status": "verified",
    }
    request = {
        "schema_version": "narrative-read-request/1",
        "narrative_ref": narrative_ref,
        "as_of_date": "2026-10-08",
        "expected_source": {
            "canonical_entity_id": "US_ACME", "market": "US",
            "security_id": "ACME", "document_kind": "investor_call_transcript",
            "fiscal_year": 2026, "fiscal_period": "Q2",
        },
    }
    receipt_bytes = canonical_bytes(receipt) + b"\n"
    context = validate_narrative_response(request, body, receipt_bytes)
    return context.to_dict()


# ---------------------------------------------------------------------------
# Shared binding helpers
# ---------------------------------------------------------------------------

def _parameter(**overrides) -> dict:
    parameter = {
        "parameter_id": "a_growth_2026_base",
        "kind": "analyst_assumption",
        "value": 0.1,
        "unit": "ratio",
        "period": "FY2026",
        "definition": "segment A growth rate base",
        "dimension": "ratio",
        "scenario": "base",
        "rationale": "Driver-based test assumption",
        "source_ids": [],
        "claim_ids": [],
    }
    parameter.update(overrides)
    return parameter


def _classic_binding(**overrides) -> dict:
    binding = {
        "role": "mechanism_direction",
        "source_id": "filing",
        "locator": "MD&A outlook",
        "excerpt": "Demand indicators point to continued order intake growth next year.",
    }
    binding.update(overrides)
    return binding


class BindParameterEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        from research.input_evidence import bind_parameter_evidence

        self.bind = bind_parameter_evidence
        self.data = forecast_document()
        self.source = self.data["sources"][0]

    def test_history_alone_cannot_support_a_forecast_assumption(self) -> None:
        parameter = _parameter()
        with self.assertRaisesRegex(ForecastInputError, "history_base"):
            self.bind(
                parameter,
                evidence_bindings=[
                    _classic_binding(role="history_base",
                                     excerpt="Revenue was USD 150 million in FY2025."),
                ],
                source=self.source,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )

    def test_history_plus_mechanism_direction_is_accepted(self) -> None:
        parameter = _parameter()
        result = self.bind(
            parameter,
            evidence_bindings=[
                _classic_binding(role="history_base",
                                 excerpt="Revenue was USD 150 million in FY2025."),
                _classic_binding(role="mechanism_direction",
                                 excerpt="Demand indicators point to continued order intake growth next year."),
            ],
            source=self.source,
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
        )
        self.assertEqual(len(result["claims"]), 2)
        self.assertEqual(len(result["parameter"]["claim_ids"]), 2)
        self.assertIn("filing", result["parameter"]["source_ids"])
        lineage = result["lineage"]
        roles = {entry["role"] for entry in lineage}
        self.assertEqual(roles, {"history_base", "mechanism_direction"})
        for entry in lineage:
            self.assertEqual(entry["content_sha256"], self.source["capture"]["snapshot_sha256"])
            self.assertEqual(entry["excerpt_sha256"], text_sha256(entry["excerpt"]))

    def test_direction_support_must_not_carry_a_numeric_value(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "mechanism_direction"):
            self.bind(
                _parameter(),
                evidence_bindings=[
                    _classic_binding(extracted_value=0.12, unit="ratio", period="FY2026"),
                ],
                source=self.source,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )

    def test_range_support_requires_a_numeric_value(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "value_range"):
            self.bind(
                _parameter(),
                evidence_bindings=[_classic_binding(role="value_range")],
                source=self.source,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )
        result = self.bind(
            _parameter(),
            evidence_bindings=[
                _classic_binding(role="value_range", extracted_value=0.12,
                                 unit="ratio", period="FY2026"),
            ],
            source=self.source,
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
        )
        self.assertEqual(result["claims"][0]["support_type"], "exact_value")
        self.assertAlmostEqual(result["claims"][0]["extracted_value"], 0.12, places=12)

    def test_accounting_policy_cannot_support_a_parameter(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "recognition|policy"):
            self.bind(
                _parameter(),
                evidence_bindings=[
                    _classic_binding(role="recognition_policy",
                                     excerpt="Revenue is recognized upon customer acceptance."),
                ],
                source=self.source,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )
        with self.assertRaisesRegex(ForecastInputError, "policy_support"):
            self.bind(
                _parameter(),
                evidence_bindings=[
                    dict(_classic_binding(), support_type="policy_support"),
                ],
                source=self.source,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )

    def test_counterevidence_cannot_be_parameter_support(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "counterevidence"):
            self.bind(
                _parameter(),
                evidence_bindings=[
                    _classic_binding(role="counterevidence",
                                     excerpt="Two customers delayed renewals this quarter."),
                ],
                source=self.source,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )

    def test_peer_analogy_requires_analogical_distance(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "analogical"):
            self.bind(
                _parameter(),
                evidence_bindings=[
                    _classic_binding(role="peer_analogy", inference_distance="direct",
                                     excerpt="Peer Co reported competing product launches."),
                ],
                source=self.source,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )
        result = self.bind(
            _parameter(),
            evidence_bindings=[
                _classic_binding(role="peer_analogy", inference_distance="analogical",
                                 excerpt="Peer Co reported competing product launches."),
            ],
            source=self.source,
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
        )
        self.assertEqual(result["claims"][0]["evidence_role"], "peer_analogy")

    def test_unknown_role_is_rejected(self) -> None:
        with self.assertRaises(ForecastInputError):
            self.bind(
                _parameter(),
                evidence_bindings=[_classic_binding(role="vibes")],
                source=self.source,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )

    def test_tampered_capture_receipt_is_rejected_at_binding_time(self) -> None:
        tampered = copy.deepcopy(self.source)
        tampered["capture"]["receipt_sha256"] = "e" * 64
        with self.assertRaisesRegex(ForecastInputError, "receipt|capture"):
            self.bind(
                _parameter(),
                evidence_bindings=[_classic_binding()],
                source=tampered,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )


class PeerTriangulationEngineTests(unittest.TestCase):
    def _doc_with_driver(self, peer: bool) -> dict:
        data = forecast_document()
        claim_a = {
            "claim_id": "claim_direct_a",
            "source_id": "filing",
            "target_type": "growth_driver",
            "target_id": "node_a",
            "support_type": "rationale_support",
            "locator": "MD&A outlook",
            "excerpt": "Company order intake grew on new customer ramps this year.",
            "excerpt_sha256": text_sha256("Company order intake grew on new customer ramps this year."),
            "content_sha256": data["sources"][0]["capture"]["snapshot_sha256"],
            "capture_receipt_sha256": data["sources"][0]["capture"]["receipt_sha256"],
            "verification_status": "opened_and_checked",
            "verified_by": "input-semantics-test",
            "verified_date": data["as_of_date"],
        }
        second_source = copy.deepcopy(data["sources"][0])
        second_source["source_id"] = "presentation"
        second_source["url"] = "https://www.sec.gov/Archives/edgar/data/1/presentation.htm"
        second_source["title"] = "Investor presentation"
        second_capture = dict(second_source["capture"])
        second_capture["tool_call_id"] = "fixture-presentation"
        host = dict(second_capture["host_receipt"])
        host["tool_name"] = second_capture["tool_name"]
        host.pop("receipt_sha256", None)
        host = build_host_receipt(
            issuer=host["issuer"], environment=host["environment"],
            tool_name=host["tool_name"], action=host["action"],
            event_sha256=text_sha256("fixture-presentation"),
            timestamp=host["timestamp"],
        )
        second_capture["host_receipt"] = host
        second_capture.pop("receipt_sha256", None)
        second_capture["receipt_sha256"] = canonical_sha256(second_capture)
        second_source["capture"] = second_capture
        data["sources"].append(second_source)
        claim_b = dict(claim_a)
        claim_b.update({
            "claim_id": "claim_direct_b",
            "source_id": "presentation",
            "target_id": "node_b",
            "excerpt": "Backlog conversion is expected to continue into next year.",
            "excerpt_sha256": text_sha256("Backlog conversion is expected to continue into next year."),
            "content_sha256": second_capture["snapshot_sha256"],
            "capture_receipt_sha256": second_capture["receipt_sha256"],
        })
        if peer:
            claim_b["evidence_role"] = "peer_analogy"
            claim_b["excerpt"] = "Peer companies reported competing capacity expansions."
            claim_b["excerpt_sha256"] = text_sha256(claim_b["excerpt"])
        data["evidence_claims"].extend([claim_a, claim_b])
        base_ids = [
            parameter_id
            for segment in data["segments"]
            for ids in segment["scenarios"]["base"]["driver_parameter_ids"].values()
            for parameter_id in ids
        ]
        data["growth_driver_tree"] = {
            "status": "modeled",
            "drivers": [{
                "driver_id": "demand_mechanism",
                "title": "Demand mechanism",
                "thesis": "Order intake converts into recognized revenue.",
                "causal_chain": ["orders", "deliveries", "recognized revenue"],
                "parameter_ids": base_ids,
                "segment_attribution": [
                    {"segment_name": "Segment A", "weight": 1.0},
                    {"segment_name": "Segment B", "weight": 1.0},
                ],
                "horizon": {"start_year": 2026, "end_year": 2027},
                "persistence": "multi_year_structural",
                "persistence_rationale": "Spans the horizon.",
                "evidence_nodes": [
                    {"evidence_id": "node_a", "evidence_type": "company_execution",
                     "inference_distance": "direct",
                     "conclusion": "Company execution supports the mechanism.",
                     "claim_ids": ["claim_direct_a"]},
                    {"evidence_id": "node_b",
                     "evidence_type": "peer_benchmark" if peer else "channel_check",
                     "inference_distance": "analogical" if peer else "direct",
                     "conclusion": "Comparable evidence supports the mechanism.",
                     "claim_ids": ["claim_direct_b"]},
                ],
                "leading_indicators": ["order intake"],
                "falsifiers": ["orders decline"],
                "counterevidence_status": "searched_none_found",
                "counterevidence_rationale": "Primary and independent sources checked.",
            }],
        }
        return data

    def test_two_independent_sources_triangulate(self) -> None:
        result = run_forecast(self._doc_with_driver(peer=False))
        driver = result["growth_driver_analysis"]["drivers"][0]
        self.assertEqual(driver["evidence_status"], "triangulated")

    def test_peer_analogy_does_not_automatically_triangulate(self) -> None:
        result = run_forecast(self._doc_with_driver(peer=True))
        driver = result["growth_driver_analysis"]["drivers"][0]
        self.assertEqual(driver["evidence_status"], "limited")
        limitations = " ".join(result["confidence"]["limitations"]).lower()
        self.assertIn("peer", limitations)
        # Revenue itself is unchanged by the evidence relabeling.
        baseline = run_forecast(self._doc_with_driver(peer=False))
        self.assertEqual(
            result["consolidated_forecast"]["base"]["annual_revenue"],
            baseline["consolidated_forecast"]["base"]["annual_revenue"],
        )


class CounterevidenceMixingTests(unittest.TestCase):
    def test_same_excerpt_cannot_support_and_contradict(self) -> None:
        data = forecast_document()
        excerpt = "Order intake grew 10 percent year over year."
        for claim_id, node_id in (("claim_mix_support", "node_support"), ("claim_mix_contra", "node_contra")):
            data["evidence_claims"].append({
                "claim_id": claim_id,
                "source_id": "filing",
                "target_type": "growth_driver",
                "target_id": node_id,
                "support_type": "rationale_support",
                "locator": "MD&A",
                "excerpt": excerpt,
                "excerpt_sha256": text_sha256(excerpt),
                "content_sha256": data["sources"][0]["capture"]["snapshot_sha256"],
                "capture_receipt_sha256": data["sources"][0]["capture"]["receipt_sha256"],
                "verification_status": "opened_and_checked",
                "verified_by": "input-semantics-test",
                "verified_date": data["as_of_date"],
            })
        base_ids = [
            parameter_id
            for segment in data["segments"]
            for ids in segment["scenarios"]["base"]["driver_parameter_ids"].values()
            for parameter_id in ids
        ]
        data["growth_driver_tree"] = {
            "status": "modeled",
            "drivers": [{
                "driver_id": "demand_mechanism",
                "title": "Demand mechanism",
                "thesis": "Order intake converts into recognized revenue.",
                "causal_chain": ["orders", "deliveries", "recognized revenue"],
                "parameter_ids": base_ids,
                "segment_attribution": [
                    {"segment_name": "Segment A", "weight": 1.0},
                    {"segment_name": "Segment B", "weight": 1.0},
                ],
                "horizon": {"start_year": 2026, "end_year": 2027},
                "persistence": "multi_year_structural",
                "persistence_rationale": "Spans the horizon.",
                "evidence_nodes": [
                    {"evidence_id": "node_support", "evidence_type": "company_execution",
                     "inference_distance": "direct", "conclusion": "Supports.",
                     "claim_ids": ["claim_mix_support"]},
                    {"evidence_id": "node_contra", "evidence_type": "company_execution",
                     "inference_distance": "contrary", "conclusion": "Contradicts.",
                     "claim_ids": ["claim_mix_contra"]},
                ],
                "leading_indicators": ["order intake"],
                "falsifiers": ["orders decline"],
                "counterevidence_status": "found",
                "counterevidence_rationale": "The same text cannot do both.",
            }],
        }
        with self.assertRaisesRegex(ForecastInputError, "same excerpt"):
            run_forecast(data)


class NarrativeBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        from research.input_evidence import bind_parameter_evidence

        self.bind = bind_parameter_evidence
        self.data = forecast_document()
        self.source = self.data["sources"][0]
        self.context = build_narrative_fixture(
            "We launched a new product and expanded overseas capacity.\nPipeline conversion remains strong.\n",
            ["We launched a new product and expanded overseas capacity."],
        )

    def test_narrative_span_binding_creates_consumable_source_and_claim(self) -> None:
        span_id = self.context["evidence_spans"][0]["span_id"]
        result = self.bind(
            _parameter(),
            evidence_bindings=[{
                "role": "mechanism_direction",
                "source_id": "narrative_transcript",
                "narrative_context": self.context,
                "span_id": span_id,
                "inference_distance": "direct",
            }],
            source=None,
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
        )
        source = result["sources"][0]
        self.assertEqual(source["source_id"], "narrative_transcript")
        self.assertEqual(source["published_date"], "2026-06-01")
        claim = result["claims"][0]
        self.assertEqual(claim["source_id"], "narrative_transcript")
        self.assertEqual(claim["content_sha256"],
                         self.context["source_ref"]["content_sha256"])
        self.assertEqual(claim["excerpt"],
                         "We launched a new product and expanded overseas capacity.")
        self.assertEqual(claim["locator"], self.context["evidence_spans"][0]["locator"])
        self.assertEqual(claim["target_id"], "a_growth_2026_base")
        self.assertIn(claim["claim_id"], result["parameter"]["claim_ids"])
        lineage = result["lineage"][0]
        self.assertEqual(lineage["narrative_span_id"], span_id)

    def test_unknown_span_id_is_rejected(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "span"):
            self.bind(
                _parameter(),
                evidence_bindings=[{
                    "role": "mechanism_direction",
                    "source_id": "narrative_transcript",
                    "narrative_context": self.context,
                    "span_id": SPAN_PREFIX + "f" * 64,
                }],
                source=None,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )

    def test_tampered_span_text_is_rejected(self) -> None:
        context = copy.deepcopy(self.context)
        context["evidence_spans"][0]["raw_text"] = "Tampered text that was never in the source."
        with self.assertRaisesRegex(ForecastInputError, "span_text_hash|hash"):
            self.bind(
                _parameter(),
                evidence_bindings=[{
                    "role": "mechanism_direction",
                    "source_id": "narrative_transcript",
                    "narrative_context": context,
                    "span_id": self.context["evidence_spans"][0]["span_id"],
                }],
                source=None,
                verified_by="input-semantics-test",
                verified_date=self.data["as_of_date"],
            )

    def test_unbound_narrative_file_is_not_a_parameter_dependency(self) -> None:
        """A claim attached without updating the parameter's dependency is
        rejected by the formal input contract: file existence is not consumption."""
        span_id = self.context["evidence_spans"][0]["span_id"]
        result = self.bind(
            _parameter(),
            evidence_bindings=[{
                "role": "mechanism_direction",
                "source_id": "narrative_transcript",
                "narrative_context": self.context,
                "span_id": span_id,
            }],
            source=None,
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
        )
        data = forecast_document()
        data["sources"].append(result["sources"][0])
        # Attach only the claim, not the parameter dependency.
        data["evidence_claims"].append(result["claims"][0])
        with self.assertRaisesRegex(ForecastInputError, "not registered on parameter"):
            run_forecast(data)

    def test_narrative_bound_driver_enters_the_formal_forecast(self) -> None:
        span_id = self.context["evidence_spans"][0]["span_id"]
        data = forecast_document()
        result = self.bind(
            _parameter(),
            evidence_bindings=[{
                "role": "mechanism_direction",
                "source_id": "narrative_transcript",
                "narrative_context": self.context,
                "span_id": span_id,
            }],
            source=None,
            verified_by="input-semantics-test",
            verified_date=data["as_of_date"],
        )
        data["sources"].append(result["sources"][0])
        data["evidence_claims"].append(result["claims"][0])
        # The same span also feeds the growth-driver node as its own claim.
        entry = result["lineage"][0]
        driver_claim = {
            "claim_id": "claim_narrative_driver",
            "source_id": entry["source_id"],
            "target_type": "growth_driver",
            "target_id": "narrative_node",
            "support_type": "rationale_support",
            "locator": result["sources"][0]["page_or_section"],
            "excerpt": entry["excerpt"],
            "excerpt_sha256": entry["excerpt_sha256"],
            "content_sha256": entry["content_sha256"],
            "capture_receipt_sha256": result["sources"][0]["capture"]["receipt_sha256"],
            "verification_status": "opened_and_checked",
            "verified_by": "input-semantics-test",
            "verified_date": data["as_of_date"],
        }
        data["evidence_claims"].append(driver_claim)
        parameter = result["parameter"]
        target = next(p for p in data["parameters"] if p["parameter_id"] == parameter["parameter_id"])
        target["claim_ids"] = list(dict.fromkeys(
            list(target.get("claim_ids", [])) + list(parameter["claim_ids"])
        ))
        target["source_ids"] = list(dict.fromkeys(
            list(target.get("source_ids", [])) + list(parameter["source_ids"])
        ))
        base_ids = [
            pid
            for segment in data["segments"]
            for ids in segment["scenarios"]["base"]["driver_parameter_ids"].values()
            for pid in ids
        ]
        data["growth_driver_tree"] = {
            "status": "modeled",
            "drivers": [{
                "driver_id": "demand_mechanism",
                "title": "Demand mechanism",
                "thesis": "Launch and capacity expansion convert into revenue.",
                "causal_chain": ["launch", "capacity", "recognized revenue"],
                "parameter_ids": base_ids,
                "segment_attribution": [
                    {"segment_name": "Segment A", "weight": 1.0},
                    {"segment_name": "Segment B", "weight": 1.0},
                ],
                "horizon": {"start_year": 2026, "end_year": 2027},
                "persistence": "multi_year_structural",
                "persistence_rationale": "Spans the horizon.",
                "evidence_nodes": [{
                    "evidence_id": "narrative_node",
                    "evidence_type": "management_statement",
                    "inference_distance": "direct",
                    "conclusion": "Management confirmed the launch and expansion.",
                    "claim_ids": ["claim_narrative_driver"],
                }],
                "leading_indicators": ["launch cadence"],
                "falsifiers": ["launch delayed"],
                "counterevidence_status": "searched_none_found",
                "counterevidence_rationale": "Primary transcript checked.",
            }],
        }
        outcome = run_forecast(data)
        driver = outcome["growth_driver_analysis"]["drivers"][0]
        self.assertIn("narrative_transcript", driver["evidence_source_ids"])
        self.assertEqual(driver["evidence_nodes"][0]["source_ids"], ["narrative_transcript"])


if __name__ == "__main__":
    unittest.main()
