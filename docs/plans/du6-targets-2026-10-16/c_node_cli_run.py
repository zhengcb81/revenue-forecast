"""DU6 C-node: synthetic models through the real public CLI.

Builds small synthetic inputs (no company originals, no supplier calls), runs
them through builder -> engine -> published validation -> the public CLI in
validate-only and formal JSON/Markdown modes, records every negative control's
real exit code, and writes one receipt. The publication registry is the owned
temp file named by ``REVENUE_PUBLICATION_REGISTRY``; the repo default registry
is never touched.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

# The publication registry is owned by this run: set it in the parent process
# before any RF import and pass it explicitly to every CLI child, so a rerun
# can never write the repository's default registry.
OWNED_REGISTRY = ROOT / ".du6-tmp" / "registry.jsonl"
os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(OWNED_REGISTRY)

FIXTURES = ROOT / "tests" / "fixtures" / "du6_targets"
OUT = ROOT / ".du6-tmp" / "c_out"
CLI = ROOT / "scripts" / "revenue_forecast.py"

from research.input_targets import build_management_target  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_du6_target_measurement_boundaries import (  # noqa: E402
    growth_document,
    money_target_document,
)


def _run_cli(args: list[str]) -> dict:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["REVENUE_PUBLICATION_REGISTRY"] = str(OWNED_REGISTRY)
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(CLI), *args],
        capture_output=True, encoding="utf-8", timeout=300, check=False, env=env,
    )
    return {
        "argv": [str(CLI), *args],
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout[-800:],
        "stderr_tail": completed.stderr[-800:],
    }


def build_models() -> dict[str, dict]:
    models: dict[str, dict] = {}

    # M1: HKD model, positive amount target stated in 万 HKD (same-currency
    # scale conversion into the model's million HKD).
    models["m1_hkd_wan_positive_amount"] = money_target_document(
        raw_value=72500, comparison_value=725, raw_currency="HKD", raw_scale="万",
        model_currency="HKD", model_unit="million", target_id="hk_wan_target",
    )

    # M2: RMB model, positive amount target stated in CNY 亿元 (CNY and RMB are
    # one currency; the target keeps its own spelling).
    models["m2_cny_yi_same_currency"] = money_target_document(
        raw_value=500, comparison_value=500, raw_currency="CNY", raw_scale="亿元",
        model_currency="RMB", model_unit="亿元", target_id="cny_yi_target",
    )

    # M3: negative YoY growth guidance, built by the typed builder and attached
    # without hand-patching the target dictionary.
    m3 = growth_document(
        raw_value=-10.0, comparison_value=-0.10, comparison="approximately",
        target_id="decline_guidance",
        growth_by_scenario={"low": -0.20, "base": -0.10, "high": 0.20},
    )
    built = build_management_target(
        "Management guides FY2027 revenue to decline about ten percent year over year.",
        target_id="decline_guidance",
        metric_name="revenue growth",
        metric_definition="year over year growth of consolidated recognized revenue",
        source_id="filing",
        locator="Guidance section",
        excerpt="Management guides FY2027 revenue to decline about ten percent year over year.",
        verified_by="du6-c-node",
        verified_date=m3["as_of_date"],
        raw_unit="percent",
        raw_currency="dimensionless",
        raw_scale="percent",
        period_label="FY2027",
        measurement_basis="annual_period",
        measurement_periods=["FY2027"],
        target_period="FY2027",
        rationale="Signed growth guidance recorded at its own percent.",
        measurement_rationale="The statement is an annual YoY growth rate.",
        normalization_rationale="The stated rate is already an annual YoY growth ratio.",
        perimeter_notes="Company recognized revenue.",
        comparison="approximately",
        raw_value=-10.0,
        comparison_spec={
            "schema_version": "management-target-comparison/1",
            "metric_kind": "year_over_year_growth",
            "period": "FY2027",
            "base_period": "FY2026",
            "raw_ratio_basis": "percent",
        },
    )
    existing = m3["management_targets"][0]
    built["target"].update(
        treatment="independent_benchmark",
        mapped_scenarios=list(existing["mapped_scenarios"]),
        mapped_parameter_ids=list(existing["mapped_parameter_ids"]),
        benchmark_rationale="A disclosed decline rate kept independent of the scenario paths.",
        benchmark_claim_ids=["benchmark_evidence"],
    )
    claim = next(c for c in built["claims"] if c["claim_id"] == "claim_decline_guidance")
    claim.update(
        source_id="filing",
        content_sha256="a" * 64,
        capture_receipt_sha256=m3["sources"][0]["capture"]["receipt_sha256"],
        target_id="decline_guidance",
    )
    m3["evidence_claims"].extend(built["claims"])
    m3["management_targets"] = [built["target"]]
    models["m3_negative_yoy"] = m3

    # M4: cross-zero growth band (a decline or a small rise), both ends kept.
    models["m4_cross_zero_growth_range"] = growth_document(
        raw_value_low=-10.0, raw_value_high=5.0, comparison="approximately",
        target_id="cross_zero_band",
        growth_by_scenario={"low": -0.20, "base": -0.02, "high": 0.20},
    )

    # M5: a period-end run-rate on a constant-currency basis with no supported
    # annual conversion: it must stay a named gap, never a fabricated number.
    m5 = money_target_document(
        raw_value=40, comparison_value=None, raw_currency="HKD", raw_scale="million",
        model_currency="HKD", model_unit="million", treatment="unmodeled_data_gap",
        target_id="cc_run_rate_gap",
    )
    m5["management_targets"][0].update(
        raw_value_kind="numeric",
        measurement_basis="run_rate_at_period_end",
        currency_basis="constant_currency",
        comparison_basis=None,
        comparison_value=None,
        comparison_currency=None,
        comparison_scale=None,
        mapped_scenarios=[],
        mapped_parameter_ids=[],
        statement="Management disclosed an exit run-rate of HKD 40 million on a constant-currency basis.",
        unmodeled_reason="Run-rate disclosure preserved; no evidence-backed annual recognized revenue conversion available.",
        rationale="Period-end run-rate is not annual recognized revenue.",
    )
    m5["management_targets"][0].pop("comparison_basis", None)
    m5["management_targets"][0].pop("benchmark_rationale", None)
    m5["management_targets"][0].pop("benchmark_claim_ids", None)
    models["m5_run_rate_cc_gap"] = m5

    # Negative controls: every one must be refused by name.
    controls: dict[str, dict] = {}
    controls["x1_cross_currency"] = money_target_document(
        raw_value=100, comparison_value=100, raw_currency="HKD", raw_scale="million",
        model_currency="USD", model_unit="million", target_id="bad_fx_target",
    )
    controls["x2_negative_amount"] = money_target_document(
        raw_value=-100, comparison_value=-100, raw_currency="USD", raw_scale="million",
        model_currency="USD", model_unit="million", target_id="bad_negative_amount",
    )
    controls["x3_operator_on_range"] = growth_document(
        raw_value_low=-10.0, raw_value_high=5.0, comparison="at_least",
        target_id="bad_operator_range",
    )
    controls["x4_wrong_unit_family"] = money_target_document(
        raw_value=100, comparison_value=100, raw_currency="USD", raw_scale="ratio",
        model_currency="USD", model_unit="million", target_id="bad_unit_family",
    )
    return {"models": models, "controls": controls}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    FIXTURES.mkdir(parents=True, exist_ok=True)
    grouped = build_models()
    receipt: dict = {
        "schema_version": "du6-c-receipt/1",
        "card_id": "DU6-RF-TARGET-MEASURES",
        "publication_registry": str(OWNED_REGISTRY),
        "supplier_calls": 0,
        "models": [],
        "negative_controls": [],
    }
    for name, data in grouped["models"].items():
        input_path = FIXTURES / f"{name}.json"
        input_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        out_json = OUT / f"{name}.json"
        out_md = OUT / f"{name}.md"
        entry = {"name": name, "input": str(input_path.relative_to(ROOT))}
        entry["validate_only"] = _run_cli([str(input_path), "--validate-only"])
        entry["formal"] = _run_cli(
            [str(input_path), "--output", str(out_json), "--markdown", str(out_md)]
        )
        entry["outputs_exist"] = {"json": out_json.is_file(), "markdown": out_md.is_file()}
        result = json.loads(out_json.read_text(encoding="utf-8"))
        validate_published_forecast(result, data)
        entry["validate_published_forecast"] = "ok"
        targets = result.get("management_target_coverage", {}).get("targets", [])
        entry["target_summaries"] = [
            {
                "target_id": t["target_id"],
                "treatment": t["treatment"],
                "comparison": t.get("comparison"),
                "comparison_reason": t.get("comparison_reason"),
                "raw_target_value": t.get("raw_target_value"),
                "raw_target_value_low": t.get("raw_target_value_low"),
                "raw_target_value_high": t.get("raw_target_value_high"),
                "comparison_value": t.get("comparison_value"),
                "scenario_comparison": t.get("scenario_comparison"),
            }
            for t in targets
        ]
        entry["data_gaps"] = result.get("data_gaps", [])
        receipt["models"].append(entry)
    for name, data in grouped["controls"].items():
        input_path = OUT / f"{name}.json"
        input_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        run = _run_cli([str(input_path), "--validate-only"])
        receipt["negative_controls"].append({"name": name, "run": run})
    (OUT / "c_receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    ok = (
        all(e["validate_only"]["exit_code"] == 0 and e["formal"]["exit_code"] == 0
            and all(e["outputs_exist"].values()) for e in receipt["models"])
        and all(c["run"]["exit_code"] != 0 for c in receipt["negative_controls"])
    )
    print(json.dumps({
        "ok": ok,
        "models": [(e["name"], e["validate_only"]["exit_code"], e["formal"]["exit_code"])
                   for e in receipt["models"]],
        "controls": [(c["name"], c["run"]["exit_code"]) for c in receipt["negative_controls"]],
    }, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
