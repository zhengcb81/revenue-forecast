#!/usr/bin/env python
"""I-10-A harness: build RED (pre-adaptation skeleton) and MUT (mutated copy)
fixtures for the judged validator arms (oracle §4).

red/<FAMILY>/  minimal skeleton artifacts that FAIL the family's rules (proves the
               rules are non-vacuous — the pre-adaptation state is detected).
mut/<FAMILY>/  copy of the REAL evidence artifacts with exactly one injected defect
               for the family (each mutant must be KILLED).
Writes only under <attempt>/_scratch/fixtures/.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATT = HERE.parent
EV = ATT / "evidence" / "I-10-A"
OUT = ATT / "_scratch" / "fixtures"

REAL_FILES = [
    "selected_model_manifest.json", "disclosure_mapping.json", "historical_reconciliation.json",
    "historical_mapping_probe.json", "forecast_integration.json", "model_DE_evidence_manifest.json",
    "disclosure_qualification.json", "accounting_decision.md", "oracle_expected.json",
]


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def copy_real(dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in REAL_FILES:
        shutil.copy2(EV / name, dst / name)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)

    # ---------------- RED: pre-adaptation skeletons ----------------
    # F-A: bookkeeping skeleton — empty manifest coverage, signed qualification, no carries
    d = OUT / "red" / "F-A"
    copy_real(d)
    write_json(d / "selected_model_manifest.json", {"companies": [], "model_registry_coverage": {"total_models": 3, "adopted": [], "not_selected": []}})
    write_json(d / "disclosure_qualification.json", {"cases": {}, "carries": {}})
    # F-B: mapping skeleton — one instance with a zero-filled missing field and a garbled quote
    d = OUT / "red" / "F-B"
    copy_real(d)
    dm = read_json(d / "disclosure_mapping.json")
    inst = dm["cases"]["ZJ-MIN-M09"]["per_instance_fields"][0]
    inst["fields"] = inst["fields"][:1]  # required+optional incomplete
    inst["fields"][0]["value"] = 0.0
    inst["fields"][0].pop("source", None)
    inst["fields"][0].pop("economic_basis", None)
    dm["cases"]["ZJ-MIN-M09"]["missing_fields"] = [{"driver": "realized_price", "status": "missing", "zero_filled": True, "reason": ""}]
    dm["cases"]["ZJ-MIN-M09"]["policy_refs"][0]["quote"] = "被篡改的引文"
    write_json(d / "disclosure_mapping.json", dm)
    # F-C: reconciliation skeleton — no tolerance, back-solved-looking sums, categories missing
    d = OUT / "red" / "F-C"
    copy_real(d)
    rc = read_json(d / "historical_reconciliation.json")
    l1 = rc["cases"]["ZJ-MIN-M09"]["level1_same_scope_rebuild"]
    l1.pop("frozen_aggregate_tolerance_rel", None)
    l1["sum_rebuilt"] = l1["sum_disclosed"]  # absorbed residual (forbidden style)
    l1["residual_disclosed_minus_rebuilt"] = 0.0
    l1["within_frozen_tolerance"] = True
    rc["cases"]["ZJ-MIN-M09"]["residual_decomposition"] = {"价": {"value": 0.0, "basis": ""}}
    write_json(d / "historical_reconciliation.json", rc)
    # F-D: probe skeleton — over-claim wording + non-identical scenarios
    d = OUT / "red" / "F-D"
    copy_real(d)
    pr = read_json(d / "historical_mapping_probe.json")
    pr["historical_mapping_probe"] = False
    pr["claim"] = "本卡授予准确性资格"
    pr["cases"]["ZJ-MIN-M09"]["low_base_high_identical"] = False
    pr["cases"]["ZJ-MIN-M09"]["arms"]["red_conv"]["verdict"] = "NOT_REFUSED_MUTANT_SURVIVED"
    write_json(d / "historical_mapping_probe.json", pr)
    # F-E: manifest/decisions skeleton — wrong hash + no AD sections
    d = OUT / "red" / "F-E"
    copy_real(d)
    de = read_json(d / "model_DE_evidence_manifest.json")
    de["aggregate_files"]["disclosure_mapping.json"]["sha256"] = "0" * 64
    de["per_model_case_products"].pop("XM-EV-M03", None)
    write_json(d / "model_DE_evidence_manifest.json", de)
    (d / "accounting_decision.md").write_text("# 空白\n\n没有结构化专业决策。\n", encoding="utf-8")

    # ---------------- MUT: single-defect mutants of the real artifacts ----------------
    # F-A mutant: flip disclosure_adaptation to signed (must be killed by R7)
    d = OUT / "mut" / "F-A"
    copy_real(d)
    q = read_json(d / "disclosure_qualification.json")
    q["cases"]["XM-PHONE-M03"]["disclosure_adaptation"]["signed"] = True
    write_json(d / "disclosure_qualification.json", q)
    # F-B mutant: corrupt one unit conversion (factor x10) — killed by R12/R4
    d = OUT / "mut" / "F-B"
    copy_real(d)
    dm = read_json(d / "disclosure_mapping.json")
    f = dm["cases"]["ZJ-MIN-M09"]["per_instance_fields"][0]["fields"][0]
    f["conversion_formula"] = f["conversion_formula"].replace("* 1000.0", "* 100.0").replace("* 1000 ", "* 100 ")
    write_json(d / "disclosure_mapping.json", dm)
    # F-C mutant: move the residual (value-changed tolerance) — killed by R4
    d = OUT / "mut" / "F-C"
    copy_real(d)
    rc = read_json(d / "historical_reconciliation.json")
    rc["cases"]["XM-EV-M03"]["level1_same_scope_rebuild"]["frozen_aggregate_tolerance_rel"] = 0.5
    rc["cases"]["XM-EV-M03"]["residual_decomposition"].pop("确认时间", None)
    write_json(d / "historical_reconciliation.json", rc)
    # F-D mutant: over-claim string — killed by R5
    d = OUT / "mut" / "F-D"
    copy_real(d)
    pr = read_json(d / "historical_mapping_probe.json")
    pr["cases"]["ZJ-SMT-M09"]["counts_measured"] = {"calculate_registered_model_calls": 8, "calculate_model_path_calls": 8}
    pr["NOT_a_three_scenario_forecast"] = False
    write_json(d / "historical_mapping_probe.json", pr)
    # F-E mutant: DE manifest slice/hash corruption — killed by R9
    d = OUT / "mut" / "F-E"
    copy_real(d)
    de = read_json(d / "model_DE_evidence_manifest.json")
    de["per_model_case_products"]["MS-IC-M06"]["forecast_integration.json"] = "evidence/I-10-A/forecast_integration.json#/cases/NO-SUCH-CASE"
    write_json(d / "model_DE_evidence_manifest.json", de)

    print(f"fixtures written under {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
