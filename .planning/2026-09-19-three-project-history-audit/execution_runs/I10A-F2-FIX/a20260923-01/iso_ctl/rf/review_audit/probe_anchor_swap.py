# Adversarial probe 2: publish inflated numbers anchored to a legitimate input hash.
import copy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "scripts"))
sys.path.insert(0, str(root / "tests"))

from revenue_core import canonical_sha256, ForecastInputError, run_forecast
from revenue_report import validate_forecast_output
from test_recognition_bridge import forecast_document


def numeric_parameters(doc):
    return [
        (p["parameter_id"], p.get("value"))
        for p in doc["parameters"]
        if isinstance(p.get("value"), (int, float))
    ]


data = forecast_document()
legit = run_forecast(copy.deepcopy(data))
legit_terminal = legit["consolidated_forecast"]["base"]["terminal_revenue"]
print(f"legit base terminal: {legit_terminal}")
print(f"legit input_sha256: {legit['input_sha256'][:16]}")

# Build attacker input: multiply every base growth-ish numeric parameter by 1.5
attacker_input = copy.deepcopy(data)
changed = 0
for p in attacker_input["parameters"]:
    if isinstance(p.get("value"), (int, float)) and p.get("kind") in {
        "analyst_assumption",
        "scenario_stress",
    }:
        p["value"] = float(p["value"]) * 1.5
        changed += 1
print(f"modified {changed} assumption/stress parameters")

try:
    forged = run_forecast(attacker_input)
except ForecastInputError as exc:
    print(f"attacker engine run rejected: {exc}")
    sys.exit(0)

forged_terminal = forged["consolidated_forecast"]["base"]["terminal_revenue"]
print(f"forged base terminal: {forged_terminal}")

# Anchor the forged result to the legitimate input hash
forged["input_sha256"] = legit["input_sha256"]
forged["input_document"] = copy.deepcopy(attacker_input)
forged["workflow_compliance_receipt"]["input_sha256"] = legit["input_sha256"]
forged["workflow_compliance_receipt"]["receipt_sha256"] = canonical_sha256(
    {
        k: v
        for k, v in forged["workflow_compliance_receipt"].items()
        if k != "receipt_sha256"
    }
)
from revenue_publication import (
    VerificationContext,
    build_publication_receipt,
    expected_publication_gates,
)
from revenue_core import ENGINE_VERSION

forged["publication_receipt"] = build_publication_receipt(
    forged,
    VerificationContext(
        forged["input_sha256"], expected_publication_gates(forged), ENGINE_VERSION
    ),
)
forged["result_sha256"] = canonical_sha256(
    {k: v for k, v in forged.items() if k != "result_sha256"}
)

try:
    validate_forecast_output(forged)
    print(
        "D2 inflated-numbers anchored to legit input hash: ACCEPTED  <-- VULNERABILITY"
    )
except (ForecastInputError, TypeError) as exc:
    print(
        f"D2 inflated-numbers anchored to legit input hash: REJECTED:{str(exc)[:120]}"
    )

# Also check snapshot path with the same trick
from revenue_backtest import validate_snapshot, create_snapshot

snap = create_snapshot(copy.deepcopy(data), "v1")
forged_snap = copy.deepcopy(snap)
forged_snap["forecast_result"] = forged
forged_snap["input_document"] = copy.deepcopy(attacker_input)
forged_snap["forecast_result_sha256"] = canonical_sha256(forged)
identity = {
    key: forged_snap[key]
    for key in (
        "company_name",
        "as_of_date",
        "forecast_version",
        "input_sha256",
        "forecast_result_sha256",
        "engine_version",
        "forecast_schema_version",
        "snapshot_schema_version",
    )
}
forged_snap["snapshot_id"] = canonical_sha256(identity)
try:
    validate_snapshot(forged_snap)
    print(
        "D3 snapshot with swapped input+result, anchored hash: ACCEPTED  <-- VULNERABILITY"
    )
except ForecastInputError as exc:
    print(
        f"D3 snapshot with swapped input+result, anchored hash: REJECTED:{str(exc)[:120]}"
    )
