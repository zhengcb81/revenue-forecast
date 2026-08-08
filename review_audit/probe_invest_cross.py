# Cross-repo probe: forged revenue artifact -> invest-core adapter.
import copy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "scripts"))
sys.path.insert(0, str(root / "tests"))
invest_core = Path(r"C:\Users\郑曾波\Projects\invest-skills\invest-core\scripts")
sys.path.insert(0, str(invest_core))

from revenue_core import canonical_sha256, run_forecast, ENGINE_VERSION
from revenue_publication import (
    VerificationContext,
    build_publication_receipt,
    expected_publication_gates,
)
from test_recognition_bridge import forecast_document

data = forecast_document()
legit = run_forecast(copy.deepcopy(data))
print(f"legit terminal: {legit['consolidated_forecast']['base']['terminal_revenue']}")

attacker_input = copy.deepcopy(data)
for p in attacker_input["parameters"]:
    if isinstance(p.get("value"), (int, float)) and p.get("kind") in {
        "analyst_assumption",
        "scenario_stress",
    }:
        p["value"] = float(p["value"]) * 1.5

forged = run_forecast(attacker_input)
print(f"forged terminal: {forged['consolidated_forecast']['base']['terminal_revenue']}")

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
forged["publication_receipt"] = build_publication_receipt(
    forged,
    VerificationContext(
        forged["input_sha256"], expected_publication_gates(forged), ENGINE_VERSION
    ),
)
forged["result_sha256"] = canonical_sha256(
    {k: v for k, v in forged.items() if k != "result_sha256"}
)

import invest_contracts

try:
    invest_contracts.validate_revenue_forecast(forged)
    print(
        "invest-core validate_revenue_forecast(forged): ACCEPTED  <-- crosses trust boundary"
    )
except Exception as exc:
    print(f"invest-core validate_revenue_forecast(forged): REJECTED:{str(exc)[:150]}")

try:
    ref = invest_contracts.adapt_revenue(forged, scope="company", segment_name=None)
    print(
        "invest-core adapt_revenue(forged): ACCEPTED, effective_revenue terminal =",
        ref.get("consolidated_effective_revenue", {}).get("base", {}).get("terminal")
        if isinstance(ref, dict)
        else "?",
    )
except Exception as exc:
    print(f"invest-core adapt_revenue(forged): REJECTED:{str(exc)[:150]}")
