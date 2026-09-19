"""Audit-only counterexamples. No catalog, download, or product edits."""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

def load_test(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def main():
    from mine_year_operation import validate_mine_year_operation, derive_saleable_volume
    from commercial_terms import validate_commercial_terms, calculate_net_revenue
    from confidence_policy import detect_gaming_mutations, validate_confidence_policy
    soak = load_test("audit_ca206", ROOT / "tests/test_ca206_soak_window.py")
    events = [soak.SoakRun(f"fabricated-{i}", "2099-01-01T00:00:00+00:00", "daily") for i in range(7)]
    rows = []
    rows.append({"id":"RF-P01", "surface":"historical_test_local_calculator_only", "input":"seven distinct IDs at same future timestamp; report hashes blank", "actual":soak.daily_window(events, now="2026-09-19T00:00:00+00:00"), "claim":"trusted natural-time 7 daily runs", "production_inference":"none: tested function defined inside test_ca206_soak_window.py"})
    op = {"volume":1000.0, "grade":2.0, "recovery":1.0, "payable":1.0, "product":"copper", "period":"FY2026", "scenario":"base"}
    result=derive_saleable_volume(validate_mine_year_operation(op))
    rows.append({"id":"RF-P02", "surface":"product_helper", "input":dict(op), "actual":result, "claim":"units and percent basis explicit", "limitation":"No unit or grade-basis field: 2 percent and fraction 0.02 cannot be distinguished; no investment recommendation"})
    op["grade"] = float("inf")
    accepted = validate_mine_year_operation(op)
    rows.append({"id":"RF-P03", "surface":"product_helper", "actual":str(derive_saleable_volume(accepted)), "claim":"finite numeric mine inputs", "result":"infinite grade accepted"})
    def term(v):
        return {"value":v,"source":"audit synthetic","assumption":"boundary probe","period":"FY2026"}
    terms = validate_commercial_terms({"price":term(10),"tc":term(2),"payability":term(0.5)})
    rows.append({"id":"RF-P04", "surface":"product_helper", "input":{"saleable_volume":100,"price":10,"tc_per_unit_documented":2,"payability":0.5}, "actual":calculate_net_revenue(100,terms), "expected_if_tc_per_unit":800, "claim":"documented per-unit TC applied, commercial payability consumed", "result":"tc subtracted once; payability ignored"})
    fake={"backtest_id":"audit","year":2026,"source_id":"s","value":123,"record_sha256":"not-a-sha","observations":2,"wape":0.1}
    rows.append({"id":"RF-P05", "surface":"product_helper", "input":fake,"actual":detect_gaming_mutations([fake]),"claim":"wrong-record hash recomputation rejected","limitation":"Main engine separately validates historical records; this proves helper claim false, not successful attack on current formal publication"})
    policy = validate_confidence_policy({"version":"1.0","weights":{"x":float("inf")}})
    rows.append({"id":"RF-P06", "surface":"product_helper", "actual":{"accepted_x_weight":str(policy["weights"]["x"])}, "claim":"usable finite confidence policy","result":"infinite arbitrary component accepted"})
    print(json.dumps({"scope":"isolated synthetic probes; no live provider or natural-time observations", "results":rows},ensure_ascii=False,indent=2,allow_nan=False))

if __name__ == "__main__":
    main()
