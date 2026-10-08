"""R6-RF-INPUT E2E: real build -> lint -> hash sync -> engine -> report ->
snapshot -> registry on an isolated test root, plus the two evidence variants
(supporting-source swap, peer relabel) proving that real consumption changes
while revenue does not.

Everything runs offline: the NarrativeRef bundle is a fully resigned fixture of
the published wire contract (no network, no model calls).
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RF_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RF_ROOT / "scripts"))
sys.path.insert(0, str(RF_ROOT / "tests"))

from revenue_core import canonical_sha256, text_sha256  # noqa: E402
from contracts.evidence import build_host_receipt  # noqa: E402
from research.input_evidence import bind_parameter_evidence  # noqa: E402
from research.input_quantities import build_sensitivity_test  # noqa: E402
from research.input_targets import build_management_target  # noqa: E402
from test_evidence_input_lineage import build_narrative_fixture  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

SPAN_TEXT = "We launched a new product and expanded overseas capacity."
SPAN_TEXT_VARIANT = "The new platform reached record engagement and bookings conversion improved."


def _second_source(data: dict) -> dict:
    source = copy.deepcopy(data["sources"][0])
    source["source_id"] = "presentation"
    source["url"] = "https://www.sec.gov/Archives/edgar/data/1/presentation.htm"
    source["title"] = "Investor presentation"
    capture = dict(source["capture"])
    capture["tool_call_id"] = "fixture-presentation"
    host = build_host_receipt(
        issuer=capture["host_receipt"]["issuer"],
        environment=capture["host_receipt"]["environment"],
        tool_name=capture["tool_name"],
        action=capture["host_receipt"]["action"],
        event_sha256=text_sha256("fixture-presentation"),
        timestamp=capture["host_receipt"]["timestamp"],
    )
    capture["host_receipt"] = host
    capture.pop("receipt_sha256", None)
    capture["receipt_sha256"] = canonical_sha256(capture)
    source["capture"] = capture
    return source


def _driver_claim(data: dict, claim_id: str, source_id: str, capture: dict,
                  node_id: str, excerpt: str, role: str | None = None) -> dict:
    claim = {
        "claim_id": claim_id,
        "source_id": source_id,
        "target_type": "growth_driver",
        "target_id": node_id,
        "support_type": "rationale_support",
        "locator": "MD&A outlook",
        "excerpt": excerpt,
        "excerpt_sha256": text_sha256(excerpt),
        "content_sha256": capture["snapshot_sha256"],
        "capture_receipt_sha256": capture["receipt_sha256"],
        "verification_status": "opened_and_checked",
        "verified_by": "input-semantics-e2e",
        "verified_date": data["as_of_date"],
    }
    if role is not None:
        claim["evidence_role"] = role
    return claim


def build_e2e_document(*, peer: bool = False, span_text: str = SPAN_TEXT) -> dict:
    """Assemble a formal input that consumes all three new builders."""
    data = forecast_document()
    presentation = _second_source(data)
    data["sources"].append(presentation)

    excerpt_a = "Company order intake grew on new customer ramps this year."
    excerpt_b = (
        "Peer companies reported competing capacity expansions."
        if peer
        else "Backlog conversion is expected to continue into next year."
    )
    claim_a = _driver_claim(
        data, "claim_direct_a", "filing", data["sources"][0]["capture"],
        "node_a", excerpt_a,
    )
    claim_b = _driver_claim(
        data, "claim_direct_b", "presentation", presentation["capture"],
        "node_b", excerpt_b,
        role="peer_analogy" if peer else None,
    )

    # NarrativeRef span -> parameter dependency + driver-level claim.
    context = build_narrative_fixture(span_text + "\n", [span_text])
    span_id = context["evidence_spans"][0]["span_id"]
    parameter = next(
        p for p in data["parameters"] if p["parameter_id"] == "a_growth_2026_base"
    )
    bound = bind_parameter_evidence(
        parameter,
        evidence_bindings=[{
            "role": "mechanism_direction",
            "source_id": "narrative_transcript",
            "narrative_context": context,
            "span_id": span_id,
            "inference_distance": "direct",
        }],
        source=None,
        verified_by="input-semantics-e2e",
        verified_date=data["as_of_date"],
    )
    data["sources"].append(bound["sources"][0])
    entry = bound["lineage"][0]
    driver_claim = {
        "claim_id": "claim_narrative_driver",
        "source_id": entry["source_id"],
        "target_type": "growth_driver",
        "target_id": "node_narrative",
        "support_type": "rationale_support",
        "locator": bound["sources"][0]["page_or_section"],
        "excerpt": entry["excerpt"],
        "excerpt_sha256": entry["excerpt_sha256"],
        "content_sha256": entry["content_sha256"],
        "capture_receipt_sha256": bound["sources"][0]["capture"]["receipt_sha256"],
        "verification_status": "opened_and_checked",
        "verified_by": "input-semantics-e2e",
        "verified_date": data["as_of_date"],
    }
    data["evidence_claims"].extend([claim_a, claim_b, bound["claims"][0], driver_claim])
    for doc_parameter in data["parameters"]:
        if doc_parameter["parameter_id"] == parameter["parameter_id"]:
            doc_parameter["claim_ids"] = list(dict.fromkeys(
                list(doc_parameter.get("claim_ids", [])) + list(bound["parameter"]["claim_ids"])
            ))
            doc_parameter["source_ids"] = list(dict.fromkeys(
                list(doc_parameter.get("source_ids", [])) + list(bound["parameter"]["source_ids"])
            ))

    base_ids = [
        pid
        for segment in data["segments"]
        for ids in segment["scenarios"]["base"]["driver_parameter_ids"].values()
        for pid in ids
    ]
    evidence_nodes = [
        {"evidence_id": "node_a", "evidence_type": "company_execution",
         "inference_distance": "direct", "conclusion": "Company execution supports the mechanism.",
         "claim_ids": ["claim_direct_a"]},
        {"evidence_id": "node_b",
         "evidence_type": "peer_benchmark" if peer else "channel_check",
         "inference_distance": "analogical" if peer else "direct",
         "conclusion": "Comparable evidence supports the mechanism.",
         "claim_ids": ["claim_direct_b"]},
    ]
    if not peer:
        # The peer variant reproduces the HK failure shape: the second core
        # evidence is a peer benchmark, so no company triangulation remains.
        evidence_nodes.append(
            {"evidence_id": "node_narrative", "evidence_type": "management_statement",
             "inference_distance": "direct", "conclusion": "Management confirmed launches and expansion.",
             "claim_ids": ["claim_narrative_driver"]}
        )
    data["growth_driver_tree"] = {
        "status": "modeled",
        "drivers": [{
            "driver_id": "demand_mechanism",
            "title": "Demand mechanism",
            "thesis": "Order intake and launches convert into recognized revenue.",
            "causal_chain": ["orders", "deliveries", "recognized revenue"],
            "parameter_ids": base_ids,
            "segment_attribution": [
                {"segment_name": "Segment A", "weight": 1.0},
                {"segment_name": "Segment B", "weight": 1.0},
            ],
            "horizon": {"start_year": 2026, "end_year": 2027},
            "persistence": "multi_year_structural",
            "persistence_rationale": "Spans the forecast horizon.",
            "evidence_nodes": evidence_nodes,
            "leading_indicators": ["order intake", "launch cadence"],
            "falsifiers": ["orders decline"],
            "counterevidence_status": "searched_none_found",
            "counterevidence_rationale": "Primary and independent sources checked.",
        }],
    }

    quarterly = build_management_target(
        "Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year.",
        target_id="t_quarterly",
        metric_name="revenue",
        metric_definition="recognized revenue",
        source_id="filing",
        locator="Results release, Q2 section",
        excerpt="Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year.",
        verified_by="input-semantics-e2e",
        verified_date=data["as_of_date"],
        raw_unit="USD million",
        raw_currency="USD",
        raw_scale="million",
        period_label="Q2 FY2026",
        measurement_basis="quarterly_period",
        target_quarter="Q2",
        commitment_strength="guidance",
        rationale="Quarterly actual disclosed in the results release.",
        measurement_rationale="Source states a single quarter; no annual basis is disclosed.",
        perimeter_notes="Company recognized revenue; quarterly basis.",
        raw_value=40.0,
        source_capture=data["sources"][0]["capture"],
    )
    data["management_targets"].append(quarterly["target"])
    data["evidence_claims"].extend(quarterly["claims"])
    data["management_communication_coverage"][0]["material_revenue_target_ids"] = [
        "t_quarterly"
    ]

    data["sensitivity_tests"] = [
        build_sensitivity_test(
            parameter_id="0_base_2026", value=5, input_unit="percent",
            shock_semantics="multiplicative", name="seg0_5pct",
        )
    ]
    return data


class InputSemanticsE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp(prefix="rf-inputsem-e2e-"))
        cls.registry = cls.root / "publications.jsonl"
        cls.base_doc = build_e2e_document()
        cls.peer_doc = build_e2e_document(peer=True)
        cls.variant_doc = build_e2e_document(span_text=SPAN_TEXT_VARIANT)
        cls.inputs = {}
        for label, doc in (
            ("base", cls.base_doc), ("peer", cls.peer_doc), ("variant", cls.variant_doc),
        ):
            path = cls.root / f"input_{label}.json"
            path.write_text(
                json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            cls.inputs[label] = path
        cls.forecasts: dict[str, dict] = {}
        for label in ("base", "peer", "variant"):
            cls.forecasts[label] = cls._run_chain(label)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.root, ignore_errors=True)

    @classmethod
    def _env(cls) -> dict:
        env = dict(os.environ)
        env["REVENUE_PUBLICATION_REGISTRY"] = str(cls.registry)
        env["PYTHONIOENCODING"] = "utf-8"
        return env

    @classmethod
    def _run(cls, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-X", "utf8", *args],
            cwd=str(cls.root), env=cls._env(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, check=False,
        )

    @classmethod
    def _run_chain(cls, label: str) -> dict:
        input_path = cls.inputs[label]
        # 1. Static collect-all lint must be clean.
        lint = cls._run(str(RF_ROOT / "scripts/lint_input.py"), str(input_path))
        assert lint.returncode == 0, lint.stderr.decode("utf-8", errors="replace")[-2000:]
        # 2. Hash sync is a no-op drift check (fixtures already carry hashes).
        fix = cls._run(str(RF_ROOT / "scripts/fix_hashes.py"), str(input_path), "--check")
        assert fix.returncode == 0, fix.stderr.decode("utf-8", errors="replace")[-2000:]
        # 3. Real engine run: forecast JSON + Markdown report.
        output = cls.root / f"forecast_{label}.json"
        markdown = cls.root / f"forecast_{label}.md"
        run = cls._run(
            str(RF_ROOT / "scripts/revenue_forecast.py"), str(input_path),
            "--output", str(output), "--markdown", str(markdown),
        )
        assert run.returncode == 0, (
            run.stderr.decode("utf-8", errors="replace")[-3000:]
        )
        # 4. Immutable snapshot.
        snapshot = cls.root / f"snapshot_{label}.json"
        snap = cls._run(
            str(RF_ROOT / "scripts/revenue_backtest.py"), "create", str(input_path),
            "--version", f"inputsem-{label}-1", "--output", str(snapshot),
        )
        assert snap.returncode == 0, snap.stderr.decode("utf-8", errors="replace")[-2000:]
        return {
            "forecast": json.loads(output.read_text(encoding="utf-8")),
            "markdown": markdown.read_text(encoding="utf-8"),
            "snapshot": json.loads(snapshot.read_text(encoding="utf-8")),
        }

    # -- the full chain ----------------------------------------------------

    def test_forecast_validates_and_registers_in_the_isolated_registry(self) -> None:
        forecast = self.forecasts["base"]["forecast"]
        self.assertEqual(forecast["input_sha256"], canonical_sha256(self.base_doc))
        self.assertIn("publication_receipt", forecast)
        self.assertGreaterEqual(forecast["confidence"]["score"], 0)
        lookup = self._run(
            str(RF_ROOT / "scripts/publication_registry.py"), "lookup",
            "--input-sha", forecast["input_sha256"],
        )
        self.assertEqual(lookup.returncode, 0, lookup.stderr.decode("utf-8", errors="replace"))
        audit = self._run(str(RF_ROOT / "scripts/publication_registry.py"), "audit")
        self.assertEqual(audit.returncode, 0, audit.stderr.decode("utf-8", errors="replace"))

    def test_quarterly_target_stays_unmodeled_with_named_reason(self) -> None:
        forecast = self.forecasts["base"]["forecast"]
        target = forecast["management_target_coverage"]["targets"][0]
        self.assertEqual(target["measurement_basis"], "quarterly_period")
        self.assertEqual(target["treatment"], "unmodeled_data_gap")
        gaps = " ".join(forecast["data_gaps"])
        self.assertIn("management_target:t_quarterly", gaps)
        self.assertIn("quarterly", gaps.lower())
        self.assertIn("Q2", self.forecasts["base"]["markdown"])

    def test_unit_converted_sensitivity_flows_through_the_engine(self) -> None:
        forecast = self.forecasts["base"]["forecast"]
        sensitivity = forecast["sensitivities"][0]
        self.assertEqual(sensitivity["shock_type"], "percent")
        self.assertAlmostEqual(sensitivity["shock_value"], 0.05, places=12)
        self.assertAlmostEqual(sensitivity["requested_values"]["down"], 104.5, places=9)
        self.assertAlmostEqual(sensitivity["requested_values"]["up"], 115.5, places=9)
        self.assertEqual(sensitivity["input_quantity"]["input_unit"], "percent")

    def test_narrative_span_is_consumed_by_the_formal_forecast(self) -> None:
        forecast = self.forecasts["base"]["forecast"]
        driver = forecast["growth_driver_analysis"]["drivers"][0]
        self.assertIn("narrative_transcript", driver["evidence_source_ids"])
        node = next(
            n for n in driver["evidence_nodes"] if n["evidence_id"] == "node_narrative"
        )
        self.assertEqual(node["source_ids"], ["narrative_transcript"])

    # -- the two variants: consumption changes, revenue does not -----------

    def test_peer_variant_keeps_revenue_but_flips_evidence_status(self) -> None:
        base, peer = self.forecasts["base"]["forecast"], self.forecasts["peer"]["forecast"]
        self.assertEqual(
            peer["consolidated_forecast"]["base"]["annual_revenue"],
            base["consolidated_forecast"]["base"]["annual_revenue"],
        )
        driver_base = base["growth_driver_analysis"]["drivers"][0]
        driver_peer = peer["growth_driver_analysis"]["drivers"][0]
        self.assertEqual(driver_base["evidence_status"], "triangulated")
        self.assertEqual(driver_peer["evidence_status"], "limited")
        peer_limitations = " ".join(peer["confidence"]["limitations"]).lower()
        self.assertIn("peer", peer_limitations)
        base_limitations = " ".join(base["confidence"]["limitations"]).lower()
        self.assertNotIn("peer-analogy evidence is disclosed", base_limitations)

    def test_supporting_source_variant_changes_lineage_not_revenue(self) -> None:
        base, variant = self.forecasts["base"]["forecast"], self.forecasts["variant"]["forecast"]
        self.assertNotEqual(
            variant["input_sha256"], base["input_sha256"],
            "a different supporting span must change the registered input anchor",
        )
        self.assertEqual(
            variant["consolidated_forecast"]["base"]["annual_revenue"],
            base["consolidated_forecast"]["base"]["annual_revenue"],
        )
        driver_variant = variant["growth_driver_analysis"]["drivers"][0]
        self.assertIn("narrative_transcript", driver_variant["evidence_source_ids"])
        claim_base = next(
            c for c in self.base_doc["evidence_claims"] if c["claim_id"] == "claim_narrative_driver"
        )
        claim_variant = next(
            c for c in self.variant_doc["evidence_claims"] if c["claim_id"] == "claim_narrative_driver"
        )
        self.assertNotEqual(
            claim_base["excerpt_sha256"], claim_variant["excerpt_sha256"]
        )
        lookup = self._run(
            str(RF_ROOT / "scripts/publication_registry.py"), "lookup",
            "--input-sha", variant["input_sha256"],
        )
        self.assertEqual(lookup.returncode, 0, lookup.stderr.decode("utf-8", errors="replace"))

    def test_unknown_publication_date_is_refused_by_name(self) -> None:
        data = forecast_document()
        context = build_narrative_fixture(SPAN_TEXT + "\n", [SPAN_TEXT])
        context["manifest"]["published_date"] = None
        parameter = next(
            p for p in data["parameters"] if p["parameter_id"] == "a_growth_2026_base"
        )
        from revenue_core import ForecastInputError

        with self.assertRaisesRegex(
            ForecastInputError, "narrative_source_publication_unknown"
        ):
            bind_parameter_evidence(
                parameter,
                evidence_bindings=[{
                    "role": "mechanism_direction",
                    "source_id": "narrative_transcript",
                    "narrative_context": context,
                    "span_id": context["evidence_spans"][0]["span_id"],
                }],
                source=None,
                verified_by="input-semantics-e2e",
                verified_date=data["as_of_date"],
            )

    def test_isolated_root_contains_no_stray_outputs(self) -> None:
        # Only the artifacts this chain wrote; no cache dirs or registry elsewhere.
        names = sorted(p.name for p in self.root.iterdir())
        for name in names:
            self.assertFalse(name.startswith("."), name)
        self.assertEqual(len([n for n in names if n.startswith("forecast_")]), 6)


if __name__ == "__main__":
    unittest.main()
