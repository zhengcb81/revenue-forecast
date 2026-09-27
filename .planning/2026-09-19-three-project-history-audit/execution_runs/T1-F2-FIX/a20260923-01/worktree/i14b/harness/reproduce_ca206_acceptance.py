"""I-14-B witness: the production CA-206 acceptance function accepts the attack.

READ-ONLY.  This loads the PRODUCTION test module by path and calls its pure
window functions on the C1 ledger (7 distinct run ids, one future instant, empty
evidence hashes -- the controlled counterexample recorded in
reviews/revenue/review.md:13).  Nothing is written into the product tree; the
module is imported, not executed, and it has no import-time side effects.

The point is that the BEFORE classifier's behaviour is not invented: it is the
behaviour of code that exists.

Usage:
  <iso-python> -X utf8 -B harness/reproduce_ca206_acceptance.py --out before/cmd-CA206REPRO
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
PRODUCTION_MODULE = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\tests\test_ca206_soak_window.py"
)
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ATTEMPT / "before" / "cmd-CA206REPRO"))
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    digest = hashlib.sha256(PRODUCTION_MODULE.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location("prod_ca206", PRODUCTION_MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclass resolution needs the module registered
    spec.loader.exec_module(module)

    case = next(c for c in CASES["cases"] if c["case_id"] == "C1")
    ledger = case["fields"]["ledger"]
    runs = [module.SoakRun(run_id=e["run_id"], started_at=e["started_at"], kind="daily",
                           ok=e["ok"], report_sha256=e["report_sha256"])
            for e in ledger["daily"]]
    runs += [module.SoakRun(run_id=e["run_id"], started_at=e["started_at"], kind="weekly",
                            ok=e["ok"], report_sha256=e["report_sha256"])
             for e in ledger["weekly"]]
    runs += [module.SoakRun(run_id=e["run_id"], started_at=e["started_at"], kind="monthly",
                            ok=e["ok"], report_sha256=e["report_sha256"])
             for e in ledger["monthly"]]

    result = module.soak_status(runs, ledger["alerts"], now=module.NOW)
    doc = {
        "card": "I-14-B",
        "attempt_id": "a20260919-01",
        "witness": "production CA-206 acceptance function on the C1 attack ledger",
        "production_module": str(PRODUCTION_MODULE),
        "production_module_sha256": digest,
        "read_only": True,
        "input": {
            "daily_run_ids": [e["run_id"] for e in ledger["daily"]],
            "distinct_daily_run_ids": len({e["run_id"] for e in ledger["daily"]}),
            "distinct_daily_instants": len({e["started_at"] for e in ledger["daily"]}),
            "non_empty_evidence_hashes": sum(1 for e in ledger["daily"] if e["report_sha256"]),
            "daily_started_at": sorted({e["started_at"] for e in ledger["daily"]}),
            "evaluated_now": module.NOW,
        },
        "production_result": result,
        "production_says_complete": result.get("status") == "complete",
        "same_input_under_i14b_classifier": "reject_claim (see after/cmd-CASES/sut_report.json case C1)",
    }
    (out_dir / "ca206_repro.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"production_says_complete": doc["production_says_complete"],
                      "daily_count": result["windows"]["daily"]["count"],
                      "status": result["status"],
                      "production_module_sha256": digest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
