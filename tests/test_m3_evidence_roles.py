"""M3-FLOW role tests: mechanism evidence must not be faked by history or financing.

Root cause: ``research/drivers.py`` excluded only peer-analogy claims, so two
sources/types of history-base or financing-background facts made a growth
driver ``triangulated``. Schema 3.9 opts into the role-aware rule:

* triangulation counts only nodes carrying at least one ``mechanism_direction``
  claim (an asserted operating mechanism of the same driver proposition);
* history_base / value_range / conversion_assumption / recognition_policy /
  counter_comparison / peer_analogy / counterevidence nodes stay disclosed but
  never count as future-mechanism support;
* mixed nodes keep their valid supports and all counterevidence rows;
* confidence must not rise because of a source category;
* schemas 3.7/3.8 keep the legacy peer-only exclusion so old published
  ``triangulated`` results are not silently re-judged.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from contracts.evidence import ForecastInputError  # noqa: E402
from revenue_core import (  # noqa: E402
    build_host_receipt,
    canonical_sha256,
    run_forecast,
    text_sha256,
    validate_document,
)
from test_recognition_bridge import forecast_document  # noqa: E402

PERIOD_EVIDENCE_SCHEMA_VERSION = "3.9"


def add_second_source(data: dict, source_id: str = "transcript") -> str:
    data["sources"].append(
        {
            "source_id": source_id,
            "source_type": "earnings_transcript",
            "title": "FY2026 results call",
            "publisher": "Test Exchange",
            "url": "https://example.test/transcript",
            "published_date": "2026-07-10",
            "accessed_date": data["as_of_date"],
            "page_or_section": "Prepared remarks",
        }
    )
    capture = {
        "capture_schema_version": "1.0",
        "capture_method": "browser_open",
        "tool_name": "test-browser",
        "tool_call_id": f"fixture-{source_id}",
        "captured_date": data["as_of_date"],
        "snapshot_sha256": "a" * 64,
        "content_treatment": "untrusted_data_only",
        "prompt_injection_status": "not_detected",
    }
    capture["host_receipt"] = build_host_receipt(
        issuer="fixture-host",
        environment="test",
        tool_name=capture["tool_name"],
        action="capture_open",
        event_sha256=text_sha256(f"fixture-open-{source_id}"),
        timestamp=capture["captured_date"],
    )
    capture["receipt_sha256"] = canonical_sha256(capture)
    data["sources"][-1]["capture"] = capture
    return source_id


def add_evidence_claim(
    data: dict, claim_id: str, source_id: str, evidence_id: str, role: str, excerpt: str
) -> str:
    data["evidence_claims"].append(
        {
            "claim_id": claim_id,
            "source_id": source_id,
            "target_type": "growth_driver",
            "target_id": evidence_id,
            "support_type": "rationale_support",
            "locator": "Prepared remarks",
            "excerpt": excerpt,
            "excerpt_sha256": text_sha256(excerpt),
            "content_sha256": "a" * 64,
            "verification_status": "opened_and_checked",
            "verified_by": "test-research-agent",
            "verified_date": data["as_of_date"],
            "capture_receipt_sha256": next(
                source["capture"]["receipt_sha256"]
                for source in data["sources"]
                if source["source_id"] == source_id
            ),
            "evidence_role": role,
        }
    )
    return claim_id


def role_document(schema_version: str, node_specs: list[dict]) -> dict:
    """Build a document whose Segment A driver carries the requested nodes.

    Each spec: {"roles": [claim roles], "source_id": ..., "evidence_type": ...,
    "inference_distance": "direct" (default)}. Claims are one per role.
    """
    data = forecast_document()
    add_second_source(data)
    driver = data["growth_driver_tree"]["drivers"][0]
    nodes = []
    for index, spec in enumerate(node_specs):
        evidence_id = f"role_node_{index}"
        claim_ids = [
            add_evidence_claim(
                data,
                f"claim_{evidence_id}_{role_index}",
                spec.get("source_id", "transcript"),
                evidence_id,
                role,
                f"Checked excerpt {evidence_id} {role} {role_index}.",
            )
            for role_index, role in enumerate(spec["roles"])
        ]
        nodes.append(
            {
                "evidence_id": evidence_id,
                "evidence_type": spec.get("evidence_type", f"evidence_kind_{index}"),
                "inference_distance": spec.get("inference_distance", "direct"),
                "conclusion": f"Node {index} conclusion.",
                "claim_ids": claim_ids,
            }
        )
    driver["evidence_nodes"] = nodes
    data["schema_version"] = schema_version
    return data


def segment_a_status(data: dict) -> tuple[str, list[dict], list[str]]:
    validated = validate_document(data)
    driver = validated["growth_driver_tree"]["drivers"][0]
    return (
        driver["evidence_status"],
        driver["evidence_nodes"],
        validated["growth_driver_tree"]["limitations"],
    )


class MechanismRoleUnitTests(unittest.TestCase):
    def test_history_and_financing_background_do_not_triangulate_in_3_9(self) -> None:
        # The HK-shaped counterexample: two sources, two evidence types, all
        # claims are historical or financing-background facts.
        data = role_document(
            PERIOD_EVIDENCE_SCHEMA_VERSION,
            [
                {"roles": ["history_base"], "source_id": "filing", "evidence_type": "company_execution"},
                {"roles": ["history_base"], "source_id": "transcript", "evidence_type": "operating_metrics"},
            ],
        )
        status, nodes, limitations = segment_a_status(data)
        self.assertEqual(status, "limited")
        self.assertEqual(len(nodes), 2)  # still disclosed, never deleted
        self.assertTrue(
            any("mechanism" in item.lower() for item in limitations),
            f"expected a mechanism limitation note, got {limitations}",
        )

    def test_same_structure_fails_for_a_second_company(self) -> None:
        data = role_document(
            PERIOD_EVIDENCE_SCHEMA_VERSION,
            [
                {"roles": ["history_base"], "source_id": "filing", "evidence_type": "company_execution"},
                {"roles": ["history_base"], "source_id": "transcript", "evidence_type": "operating_metrics"},
            ],
        )
        data["company_name"] = "Second Co Ltd"
        status, _, _ = segment_a_status(data)
        self.assertEqual(status, "limited")

    def test_true_same_proposition_mechanism_support_triangulates(self) -> None:
        data = role_document(
            PERIOD_EVIDENCE_SCHEMA_VERSION,
            [
                {"roles": ["mechanism_direction"], "source_id": "filing", "evidence_type": "company_execution"},
                {"roles": ["mechanism_direction"], "source_id": "transcript", "evidence_type": "operating_metrics"},
            ],
        )
        status, _, limitations = segment_a_status(data)
        self.assertEqual(status, "triangulated")
        # Segment B keeps its unroled fixture node and legitimately reports a
        # limitation; Segment A must carry none.
        self.assertFalse(
            any("fixture_driver_Segment_A" in item for item in limitations),
            f"unexpected limitation for a genuinely triangulated driver: {limitations}",
        )

    def test_peer_contrary_and_value_roles_stay_disclosed_but_uncounted(self) -> None:
        data = role_document(
            PERIOD_EVIDENCE_SCHEMA_VERSION,
            [
                {"roles": ["peer_analogy"], "source_id": "filing", "evidence_type": "company_execution"},
                {"roles": ["counter_comparison"], "source_id": "transcript", "evidence_type": "operating_metrics"},
            ],
        )
        status, nodes, _ = segment_a_status(data)
        self.assertEqual(status, "limited")
        self.assertEqual(len(nodes), 2)

    def test_mixed_node_keeps_valid_support_and_counterevidence_rows(self) -> None:
        data = role_document(
            PERIOD_EVIDENCE_SCHEMA_VERSION,
            [
                {
                    "roles": ["mechanism_direction", "history_base"],
                    "source_id": "filing",
                    "evidence_type": "company_execution",
                },
                {"roles": ["mechanism_direction"], "source_id": "transcript", "evidence_type": "operating_metrics"},
                {
                    "roles": ["counterevidence"],
                    "source_id": "transcript",
                    "evidence_type": "risk_disclosure",
                    "inference_distance": "contrary",
                },
            ],
        )
        data["growth_driver_tree"]["drivers"][0]["counterevidence_status"] = "found"
        status, nodes, _ = segment_a_status(data)
        self.assertEqual(status, "triangulated")  # mixed node still counts via its mechanism claim
        self.assertEqual(len(nodes), 3)  # the contrary row is preserved, not dropped

    def test_legacy_peer_only_exclusion_unchanged_for_old_schemas(self) -> None:
        # On 3.7/3.8 the historical rule stands: only peer analogies are
        # excluded, so two non-peer sources of history still triangulate and
        # previously published results are not re-judged.
        data = role_document(
            "3.7",
            [
                {"roles": ["history_base"], "source_id": "filing", "evidence_type": "company_execution"},
                {"roles": ["history_base"], "source_id": "transcript", "evidence_type": "operating_metrics"},
            ],
        )
        status, _, _ = segment_a_status(data)
        self.assertEqual(status, "triangulated")

    def test_confidence_does_not_rise_from_role_category(self) -> None:
        def score_for(roles: list[str]) -> float:
            data = role_document(
                PERIOD_EVIDENCE_SCHEMA_VERSION,
                [
                    {"roles": [roles[0]], "source_id": "filing", "evidence_type": "company_execution"},
                    {"roles": [roles[1]], "source_id": "transcript", "evidence_type": "operating_metrics"},
                ],
            )
            return run_forecast(data)["confidence"]["score"]

        history_score = score_for(["history_base", "history_base"])
        mechanism_score = score_for(["mechanism_direction", "mechanism_direction"])
        self.assertEqual(history_score, mechanism_score)

    def test_role_vocabulary_still_validated_on_claims(self) -> None:
        data = role_document(
            PERIOD_EVIDENCE_SCHEMA_VERSION,
            [{"roles": ["not_a_role"], "source_id": "filing"}],
        )
        with self.assertRaisesRegex(ForecastInputError, "evidence_role"):
            validate_document(data)


if __name__ == "__main__":
    unittest.main()
