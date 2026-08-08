from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import (  # noqa: E402
    ENGINE_VERSION,
    ForecastInputError,
    build_workflow_compliance_receipt,
    calculate_cagr,
    canonical_sha256,
    run_forecast,
)
from revenue_report import render_markdown, validate_forecast_output  # noqa: E402
from test_management_targets import add_target  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def _republish(result: dict) -> None:
    """Recompute the publication receipt and result hash after mutating a result.

    Adversarial tests mutate a published result and then recompute every hash
    the validator re-checks — including the verification context — so the
    artifact stays internally self-consistent.  This isolates the semantic gap
    under test from plain hash tampering: even a fully rehashed artifact with a
    valid-looking verification context must be rejected by the strong validator.
    """
    from revenue_publication import (
        VerificationContext,
        build_publication_receipt,
        expected_publication_gates,
    )

    result["publication_receipt"] = build_publication_receipt(
        result,
        VerificationContext(
            result["input_sha256"],
            expected_publication_gates(result),
            ENGINE_VERSION,
        ),
    )
    result["result_sha256"] = canonical_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"}
    )


class OutputReportTests(unittest.TestCase):
    def test_forged_headwind_is_rejected_after_recomputation(self) -> None:
        result = run_forecast(forecast_document())
        self.assertEqual(result["growth_driver_analysis"]["headwinds"], [])
        result["growth_driver_analysis"]["headwinds"].append(
            {
                "driver_id": "forged_headwind",
                "title": "Forged headwind",
                "thesis": "Not backed by any driver tree root.",
                "estimated_base_terminal_increment": -10.0,
                "share_of_positive_driver_increment": 0.0,
                "segment_names": ["Segment A"],
                "causal_chain": ["x", "y"],
                "evidence_status": "limited",
                "leading_indicators": ["z"],
                "falsifiers": ["w"],
                "rank": 1,
            }
        )
        _republish(result)
        with self.assertRaisesRegex(
            ForecastInputError, "growth driver analysis recomputation mismatch"
        ):
            validate_forecast_output(result, forecast_document())

    def test_valid_output_and_markdown(self) -> None:
        result = run_forecast(forecast_document())
        validate_forecast_output(result)
        markdown = render_markdown(result)
        self.assertIn("## 核心营收结论", markdown)
        self.assertIn("## 未来收入主要驱动力", markdown)
        self.assertIn("## 收入增长驱动树", markdown)
        self.assertIn("## 九维研究覆盖", markdown)
        self.assertIn("## 三情景经营驱动", markdown)
        self.assertIn("## 分部驱动与收入确认", markdown)
        self.assertIn("## 参数—证据claim映射", markdown)
        self.assertIn("## 参数来源", markdown)

    def test_tampered_research_coverage_counts_are_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["research_coverage"]["counts"]["modeled_driver"] += 1
        with self.assertRaisesRegex(ForecastInputError, "counts mismatch"):
            validate_forecast_output(result)

    def test_tampered_cagr_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["consolidated_forecast"]["base"]["cagr"] = 0.99
        with self.assertRaisesRegex(ForecastInputError, "CAGR mismatch"):
            validate_forecast_output(result)

    def test_tampered_bridge_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["consolidated_forecast"]["base"]["annual_revenue"]["2026"] += 1
        with self.assertRaisesRegex(ForecastInputError, "mismatch"):
            validate_forecast_output(result)

    def test_prohibited_non_revenue_key_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["valuation"] = {"multiple": 10}
        with self.assertRaisesRegex(ForecastInputError, "prohibited"):
            validate_forecast_output(result)

    def test_probability_tampering_is_rejected(self) -> None:
        data = forecast_document()
        data["scenario_probabilities"] = {"low": 0.25, "base": 0.5, "high": 0.25}
        data["probability_rationale"] = "test"
        result = run_forecast(data)
        tampered = copy.deepcopy(result)
        tampered["probability_weighted_forecast"]["annual_revenue"]["2026"] += 1
        with self.assertRaisesRegex(ForecastInputError, "probability-weighted"):
            validate_forecast_output(tampered)

    def test_parameter_trace_custom_key_is_not_prohibited(self) -> None:
        # A custom key is legitimate when it comes from the input itself (the
        # trace mirrors the validated parameters); only out-of-band injection
        # is rejected (R6.2 consistency gate).
        data = forecast_document()
        data["parameters"][0]["profit"] = "source vocabulary only"
        result = run_forecast(copy.deepcopy(data))
        validate_forecast_output(result)

    def test_tampered_segment_recognition_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["segments"][0]["scenarios"]["base"]["recognized_revenue"]["2026"] = 9999
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        with self.assertRaisesRegex(ForecastInputError, "recognized revenue mismatch"):
            validate_forecast_output(result)

    def test_tampered_annual_growth_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["consolidated_forecast"]["base"]["annual_growth"]["2026"] = 123
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        with self.assertRaisesRegex(ForecastInputError, "annual growth mismatch"):
            validate_forecast_output(result)

    def test_tampered_growth_driver_impact_is_rejected_even_after_rehash(self) -> None:
        result = run_forecast(forecast_document())
        result["growth_driver_analysis"]["drivers"][0][
            "estimated_base_terminal_increment"
        ] += 1
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        with self.assertRaisesRegex(
            ForecastInputError, "growth driver analysis recomputation mismatch"
        ):
            validate_forecast_output(result)

    def test_missing_workflow_receipt_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        del result["workflow_compliance_receipt"]
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        with self.assertRaisesRegex(ForecastInputError, "workflow_compliance_receipt"):
            validate_forecast_output(result)

    def test_tampered_workflow_receipt_is_rejected_even_after_rehash(self) -> None:
        result = run_forecast(forecast_document())
        result["workflow_compliance_receipt"]["freeform_formal_output_allowed"] = True
        result["workflow_compliance_receipt"]["receipt_sha256"] = canonical_sha256(
            {
                key: value
                for key, value in result["workflow_compliance_receipt"].items()
                if key != "receipt_sha256"
            }
        )
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        with self.assertRaisesRegex(
            ForecastInputError, "workflow compliance receipt mismatch"
        ):
            validate_forecast_output(result)

    # The four tests below are adversarial RED tests for Phase 1 of task_plan.md.
    # They mutate a published result, recompute every derived field that the
    # validator re-checks (so the artifact stays internally self-consistent),
    # recompute result_sha256, and then expect validate_forecast_output to
    # reject the forgery. They currently FAIL because validate_forecast_output
    # trusts the forged field instead of re-deriving it from frozen input. The
    # companion positive test pins the intended non-regression behavior.

    def test_rehashed_invalid_probability_contract_is_rejected(self) -> None:
        # Input validation rejects probabilities that do not sum to 1, but the
        # output validator only re-checks the weighted arithmetic. A rehashed
        # artifact with illegal probabilities (sum == 2 here) plus a
        # self-consistent recomputed weighted path must be rejected; today it is
        # accepted (RED).
        data = forecast_document()
        data["scenario_probabilities"] = {"low": 0.25, "base": 0.5, "high": 0.25}
        data["probability_rationale"] = "valid calibration"
        result = run_forecast(data)
        forged = copy.deepcopy(result)
        forged_probabilities = {"low": 2.0, "base": 0.0, "high": 0.0}
        forged["scenario_probabilities"] = forged_probabilities
        consolidated = forged["consolidated_forecast"]
        years = list(map(str, forged["forecast_years"]))
        weighted = forged["probability_weighted_forecast"]
        for year in years:
            weighted["annual_revenue"][year] = sum(
                forged_probabilities[scenario]
                * consolidated[scenario]["annual_revenue"][year]
                for scenario in ("low", "base", "high")
            )
        terminal = float(weighted["annual_revenue"][years[-1]])
        weighted["terminal_revenue"] = terminal
        weighted["expected_terminal_implied_cagr"] = calculate_cagr(
            float(forged["base_revenue"]), terminal, len(years)
        )
        weighted["incremental_revenue"] = terminal - float(forged["base_revenue"])
        _republish(forged)
        with self.assertRaisesRegex(ForecastInputError, "probabilities must sum to 1"):
            validate_forecast_output(forged)

    def test_rehashed_forged_target_comparison_is_rejected(self) -> None:
        # The output validator recomputes modeled_value and attainment_ratio
        # but only requires meets_target to be True; it never re-derives
        # meets_target from the comparison operator and tolerance. A rehashed
        # target that lifts comparison_value far above actual delivery (genuinely
        # unmet) yet keeps meets_target=True must be rejected; today it is
        # accepted (RED).
        result = run_forecast(add_target(forecast_document()))
        forged = copy.deepcopy(result)
        target = forged["management_target_coverage"]["targets"][0]
        comparison = target["scenario_comparison"]["high"]
        modeled_value = float(comparison["modeled_value"])
        forged_target_value = modeled_value * 10.0
        target["comparison_value"] = forged_target_value
        comparison["target_value"] = forged_target_value
        comparison["attainment_ratio"] = modeled_value / forged_target_value
        comparison["meets_target"] = True
        _republish(forged)
        with self.assertRaisesRegex(ForecastInputError, "management target"):
            validate_forecast_output(forged)

    def test_rehashed_forged_sensitivity_terminals_are_rejected(self) -> None:
        # The output validator recomputes only the derived impact fields from
        # the stored terminals; it never re-runs the shock against the model.
        # Replacing the terminals with arbitrary values and recomputing those
        # derived fields must be rejected; today it is accepted (RED).
        data = forecast_document()
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"][
            "revenue"
        ][1]
        data["sensitivity_tests"] = [
            {
                "name": "Core terminal revenue",
                "parameter_id": parameter_id,
                "shock_type": "percent",
                "shock_value": 0.1,
            }
        ]
        result = run_forecast(data)
        forged = copy.deepcopy(result)
        sensitivity = forged["sensitivities"][0]
        baseline = float(sensitivity["baseline_terminal_revenue"])
        sensitivity["down_terminal_revenue"] = 1.0
        sensitivity["up_terminal_revenue"] = baseline * 100.0
        impact = max(abs(1.0 - baseline), abs(baseline * 100.0 - baseline))
        sensitivity["max_absolute_terminal_impact"] = impact
        sensitivity["max_relative_terminal_impact"] = impact / baseline
        _republish(forged)
        with self.assertRaisesRegex(ForecastInputError, "sensitivity"):
            validate_forecast_output(forged, data)

    def test_nested_structured_valuation_field_is_rejected(self) -> None:
        # The prohibited-field scan (_walk_keys) only walks a fixed allowlist of
        # top-level blocks; parameter_trace is not among them. Embedding
        # structured investment fields (valuation/pe/dcf) inside a parameter
        # trace node and rehashing must be rejected; today it is accepted (RED).
        result = run_forecast(forecast_document())
        forged = copy.deepcopy(result)
        forged["parameter_trace"][0]["valuation"] = {
            "pe": 15.0,
            "dcf": {"fair_value": 100.0},
        }
        _republish(forged)
        # Rejected either by the trace/input consistency gate (R6.2) or the
        # prohibited-field scan — the injection must not survive either way.
        with self.assertRaisesRegex(
            ForecastInputError, "parameter_trace must match|prohibited"
        ):
            validate_forecast_output(forged)

    def test_plain_text_investment_vocabulary_in_source_is_allowed(self) -> None:
        # Positive guard rail: plain-text occurrences of investment vocabulary
        # in source titles are legitimate evidence wording, not structured
        # investment conclusions, and must never be false-positived. This pins
        # the intended behavior so the Phase 4 field-boundary fix stays precise.
        result = run_forecast(forecast_document())
        result["sources"][0]["title"] = (
            "Annual report references segment profit and an internal valuation study."
        )
        result["workflow_compliance_receipt"] = build_workflow_compliance_receipt(
            result["input_sha256"],
            result["sources"],
            result["evidence_claims"],
            result["parameter_trace"],
            result.get("data_gaps", []),
        )
        _republish(result)
        validate_forecast_output(result)

    def test_build_publication_receipt_requires_verification_context(self) -> None:
        # Phase 6 A1 RED: the public builder must fail closed when no strong
        # verification context is supplied.  A forged artifact can no longer
        # self-issue a "pass" receipt by recomputing hashes alone.
        from revenue_publication import build_publication_receipt

        result = run_forecast(forecast_document())
        with self.assertRaisesRegex(TypeError, "VerificationContext"):
            build_publication_receipt(result)

    def test_no_input_weak_path_rejects_forged_sensitivity(self) -> None:
        # Phase 6 A1 RED (F-02): validate_forecast_output(forged) with NO explicit
        # input must reject forged sensitivity terminals, because the published
        # artifact now carries a self-contained input_document that the strong
        # path re-runs.  This is the exact exploit the audit reproduced.
        data = forecast_document()
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"][
            "revenue"
        ][1]
        data["sensitivity_tests"] = [
            {
                "name": "Core terminal revenue",
                "parameter_id": parameter_id,
                "shock_type": "percent",
                "shock_value": 0.1,
            }
        ]
        result = run_forecast(data)
        forged = copy.deepcopy(result)
        sensitivity = forged["sensitivities"][0]
        baseline = float(sensitivity["baseline_terminal_revenue"])
        sensitivity["down_terminal_revenue"] = 1.0
        sensitivity["up_terminal_revenue"] = baseline * 100.0
        impact = max(abs(1.0 - baseline), abs(baseline * 100.0 - baseline))
        sensitivity["max_absolute_terminal_impact"] = impact
        sensitivity["max_relative_terminal_impact"] = impact / baseline
        _republish(forged)
        with self.assertRaisesRegex(
            ForecastInputError, "sensitivity down terminal recomputation mismatch"
        ):
            validate_forecast_output(forged)

    def test_strong_entry_requires_input(self) -> None:
        # Phase 6 A1 RED: the formal-only entry must reject a None input.
        from revenue_report import validate_published_forecast

        result = run_forecast(forecast_document())
        with self.assertRaisesRegex(TypeError, "original input"):
            validate_published_forecast(result, None)

    def test_swapped_embedded_input_is_rejected(self) -> None:
        # R1.1 RED (N-01 D1): swapping the embedded input_document for a
        # different valid input while keeping the original input_sha256 must
        # be rejected — the embedded document must hash to the claimed anchor
        # (binding invariant).  Previously ACCEPTED.
        data = forecast_document()
        data["sensitivity_tests"] = [
            {
                "name": "Core terminal revenue",
                "parameter_id": data["segments"][0]["scenarios"]["base"][
                    "driver_parameter_ids"
                ]["revenue"][1],
                "shock_type": "percent",
                "shock_value": 0.1,
            }
        ]
        legit = run_forecast(copy.deepcopy(data))
        forged = copy.deepcopy(legit)
        attacker_input = copy.deepcopy(data)
        attacker_input["forecast_version"] = "attacker-version"
        forged["input_document"] = attacker_input
        _republish(forged)
        with self.assertRaisesRegex(ForecastInputError, "input"):
            validate_forecast_output(forged)

    def test_inflated_numbers_anchored_to_legit_hash_are_rejected(self) -> None:
        # R1.1 RED (N-01 D2): re-running the engine on inflated assumption /
        # stress parameters and anchoring the forged result to a legitimate
        # input hash must be rejected — the actual validated input document
        # must hash to input_sha256 (binding invariant).  Previously ACCEPTED.
        data = forecast_document()
        legit = run_forecast(copy.deepcopy(data))
        attacker_input = copy.deepcopy(data)
        changed = 0
        for parameter in attacker_input["parameters"]:
            if isinstance(parameter.get("value"), (int, float)) and parameter.get(
                "kind"
            ) in {"analyst_assumption", "scenario_stress"}:
                parameter["value"] = float(parameter["value"]) * 1.5
                changed += 1
        self.assertGreater(changed, 0)
        forged = run_forecast(attacker_input)
        self.assertNotEqual(
            forged["consolidated_forecast"]["base"]["terminal_revenue"],
            legit["consolidated_forecast"]["base"]["terminal_revenue"],
        )
        forged["input_sha256"] = legit["input_sha256"]
        forged["workflow_compliance_receipt"]["input_sha256"] = legit["input_sha256"]
        forged["workflow_compliance_receipt"]["receipt_sha256"] = canonical_sha256(
            {
                key: value
                for key, value in forged["workflow_compliance_receipt"].items()
                if key != "receipt_sha256"
            }
        )
        _republish(forged)
        with self.assertRaises(ForecastInputError):
            validate_forecast_output(forged)


if __name__ == "__main__":
    unittest.main()
