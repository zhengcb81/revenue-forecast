#!/usr/bin/env python
"""I-10-A harness: judged validator for the adaptation artifacts (oracle rules R1-R12).

Usage: validate_adaptation.py --evidence-root <dir> --expect pass|fail
                              [--rule-family F-A|F-B|F-C|F-D|F-E] [--out <dir>]

rc legend (frozen): 0=pass and expected pass · 2=violations found and expected fail
(negative correctly rejected) · 3=not as expected (expected fail but clean = 应红未红;
expected pass but dirty) · 1=harness failure.

Rule families (oracle §4):
  F-A = R1,R7,R8,R10  manifest/qualification/carry bookkeeping
  F-B = R2,R3,R12     per-driver mapping + verbatim quotes + unit conversions
  F-C = R4            reconciliation (tolerance provenance, no back-solving, categories)
  F-D = R5,R6         probe labelling + wiring evidence
  F-E = R9,R11        DE evidence manifest + accounting decision structure
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATT = HERE.parent
sys.path.insert(0, str(HERE))

import cases_data  # noqa: E402

FAMILIES = {
    "F-A": ["R1", "R7", "R8", "R10"],
    "F-B": ["R2", "R3", "R12"],
    "F-C": ["R4"],
    "F-D": ["R5", "R6"],
    "F-E": ["R9", "R11"],
}
FORBIDDEN_CLAIMS = ["授予准确性资格", "通过三情景", "企业适配已通过", "适配资格已签署", "accuracy granted"]
DECLARATIONS = [
    "三公司仅来源准备通过，仍未授予正式预测资格。",
    "缺一市场/真实路径不得总体写三市场通过。",
    "恢复：保留已取得raw，只回退当前隔离变更。",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


def load(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


def check(root: Path) -> list:
    v: list = []

    def viol(rule: str, msg: str):
        v.append({"rule": rule, "msg": msg})

    try:
        manifest = load(root, "selected_model_manifest.json")
        mapping = load(root, "disclosure_mapping.json")
        recon = load(root, "historical_reconciliation.json")
        probe = load(root, "historical_mapping_probe.json")
        integ = load(root, "forecast_integration.json")
        de = load(root, "model_DE_evidence_manifest.json")
        qual = load(root, "disclosure_qualification.json")
        exp = load(root, "oracle_expected.json")
    except Exception as exc:
        viol("R0", f"artifact load failure: {type(exc).__name__}: {exc}")
        return v

    # ---------- R1 manifest completeness / labels ----------
    adopted = {m["model_id"] for m in manifest["model_registry_coverage"]["adopted"]}
    not_sel = {m["model_id"] for m in manifest["model_registry_coverage"]["not_selected"]}
    all_ids = adopted | not_sel
    sys.path.insert(0, str(ATT / "iso" / "rf" / "scripts"))
    import model_registry  # noqa: E402

    reg_ids = set(model_registry.MODEL_REGISTRY)
    if len(all_ids) != 31 or all_ids != reg_ids:
        viol("R1", f"model coverage != 31 registry ids (covered={len(all_ids)}, missing={sorted(reg_ids-all_ids)}, extra={sorted(all_ids-reg_ids)})")
    total = manifest["model_registry_coverage"].get("total_models")
    if total != 31:
        viol("R1", f"total_models declared {total} != 31")
    for comp in manifest["companies"]:
        for seg in comp["segments"]:
            if seg["status"] == "adopted":
                for am in seg["adopted_models"]:
                    if "case_id" not in am or "model_id" not in am:
                        viol("R1", f"{comp['company_id']}/{seg['segment']}: adopted model missing case_id/model_id")
            elif seg["status"] == "not_selected":
                if not seg.get("reason"):
                    viol("R1", f"{comp['company_id']}/{seg['segment']}: not_selected without reason")
            else:
                viol("R1", f"{comp['company_id']}/{seg['segment']}: unknown status {seg['status']}")
    for comp in manifest["companies"]:
        for seg in comp["segments"]:
            if seg["status"] == "adopted" and not seg["adopted_models"]:
                viol("R1", f"{seg['segment']}: adopted with no model")

    # ---------- R2 per-driver mapping completeness ----------
    for case_id, case in cases_data.CASES.items():
        cm = mapping["cases"].get(case_id)
        if not cm:
            viol("R2", f"{case_id}: missing disclosure_mapping case")
            continue
        spec = cases_data.driver_spec(case["model_id"])
        want = set(spec["required"]) | set(spec["optional"])
        if not case["instances"]:
            have_missing = {m["driver"] for m in cm.get("missing_fields", [])}
            if not want <= have_missing:
                viol("R2", f"{case_id}: missing-fields list incomplete (want {sorted(want-have_missing)})")
            for m in cm.get("missing_fields", []):
                if m.get("zero_filled") is not False:
                    viol("R2", f"{case_id}/{m['driver']}: missing field must carry zero_filled=false")
                if not m.get("reason"):
                    viol("R2", f"{case_id}/{m['driver']}: missing without reason")
            continue
        for inst in cm["per_instance_fields"]:
            got = {f["driver"] for f in inst["fields"]}
            if got != want:
                viol("R2", f"{case_id}/{inst['instance']}: drivers {sorted(got)} != model drivers {sorted(want)}")
            for f in inst["fields"]:
                for key in ("parameter_id", "unit", "value", "period", "scope"):
                    if f.get(key) is None:
                        viol("R2", f"{case_id}/{inst['instance']}/{f.get('driver')}: field lacks {key}")
                if f.get("period") != case["period"]:
                    viol("R2", f"{case_id}/{inst['instance']}/{f.get('driver')}: period mismatch")
                if "source" not in f and not (f.get("source_kind") and f.get("economic_basis")):
                    viol("R2", f"{case_id}/{inst['instance']}/{f.get('driver')}: neither source nor explicit economic_basis default")
                if f.get("value") == 0 and not (f.get("source") or f.get("economic_basis")):
                    viol("R2", f"{case_id}/{inst['instance']}/{f.get('driver')}: zero value without basis (zero-fill suspicion)")

    # ---------- R3 quote verifiability ----------
    def quote_ok(ref: dict) -> bool:
        extract = ATT / ref["extract"]
        if not extract.is_file():
            return False
        lines = extract.read_text(encoding="utf-8").splitlines()
        a, b = ref["extract_lines"]
        joined = "\n".join(lines[a - 1: b])
        return norm(ref["quote"]) in norm(joined)

    def walk_refs(obj):
        if isinstance(obj, dict):
            if "quote" in obj and "extract_lines" in obj:
                yield obj
            for val in obj.values():
                yield from walk_refs(val)
        elif isinstance(obj, list):
            for val in obj:
                yield from walk_refs(val)

    for case_id, cm in mapping["cases"].items():
        for ref in walk_refs(cm):
            if not quote_ok(ref):
                viol("R3", f"{case_id}: quote not found in extract {ref['extract']} lines {ref['extract_lines']}: {ref['quote'][:40]}…")

    # ---------- R4 reconciliation integrity ----------
    for case_id, case in cases_data.CASES.items():
        rc = recon["cases"].get(case_id, {})
        exp_case = exp["cases"][case_id]
        if case["instances"]:
            l1 = rc.get("level1_same_scope_rebuild") or {}
            if not l1:
                viol("R4", f"{case_id}: missing level1 rebuild")
                continue
            # 4a tolerance provenance == frozen oracle values
            if l1.get("frozen_aggregate_tolerance_rel") != exp_case["aggregate_tolerance_rel"]:
                viol("R4", f"{case_id}: aggregate tolerance deviates from frozen oracle")
            # recompute residual from the two sums and re-derive the tolerance verdict
            resid = l1["sum_disclosed"] - l1["sum_rebuilt"]
            if abs(resid - l1["residual_disclosed_minus_rebuilt"]) > 1e-6:
                viol("R4", f"{case_id}: residual not consistent with sums (back-solving/rounding suspicion)")
            within = abs(resid) <= exp_case["aggregate_tolerance_rel"] * abs(l1["sum_disclosed"])
            if within is not l1.get("within_frozen_tolerance"):
                viol("R4", f"{case_id}: within_frozen_tolerance flag inconsistent with recomputation")
            if abs(resid - exp_case["expected_aggregate_residual_disclosed_minus_rebuilt"]) > 1e-6 * max(1.0, abs(exp_case["expected_aggregate_residual_disclosed_minus_rebuilt"])):
                viol("R4", f"{case_id}: residual deviates from frozen hand value")
            # 4b no back-solving: every quantity/price field must carry an independent source
            cm = mapping["cases"][case_id]
            for inst in cm["per_instance_fields"]:
                for f in inst["fields"]:
                    if f["driver"] in ("saleable_volume", "units", "realized_price", "unit_revenue"):
                        if "source" not in f:
                            viol("R4", f"{case_id}/{inst['instance']}/{f['driver']}: operating input lacks independent source (R4b)")
            # 4c all five categories present with value or basis
            dec = rc.get("residual_decomposition") or {}
            for cat in ("量", "价", "汇率", "范围", "确认时间"):
                if cat not in dec:
                    viol("R4", f"{case_id}: residual category {cat} missing")
                elif dec[cat].get("value") is None and not dec[cat].get("basis"):
                    viol("R4", f"{case_id}: category {cat} has neither value nor basis")
        else:
            if rc.get("E_status") != exp_case["expected_E_status"]:
                viol("R4", f"{case_id}: E_status != frozen expectation {exp_case['expected_E_status']}")

    # ---------- R5 probe labelling + no over-claim ----------
    if probe.get("historical_mapping_probe") is not True or probe.get("NOT_a_three_scenario_forecast") is not True:
        viol("R5", "probe aggregate lacks historical_mapping_probe / NOT_a_three_scenario_forecast labels")
    if probe.get("NOT_accuracy_evidence") is not False and probe.get("NOT_accuracy_evidence") is not True:
        viol("R5", "probe aggregate lacks NOT_accuracy_evidence marker")
    if probe.get("NOT_accuracy_evidence") is not True:
        viol("R5", "probe aggregate NOT_accuracy_evidence must be true")
    for text_file in (root).rglob("*"):
        if text_file.suffix in (".json", ".md"):
            try:
                content = text_file.read_text(encoding="utf-8")
            except Exception:
                continue
            for bad in FORBIDDEN_CLAIMS:
                if bad in content:
                    viol("R5", f"forbidden over-claim string {bad!r} in {text_file.name}")

    # ---------- R6 probe wiring evidence ----------
    for case_id, case in cases_data.CASES.items():
        exp_case = exp["cases"][case_id]
        if case["instances"]:
            pc = probe["cases"].get(case_id) or {}
            if not pc.get("low_base_high_identical"):
                viol("R6", f"{case_id}: low/base/high not identical")
            if not pc.get("matches_frozen_expected_all_instances"):
                viol("R6", f"{case_id}: probe output deviates from frozen expected")
            if pc.get("counts_measured") != {
                "calculate_registered_model_calls": exp_case["expected_probe_counts"]["calculate_registered_model_calls"],
                "calculate_model_path_calls": exp_case["expected_probe_counts"]["calculate_registered_model_calls"],
            } and pc.get("counts_measured", {}).get("calculate_registered_model_calls") != exp_case["expected_probe_counts"]["calculate_registered_model_calls"]:
                viol("R6", f"{case_id}: spy counts deviate from frozen counts")
            arms = pc.get("arms", {})
            for arm in ("red_conv", "mut_swap_ids"):
                if arms.get(arm, {}).get("verdict") != "correctly_rejected":
                    viol("R6", f"{case_id}: red/kill arm {arm} not correctly_rejected")
        else:
            nr = probe["not_run"].get(case_id) or {}
            if nr.get("probe_status") != "not_run" or not nr.get("not_run_reason"):
                viol("R6", f"{case_id}: not-run probe case lacks recorded reason")

    # ---------- R7 qualification bookkeeping ----------
    for case_id in cases_data.CASES:
        q = qual["cases"].get(case_id) or {}
        if q.get("formula", {}).get("status") != "accepted_scoped":
            viol("R7", f"{case_id}: formula column must stay accepted_scoped (M-cards' grant)")
        da = q.get("disclosure_adaptation", {})
        if da.get("status") != "unmapped":
            viol("R7", f"{case_id}: disclosure_adaptation must stay unmapped until reviewer signs")
        if da.get("signed") is not False or da.get("implementer_never_signs") is not True:
            viol("R7", f"{case_id}: unsigned/implementer-never-signs flags broken")
        if q.get("accuracy", {}).get("status") != "unproven":
            viol("R7", f"{case_id}: accuracy must stay unproven")

    # ---------- R8 carry integrity ----------
    carries = qual.get("carries", {})
    if carries.get("three_verbatim_declarations") != DECLARATIONS:
        viol("R8", "three declarations missing or not verbatim")
    if carries.get("overall_three_market_pass") is not False:
        viol("R8", "overall_three_market_pass must be false")
    if carries.get("zero_RevenueSourceRecord_measured_fact") is not True:
        viol("R8", "zero-RevenueSourceRecord measured fact missing")
    if not set(["F1", "F2", "F3"]) <= set(carries.get("carried_findings", [])):
        viol("R8", "carried findings F1/F2/F3 missing")

    # ---------- R9 DE evidence manifest ----------
    for case_id, item in de.get("per_model_case_products", {}).items():
        for prod in ("disclosure_mapping.json", "accounting_decision.md", "historical_reconciliation.json", "forecast_integration.json"):
            ref = item.get(prod)
            if not ref:
                viol("R9", f"{case_id}: missing M-card product {prod}")
                continue
            path_part = ref.split("#")[0].replace("evidence/I-10-A/", "")
            if not (root / path_part).exists():
                viol("R9", f"{case_id}: product file missing {path_part}")
            if "#/cases/" in ref:
                key = ref.split("#/cases/")[1]
                target = load(root, path_part)
                if key not in target.get("cases", {}):
                    viol("R9", f"{case_id}: slice {key} missing in {path_part}")
    for name, meta in de.get("aggregate_files", {}).items():
        if "sha256" in meta and len(str(meta["sha256"])) == 64:
            actual = sha256_file(root / name)
            if actual != meta["sha256"]:
                viol("R9", f"aggregate hash mismatch for {name}")

    # ---------- R10 not_selected honesty ----------
    for entry in manifest["model_registry_coverage"]["not_selected"]:
        if not entry.get("reason") and not entry.get("reason_note"):
            viol("R10", f"{entry['model_id']}: not_selected without reason")
        if entry.get("DE_status", "").startswith("D/E executed"):
            viol("R10", f"{entry['model_id']}: not_selected model claims adaptation")

    # ---------- R12 unit-conversion integrity ----------
    factor_re = re.compile(r"\*\s*([0-9][0-9_,\.]*(?:[eE][+-]?\d+)?)")
    for case_id, cm in mapping["cases"].items():
        for inst in cm.get("per_instance_fields", []):
            for f in inst["fields"]:
                conv = str(f.get("conversion_formula", ""))
                raw = f.get("raw_value")
                val = f.get("value")
                if raw is None or val is None:
                    continue
                m = factor_re.search(conv)
                if conv.strip().lower().startswith("none") or not m:
                    if abs(float(raw) - float(val)) > 1e-9 * max(1.0, abs(float(val))):
                        viol("R12", f"{case_id}/{inst['instance']}/{f.get('driver')}: value != raw_value under a no-conversion field")
                else:
                    factor = float(m.group(1).replace(",", ""))
                    expect_val = float(raw) * factor
                    if abs(expect_val - float(val)) > 1e-9 * max(1.0, abs(float(val))):
                        viol("R12", f"{case_id}/{inst['instance']}/{f.get('driver')}: raw*factor != value (conversion_formula integrity)")

    # ---------- R11 accounting decision structure ----------
    ad = (root / "accounting_decision.md").read_text(encoding="utf-8") if (root / "accounting_decision.md").exists() else ""
    if len(re.findall(r"^## AD-\d+", ad, re.M)) < 8:
        viol("R11", "accounting_decision.md lacks >= 8 AD sections")
    for marker in ("选择", "理由", "反例", "兼容影响", "恢复规则"):
        if marker not in ad:
            viol("R11", f"accounting_decision.md lacks marker {marker}")
    if "special_review" not in ad:
        viol("R11", "accounting_decision.md lacks special_review routing")
    if "actuarial_reviewer" not in ad:
        viol("R11", "accounting_decision.md lacks actuarial reviewer N/A note")
    return v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-root", required=True)
    ap.add_argument("--expect", required=True, choices=["pass", "fail"])
    ap.add_argument("--rule-family", default=None, choices=sorted(FAMILIES))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    root = Path(args.evidence_root)
    try:
        violations = check(root)
    except Exception as exc:
        print(f"harness failure: {type(exc).__name__}: {exc}")
        return 1
    if args.rule_family:
        rules = set(FAMILIES[args.rule_family])
        relevant = [x for x in violations if x["rule"] in rules or x["rule"] == "R0"]
    else:
        relevant = violations
    clean = not relevant
    if args.expect == "pass":
        rc = 0 if clean else 3
        verdict = "pass" if clean else "not_as_expected_dirty"
    else:
        rc = 2 if not clean else 3
        verdict = "correctly_rejected" if not clean else "NOT_REJECTED_ARM_SURVIVED"
    payload = {
        "artifact": "validate_adaptation_result",
        "expect": args.expect,
        "rule_family": args.rule_family,
        "violations_all": violations,
        "violations_relevant": relevant,
        "verdict": verdict,
        "raw_rc": rc,
    }
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "validate_result.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"expect": args.expect, "family": args.rule_family, "verdict": verdict,
                      "rc": rc, "n_relevant": len(relevant), "n_all": len(violations)}, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
